"""Small neutral-prompt model-agnostic execution probe. Default: prepare only, no API.
python scripts/compare_skill.py --model <exact-provider-model-id> --out <directory> [--run]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
BASE='62d51508aad00003dc6209afa80c4b5dc540de59'
BRIEF='''制作一个6秒1920×1080、30fps、无旁白的曲柄滑块机构解释镜头，让人看清旋转如何变成往复。
曲柄半径r=.35，连杆L=1.2，匀速角φ=2πt/6；曲柄销(r cosφ,r sinφ)，滑块(x,0)，x=r cosφ+sqrt(L²-r²sin²φ)。
自行选择构图、材质、字体与机位。仅生成film.js，工程index.html已提供VK和VKit；可选场景层按下列共同API使用。
画面须为时间t的确定性函数，使用VK.film({dur:6,...})，不要联网或添加依赖。返回JSON对象{"film_js":"完整JavaScript"}。
这是单镜头实现探针，不是完整创作流程测试；不用输出长篇报告。'''


def prepare(out,model,max_tokens):
    if out.exists() and any(out.iterdir()):raise ValueError('output directory is not empty; choose a fresh directory')
    out.mkdir(parents=True,exist_ok=True)
    old=subprocess.check_output(['git','show',f'{BASE}:SKILL.md'],cwd=ROOT,text=True,encoding='utf-8')
    new='\n\n'.join((ROOT/p).read_text(encoding='utf-8') for p in ['SKILL.md','references/complex-scenes.md'])
    # Both arms receive the same runtime/API source and no artwork/example film.
    api='\n\n'.join((ROOT/p).read_text(encoding='utf-8') for p in ['engine/vk-scene.mjs'])
    common=BRIEF+'\n共同API源码：\n'+api+'\nVK/VKit API参考：\n'+(ROOT/'references/engine.md').read_text(encoding='utf-8')
    for arm,guide in [('original',old),('upgraded',new)]:
        folder=out/arm;folder.mkdir()
        payload={'model':model,'temperature':.2,'max_tokens':max_tokens,'response_format':{'type':'json_object'},
                 'messages':[{'role':'system','content':guide},{'role':'user','content':common}]}
        (folder/'request.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        (folder/'index.html').write_text((ROOT/'engine/index.html').read_text(encoding='utf-8'),encoding='utf-8')
    manifest={'status':'prepared_not_run','requested_model':model,'baseline_commit':BASE,
              'upgraded_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'upgraded_guidance_sha256':hashlib.sha256(new.encode()).hexdigest(),
              'original_guidance_sha256':hashlib.sha256(old.encode()).hexdigest(),
              'common_prompt_sha256':hashlib.sha256(common.encode()).hexdigest(),
              'temperature':.2,'max_tokens_per_arm':max_tokens,'iterations_per_arm':1,
              'scope':'single-shot execution probe; no model efficacy result without real outputs and review'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')


def run(out):
    key=os.environ.get('VK_MODEL_API_KEY') or os.environ.get('DEEPSEEK_API_KEY')
    if not key:raise ValueError('VK_MODEL_API_KEY is not configured; prepared requests only, no API call')
    base=(os.environ.get('VK_MODEL_BASE_URL') or os.environ.get('DEEPSEEK_BASE_URL') or '').rstrip('/')
    if not base:raise ValueError('VK_MODEL_BASE_URL is not configured; use an OpenAI-compatible endpoint')
    manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
    if manifest['status']!='prepared_not_run':raise ValueError('probe already started; use a fresh output directory')
    payloads=[json.loads((out/a/'request.json').read_text(encoding='utf-8')) for a in ['original','upgraded']]
    if payloads[0]['messages'][1:]!=payloads[1]['messages'][1:]:raise ValueError('common prompts differ')
    if hashlib.sha256(payloads[0]['messages'][1]['content'].encode()).hexdigest()!=manifest['common_prompt_sha256']:
        raise ValueError('prepared common prompt changed; create a new probe')
    if {k:v for k,v in payloads[0].items() if k!='messages'}!={k:v for k,v in payloads[1].items() if k!='messages'}:
        raise ValueError('model parameters differ')
    for arm,payload in zip(['original','upgraded'],payloads):
        if hashlib.sha256(payload['messages'][0]['content'].encode()).hexdigest()!=manifest[arm+'_guidance_sha256']:
            raise ValueError('prepared guidance changed; create a new probe')
    manifest['status']='running'
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    for arm in ['original','upgraded']:
        folder=out/arm;payload=(folder/'request.json').read_bytes();start=time.monotonic()
        req=urllib.request.Request(base+'/chat/completions',data=payload,
            headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        try:
            try:
                with urllib.request.urlopen(req,timeout=120) as response:result=json.load(response)
            except urllib.error.HTTPError as exc:raise RuntimeError(f'{arm}: API HTTP {exc.code}; credentials/response body not logged') from None
            (folder/'response.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
            manifest[arm]={'reported_model':result.get('model'),'usage':result.get('usage','unavailable'),
                           'elapsed_seconds':time.monotonic()-start}
            film=json.loads(result['choices'][0]['message']['content'])['film_js']
            if not isinstance(film,str) or not film.strip():raise ValueError(f'{arm}: missing film_js; raw response preserved')
            (folder/'film.js').write_text(film,encoding='utf-8')
        except BaseException:
            manifest.update(status='failed_unreviewed',failed_arm=arm)
            (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
            raise
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    manifest['status']='generated_unreviewed'
    manifest['reported_models_match']=manifest['original']['reported_model']==manifest['upgraded']['reported_model']
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',required=True,help='actual provider model ID; no invented alias')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--max-tokens',type=int,default=3000)
    parser.add_argument('--run',action='store_true',help='make exactly two API calls; consumes provider credits')
    args=parser.parse_args()
    if args.max_tokens<1:parser.error('--max-tokens must be positive')
    if args.run and (args.out/'manifest.json').exists():
        manifest=json.loads((args.out/'manifest.json').read_text(encoding='utf-8'))
        if manifest['requested_model']!=args.model or manifest['max_tokens_per_arm']!=args.max_tokens:
            parser.error('arguments do not match the prepared model/budget')
    else:prepare(args.out,args.model,args.max_tokens)
    if args.run:run(args.out)
    print('prepared' if not args.run else 'generated, not reviewed',args.out)


if __name__=='__main__':main()

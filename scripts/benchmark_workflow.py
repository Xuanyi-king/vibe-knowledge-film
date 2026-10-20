"""Offline document proxy metrics and optional tiny real production comparison.
python scripts/benchmark_workflow.py --baseline-root ../vk-baseline --output ../metrics.json
Add --run for identical .4s technical fixtures; --scene probes the existing 3D shot.
No model API, synthetic token estimates, new film or benchmark dependencies.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from time import perf_counter

ROOT=Path(__file__).resolve().parents[1]
# Audited task routes, not observed model behavior; links are not required reads.
ROUTES={
    'topic':(['script','directing','worlds','visualization','craft'],[]),
    'single_shot':(['directing','craft','review','engine'],['engine']),
    'complex_3d':(['directing','craft','complex-scenes','engine','choreography'],['engine','complex-scenes','choreography']),
    'full_release':(['script','directing','worlds','visualization','craft','choreography','review','production','mobile'],['engine','choreography','production','review','mobile']),
}
FIXTURE="""import('/engine/vk-motion.mjs').then(M=>{
window.VK_SCORE=M.score({end:.4,events:[{id:'hit',start:.2,duration:.1,sound:{kind:'impact'}}]});
VK.film({dur:.4,grain:0,draw(fr,t){fr.rect(30+t*10,20,30,30,{fill:'#abc'})}});
});"""


def documents(root, after):
    result={}
    for name,(before,current) in ROUTES.items():
        paths=['SKILL.md',*[f'references/{x}.md' for x in (current if after else before)]]
        result[name]={'files':paths,'utf8_bytes':sum((root/p).stat().st_size for p in paths),
                      'reference_count':len(paths)-1}
    links={}
    for path in [root/'SKILL.md',*sorted((root/'references').glob('*.md'))]:
        links[path.relative_to(root).as_posix()]=re.findall(r'\]\((?!https?://)([^)#]+)',path.read_text(encoding='utf-8'))
    return {'startup':{'utf8_bytes':(root/'SKILL.md').stat().st_size,'lines':len((root/'SKILL.md').read_text(encoding='utf-8').splitlines())},
            'routes_proxy':result,'local_link_graph':links}


def command(root,project,args,label,logs):
    start=perf_counter()
    run=subprocess.run([sys.executable,str(root/'scripts/produce.py'),str(project),*args],
                       capture_output=True,text=True,encoding='utf-8',errors='replace')
    (logs/(label+'.log')).write_text(run.stdout+run.stderr,encoding='utf-8')
    if run.returncode:raise RuntimeError(f'{label} failed; see {logs/(label+".log")}')
    report=json.loads((project/('review/draft.json' if '--mode' in args and 'draft' in args else 'review/production.json')).read_text(encoding='utf-8'))
    return {'seconds':round(perf_counter()-start,4),'stage_subprocess_count':len(report['stages']),
            'stages':report['stages'],'reused':report.get('reused',[]),'status':report['status']}


def measure(baseline,logs,scene=False):
    logs.mkdir(parents=True,exist_ok=True);results={}
    if scene:
        subprocess.run([sys.executable,str(ROOT/'engine/get_scene_assets.py')],check=True)
        shutil.copytree(ROOT/'engine/vendor',baseline/'engine/vendor',dirs_exist_ok=True)
    # Sequential, identical inputs, same environment; one tiny fixture per version.
    with tempfile.TemporaryDirectory(prefix='vk workflow bench ') as d:
        for label,root in [('before',baseline),('after',ROOT)]:
            p=Path(d)/label;p.mkdir()
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script src="film.js"></script>',encoding='utf-8')
            (p/'film.js').write_text(FIXTURE,encoding='utf-8')
            if label=='before':
                for run in ('cold_release','warm_release'):
                    results[label+'_'+run]=command(root,p,['--chunk','.2'],label+'_'+run,logs)
            else:
                release=Path(d)/'after-release';release.mkdir()
                for file in ('index.html','film.js'):shutil.copyfile(p/file,release/file)
                for run in ('cold_release','warm_release'):
                    results[label+'_'+run]=command(root,release,['--chunk','.2'],label+'_'+run,logs)
                for run,args in [('cold_standard',['--mode','standard']),('warm_standard',['--mode','standard']),
                                 ('release_from_standard',[]),('warm_release_from_standard',[]),
                                 ('shot_still',['--mode','draft','--stills','.2']),
                                 ('shot_motion',['--mode','draft','--motion','0','.3']),
                                 ('shot_clip',['--mode','draft','--clip','0','.3'])]:
                    results[label+'_'+run]=command(root,p,[*args,'--chunk','.2'],label+'_'+run,logs)
        if scene:
            for label,root in [('before',baseline),('after',ROOT)]:
                p=Path(d)/(label+'-scene');shutil.copytree(root/'examples/governor_scene',p,
                    ignore=shutil.ignore_patterns('renders','review','audio'))
                # Both use the same existing low-cost still, no full 3D movie.
                start=perf_counter()
                r=subprocess.run([sys.executable,str(root/'engine/render.py'),str(p),'--stills','2'],capture_output=True)
                (logs/(label+'-scene.log')).write_bytes(r.stdout+r.stderr)
                if r.returncode:raise RuntimeError('scene probe failed')
                results[label+'_complex_3d']={'seconds':round(perf_counter()-start,4),'render_cli_calls':1}
    return results


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--run',action='store_true');p.add_argument('--scene',action='store_true')
    a=p.parse_args();baseline=a.baseline_root.resolve()
    data={'measurement':'UTF-8 bytes and declared routes are static proxies; runtime is a .4s technical fixture, not a film or model benchmark',
          'model_tool_calls':None,'model_tokens':None,
          'before':documents(baseline,False),'after':documents(ROOT,True)}
    if a.run:data['runtime']=measure(baseline,a.output.resolve().parent/(a.output.stem+'-logs'),a.scene)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(a.output)

if __name__=='__main__':main()

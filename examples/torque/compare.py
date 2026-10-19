"""Capture matched art controls and close contact strip; no alternate video pipeline.
Run after prepare_instrument.py: python examples/torque/compare.py
"""
from pathlib import Path
import hashlib,io,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from engine import render
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright

def main():
    project=Path(__file__).resolve().parent;out=project/'review';out.mkdir(exist_ok=True)
    srv,url=render.serve(project);record={'scope':'same geometry/camera/colors/score/type; lighting and surface only, not a model experiment','frames':[]}
    try:
        with sync_playwright() as p:
            pictures=[]
            for variant in ['baseline','cinematic']:
                browser,page=render.open_page(p,url)
                try:
                    if variant=='baseline':
                        page.goto(url+'baseline.html')
                        page.wait_for_function('window.READY === true || !!window.READY_ERROR',timeout=180000)
                        error=page.evaluate('window.READY_ERROR || null')
                        if error:raise RuntimeError(error)
                    for t in [3.2,8.5]:
                        raw=render.shot(page,t);im=Image.open(io.BytesIO(raw)).convert('RGB')
                        im.save(out/f'{variant}-{t}.jpg',quality=92)
                        state=page.evaluate('ART_SHOT.inspect()');record['frames'].append({'variant':variant,'time':t,'png_sha256':hashlib.sha256(raw).hexdigest(),'r':state['r'],'force':state['force'],'torque':state['torque']})
                        pictures.append((variant,t,im))
                    if variant=='cinematic':
                        render.shot(page,1.8);x,y=page.evaluate('ART_SHOT.inspect().contactScreen')
                        strip=Image.new('RGB',(1200,1080),'#202426');d=ImageDraw.Draw(strip)
                        for i,f in enumerate(range(50,62)):
                            raw=render.shot(page,f/30);im=Image.open(io.BytesIO(raw)).convert('RGB')
                            crop=im.crop((round(x)-150,round(y)-220,round(x)+150,round(y)+30))
                            xx,yy=(i%4)*300,(i//4)*360;strip.paste(crop,(xx,yy));d.text((xx+10,yy+260),f'{f/30:.3f}s',fill='white')
                        strip.save(out/'contact-strip.jpg',quality=92)
                        raw=render.shot(page,8.5);phone=Image.open(io.BytesIO(raw)).convert('RGB').resize((390,219),Image.Resampling.LANCZOS);phone.save(out/'phone-390.jpg',quality=95)
                finally:browser.close()
            pair=Image.new('RGB',(1920,1160),'#202426');d=ImageDraw.Draw(pair)
            for variant,t,im in pictures:
                x=0 if variant=='baseline' else 960;y=0 if t==3.2 else 580
                pair.paste(im.resize((960,540),Image.Resampling.LANCZOS),(x,y+40));d.text((x+20,y+12),f'{variant} / {t:.1f}s',fill='white')
            pair.save(out/'matched-art.jpg',quality=92)
            (out/'comparison.json').write_text(json.dumps(record,indent=2)+'\n')
    finally:srv.shutdown();srv.server_close()
    print(out/'matched-art.jpg')
if __name__=='__main__':main()

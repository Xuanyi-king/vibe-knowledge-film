"""Linux measurement harness, not a production dependency (pip install psutil).
Run with --baseline old_check_mobile.py --candidate scripts/check_mobile.py
--synthetic /path/to/180s.mp4 --output /tmp/mobile-benchmark.
"""
import argparse, hashlib, importlib.util, json, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))

if len(sys.argv)>1 and sys.argv[1]=='--worker':
    import resource
    module,video,out,times=sys.argv[2:]
    spec=importlib.util.spec_from_file_location('bench_mobile',module)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    counts={'ffmpeg_calls':0,'selection_passes':0};run=m.run
    def count(cmd):
        if cmd[0]=='ffmpeg':counts['ffmpeg_calls']+=1
        if ('-vf' in cmd and 'select=eq' in cmd[cmd.index('-vf')+1]) or '-filter_script:v' in cmd:counts['selection_passes']+=1
        return run(cmd)
    m.run=count
    start=time.perf_counter();r=m.review_video(Path(video),Path(out),times=json.loads(times))
    cpu=sum(resource.getrusage(w).ru_utime+resource.getrusage(w).ru_stime for w in (resource.RUSAGE_SELF,resource.RUSAGE_CHILDREN))
    print(json.dumps({'wall_seconds':time.perf_counter()-start,'cpu_seconds':cpu,'samples':len(r['frames']),**counts}),flush=True)
else:
    import psutil
    from PIL import Image
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('baseline','candidate','synthetic','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);results=[]
    cases=[('14s',ROOT/'evidence/torque/mobile/final.mp4',[53/30,54/30,55/30,3.2,161/30,8.5,12]),
           ('72s',ROOT/'evidence/atlas/final.mp4',[2,6,12,18,24,30,36,42,48,54,60,70]),
           ('180s',a.synthetic,[1+178*i/31 for i in range(32)])]
    for version,module in [('before',a.baseline),('after',a.candidate)]:
        for name,video,times in cases:
            out=a.output/f'{version}-{name}';log=a.output/f'{version}-{name}.log';peak=0
            with log.open('w') as f:
                proc=subprocess.Popen([sys.executable,__file__,'--worker',str(module.resolve()),str(video.resolve()),str(out.resolve()),json.dumps(times)],stdout=f,stderr=subprocess.STDOUT)
                watched=psutil.Process(proc.pid)
                while proc.poll() is None:
                    try:procs=[watched]+watched.children(recursive=True)
                    except psutil.NoSuchProcess:procs=[]
                    rss=0
                    for child in procs:
                        try:rss+=child.memory_info().rss
                        except psutil.NoSuchProcess:pass
                    peak=max(peak,rss);time.sleep(.02)
            if proc.returncode:raise RuntimeError(log.read_text()[-4000:])
            row=json.loads(log.read_text().splitlines()[-1]);hashes={}
            for path in sorted(out.glob('master-*.png'))+sorted(out.glob('stress-*.png')):
                with Image.open(path) as im:hashes[path.name]=hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
            row.update(version=version,case=name,peak_tree_rss_mib=peak/2**20,preview_rgb_hashes=hashes)
            results.append(row);(a.output/'results.json').write_text(json.dumps(results,indent=2))
            print(version,name,row['wall_seconds'],flush=True)
    for name,_,_ in cases:
        pair=[r for r in results if r['case']==name]
        assert pair[0]['preview_rgb_hashes']==pair[1]['preview_rgb_hashes'],name
    print('All selected master/stress RGB previews identical.')

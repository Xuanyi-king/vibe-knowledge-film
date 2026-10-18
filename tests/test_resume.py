import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

try:
    from engine import render_cache as cache
except ImportError:
    cache = None


class ResumeTest(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(cache, 'persistent render cache is not implemented')
        self.tmp=tempfile.TemporaryDirectory(prefix="vk cache's 空格 ")
        self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name);(self.p/'renders').mkdir()
        (self.p/'film.js').write_text('// fixture')
        (self.p/'labels.md').write_text('{"color":"red"}')
        self.out=self.p/'renders/raw.mp4'
        self.meta={'end':.6,'fps':30,'width':64,'height':64,'browser':'test-runtime'}
        self.calls=[]

    def part(self,proj,path,a,b):
        self.calls.append(a)
        color=json.loads((proj/'labels.md').read_text())['color']
        color=[color,'green','blue'][round(a/.2)]
        subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',
            f'color=c={color}:s={self.meta["width"]}x64:r={self.meta["fps"]}:d={b-a}',
            '-frames:v',str(round((b-a)*self.meta['fps'])),'-c:v','libx264','-threads','1','-pix_fmt','yuv420p',str(path)],check=True)

    def render(self,fn=None):
        return cache.render_cached(self.p,self.out,self.meta,.2,1,fn or self.part)

    def pixel(self,t):
        return subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(self.out),
            '-vf','scale=1:1','-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-'])

    def test_interruption_keeps_completed_parts_and_resumes_in_order(self):
        self.out.write_bytes(b'previous film')
        def interrupted(*args):
            if self.calls:raise KeyboardInterrupt()
            self.part(*args)
        with self.assertRaises(KeyboardInterrupt): self.render(interrupted)
        self.assertEqual(self.out.read_bytes(),b'previous film')
        first=next((self.p/'renders/.vk-cache').rglob('part00000.mp4'))
        before=first.stat().st_mtime_ns
        self.calls.clear();self.render()
        self.assertEqual(first.stat().st_mtime_ns,before)
        self.assertEqual(len(self.calls),2)
        for t,channel in [(0,0),(.2,1),(.4,2)]:
            px=self.pixel(t);self.assertGreater(px[channel],max(px[(channel+1)%3],px[(channel+2)%3]))

    def test_corrupt_part_is_rebuilt_without_rebuilding_valid_parts(self):
        self.render();self.calls.clear()
        parts=sorted((self.p/'renders/.vk-cache').rglob('part*.mp4'))
        untouched=parts[0].stat().st_mtime_ns
        parts[1].write_bytes(b'corrupt')
        self.render()
        self.assertEqual(len(self.calls),1)
        self.assertEqual(parts[0].stat().st_mtime_ns,untouched)

    def test_asset_and_render_parameter_changes_invalidate_cache(self):
        self.render();before=self.pixel(0)
        (self.p/'labels.md').write_text('{"color":"yellow"}')
        self.calls.clear();self.render()
        self.assertEqual(len(self.calls),3);self.assertNotEqual(before,self.pixel(0))
        self.meta['width']=128;self.calls.clear();self.render()
        self.assertEqual(len(self.calls),3)
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(self.out)]))
        self.assertEqual(info['streams'][0]['width'],128)
        self.meta['browser']='another runtime';self.calls.clear();self.render()
        self.assertEqual(len(self.calls),3)

    def test_browser_initialization_source_race_is_rejected(self):
        expected=cache.source_files(self.p)
        (self.p/'film.js').write_text('// edited while browser initialized')
        with self.assertRaisesRegex(RuntimeError,'changed during browser'):
            cache.render_cached(self.p,self.out,self.meta,.2,1,self.part,expected_sources=expected)

    def test_parallel_parts_are_concatenated_in_frame_order(self):
        cache.render_cached(self.p,self.out,self.meta,.2,2,self.part)
        for t,channel in [(0,0),(.2,1),(.4,2)]:
            px=self.pixel(t);self.assertEqual(px.index(max(px)),channel)

    def test_parallel_interrupt_cancels_queued_segments(self):
        self.meta['end']=1.2;started=[]
        def interrupted(proj,path,a,b):
            started.append(a)
            if a==0:raise KeyboardInterrupt()
            self.part(proj,path,0,.2)
        with self.assertRaises(KeyboardInterrupt):
            cache.render_cached(self.p,self.out,self.meta,.2,2,interrupted)
        self.assertLess(len(started),6)
        self.assertFalse(self.out.exists())

    def test_failed_concat_preserves_old_final(self):
        self.render();before=self.out.read_bytes()
        real_run=subprocess.run
        def fail(cmd,**kw):
            if 'concat' in cmd:raise subprocess.CalledProcessError(9,cmd,stderr='injected concat failure')
            return real_run(cmd,**kw)
        with patch.object(cache.subprocess,'run',side_effect=fail),self.assertRaisesRegex(RuntimeError,'concat'):
            self.render()
        self.assertEqual(self.out.read_bytes(),before)

    def test_invalid_part_never_published(self):
        self.out.write_bytes(b'previous film')
        def broken(proj,path,a,b):path.write_bytes(b'not video')
        with self.assertRaisesRegex(RuntimeError,'part00000'):self.render(broken)
        self.assertEqual(self.out.read_bytes(),b'previous film')

    def test_source_change_during_render_is_rejected(self):
        def changed(*args):
            self.part(*args);(self.p/'film.js').write_text('// changed during frame export')
        with self.assertRaisesRegex(RuntimeError,'changed'):self.render(changed)
        self.assertFalse(self.out.exists())

    def test_lock_releases_after_interruption(self):
        lock=self.p/'lock'
        with self.assertRaises(KeyboardInterrupt):
            with cache.cache_lock(lock):
                with self.assertRaisesRegex(RuntimeError,'another render'):
                    with cache.cache_lock(lock):pass
                raise KeyboardInterrupt()
        with cache.cache_lock(lock):pass

    def test_invalid_chunk_is_rejected(self):
        for n in [0,-1,float('nan'),.001]:
            with self.subTest(n=n),self.assertRaises(ValueError):
                cache.render_cached(self.p,self.out,self.meta,n,1,self.part)


if __name__=='__main__':unittest.main()

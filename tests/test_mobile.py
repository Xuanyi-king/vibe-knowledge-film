import hashlib,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
OLD='{"producer":"vk-mobile-qa","version":1,"note":"old"}'

class MobileTest(unittest.TestCase):
    def module(self):
        from scripts import check_mobile
        return check_mobile

    def make(self,p):
        subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=s=320x180:r=30:d=0.6',
            '-f','lavfi','-i','sine=frequency=440:duration=0.6','-c:v','libx264','-threads','1','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(p)],check=True)

    def test_risks_use_effective_pixels_importance_bounds_and_declared_contrast(self):
        m=self.module()
        items=[{'text':'刻度','role':'label','importance':'essential','left':20,'top':20,'width':160,'height':60,'style':{'size':30,'color':'#666666'},'background':'#222222'},
               {'text':'发现','role':'caption','importance':'essential','left':20,'top':120,'width':1600,'height':118,'style':{'size':84,'color':'#eee7d8'},'background':'#131619'},
               {'text':'出处','role':'source','importance':'supporting','left':1900,'top':300,'width':100,'height':30,'style':{'size':25,'color':'#aaaaaa'}}]
        r=m.layout_risks(items,320,1920,1080)
        self.assertTrue(any(x['kind']=='small-essential-text' and x['text']=='刻度' and x['effective_px']==5 for x in r))
        self.assertTrue(any(x['kind']=='declared-low-contrast' for x in r))
        self.assertTrue(any(x['kind']=='out-of-frame' and x['text']=='出处' for x in r))
        self.assertFalse(any(x['kind']=='small-essential-text' and x['text']=='发现' for x in r))

    def test_final_encoded_previews_preserve_audio_frames_and_master(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);video=p/'master.mp4';self.make(video);before=video.read_bytes()
            r=m.review_video(video,p/'mobile',times=[.1,.3],widths=[320,390])
            self.assertEqual(video.read_bytes(),before)
            self.assertEqual(r['status'],'needs_visual_review')
            self.assertFalse(r['actual_platform_verified'])
            self.assertTrue(r['simulation']['audio_payload_identical'])
            self.assertEqual(r['simulation']['frames'],18)
            self.assertEqual(len(r['frames']),2)
            with Image.open(p/'mobile/master-000003-390.png') as image:self.assertEqual(image.size,(390,219))
            with Image.open(p/'mobile/stress-000009-320.png') as image:self.assertEqual(image.size,(320,180))
            self.assertIn('text layout unavailable',r['unverified'])
            self.assertEqual(r['video_sha256'],hashlib.sha256(before).hexdigest())

    def test_bad_time_and_output_overlap_preserve_existing_evidence(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);v=p/'master.mp4';self.make(v);out=p/'mobile';out.mkdir();(out/'report.json').write_text(OLD)
            for times in [[float('nan')],[-1],[.6]]:
                with self.assertRaises(ValueError):m.review_video(v,out,times=times)
            with self.assertRaises(ValueError):m.review_video(v,p,times=[.2])
            self.assertEqual((out/'report.json').read_text(),OLD)
            self.assertTrue(v.exists())

    def test_encoder_failure_preserves_old_report_and_video(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);v=p/'master.mp4';self.make(v);old=v.read_bytes();out=p/'mobile';out.mkdir();(out/'report.json').write_text(OLD)
            real=m.run
            def fail(cmd):
                if 'libx264' in cmd:raise RuntimeError('injected encoder failure')
                return real(cmd)
            with patch.object(m,'run',side_effect=fail):
                with self.assertRaisesRegex(RuntimeError,'encoder failure'):m.review_video(v,out,times=[.2])
            self.assertEqual((out/'report.json').read_text(),OLD);self.assertEqual(v.read_bytes(),old)
            self.assertFalse(list(p.glob('.mobile-*')))

    def test_invalid_width_and_profile_are_not_silent_fallbacks(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);v=p/'master.mp4';self.make(v)
            for kwargs in [{'widths':[0]},{'widths':[float('nan')]},{'profile':'official-douyin'}]:
                with self.assertRaises(ValueError):m.review_video(v,p/'mobile',times=[.2],**kwargs)

    def test_default_samples_include_action_midstate_and_hold(self):
        m=self.module()
        frames=m.sample_frames(14,30,checks=[{'time':1.8},{'time':1.8}],events=[{'start':3.7,'end':7,'action':'slide'}])
        self.assertIn(54,frames);self.assertIn(161,frames) # same positive half-frame rounding as JS
        self.assertEqual(len(frames),len(set(frames)))
        self.assertTrue(all(0<=x<420 for x in frames))

    def test_source_validation_failure_does_not_publish_new_evidence(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);v=p/'master.mp4';self.make(v);out=p/'mobile';out.mkdir();(out/'report.json').write_text(OLD)
            def changed():raise RuntimeError('source changed')
            with self.assertRaisesRegex(RuntimeError,'source changed'):m.review_video(v,out,times=[.2],validate=changed)
            self.assertEqual((out/'report.json').read_text(),OLD)

    def test_stale_layout_source_is_rejected_before_browser_or_encoding(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'audio').mkdir();(p/'audio/events.json').write_text('{"end":1,"fps":30}')
            with patch.object(m.render,'with_page',side_effect=AssertionError('must not open browser')):
                with self.assertRaisesRegex(RuntimeError,'stale'):m.check_project(p,p/'final.mp4',p/'review/mobile')

    def test_output_cannot_replace_assets_audio_engine_or_create_tracked_sources(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'assets').mkdir();asset=p/'assets/source.js';asset.write_text('keep')
            with patch.object(m.render,'with_page',side_effect=AssertionError('must not open browser')):
                for out in [p/'assets',p/'audio',p/'mobile',p/'review',p,m.render.ENGINE/'fonts/mobile']:
                    with self.assertRaises(ValueError):m.check_project(p,p/'renders/final.mp4',out)
            self.assertEqual(asset.read_text(),'keep');self.assertFalse((p/'mobile').exists())
            out=p/'unowned';out.mkdir();(out/'file.txt').write_text('keep')
            with self.assertRaisesRegex(ValueError,'not owned'):m.review_video(p/'master.mp4',out,times=[.2])
            self.assertEqual((out/'file.txt').read_text(),'keep')

    def test_publication_error_restores_previous_owned_directory(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            if os.name!='nt':
                # Exercise the same alias/canonical difference as Windows TEMP's
                # RUNNER~1 path, without requiring Windows symlink privileges.
                real=p/'real';real.mkdir();alias=p/'alias';alias.symlink_to(real,target_is_directory=True);p=alias
            v=p/'master.mp4';self.make(v);out=p/'mobile';out.mkdir();(out/'report.json').write_text(OLD)
            published=out.resolve()
            original=Path.replace
            def fail(src,dst):
                if src.name.startswith('.mobile-') and not src.name.startswith('.mobile-old-') and Path(dst)==published:raise OSError('publication failed')
                return original(src,dst)
            with patch.object(Path,'replace',fail):
                with self.assertRaisesRegex(OSError,'publication failed'):m.review_video(v,out,times=[.2])
            self.assertEqual((out/'report.json').read_text(),OLD)

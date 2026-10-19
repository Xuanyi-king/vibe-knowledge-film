"""Draft renders only needed inputs and never adopts stale music anchors."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from engine.provenance import digest
from scripts import produce

ROOT=Path(__file__).resolve().parents[1]


class DraftResourcesTest(unittest.TestCase):
    def test_explicit_visual_dependencies_are_still_prepared_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with patch.object(produce.subprocess,'run') as run:
                report=produce.produce(p,assets=('scene',),mode='draft',preview=('--stills',0))
                self.assertEqual(report['stages'],['assets-scene','fonts','preview'])
                self.assertTrue(run.call_args_list[0].args[0][1].endswith('get_scene_assets.py'))
            with patch.object(produce.subprocess,'run',side_effect=OSError('scene dependency unavailable')) as run:
                with self.assertRaisesRegex(OSError,'scene dependency'):produce.produce(p,assets=('scene',),mode='draft')
                self.assertEqual(run.call_count,1)
            self.assertEqual(json.loads((p/'review/draft.json').read_text())['status'],'failed')

    def test_music_anchor_plan_is_prepared_and_updated_before_preview(self):
        import numpy as np
        from scipy.io import wavfile
        with tempfile.TemporaryDirectory(prefix="vk 音乐 anchors '") as d:
            p=Path(d);(p/'assets').mkdir()
            audio=p/'assets/bed.wav'
            wavfile.write(audio,12000,(np.sin(np.arange(12000)*.15)*.2).astype(np.float32))
            cfg={'mode':'custom','src':'assets/bed.wav','source_sha256':digest(audio),'end':.3,
                 'rights':{'scope':'embed','statement':'Original generated test tone; CC0'},
                 'clips':[{'id':'bed','start':0,'source_in':0,'duration':.3}],
                 'anchors':[{'id':'reveal','clip':'bed','source_time':.1}]}
            (p/'music.json').write_text(json.dumps(cfg),encoding='utf-8')
            (p/'film.js').write_text('// Film is declared in the module below.')
            (p/'index.html').write_text('''<canvas id="stage"></canvas><script src="/engine/vk.js"></script>
              <script type="module">import {anchor} from './assets/music-plan.mjs';
              VK.film({dur:.3,grain:0,draw(fr){fr.rect(anchor('reveal')*200,10,20,20,{fill:'#abc'})}});</script>''',encoding='utf-8')
            args=dict(mode='draft',preview=('--stills',.1))
            first=produce.produce(p,**args)
            self.assertIn('music_preparation',first['stages'])
            self.assertNotIn('sound',first['stages'])
            self.assertFalse((p/'audio/score.wav').exists())
            image=p/'review/s_0000.10.png';before=image.read_bytes()
            # Existing plans can also be consumed without the checked adapter
            # or a literal path; keep them fresh rather than guessing usage.
            html=p/'index.html'
            html.write_text(html.read_text().replace("import {anchor} from './assets/music-plan.mjs';",
                "const {anchors}=await fetch('./assets/'+'music'+'-plan.json').then(r=>r.json());const anchor=id=>anchors[id];"),encoding='utf-8')
            self.assertNotIn('music-plan',html.read_text())
            cfg['anchors'][0]['source_time']=.2
            (p/'music.json').write_text(json.dumps(cfg),encoding='utf-8')
            produce.produce(p,**args)
            self.assertEqual(json.loads((p/'assets/music-plan.json').read_text())['anchors']['reveal'],.2)
            self.assertNotEqual(image.read_bytes(),before,'preview must use the changed anchor')
            current=image.read_bytes();audio.write_bytes(audio.read_bytes()+b'changed source')
            with self.assertRaises(subprocess.CalledProcessError):produce.produce(p,**args)
            self.assertEqual(image.read_bytes(),current,'failed preparation must not publish a fake preview')
            self.assertFalse((p/'renders/final.mp4').exists())
            self.assertFalse((p/'review/production.json').exists())

    def test_missing_visual_resource_fails_without_overwriting_release(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'renders').mkdir();(p/'review').mkdir()
            (p/'film.js').write_text('// Film is declared in the module below.')
            (p/'index.html').write_text('''<canvas id="stage"></canvas><script src="/engine/vk.js"></script>
              <script type="module">import './assets/missing-scene.mjs';VK.film({dur:.2,draw(){}});</script>''')
            protected=['renders/final.mp4','renders/final.mp4.provenance.json',
                       'review/production.json','review/production-cache.json']
            for name in protected:(p/name).write_bytes(b'previous release evidence')
            r=subprocess.run([sys.executable,str(ROOT/'scripts/produce.py'),str(p),
                              '--mode','draft','--stills','.1'],capture_output=True,text=True,timeout=60)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('missing-scene.mjs',r.stdout+r.stderr)
            for name in protected:self.assertEqual((p/name).read_bytes(),b'previous release evidence')
            self.assertEqual(json.loads((p/'review/draft.json').read_text())['status'],'failed')

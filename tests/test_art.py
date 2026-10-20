from pathlib import Path
import tempfile,unittest
from engine import render
ROOT=Path(__file__).resolve().parents[1]
THREE=(ROOT/'engine/vendor/three/three.module.min.js').exists()

def component_page(check):
    # Geometry/material tests need an origin and Canvas, not fold_C's font/network
    # startup. Legacy film and typography tests exercise that integration separately.
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)
        (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script>VK.film({dur:1,grain:0,draw(){}})</script>')
        render.with_page(p,check)

class TypographyTest(unittest.TestCase):
    def test_mobile_metadata_does_not_replace_legacy_character_layout(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script>VK.film({dur:1,grain:0,draw(fr){window.FR=fr;fr.chars("test",100,100,{size:48});}})</script>')
            def check(pg):
                a=render.shot(pg,.5)
                self.assertEqual(pg.evaluate('typeof FR.layout'),'function')
                self.assertEqual(pg.evaluate('FR.layout("test",100,{size:48}).length'),4)
                self.assertEqual(pg.evaluate('VK_LAYOUT()'),[])
                render.shot(pg,0);self.assertEqual(a,render.shot(pg,.5))
            render.with_page(p,check)

    def test_layout_metadata_resets_on_repeated_seek_without_changing_text(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);template=(ROOT/'engine/index.html').read_text()
            script="""<script type="module">import {type} from '/engine/vk-art.mjs';
            VK.film({dur:1,draw(fr,t){fr.x.save();if(t>.7){fr.x.translate(100,50);fr.x.scale(.5,.5);}
              type(fr,'距离',200,200,{role:'label',importance:'essential',id:'distance',background:'#131619'});fr.x.restore();}});</script>"""
            (p/'index.html').write_text(template.replace('<script src="film.js"></script>',script))
            def check(pg):
                first=render.shot(pg,.5);a=pg.evaluate('window.VK_LAYOUT?.() || []')
                self.assertEqual(len(a),1)
                self.assertEqual(a[0]['importance'],'essential');self.assertEqual(a[0]['id'],'distance')
                self.assertEqual(a[0]['text'],'距离');self.assertEqual(a[0]['style']['size'],42)
                self.assertEqual(first,render.shot(pg,.5));self.assertEqual(pg.evaluate('VK_LAYOUT().length'),1)
                render.shot(pg,.8);self.assertEqual(pg.evaluate('VK_LAYOUT().length'),1)
                scaled=pg.evaluate('VK_LAYOUT()[0]')
                self.assertEqual(scaled['style']['size'],21);self.assertAlmostEqual(scaled['left'],200)
            render.with_page(p,check)

    def test_roles_measure_real_text_and_reject_overflow_without_painting(self):
        self.assertTrue((ROOT/'engine/vk-art.mjs').exists(),'measured art-direction adapter missing')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            template=(ROOT/'engine/index.html').read_text()
            (p/'index.html').write_text(template.replace('<script src="film.js"></script>','<script>VK.film({dur:1,draw(fr){window.F=fr;}})</script>'))
            def check(pg):
                r=pg.evaluate('''async()=>{const A=await import('/engine/vk-art.mjs');
                  const box=A.type(F,'力臂与力矩',960,150,{role:'title',align:'c',maxWidth:1000});
                  const measured=F.measure('力臂与力矩',box.style);
                  // The first read can migrate Chromium's Canvas backing store.
                  // Establish readback before testing whether rejected calls paint.
                  F.x.getImageData(0,0,1920,1080);
                  const before=F.x.getImageData(0,0,1920,1080).data;let rejected=0;
                  for(const o of [{maxWidth:10},{role:'unknown'},{maxWidth:NaN}])try{A.type(F,'不能缩字掩盖越界',960,300,o)}catch(e){rejected++}
                  const after=F.x.getImageData(0,0,1920,1080).data;
                  return {box,measured,rejected,unchanged:before.every((v,i)=>v===after[i]),fill:F.x.fillStyle};}''')
                self.assertAlmostEqual(r['box']['width'],r['measured'],places=5)
                self.assertAlmostEqual(r['box']['left'],960-r['measured']/2,places=5)
                self.assertEqual(r['rejected'],3);self.assertTrue(r['unchanged'])
            render.with_page(p,check)

    def test_missing_font_declaration_cannot_silently_use_a_fallback(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'index.html').write_text('<canvas id="stage"></canvas><script src="/engine/vk.js"></script><script>VK.film({dur:1,draw(fr){window.F=fr;}})</script>')
            def check(pg):
                r=pg.evaluate('''async()=>{const A=await import('/engine/vk-art.mjs');try{A.type(F,'知识不是装饰',100,200);return ''}catch(e){return e.message}}''')
                self.assertIn('font',r)
            render.with_page(p,check)

class CinematicTest(unittest.TestCase):
    @unittest.skipUnless(THREE,'optional Three.js')
    def test_beveled_block_keeps_declared_dimensions(self):
        def check(pg):
            r=pg.evaluate('''async()=>{const A=await import('/engine/vk-cinematic.mjs'),M=await import('/engine/vk-scene.mjs');
              if(!A.beveledBlock)return {available:false};
              const mesh=A.beveledBlock([1.2,.3,.6],new M.THREE.MeshStandardMaterial(),{bevel:.02});
              const size=new M.THREE.Box3().setFromObject(mesh).getSize(new M.THREE.Vector3()).toArray();
              let invalid=false;try{A.beveledBlock([1,.02,1],mesh.material,{bevel:.1})}catch(e){invalid=true}
              mesh.geometry.dispose();mesh.material.dispose();return {available:true,size,invalid};}''')
            self.assertTrue(r['available'],'beveled geometry helper missing')
            for a,b in zip(r['size'],[1.2,.3,.6]):self.assertAlmostEqual(a,b,places=6)
            self.assertTrue(r['invalid'])
        component_page(check)

class TorqueTest(unittest.TestCase):
    @unittest.skipUnless(THREE and (ROOT/'examples/torque/assets/piano/bank.json').exists(),'optional Three.js/recorded piano bank')
    def test_moment_label_value_and_unit_wait_for_static_condition_together(self):
        def check(pg):
            for t in [53/30,54/30,55/30,2.699]:
                render.shot(pg,t)
                text=pg.evaluate('VK_LAYOUT().map(x=>x.text)')
                self.assertNotIn('N·m',text);self.assertNotIn('力矩',text);self.assertNotIn('—',text)
            render.shot(pg,2.7);text=pg.evaluate('VK_LAYOUT().map(x=>x.text)')
            for item in ['力矩','0.70','N·m','2 N']:self.assertIn(item,text)
        render.with_page(ROOT/'examples/torque',check)

    @unittest.skipUnless(THREE and (ROOT/'examples/torque/assets/piano/bank.json').exists(),'optional Three.js/recorded piano bank')
    def test_actual_mesh_lever_arm_and_rendered_conditions_replay(self):
        def check(pg):
            for time,expected in [(3.2,.35),(8.5,.70)]:
                frame=render.shot(pg,time);s=pg.evaluate('ART_SHOT.inspect()')
                distance=s['weightPosition'][0]-s['pivotPosition'][0]
                self.assertAlmostEqual(distance,expected,places=6)
                self.assertAlmostEqual(s['torque'],2*distance,places=6)
                render.shot(pg,.5);self.assertEqual(frame,render.shot(pg,time))
            for d in pg.evaluate('VK_CHECKS.list()'):
                render.shot(pg,d['time']);r=pg.evaluate('id=>VK_CHECKS.measure(id)',d['id'])
                self.assertTrue(r['passed'],r)
            self.assertEqual(pg.evaluate('ART_SHOT.inspect().glError'),0)
        render.with_page(ROOT/'examples/torque',check)

class SceneAdapterTest(unittest.TestCase):
    @unittest.skipUnless(THREE,'optional Three.js')
    def test_camera_projects_same_point_before_and_after_render_update(self):
        def check(pg):
            r=pg.evaluate('''async()=>{const M=await import('/engine/vk-motion.mjs'),{THREE:T}=await import('/engine/vk-scene.mjs');
              const c=new T.PerspectiveCamera(35,16/9,.1,100),keys=[[0,{position:[0,0,5],target:[0,0,0]}],[1,{position:[2,1,3],target:[.3,.2,0]}]];
              M.camera(c,keys,.75);const point=new T.Vector3(.6,.5,0),before=point.clone().project(c).toArray();
              c.updateMatrixWorld(true);return {before,after:point.project(c).toArray()};}''')
            for a,b in zip(r['before'],r['after']):self.assertAlmostEqual(a,b,places=10)
        component_page(check)

    @unittest.skipUnless(THREE,'optional Three.js')
    def test_studio_environment_hook_exposure_and_original_defaults(self):
        def check(pg):
            r=pg.evaluate('''async()=>{const M=await import('/engine/vk-scene.mjs');let calls=0;
              const a=M.studio({width:160,height:90,exposure:.8,environment(c,w,h){calls++;c.fillStyle='#111';c.fillRect(0,0,w,h)}});
              const b=M.studio({width:160,height:90});
              const out={calls,exposure:a.renderer.toneMappingExposure,fill:!!a.fill,
                defaults:[b.key.intensity,b.fill?.intensity,b.renderer.toneMappingExposure]};a.dispose();b.dispose();return out;}''')
            self.assertEqual(r['calls'],1);self.assertEqual(r['exposure'],.8);self.assertTrue(r['fill'])
            self.assertEqual(r['defaults'],[3.2,1.2,1.05])
        component_page(check)

    @unittest.skipUnless(THREE,'optional Three.js')
    def test_finish_is_seeded_disposable_and_scene_renders_repeatably(self):
        self.assertTrue((ROOT/'engine/vk-cinematic.mjs').exists(),'cinematic lighting/finish adapter missing')
        def check(pg):
            r=pg.evaluate('''async()=>{const A=await import('/engine/vk-cinematic.mjs'),M=await import('/engine/vk-scene.mjs');
              const a=A.brushedMetal({seed:8}),b=A.brushedMetal({seed:8}),c=A.brushedMetal({seed:9});let disposed=0;
              const same=a.roughnessMap.image.toDataURL()===b.roughnessMap.image.toDataURL(),different=a.roughnessMap.image.toDataURL()!==c.roughnessMap.image.toDataURL();
              a.roughnessMap.addEventListener('dispose',()=>disposed++);
              const S=A.cinematicStudio({width:320,height:180,position:[2,2,4],target:[0,0,0]}),cube=M.solid(new M.THREE.BoxGeometry(1,1,1),a);S.scene.add(cube);
              const cv=document.createElement('canvas');cv.width=320;cv.height=180;const ctx=cv.getContext('2d');
              const frame=t=>{cube.rotation.y=t;ctx.clearRect(0,0,320,180);S.render(ctx);return cv.toDataURL()};
              const first=frame(.2);frame(1.2);const replay=frame(.2);const error=S.renderer.getContext().getError();
              let invalid=false;try{A.brushedMetal({roughness:-1})}catch(e){invalid=true}
              S.dispose();b.dispose();c.dispose();return {same,different,disposed,replay:first===replay,error,invalid};}''')
            self.assertTrue(r['same']);self.assertTrue(r['different']);self.assertEqual(r['disposed'],1)
            self.assertTrue(r['replay']);self.assertEqual(r['error'],0);self.assertTrue(r['invalid'])
        component_page(check)

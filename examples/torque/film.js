import {THREE as T,studio,solid,rod,surface,lathe} from '/engine/vk-scene.mjs';
import {cinematicStudio,brushedMetal,beveledBlock} from '/engine/vk-cinematic.mjs';
import {type,INK} from '/engine/vk-art.mjs';
import * as M from '/engine/vk-motion.mjs';
import {visualChecks} from '/engine/vk-checks.mjs';
import {SCORE} from './score.mjs';

export async function makeFilm(variant='cinematic') {
 const cinematic=variant==='cinematic';window.VK_SCORE=SCORE;
 const seat=SCORE.event('seat'),slide=SCORE.event('slide'),reveal=SCORE.event('reveal');
 const config={position:[1.2,1.2,3.1],target:[.45,.46,0],fov:30};
 const S=cinematic?cinematicStudio({...config,focus:[.3,.55,0]}):studio(config);
 // Local bounce restores the near support faces without lifting the background.
 const bounce=new T.PointLight('#e0d0b6',.8,2.8,2);bounce.position.set(.65,.85,1.15);S.scene.add(bounce);
 S.scene.background=new T.Color(INK.black);S.scene.fog=new T.Fog(INK.black,5,13);
 const bronze=cinematic?brushedMetal({seed:16,color:'#b6a381'}):surface({seed:16,color:'#b6a381',metalness:.88,roughness:.46});
 const steel=cinematic?brushedMetal({seed:22,color:'#8d9797',roughness:.6}):surface({seed:22,color:'#8d9797',metalness:.88,roughness:.6});
 const graphite=surface({seed:9,color:'#3a4245',metalness:0,roughness:.92,grain:.10,bump:.001});
 const ceramic=surface({seed:11,color:'#dce0da',metalness:0,roughness:.6,grain:.04,bump:.0005});
 const floor=solid(new T.PlaneGeometry(100,100),surface({color:'#24282b',metalness:0,roughness:.86,grain:.09,bump:.0005}));floor.rotation.x=-Math.PI/2;floor.position.y=-.015;floor.castShadow=false;S.scene.add(floor);
 const base=beveledBlock([1.65,.10,.65],graphite,{bevel:.018});base.position.set(.28,.05,0);S.scene.add(base);
 const pedestal=beveledBlock([.18,.36,.22],graphite,{bevel:.012});pedestal.position.y=.28;S.scene.add(pedestal);
 const pivot=solid(new T.CylinderGeometry(.08,.08,.28,48),bronze);pivot.rotation.x=Math.PI/2;pivot.position.y=.5;S.scene.add(pivot);
 const cap=solid(new T.CylinderGeometry(.051,.051,.012,6),steel);cap.rotation.x=Math.PI/2;cap.position.set(0,.5,.148);S.scene.add(cap);
 const bearing=solid(new T.TorusGeometry(.067,.006,12,64),bronze);bearing.position.set(0,.5,.147);S.scene.add(bearing);
 const arm=beveledBlock([1.05,.055,.105],steel,{bevel:.007});arm.position.set(.37,.5,0);S.scene.add(arm);
 const carrier=beveledBlock([.24,.08,.18],graphite,{bevel:.008});carrier.position.y=.5675;S.scene.add(carrier);
 const weight=lathe([[0,0],[.075,0],[.092,.014],[.092,.26],[.077,.28],[0,.28]],ceramic,64);S.scene.add(weight);
 const ring=solid(new T.TorusGeometry(.06,.012,12,48),steel);ring.rotation.x=Math.PI/2;ring.position.y=.29;weight.add(ring);
 // Small real screws/feet anchor scale and support. No decorative particle field.
 for(const x of [-.4,.96])for(const z of [-.23,.23]){
   const foot=solid(new T.CylinderGeometry(.035,.038,.035,24),graphite);foot.position.set(x,.002,z);S.scene.add(foot);
   const screw=solid(new T.CylinderGeometry(.012,.012,.014,20),bronze);screw.position.set(x,.106,z);S.scene.add(screw);
 }
 const forceRod=rod(new T.MeshBasicMaterial({color:INK.blue}),.005);S.scene.add(forceRod);
 const arrow=solid(new T.ConeGeometry(.02,.055,24),new T.MeshBasicMaterial({color:INK.blue}));arrow.rotation.z=Math.PI;S.scene.add(arrow);
 const finalCamera={position:[1.0,1.12,2.85],target:[.46,.39,0],fov:30};
 const keys=[[0,config],[2.8,config],[5.8,finalCamera],[14,finalCamera]];
 let state={},boxes=[];
 window.VK_MOBILE_TIMES=[53/30,54/30,55/30,3.2,5.35,8.5,12];
 function pose(t){
   const x=M.track([[0,.35],[slide.start,.35],[slide.end,.70],[14,.70]],t);
   carrier.position.x=x;const dt=t-seat.start;
   const drop=t<seat.start?.15*(1-M.smooth((t-(seat.start-.65))/.65)):Math.max(0,M.impulse(dt,{velocity:.18,frequency:3.2,damping:.65}));
   weight.position.set(x,.6075+(dt>.7?0:drop),0);
   // A small bearing response is prescribed secondary motion, not free rotation.
   arm.rotation.z=M.impulse(dt,{velocity:.006,frequency:7,damping:.65});
   const applied=t>=2.7?2:0;
   forceRod.visible=arrow.visible=!!applied;
   forceRod.between([x,1.05,0],[x,.97,0]);forceRod.visible=!!applied;arrow.position.set(x,.94,0);
   M.camera(S.camera,keys,t);S.scene.updateMatrixWorld(true);
   const w=weight.getWorldPosition(new T.Vector3()),p=pivot.getWorldPosition(new T.Vector3()),r=w.clone().sub(p),F=new T.Vector3(0,-applied,0);
   state={r:w.x-p.x,force:applied,torque:r.cross(F).length(),gap:new T.Box3().setFromObject(weight).min.y-new T.Box3().setFromObject(carrier).max.y,static:t>=2.7};
 }
 const project=(x,y,z=0)=>{const p=new T.Vector3(x,y,z).project(S.camera);return [(p.x+1)*960,(1-p.y)*540];};
 const add=(fr,text,x,y,options)=>{const b=type(fr,text,x,y,options);boxes.push(b);return b;};
 window.ART_SHOT={inspect(){return {...state,contactScreen:project(state.r,.6075),weightPosition:weight.getWorldPosition(new T.Vector3()).toArray(),pivotPosition:pivot.getWorldPosition(new T.Vector3()).toArray(),boxes,variant,glError:S.renderer.getContext().getError()};}};
 window.VK_CHECKS=visualChecks(SCORE,[
  {id:'before-contact',event:'seat',offset:-1/30,min:.001,max:.1,measure:()=>state.gap,unit:'m'},
  {id:'contact',event:'seat',min:-.0001,max:.0001,measure:()=>state.gap,unit:'m'},
  {id:'recoil',event:'seat',offset:1/30,min:.001,max:.02,measure:()=>state.gap,unit:'m'},
  {id:'short-arm',event:'slide',min:.34999,max:.35001,measure:()=>state.r,unit:'m'},
  {id:'long-arm',event:'reveal',min:.69999,max:.70001,measure:()=>state.r,unit:'m'},
  {id:'computed-moment',event:'reveal',min:1.39999,max:1.40001,measure:()=>state.torque,unit:'N m'},
  {id:'unchanged-force',event:'reveal',min:1.99999,max:2.00001,measure:()=>state.force,unit:'N'},
  {id:'caption-bounds',event:'hold',min:0,max:0,measure:()=>boxes.reduce((n,b)=>n+(b.left<96||b.left+b.width>1824||b.top<43||b.top+b.height>1037?1:0),0),unit:'layout bounds outside safe area'},
 ]);
 VK.film({dur:14,theme:'flat',bloom:0,grain:0,meta:{title:'力的远近',drone:0},draw(fr,t){
   pose(t);boxes=[];fr.look.under=c=>S.render(c);
   add(fr,'力的远近',112,132,{role:'title',size:84});
   add(fr,'锁角静载示意',114,235,{role:'label',size:72,importance:'essential',color:'#c8ccc2'});
   const p=project(state.r,.97);if(state.static)add(fr,'2 N',p[0]+34,p[1],{role:'label',importance:'essential',color:INK.ivory,size:84});
   // One changing dimension, anchored to actual pivot/load, replaces three tiny ticks.
   const a=project(0,.31,.14),b=project(state.r,.31,.14);
   fr.line(a[0],a[1],b[0],b[1],{w:6,color:INK.ivory});
   for(const point of [a,b])fr.line(point[0],point[1]-14,point[0],point[1]+14,{w:6,color:INK.ivory});
   add(fr,`${state.r.toFixed(2)} m`,(a[0]+b[0])/2,(a[1]+b[1])/2+68,{role:'label',importance:'essential',align:'c',size:78,font:'mono',color:INK.ivory});
   // Force stays beside its object; removing the duplicate F block gives the comparison air.
   add(fr,'力臂',1360,435,{role:'label',size:72,importance:'essential',color:INK.ivory});
   add(fr,`${state.r.toFixed(2)} m`,1360,530,{role:'number',size:96,color:INK.ivory,maxWidth:464});
   add(fr,'力矩',1360,680,{role:'label',size:72,importance:'essential',color:INK.ivory});
   add(fr,state.static?state.torque.toFixed(2):'—',1360,785,{role:'number',size:112,color:t>=reveal.start?INK.gold:INK.ivory,maxWidth:300});
   add(fr,'N·m',1672,797,{role:'label',importance:'essential',font:'mono',size:74,color:INK.ivory,maxWidth:152});
   // The larger caption supplies the conclusion; no extra tiny gold sentence.
   const caption=t<2.7?'同样的力，换个位置会怎样？':t<7.7?'保持 2 N，只把施力点移远。':'力臂翻倍，力矩也翻倍。';
   add(fr,caption,960,973,{role:'caption',size:84,align:'c',maxWidth:1660});
 }});
}

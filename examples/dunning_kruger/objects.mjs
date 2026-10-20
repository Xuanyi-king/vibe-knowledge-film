// Reuse the original optional scene layer: actual perspective, PBR and contact shadows.
import {THREE as T,studio,rod,surface,solid} from '/engine/vk-scene.mjs';
import * as M from '/engine/vk-motion.mjs';
export const vertices=[[-2.12,0,-1.45],[2.12,0,-1.45],[0,0,2.05],[0,0,-.05]];
export const edges=[[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]];
export const openingPath=[0,1,2,0,3,1];
export const endingPath=[2,0,3,1,2,3];
export function instrument(){
 const L=studio({position:[4,5,7],target:[0,0,.05],fov:35,shadowSize:1024,exposure:1.06});
 L.scene.environmentIntensity=.4;L.fill.intensity=.35;L.key.intensity=2.8;
 L.scene.fog=new T.FogExp2('#080a0f',.035);
 const group=new T.Group();L.scene.add(group);
 const brass=surface({seed:18,color:'#b99859',metalness:.83,roughness:.3,grain:.08});
 const ivory=new T.MeshStandardMaterial({color:'#e7dfc9',metalness:.1,roughness:.26});
 const dull=surface({seed:21,color:'#555045',metalness:.7,roughness:.42});
 const ink=surface({seed:82,color:'#101219',metalness:.28,roughness:.48,grain:.1});
 const red=new T.MeshStandardMaterial({color:'#8e4037',metalness:.55,roughness:.4});
 const gold=new T.MeshStandardMaterial({color:'#edcd87',metalness:.7,roughness:.23,emissive:'#5d3812',emissiveIntensity:.16});
 const lifted=brass.clone();lifted.transparent=true;
 const base=solid(new T.CylinderGeometry(3.13,3.22,.16,128),ink);base.position.y=-.18;group.add(base);
 const rim=solid(new T.TorusGeometry(3.16,.024,12,160),brass);rim.rotation.x=Math.PI/2;rim.position.y=-.11;group.add(rim);
 const foot=solid(new T.CylinderGeometry(2.95,3.02,.11,128),dull);foot.position.y=-.3;group.add(foot);
 const lines=edges.map(([a,b])=>{
  const dark=rod(dull,.026),active=rod(gold,.029);group.add(dark,active);
  dark.between(vertices[a].map((v,i)=>i===1?.03:v),vertices[b].map((v,i)=>i===1?.03:v));
  return {dark,active,a,b};
 });
 const pins=vertices.map(v=>{
  const g=new T.Group();g.position.fromArray(v);group.add(g);
  const collar=solid(new T.CylinderGeometry(.16,.19,.045,40),brass);collar.position.y=.04;g.add(collar);
  const cap=solid(new T.SphereGeometry(.095,32,24),ivory);cap.position.y=.105;cap.scale.y=.52;g.add(cap);
  return {g,cap,collar};
 });
 // The nib is a recognisable little metal pen, not an emissive dot.
 const pen=new T.Group();group.add(pen);
 const body=solid(new T.CylinderGeometry(.04,.047,.7,24),ink);body.rotation.z=-.52;body.position.set(.15,.43,0);pen.add(body);
 const nib=solid(new T.ConeGeometry(.055,.22,24),brass);nib.rotation.z=Math.PI-.52;nib.position.set(.025,.11,0);pen.add(nib);
 const floor=solid(new T.PlaneGeometry(100,100),new T.ShadowMaterial({opacity:.35}));
 floor.rotation.x=-Math.PI/2;floor.position.y=-.36;L.scene.add(floor);
 function show(ctx,t,{path=openingPath,progress=0,removed=0,mark=0,markList=null,alpha=1,pose=null}={}){
  group.position.set(0,0,0);group.rotation.set(0,0,0);
  const cam=pose||{position:[3.3,5.7,7.3],target:[0,.0,0],fov:35};
  M.camera(L.camera,[[0,cam]],t);
  const visited=new Map();let cursor=vertices[path[0]];
  for(let j=0;j<path.length-1;j++){
   const a=path[j],b=path[j+1],q=Math.max(0,Math.min(1,progress-j));
   if(q>0)visited.set([Math.min(a,b),Math.max(a,b)].join(','),{a,b,q});
   if(progress>=j&&progress<=j+1)cursor=vertices[a].map((v,i)=>v+(vertices[b][i]-v)*q);
  }
  if(progress>=path.length-1)cursor=vertices[path.at(-1)];
  lines.forEach(({dark,active,a,b},i)=>{
   const e=visited.get([Math.min(a,b),Math.max(a,b)].join(','));
   dark.visible=!(i===0&&removed>=.99);dark.position.y=(i===0?removed*.7:0)+.03;
   if(i===0&&removed>0){dark.material=lifted;lifted.opacity=1-M.smooth((removed-.1)/.9);}
   else dark.material=!e&&progress>=path.length-1?red:dull;
   active.visible=!!e;
   if(e){const av=vertices[e.a].map((v,i)=>i===1?.065:v),bv=vertices[e.a].map((v,i)=>i===1?.065:v+(vertices[e.b][i]-v)*e.q);active.between(av,bv);}
  });
  pins.forEach((p,i)=>{p.collar.material=(markList?markList.includes(i):i<mark)?red:brass;});
  pen.position.set(cursor[0],.04,cursor[2]);pen.visible=progress>0;
  ctx.save();ctx.globalAlpha=alpha;L.render(ctx);ctx.restore();
  return {position:pen.position.toArray(),drawn:lines.filter(e=>e.active.visible).length,
   remaining:lines.filter(e=>e.dark.visible&&!e.active.visible).length,
   visibleEdges:lines.filter(e=>e.dark.visible).length,removed};
 }
 function project(world){const p=new T.Vector3(...world).project(L.camera);return[(p.x+1)*960,(1-p.y)*540];}
 return {show,project,L};
}

import {THREE as T,studio,solid} from '/engine/vk-scene.mjs';
export async function portrait(){
 const data=await (await fetch('assets/portrait.json')).json();
 const S=studio({width:768,height:896,shadowSize:1024,fov:25,position:[0,0,1.6],target:[0,0,.1]});
 S.scene.background=new T.Color('#e2d9ca');S.scene.environmentIntensity=.45;S.key.intensity=2.8;S.key.position.set(-.5,.6,.85);
 S.key.shadow.camera.left=-.35;S.key.shadow.camera.right=.35;S.key.shadow.camera.top=.35;S.key.shadow.camera.bottom=-.35;S.key.shadow.camera.near=.1;S.key.shadow.camera.far=3;S.key.shadow.normalBias=.0003;
 const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(data.positions.flat(),3));g.setIndex(data.triangles.flat());g.computeVertexNormals();
 const body=solid(g,new T.MeshStandardMaterial({color:'#b4ada1',roughness:.72}));S.scene.add(body);
 const offwhite=new T.MeshStandardMaterial({color:'#ded7cc',roughness:.34});
 const brown=new T.MeshStandardMaterial({color:'#79776f',roughness:.5});
 const black=new T.MeshStandardMaterial({color:'#4e4d48',roughness:.3});
 for(const x of [-.030775,.030775]){
  const eye=solid(new T.SphereGeometry(.0133,32,24),offwhite);eye.position.set(x,.018415,.124535);S.scene.add(eye);
  const iris=solid(new T.SphereGeometry(.005,24,16),brown);iris.scale.set(1,1,.25);iris.position.set(x,.018415,.1374);S.scene.add(iris);
  const pupil=solid(new T.SphereGeometry(.0025,20,12),black);pupil.scale.z=.2;pupil.position.set(x,.018415,.1383);S.scene.add(pupil);
 }
 const canvas=document.createElement('canvas');canvas.width=768;canvas.height=896;const ctx=canvas.getContext('2d');
 const cheekZ=data.landmarks.cheek.map(i=>data.positions[i][2]).reduce((a,b)=>a+b)/2;
 function set(distance=1.5,{yaw=0,light=0}={}){
  body.rotation.set(0,0,0); // State is absolute; no model deformation for the distance comparison.
  S.key.position.set(-.5+light,.6,.85);
  S.camera.position.set(Math.sin(yaw)*distance,0,cheekZ+Math.cos(yaw)*distance);
  S.camera.lookAt(0,0,cheekZ);S.camera.fov=2*Math.atan(.155/distance)*180/Math.PI;S.camera.updateProjectionMatrix();
  S.render(ctx);
 }
 const width=ids=>{body.updateMatrixWorld(true);S.camera.updateMatrixWorld(true);const p=ids.map(i=>new T.Vector3().fromBufferAttribute(g.attributes.position,i).applyMatrix4(body.matrixWorld).project(S.camera));return Math.abs(p[1].x-p[0].x);};
 function metrics(){const points=data.landmarks.nose.map(i=>new T.Vector3().fromBufferAttribute(g.attributes.position,i).applyMatrix4(body.matrixWorld).project(S.camera).toArray());return {distance:S.camera.position.distanceTo(new T.Vector3(0,0,cheekZ)),noseWidth:width(data.landmarks.nose),cheekWidth:width(data.landmarks.cheek),nosePoints:points,glError:S.renderer.getContext().getError()};}
 set();const base=document.createElement('canvas');base.width=768;base.height=896;base.getContext('2d').drawImage(canvas,0,0);
 const flipped=document.createElement('canvas');flipped.width=768;flipped.height=896;const fc=flipped.getContext('2d');fc.translate(768,0);fc.scale(-1,1);fc.drawImage(base,0,0);
 const a=base.getContext('2d').getImageData(0,0,768,896).data,b=fc.getImageData(0,0,768,896).data;let pixelMirrorError=0;
 for(let y=0;y<896;y+=19)for(let x=0;x<768;x+=13)for(let k=0;k<4;k++)pixelMirrorError=Math.max(pixelMirrorError,Math.abs(a[(y*768+x)*4+k]-b[(y*768+767-x)*4+k]));
 // FNV is a repeatability label, not security; media provenance uses SHA256.
 const geometryHash=()=>{let hash=2166136261;for(const v of g.attributes.position.array){hash^=Math.round(v*1e6);hash=Math.imul(hash,16777619);}return (hash>>>0).toString(16);};
 return {set,metrics,canvas,base,flipped,pixelMirrorError,geometryHash,scene:S};
}

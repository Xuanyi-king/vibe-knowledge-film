/* Optional art tools. No props, timeline, fixed camera move or music embedded. */
import {THREE as T,studio,solid} from './vk-scene.mjs';

// Three's mature extrusion supplies bevel normals and topology. Dimensions
// include the bevel; declared contact/bounds need not compensate for it.
export function beveledBlock(size,material,{bevel=.01,segments=3}={}) {
  if(size.length!==3||!size.every(v=>Number.isFinite(v)&&v>2*bevel)||!(bevel>0)||!Number.isInteger(segments)||segments<1)throw Error('bevel must fit inside all positive dimensions');
  const [w,h,d]=size.map(v=>v-2*bevel),shape=new T.Shape();
  shape.moveTo(-w/2,-h/2);shape.lineTo(w/2,-h/2);shape.lineTo(w/2,h/2);shape.lineTo(-w/2,h/2);shape.closePath();
  const geometry=new T.ExtrudeGeometry(shape,{depth:d,steps:1,bevelEnabled:true,bevelThickness:bevel,bevelSize:bevel,bevelSegments:segments});
  geometry.translate(0,0,-d/2);return solid(geometry,material);
}

export function softboxes(c,w,h) {
  const g=c.createLinearGradient(0,0,0,h);
  g.addColorStop(0,'#0c141c');g.addColorStop(.52,'#373d40');g.addColorStop(1,'#0a0d10');
  c.fillStyle=g;c.fillRect(0,0,w,h);
  function panel(x,y,ww,hh,color) {
    const g=c.createLinearGradient(x,0,x+ww,0);
    g.addColorStop(0,'#0000');g.addColorStop(.15,color);g.addColorStop(.85,color);g.addColorStop(1,'#0000');
    c.fillStyle=g;c.fillRect(x,y,ww,hh);
  }
  panel(.06*w,.12*h,.18*w,.45*h,'#ffe6c5');
  panel(.60*w,.18*h,.07*w,.5*h,'#a3bbcc');
}

// Default is a starting rig; focus, light positions and ratios follow the shot.
export function cinematicStudio({focus=[0,.6,0],keyPosition=[-3,5,3],rimPosition=[2,3,-3],keyPower=3,fillPower=.28,rimPower=1.3,environmentPower=.38,...options}={}) {
  const S=studio({exposure:.95,shadowSize:2048,environment:softboxes,...options});
  S.key.color.set('#ffe7c7');S.key.intensity=keyPower;S.key.position.fromArray(keyPosition);
  S.key.target.position.fromArray(focus);S.scene.add(S.key.target);
  S.key.shadow.normalBias=.003;S.key.shadow.bias=-.00008;
  S.renderer.shadowMap.type=T.PCFShadowMap;S.key.shadow.radius=3;
  S.fill.intensity=fillPower;S.fill.color.set('#9cabb4');S.fill.groundColor.set('#3d332c');
  const rim=new T.DirectionalLight('#aabecb',rimPower);rim.position.fromArray(rimPosition);
  rim.target.position.fromArray(focus);S.scene.add(rim,rim.target);
  S.scene.environmentIntensity=environmentPower;
  return {...S,rim};
}

// Real roughness/bump and anisotropic PBR, with stable object-UV striations.
// Not a painted specular streak. Turn/resize the object to inspect response.
export function brushedMetal({seed=1,color='#b6a381',roughness=.46,anisotropy=.45,bump=.0008}={}) {
  if(![roughness,anisotropy,bump].every(Number.isFinite)||roughness<0||roughness>1||anisotropy<0||anisotropy>1||bump<0)throw Error('invalid metal finish');
  const cv=document.createElement('canvas');cv.width=cv.height=128;
  const c=cv.getContext('2d'),pixels=c.createImageData(128,128);let state=seed>>>0;
  const random=()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296;};
  for(let y=0;y<128;y++){
    const band=(random()-.5)*24;
    for(let x=0;x<128;x++){
      const v=Math.round(192+band+(random()-.5)*5),i=(y*128+x)*4;pixels.data.set([v,v,v,255],i);
    }
  }
  c.putImageData(pixels,0,0);const map=new T.CanvasTexture(cv);map.wrapS=map.wrapT=T.RepeatWrapping;
  const material=new T.MeshPhysicalMaterial({color,metalness:.88,roughness,anisotropy,roughnessMap:map,bumpMap:map,bumpScale:bump});
  material.addEventListener('dispose',()=>map.dispose());return material;
}

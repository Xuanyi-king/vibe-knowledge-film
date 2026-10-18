/* Optional real-depth scene layer; Three.js is installed separately, MIT. */
import * as THREE from './vendor/three/three.module.min.js';
export {THREE};

// Model a surface of revolution without implementing triangulation or normals.
export function lathe(profile, material, segments=64) {
  return solid(new THREE.LatheGeometry(profile.map(p=>new THREE.Vector2(...p)),segments),material);
}
export function solid(geometry,material) {
  const mesh=new THREE.Mesh(geometry,material);
  mesh.castShadow=true;mesh.receiveShadow=true;return mesh;
}
// Cylinder axis, quaternion and length are maintained by the library. Reuse for
// linkages, molecular bonds, struts; set both endpoints on every seek.
export function rod(material,radius=.025) {
  const mesh=solid(new THREE.CylinderGeometry(radius,radius,1,16),material);
  const y=new THREE.Vector3(0,1,0),a=new THREE.Vector3(),b=new THREE.Vector3(),d=new THREE.Vector3();
  mesh.between=(from,to)=>{
    a.fromArray(from);b.fromArray(to);d.subVectors(b,a);
    const length=d.length();
    mesh.visible=length>1e-9;
    if(mesh.visible){mesh.position.copy(a).add(b).multiplyScalar(.5);mesh.scale.set(1,length,1);mesh.quaternion.setFromUnitVectors(y,d.divideScalar(length));}
    return mesh;
  };
  return mesh;
}

// A seeded micro-finish modifies actual PBR roughness/normals, not painted highlights.
// UV scale is object-specific; large grain can falsely suggest corrosion.
export function surface({seed=1,grain=.07,bump=.003,...parameters}={}) {
  const canvas=document.createElement('canvas');canvas.width=256;canvas.height=256;
  const c=canvas.getContext('2d'),pixels=c.createImageData(256,256);let state=seed>>>0;
  for(let i=0;i<pixels.data.length;i+=4){state=(Math.imul(state,1664525)+1013904223)>>>0;
    const v=Math.round(210+(state/4294967296-.5)*255*grain);pixels.data.set([v,v,v,255],i);}
  c.putImageData(pixels,0,0);const texture=new THREE.CanvasTexture(canvas);
  texture.wrapS=texture.wrapT=THREE.RepeatWrapping;
  const material=new THREE.MeshStandardMaterial({roughness:.4,...parameters,roughnessMap:texture,bumpMap:texture,bumpScale:bump});
  material.addEventListener('dispose',()=>texture.dispose());return material;
}

export function studio({width=1920,height=1080,target=[0,1,0],position=[4,3,6],fov=36,shadowSize=1024}={}) {
  let renderer;
  try {renderer=new THREE.WebGLRenderer({alpha:true,antialias:true,preserveDrawingBuffer:true});}
  catch(e){throw new Error('WebGL2 unavailable: use current Chrome/Chromium with a working GPU or VK_SOFTWARE_GL=1. '+e.message);}
  renderer.setPixelRatio(1);renderer.setSize(width,height,false);
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(fov,width/height,.1,100);
  camera.position.fromArray(position);camera.lookAt(...target);
  // Procedural softboxes are an environment, not a painted object highlight.
  // PMREM supplies roughness-dependent reflections to standard PBR materials.
  const canvas=document.createElement('canvas');canvas.width=512;canvas.height=256;
  const c=canvas.getContext('2d'),gradient=c.createLinearGradient(0,0,0,256);
  gradient.addColorStop(0,'#cbd5db');gradient.addColorStop(.55,'#6a747c');gradient.addColorStop(1,'#242d36');
  c.fillStyle=gradient;c.fillRect(0,0,512,256);
  c.fillStyle='#fff4df';c.fillRect(40,35,90,110);
  c.fillStyle='#eff9ff';c.fillRect(300,55,45,120);
  const env=new THREE.CanvasTexture(canvas);env.mapping=THREE.EquirectangularReflectionMapping;env.colorSpace=THREE.SRGBColorSpace;
  const pmrem=new THREE.PMREMGenerator(renderer),map=pmrem.fromEquirectangular(env);
  scene.environment=map.texture;env.dispose();pmrem.dispose();
  const key=new THREE.DirectionalLight('#fff3df',3.2);key.position.set(-3,6,4);key.castShadow=true;
  key.shadow.mapSize.set(shadowSize,shadowSize);key.shadow.camera.left=-3;key.shadow.camera.right=3;
  key.shadow.camera.top=4;key.shadow.camera.bottom=-2;key.shadow.camera.near=.5;key.shadow.camera.far=15;
  key.shadow.bias=-.0002;key.shadow.normalBias=.025;scene.add(key);
  const fill=new THREE.HemisphereLight('#d9eeff','#404952',1.2);scene.add(fill);
  const gl=renderer.getContext(),ext=gl.getExtension('WEBGL_debug_renderer_info');
  window.VK_SCENE_INFO={three:THREE.REVISION,renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)};
  return {scene,camera,renderer,key,
    render(ctx){if(gl.isContextLost())throw new Error('WebGL context lost; restart render to resume valid segments');renderer.render(scene,camera);ctx.drawImage(renderer.domElement,0,0,width,height);},
    dispose(){scene.traverse(n=>{n.geometry?.dispose();if(n.material)for(const m of [n.material].flat())m.dispose();});map.dispose();renderer.dispose();},
  };
}

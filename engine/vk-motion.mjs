/* Absolute-time choreography. No timers, integration state, or render-order dependence. */
const finite=(n,name)=>{if(!Number.isFinite(n))throw Error(`${name} must be finite`);return n;};
const clamp=x=>Math.max(0,Math.min(1,x));
const mix=(a,b,u)=>Array.isArray(a)?a.map((v,i)=>mix(v,b[i],u)):a+(b-a)*u;
export const smooth=u=>{u=clamp(u);return u*u*(3-2*u);};
export function track(keys,t,{ease=smooth}={}) {
  if(!keys.length||keys.some((k,i)=>!Number.isFinite(k[0])||(i&&k[0]<=keys[i-1][0])))throw Error('track times must increase');
  if(t<=keys[0][0])return structuredClone(keys[0][1]);
  for(let i=1;i<keys.length;i++)if(t<keys[i][0])return mix(keys[i-1][1],keys[i][1],ease((t-keys[i-1][0])/(keys[i][0]-keys[i-1][0])));
  return structuredClone(keys.at(-1)[1]);
}
// Solution of x'' + 2*zeta*omega*x' + omega²*x = 0, in seconds.
function response(t,x,v,frequency,damping) {
  if(!(frequency>0&&damping>=0))throw Error('frequency > 0 and damping >= 0 required');
  if(t<0)return x;
  const w=2*Math.PI*frequency,z=damping;
  if(Math.abs(z-1)<1e-6)return (x+(v+w*x)*t)*Math.exp(-w*t);
  if(z<1){const d=w*Math.sqrt(1-z*z);return Math.exp(-z*w*t)*(x*Math.cos(d*t)+(v+z*w*x)/d*Math.sin(d*t));}
  const q=Math.sqrt(z*z-1),r1=-w/(z+q),r2=-w*(z+q),a=(v-r2*x)/(r1-r2);
  return a*Math.exp(r1*t)+(x-a)*Math.exp(r2*t);
}
export function spring(t,{from=0,to=1,velocity=0,frequency=2,damping=.7}={}) {
  return to+response(t,from-to,velocity,frequency,damping);
}
export function impulse(t,{velocity=1,frequency=3,damping=.2}={}) {
  return t<0?0:response(t,0,velocity,frequency,damping);
}
export function path(points,u) {
  if(points.length!==4)throw Error('cubic path needs four control points');
  u=clamp(u);const [a,b,c,d]=points,s=1-u;
  return a.map((v,i)=>s*s*s*v+3*s*s*u*b[i]+3*s*u*u*c[i]+u*u*u*d[i]);
}
export function score(input) {
  const data=structuredClone(input);if(!(data.end>0))throw Error('score end must be positive');
  data.version=1;data.fps??=30;data.tempo??=[{beat:0,bpm:120}];data.shots??=[];data.events??=[];
  if(!(data.fps>0))throw Error('fps must be positive');
  let seconds=0;
  const tempo=data.tempo.map((p,i)=>{
    if(!(p.bpm>0)||!Number.isFinite(p.beat)||(i?p.beat<=data.tempo[i-1].beat:p.beat!==0))throw Error('tempo starts at beat 0 and increases; bpm > 0');
    if(i)seconds+=(p.beat-data.tempo[i-1].beat)*60/data.tempo[i-1].bpm;
    return {...p,seconds};
  });
  function time(beat){finite(beat,'beat');const p=tempo.findLast(p=>p.beat<=beat)||tempo[0];return p.seconds+(beat-p.beat)*60/p.bpm;}
  function beat(t){finite(t,'time');const p=tempo.findLast(p=>p.seconds<=t)||tempo[0];return p.beat+(t-p.seconds)*p.bpm/60;}
  const shots=new Map();for(const s of data.shots){if(!s.id||shots.has(s.id)||!(s.start>=0&&s.end>s.start&&s.end<=data.end))throw Error('invalid/duplicate shot');shots.set(s.id,s);}
  const events=new Map();data.events=data.events.map(e=>{
    if(!e.id||events.has(e.id))throw Error('event IDs must be unique');
    if(e.shot&&!shots.has(e.shot))throw Error(`unknown shot ${e.shot}`);
    if(e.start!==undefined&&e.beat!==undefined)throw Error('choose start or beat');
    const start=e.beat!==undefined?time(e.beat):(shots.get(e.shot)?.start||0)+finite(e.start??0,'event start');
    const end=e.end!==undefined?e.end:start+(e.duration??0);
    if(!(start>=0&&end>=start&&end<=data.end))throw Error(`event ${e.id} outside timeline`);
    if(e.shot&&(start<shots.get(e.shot).start||end>shots.get(e.shot).end))throw Error(`event ${e.id} outside shot`);
    const result={...e,start,end};events.set(e.id,result);return result;
  });
  // Export a snapshot, so downstream code cannot silently retime registered events.
  return {time,beat,event(id){if(!events.has(id))throw Error(`unknown event ${id}`);return structuredClone(events.get(id));},json(){return structuredClone(data);}};
}
// Focal position, target and field-of-view share key times; repeated poses make holds.
const cameraDefaults=new WeakMap();
export function camera(camera,keys,t) {
  if(!cameraDefaults.has(camera))cameraDefaults.set(camera,camera.fov);
  const baseFov=cameraDefaults.get(camera);
  const pose=track(keys.map(([s,p])=>[s,[...p.position,...p.target,p.fov??baseFov]]),t);
  camera.position.fromArray(pose.slice(0,3));camera.lookAt(...pose.slice(3,6));camera.fov=pose[6];camera.updateProjectionMatrix();
  // Overlay labels may project before renderer.render(). Update the view matrix
  // here too, otherwise their position depends on the previously sought frame.
  camera.updateMatrixWorld?.(true);
}
// Prescribed contact choreography, not a collision solver. The approach has
// nonzero contact speed; the recoil starts with restitution * incoming speed.
export function contact(t,{time,from,to,lead=.7,restitution=.35,frequency=1,damping=1}={}) {
  if(!(lead>0&&restitution>=0&&restitution<=1))throw Error('positive lead and restitution in [0,1] required');
  const incomingSpeed=2*Math.abs(to-from)/lead;
  const u=clamp((t-(time-lead))/lead),direction=Math.sign(from-to);
  return {position:t<time?from+(to-from)*u*u:spring(t-time,{from:to,to:from,velocity:direction*incomingSpeed*restitution,frequency,damping}),incomingSpeed};
}

/* Prepared adapter to VK_SCORE events, not a second clock or audio engine. */
const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
const response=await fetch(new URL('./music-plan.json',import.meta.url));
if(!response.ok)throw Error('prepare music-plan.json before rendering');
const bytes=await response.arrayBuffer();
if(await sha(bytes)!=='__PLAN_SHA__')throw Error('music plan fingerprint differs; rerun prepare_music.py');
const plan=JSON.parse(new TextDecoder().decode(bytes));
const config=await fetch(new URL('../music.json',import.meta.url));
if(!config.ok||await sha(await config.arrayBuffer())!==plan.config_sha256)throw Error('music config fingerprint differs; rerun prepare_music.py before rendering');
if(plan.source){
  const r=await fetch(new URL(plan.source.src,new URL('../',import.meta.url)));
  if(!r.ok||await sha(await r.arrayBuffer())!==plan.source.sha256)throw Error('music source fingerprint differs; re-analyze and re-author the music config');
}
function freeze(x){if(x&&typeof x==='object'){Object.values(x).forEach(freeze);Object.freeze(x);}return x;}
export const MUSIC=freeze(plan);
export function anchor(id){if(!Object.hasOwn(MUSIC.anchors,id))throw Error(`unknown music anchor ${id}`);return MUSIC.anchors[id];}

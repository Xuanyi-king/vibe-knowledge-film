import {score} from '/engine/vk-motion.mjs';
import {phrase} from '/engine/vk-music.mjs';
const r=await fetch('assets/piano/bank.json');if(!r.ok)throw Error('Prepare the licensed piano bank first: python scripts/prepare_instrument.py examples/mirror examples/mirror/piano.json');
const piano=await r.json(),clock=score({end:112,fps:30,tempo:[{beat:0,bpm:80}]});
const events=[
 {id:'photo-arrives',start:4,duration:1.5,action:'paper-arrival',sound:{kind:'friction',material:'paper',speed:[[0,.2],[.3,.6],[1.5,0]],gain:.075}},
 {id:'flip',start:9,duration:3,action:'horizontal-reversal',sound:{kind:'friction',material:'paper',speed:[[0,0],[1.5,.4],[3,0]],gain:.045}},
 {id:'orientation',start:17,duration:0,action:'controlled-comparison'},
 {id:'study-self',start:36,duration:0,action:'published-count'},
 {id:'study-partner',start:40,duration:0,action:'published-count'},
 {id:'distance-start',start:56,duration:0,action:'camera-comparison'},
 {id:'camera-move',start:58,duration:9,action:'camera-approach',sound:{kind:'friction',material:'felt',speed:[[0,0],[4.5,.3],[9,0]],cutoff:700,gain:.025}},
 {id:'near',start:67,duration:0,action:'camera-arrival'},
 {id:'separate',start:82,duration:0,action:'distinguish-mechanisms'},
 {id:'closing',start:110,duration:0,action:'return-with-new-understanding'}
];
// Original 36-bar miniature. Chords and rests follow the story, not subtitle arrivals.
const harmony=[[53,57,60,64],[48,52,55,59],[50,57,60,65],[55,59,62,67]];
for(let bar=0;bar<36;bar++){
 if([4,5,15,16,25].includes(bar))continue;
 const b=bar*4,ch=harmony[Math.floor(bar/2)%4],late=bar>=31;
 events.push(...phrase(clock,{id:`support-${bar}`,beat:b,instrument:piano,gain:late?.12:.095,pan:-.13,tail:1.4,notes:[[0,ch[0],2.2,.75],[.12,ch[2],2,.32]]}));
 if(bar%2===0)events.push(...phrase(clock,{id:`line-${bar}`,beat:b,instrument:piano,gain:.15,pan:.16,tail:1.3,notes:[[.75,ch[3],1,.8],[2.5,ch[2]+12,1,.6]]}));
}
// The opening motif returns with a complete cadence; no inherited Atlas music.
for(const [id,start,notes] of [['question',0,[[.1,64,1.1,.7],[1.7,67,1,.65],[3.1,69,2,.6]]],['return',94,[[.1,64,1.1,.65],[1.7,67,1,.55],[3.1,69,2,.5]]],['cadence',105,[[0,65,1.8,.55],[2,64,1.8,.6],[4,60,3,.65]]]])
 events.push(...phrase(clock,{id,beat:clock.beat(start),notes,instrument:piano,gain:.19,tail:2,pan:.03}));
export const SCORE=score({end:112,fps:30,tempo:[{beat:0,bpm:80}],shots:[{id:'whole',start:0,end:112}],events,
 tracks:{music:{room:.13,t60:.9,highpass:42,lowpass:6800,gain:[[0,.6],[7,.5],[13,.28],[21,.5],[33,.55],[42,.38],[49,.2],[55,.48],[68,.55],[75,.12],[79,.45],[94,.55],[107,.45],[111.7,0]]},sfx:{room:.04,t60:.2,highpass:70,lowpass:7000}},silence:[[76,78]]});

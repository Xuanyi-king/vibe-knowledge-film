import {score} from '/engine/vk-motion.mjs';
import {phrase} from '/engine/vk-music.mjs';
const r=await fetch('assets/piano/bank.json');if(!r.ok)throw Error('Prepare piano.json before production');
const piano=await r.json(),clock=score({end:14,tempo:[{beat:0,bpm:84}]});
const events=[
 {id:'seat',start:1.8,duration:.4,action:'controlled-contact',sound:{kind:'impact',material:'wood',frequency:480,gain:.12,pan:-.25}},
 {id:'slide',start:3.7,duration:3.3,action:'slide',sound:{kind:'friction',material:'felt',gain:.09,speed:[[0,0],[1.5,.3],[3.3,0]],cutoff:1200,pan:[ [0,-.2],[3.3,.2] ]}},
 {id:'reveal',beat:11,duration:0,action:'computed-double'},
 {id:'hold',start:12,duration:0,action:'observation'}
];
for(const [id,beat,notes] of [
 ['question',0,[[0,53,2.8,.7],[.3,60,2.5,.4],[1.5,64,1.8,.55]]],
 ['compare',4,[[0,57,2,.5],[1.5,60,2,.4],[3.2,65,1.8,.5]]],
 ['answer',11,[[0,53,2.5,.6],[.15,60,2.5,.4],[1.1,64,2,.6]]],
 ['return',15,[[0,57,1.8,.5],[1.5,60,2,.45],[3,65,2,.55]]]
])events.push(...phrase(clock,{id,beat,notes,instrument:piano,gain:4,pan:.08,tail:1.4}));
export const SCORE=score({end:14,fps:30,tempo:[{beat:0,bpm:84}],events,
 tracks:{music:{room:.10,t60:.8,highpass:55,lowpass:6800,gain:[[0,.8],[1.5,.55],[2.1,.75],[6.9,.7],[7.4,0],[7.7,.8],[12.9,.65],[14,0]]},sfx:{room:.05,t60:.25,highpass:75}},silence:[[7.4,7.7]]});

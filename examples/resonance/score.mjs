import {score,contact} from '/engine/vk-motion.mjs';
// Contact, material, motion, music and gain envelopes have one source of time.
const MALLET={from:1.8,to:.19,lead:.7,restitution:.35};
const speed=contact(2,{time:2,...MALLET}).incomingSpeed;
export const SCORE=score({end:8,fps:30,tempo:[{beat:0,bpm:90}],
  shots:[{id:'resonance',start:0,end:8}],
  tracks:{music:{gain:[[0,.35],[1.5,.18],[1.9,0],[5.65,0],[6.2,.3],[7.8,0]]},sfx:{room:.08,t60:.32,highpass:45}},
  silence:[[5.72,6.0]],
  events:[
    {id:'approach',shot:'resonance',start:1.3,duration:.7,object:'mallet',action:'movement',sound:{kind:'whoosh',material:'wood',gain:.16,pan:-.2}},
    {id:'strike',shot:'resonance',beat:3,duration:3.7,object:'disc',action:'collision',material:'metal',intensity:Math.min(1,speed/5),motion:MALLET,position:[-.45,1.62,.02],speed,
      sound:{kind:'impact',material:'metal',frequency:220,pan:-.15,gain:[[0,.9],[3.333,.9],[3.5,0]]}},
    {id:'damp',shot:'resonance',beat:8,duration:.38,object:'felt',action:'friction',material:'felt',speed:.35,intensity:.25,
      sound:{kind:'friction',material:'felt',gain:.55,pan:.35,speed:[[0,.5],[.15,.15],[.38,0]]}},
    ...[[0,57],[1,64],[9.25,60],[10,64],[10.7,69]].map(([beat,midi],i)=>({id:`music-${i}`,beat,duration:.65,action:'music',sound:{kind:'pluck',midi,gain:.24,track:'music',pan:i%2?.4:-.4}})),
    {id:'macro',start:2.7,duration:1.6,action:'camera',object:'disc'},
    {id:'breath',start:5.72,duration:.28,action:'silence',reason:'让停止成为可听见的结论'}
  ]});

import {score} from '/engine/vk-motion.mjs';
const events=[
 {id:'opening-layout',start:3,duration:0,action:'observation'},
 {id:'latitude-half',start:20,duration:0,action:'observation'},
 {id:'choice-layout',start:65,duration:0,action:'observation'},
 {id:'unfold',start:7,duration:1.2,action:'transformation',sound:{kind:'friction',material:'paper',gain:.09,speed:[[0,.1],[.5,1],[1.2,0]]}},
 {id:'stretch-x',start:28,duration:.5,action:'reveal',sound:{kind:'pluck',midi:64,gain:.15}},
 {id:'keep-angle',start:35,duration:.6,action:'reveal',sound:{kind:'pluck',midi:67,gain:.13}},
 {id:'four',start:38.25,duration:.7,action:'reveal',sound:{kind:'impact',material:'wood',frequency:180,intensity:.3,gain:.3}},
 {id:'reproject',start:44,duration:1.2,action:'transformation',sound:{kind:'friction',material:'paper',gain:.1,speed:[[0,.2],[.4,.8],[1.2,0]]}},
 {id:'equal-area',start:52,duration:.65,action:'reveal',sound:{kind:'pluck',midi:72,gain:.14}},
 {id:'compare',start:58,duration:0,action:'comparison'},
 {id:'finish',start:71,duration:0,action:'resolution'}
];
const chords=[[53,57,60,64],[50,53,57,60],[46,53,57,62],[48,55,58,62]];
// Original 24-bar miniature, not a stock drone; sparse bass + changing string figures.
for(let bar=0;bar<24;bar++){
 const ch=chords[bar>=22?0:Math.floor(bar/2)%4],beat=bar*4;
 events.push({id:`bass-${bar}`,beat,duration:2.6,action:'music',sound:{kind:'string',midi:ch[0]-12,feedback:.978,gain:.16,track:'music',pan:-.13}});
 for(let j=0;j<2;j++)events.push({id:`line-${bar}-${j}`,beat:beat+.75+j*1.5,duration:Math.min(1.7,72-(beat+.75+j*1.5)*.75),action:'music',sound:{kind:'string',midi:ch[(bar+j)%4]+12+(bar>=16&&j===1?12:0),gain:.15,feedback:.975,track:'music',pan:j?.28:-.28}});
}
export const SCORE=score({end:72,fps:30,tempo:[{beat:0,bpm:80}],shots:[{id:'whole',start:0,end:72}],
 tracks:{music:{gain:[[0,0],[1,.75],[20,.55],[29,.3],[37,.15],[40,.02],[44,.5],[61,.55],[68,.6],[71.8,0]],room:.11,t60:.8,highpass:50},sfx:{room:.04,t60:.22}},
 silence:[[41,42]],events});

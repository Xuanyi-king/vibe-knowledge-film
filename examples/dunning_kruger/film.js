/* 原创导演重制版。图论挑战是教学类比，不是1999年实验材料。
 * 严格系列配置缺母版时仍拒绝正式加载；独立预览快照显式注入visual flag。
 */
import * as M from '/engine/vk-motion.mjs';
import {visualChecks} from '/engine/vk-checks.mjs';
import {instrument,openingPath,endingPath} from './objects.mjs';
import {P,ss,mix,txt,ln,dot,background,paper,graph,Q,E,pathBetween,flourish} from './canvas.mjs';
const END=130;
export const SUBS=[
 [1.1,5.3,'这张图，你觉得能一笔画完吗？'],
 [5.8,9.6,'每条线，只走一次。'],
 [10.6,13.7,'总有一条，留在最后。'],
 [22.8,26.3,'1999年，两位心理学家问：'],
 [26.7,30.7,'你做得怎样，又觉得自己做得怎样？'],
 [31.3,35.2,'低分组实际只超过约12%的人；'],
 [35.6,39.5,'却以为，自己超过了约62%。'],
 [40.6,44.5,'做对一道题，需要知识。'],
 [45,49.4,'看出自己哪里错了，也可能需要它。'],
 [50.0,53.7,'缺的知识，可能让错误也藏了起来。'],
 [54.6,58.7,'回到这张图：经过路口，要一进一出。'],
 [59.3,63.3,'三条线，总有一条落单。'],
 [64,68.4,'这种路口，只能留给起点或终点。'],
 [68.9,72.4,'起点和终点，只有两个。'],
 [73,76.5,'这样的路口，这里却有四个。'],
 [77.1,80.2,'原来，它根本画不完。'],
 [81,85,'学到的，也是一把判断自己的尺。'],
 [85.8,89.5,'但别急着，拿它给别人贴标签。'],
 [90.1,94.1,'分组与测量，也可能放大差距。'],
 [94.7,98.6,'后来的智力研究，结果并不一致。'],
 [99.1,102.7,'偏差有多大，还要看任务与方法。'],
 [103.6,107.8,'再看这张图，你先数了路口。'],
 [108.6,112.0,'少一条线，会怎样？'],
 [112.8,117.5,'先提出判断，再让结果检验它。'],
 [119.1,122.6,'所以，觉得自己会了，先做一次验证。'],
 [123.1,126.8,'看见差距，再用反馈修正自己的判断。'],
];
export const SHOTS=[
 {id:'challenge',start:0,end:14},{id:'name',start:14,end:22},
 {id:'research',start:22,end:40},{id:'two-judgements',start:40,end:54},
 {id:'rule',start:54,end:64},{id:'four-ends',start:64,end:85.5},
 {id:'limits',start:85.5,end:103},{id:'return',start:103,end:119},
 {id:'afterword',start:119,end:127},{id:'sources',start:127,end:130}
];
// Deliberately sparse: no impacts, notification tones, whooshes or ambience drone.
export const soundEvents=[
 {id:'paper-arrives',start:22.55,duration:.65,material:'paper',speed:.1,
  sound:{kind:'friction',track:'sfx',gain:.16,pan:-.12}},
 {id:'pen-touches',start:112.6,duration:.5,material:'paper',speed:.05,
  sound:{kind:'friction',track:'sfx',gain:.12,pan:.12}}
];

try{
const MUSIC=window.__VK_VISUAL_DRAFT__===true?null:(await import('./assets/music-plan.mjs')).MUSIC;
if(!window.__VK_VISUAL_DRAFT__&&(MUSIC.selected!=='signature'||MUSIC.signature?.id!=='shape-of-luck'))throw Error('specified music master missing');
const localReference=window.__VK_REFERENCE_MIX_PREVIEW__===true?[{
 id:'actual-reference-recording',start:0,duration:END,sync:'exempt',
 sync_reason:'continuous user-supplied reference mix; no discrete visual action',
 sound:{kind:'sample',track:'music',src:'assets/private-reference/reference.mp4',trim:0,
 gain:[[0,0],[.18,.4],[127.5,.4],[130,0]],
 license:'Actual user-supplied reference soundtrack, explicitly requested local review edit; not an isolated master or public distribution grant'}
}]:[];
const S=window.VK_SCORE=M.score({end:END,fps:30,shots:SHOTS,
 tracks:{sfx:{highpass:180,lowpass:1800},ambience:{}},events:[...(MUSIC?.events||[]),...localReference,...soundEvents,
 {id:'opening-stops',start:10.2,duration:0},{id:'ending-complete',start:117.9,duration:0}]});
const model=instrument();
let actualModelState=null;
window.VK_CHECKS=visualChecks(S,[
 {id:'opening-one-edge-left',event:'opening-stops',min:1,max:1,measure:()=>actualModelState?.remaining,
  unit:'visible untraced rods',description:'读取实际绘制的未走过轨道数量'},
 {id:'ending-all-five-traced',event:'ending-complete',min:5,max:5,measure:()=>actualModelState?.drawn,
  unit:'visible traced rods',description:'读取实际绘制的已走过轨道数量'},
 {id:'ending-five-rods',event:'ending-complete',min:5,max:5,measure:()=>actualModelState?.visibleEdges,
  unit:'visible rods',description:'移去一条后实际绘制五条轨道'}
]);
let c;
function alpha(a,fn){c.save();c.globalAlpha*=Math.max(0,Math.min(1,a));fn();c.restore();}
function heading(year,where){
 txt(c,year,118,105,76,P.gold,'left','VK Latin',600);
 ln(c,[120,153],[425,153],'#aa8b514d',1);
 txt(c,where,120,188,27,P.muted,'left');
}
function caption(fr,t){
 const active=SUBS.find(([a,b])=>t>=a&&t<=b);
 if(!active)return;
 const [a,b,s]=active,opacity=ss(t,a,a+.38)*(1-ss(t,b-.3,b));
 c.save();c.globalAlpha=opacity;c.shadowColor='#000';c.shadowBlur=8;c.shadowOffsetY=2;
 const size= s.length>22?74:80;
 const width=txt(c,s,960,950,size,P.white,'center','VK Serif',500);
 c.restore();
 fr.artLayout.push({role:'caption',importance:'essential',text:s,left:960-width/2,top:905,width,height:90,
  background:P.bg,style:{font:'serifm',size,color:P.white,a:opacity,track:0}});
}
function label(s,x,y,size=34,col=P.muted){txt(c,s,x,y,size,col);}
function strokeProgress(t,start,step){
 const keys=[[start,0]];
 for(let i=0;i<5;i++){keys.push([start+i*step+step*.84,i+1]);if(i<4)keys.push([start+(i+1)*step,i+1]);}
 return M.track(keys,t);
}
function title(t){
 const u=ss(t,14,16),v=ss(t,15.2,16.5);
 model.show(c,t,{progress:5,alpha:.24*(1-ss(t,20.7,22)),pose:{position:[1.5,7.2,11],target:[0,0,0],fov:35}});
 alpha(v,()=>{
  txt(c,'THE DUNNING–KRUGER EFFECT',960,280,30,P.muted,'center','VK Latin');
  const g=c.createLinearGradient(0,350,0,570);g.addColorStop(0,'#f6e4b9');g.addColorStop(.6,'#d5b16c');g.addColorStop(1,'#93713e');
  txt(c,'盲 区',960,440,190,g,'center','VK Serif',700);
  flourish(c,960,590,510);txt(c,'邓宁—克鲁格效应',960,660,49,P.white);
  txt(c,'为什么，我们会看错自己？',960,747,38,P.muted);
 });
}
function hook(t){
 const pose=M.track([[0,[4.4,4.8,7.4]],[4.3,[1.5,6.7,7.3]],[12.5,[1.5,6.7,7.3]],[14,[1.5,7.2,11]]],t);
 const progress=strokeProgress(t,5.6,.9);
 actualModelState=model.show(c,t,{progress,alpha:1-.76*ss(t,13.5,14),pose:{position:pose,target:[0,-.48,0],fov:40}});
 alpha(ss(t,.3,1),()=>{txt(c,'一 笔 画',120,135,48,P.gold,'left');txt(c,'不抬笔 · 不重复走线',120,197,27,P.muted,'left');});
 if(t>10.5){alpha(ss(t,10.5,11.2),()=>{const p=model.project([0,.08,1]);txt(c,'还剩一条',1480,610,44,P.red);ln(c,[1370,624],[p[0]+14,p[1]],P.red,1.5);});}
}
function documentPage(t){
 const u=ss(t,22,23.8),shift=mix(150,0,u),expand=ss(t,30.6,31.2);
 heading('1999','KRUGER & DUNNING');
 if(t<32){alpha(1-ss(t,30,30.55),()=>paper(c,1000,490+shift,1000,510,-.035,q=>{
  txt(q,'UNSKILLED AND UNAWARE OF IT',0,-183,31,P.ink,'center','VK Latin',600);
  ln(q,[-410,-137],[410,-137],'#63543b88',1);
  txt(q,'表现 与 自我估计',0,-72,48,P.ink);
  ['幽默','语法','逻辑'].forEach((s,i)=>{
   const x=(i-1)*270;txt(q,s,x,27,39,P.ink);ln(q,[x-88,75],[x+88,75],'#8e7b5555',2);
   for(let j=0;j<4;j++)ln(q,[x-88,103+j*20],[x+40+(j%2)*35,103+j*20],'#76603e66',1.4);
  });
  txt(q,'四项研究 · 任务表现与自我评估',0,212,23,'#766648');
 }));}
 if(expand>0)alpha(expand,()=>{
  const left=400,right=1570,w=right-left;
  const strip=(y,name,num,col)=>paper(c,970,y,1390,166,y===390?-.009:.012,q=>{
   txt(q,name,-655,-27,44,P.ink,'left');
   const a=left-970,b=right-970;
   ln(q,[a,25],[b,25],'#6a5d4277',1.5);
   for(let i=0;i<=100;i++)ln(q,[a+w*i/100,25],[a+w*i/100,25+(i%10===0?17:7)],'#6a5d4277',1);
   [0,50,100].forEach(v=>txt(q,''+v,a+w*v/100,60,22,'#6c604c','center','VK Latin'));
   const x=a+w*num/100;ln(q,[x,17],[x,-36],col,3);dot(q,x,17,5,col);txt(q,''+num,x,-48,77,col,'center','VK Latin',600);
  });
  strip(390,'自我估计',62,'#806022');strip(650,'实际表现',12,'#a24e41');
  label('最低四分位组的平均百分位 · 不是答对率',985,800,29);
 });
}
function doubleJudgement(t){
 const reveal=ss(t,45,47.5);heading('1999','一种解释 · 不是唯一解释');
 const xs=[560,1360];
 xs.forEach((x,i)=>{
  paper(c,x,480,590,490,(i===0?-.035:.025),q=>{
   txt(q,i?'检查答案':'尝试作答',0,-187,37,P.ink);
   q.save();q.translate(0,-20);q.scale(.56,.56);graph(q,{x:0,y:0,s:1,progress:i?5:mix(0,5,ss(t,41,44)),mark:0});q.restore();
   if(i){txt(q,'我觉得，可以。',0,185,31,reveal>.5?'#a24e41':P.ink);}
  });
 });
 const py=mix(697,307,reveal);
 paper(c,960,py,380,110,-.02,q=>{txt(q,'判断的规则',0,0,37,P.ink);});
 if(t>49){alpha(ss(t,49,50),()=>{ln(c,[960,370],[560,390],P.gold,1.5);ln(c,[960,370],[1360,390],P.gold,1.5);label('同一份知识，可能参与两种判断',960,807,31);});}
}
function junction(t){
 heading('Ⅰ','一笔画 · 教学类比');
 const center=[960,470],arms=[[580,250],[1340,250],[960,800]];
 arms.forEach(p=>ln(c,center,p,'#756d5c',11));
 const p=ss(t,55.1,58.2);pathBetween(c,[arms[0],center,arms[1]],p,P.gold,12);
 if(t>58.8){alpha(ss(t,58.8,59.8),()=>{ln(c,center,arms[2],P.red,11);label('落单的这一条',1190,725,39,P.red);ln(c,[1070,719],[982,703],P.red,1.5);});}
 // Raised porcelain central pin, a pair of route arrows, then a still observation.
 const g=c.createRadialGradient(952,456,3,960,470,31);g.addColorStop(0,'#fff3d8');g.addColorStop(.6,'#d6c6a0');g.addColorStop(1,'#79613a');dot(c,...center,30,g);
 if(t>56){alpha(ss(t,56,56.6),()=>{label('进',750,322,42,P.gold);label('出',1180,322,42,P.gold);});}
}
function fourEnds(t){
 heading('Ⅱ','四个路口 · 每处三条线');
 const zoom=mix(1.16,.93,ss(t,64,66));
 const mark=Math.floor(4*ss(t,71.8,75.0)+.00001);
 graph(c,{x:1040,y:460,s:zoom,mark,labels:t>71.7});
 if(t<72){alpha(1-ss(t,71.3,72),()=>{
  paper(c,390,500,340,250,-.035,q=>{txt(q,'起点',-80,-20,42,P.ink);txt(q,'终点',80,-20,42,P.ink);dot(q,-80,45,13,'#9c7641');dot(q,80,45,13,'#9c7641');txt(q,'最多两个例外',0,95,27,'#756548');});
 });}
 if(t>75.2){alpha(ss(t,75.2,76),()=>{txt(c,'4',390,440,140,P.red,'center','VK Latin');label('四个“落单”的路口',390,565,35,P.muted);});}
 if(t>80.5){const u=ss(t,80.5,82);alpha(u,()=>{
  paper(c,960,790,1050,64,.0,q=>{for(let i=0;i<=60;i++){const x=-480+i*16;ln(q,[x,-21],[x,i%5===0?14:-4],'#76603e',1);}txt(q,'一份新的判断依据',0,0,25,P.ink);});
 });}
}
function limits(t){
 // A field of paper slips becomes two readable research records; no invented dataset.
 const r=ss(t,85.5,88);heading('Ⅲ','研究也需要被检验');
 alpha(.35*(1-ss(t,90,92)),()=>{
  for(let i=0;i<45;i++){
   const col=i%9,row=Math.floor(i/9),x=310+col*175+(VK.hash(i+40)-.5)*30,y=270+row*98;
   paper(c,x,y,132,75,(VK.hash(i+15)-.5)*.16,q=>{ln(q,[-42,-10],[42,-10],'#88734a',2);ln(q,[-42,10],[15,10],'#88734a88',1);});
  }
 });
 const a=ss(t,89,90.5);
 alpha(a,()=>{
  const w=680,h=385;
  paper(c,565,490,w,h,-.028,q=>{
   txt(q,'2020',0,-117,80,'#84632c','center','VK Latin',600);
   txt(q,'未检出预期关系',0,-12,47,P.ink);
   txt(q,'Gignac & Zajenkowski',0,79,27,'#756548','center','VK Latin');
   txt(q,'一般智力 · 社区样本',0,132,25,'#756548');
  });
  paper(c,1360,510,w,h,.027,q=>{
   txt(q,'2023',0,-117,80,'#84632c','center','VK Latin',600);
   txt(q,'检出，但效应很小',0,-12,47,P.ink);
   txt(q,'Dunkel, Nedelec & van der Linden',0,79,25,'#756548','center','VK Latin');
   txt(q,'一般智力 · 后续复现',0,132,25,'#756548');
  });
  label('不能外推为所有任务、所有人的固定规律',960,785,31);
 });
 // Before the records settle, visible displaced measurement ticks convey uncertainty.
 if(t<90){alpha(ss(t,86,87)*(1-ss(t,89,90)),()=>{
  txt(c,'测量有误差，分组会影响比较',960,720,39,P.white);
 });}
}
function returnScene(t){
 const p=strokeProgress(t,112.6,1.03),removed=ss(t,109,110.5);
 const pose=M.track([[103,[1.5,6.7,7.3]],[107,[1.5,6.7,7.3]],[111,[.2,7.5,7.0]],[118,[.2,7.5,7.0]],[119,[.4,7.6,8.0]]],t);
 actualModelState=model.show(c,t,{path:endingPath,progress:p,removed,mark:t<109?4:0,markList:t>110.5?[2,3]:null,
  pose:{position:pose,target:[0,-.48,0],fov:40}});
 txt(c,'还是这张图',120,135,46,P.gold,'left');
 txt(c,removed>.9?'改动之后：两个三岔路口':'先找判断的依据',120,197,27,P.muted,'left');
 if(t>110.6&&t<113){alpha(ss(t,110.6,111.2)*(1-ss(t,112.5,113)),()=>label('现在，可以试了。',1450,470,43,P.gold));}
}
function afterword(t){
 model.show(c,t,{path:endingPath,progress:5,removed:1,alpha:1-ss(t,124,127),
  pose:{position:M.track([[119,[.4,7.6,8]],[123,[3.8,7.6,10.8]],[127,[5.8,7.6,12.8]]],t),target:[0,-.48,0],fov:40}});
 alpha(ss(t,119.5,121),()=>{txt(c,'盲 区',390,275,100,P.gold);flourish(c,390,368,350);txt(c,'邓宁—克鲁格效应',390,420,35,P.muted);});
}
function credits(t){
 const a=ss(t,126.8,127.4);alpha(a,()=>{
  txt(c,'盲 区',960,245,112,P.gold);txt(c,'邓宁—克鲁格效应',960,360,42,P.white);flourish(c,960,447,530);
  txt(c,'科学来源',960,515,28,P.muted);
  txt(c,'Kruger & Dunning · 1999 · Journal of Personality and Social Psychology',960,580,30,P.white,'center','VK Latin');
  txt(c,'Gignac & Zajenkowski · 2020 · Intelligence 80, 101449',960,635,30,P.white,'center','VK Latin');
  txt(c,'Dunkel, Nedelec & van der Linden · 2023 · Intelligence 96, 101717',960,690,30,P.white,'center','VK Latin');
 });
}
let state={};window.DK_STATE=()=>structuredClone(state);
VK.film({dur:END,fps:30,theme:'flat',bloom:0,grain:.018,
 meta:{title:'盲区 · 邓宁—克鲁格效应',subtitle:'The Dunning–Kruger Effect',preview:window.__VK_VISUAL_DRAFT__===true},
 draw(fr,t){
  c=fr.x;background(c,t);state={time:t};actualModelState=null;
  if(t<14)hook(t);else if(t<22)title(t);else if(t<40)documentPage(t);
  else if(t<54)doubleJudgement(t);else if(t<64)junction(t);else if(t<85.5)fourEnds(t);
  else if(t<103)limits(t);else if(t<119)returnScene(t);else if(t<127)afterword(t);else credits(t);
  state.renderedModel=actualModelState;
  caption(fr,t);
  // Short intentional dips hide no intermediate reasoning; typography stays steady.
  const dip=[22,40,54,64,85.5,103].reduce((a,v)=>Math.max(a,Math.max(0,1-Math.abs(t-v)/.22)),0);
  if(dip>0){c.fillStyle=`rgba(5,7,10,${dip*.93})`;c.fillRect(0,0,1920,1080);}
 }});
}catch(e){window.READY_ERROR=String(e);throw e;}

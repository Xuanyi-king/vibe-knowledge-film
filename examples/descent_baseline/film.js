/* 抢先一步：原版 Skill 工作流，独立现写。所有轨迹和计时使用解析物理，详见facts.md。 */
(function(){'use strict';
const K=VKit, {ss,clamp,lerp}=VK;
const A=.3006410009354001, TH=3.2339751452171397,G=9.81;
const TC=Math.sqrt(A/G)*TH, TS=Math.sqrt(2*1.36/(G*.6));
const C={gold:'#F8D893',blue:'#64E3F6',white:'#F8F9F8',muted:'#879399'};
const SUBS=[
{a:.4,b:3.6,zh:'同时松手，哪条轨道先到？',en:'Released together. Which path arrives first?'},
{a:4.2,b:7.2,zh:'曲线更长，却先到了。',en:'The longer path arrives sooner.'},
{a:11.3,b:15.3,zh:'同一终点，从静止、无摩擦滑下。',en:'Same endpoints. From rest. No friction.'},
{a:16,b:21.5,zh:'起步更陡，它先把高度换成速度。',en:'A steeper start turns height into speed earlier.'},
{a:28.2,b:31.8,zh:'这条最快的曲线，叫作摆线。',en:'The fastest curve is a cycloid.'}
];
function txt(c,s,x,y,size=26,color=C.white,align='left',font='VK Sans',weight=400){c.fillStyle=color;c.font=`${weight} ${size}px "${font}"`;c.textAlign=align;c.textBaseline='middle';c.fillText(s,x,y);}
function line(c,x0,y0,x1,y1,color,w=1){c.beginPath();c.moveTo(x0,y0);c.lineTo(x1,y1);c.strokeStyle=color;c.lineWidth=w;c.stroke();}
function dot(c,x,y,r,color){c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fillStyle=color;c.fill();}
function ball(c,x,y,color){c.save();c.shadowColor=color;c.shadowBlur=18;const d=c.createRadialGradient(x-6,y-8,1,x,y,20);d.addColorStop(0,'#ffffff');d.addColorStop(.24,color);d.addColorStop(.8,color===C.gold?'#99733C':'#287582');d.addColorStop(1,'#151C26');dot(c,x,y,20,d);c.shadowBlur=0;dot(c,x-6,y-8,4,'#FFFFFF');c.restore();}
function pos(kind,t){if(kind==='gold'){const q=Math.min(TH,t*Math.sqrt(G/A));return [A*(q-Math.sin(q)),A*(1-Math.cos(q))];}const q=Math.min(1,(t/TS)**2);return [q,.6*q];}
function alpha(t,a,b,r=.5){return ss(t,a,a+r)*(1-ss(t,b-r,b));}
function rail(c,map,kind){const pts=[];for(let i=0;i<=240;i++){const q=i/240;pts.push(map(kind==='gold'?[A*(q*TH-Math.sin(q*TH)),A*(1-Math.cos(q*TH))]:[q,.6*q]));}
 c.lineCap='round';for(const [w,color,dy] of [[20,'#05090D',7],[15,kind==='gold'?'#57462C':'#27434B',3],[6,kind==='gold'?'#BE9B59':'#4E9CAE',0],[1.5,kind==='gold'?'#FFF0C3':'#A2F6FF',-3]]){c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y+dy):c.moveTo(x,y+dy));c.strokeStyle=color;c.lineWidth=w;c.stroke();}}
function ruler(c,x0,y0,x1,y1,label){line(c,x0,y0,x1,y1,'#68737B',1.5);const horizontal=y0===y1;for(let i=0;i<=10;i++){const x=lerp(x0,x1,i/10),y=lerp(y0,y1,i/10);line(c,x-(horizontal?0:5),y-(horizontal?5:0),x+(horizontal?0:5),y+(horizontal?5:0),'#68737B',1.5);}txt(c,label,horizontal?(x0+x1)/2:x0-23,horizontal?y0-27:(y0+y1)/2,25,C.muted,horizontal?'center':'right');}
function clock(c,x,y,label,time,total,col,showLength){txt(c,label,x,y,26,col);txt(c,Math.min(time,total).toFixed(3),x,y+61,62,col,'left','VK Mono',400);txt(c,'s',x+220,y+68,26,C.muted);line(c,x,y+108,x+260,y+108,'#27313C',3);line(c,x,y+108,x+260*Math.min(1,time/total),y+108,col,3);if(time>=total)txt(c,'已到达',x+260,y,22,col,'right');if(showLength)txt(c,col===C.gold?'路长 1.258 m':'路长 1.166 m',x,y+142,23,C.muted);}
function arrow(c,x,y,dx,dy,col){line(c,x,y,x+dx,y+dy,col,4);const a=Math.atan2(dy,dx);line(c,x+dx,y+dy,x+dx-13*Math.cos(a-.45),y+dy-13*Math.sin(a-.45),col,4);line(c,x+dx,y+dy,x+dx-13*Math.cos(a+.45),y+dy-13*Math.sin(a+.45),col,4);}
// 两条滑轨 / 同时滑下 / 同端点条件下路程和用时并不等价。
function apparatus(c,t,a){if(a<=0)return;c.save();c.globalAlpha=a;
 const explaining=t>=15.5&&t<22.3,zoom=ss(t,15.5,16.3)*(1-ss(t,21.4,22.3));
 const ox=lerp(350,350,zoom),oy=lerp(235,220,zoom),scale=lerp(900,990,zoom),map=p=>[ox+p[0]*scale,oy+p[1]*scale];
 let time=t<7.4?clamp((t-.8)/6,0,TS):t<15.8?0:t<22.3?Math.min(.25,Math.max(0,(t-16)/12))*(1-ss(t,21.5,22.3)):clamp((t-22.3)/6,0,TS);

 txt(c,t<7.4?'01  /  同时松手':explaining?'02  /  把高度换成速度':t<15.8?'02  /  同一场实验':'03  /  再看一次',104,87,23,C.muted);
 line(c,104,119,415,119,'#36404A',1);
 txt(c,explaining?(t>=21.5?'回到起点 · 再看一次':'同一时刻的比较 · 慢放 ×12'):t<15.8&&t>10?'无摩擦质点 · g = 9.81 m/s²':'统一慢放 ×6 · 质点放大示意',1785,92,24,C.muted,'right');
 const end=map([1,.6]);
 // 实验架：实体底座、固定支柱和两条有厚度的金属滑轨。
 const grd=c.createLinearGradient(0,825,0,864);grd.addColorStop(0,'#1C2734');grd.addColorStop(1,'#080C13');c.fillStyle=grd;c.fillRect(ox-55,835,scale+110,26);line(c,ox-55,835,ox+scale+55,835,'#344251',2);
 line(c,ox,oy+12,ox,835,'#344251',9);line(c,end[0],end[1]+12,end[0],835,'#344251',9);
 for(const q of [.25,.55,.82]){const p=map([A*(q*TH-Math.sin(q*TH)),A*(1-Math.cos(q*TH))]);line(c,p[0],p[1]+12,p[0],835,'#1E2B39',4);}
 rail(c,map,'blue');rail(c,map,'gold');
 if(!explaining){ruler(c,ox,176,ox+scale,176,'水平距离 1.00 m');ruler(c,ox+scale+65,oy,ox+scale+65,end[1],'落差 0.60 m');}
 txt(c,'起点',ox-45,oy-5,26,C.white,'right');txt(c,'终点',end[0]+5,end[1]-39,26,C.white,'center');
 for(const kind of ['blue','gold']){const p=pos(kind,time),v=Math.sqrt(2*G*p[1]),xy=map(p),col=C[kind];
 if(explaining&&time>.03){c.save();c.setLineDash([5,8]);line(c,xy[0],oy,xy[0],xy[1],col,2);c.restore();const th=time*Math.sqrt(G/A),ang=kind==='gold'?Math.PI/2-th/2:Math.atan(.6);arrow(c,xy[0]+27,xy[1]+5,Math.cos(ang)*v*45,Math.sin(ang)*v*45,col);}
 ball(c,...xy,col);if(explaining&&time>.2){c.save();c.globalAlpha*=ss(time,.2,.245);txt(c,`下降 ${p[1].toFixed(3)} m`,ox-45,xy[1],25,col,'right');line(c,ox-25,xy[1],xy[0]-30,xy[1],col,1);c.restore();}
 }
 if(time===0||time>=TS){const p=map(time===0?[0,0]:[1,.6]);c.beginPath();c.arc(p[0],p[1],24,Math.PI*.5,Math.PI*1.5);c.strokeStyle=C.blue;c.lineWidth=4;c.stroke();c.beginPath();c.arc(p[0],p[1],24,-Math.PI*.5,Math.PI*.5);c.strokeStyle=C.gold;c.stroke();} if(explaining){txt(c,`t = ${time.toFixed(3)} s`,1450,280,33,C.white,'left','VK Mono');
 for(const [kind,y] of [['blue',405],['gold',575]]){const p=pos(kind,time),v=Math.sqrt(2*G*p[1]);txt(c,kind==='blue'?'直线':'曲线',1450,y-35,25,C[kind]);txt(c,`${v.toFixed(3)} m/s`,1450,y+8,36,C[kind],'left','VK Mono');line(c,1450,y+56,1770,y+56,'#27323F',12);line(c,1450,y+56,1450+320*v/3.5,y+56,C[kind],12);}
 txt(c,'速度尺：0 — 3.5 m/s',1450,727,22,C.muted);
 }else{clock(c,1460,310,'直线',time,TS,C.blue,t<7.4||t>=28);clock(c,1460,545,t>=28?'摆线':'曲线',time,TC,C.gold,t<7.4||t>=28);}
 c.restore();}
function titles(c,t){const a=alpha(t,7.1,11.4,.6);if(a>0){c.save();c.globalAlpha=a;txt(c,'抢先一步',960,425,150,C.white,'center','VK Serif',300);line(c,510,538,1410,538,C.gold,1);txt(c,'最速降线',960,603,36,C.gold,'center','VK Serif');txt(c,'BRACHISTOCHRONE',960,676,21,C.muted,'center','VK Mono');c.restore();}}
function credits(c,t){const a=ss(t,31.7,32.5);if(a<=0)return;c.save();c.globalAlpha=a;txt(c,'抢先一步',960,280,86,C.white,'center','VK Serif',300);txt(c,'先获得速度，再赢得时间。',960,401,38,C.gold,'center','VK Serif');line(c,550,480,1370,480,'#394452',1);txt(c,'文献线索  /  WOLFRAM MATHWORLD',960,555,23,C.muted,'center','VK Sans');txt(c,'Eric W. Weisstein · Brachistochrone Problem',960,614,29,C.white,'center','VK Latin');txt(c,'Cycloid · 参数方程与弧长',960,660,27,C.white,'center','VK Serif');txt(c,'适用：匀强重力 · 无摩擦质点 · 静止释放',960,743,25,C.muted,'center');txt(c,'轨道按公式绘制；质点与轨道厚度为放大示意',960,792,23,C.muted,'center');c.restore();}
VK.film({dur:36,theme:'night',meta:{title:'抢先一步',drone:.28,silence:[[0,3.8]]},draw(fr,t){
 fr.look.bgo={stars:.14,core:.6};fr.look.bloom=.25;fr.look.grain=.025;
 fr.look.under=c=>{apparatus(c,t,(1-ss(t,7,7.6))+ss(t,10.8,11.5)*(1-ss(t,31.5,32.1)));titles(c,t);credits(c,t);};
 K.subs(fr,t,SUBS,'night');
 [[.8+6*TC,'soft'],[.8+6*TS,'tock'],[7.5,'chord'],[11.4,'soft'],[15.7,'rise'],[19,'tick'],[22.3,'soft'],[22.3+6*TC,'soft'],[22.3+6*TS,'tock'],[28.2,'chord'],[32.3,'chord']].forEach(([s,n])=>fr.sfx(s,n,{gain:.45}));
 }});
})();

(function(){
'use strict';
const {ss,lerp}=VK, P=PHYS;
const C={bg:'#102222',ivory:'#e6ddc8',copper:'#d99465',muted:'#9aa8a0',white:'#f2ead8',ink:'#071514'};
const mix=(a,b,k)=>a.map((v,i)=>lerp(v,b[i],k));
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
function cam(t){
 let wide=[930,460,980,.5,.31,-.22,.43];
 if(t<4.5)return mix([1050,540,1850,.17,.16,-.35,.36],wide,ss(t,1,4.5));
 if(t<14.5)return wide;
 if(t<22)return [930,485,1450,.28,.30,-.07,.20];
 if(t<28)return [960,520,1200,.5,.30,0,0];
 return mix([930,465,980,.5,.31,-.22,.43],[930,480,930,.5,.31,-.34,.47],ss(t,28,35));
}
function projection(c){let [cx,cy,s,tx,ty,yaw,pitch]=c;return (x,y,z=0)=>{let X=(x-tx)*Math.cos(yaw)+z*Math.sin(yaw),Z=(x-tx)*Math.sin(yaw)-z*Math.cos(yaw);return [cx+s*X,cy+s*((y-ty)*Math.cos(pitch)+Z*Math.sin(pitch))];};}
function poly(ctx,pts,fill,stroke,width=1){ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=width;ctx.stroke();}}
function line(ctx,pts,color,width=1,dash=[]){ctx.beginPath();pts.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.stroke();ctx.setLineDash([]);}
function txt(ctx,str,x,y,size=28,color=C.white,font='VK Sans',weight=400,align='left'){ctx.font=`${weight} ${size}px "${font}"`;ctx.textAlign=align;ctx.textBaseline='middle';ctx.fillStyle=color;ctx.fillText(str,x,y);}
function points(kind,n=100){return Array.from({length:n+1},(_,i)=>kind==='c'?P.curve(P.theta*i/n):{x:i/n,y:.6*i/n});}
const pc=points('c'),ps=points('s');
function background(ctx){let g=ctx.createLinearGradient(0,0,1920,1080);g.addColorStop(0,'#1d3836');g.addColorStop(.55,'#112624');g.addColorStop(1,'#081816');ctx.fillStyle=g;ctx.fillRect(0,0,1920,1080);
 let l=ctx.createRadialGradient(440,40,0,440,40,1250);l.addColorStop(0,'#c3b28a20');l.addColorStop(1,'#233d3300');ctx.fillStyle=l;ctx.fillRect(0,0,1920,1080);
 ctx.fillStyle='#061210';ctx.fillRect(0,953,1920,127);line(ctx,[[96,953],[1824,953]],'#4d625433',1);
}
function block(ctx,pr,x0,x1,y0,y1,z0,z1){
 poly(ctx,[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0]].map(q=>pr(...q)),'#2e3d36');
 poly(ctx,[[x1,y0,z0],[x1,y0,z1],[x1,y1,z1],[x1,y1,z0]].map(q=>pr(...q)),'#182a24');
 let g=ctx.createLinearGradient(300,600,1300,850);g.addColorStop(0,'#6a7060');g.addColorStop(1,'#3a4c40');
 poly(ctx,[[x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1]].map(q=>pr(...q)),g,'#8c918044',1);
}
function base(ctx,pr){
 ctx.save();ctx.filter='blur(30px)';poly(ctx,[[-.15,.79,-.38],[1.18,.79,-.38],[1.18,.79,.38],[-.15,.79,.38]].map(q=>pr(...q)),'#0009');ctx.restore();
 block(ctx,pr,-.12,1.12,.69,.77,-.30,.30);
 for(let i=0;i<=20;i++){let x=i/20;line(ctx,[pr(x,.689,-.24),pr(x,.689,-.24+(i%5===0?.035:.018))],'#c0c0a155',1);}
 for(let kind of ['s','c']){let z=kind==='s'?.16:-.16;for(let u of [.03,.48,.95]){let p=kind==='s'?{x:u,y:u*.6}:P.curve(P.theta*u);let a=pr(p.x,p.y+.025,z),b=pr(p.x,.69,z);line(ctx,[a,b],'#172a23',11);line(ctx,[[a[0]-2,a[1]],[b[0]-2,b[1]]],'#728071',3);}}
}
function rail(ctx,pr,kind,cameraScale,alpha=1){ctx.save();ctx.globalAlpha=alpha;let pts=kind==='c'?pc:ps,z=kind==='c'?-.16:.16,w=.052,d=.019;
 const a=pts.map(p=>pr(p.x,p.y,z-w)),b=pts.map(p=>pr(p.x,p.y,z+w)),bot=pts.map(p=>pr(p.x,p.y+d,z-w));
 ctx.save();ctx.filter='blur(11px)';line(ctx,pts.map(p=>pr(p.x,.688,z-.015)), '#0008',cameraScale*.036);ctx.restore();
 let g=ctx.createLinearGradient(450,200,1350,750);if(kind==='c'){g.addColorStop(0,'#f0c19a');g.addColorStop(.28,'#bb754e');g.addColorStop(.55,'#dfaa7d');g.addColorStop(1,'#8f5038');}else{g.addColorStop(0,'#f5eddd');g.addColorStop(.6,'#c6c6b6');g.addColorStop(1,'#a4afa3');}
 poly(ctx,a.concat(bot.slice().reverse()),kind==='c'?'#693d2a':'#69766b');poly(ctx,a.concat(b.slice().reverse()),g);
 line(ctx,a,kind==='c'?'#eac69a':'#f9f3e2',1.6);line(ctx,b,kind==='c'?'#69432b':'#768377',1.3);
 line(ctx,pts.map(p=>pr(p.x,p.y-.001,z)),kind==='c'?'#784830aa':'#8d978999',cameraScale*.003);
 ctx.restore();}
function bead(ctx,pr,kind,t,s,ghost=false){let p=P.sample(kind,t),z=kind==='c'?-.16:.16,r=.0185;
 let foot=pr(p.x,p.y,z),center=pr(p.x+p.ty*r,p.y-p.tx*r,z);let R=s*r;
 ctx.save();if(ghost)ctx.globalAlpha=.18;
 ctx.save();ctx.translate(...foot);ctx.rotate(Math.atan2(center[1]-foot[1],center[0]-foot[0])+Math.PI/2);ctx.scale(1,.34);let sh=ctx.createRadialGradient(0,0,1,0,0,R*1.45);sh.addColorStop(0,'#000b');sh.addColorStop(1,'#0000');ctx.fillStyle=sh;ctx.beginPath();ctx.arc(0,0,R*1.45,0,Math.PI*2);ctx.fill();ctx.restore();
 let g=ctx.createRadialGradient(center[0]-R*.35,center[1]-R*.42,R*.05,center[0]+R*.22,center[1]+R*.26,R*1.25);
 if(kind==='c'){g.addColorStop(0,'#ffe2b8');g.addColorStop(.3,'#e5aa71');g.addColorStop(.65,'#ad633b');g.addColorStop(1,'#3d251b');}else{g.addColorStop(0,'#fffbee');g.addColorStop(.45,'#e6e5d3');g.addColorStop(.8,'#a0afa1');g.addColorStop(1,'#40564a');}
 ctx.fillStyle=g;ctx.beginPath();ctx.arc(...center,R,0,Math.PI*2);ctx.fill();ctx.strokeStyle=kind==='c'?'#edbd8255':'#f7ffe766';ctx.lineWidth=1;ctx.stroke();
 ctx.fillStyle='#fff5d9bb';ctx.beginPath();ctx.ellipse(center[0]-R*.32,center[1]-R*.42,R*.22,R*.12,-.5,0,Math.PI*2);ctx.fill();ctx.restore();return {p,center,foot};}
function arrow(ctx,from,to,col,w=3){line(ctx,[from,to],col,w);let a=Math.atan2(to[1]-from[1],to[0]-from[0]);poly(ctx,[to,[to[0]-14*Math.cos(a-.38),to[1]-14*Math.sin(a-.38)],[to[0]-14*Math.cos(a+.38),to[1]-14*Math.sin(a+.38)]],col);}
function apparatus(ctx,c,t,{balls=true,baseOn=true,alphaS=1}={}){let pr=projection(c);if(baseOn)base(ctx,pr);rail(ctx,pr,'s',c[2],alphaS);if(balls)bead(ctx,pr,'s',t,c[2]);rail(ctx,pr,'c',c[2]);if(balls)bead(ctx,pr,'c',t,c[2]);return pr;}
function header(ctx,n,label){txt(ctx,'GRAVITY / 01',96,65,23,'#c5d0bc','VK Mono');txt(ctx,label,1824,65,24,'#becbbc','VK Sans',400,'right');line(ctx,[[96,102],[1824,102]],'#92aa8a40',1);txt(ctx,n,96,146,25,C.copper,'VK Mono');}
function caption(ctx,a,b){ctx.fillStyle='#061210';ctx.fillRect(0,953,1920,127);line(ctx,[[96,953],[1824,953]],'#4d625455',1);txt(ctx,a,960,1002,42,C.white,'VK Sans',500,'center');if(b)txt(ctx,b,960,1050,23,'#9cb09e','VK Sans',400,'center');}
function label(ctx,pr,pos,name,color,dx=0,dy=0){let p=pr(...pos);txt(ctx,name,p[0]+dx,p[1]+dy,26,color,'VK Sans',500);}
function dim(ctx,pr){let a=pr(0,0,.16),b=pr(1,.6,.16),ac=pr(0,0,-.16),bc=pr(1,.6,-.16);
 line(ctx,[a,ac],'#d5dcc177',1,[4,6]);line(ctx,[b,bc],'#d5dcc177',1,[4,6]);
 for(let p of [a,b,ac,bc]){ctx.strokeStyle='#c3d0b599';ctx.lineWidth=1;ctx.beginPath();ctx.arc(...p,7,0,6.283);ctx.stroke();}
 const y=865;line(ctx,[[a[0],y],[b[0],y]],'#a0b49c88',1);for(let x of [a[0],b[0]])line(ctx,[[x,y-8],[x,y+8]],'#a0b49c',1);txt(ctx,'水平 1.00 m',(a[0]+b[0])/2,y+31,25,C.muted,'VK Sans',400,'center');
 txt(ctx,'落差 0.60 m',1610,505,28,C.ivory);line(ctx,[[1575,230],[1575,690]],'#a0b49c88',1);line(ctx,[[1567,230],[1583,230]],'#a0b49c',1);line(ctx,[[1567,690],[1583,690]],'#a0b49c',1);
}
function intro(ctx,t){let c=cam(t);apparatus(ctx,c,0);header(ctx,'01','重力工坊');
 if(t<3.9){let a=1-ss(t,3.3,4.1);ctx.save();ctx.globalAlpha=a;txt(ctx,'更短的路，',132,260,75,C.white,'VK Serif',500);txt(ctx,'就更快吗？',132,358,75,C.white,'VK Serif',500);txt(ctx,'A QUESTION OF TIME',137,438,24,C.copper,'VK Mono');ctx.restore();}
 if(t>=4){ctx.save();ctx.globalAlpha=ss(t,4,4.8);dim(ctx,projection(c));label(ctx,projection(c),[.45,.27,.16],'直线',C.ivory,-30,-38);label(ctx,projection(c),[.4,.56,-.16],'弯路',C.copper,-50,-50);ctx.restore();}
 if(t<4.5)caption(ctx,'长度的直觉，可能会骗过你。');else caption(ctx,'同一起点，同一终点。','无摩擦 · 质点 · 静止释放  /  双轨为同条件实验的并置');
}
function race(ctx,t){let c=cam(t),tau=Math.max(0,(t-8.8)/6),pr=apparatus(ctx,c,tau);header(ctx,'02','同场计时');
 txt(ctx,'6× 慢放',96,208,27,C.muted);txt(ctx,'球为质点标记',96,249,23,C.muted);
 for(let kind of ['s','c']){let p=P.sample(kind,tau),y=kind==='s'?354:485,col=kind==='s'?C.ivory:C.copper;
 txt(ctx,kind==='s'?'直线':'弯路',1520,y,28,col);txt(ctx,p.t.toFixed(3),1520,y+53,48,col,'VK Mono',500);txt(ctx,'s',1707,y+56,26,C.muted,'VK Mono');if(tau>=p.end)txt(ctx,'到达',1767,y+55,25,col);}
 if(t<12.15)caption(ctx,'让它们同时出发。','重力加速度 g = 9.81 m/s²');else caption(ctx,'弯路，先到了。','计时到终点停止');
}
function early(ctx,t){let c=cam(t),tau=clamp((t-15.2)/6,0,.30),pr=apparatus(ctx,c,tau,{baseOn:false});header(ctx,'03','回看起步');
 txt(ctx,t>=17?'定格比较 / 同一时刻':'6× 慢放 / 同一时刻',96,212,25,C.muted);txt(ctx,Math.min(tau,.30).toFixed(3)+' s',96,263,42,C.ivory,'VK Mono');
 for(let kind of ['s','c']){let p=P.sample(kind,tau),z=kind==='c'?-.16:.16,col=kind==='c'?C.copper:C.ivory;let pt=pr(p.x,p.y,z),start=pr(p.x+p.ty*.021,p.y-p.tx*.021,z),vto=pr(p.x+p.ty*.021+p.tx*p.v*.055,p.y-p.tx*.021+p.ty*p.v*.055,z);
 if(tau>0)arrow(ctx,start,vto,col,4);
 const yy=kind==='s'?380:527;txt(ctx,kind==='s'?'直线':'摆线',1425,yy,27,col);txt(ctx,p.v.toFixed(2)+' m/s',1425,yy+49,43,col,'VK Mono');
 if(tau>.08&&tau<.43){line(ctx,[pt,[1355,pt[1]]],col+'66',1,[4,7]);}
 }
 txt(ctx,'v = √(2gh)',96,794,48,C.copper,'VK Latin',500);txt(ctx,'落得越深，速度越大',96,849,28,C.muted);
 caption(ctx,'先陡降，更早换来速度。','相同落差处速度相同；关键在于何时获得速度');
}
function geometry(ctx,t){let c=cam(t),pr=projection(c);header(ctx,'04','从轨道到曲线');
 const k=ss(t,22.6,26.8),q=P.theta*k,a=P.a,cx=a*q,cy=a,r=a*c[2],cc=pr(cx,cy,0),p=P.curve(q),dot=pr(p.x,p.y,0);
 line(ctx,[pr(-.1,0,0),pr(1.18,0,0)],'#bfcdb166',1);txt(ctx,'几何生成示意',96,210,25,C.muted);
 ctx.save();ctx.globalAlpha=1-ss(t,26.3,27);ctx.strokeStyle='#a8b59a77';ctx.lineWidth=2;ctx.beginPath();ctx.arc(...cc,r,0,Math.PI*2);ctx.stroke();line(ctx,[cc,dot],'#e8c39a88',2);ctx.fillStyle=C.ivory;ctx.beginPath();ctx.arc(...cc,5,0,Math.PI*2);ctx.fill();ctx.restore();
 const reveal=Array.from({length:150},(_,i)=>{let p=P.curve(q*i/149);return pr(p.x,p.y,0);});line(ctx,pc.map(p=>pr(p.x,p.y,0)),'#cba47a22',15);line(ctx,reveal,C.copper,6);ctx.fillStyle=C.copper;ctx.beginPath();ctx.arc(...dot,10,0,Math.PI*2);ctx.fill();
 txt(ctx,'摆线',1500,385,77,C.copper,'VK Serif',500);txt(ctx,'CYCLOID',1506,465,26,C.muted,'VK Mono');txt(ctx,'圆周上一点',1506,535,27,C.ivory);txt(ctx,'滚过的轨迹',1506,577,27,C.ivory);
 caption(ctx,'这条最快的曲线，叫摆线。','圆在直线上无滑动滚动，其圆周点描出的轨迹');
}
function finale(ctx,t){let c=cam(t),pr=apparatus(ctx,c,1);header(ctx,'05','最速降线');
 txt(ctx,'先换来速度，',96,244,59,C.white,'VK Serif',500);txt(ctx,'再赢得时间。',96,322,59,C.white,'VK Serif',500);
 txt(ctx,'摆线',1480,274,29,C.copper);txt(ctx,'0.566 s',1480,327,52,C.copper,'VK Mono',500);txt(ctx,'1.258 m',1480,373,24,C.muted,'VK Mono');
 txt(ctx,'直线',1480,459,29,C.ivory);txt(ctx,'0.680 s',1480,512,52,C.ivory,'VK Mono',500);txt(ctx,'1.166 m',1480,558,24,C.muted,'VK Mono');
 txt(ctx,'长了 9.2 cm，却早了 0.114 s',960,879,34,C.white,'VK Sans',500,'center');caption(ctx,'最短的路程，不一定是最短的时间。','均匀重力 · 无摩擦 · 从静止出发  /  数值取三位小数');
}
VK.film({dur:36,theme:'flat',meta:{title:'先换来速度 · 最速降线',root:-5,drone:.35,silence:[[35.4,36]]},draw(fr,t){fr.look.bloom=0;fr.look.grain=.018;fr.look.bgo={color:C.bg};fr.look.under=ctx=>{background(ctx);ctx.lineJoin='round';ctx.lineCap='round';if(t<8.5)intro(ctx,t);else if(t<14.5)race(ctx,t);else if(t<22)early(ctx,t);else if(t<28)geometry(ctx,t);else finale(ctx,t);};
 for(let [at,name,p] of [[.25,'chord',{gain:.4}],[4.5,'soft',{gain:.3}],[8.8,'tock',{gain:.4}],[8.8+6*P.Tc,'tock',{pitch:3,gain:.65}],[8.8+6*P.Ts,'tock',{pitch:0,gain:.4}],[14.5,'soft',{gain:.4}],[22.6,'rise',{dur:2.8,gain:.15}],[26.8,'shimmer',{gain:.2}],[28,'chord',{root:7,gain:.45}],[35.4,'hush',{dur:.6}]])fr.sfx(at,name,p);
}});
})();

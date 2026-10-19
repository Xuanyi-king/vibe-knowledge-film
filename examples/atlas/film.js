(async()=>{
 const [M,G,C,{SCORE}]=await Promise.all([import('/engine/vk-motion.mjs'),import('/engine/vk-geo.mjs'),import('/engine/vk-checks.mjs'),import('./score.mjs')]);
 const A=await G.loadAtlas(),D=A.d3;window.VK_SCORE=SCORE;
 const P={paper:'#ede8da',ink:'#183d3d',water:'#c9dad4',land:'#527c70',red:'#bb5338',muted:'#607977',line:'#9eb3a7'};
 const state={sx:1,sy:1,area:1,closing:0,circumference:1,textOverflow:0};
 const clamp=x=>Math.max(0,Math.min(1,x)),ease=(t,a,b)=>M.smooth((t-a)/(b-a));
 function text(c,s,x,y,size=32,color=P.ink,font='VK Sans',align='left',weight=500){c.fillStyle=color;c.font=`${weight} ${size}px "${font}"`;c.textAlign=align;c.textBaseline='middle';const w=c.measureText(s).width,left=align==='center'?x-w/2:align==='right'?x-w:x;state.textOverflow=Math.max(state.textOverflow,-left,left+w-1920,y-size/2<0?-y+size/2:0,y+size/2-1080);c.fillText(s,x,y);}
 function stroke(c,points,color=P.red,width=2){c.strokeStyle=color;c.lineWidth=width;c.beginPath();points.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.stroke();}
 function circle(c,x,y,r,color=P.red,width=3){c.strokeStyle=color;c.lineWidth=width;c.beginPath();c.arc(x,y,r,0,2*Math.PI);c.stroke();}
 function arrow(c,x0,y0,x1,y1,color=P.red){stroke(c,[[x0,y0],[x1,y1]],color,2);let a=Math.atan2(y1-y0,x1-x0);for(const k of [-1,1])stroke(c,[[x1-12*Math.cos(a+k*.45),y1-12*Math.sin(a+k*.45)],[x1,y1]],color,2);}
 const paper=document.createElement('canvas');paper.width=256;paper.height=256;const pc=paper.getContext('2d'),im=pc.createImageData(256,256),rng=VK.rng(1729);
 for(let i=0;i<im.data.length;i+=4){im.data[i]=im.data[i+1]=im.data[i+2]=20;im.data[i+3]=Math.round(rng()*9);}pc.putImageData(im,0,0);
 function backdrop(c){c.fillStyle=P.paper;c.fillRect(0,0,1920,1080);c.fillStyle=c.createPattern(paper,'repeat');c.fillRect(0,0,1920,1080);}
 function frame(c,n,title,sub){text(c,`ATLAS / ${String(n).padStart(2,'0')}`,96,62,19,P.muted,'VK Mono');text(c,title,96,125,52);text(c,sub,1820,65,18,P.muted,'VK Mono','right');stroke(c,[[96,174],[1824,174]],'#c0cbbf',1);}
 function footer(c,s,note='球形地球 · 局部微分尺度 · 赤道为真尺度基准'){
  c.fillStyle=P.paper;c.fillRect(0,922,1920,158);stroke(c,[[96,922],[1824,922]],'#c0cbbf',1);
  text(c,s,960,978,39,P.ink,'VK Sans','center');text(c,note,960,1041,21,P.muted,'VK Sans','center');
 }
 function globe(c,x,y,r,rotate){
  const p=D.geoOrthographic().translate([x,y]).scale(r).rotate(rotate).precision(.25);
  c.save();c.shadowColor='#233e3533';c.shadowBlur=35;c.shadowOffsetY=15;
  G.paintMap(c,A,p,{ocean:P.water,land:P.land,coast:'#3f6b60',grid:'#91aaa0',width:.8});c.restore();
  c.save();c.beginPath();c.arc(x,y,r,0,2*Math.PI);c.clip();const grad=c.createRadialGradient(x-r*.4,y-r*.4,r*.1,x+r*.25,y+r*.2,r*1.25);grad.addColorStop(0,'#fffbe822');grad.addColorStop(.6,'#123a3000');grad.addColorStop(1,'#133b3055');c.fillStyle=grad;c.fillRect(x-r,y-r,2*r,2*r);c.restore();circle(c,x,y,r,'#355e53',1.2);return p;
 }
 function flat(c,morph=0,{x=920,y=530,scale=225,box=[[100,195],[1810,900]],alpha=1}={}){
  const p=G.cylindrical(morph).scale(scale).translate([x,y]).clipExtent(box);
  c.save();c.globalAlpha=alpha;G.paintMap(c,A,p,{ocean:P.water,land:P.land,coast:'#426c62',grid:'#9ab1a6'});c.restore();return p;
 }
 function band(c,p,lat,color){const pts=[];for(let lon=-180;lon<=180;lon+=2)pts.push([lon,lat]);c.beginPath();D.geoPath(p,c)({type:'LineString',coordinates:pts});c.strokeStyle=color;c.lineWidth=3;c.stroke();}
 function smallRegion(c,p,lon,lat,color=P.red){c.beginPath();D.geoPath(p,c)(D.geoCircle().center([lon,lat]).radius(4)());c.fillStyle=color+'33';c.fill();c.strokeStyle=color;c.lineWidth=2;c.stroke();}
 function measurement(c,x,y,b,sx,sy,{grid=false}={}){
  const w=b*sx,h=b*sy;c.save();c.setLineDash([7,7]);c.strokeStyle='#739589';c.lineWidth=2;c.strokeRect(x-b/2,y-b/2,b,b);c.setLineDash([]);
  c.fillStyle='#bb53381e';c.fillRect(x-w/2,y-h/2,w,h);c.strokeStyle=P.red;c.lineWidth=4;c.strokeRect(x-w/2,y-h/2,w,h);
  if(grid){stroke(c,[[x,y-h/2],[x,y+h/2]],P.red,2);stroke(c,[[x-w/2,y],[x+w/2,y]],P.red,2);}
  arrow(c,x-w/2,y+h/2+38,x+w/2,y+h/2+38);text(c,`${sx.toFixed(2)} ×`,x,y+h/2+72,28,P.red,'VK Mono','center');
  arrow(c,x+w/2+35,y+h/2,x+w/2+35,y-h/2);text(c,`${sy.toFixed(2)} ×`,x+w/2+68,y,28,P.red,'VK Mono');c.restore();
  // The probe reads dimensions actually passed to strokeRect, not an ideal time curve.
  state.sx=w/b;state.sy=h/b;state.area=w*h/(b*b);
 }
 function opening(c,t){
  frame(c,1,'同样大小，为什么看起来不同？','A WORLD / TWO SCALES');
  const q=ease(t,0,7);let p=globe(c,800,550,325,[-20-30*q,-22,0]);
  smallRegion(c,p,10,0);smallRegion(c,p,10,60);text(c,'地球上的两个微小区域',1290,430,31);text(c,'真实面积相同',1290,485,38,P.red);
  text(c,'放进地图以后呢？',1290,590,30);footer(c,'地图里的“大小”，一定是地球上的大小吗？','地球视图为正射投影，海岸线来自 Natural Earth');
 }
 function unfold(c,t){
  frame(c,2,'从球面，到一张纸','THE PRICE OF FLATTENING');const q=ease(t,7,10);
  const p=globe(c,460,550,240,[-20,-18,0]);smallRegion(c,p,10,0);smallRegion(c,p,10,60);
  arrow(c,760,540,900,540,P.muted);const p2=flat(c,0,{x:1370,y:565,scale:130,box:[[930,220],[1810,895]],alpha:q});
  c.save();c.globalAlpha=q;smallRegion(c,p2,10,0);smallRegion(c,p2,10,60);text(c,'Mercator',1370,855,24,P.muted,'VK Mono','center');c.restore();
  footer(c,'不是地球变了，是我们把球面放进了平面。');
 }
 function latitude(c,t){
  frame(c,3,'越往北，一圈越短','LATITUDE / CIRCUMFERENCE');const p=globe(c,620,550,300,[0,-90,0]);
  const phi=60*ease(t,14.6,19),r=300*Math.cos(phi*Math.PI/180);circle(c,620,550,300,P.red,3);circle(c,620,550,r,'#faf6e9',4);circle(c,620,550,r,P.red,2);
  arrow(c,620,550,620+r,550);text(c,`${Math.round(phi)}°`,960,390,64,P.red,'VK Mono');
  text(c,'赤道一圈',1140,475,28);text(c,'2πR',1510,475,42,P.ink,'VK Mono');text(c,`${Math.round(phi)}° 纬圈`,1140,585,28);text(c,phi>=59.99?'πR':`${(2*r/300).toFixed(2)}πR`,1510,585,42,P.red,'VK Mono');
  state.circumference=r/300;text(c,phi>=59.99?'周长只有一半':`赤道的 ${Math.round(r/300*100)}%`,1140,710,41);footer(c,phi>=59.99?'在60°纬度，一圈只有赤道那么长的一半。':'纬圈越靠近极点，一圈就越短。','纬圈周长 = 2πR cos φ · 北极俯视示意');
 }
 function stretch(c,t){
  const phase=t<29?4:t<37?5:6;frame(c,phase,phase===4?'把经线画成等距直线':phase===5?'保住角度，还要再拉一次':'长度两倍，面积四倍','MERCATOR / LOCAL SCALE');
  const p=flat(c,0,{x:660,y:550,scale:245,box:[[100,215],[1120,865]],alpha:.26});band(c,p,60,'#8b9c90');
  c.fillStyle='#ede8daec';c.fillRect(320,290,760,550);const origin=p([15,60]);stroke(c,[origin,[400,330]],P.muted,1.5);circle(c,...origin,5,P.red,2);text(c,'60° 附近 · 局部放大示意',435,326,22,P.muted);let sx=1+ease(t,22,27.5),sy=t<29?1:1+ease(t,29,34.5);measurement(c,610,520,160,sx,sy,{grid:t>=37});
  text(c,'60° N',1320,300,29,P.muted,'VK Mono');text(c,'东西',1300,410,30);text(c,`${sx.toFixed(2)} ×`,1530,410,52,P.red,'VK Mono');
  text(c,'南北',1300,520,30);text(c,`${sy.toFixed(2)} ×`,1530,520,52,P.red,'VK Mono');
  if(t>=37){text(c,'面积',1300,665,30);text(c,'4 ×',1515,665,104,P.red,'VK Mono');}
  else text(c,t<29?'短的一圈，被拉成同样宽。':'两方向同比例，局部角度才不变。',1260,680,28);
  footer(c,t<29?'东西方向，要放大两倍。':t<37?'墨卡托保局部角度，南北也得放大两倍。':'每个方向两倍，面积就是四倍。');
 }
 function reprojection(c,t){
  frame(c,7,'如果改为保面积呢？','SAME EARTH / DIFFERENT CHOICE');const q=ease(t,44,51.5),p=flat(c,q,{x:740,y:540,scale:180,box:[[90,220],[1330,885]]});
  band(c,p,60,P.red);smallRegion(c,p,15,60);const k=G.localScale(60,q);measurement(c,1520,510,100,k.x,k.y);
  text(c,'面积',1450,740,28);text(c,`${k.area.toFixed(2)} ×`,1450,800,48,P.red,'VK Mono');
  footer(c,'东西两倍 × 南北一半，面积回到一倍。','从 Mercator 连续变为 Lambert 柱面等面积；中间态仅为演示');
 }
 function compare(c,t){
  frame(c,8,'面积保住了，形状却变了','CONFORMAL / EQUAL AREA');
  for(const [i,m] of [[0,0],[1,1]]){
   const x=510+i*900;const p=flat(c,m,{x,y:480,scale:95,box:[[x-390,285],[x+390,620]]});
   text(c,m?'等面积':'保局部角度',x,235,31,P.ink,'VK Sans','center');
   const pos=p([20,60]);stroke(c,[pos,[x,660]],P.red,1.2);circle(c,...pos,5,P.red,2);text(c,'60° 局部',x+125,700,20,P.muted);const k=G.localScale(60,m);c.save();c.strokeStyle=P.red;c.lineWidth=3;c.fillStyle='#bb53382a';c.beginPath();c.ellipse(x,738,40*k.x,40*k.y,0,0,Math.PI*2);c.fill();c.stroke();c.restore();
   text(c,m?'面积 ×1，局部圆被压扁':'面积 ×4，局部角度不变',x,830,26,P.red,'VK Sans','center');
  }
  state.area=1;state.sx=2;state.sy=.5;footer(c,'保面积，不会同时保住局部形状。');
 }
 function choice(c,t){
  frame(c,9,'先问：你要保住什么？','ASK THE MAP A BETTER QUESTION');
  const q=ease(t,61,64),p=flat(c,q,{x:820,y:520,scale:205,box:[[110,210],[1550,880]]});band(c,p,60,P.red);
  text(c,'局部角度',1550,400,36,q<.5?P.red:P.muted);text(c,'比较面积',1550,600,36,q>=.5?P.red:P.muted);
  footer(c,'地图的取舍，应该跟着你的问题走。');
 }
 function ending(c,t){
  const p=globe(c,570,510,290,[-44-3*(t-68),-20,0]);
  text(c,'地图',1050,380,64);text(c,'是一种选择。',1050,485,76,P.red,'VK Serif');
  text(c,'不是世界的复制品。',1050,600,35);text(c,'A MAP IS AN ARGUMENT.',1055,700,21,P.muted,'VK Mono');
  footer(c,'球面无法原样铺平。先问地图保住了什么。','资料：USGS / Snyder 1987 · 制图几何：D3 · 海岸线：Natural Earth');state.closing=1;
 }
 const rows=[
  ['x-scale','stretch-x','sx',2],['angle-scale','keep-angle','sy',2],['four-area','four','area',4],['one-area','equal-area','area',1],['end-complete','finish','closing',1],['latitude-half','latitude-half','circumference',.5]
 ];for(const event of ['opening-layout','latitude-half','stretch-x','keep-angle','four','equal-area','compare','choice-layout','finish'])rows.push([`text-${event}`,event,'textOverflow',0]);window.VK_CHECKS=C.visualChecks(SCORE,rows.map(([id,event,key,value])=>({id,event,min:value-.0001,max:value+.0001,measure:()=>state[key],unit:key==='closing'?'visible ending':key==='area'?'area ratio':'length ratio',description:`实际绘制状态 ${key} 应达到 ${value}`})));
 VK.film({dur:72,theme:'flat',bloom:0,grain:0,meta:{title:'地图是一种选择',drone:0},draw(fr,t){
  state.sx=1;state.sy=1;state.area=1;state.closing=0;state.circumference=1;state.textOverflow=0;
  fr.look.under=c=>{backdrop(c);if(t<7)opening(c,t);else if(t<14)unfold(c,t);else if(t<22)latitude(c,t);else if(t<44)stretch(c,t);else if(t<53)reprojection(c,t);else if(t<61)compare(c,t);else if(t<68)choice(c,t);else ending(c,t);};
 }});
})().catch(e=>{window.READY_ERROR=String(e);});

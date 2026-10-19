(async()=>{
 const [{portrait},M,C,I,{SCORE},claims]=await Promise.all([import('./portrait.mjs'),import('/engine/vk-motion.mjs'),import('/engine/vk-checks.mjs'),import('/engine/vk-image.mjs'),import('./score.mjs'),fetch('claims.json').then(r=>r.json())]);
 const P=await portrait(),person=new Image();person.src='assets/person.png';await person.decode();window.VK_SCORE=SCORE;
 const base=document.createElement('canvas');base.width=person.width;base.height=person.height;base.getContext('2d').drawImage(person,0,0);
 const mirrored=document.createElement('canvas');mirrored.width=base.width;mirrored.height=base.height;const mc=mirrored.getContext('2d');mc.translate(base.width,0);mc.scale(-1,1);mc.drawImage(base,0,0);
 const da=base.getContext('2d').getImageData(0,0,base.width,base.height).data,db=mc.getImageData(0,0,base.width,base.height).data;let pixelMirrorError=0;
 for(let y=0;y<base.height;y+=23)for(let x=0;x<base.width;x+=17)for(let k=0;k<4;k++)pixelMirrorError=Math.max(pixelMirrorError,Math.abs(da[(y*base.width+x)*4+k]-db[(y*base.width+base.width-1-x)*4+k]));
 const arrive=SCORE.event('photo-arrives'),flip=SCORE.event('flip'),move=SCORE.event('camera-move');
 const palette={paper:'#eee9de',ink:'#343e3a',sage:'#6d8070',red:'#a76856',muted:'#737b70',line:'#c5c8ba'};
 const state={distance:1.5,textOverflow:0,minCoreFont:999,selfCount:0,partnerCount:0,closing:0,imageDistortion:0};
 const ease=(t,a,b)=>M.smooth((t-a)/(b-a)),mix=(a,b,u)=>a+(b-a)*u;
 function txt(c,s,x,y,size=48,color=palette.ink,align='left',core=true,font='VK Sans',weight=500){
  c.font=`${weight} ${size}px "${font}"`;c.fillStyle=color;c.textAlign=align;c.textBaseline='middle';
  const m=c.measureText(s),left=align==='center'?x-m.width/2:align==='right'?x-m.width:x;
  state.textOverflow=Math.max(state.textOverflow,-left,left+m.width-1920,size/2-y,y+size/2-1080);
  if(core)state.minCoreFont=Math.min(state.minCoreFont,size);c.fillText(s,x,y);
 }
 function line(c,points,color=palette.line,w=2){c.beginPath();points.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.lineWidth=w;c.strokeStyle=color;c.stroke();}
 function rect(c,x,y,w,h,r=0,fill=palette.paper){c.beginPath();c.roundRect(x,y,w,h,r);c.fillStyle=fill;c.fill();}
 function photo(c,image,x,y,w,h,{angle=0,alpha=1,frame=true}={}){
  c.save();c.globalAlpha*=alpha;c.translate(x+w/2,y+h/2);c.rotate(angle);c.shadowColor='#3e3b2922';c.shadowBlur=30;c.shadowOffsetY=14;
  rect(c,-w/2-14,-h/2-14,w+28,h+58,2,'#f8f6ed');c.shadowColor='transparent';const a=I.paintImage(c,image,[-w/2,-h/2,w,h]);state.imageDistortion=Math.max(state.imageDistortion,Math.abs(a.scaleX-a.scaleY));c.restore();
 }
 function mirror(c,image,x,y,w,h){c.save();c.shadowColor='#5f625833';c.shadowBlur=38;c.shadowOffsetY=15;
  const metal=c.createLinearGradient(x,y,x+w,y+h);metal.addColorStop(0,'#b7b8a8');metal.addColorStop(.35,'#e1deca');metal.addColorStop(.7,'#999e92');metal.addColorStop(1,'#d0cbb5');
  rect(c,x-12,y-12,w+24,h+24,w/2,metal);c.shadowColor='transparent';c.beginPath();c.roundRect(x,y,w,h,w/2);c.clip();const a=I.paintImage(c,image,[x,y,w,h]);state.imageDistortion=Math.max(state.imageDistortion,Math.abs(a.scaleX-a.scaleY));c.restore();}
 const CUES=[
 [0,4,'有时，为什么觉得镜子里的自己更好看？'],[4,8,'同一个人，怎么有点陌生？'],
 [8,13,'先不换表情和光线，只做水平翻转。'],[13,18,'你更习惯哪一边？'],[18,22,'这不是颜值测验。'],
 [22,27,'1977年，研究者把同一照片印成两个朝向。'],[27,32,'熟人会和你选同一个方向吗？'],[32,37,'研究2：28对本人和伴侣，各选五次。'],
 [37,42,'多数偏好：本人偏镜像，伴侣偏普通照。'],[42,46,'熟悉，可能影响我们偏爱哪一张。'],[46,49,'这是群体结果，不是每个人的答案。'],
 [49,55,'但有些近照，翻回来仍有点不同。'],[55,59,'这次不翻转。只改变相机距离。'],[59,64,'靠近时，鼻子比脸颊离镜头更近。'],
 [64,69,'距离差，占拍摄距离的比例变大。'],[69,73,'近处的部分，在投影中显得更大。'],[73,77,'这是透视变化，不是你的脸改变了。'],
 [78,81,'朝向的陌生，和距离的变化——'],[81,85,'是两件不同的事。'],[85,90,'光线、角度、表情和处理，也会影响照片。'],
 [90,94,'没有一条研究，能替每张照片下结论。'],[94,99,'镜子给你熟悉的朝向。'],[99,104,'照片留下某个角度、某段距离的一刻。'],[104,109,'陌生的那一张，不必成为对自己的判决。']];
 function caption(c,t){const q=CUES.find(q=>t>=q[0]&&t<q[1]);if(!q)return;const a=Math.min(1,(t-q[0])/.16,(q[1]-t)/.16);c.save();c.globalAlpha=a;txt(c,q[2],960,994,64,palette.ink,'center');c.restore();}
 function source(c,s){txt(c,s,960,1050,30,palette.muted,'center',false);}
 function opening(c,t){
  const q=ease(t,arrive.start,arrive.end);mirror(c,mirrored,240,165,470,470*base.height/base.width);
  c.save();c.globalAlpha=q;photo(c,base,1120,165+M.impulse(t-arrive.start,{velocity:36,frequency:2,damping:.65}),470,470*base.height/base.width,{angle:-.04});c.restore();
  txt(c,'镜子',475,835,48,palette.sage,'center');if(q>.1)txt(c,'照片',1350,835,48,palette.red,'center');
  txt(c,'另一种你',960,65,76,palette.ink,'center',true,'VK Serif');
  if(t<4)txt(c,'你有没有过这样的时刻？',1255,460,52,palette.muted,'center');
  source(c,'原创虚构人像 · 朝向演示，不是真实参与者');
 }
 function orientation(c,t){
  if(t<13){const turn=ease(t,flip.start,flip.end)*Math.PI,scale=Math.max(.015,Math.abs(Math.cos(turn)));
   c.save();c.translate(960,480);c.scale(scale,1);photo(c,turn<Math.PI/2?mirrored:base,-260,-330,520,650);c.restore();
   txt(c,'只改变朝向',960,100,60,palette.sage,'center');
  }else{photo(c,mirrored,360,180,460,575);photo(c,base,1100,180,460,575);
   txt(c,'镜像',590,845,48,palette.sage,'center');txt(c,'普通朝向',1330,845,48,palette.red,'center');
   txt(c,'同一图像 · 同一大小 · 同一光线',960,90,48,palette.muted,'center');}
  source(c,'观察体验不证明群体偏好；你不需要选出“正确答案”');
 }
 function dots(c,x,y,count,total,color){for(let i=0;i<total;i++){c.beginPath();c.arc(x+(i%7)*46,y+Math.floor(i/7)*46,12,0,2*Math.PI);c.fillStyle=i<count?color:'#d5d6c9';c.fill();}}
 function study(c,t){
  if(t<32){const q=ease(t,23,26);photo(c,base,190,210,320,400,{angle:-.06});photo(c,mirrored,610,210,320,400,{angle:.05});
   txt(c,'同一底片',540,760,52,palette.sage,'center');
   txt(c,'本人',1370,300,64);txt(c,'熟人',1370,525,64);line(c,[[970,415],[1220,300],[1310,300]],palette.sage,3);line(c,[[970,415],[1220,525],[1310,525]],palette.red,3);
   txt(c,'Mita · Dermer · Knight',1200,112,42,palette.muted,'center',false);
  }else{
   photo(c,mirrored,150,210,280,350,{angle:-.045});photo(c,base,1490,210,280,350,{angle:.045});
   txt(c,'本人',695,210,60,palette.sage,'center');txt(c,'伴侣',1210,210,60,palette.red,'center');
   const showSelf=ease(t,33,35),showPartner=ease(t,37,39);state.selfCount=t>=35?claims.study.selfMirror:0;state.partnerCount=t>=39?claims.study.partnerOrdinary:0;
   dots(c,555,330,t>=35?claims.study.selfMirror:0,claims.study.pairs,palette.sage);dots(c,1070,330,t>=39?claims.study.partnerOrdinary:0,claims.study.pairs,palette.red);
   c.save();c.globalAlpha=showSelf;txt(c,`${claims.study.selfMirror} / ${claims.study.pairs}`,695,610,82,palette.sage,'center');txt(c,'偏向镜像',695,730,50,palette.sage,'center');c.restore();
   c.save();c.globalAlpha=showPartner;txt(c,`${claims.study.partnerOrdinary} / ${claims.study.pairs}`,1210,610,82,palette.red,'center');txt(c,'偏向普通照',1210,730,50,palette.red,'center');c.restore();
   txt(c,'28对 · 五次选择的多数偏好',960,105,48,palette.muted,'center');
   txt(c,'不是实时投票，也不是所有人的选择',960,850,44,palette.muted,'center');
  }
  source(c,'示意人像 · Mita 等，1977，研究2 · 女性本人 / 男性伴侣子样本');
 }
 function doubt(c,t){
  photo(c,mirrored,300,180,450,562,{angle:-.04});photo(c,base,1150,180,450,562,{angle:.04});
  txt(c,t<49?'熟悉 ≠ 唯一原因':'翻回来，就一样了吗？',960,100,64,palette.ink,'center');
  txt(c,t<49?'朝向的经验':'还有：拍摄距离',960,825,54,palette.red,'center');
  source(c,t<49?'群体趋势与熟悉性解释一致；不代表每个人偏爱镜像':'下面切换独立三维教学模型，不是原人像或研究参与者');
 }
 let farImage,farRatio,farNosePoints;
 function geometry(c,t){
  const near=claims.distance.near,far=claims.distance.far;state.distance=M.track([[55,far],[move.start,far],[move.end,near],[69,near]],t);
  P.set(state.distance);Object.assign(state,P.metrics());
  if(!farImage){P.set(far);farImage=document.createElement('canvas');farImage.width=768;farImage.height=896;farImage.getContext('2d').drawImage(P.canvas,0,0);const fm=P.metrics();farRatio=fm.noseWidth/fm.cheekWidth;farNosePoints=fm.nosePoints;P.set(state.distance);}
  txt(c,'同一个头模型，只改相机距离',960,92,60,palette.ink,'center');
  photo(c,farImage,225,200,500,583);photo(c,P.canvas,1195,200,500,583);
  txt(c,'1.5 m',475,847,56,palette.sage,'center');txt(c,`${(state.distance*100).toFixed(1)} cm`,1445,847,56,palette.red,'center');
  for(const [x,pts] of [[225,farNosePoints],[1195,state.nosePoints]]){const yy=200+(1-pts[0][1])*583/2+28;const xx=pts.map(p=>x+(p[0]+1)*500/2);line(c,[[xx[0],yy],[xx[1],yy]],palette.red,3);for(const a of xx)line(c,[[a,yy-8],[a,yy+8]],palette.red,3);}
  txt(c,'鼻翼 / 脸颊比',960,310,44,palette.muted,'center');txt(c,`×${((state.noseWidth/state.cheekWidth)/farRatio).toFixed(2)}`,960,400,72,palette.red,'center');
  const camX=mix(820,1095,ease(t,move.start,move.end));rect(c,camX,470,68,45,7,palette.sage);line(c,[[camX+68,480],[camX+87,470],[camX+87,515],[camX+68,505]],palette.sage,3);line(c,[[820,550],[1140,550]],palette.line,3);
  txt(c,'靠近',960,625,48,palette.muted,'center');
  source(c,'示意模型 · 相对1.5m的当前模型比值，非论文数值 · 脸颊参照宽相同');
 }
 function projection(c,t){
  const d=M.track([[69,1.5],[71,1.5],[75,.3048],[77,.3048]],t),delta=.034;
  const cx=760+440*(d-.3048)/(1.5-.3048),cy=510,plane=1470;
  txt(c,'距离差，怎样变成比例差？',960,100,64,palette.ink,'center');
  // Equal-length marks at two parallel depth planes isolate perspective magnification.
  for(const [x,col,label] of [[300,palette.sage,'脸颊平面'],[390,palette.red,'鼻端平面']]){
   line(c,[[x,390],[x,630]],col,5);txt(c,label,x===300?250:520,x===300?265:330,44,col,'center');
   for(const y of [390,630]){const screenY=cy-(y-cy)*(plane-cx)/(cx-x);line(c,[[x,y],[cx,cy],[plane,screenY]],col,2);}
  }
  rect(c,cx-28,cy-30,56,60,7,palette.ink);line(c,[[plane,230],[plane,790]],palette.ink,4);
  txt(c,'相机',cx,720,48,palette.ink,'center');txt(c,'投影面',plane,850,48,palette.ink,'center');
  txt(c,'越靠近，相同深度差越显眼',960,165,44,palette.muted,'center');
  source(c,'平行面/等长标记光路示意（非比例图），非真实面部测量 · Ward 等，2018提供几何研究入口');
 }
 function distinct(c,t){
  txt(c,'两个问题，分开看',960,100,64,palette.ink,'center');
  photo(c,mirrored,195,235,285,356);photo(c,base,535,235,285,356);
  photo(c,farImage||P.base,1110,235,285,356);P.set(claims.distance.near);photo(c,P.canvas,1450,235,285,356);
  txt(c,'朝向 / 熟悉',505,755,56,palette.sage,'center');txt(c,'距离 / 透视',1420,755,56,palette.red,'center');
  source(c,'翻转不会消除距离造成的比例变化；两项研究不能合成一个万能解释');
 }
 function limits(c,t){
  photo(c,base,260,160,500,625,{angle:mix(-.02,.02,ease(t,85,94))});
  txt(c,'不只一种条件',1250,215,68,palette.ink,'center');
  ['光线与角度','表情与姿态','处理与观看情境'].forEach((s,i)=>txt(c,s,1260,400+i*140,54,i===2?palette.red:palette.sage,'center'));
  source(c,'其他因素未由1977/2018两篇研究逐项检验；不对个人照片诊断原因');
 }
 function ending(c,t){
  const u=ease(t,94,108);mirror(c,mirrored,250+20*u,155,430-20*u,(430-20*u)*base.height/base.width);photo(c,base,1190-20*u,155,430-20*u,(430-20*u)*base.height/base.width,{angle:-.025});
  txt(c,'另一种你',960,430,84,palette.ink,'center',true,'VK Serif');
  if(t>=108){txt(c,'镜子与照片，为什么看起来不同',960,840,48,palette.sage,'center');state.closing=1;}
  source(c,'Mita 等 1977 · Ward 等 2018 · 研究条件、许可与完整来源见源码facts.md');
 }
 window.MIRROR={inspect:()=>({...state,pixelMirrorError,geometryHash:P.geometryHash(),study:claims.study,glError:P.scene.renderer.getContext().getError()}),cues:()=>CUES};
 const checks=[
  {id:'opening-image-aspect',event:'photo-arrives',offset:2,min:0,max:1e-12,unit:'scale anisotropy',measure:()=>state.imageDistortion,description:'实际绘制图像保持纵横相同比例，不以拉瘦镜中脸制造差异'},
  {id:'closing-image-aspect',event:'closing',min:0,max:1e-12,unit:'scale anisotropy',measure:()=>state.imageDistortion,description:'结尾人像同样保持原始比例'},
  {id:'same-pixels-reversed',event:'orientation',min:0,max:0,unit:'max sampled channel error',measure:()=>pixelMirrorError,description:'实际使用的两张人像仅为水平像素反转；不证明主观偏好'},
  {id:'self-count',event:'study-self',min:20,max:20,unit:'participants',measure:()=>state.selfCount,description:'实际绘图共读原研究2多数偏好计数'},
  {id:'partner-count',event:'study-partner',min:19,max:19,unit:'participants',measure:()=>state.partnerCount,description:'伴侣偏普通朝向的多数计数，不是首次选择'},
  {id:'far-camera',event:'distance-start',min:1.4999,max:1.5001,unit:'m',measure:()=>state.distance,description:'轴上相机实际距离设置'},
  {id:'near-camera',event:'near',min:.30479,max:.30481,unit:'m',measure:()=>state.distance,description:'相机到脸颊参考平面距离'},
  {id:'completed-ending',event:'closing',min:1,max:1,unit:'visible ending',measure:()=>state.closing,description:'完整回扣与片尾，而非开头技术片段'}
 ];
 for(const event of ['orientation','study-self','study-partner','distance-start','near','separate','closing'])checks.push({id:`text-${event}`,event,min:0,max:0,unit:'canvas px overflow',measure:()=>state.textOverflow,description:'本帧实际字体量测画布边界'});
 window.VK_CHECKS=C.visualChecks(SCORE,checks);
 VK.film({dur:112,theme:'flat',bloom:0,grain:0,meta:{title:'另一种你',drone:0},draw(fr,t){
  state.textOverflow=0;state.minCoreFont=999;state.selfCount=0;state.partnerCount=0;state.closing=0;state.imageDistortion=0;
  fr.look.under=c=>{c.fillStyle=palette.paper;c.fillRect(0,0,1920,1080);
   // The main stage has varied framing; no permanent dashboard/chapter grid.
   if(t<8)opening(c,t);else if(t<22)orientation(c,t);else if(t<42)study(c,t);else if(t<55)doubt(c,t);else if(t<69)geometry(c,t);else if(t<78)projection(c,t);else if(t<85)distinct(c,t);else if(t<94)limits(c,t);else ending(c,t);
   caption(c,t);
  };
 }});
})().catch(e=>window.READY_ERROR=String(e));

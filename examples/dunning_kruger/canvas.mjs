import * as M from '/engine/vk-motion.mjs';
export const P={bg:'#080b11',white:'#e7dfcc',gold:'#c6a264',red:'#b96758',muted:'#a59d8d',paper:'#ded1b2',ink:'#29251f'};
export const ss=(t,a,b)=>M.smooth((t-a)/(b-a));
export const mix=(a,b,k)=>a+(b-a)*k;
export function txt(c,s,x,y,size=46,col=P.white,align='center',font='VK Serif',weight=400){c.font=`${weight} ${size}px "${font}"`;c.textAlign=align;c.textBaseline='middle';c.fillStyle=col;c.fillText(s,x,y);return c.measureText(s).width;}
export function ln(c,a,b,col=P.gold,w=2){c.strokeStyle=col;c.lineWidth=w;c.lineCap='round';c.beginPath();c.moveTo(...a);c.lineTo(...b);c.stroke();}
export function dot(c,x,y,r=7,col=P.gold){c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fillStyle=col;c.fill();}
const grain=document.createElement('canvas');grain.width=480;grain.height=270;
{const c=grain.getContext('2d'),im=c.createImageData(480,270);let s=735;for(let i=0;i<im.data.length;i+=4){s=(Math.imul(s,1664525)+1013904223)>>>0;const v=s>>>24;im.data.set([v,v,v,255],i);}c.putImageData(im,0,0);}
export function background(c,t){
 const g=c.createRadialGradient(940,330,20,940,430,1100);g.addColorStop(0,'#29231c');g.addColorStop(.48,'#111318');g.addColorStop(1,'#06080d');c.fillStyle=g;c.fillRect(0,0,1920,1080);
 c.save();c.globalCompositeOperation='soft-light';c.globalAlpha=.045;c.drawImage(grain,0,0,1920,1080);c.restore();
 // Sparse out-of-focus dust only gives depth; it never carries a concept.
 c.save();for(let i=0;i<26;i++){const x=(VK.hash(i+32)*2000+t*(1+VK.hash(i)*2))%2000-40,y=(VK.hash(i+131)*950-t*.8+1080)%1080;
 c.globalAlpha=.04+VK.hash(i+18)*.09;dot(c,x,y,.7+VK.hash(i+9)*2,P.paper);}c.restore();
}
export function paper(c,x,y,w,h,angle=0,fn=()=>{}){
 c.save();c.translate(x,y);c.rotate(angle);c.shadowColor='#000b';c.shadowBlur=35;c.shadowOffsetY=22;
 const g=c.createLinearGradient(-w/2,-h/2,w/2,h/2);g.addColorStop(0,'#efe4cb');g.addColorStop(.6,'#d9cbab');g.addColorStop(1,'#c4b492');c.fillStyle=g;c.fillRect(-w/2,-h/2,w,h);c.shadowBlur=0;c.shadowOffsetY=0;
 c.strokeStyle='#fff5';c.lineWidth=2;c.strokeRect(-w/2+4,-h/2+4,w-8,h-8);
 c.save();c.globalAlpha=.07;c.globalCompositeOperation='multiply';c.drawImage(grain,-w/2,-h/2,w,h);c.restore();fn(c);c.restore();
}
export const Q=[[-310,-185],[310,-185],[0,310],[0,15]];
export const E=[[0,1],[1,2],[2,0],[0,3],[1,3],[2,3]];
export function graph(c,{x=960,y=460,s=1,progress=0,path=[0,1,2,0,3,1],mark=0,remove=0,labels=false}={}){
 c.save();c.translate(x,y);c.scale(s,s);
 const opacity=c.globalAlpha;E.forEach(([a,b],i)=>{c.globalAlpha=opacity*(i===0?1-remove:1);ln(c,Q[a],Q[b],'#7b7059',5);});c.globalAlpha=opacity;
 for(let j=0;j<path.length-1;j++){
  const u=Math.max(0,Math.min(1,progress-j));if(!u)continue;
  const a=Q[path[j]],b=Q[path[j+1]];ln(c,a,[mix(a[0],b[0],u),mix(a[1],b[1],u)],P.gold,8);
 }
 Q.forEach(([a,b],i)=>{
  c.shadowBlur=0;dot(c,a,b,17,'#26231e');dot(c,a,b,12,i<mark?P.red:P.white);dot(c,a-2,b-3,3,'#fff6');
  if(labels)txt(c,String(E.filter(e=>e.includes(i)).length),a+(a<0?-38:a>0?38:36),b-30,38,P.red);
 });c.restore();
}
export function pathBetween(c,pts,k=1,color=P.gold,width=5){
 const lengths=pts.slice(1).map((p,i)=>Math.hypot(p[0]-pts[i][0],p[1]-pts[i][1]));const total=lengths.reduce((a,b)=>a+b,0);let left=k*total;
 for(let i=0;i<lengths.length&&left>0;i++){const u=Math.min(1,left/lengths[i]);ln(c,pts[i],[mix(pts[i][0],pts[i+1][0],u),mix(pts[i][1],pts[i+1][1],u)],color,width);left-=lengths[i];}
}
export function flourish(c,x,y,w,k=1){c.save();c.strokeStyle=P.gold;c.lineWidth=1.5;c.beginPath();c.moveTo(x-w/2,y);c.bezierCurveTo(x-w*.22,y,x-w*.12,y-28,x,y-28);c.bezierCurveTo(x+w*.12,y-28,x+w*.22,y,x+w/2,y);c.stroke();dot(c,x-w/2,y,2);dot(c,x+w/2,y,2);c.restore();}

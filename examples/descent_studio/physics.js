(function(){
'use strict';
const g=9.81, X=1,Y=.6;
let lo=.001,hi=2*Math.PI-.001;
for(let i=0;i<100;i++){let q=(lo+hi)/2;if((q-Math.sin(q))/(1-Math.cos(q))<X/Y)lo=q;else hi=q;}
const theta=(lo+hi)/2,a=Y/(1-Math.cos(theta)),L=Math.hypot(X,Y),Tc=theta*Math.sqrt(a/g),Ts=Math.sqrt(2*L*L/(g*Y));
function curve(q){return {x:a*(q-Math.sin(q)),y:a*(1-Math.cos(q))};}
function sample(kind,t){let end=kind==='c'?Tc:Ts,tt=Math.max(0,Math.min(end,t)),x,y,dx,dy;
if(kind==='c'){let q=tt*Math.sqrt(g/a),p=curve(q);x=p.x;y=p.y;dx=1-Math.cos(q);dy=Math.sin(q);if(tt===0){dx=0;dy=1;}}
else{let s=.5*g*Y/L*tt*tt;x=s/L;y=s*Y/L;dx=1;dy=Y;}
let n=Math.hypot(dx,dy);return {x,y,v:Math.sqrt(2*g*y),tx:dx/n,ty:dy/n,t:tt,end};}
window.PHYS={g,X,Y,theta,a,L,Tc,Ts,Lc:4*a*(1-Math.cos(theta/2)),curve,sample};
})();

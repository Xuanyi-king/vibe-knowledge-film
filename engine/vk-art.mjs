/* Optional editorial roles, not a global theme. Reuses Frame's text shaping. */
export const INK=Object.freeze({black:'#131619',graphite:'#24282b',ivory:'#eee7d8',muted:'#a5aea9',gold:'#d1b77e',red:'#ba6759',blue:'#819baa'});
export const TYPE=Object.freeze({
  title:{font:'serifm',size:76,track:1.2,color:INK.ivory},
  concept:{font:'serif',size:86,color:INK.ivory},
  number:{font:'mono',size:74,color:INK.gold},
  caption:{font:'sansm',size:64,color:INK.ivory},
  label:{font:'sansm',size:42,color:INK.muted},
  source:{font:'sansr',size:25,color:INK.muted},
  eyebrow:{font:'mono',size:24,track:2.5,color:INK.muted},
});
// Layout bounds use real text advance and a conservative vertical reserve.
// They do not detect occlusion, ink contours or subjective readability.
export function type(fr,text,x,y,{role='caption',maxWidth=1728,align='l',importance,id=null,background=null,...overrides}={}) {
  if(!TYPE[role])throw Error(`unknown type role ${role}`);
  if(![x,y,maxWidth].every(Number.isFinite)||maxWidth<=0)throw Error('type position/width must be finite; width positive');
  if(!['l','c','r'].includes(align))throw Error('type align must be l/c/r');
  const style={...TYPE[role],...overrides,align};
  importance??= ['title','concept','number','caption'].includes(role)?'essential':role==='eyebrow'?'decorative':'supporting';
  if(!['essential','supporting','decorative'].includes(importance))throw Error('invalid type importance');
  if(!(Number.isFinite(style.size)&&style.size>0))throw Error('type size must be positive');
  // FontFaceSet.check alone returns true for an unregistered fallback family.
  const family=(VK.FONTS[style.font]||VK.FONTS.serif)[1].split(',')[0].replace(/["']/g,'');
  if(![...document.fonts].some(f=>f.family.replace(/["']/g,'')===family&&f.status==='loaded'))
    throw Error(`required font ${family} is not registered/loaded; use engine/index.html font-face declarations and get_fonts.py`);
  const width=fr.measure(String(text),style),left=x-(align==='c'?width/2:align==='r'?width:0);
  if(width>maxWidth)throw Error(`type exceeds ${maxWidth}px (${width.toFixed(1)}px); rewrite/split the line instead of shrinking it`);
  const box={left,top:y-style.size*.7,width,height:style.size*1.4,style};
  const m=fr.x.getTransform(),points=[[left,box.top],[left+width,box.top],[left,box.top+box.height],[left+width,box.top+box.height]].map(([px,py])=>[m.a*px+m.c*py+m.e,m.b*px+m.d*py+m.f]);
  const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
  const entry={id,text:String(text),role,importance,background,left:Math.min(...xs),top:Math.min(...ys),
    width:Math.max(...xs)-Math.min(...xs),height:Math.max(...ys)-Math.min(...ys),
    style:{font:style.font,size:style.size*Math.hypot(m.c,m.d),color:typeof style.color==='string'?style.color:null,
           track:(style.track||0)*Math.hypot(m.a,m.b),a:(style.a??1)*fr.x.globalAlpha,blur:style.blur||0}};
  fr.text(String(text),x,y,style);(fr.artLayout??=[]).push(entry);return box;
}

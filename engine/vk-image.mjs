/* Aspect-safe image placement. Crop/letterbox deliberately, never stretch a face. */
export function paintImage(ctx,image,[x,y,width,height],{fit='cover'}={}) {
 const iw=image.videoWidth||image.naturalWidth||image.width,ih=image.videoHeight||image.naturalHeight||image.height;
 if(![x,y,width,height,iw,ih].every(Number.isFinite)||Math.min(width,height,iw,ih)<=0||!['cover','contain'].includes(fit))throw Error('finite positive image/box dimensions and cover/contain required');
 const scale=(fit==='cover'?Math.max:Math.min)(width/iw,height/ih),w=iw*scale,h=ih*scale;
 const dx=x+(width-w)/2,dy=y+(height-h)/2;
 ctx.save();ctx.beginPath();ctx.rect(x,y,width,height);ctx.clip();ctx.drawImage(image,dx,dy,w,h);ctx.restore();
 return {source:[iw,ih],destination:[dx,dy,w,h],scaleX:w/iw,scaleY:h/ih};
}

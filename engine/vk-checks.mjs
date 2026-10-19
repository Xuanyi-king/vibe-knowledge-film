/* Numeric assertions on rendered scene state; no image semantics or aesthetics. */
export function visualChecks(score,definitions) {
  const data=score.json(),ids=new Set(),items=definitions.map(d=>{
    if(!d.id||ids.has(d.id)||typeof d.measure!=='function')throw Error('visual checks need unique IDs and measure()');
    ids.add(d.id);const event=score.event(d.event),anchor=d.anchor??'start';
    if(!['start','end'].includes(anchor))throw Error('visual check anchor must be start or end');
    const requested=event[anchor]+(d.offset??0),frame=Math.round(requested*data.fps),time=frame/data.fps;
    if(!Number.isFinite(requested)||requested<0||requested>data.end||frame>=Math.round(data.end*data.fps)||
       !Number.isFinite(d.min)||!Number.isFinite(d.max)||d.min>d.max)throw Error('visual check time/range invalid');
    return {...d,descriptor:{id:d.id,event:d.event,anchor,event_time:event[anchor],offset:d.offset??0,
      requested_time:requested,frame,time,quantization_seconds:time-requested,min:d.min,max:d.max,
      unit:d.unit??'scene units',description:d.description??'',has_sound:!!event.sound}};
  });
  return {
    list(){return items.map(d=>structuredClone(d.descriptor));},
    measure(id){
      const d=items.find(d=>d.id===id);if(!d)throw Error(`unknown visual check ${id}`);
      const value=d.measure();const finite=typeof value==='number'&&Number.isFinite(value);
      return {...structuredClone(d.descriptor),value:finite?value:null,passed:finite&&value>=d.min&&value<=d.max,
        ...(finite?{}:{error:'measure() did not return a finite number'})};
    }
  };
}

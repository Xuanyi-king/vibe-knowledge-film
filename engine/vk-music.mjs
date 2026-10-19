/* One phrase in the same absolute clock as camera/action events. No fixed style. */
export function phrase(clock,{id,beat=0,notes,instrument,tail=.5,gain=1,pan=0,track='music'}) {
  if(!id||!Array.isArray(notes)||!Number.isFinite(beat)||!Number.isFinite(tail)||tail<0||!Number.isFinite(gain)||gain<0||!Number.isFinite(pan)||Math.abs(pan)>1)throw Error('invalid phrase parameters');
  const end=clock.json().end;
  return notes.flatMap(([offset,midi,length,velocity=1],i)=>{
    if(!Number.isFinite(offset)||offset<0||!Number.isFinite(length)||length<=0||!Number.isFinite(velocity)||velocity<0)throw Error('note requires offset >= 0, length > 0, velocity >= 0');
    if(midi===null)return []; // A rest occupies musical time, creates no audio event.
    const sample=instrument.notes?.[midi];if(!sample?.src||!sample.license||!(sample.duration>0))throw Error(`prepared sample missing for MIDI ${midi}`);
    const start=clock.time(beat+offset),held=clock.time(beat+offset+length)-start;
    if(start<0||start>=end)throw Error('note outside film');
    return [{id:`${id}-${i}`,start,duration:Math.min(sample.duration,held+tail,end-start),action:'music',sound:{kind:'sample',src:sample.src,license:sample.license,gain:gain*velocity,pan,track}}];
  });
}

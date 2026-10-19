/* Optional D3 geographic geometry adapter. No transitions/timers or remote assets. */
const radians=Math.PI/180;
export function localScale(latitude,morph=0) {
  if(!Number.isFinite(latitude)||Math.abs(latitude)>=90||!Number.isFinite(morph)||morph<0||morph>1)throw Error('latitude in (-90,90), morph in [0,1] required');
  const c=Math.cos(latitude*radians),x=1/c,y=(1-morph)/c+morph*c;return{x,y,area:x*y};
}
async function script(src){await new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=src;s.onload=resolve;s.onerror=()=>reject(Error(`Missing ${src}; run python engine/get_geo_assets.py`));document.head.append(s);});}
export async function loadAtlas() {
  if(!window.d3?.geoPath){await script('/engine/vendor/geo/d3-array.min.js');await script('/engine/vendor/geo/d3-geo.min.js');}
  const d3=window.d3,response=await fetch('/engine/vendor/geo/land.geojson');
  if(!response.ok)throw Error('Missing land data; run python engine/get_geo_assets.py');
  const land=await response.json();
  // D3 spherical rings use the opposite exterior orientation to RFC7946.
  // Normalize per polygon, including all its holes; do not paint the complement.
  function orient(g){
    if(g.type==='Polygon'&&d3.geoArea(g)>2*Math.PI)g.coordinates=g.coordinates.map(r=>r.slice().reverse());
    if(g.type==='MultiPolygon')g.coordinates=g.coordinates.map(c=>{const p={type:'Polygon',coordinates:c};orient(p);return p.coordinates;});
  }
  for(const f of land.features)orient(f.geometry);
  return {d3,land,graticule:d3.geoGraticule10()};
}
export function cylindrical(morph=0) {
  if(!window.d3?.geoProjection)throw Error('loadAtlas() first');
  if(!(morph>=0&&morph<=1))throw Error('morph in [0,1] required');
  return d3.geoProjection((lambda,phi)=>{phi=Math.max(-Math.PI/2+1e-5,Math.min(Math.PI/2-1e-5,phi));return[lambda,(1-morph)*Math.log(Math.tan(Math.PI/4+phi/2))+morph*Math.sin(phi)];}).precision(.25);
}
export function paintMap(c,atlas,projection,{ocean='#cfddd8',land='#37665e',coast='#214b46',grid='#88a39b',width=1.1}={}) {
  const path=atlas.d3.geoPath(projection,c);c.beginPath();path({type:'Sphere'});c.fillStyle=ocean;c.fill();
  c.beginPath();path(atlas.land);c.fillStyle=land;c.fill();c.strokeStyle=coast;c.lineWidth=width;c.stroke();
  c.beginPath();path(atlas.graticule);c.strokeStyle=grid;c.lineWidth=.8;c.stroke();return path;
}

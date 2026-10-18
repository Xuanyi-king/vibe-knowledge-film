/* Six-second linkage study. Pose is illustrative kinematics, not a force solver. */
(async()=>{
  const {THREE:T,studio,solid,rod,lathe}=await import('/engine/vk-scene.mjs');
  const S=studio({position:[4.5,3.2,6],target:[.55,1.35,0],fov:35});
  S.scene.background=new T.Color('#d5dedb');S.scene.fog=new T.Fog('#d5dedb',10,28);
  const metal=new T.MeshStandardMaterial({color:'#9cabb0',metalness:.88,roughness:.26});
  const red=new T.MeshStandardMaterial({color:'#aa382b',metalness:.68,roughness:.24});
  const ink=new T.MeshStandardMaterial({color:'#263844',metalness:.55,roughness:.34});
  const ceramic=new T.MeshStandardMaterial({color:'#e3e8df',metalness:.05,roughness:.36});
  const floor=solid(new T.PlaneGeometry(200,200),new T.MeshStandardMaterial({color:'#b8c8c7',roughness:.9}));
  floor.rotation.x=-Math.PI/2;floor.position.y=-.02;floor.castShadow=false;S.scene.add(floor);
  const base=lathe([[0,0],[.94,0],[1.03,.06],[1.03,.13],[.96,.2],[.42,.2],[.38,.28],[0,.28]],ink);S.scene.add(base);
  const shaft=solid(new T.CylinderGeometry(.065,.065,2.65,32),metal);shaft.position.y=1.55;S.scene.add(shaft);
  for(let i=0;i<6;i++){const q=i*Math.PI/3,b=solid(new T.CylinderGeometry(.075,.075,.065,6),metal);b.position.set(.8*Math.cos(q),.235,.8*Math.sin(q));S.scene.add(b);}
  for(const y of [.08,.18]){const ring=solid(new T.TorusGeometry(.99,.018,8,80),metal);ring.rotation.x=Math.PI/2;ring.position.y=y;S.scene.add(ring);}
  const rotor=new T.Group();S.scene.add(rotor);
  const pivot=solid(new T.CylinderGeometry(.13,.13,.15,32),metal);pivot.position.y=2.65;rotor.add(pivot);
  const collar=new T.Group();rotor.add(collar);
  const sleeve=solid(new T.CylinderGeometry(.17,.17,.3,32),ceramic);collar.add(sleeve);
  for(const y of [-.15,.15]){const ring=solid(new T.TorusGeometry(.16,.025,10,48),red);ring.rotation.x=Math.PI/2;ring.position.y=y;collar.add(ring);}
  const balls=[],links=[],joints=[];
  for(const sign of [-1,1]){
    const ball=solid(new T.SphereGeometry(.21,40,24),red);rotor.add(ball);balls.push(ball);
    const upper=rod(metal,.032),lower=rod(metal,.025);rotor.add(upper,lower);links.push([upper,lower]);
    const joint=solid(new T.SphereGeometry(.07,16,12),ceramic);rotor.add(joint);joints.push(joint);
  }
  let error=0;
  function pose(t){
    const u=Math.max(0,Math.min(1,t/6)),k=u*u*(3-2*u),theta=.23+.72*k;
    const r=.9*Math.sin(theta),y=2.65-.9*Math.cos(theta),cy=2.65-1.8*Math.cos(theta);
    rotor.rotation.y=2*t+5*6*(u*u*u-.5*u*u*u*u);collar.position.y=cy;error=0;
    for(let i=0;i<2;i++){
      const p=[(i?1:-1)*r,y,0];balls[i].position.fromArray(p);joints[i].position.fromArray(p);
      links[i][0].between([0,2.65,0],p);links[i][1].between(p,[0,cy,0]);
      for(const link of links[i])error=Math.max(error,Math.abs(link.scale.y-.9));
    }
    const az=.55+.3*k;S.camera.position.set(7.5*Math.sin(az),3.2,7.5*Math.cos(az));S.camera.lookAt(.55,1.35,0);
    return (Math.cos(.23)-Math.cos(theta))/(Math.cos(.23)-Math.cos(.95));
  }
  let flat=false;const originals=new Map();
  window.SHOT={
    flat(value){if(value===flat)return;flat=value;S.scene.traverse(n=>{if(n.isMesh){if(!originals.has(n))originals.set(n,n.material);if(!value)n.material.dispose();n.material=value?new T.MeshBasicMaterial({color:originals.get(n).color}):originals.get(n);}});},
    inspect(){let meshes=0;S.scene.traverse(n=>{if(n.isMesh)meshes++;});return{shadow:S.renderer.shadowMap.enabled,meshes,maxLinkError:error,glError:S.renderer.getContext().getError(),backend:window.VK_SCENE_INFO};},
  };
  function text(c,str,x,y,size=28,color='#233b42',font='VK Sans'){c.font=`500 ${size}px "${font}"`;c.fillStyle=color;c.textAlign='left';c.textBaseline='middle';c.fillText(str,x,y);}
  VK.film({dur:6,theme:'flat',bloom:0,grain:0,meta:{title:'转速如何变成位移',drone:.15},draw(fr,t){
    const k=pose(t);
    fr.look.under=c=>{
      c.fillStyle='#b8c8c7';c.fillRect(0,0,1920,1080);S.render(c);
      text(c,'转速如何变成位移？',96,100,66);text(c,'CENTRIFUGAL GOVERNOR',100,163,23,'#537078','VK Mono');
      text(c,'飞球张开',1390,390,43);text(c,'套筒上移',1390,458,43);
      text(c,'行程示意',1390,580,26,'#537078');text(c,Math.round(k*100)+'%',1390,635,62,'#a4392d','VK Mono');
      c.fillStyle='#f0f3ed';c.fillRect(0,945,1920,135);
      text(c,'旋转 → 径向展开 → 轴向位移',470,990,40);text(c,'机构运动示意 · 未模拟惯性、重力平衡或负载',540,1044,24,'#537078');
    };
    fr.sfx(.3,'soft',{gain:.3});fr.sfx(5.7,'tock',{gain:.25});
  }});
})().catch(e=>{window.READY_ERROR=String(e)+'; optional setup: python engine/get_scene_assets.py';});

(async()=>{
  const [{THREE:T,studio,solid,rod,lathe,surface},M,{SCORE}]=await Promise.all([import('/engine/vk-scene.mjs'),import('/engine/vk-motion.mjs'),import('./score.mjs')]);
  window.VK_SCORE=SCORE;
  const hit=SCORE.event('strike'),damp=SCORE.event('damp'),macro=SCORE.event('macro');
  const S=studio({position:[3.2,2.9,6.4],target:[.15,1.6,0],fov:35});
  S.scene.background=new T.Color('#d9d4c8');S.scene.fog=new T.Fog('#d9d4c8',11,25);
  const bronze=surface({color:'#c59b62',metalness:.86,roughness:.3,grain:.18,bump:.006,seed:21});
  const black=new T.MeshStandardMaterial({color:'#26322e',metalness:.5,roughness:.4});
  const felt=surface({color:'#405a49',metalness:0,roughness:1,grain:.5,bump:.018,seed:8});
  const wood=new T.MeshStandardMaterial({color:'#865c39',roughness:.65});
  const linen=new T.MeshStandardMaterial({color:'#e4d8b9',roughness:1});
  const floor=solid(new T.PlaneGeometry(200,200),new T.MeshStandardMaterial({color:'#bab5a7',roughness:.9}));floor.rotation.x=-Math.PI/2;floor.position.y=-.05;floor.castShadow=false;S.scene.add(floor);
  const base=solid(new T.BoxGeometry(3.2,.1,1.25),black);S.scene.add(base);
  const beam=rod(black,.035).between([-1.45,3.05,0],[1.45,3.05,0]);S.scene.add(beam);
  for(const x of [-1.45,1.45])S.scene.add(rod(black,.035).between([x,.05,0],[x,3.05,0]));
  const disc=new T.Group();disc.position.y=1.62;S.scene.add(disc);
  const profile=[[0,.12],[.12,.12],[.2,.055],[.35,.025],[.55,.01],[.78,0],[.9,-.018],[.92,-.06],[.92,-.10],[.88,-.04],[.55,-.03],[.19,.015],[.1,.07],[0,.07]];
  const plate=lathe(profile,bronze,128);plate.rotation.x=Math.PI/2;disc.add(plate);
  for(const [radius,z] of [[.32,.031],[.48,.017],[.65,.006],[.82,-.006],[.90,-.018]]){
    const ring=solid(new T.TorusGeometry(radius,.003,6,128),bronze);ring.position.z=z+.003;disc.add(ring);
  }
  const threads=[rod(linen,.006),rod(linen,.006)];S.scene.add(...threads);
  const hammer=new T.Group();S.scene.add(hammer);
  const head=solid(new T.SphereGeometry(.17,36,20),wood);hammer.add(head);
  const handle=rod(wood,.024).between([0,-.05,.08],[0,-.34,1.05]);hammer.add(handle);
  const pad=solid(new T.BoxGeometry(.25,.48,.24),felt);S.scene.add(pad);
  const padHandle=rod(black,.025);S.scene.add(padHandle);
  const keys=[
    [0,{position:[3.2,2.9,6.4],target:[.2,1.65,0],fov:35}],
    [macro.start,{position:[3.2,2.9,6.4],target:[.2,1.65,0],fov:35}],
    [macro.end,{position:[2,2.6,4.9],target:[.15,1.65,0],fov:35}],
    [8,{position:[2,2.6,4.9],target:[.15,1.65,0],fov:35}]
  ];
  function envelope(t){const dt=Math.max(0,t-hit.start);return t<hit.start?0:Math.exp(-dt*.42)*Math.exp(-Math.max(0,t-damp.start)*18);}
  function pose(t){
    const env=envelope(t);
    // Visible low-frequency envelope is an explanatory magnification, not the 220Hz acoustic mode.
    const vibration=M.impulse(t-hit.start,{velocity:1.0,frequency:4.2,damping:.025})*Math.exp(-Math.max(0,t-damp.start)*18);
    disc.rotation.x=vibration*.7;disc.rotation.y=vibration*.28;
    const z=M.contact(t,{time:hit.start,...hit.motion}).position;
    hammer.position.set(-.45,1.62,z);hammer.rotation.x=M.impulse(t-hit.start,{velocity:-2,frequency:2.7,damping:.6});
    const px=M.track([[0,2],[damp.start-.55,2],[damp.start,1.035],[8,1.035]],t);
    pad.position.set(px,1.7,.01);pad.scale.x=1-.07*M.spring(t-damp.start,{from:0,to:1,frequency:5,damping:.65});
    padHandle.between([px+.1,1.7,.13],[px+.65,1.7,.85]);
    disc.updateMatrixWorld(true);for(let i=0;i<2;i++){const p=disc.localToWorld(new T.Vector3((i?1:-1)*.5,.77,0));threads[i].between([(i?1:-1)*.5,3.05,0],p.toArray());}
    M.camera(S.camera,keys,t);return env;
  }
  function label(c,s,x,y,size,color='#26322e',font='VK Sans'){
    c.fillStyle=color;c.textAlign='left';c.textBaseline='middle';c.font=`500 ${size}px "${font}"`;c.fillText(s,x,y);
  }
  window.SHOT={inspect(t){pose(t);return{hit:hit.start,damp:damp.start,hammerZ:hammer.position.z,damperX:pad.position.x,glError:S.renderer.getContext().getError()};}};
  VK.film({dur:8,theme:'flat',bloom:0,grain:0,meta:{title:'一击之后',drone:0},draw(fr,t){
    const env=pose(t);
    fr.look.under=c=>{
      S.render(c);
      label(c,'一击之后',96,105,52);label(c,'AFTER THE IMPACT',100,165,19,'#666d60','VK Mono');
      const state=t<hit.start?'01  接触':t<damp.start?'02  余振':'03  阻尼';label(c,state,1440,115,28,'#526452');
      // Abstract evidence grows out of the same oscillation envelope; no scene reset.
      const show=M.smooth((t-2.6)/.65);c.globalAlpha=show;
      label(c,'振动包络',1530,245,25,'#526452');c.strokeStyle='#a4652f';c.lineWidth=3;c.beginPath();
      for(let i=0;i<=280;i++){const x=1510+i,amp=env*43*Math.sin(i*.13+t*10),y=330+amp;i?c.lineTo(x,y):c.moveTo(x,y);}c.stroke();
      label(c,t<damp.start?'能量逐渐耗散':'接触吸收能量',1530,410,26,'#526452');c.globalAlpha=1;
      c.fillStyle='#e7e1d5';c.fillRect(0,925,1920,155);
      label(c,t<2.5?'撞击结束，声音为什么还在？':t<damp.start?'持续振动，让空气继续传递声音。':'阻尼带走能量，余振随之消失。',270,979,42);
      label(c,'振幅与频率为慢速放大示意 · 合成音色，不是实测声学模型',420,1040,23,'#697262');
    };
  }});
})().catch(e=>{window.READY_ERROR=String(e);});

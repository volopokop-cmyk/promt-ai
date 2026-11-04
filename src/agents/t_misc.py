T_3D_OBJECT = '''<div id="obj3d" style="width:360px;height:360px;margin:0 auto"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const shape="{shape}";
  const el=document.getElementById("obj3d");
  const scene=new THREE.Scene();
  const cam=new THREE.PerspectiveCamera(40,1,0.1,100);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(360,360);
  el.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xffffff,0x333355,1.0));
  const d=new THREE.DirectionalLight(0xffffff,1.2);
  d.position.set(2,4,3); scene.add(d);
  const mat=new THREE.MeshStandardMaterial({color:"{c1}",roughness:0.4,metalness:0.2});
  let geo;
  if(shape==="sphere") geo=new THREE.SphereGeometry(1.1,24,24);
  else if(shape==="torus") geo=new THREE.TorusGeometry(0.9,0.35,16,32);
  else geo=new THREE.BoxGeometry(1.4,1.4,1.4);
  const mesh=new THREE.Mesh(geo,mat);
  scene.add(mesh);
  cam.position.set(0,0.8,3.5);
  cam.lookAt(0,0,0);
  const clock=new THREE.Clock();
  function a(){
    requestAnimationFrame(a);
    const t=clock.getElapsedTime();
    mesh.rotation.x=t*0.4;
    mesh.rotation.y=t*0.7;
    renderer.render(scene,cam);
  }
  a();
})();
</script>'''

T_3D_WORLD = '''<div id="world3d" style="width:420px;height:480px;margin:0 auto"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const el=document.getElementById("world3d");
  const scene=new THREE.Scene();
  scene.background=new THREE.Color("{c0}");
  const cam=new THREE.PerspectiveCamera(50,420/480,0.1,200);
  const renderer=new THREE.WebGLRenderer({antialias:true});
  renderer.setSize(420,480);
  el.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xffffff,0x223344,0.9));
  const sun=new THREE.DirectionalLight(0xfff0dd,1.2);
  sun.position.set(5,10,3); scene.add(sun);
  // земля
  const ground=new THREE.Mesh(
    new THREE.PlaneGeometry(40,40),
    new THREE.MeshStandardMaterial({color:"{c3}",roughness:0.9})
  );
  ground.rotation.x=-Math.PI/2;
  scene.add(ground);
  // холмы / здания-примитивы
  const mat=new THREE.MeshStandardMaterial({color:"{c1}",roughness:0.7});
  for(let i=0;i<8;i++){
    const h=0.8+Math.random()*2.5;
    const b=new THREE.Mesh(new THREE.BoxGeometry(0.8+Math.random(),h,0.8+Math.random()),mat);
    b.position.set((Math.random()-0.5)*12,h/2,(Math.random()-0.5)*10-4);
    scene.add(b);
  }
  // небо-сфера акцент
  const orb=new THREE.Mesh(
    new THREE.SphereGeometry(0.6,16,16),
    new THREE.MeshStandardMaterial({color:"{c2}",emissive:"{c1}",emissiveIntensity:0.3})
  );
  orb.position.set(3,4,-6);
  scene.add(orb);
  cam.position.set(0,2.2,8);
  cam.lookAt(0,1,0);
  const clock=new THREE.Clock();
  function a(){
    requestAnimationFrame(a);
    const t=clock.getElapsedTime();
    cam.position.x=Math.sin(t*0.25)*1.5;
    cam.lookAt(0,1,0);
    orb.position.y=4+Math.sin(t)*0.3;
    renderer.render(scene,cam);
  }
  a();
})();
</script>'''

T_2D_SCENE = '''<div style="width:360px;height:420px;margin:0 auto;border-radius:28px;background:linear-gradient(180deg,{c0},{c3} 60%,{c1})"></div>'''
T_2D_CARD = '''<div style="width:300px;height:400px;margin:0 auto;border-radius:28px;background:linear-gradient(160deg,{c1},{c3});display:flex;align-items:center;justify-content:center;color:#fff;font-size:22px;font-weight:700">{text}</div>'''
T_ABSTRACT = '''<div id="abs3d" style="width:360px;height:360px;margin:0 auto"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const el=document.getElementById("abs3d");
  const scene=new THREE.Scene();
  const cam=new THREE.PerspectiveCamera(40,1,0.1,100);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(360,360);
  el.appendChild(renderer.domElement);
  scene.add(new THREE.AmbientLight(0xffffff,0.5));
  const d=new THREE.DirectionalLight(0xffffff,1); d.position.set(2,3,2); scene.add(d);
  const mats=[
    new THREE.MeshStandardMaterial({color:"{c1}",roughness:0.3,metalness:0.4}),
    new THREE.MeshStandardMaterial({color:"{c2}",roughness:0.3,metalness:0.4}),
  ];
  const g=new THREE.Group(); scene.add(g);
  for(let i=0;i<5;i++){
    const m=new THREE.Mesh(new THREE.IcosahedronGeometry(0.4+i*0.15,0),mats[i%2]);
    m.position.set(Math.sin(i)*1.2,Math.cos(i*1.3)*0.8,Math.cos(i)*0.5);
    g.add(m);
  }
  cam.position.set(0,0,5);
  const clock=new THREE.Clock();
  function a(){
    requestAnimationFrame(a);
    const t=clock.getElapsedTime();
    g.rotation.y=t*0.5;
    g.rotation.x=t*0.2;
    renderer.render(scene,cam);
  }
  a();
})();
</script>'''
T_DEFAULT = '''<div style="width:160px;height:160px;margin:0 auto;border-radius:32px;background:linear-gradient(135deg,{c1},{c2})"></div>'''
BASE_HTML = '''<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;overflow:hidden;background:linear-gradient(135deg,{c0},{c3});height:100vh;display:flex;align-items:center;justify-content:center;font-family:system-ui,sans-serif}
.text{position:absolute;top:40px;width:90%;left:5%;text-align:center;font-size:36px;font-weight:800;color:{c2};text-shadow:0 4px 12px rgba(0,0,0,.45);z-index:10}
</style></head><body><div class="text">{text}</div><div class="scene">{object_html}</div></body></html>'''

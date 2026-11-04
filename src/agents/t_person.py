# 2D — CSS со светлой кожей
# 3D — Three.js r128 (Cylinder/Sphere)

_PERSON_CSS = '''
.p-skin{background:#e8b89a}
.p-shirt{background:#4a90d9}
.p-pants{background:#2a3a5c}
.p-eye{background:#1a1a1a}
.p-mouth{background:#2b1010}
'''

T_2D_PERSON = '''<div class="person-wrap" style="width:320px;height:480px;margin:0 auto;position:relative">
<style>''' + _PERSON_CSS + '''</style>
<div id="body" class="p-shirt" style="position:absolute;left:110px;top:200px;width:100px;height:140px;border-radius:40px"></div>
<div id="head" class="p-skin" style="position:absolute;left:120px;top:120px;width:80px;height:80px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:135px;top:145px;width:12px;height:12px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:175px;top:145px;width:12px;height:12px;border-radius:50%"></div>
<div id="mouth" class="p-mouth" style="position:absolute;left:145px;top:175px;width:30px;height:8px;border-radius:8px"></div>
<div id="legL" class="p-pants" style="position:absolute;left:100px;top:340px;width:30px;height:100px;border-radius:12px"></div>
<div id="legR" class="p-pants" style="position:absolute;left:190px;top:340px;width:30px;height:100px;border-radius:12px"></div>
<script>
(function(){
  const anim="{anim}";
  const lip={lip_curve};
  const t0=performance.now()/1000;
  const mouth=document.getElementById("mouth");
  const body=document.getElementById("body");
  const head=document.getElementById("head");
  const legL=document.getElementById("legL");
  const legR=document.getElementById("legR");
  function tick(){
    const el=(performance.now()/1000-t0);
    const fr=Math.min(lip.length-1,Math.max(0,Math.floor(el*15)));
    const v=lip.length?lip[fr]:0;
    if(mouth) mouth.style.height=(8+v*18)+"px";
    if(anim==="squat" && body){
      const s=(Math.sin(el*1.6)+1)/2;
      body.style.top=(200+s*45)+"px";
      if(head) head.style.top=(120+s*45)+"px";
      if(legL){legL.style.height=(100-s*30)+"px"; legL.style.top=(340+s*30)+"px";}
      if(legR){legR.style.height=(100-s*30)+"px"; legR.style.top=(340+s*30)+"px";}
    } else if(anim==="stand" && body){
      const s=Math.min(1, el/1.2);
      body.style.top=(245-s*45)+"px";
      if(head) head.style.top=(165-s*45)+"px";
    } else if(anim==="walk" && body){
      const s=Math.sin(el*3)*12;
      body.style.left=(110+s)+"px";
      if(head) head.style.left=(120+s)+"px";
      if(legL) legL.style.transform="rotate("+Math.sin(el*3)*15+"deg)";
      if(legR) legR.style.transform="rotate("+Math.sin(el*3+Math.PI)*15+"deg)";
    } else if(anim==="wave" && body){
      body.style.transform="rotate("+Math.sin(el*4)*8+"deg)";
    } else if(anim==="jump" && body){
      const s=Math.abs(Math.sin(el*2.5))*50;
      body.style.top=(200-s)+"px";
      if(head) head.style.top=(120-s)+"px";
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
</script></div>'''

T_3D_PERSON = '''<div id="c3d" style="width:400px;height:520px;margin:0 auto"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const anim="{anim}";
  const lip={lip_curve};
  const el=document.getElementById("c3d");
  const W=400,H=520;
  const scene=new THREE.Scene();
  const cam=new THREE.PerspectiveCamera(40,W/H,0.1,100);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(W,H);
  renderer.setPixelRatio(1);
  el.appendChild(renderer.domElement);

  scene.add(new THREE.HemisphereLight(0xffffff,0x444466,1.0));
  const dir=new THREE.DirectionalLight(0xffffff,1.1);
  dir.position.set(3,6,4);
  scene.add(dir);

  const skin=new THREE.MeshStandardMaterial({color:0xe8b89a,roughness:0.7});
  const shirt=new THREE.MeshStandardMaterial({color:0x4a90d9,roughness:0.6});
  const pants=new THREE.MeshStandardMaterial({color:0x2a3a5c,roughness:0.7});
  const dark=new THREE.MeshStandardMaterial({color:0x1a1a1a});

  const root=new THREE.Group();
  scene.add(root);

  function mesh(geo,mat,x,y,z){
    const m=new THREE.Mesh(geo,mat);
    m.position.set(x,y,z);
    root.add(m);
    return m;
  }

  const body=mesh(new THREE.CylinderGeometry(0.38,0.42,0.95,12),shirt,0,0.95,0);
  const head=mesh(new THREE.SphereGeometry(0.32,16,16),skin,0,1.85,0);
  mesh(new THREE.SphereGeometry(0.05,8,8),dark,-0.1,1.9,0.28);
  mesh(new THREE.SphereGeometry(0.05,8,8),dark,0.1,1.9,0.28);
  const mouth=mesh(new THREE.BoxGeometry(0.14,0.04,0.06),dark,0,1.72,0.28);
  const armL=mesh(new THREE.CylinderGeometry(0.07,0.08,0.55,8),skin,-0.55,1.05,0);
  const armR=mesh(new THREE.CylinderGeometry(0.07,0.08,0.55,8),skin,0.55,1.05,0);
  const legL=mesh(new THREE.CylinderGeometry(0.1,0.12,0.7,8),pants,-0.18,0.2,0);
  const legR=mesh(new THREE.CylinderGeometry(0.1,0.12,0.7,8),pants,0.18,0.2,0);

  cam.position.set(0,1.2,4.2);
  cam.lookAt(0,1.0,0);

  const t0=performance.now()/1000;
  function tick(){
    const t=(performance.now()/1000-t0);
    const fr=Math.min(lip.length-1,Math.max(0,Math.floor(t*15)));
    const v=lip.length?lip[fr]:0;
    if(mouth) mouth.scale.y=1+v*4;

    if(anim==="squat"){
      const s=(Math.sin(t*1.6)+1)/2;
      body.position.y=0.95-s*0.35;
      head.position.y=1.85-s*0.35;
      legL.scale.y=1-s*0.35;
      legR.scale.y=1-s*0.35;
    } else if(anim==="stand"){
      const s=Math.min(1,t/1.2);
      body.position.y=0.6+s*0.35;
      head.position.y=1.5+s*0.35;
    } else if(anim==="walk"){
      root.position.x=Math.sin(t*2.5)*0.15;
      legL.rotation.x=Math.sin(t*3)*0.4;
      legR.rotation.x=Math.sin(t*3+Math.PI)*0.4;
      armL.rotation.x=Math.sin(t*3+Math.PI)*0.35;
      armR.rotation.x=Math.sin(t*3)*0.35;
    } else if(anim==="wave"){
      armR.rotation.z=-0.8+Math.sin(t*5)*0.5;
      armR.rotation.x=0.3;
    } else if(anim==="jump"){
      root.position.y=Math.abs(Math.sin(t*2.5))*0.5;
    } else {
      root.rotation.y=Math.sin(t*0.8)*0.15;
    }

    renderer.render(scene,cam);
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
</script>'''

T_2_PEOPLE = '''<div class="two-people" style="width:420px;height:480px;margin:0 auto;position:relative">
<style>
.p-skin{background:#e8b89a}
.p-shirt-a{background:#4a90d9}
.p-shirt-b{background:#e94560}
.p-pants{background:#2a3a5c}
.p-eye{background:#1a1a1a}
.p-mouth{background:#2b1010}
</style>
<div id="bodyA" class="p-shirt-a" style="position:absolute;left:40px;top:200px;width:90px;height:130px;border-radius:36px"></div>
<div id="headA" class="p-skin" style="position:absolute;left:50px;top:125px;width:70px;height:70px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:62px;top:148px;width:10px;height:10px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:95px;top:148px;width:10px;height:10px;border-radius:50%"></div>
<div class="p-mouth" style="position:absolute;left:72px;top:172px;width:24px;height:7px;border-radius:6px"></div>
<div class="p-pants" style="position:absolute;left:48px;top:330px;width:26px;height:90px;border-radius:10px"></div>
<div class="p-pants" style="position:absolute;left:96px;top:330px;width:26px;height:90px;border-radius:10px"></div>
<div id="bodyB" class="p-shirt-b" style="position:absolute;left:250px;top:200px;width:90px;height:130px;border-radius:36px"></div>
<div id="headB" class="p-skin" style="position:absolute;left:260px;top:125px;width:70px;height:70px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:272px;top:148px;width:10px;height:10px;border-radius:50%"></div>
<div class="p-eye" style="position:absolute;left:305px;top:148px;width:10px;height:10px;border-radius:50%"></div>
<div class="p-mouth" style="position:absolute;left:282px;top:172px;width:24px;height:7px;border-radius:6px"></div>
<div class="p-pants" style="position:absolute;left:258px;top:330px;width:26px;height:90px;border-radius:10px"></div>
<div class="p-pants" style="position:absolute;left:306px;top:330px;width:26px;height:90px;border-radius:10px"></div>
<script>
(function(){
  const anim="{anim}";
  const t0=performance.now()/1000;
  const bodyA=document.getElementById("bodyA");
  const bodyB=document.getElementById("bodyB");
  const headA=document.getElementById("headA");
  const headB=document.getElementById("headB");
  function tick(){
    const el=(performance.now()/1000-t0);
    if(anim==="wave"){
      if(bodyA) bodyA.style.transform="rotate("+Math.sin(el*4)*10+"deg)";
      if(bodyB) bodyB.style.transform="rotate("+Math.sin(el*4+1)*10+"deg)";
    } else if(anim==="walk"){
      const s=Math.sin(el*2.5)*10;
      if(bodyA) bodyA.style.left=(40+s)+"px";
      if(headA) headA.style.left=(50+s)+"px";
      if(bodyB) bodyB.style.left=(250-s)+"px";
      if(headB) headB.style.left=(260-s)+"px";
    } else if(anim==="jump"){
      const s=Math.abs(Math.sin(el*2))*40;
      if(bodyA) bodyA.style.top=(200-s)+"px";
      if(headA) headA.style.top=(125-s)+"px";
      if(bodyB) bodyB.style.top=(200-s)+"px";
      if(headB) headB.style.top=(125-s)+"px";
    } else {
      if(bodyA) bodyA.style.transform="rotate("+Math.sin(el*1.2)*3+"deg)";
      if(bodyB) bodyB.style.transform="rotate("+Math.sin(el*1.2+2)*3+"deg)";
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
</script></div>'''

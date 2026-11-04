from qwen_llm import ask
import json
import re

# ========== ШАБЛОНЫ ==========

T_3D_PERSON = r'''
<div class="character" style="position:relative;width:420px;height:560px;margin:0 auto;">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const container=document.currentScript.parentElement;
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(42,420/560,0.1,100);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(420,560);renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));
  container.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xddeeff,0x443322,1.15));
  const key=new THREE.DirectionalLight(0xfff0dd,1.6);key.position.set(-2.5,5,4);scene.add(key);
  const skinMat=new THREE.MeshStandardMaterial({color:"{c1}",roughness:0.65});
  const shirtMat=new THREE.MeshStandardMaterial({color:"{c2}",roughness:0.75});
  const pantsMat=new THREE.MeshStandardMaterial({color:"#2a3a5c",roughness:0.8});
  const root=new THREE.Group();scene.add(root);
  const pelvis=new THREE.Group();pelvis.position.set(0,1.05,0);root.add(pelvis);
  const spine=new THREE.Group();spine.position.set(0,0.18,0);pelvis.add(spine);
  const chest=new THREE.Group();chest.position.set(0,0.28,0);spine.add(chest);
  const neck=new THREE.Group();neck.position.set(0,0.38,0);chest.add(neck);
  const head=new THREE.Group();head.position.set(0,0.22,0);neck.add(head);
  const armL=new THREE.Group();armL.position.set(-0.38,0.2,0);chest.add(armL);
  const armR=new THREE.Group();armR.position.set(0.38,0.2,0);chest.add(armR);
  const legL=new THREE.Group();legL.position.set(-0.15,-0.05,0);pelvis.add(legL);
  const legR=new THREE.Group();legR.position.set(0.15,-0.05,0);pelvis.add(legR);
  function mesh(p,g,m,y=0,x=0,z=0){const o=new THREE.Mesh(g,m);o.position.set(x,y,z);p.add(o);return o;}
  mesh(pelvis,new THREE.SphereGeometry(0.3,20,20),pantsMat,0,0,0).scale.set(1.15,0.75,0.95);
  mesh(spine,new THREE.CylinderGeometry(0.24,0.26,0.38,18),shirtMat,0.12);
  mesh(chest,new THREE.CylinderGeometry(0.27,0.25,0.4,18),shirtMat,0.12);
  mesh(neck,new THREE.CylinderGeometry(0.09,0.1,0.18,14),skinMat,0.06);
  mesh(head,new THREE.SphereGeometry(0.24,28,28),skinMat,0.2);
  mesh(armL,new THREE.CylinderGeometry(0.085,0.075,0.55,14),skinMat,-0.28);
  mesh(armR,new THREE.CylinderGeometry(0.085,0.075,0.55,14),skinMat,-0.28);
  mesh(legL,new THREE.CylinderGeometry(0.11,0.095,0.75,14),pantsMat,-0.38);
  mesh(legR,new THREE.CylinderGeometry(0.11,0.095,0.75,14),pantsMat,-0.38);
  camera.position.set(0,1.35,5);camera.lookAt(0,1.15,0);
  const anim="{anim}";const clock=new THREE.Clock();
  function animate(){requestAnimationFrame(animate);const t=clock.getElapsedTime();
    if(anim==="jump"){const c=(t*1.5)%(Math.PI*2);root.position.y=Math.max(0,Math.sin(c))*0.38;armL.rotation.z=0.25+Math.sin(c)*0.35;armR.rotation.z=-0.25-Math.sin(c)*0.35;}
    else if(anim==="wave"){armR.rotation.z=Math.sin(t*6)*0.45-1.35;}
    else if(anim==="walk"){legL.rotation.x=Math.sin(t*5)*0.38;legR.rotation.x=-Math.sin(t*5)*0.38;}
    else{chest.position.y=0.28+Math.sin(t*1.6)*0.012;}
    renderer.render(scene,camera);}
  animate();
})();
</script></div>
'''

T_3D_OBJECT = r'''
<div style="position:relative;width:420px;height:420px;margin:0 auto;">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const box=document.currentScript.parentElement;
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(45,1,0.1,100);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(420,420);box.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xffffff,0x222233,1.2));
  const d=new THREE.DirectionalLight(0xffffff,1.4);d.position.set(3,5,4);scene.add(d);
  const mat=new THREE.MeshStandardMaterial({color:"{c1}",metalness:0.35,roughness:0.35});
  const mat2=new THREE.MeshStandardMaterial({color:"{c2}",metalness:0.2,roughness:0.5});
  const group=new THREE.Group();scene.add(group);
  const shape="{shape}";
  let main;
  if(shape==="sphere") main=new THREE.Mesh(new THREE.SphereGeometry(1.1,32,32),mat);
  else if(shape==="torus") main=new THREE.Mesh(new THREE.TorusGeometry(0.9,0.35,16,48),mat);
  else if(shape==="cone") main=new THREE.Mesh(new THREE.ConeGeometry(1,1.8,24),mat);
  else if(shape==="cylinder") main=new THREE.Mesh(new THREE.CylinderGeometry(0.7,0.7,1.6,24),mat);
  else main=new THREE.Mesh(new THREE.BoxGeometry(1.4,1.4,1.4),mat);
  group.add(main);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(1.7,0.06,12,64),mat2);
  ring.rotation.x=Math.PI/2.5;group.add(ring);
  camera.position.set(0,1.2,4.2);camera.lookAt(0,0,0);
  const anim="{anim}";const clock=new THREE.Clock();
  function animate(){requestAnimationFrame(animate);const t=clock.getElapsedTime();
    if(anim==="spin"){group.rotation.y=t*0.9;group.rotation.x=Math.sin(t*0.5)*0.2;}
    else if(anim==="bounce"){group.position.y=Math.abs(Math.sin(t*2.2))*0.5;group.rotation.y=t*0.5;}
    else if(anim==="pulse"){const s=1+Math.sin(t*2)*0.12;group.scale.set(s,s,s);group.rotation.y=t*0.4;}
    else{group.rotation.y=t*0.55;group.position.y=Math.sin(t*1.2)*0.15;}
    ring.rotation.z=t*0.7;renderer.render(scene,camera);}
  animate();
})();
</script></div>
'''

T_3D_WORLD = r'''
<div style="position:relative;width:480px;height:480px;margin:0 auto;">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const box=document.currentScript.parentElement;
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(50,1,0.1,200);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(480,480);box.appendChild(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xaaccff,0x223311,1.0));
  const sun=new THREE.DirectionalLight(0xffeecc,1.5);sun.position.set(5,10,3);scene.add(sun);
  const ground=new THREE.Mesh(new THREE.CircleGeometry(8,48),new THREE.MeshStandardMaterial({color:"{c3}",roughness:0.9}));
  ground.rotation.x=-Math.PI/2;scene.add(ground);
  const accent=new THREE.MeshStandardMaterial({color:"{c1}",roughness:0.6});
  const mid=new THREE.MeshStandardMaterial({color:"{c2}",roughness:0.5});
  for(let i=0;i<12;i++){
    const h=0.6+Math.random()*1.8;
    const m=new THREE.Mesh(new THREE.BoxGeometry(0.5,h,0.5),i%2?accent:mid);
    const a=i/12*Math.PI*2;m.position.set(Math.cos(a)*3.2,h/2,Math.sin(a)*3.2);scene.add(m);
  }
  const ball=new THREE.Mesh(new THREE.SphereGeometry(0.45,20,20),new THREE.MeshStandardMaterial({color:"{c1}",metalness:0.4,roughness:0.3}));
  ball.position.set(0,0.45,0);scene.add(ball);
  camera.position.set(0,3.5,7);camera.lookAt(0,0.5,0);
  const clock=new THREE.Clock();
  function animate(){requestAnimationFrame(animate);const t=clock.getElapsedTime();
    camera.position.x=Math.sin(t*0.25)*7;camera.position.z=Math.cos(t*0.25)*7;camera.lookAt(0,0.5,0);
    ball.position.y=0.45+Math.abs(Math.sin(t*2))*0.6;renderer.render(scene,camera);}
  animate();
})();
</script></div>
'''

T_2D_SCENE = r'''
<div class="scene2d" style="position:relative;width:360px;height:420px;margin:0 auto;">
  <div style="
    width:100%;height:100%;border-radius:28px;overflow:hidden;position:relative;
    background: linear-gradient(180deg, {c0} 0%, {c3} 55%, {c1} 100%);
    box-shadow:0 20px 50px rgba(0,0,0,0.35);
  ">
    <div class="sun" style="position:absolute;top:36px;right:40px;width:70px;height:70px;border-radius:50%;
      background:radial-gradient(circle at 30% 30%, #fff7c8, {c2});box-shadow:0 0 40px {c2};animation:pulse 3s ease-in-out infinite;"></div>
    <div class="hill" style="position:absolute;bottom:0;left:-20%;width:70%;height:45%;border-radius:50% 50% 0 0;background:{c1};opacity:0.85;"></div>
    <div class="hill2" style="position:absolute;bottom:0;right:-15%;width:65%;height:38%;border-radius:50% 50% 0 0;background:{c2};opacity:0.7;"></div>
    <div class="orb" style="position:absolute;bottom:28%;left:50%;transform:translateX(-50%);
      width:90px;height:90px;border-radius:50%;background:linear-gradient(135deg,{c2},{c1});
      box-shadow:0 12px 30px rgba(0,0,0,0.35);animation:floaty 3.2s ease-in-out infinite;"></div>
    <div style="position:absolute;bottom:18px;width:100%;text-align:center;color:#fff;font-weight:700;font-size:18px;
      text-shadow:0 2px 8px rgba(0,0,0,0.5);padding:0 12px;">{text}</div>
  </div>
</div>
<style>
@keyframes floaty{0%,100%{transform:translate(-50%,0)}50%{transform:translate(-50%,-14px)}}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
</style>
'''

T_DEFAULT = r'''
<div style="width:180px;height:180px;border-radius:40px;background:linear-gradient(135deg,{c1},{c2});
box-shadow:0 15px 40px rgba(0,0,0,0.3);animation:pulse 2.5s ease-in-out infinite;"></div>
<style>@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}</style>
'''

TEMPLATES = {
    "3d_person": T_3D_PERSON,
    "3d_object": T_3D_OBJECT,
    "3d_world": T_3D_WORLD,
    "2d_scene": T_2D_SCENE,
    "default": T_DEFAULT,
}

BASE_HTML = """
<!doctype html>
<html><head><style>
body{margin:0;overflow:hidden;background:linear-gradient(135deg,{c0},{c3});height:100vh;
display:flex;align-items:center;justify-content:center;font-family:system-ui,-apple-system,sans-serif;}
.text{position:absolute;top:48px;width:90%;left:5%;text-align:center;font-size:42px;font-weight:800;
color:{c2};text-shadow:0 4px 16px rgba(0,0,0,0.45);z-index:10;line-height:1.2;}
</style></head>
<body>
  <div class="text">{text}</div>
  <div class="scene">{object_html}</div>
</body></html>
"""

PERSON_WORDS = ["человек", "челик", "персонаж", "парень", "девушка", "мужик", "женщина", "мужчина", "мальчик", "девочка", "герой"]
WORLD_WORDS = ["город", "мир", "планета", "космос", "лес", "море", "океан", "горы", "пейзаж", "улица", "здание"]

def _has_any(text: str, words: list) -> bool:
    t = (text or "").lower()
    return any(w in t for w in words)

def _pick_shape(idea: str) -> str:
    t = (idea or "").lower()
    if any(w in t for w in ["шар", "мяч"]): return "sphere"
    if any(w in t for w in ["кольц", "тор"]): return "torus"
    if any(w in t for w in ["конус", "ракет"]): return "cone"
    if any(w in t for w in ["цилиндр"]): return "cylinder"
    return "box"

def run(scene: dict, plan: dict, original_idea: str = "", lip_curve: list | None = None, use_llm: bool = True) -> str:
    c0 = plan["palette"][0] if len(plan.get("palette", [])) > 0 else "#1a1a2e"
    c1 = plan["palette"][1] if len(plan.get("palette", [])) > 1 else "#e94560"
    c2 = plan["palette"][2] if len(plan.get("palette", [])) > 2 else "#ffffff"
    c3 = plan["palette"][3] if len(plan.get("palette", [])) > 3 else "#16213e"

    idea = original_idea or ""
    scene_text = scene.get("text", "") or ""
    
    wants_person = _has_any(idea, PERSON_WORDS)
    wants_world = _has_any(idea, WORLD_WORDS)
    
    if wants_person:
        template_key = "3d_person"
    elif wants_world:
        template_key = "3d_world"
    else:
        template_key = "3d_object"
        
    object_html = TEMPLATES[template_key]

    anim = "idle"
    if "прыг" in idea: anim = "jump"
    elif "маш" in idea or "привет" in idea: anim = "wave"
    elif "ид" in idea or "ход" in idea: anim = "walk"
    elif template_key == "3d_object": anim = "spin"

    text_safe = re.sub(r"[<>]", "", scene_text)[:80]
    shape = _pick_shape(idea)

    html = BASE_HTML.replace("{text}", text_safe)
    html = html.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{c3}", c3)
    html = html.replace("{object_html}", object_html)
    html = html.replace("{anim}", anim)
    html = html.replace("{lip_curve}", "[0.0]")
    html = html.replace("{shape}", shape)
    
    return html

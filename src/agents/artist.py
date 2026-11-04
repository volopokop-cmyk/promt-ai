from qwen_llm import ask
import json
import re

# ========== ШАБЛОНЫ ==========

T_3D_PERSON = r'''
<div class="character" style="position:relative;width:420px;height:560px;margin:0 auto;">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
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

  // Загружаем GLB-модель
  const loader = new THREE.GLTFLoader();
  let mixer = null;
  let model = null;
  let actions = {};

  loader.load('man.glb', (gltf) => {
    model = gltf.scene;
    
    // Масштаб и позиция (если модель слишком большая/маленькая, меняй scale)
    model.scale.set(1, 1, 1); 
    model.position.set(0, 0, 0);
    
    scene.add(model);
    
    if (gltf.animations && gltf.animations.length > 0) {
      mixer = new THREE.AnimationMixer(model);
      for (const clip of gltf.animations) {
        actions[clip.name] = mixer.clipAction(clip);
      }
    }
  }, undefined, (error) => {
    console.error('Ошибка загрузки модели:', error);
  });

  camera.position.set(0,1.35,5);camera.lookAt(0,1.15,0);
  const anim="{anim}";
  const clock=new THREE.Clock();

  function animate(){
    requestAnimationFrame(animate);
    const t=clock.getElapsedTime();
    const delta = clock.getDelta();

    if (mixer) {
      mixer.update(delta);
      if (anim === "walk" && actions["Walk"]) actions["Walk"].play();
      else if (anim === "jump" && actions["Jump"]) actions["Jump"].play();
      else if (anim === "wave" && actions["Wave"]) actions["Wave"].play();
      else if (actions["Idle"]) actions["Idle"].play();
    } 
    else if (model) {
      // Если встроенных анимаций нет, делаем простые движения кодом
      if(anim==="jump"){
        model.position.y = Math.abs(Math.sin(t*1.5))*0.3;
      } else if(anim==="walk"){
        model.position.z = Math.sin(t*5)*0.1;
      } else if(anim==="wave"){
        model.rotation.z = Math.sin(t*4)*0.1;
      }
    }
    renderer.render(scene,camera);
  }
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

T_2D_PERSON = r'''
<div class="char2d" style="position:relative;width:280px;height:480px;margin:0 auto;">
<svg viewBox="0 0 280 480" width="280" height="480" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="140" cy="300" rx="70" ry="90" fill="{c2}"/>
  <rect x="125" y="190" width="30" height="40" rx="10" fill="{c1}"/>
  <circle cx="140" cy="140" r="62" fill="{c1}"/>
  <path d="M78 130 Q140 40 202 130 Q190 95 140 85 Q90 95 78 130" fill="#3b2a1f"/>
  <ellipse cx="118" cy="135" rx="12" ry="14" fill="#fff"/><ellipse cx="162" cy="135" rx="12" ry="14" fill="#fff"/>
  <circle cx="120" cy="137" r="6" fill="#1a1a1a"/><circle cx="164" cy="137" r="6" fill="#1a1a1a"/>
  <rect id="armR" x="212" y="230" width="28" height="110" rx="14" fill="{c1}" transform="rotate(-12 226 230)"/>
  <rect x="105" y="380" width="28" height="90" rx="12" fill="#2a3a5c"/>
  <rect x="147" y="380" width="28" height="90" rx="12" fill="#2a3a5c"/>
  <g id="mouth" transform="translate(140,175)">
    <ellipse id="mouthHole" cx="0" cy="0" rx="18" ry="3" fill="#2b1010"/>
    <path id="lowerLip" d="M-20 0 Q0 8 20 0" stroke="#c45c6a" stroke-width="5" fill="none" stroke-linecap="round"/>
  </g>
</svg>
<script>
(function(){const lipCurve={lip_curve};const fps=15;const anim="{anim}";
const hole=document.getElementById('mouthHole');const lower=document.getElementById('lowerLip');
const armR=document.getElementById('armR');const t0=performance.now()/1000;
function tick(){const el=performance.now()/1000-t0;const fr=Math.min(lipCurve.length-1,Math.max(0,Math.floor(el*fps)));
const v=lipCurve.length?lipCurve[fr]:0;hole.setAttribute('ry',String(3+v*14));lower.setAttribute('d',`M-20 0 Q0 ${8+v*16} 20 0`);
if(anim==='wave'&&armR)armR.setAttribute('transform',`rotate(${Math.sin(el*4.2)*18-12} 226 230)`);
requestAnimationFrame(tick);}requestAnimationFrame(tick);})();
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

T_2D_CARD = r'''
<div class="card" style="width:320px;height:420px;background:linear-gradient(160deg,{c1},{c3});border-radius:28px;
display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 20px 50px rgba(0,0,0,0.35);
animation:floaty 3.5s ease-in-out infinite;">
  <div style="width:110px;height:110px;border-radius:50%;background:{c2};margin-bottom:24px;box-shadow:0 8px 20px rgba(0,0,0,0.25);"></div>
  <div style="color:white;font-size:22px;font-weight:700;text-align:center;padding:0 20px;line-height:1.3;text-shadow:0 2px 8px rgba(0,0,0,0.4);">{text}</div>
</div>
<style>@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}</style>
'''

T_ABSTRACT = r'''
<div style="position:relative;width:380px;height:380px;margin:0 auto;">
  <div class="a1" style="position:absolute;inset:10%;border-radius:40%;background:linear-gradient(135deg,{c1},{c2});
    filter:blur(0.5px);animation:spin 8s linear infinite;opacity:0.9;"></div>
  <div class="a2" style="position:absolute;inset:22%;border-radius:30%;background:linear-gradient(225deg,{c2},{c3});
    animation:spin 12s linear infinite reverse;opacity:0.85;"></div>
  <div class="a3" style="position:absolute;inset:36%;border-radius:50%;background:{c0};border:3px solid {c2};
    box-shadow:0 0 40px {c1};animation:pulse 2.8s ease-in-out infinite;"></div>
</div>
<style>
@keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
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
    "2d_person": T_2D_PERSON,
    "2d_scene": T_2D_SCENE,
    "2d_card": T_2D_CARD,
    "abstract": T_ABSTRACT,
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

PERSON_WORDS = [
    "человек", "челик", "персонаж", "парень", "девушка", "мужик",
    "женщина", "мужчина", "мальчик", "девочка", "герой",
    "person", "man", "woman", "guy", "girl", "character", "boy", "girl"
]
WORLD_WORDS = [
    "город", "мир", "планета", "космос", "лес", "море", "океан", "горы",
    "пейзаж", "улица", "здание", "небо", "закат", "рассвет",
    "city", "world", "planet", "space", "forest", "sea", "ocean", "mountain", "landscape"
]
OBJECT_WORDS = [
    "шар", "куб", "мяч", "машина", "авто", "ракета", "робот", "коробка",
    "кольцо", "тор", "конус", "цилиндр", "предмет", "объект",
    "ball", "cube", "car", "rocket", "robot", "box", "ring", "object", "sphere"
]
ABSTRACT_WORDS = [
    "абстрак", "энерги", "маги", "неон", "портал", "вихрь",
    "abstract", "energy", "magic", "neon", "portal", "vortex"
]

def _has_any(text: str, words: list) -> bool:
    t = (text or "").lower()
    return any(w in t for w in words)

def _pick_shape(idea: str) -> str:
    t = (idea or "").lower()
    if any(w in t for w in ["шар", "мяч", "sphere", "ball"]): return "sphere"
    if any(w in t for w in ["кольц", "тор", "ring", "torus"]): return "torus"
    if any(w in t for w in ["конус", "cone", "ракет"]): return "cone"
    if any(w in t for w in ["цилиндр", "cylinder"]): return "cylinder"
    return "box"

SYSTEM_PROMPT = """Выбери визуальный шаблон для сцены.
Ключи:
- 3d_person / 2d_person — только если есть человек/персонаж
- 3d_object — предмет, шар, куб, робот, машина (3D)
- 3d_world — город, мир, пейзаж, космос (3D)
- 2d_scene — пейзаж/сцена в 2D
- 2d_card — карточка с текстом
- abstract — энергия, неон, абстракция
- default — простая фигура

Анимации: idle, spin, bounce, pulse, walk, wave, jump
Верни СТРОГО JSON: {"key":"3d_object","anim":"spin"}"""

def run(scene: dict, plan: dict, original_idea: str = "", lip_curve: list | None = None) -> str:
    c0 = plan["palette"][0] if len(plan.get("palette", [])) > 0 else "#1a1a2e"
    c1 = plan["palette"][1] if len(plan.get("palette", [])) > 1 else "#e94560"
    c2 = plan["palette"][2] if len(plan.get("palette", [])) > 2 else "#ffffff"
    c3 = plan["palette"][3] if len(plan.get("palette", [])) > 3 else "#16213e"

    style = plan.get("style", "3d")
    idea = original_idea or ""
    scene_text = scene.get("text", "") or ""
    blob = f"{idea} {scene_text}"

    wants_person = _has_any(idea, PERSON_WORDS)
    wants_world = _has_any(idea, WORLD_WORDS)
    wants_object = _has_any(idea, OBJECT_WORDS)
    wants_abstract = _has_any(idea, ABSTRACT_WORDS)

    if wants_person:
        template_key = "2d_person" if style == "2d" else "3d_person"
    else:
        if wants_world:
            template_key = "2d_scene" if style == "2d" else "3d_world"
        elif wants_object:
            template_key = "2d_card" if style == "2d" else "3d_object"
        elif wants_abstract:
            template_key = "abstract"
        else:
            template_key = "2d_scene" if style == "2d" else "3d_object"

    user = f"Стиль:{style}. Идея:{idea}. Сцена:{scene_text}"
    response = ask(SYSTEM_PROMPT, user, max_new_tokens=60).strip()

    anim = "idle"
    try:
        start = response.find("{")
        end = response.rfind("}")
        if start != -1 and end != -1:
            data = json.loads(response[start:end+1])
            anim = data.get("anim", "idle")
    except Exception:
        pass

    if template_key == "3d_object" and anim in ("walk", "wave", "jump"):
        anim = "spin"
    if template_key in ("3d_person", "2d_person") and anim in ("spin", "bounce", "pulse"):
        anim = "idle"

    shape = _pick_shape(idea)
    curve = lip_curve if lip_curve is not None else [0.0]
    lip_js = json.dumps(curve)

    object_html = TEMPLATES[template_key]
    text_safe = re.sub(r"[<>]", "", scene_text)[:80]

    html = BASE_HTML.replace("{text}", text_safe)
    html = html.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{c3}", c3)
    html = html.replace("{object_html}", object_html)
    html = html.replace("{anim}", anim)
    html = html.replace("{lip_curve}", lip_js)
    html = html.replace("{shape}", shape)
    html = html.replace("{text}", text_safe)
    return html

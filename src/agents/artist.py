from qwen_llm import ask

BASE_2D = """
<!doctype html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: linear-gradient(135deg, {c0}, {c0}); height: 100vh; display: flex; align-items: center; justify-content: center; font-family: system-ui, sans-serif; }
  .scene { position: relative; width: 100%; height: 100%; display: flex; align-items: flex-end; justify-content: center; padding-bottom: 50px; }
  .text { position: absolute; top: 15%; width: 100%; text-align: center; font-size: 64px; font-weight: bold; color: {c2}; text-shadow: 0 10px 30px rgba(0,0,0,0.5); z-index: 10; animation: fadeIn 1s ease-out forwards; opacity: 0; }
  .character { position: relative; animation: float 4s infinite alternate ease-in-out; }
  @keyframes fadeIn { to { opacity: 1; } }
  @keyframes float { 0% { transform: translateY(0px); } 100% { transform: translateY(-15px); } }
</style>
</head>
<body>
  <div class="scene">
    <div class="text">{text}</div>
    <div class="character">
      <svg width="400" height="500" viewBox="0 0 400 500" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="200" cy="100" r="60" fill="{c1}" />
        <rect x="180" y="150" width="40" height="30" fill="{c1}" />
        <path d="M 120 180 C 120 180, 100 350, 100 350 L 300 350 C 300 350, 280 180, 280 180 C 250 190, 150 190, 120 180 Z" fill="{c1}" />
        <path d="M 120 200 C 80 250, 50 320, 80 360" stroke="{c1}" stroke-width="35" stroke-linecap="round" />
        <path d="M 280 200 C 320 250, 350 320, 320 360" stroke="{c1}" stroke-width="35" stroke-linecap="round" />
        <rect x="50" y="380" width="300" height="20" rx="10" fill="{c1}" opacity="0.8"/>
        <rect x="290" y="330" width="30" height="50" rx="5" fill="{c2}" />
        <path d="M 320 340 C 340 340, 340 370, 320 370" stroke="{c2}" stroke-width="8" stroke-linecap="round" fill="none" />
        <path d="M 300 310 C 290 290, 310 280, 300 260" stroke="{c2}" stroke-width="4" stroke-linecap="round" fill="none" opacity="0.6">
          <animate attributeName="opacity" values="0.6; 0.1; 0.6" dur="2s" repeatCount="indefinite" />
        </path>
      </svg>
    </div>
  </div>
</body>
</html>
"""

BASE_3D = """
<!doctype html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: {c0}; }
  #text { position: absolute; top: 50px; width: 100%; text-align: center; font-size: 64px; font-weight: bold; color: {c2}; text-shadow: 0 4px 20px rgba(0,0,0,0.8); z-index: 10; animation: fadeIn 2s ease-out forwards; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
</style>
<script type="importmap">
  { "imports": { "three": "https://unpkg.com/three@0.160.0/build/three.module.js" } }
</script>
</head>
<body>
  <div id="text">{text}</div>
  <script type="module">
    import * as THREE from 'three';
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    const colorMat = new THREE.MeshStandardMaterial({ color: {c1}, roughness: 0.5 });
    const body = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 3, 32), colorMat); body.position.y = 0; scene.add(body);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.8, 32, 32), colorMat); head.position.y = 2.2; scene.add(head);
    const limbGeo = new THREE.CylinderGeometry(0.25, 0.25, 2, 16);
    const armL = new THREE.Mesh(limbGeo, colorMat); armL.position.set(-1.2, 0.5, 0); armL.rotation.z = 0.5; scene.add(armL);
    const armR = new THREE.Mesh(limbGeo, colorMat); armR.position.set(1.2, 0.5, 0); armR.rotation.z = -0.5; scene.add(armR);
    const legL = new THREE.Mesh(limbGeo, colorMat); legL.position.set(-0.5, -2.5, 0); scene.add(legL);
    const legR = new THREE.Mesh(limbGeo, colorMat); legR.position.set(0.5, -2.5, 0); scene.add(legR);
    const light = new THREE.DirectionalLight(0xffffff, 2); light.position.set(5, 5, 5); scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040, 2));
    camera.position.set(0, 0, 10);
    function animate() { requestAnimationFrame(animate); scene.rotation.y = Math.sin(Date.now() * 0.001) * 0.2; renderer.render(scene, camera); }
    animate();
  </script>
</body>
</html>
"""

SYSTEM_PROMPT = """Ты — умный ассистент-художник. Твоя задача — взять готовый HTML-шаблон и заменить в нём переменные на нужные цвета и текст.
Правила:
1. Замени {c0} на palette[0] (фон).
2. Замени {c1} на palette[1] (цвет человека/объектов).
3. Замени {c2} на palette[2] (цвет текста и деталей).
4. Замени {text} на текст из сцены (поле "text").
5. Верни ТОЛЬКО готовый HTML-код без markdown.

Вот шаблон:
{template}
"""

def run(scene: dict, plan: dict, original_idea: str = "") -> str:
    template = BASE_3D if plan.get("style") == "3d" else BASE_2D
    system = SYSTEM_PROMPT.replace("{template}", template)
    user = f"Запрос пользователя: {original_idea}\nСцена: {scene}\nПалитра: {plan['palette']}"
    
    html = ask(system, user, max_new_tokens=2048)
    
    if "```" in html:
        html = html.split("```")[1]
        if html.startswith("html"): html = html[4:]
    html = html.strip()
    
    if "<!doctype" not in html.lower() or len(html) < 100:
        c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
        c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#e94560"
        c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#ffffff"
        html = template.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{text}", scene.get("text", ""))
        
    return html

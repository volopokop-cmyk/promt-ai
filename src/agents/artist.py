from qwen_llm import ask

# Шаблон с человеком и столом
BASE_2D = """
<!doctype html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: {c0}; height: 100vh; display: flex; align-items: center; justify-content: center; }
  .text { position: absolute; bottom: 50px; color: {c2}; font-size: 48px; font-weight: bold; text-align: center; z-index: 10; width: 100%; text-shadow: 0 4px 10px rgba(0,0,0,0.5); }
  
  /* Человек */
  .head { position: absolute; top: 250px; left: 50%; transform: translateX(-50%); width: 80px; height: 80px; background: {c1}; border-radius: 50%; }
  .body { position: absolute; top: 330px; left: 50%; transform: translateX(-50%); width: 120px; height: 150px; background: {c1}; border-radius: 20px; }
  .arm-left { position: absolute; top: 340px; left: 40%; width: 20px; height: 100px; background: {c1}; border-radius: 10px; transform: rotate(20deg); }
  .arm-right { position: absolute; top: 340px; right: 40%; width: 20px; height: 100px; background: {c1}; border-radius: 10px; transform: rotate(-20deg); }
  
  /* Стол и кружка */
  .table { position: absolute; bottom: 100px; left: 50%; transform: translateX(-50%); width: 400px; height: 20px; background: {c1}; border-radius: 10px; }
  .cup { position: absolute; bottom: 120px; left: 60%; width: 40px; height: 50px; background: {c2}; border-radius: 5px; }
  .cup-handle { position: absolute; bottom: 140px; left: 63%; width: 20px; height: 20px; border: 4px solid {c2}; border-radius: 50%; }
</style>
</head>
<body>
  <div class="head"></div>
  <div class="body"></div>
  <div class="arm-left"></div>
  <div class="arm-right"></div>
  
  <div class="table"></div>
  <div class="cup"></div>
  <div class="cup-handle"></div>
  
  <div class="text">{text}</div>
</body>
</html>
"""

# Шаблон с 3D-сферой (если режиссёр выберет 3D)
BASE_3D = """
<!doctype html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: {c0}; }
  #text { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); color: {c2}; font-size: 48px; font-weight: bold; z-index: 10; text-align: center; width: 100%; }
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
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    
    // 3D Человек (состоит из сферы и цилиндра)
    const headGeo = new THREE.SphereGeometry(0.5, 32, 32);
    const headMat = new THREE.MeshStandardMaterial({ color: {c1} });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.y = 1;
    scene.add(head);

    const bodyGeo = new THREE.CylinderGeometry(0.5, 0.5, 1.5, 32);
    const bodyMat = new THREE.MeshStandardMaterial({ color: {c1} });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 0;
    scene.add(body);

    const light = new THREE.DirectionalLight(0xffffff, 2);
    light.position.set(5, 5, 5);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040, 2));

    camera.position.z = 4;

    function animate() { requestAnimationFrame(animate); head.rotation.y += 0.01; body.rotation.y += 0.01; renderer.render(scene, camera); }
    animate();
  </script>
</body>
</html>
"""

SYSTEM_PROMPT = """Ты — умный ассистент-художник. Твоя задача — взять готовый HTML-шаблон и заменить в нём переменные на нужные цвета и текст.
Правила:
1. Замени {c0} на palette[0] (фон).
2. Замени {c1} на palette[1] (цвет человека и стола).
3. Замени {c2} на palette[2] (цвет кружки и текста).
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
    
    # Если нейросеть сломала шаблон, мы подставляем его сами
    if "<!doctype" not in html.lower() or len(html) < 100:
        c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
        c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#e94560"
        c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#ffffff"
        html = template.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{text}", scene.get("text", ""))
        
    return html

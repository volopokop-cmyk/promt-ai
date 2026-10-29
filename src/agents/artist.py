from qwen_llm import ask

# ==========================================
# ИДЕАЛЬНЫЙ 2D ШАБЛОН (Красивый градиент + летающие шары)
# ==========================================
BASE_2D = """
<!doctype html>
<html>
<head>
<style>
  body { 
    margin: 0; overflow: hidden; background: linear-gradient(135deg, {c0}, {c1}); 
    font-family: system-ui, sans-serif; height: 100vh; display: flex; align-items: center; justify-content: center;
  }
  .text { 
    color: {c2}; font-size: 72px; font-weight: bold; text-align: center; 
    animation: fadeIn 1.5s ease-out forwards; opacity: 0; transform: translateY(30px);
    text-shadow: 0 10px 30px rgba(0,0,0,0.5); z-index: 10; max-width: 80%;
  }
  .circle {
    position: absolute; border-radius: 50%; background: {c1}; opacity: 0.3;
    filter: blur(40px); animation: float 6s infinite alternate ease-in-out;
  }
  .c1 { width: 300px; height: 300px; top: -50px; left: -50px; }
  .c2 { width: 400px; height: 400px; bottom: -100px; right: -100px; animation-delay: 2s; }
  @keyframes fadeIn { to { opacity: 1; transform: translateY(0); } }
  @keyframes float { 0% { transform: translate(0, 0); } 100% { transform: translate(30px, 50px); } }
</style>
</head>
<body>
  <div class="circle c1"></div>
  <div class="circle c2"></div>
  <div class="text">{text}</div>
</body>
</html>
"""

# ==========================================
# ИДЕАЛЬНЫЙ 3D ШАБЛОН (Вращающийся объект + Three.js)
# ==========================================
BASE_3D = """
<!doctype html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: {c0}; }
  #text {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    color: {c2}; font-family: system-ui, sans-serif; font-size: 72px; font-weight: bold;
    text-shadow: 0 4px 20px rgba(0,0,0,0.8); z-index: 10; text-align: center; width: 100%;
    animation: fadeIn 2s ease-out forwards;
  }
  @keyframes fadeIn { from { opacity: 0; transform: translate(-50%, -30%); } to { opacity: 1; transform: translate(-50%, -50%); } }
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

    const geometry = new THREE.IcosahedronGeometry(2, 0);
    const material = new THREE.MeshStandardMaterial({ color: {c1}, wireframe: true });
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    const light = new THREE.DirectionalLight(0xffffff, 2);
    light.position.set(5, 5, 5);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040, 2));

    camera.position.z = 5;

    function animate() {
      requestAnimationFrame(animate);
      mesh.rotation.x += 0.005;
      mesh.rotation.y += 0.01;
      renderer.render(scene, camera);
    }
    animate();
  </script>
</body>
</html>
"""

SYSTEM_PROMPT = """Ты — умный ассистент-художник. Твоя задача — взять готовый HTML-шаблон и заменить в нём переменные на нужные цвета и текст.

Правила:
1. Замени {c0} на palette[0].
2. Замени {c1} на palette[1].
3. Замени {c2} на palette[2].
4. Замени {text} на текст из сцены (поле "text").
5. Верни ТОЛЬКО готовый HTML-код без markdown и объяснений.

Вот шаблон, с которым ты работаешь:
{template}
"""

def run(scene: dict, plan: dict) -> str:
    # Выбираем шаблон в зависимости от стиля режиссёра
    template = BASE_3D if plan.get("style") == "3d" else BASE_2D
    
    # Формируем промт для нейросети
    system = SYSTEM_PROMPT.replace("{template}", template)
    user = f"Сцена: {scene}\nПалитра: {plan['palette']}"
    
    html = ask(system, user, max_new_tokens=2048)
    
    # Очищаем ответ от возможного markdown
    if "```" in html:
        html = html.split("```")[1]
        if html.startswith("html"):
            html = html[4:]
    html = html.strip()
    
    # ФОЛБЭК (Страховка): если нейросеть вернула мусор, мы сами подставляем цвета
    if "<!doctype" not in html.lower():
        # Берем цвета из палитры режиссёра, а если их нет — дефолтные
        c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
        c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#16213e"
        c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#ffffff"
        
        html = template.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{text}", scene.get("text", ""))
        
    return html

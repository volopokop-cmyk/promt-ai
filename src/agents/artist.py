from qwen_llm import ask

# --- БИБЛИОТЕКА 2D И 3D ШАБЛОНОВ ---
TEMPLATES = {
    "3d_person": """
    <div class="character" style="position:relative; width:400px; height:500px;">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
      <script>
      (function() {
        const container = document.currentScript.parentElement;
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, 400/500, 0.1, 80);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(400, 500);
        container.appendChild(renderer.domElement);

        scene.add(new THREE.HemisphereLight(0xc9e4ff, 0x3c2c2a, 1.2));
        const dirLight = new THREE.DirectionalLight(0xffe8d3, 2.0);
        dirLight.position.set(-3, 6, 5);
        scene.add(dirLight);
        const faceLight = new THREE.PointLight(0xfff0df, 0.6, 5);
        faceLight.position.set(0, 2.2, 1);
        scene.add(faceLight);

        const skinMat = new THREE.MeshStandardMaterial({ color: {c1}, roughness: 0.7 });
        const shirtMat = new THREE.MeshStandardMaterial({ color: {c2}, roughness: 0.8 });
        const pantsMat = new THREE.MeshStandardMaterial({ color: 0x293d63, roughness: 0.8 });
        const hairMat = new THREE.MeshStandardMaterial({ color: 0x33251f, roughness: 0.9 });

        const root = new THREE.Group();
        scene.add(root);

        const pelvis = new THREE.Group(); pelvis.position.set(0, 1.0, 0); root.add(pelvis);
        const spine = new THREE.Group(); spine.position.set(0, 0.15, 0); pelvis.add(spine);
        const chest = new THREE.Group(); chest.position.set(0, 0.25, 0); spine.add(chest);
        const neck = new THREE.Group(); neck.position.set(0, 0.35, 0); chest.add(neck);
        const head = new THREE.Group(); head.position.set(0, 0.25, 0); neck.add(head);

        const armL = new THREE.Group(); armL.position.set(-0.36, 0.22, 0); chest.add(armL);
        const elbowL = new THREE.Group(); elbowL.position.set(0, -0.35, 0); armL.add(elbowL);
        const armR = new THREE.Group(); armR.position.set(0.36, 0.22, 0); chest.add(armR);
        const elbowR = new THREE.Group(); elbowR.position.set(0, -0.35, 0); armR.add(elbowR);

        const legL = new THREE.Group(); legL.position.set(-0.16, -0.05, 0); pelvis.add(legL);
        const kneeL = new THREE.Group(); kneeL.position.set(0, -0.45, 0); legL.add(kneeL);
        const legR = new THREE.Group(); legR.position.set(0.16, -0.05, 0); pelvis.add(legR);
        const kneeR = new THREE.Group(); kneeR.position.set(0, -0.45, 0); legR.add(kneeR);

        function addMesh(parent, geo, mat, y = 0, x = 0, z = 0) {
          const mesh = new THREE.Mesh(geo, mat); mesh.position.set(x, y, z); parent.add(mesh); return mesh;
        }

        addMesh(pelvis, new THREE.SphereGeometry(0.28, 16, 16), pantsMat).scale.set(1.1, 0.7, 0.9);
        addMesh(spine, new THREE.CylinderGeometry(0.26, 0.24, 0.35, 16), shirtMat, 0.1);
        addMesh(chest, new THREE.CylinderGeometry(0.26, 0.26, 0.35, 16), shirtMat, 0.1);
        addMesh(neck, new THREE.CylinderGeometry(0.09, 0.09, 0.2, 16), skinMat, 0.05);
        addMesh(head, new THREE.SphereGeometry(0.22, 24, 24), skinMat, 0.22);
        
        // Глаза
        addMesh(head, new THREE.SphereGeometry(0.035, 12, 12), new THREE.MeshStandardMaterial({color: 0xffffff}), 0.24, -0.08, 0.19);
        addMesh(head, new THREE.SphereGeometry(0.035, 12, 12), new THREE.MeshStandardMaterial({color: 0xffffff}), 0.24, 0.08, 0.19);

        // Руки и ноги
        addMesh(armL, new THREE.CylinderGeometry(0.09, 0.08, 0.35, 16), skinMat, -0.15);
        addMesh(elbowL, new THREE.CylinderGeometry(0.08, 0.07, 0.35, 16), skinMat, -0.15);
        addMesh(armR, new THREE.CylinderGeometry(0.09, 0.08, 0.35, 16), skinMat, -0.15);
        addMesh(elbowR, new THREE.CylinderGeometry(0.08, 0.07, 0.35, 16), skinMat, -0.15);
        addMesh(legL, new THREE.CylinderGeometry(0.12, 0.1, 0.45, 16), pantsMat, -0.2);
        addMesh(kneeL, new THREE.CylinderGeometry(0.1, 0.08, 0.45, 16), pantsMat, -0.2);
        addMesh(legR, new THREE.CylinderGeometry(0.12, 0.1, 0.45, 16), pantsMat, -0.2);
        addMesh(kneeR, new THREE.CylinderGeometry(0.1, 0.08, 0.45, 16), pantsMat, -0.2);

        camera.position.set(0, 1.5, 4.5);
        camera.lookAt(0, 1.2, 0);

        // Нейросеть передает анимацию через эти переменные
        const anim = "{anim}";
        
        function animate() {
          requestAnimationFrame(animate);
          const time = Date.now() * 0.001;
          
          if (anim === "wave") {
            armR.rotation.z = -Math.sin(time * 5) * 0.8 - 1.5;
          } else if (anim === "walk") {
            legL.rotation.x = Math.sin(time * 5) * 0.5;
            legR.rotation.x = -Math.sin(time * 5) * 0.5;
            armL.rotation.x = -Math.sin(time * 5) * 0.5;
            armR.rotation.x = Math.sin(time * 5) * 0.5;
          } else {
             // Стоит и дышит
            chest.position.y = 0.25 + Math.sin(time * 2) * 0.01;
          }

          renderer.render(scene, camera);
        }
        animate();
      })();
      </script>
    </div>
    """,
    "person_walk": """
    <div class="character" style="position:relative; width:200px; height:300px;">
      <div class="head" style="position:absolute; top:0; left:50px; width:100px; height:100px; background:{c1}; border-radius:50%;"></div>
      <div class="body" style="position:absolute; top:100px; left:75px; width:50px; height:120px; background:{c1}; border-radius:20px;"></div>
      <div class="arm walk-arms" style="position:absolute; top:110px; left:40px; width:30px; height:100px; background:{c1}; border-radius:15px; transform-origin:top center;"></div>
      <div class="arm walk-arms" style="position:absolute; top:110px; left:130px; width:30px; height:100px; background:{c1}; border-radius:15px; transform-origin:top center;"></div>
      <div class="leg walk-legs" style="position:absolute; top:210px; left:60px; width:30px; height:90px; background:{c1}; border-radius:15px; transform-origin:top center;"></div>
      <div class="leg walk-legs" style="position:absolute; top:210px; left:110px; width:30px; height:90px; background:{c1}; border-radius:15px; transform-origin:top center;"></div>
    </div>
    """,
    "fat_cat": """
    <div class="character" style="position:relative; width:300px; height:300px; animation: breathe 3s infinite alternate ease-in-out;">
      <svg viewBox="0 0 600 600" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id="fluffy"><feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise" /><feDisplacementMap in="SourceGraphic" in2="noise" scale="5" xChannelSelector="R" yChannelSelector="G" /></filter>
          <radialGradient id="whiteFur" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ffffff" /><stop offset="100%" stop-color="#dcdcdc" /></radialGradient>
          <radialGradient id="orangeFur" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#f2b268" /><stop offset="100%" stop-color="#c97a2b" /></radialGradient>
          <radialGradient id="blackFur" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#3b3b3b" /><stop offset="100%" stop-color="#111111" /></radialGradient>
          <radialGradient id="eyeGradient" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#bbf7d0" /><stop offset="30%" stop-color="#4ade80" /><stop offset="80%" stop-color="#166534" /><stop offset="100%" stop-color="#064e3b" /></radialGradient>
        </defs>
        <ellipse cx="300" cy="550" rx="200" ry="30" fill="rgba(0,0,0,0.15)" />
        <g filter="url(#fluffy)">
          <path d="M 150 450 C 100 400, 100 250, 200 200 C 250 180, 350 180, 400 200 C 500 250, 500 400, 450 450 C 400 520, 200 520, 150 450 Z" fill="url(#whiteFur)" />
          <path d="M 350 200 C 420 220, 480 300, 460 400 C 440 480, 350 500, 300 480 C 350 400, 380 300, 350 200 Z" fill="url(#orangeFur)" />
          <ellipse cx="300" cy="250" rx="140" ry="120" fill="url(#whiteFur)" />
          <path d="M 300 130 C 200 130, 160 200, 160 250 C 160 320, 250 370, 300 370 Z" fill="url(#blackFur)" />
          <path d="M 180 170 L 150 60 L 250 130 Z" fill="url(#blackFur)" />
          <path d="M 420 170 L 450 60 L 350 130 Z" fill="url(#orangeFur)" />
          <ellipse cx="230" cy="240" rx="40" ry="45" fill="url(#eyeGradient)" />
          <ellipse cx="230" cy="240" rx="15" ry="35" fill="#000" />
          <ellipse cx="370" cy="240" rx="40" ry="45" fill="url(#eyeGradient)" />
          <ellipse cx="370" cy="240" rx="15" ry="35" fill="#000" />
        </g>
      </svg>
    </div>
    """,
    "default": """
    <div class="character" style="position:relative; width:100px; height:100px; background:{c1}; border-radius:20px; animation: float 2s infinite alternate;"></div>
    """
}

BASE_HTML = """
<!doctype html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: linear-gradient(135deg, {c0}, {c3}); height: 100vh; display: flex; align-items: center; justify-content: center; font-family: system-ui, sans-serif; }
  .text { position: absolute; top: 50px; width: 100%; text-align: center; font-size: 48px; font-weight: bold; color: {c2}; text-shadow: 0 4px 10px rgba(0,0,0,0.5); z-index: 10; }
  
  @keyframes walkLegs { 0%, 100% { transform: rotate(-20deg); } 50% { transform: rotate(20deg); } }
  @keyframes walkArms { 0%, 100% { transform: rotate(20deg); } 50% { transform: rotate(-20deg); } }
  @keyframes float { 0% { transform: translateY(0); } 100% { transform: translateY(-20px); } }
  @keyframes breathe { 0% { transform: scale(1); } 100% { transform: scale(1.03); } }

  .walk-legs { animation: walkLegs 0.6s infinite ease-in-out; }
  .walk-arms { animation: walkArms 0.6s infinite ease-in-out; }
</style>
</head>
<body>
  <div class="text">{text}</div>
  <div class="scene">{object_html}</div>
</body>
</html>
"""

SYSTEM_PROMPT = """Ты — умный ассистент-художник. Твоя задача — выбрать подходящий шаблон для сцены и заменить в нём переменные на цвета и текст.

Доступные шаблоны (ключи): 3d_person, person_walk, fat_cat, default.

Правила:
1. Выбери ОДИН ключ шаблона.
2. Если пользователь просит 3D, объемного человека, или "как в коде", выбирай 3d_person. Если он машет рукой, передай анимацию "wave", если идет - "walk", если стоит - "idle".
3. Замени {c0} на palette[0] (фон 1).
4. Замени {c1} на palette[1] (цвет тела/кожи).
5. Замени {c2} на palette[2] (цвет текста/одежды).
6. Замени {c3} на palette[3] (фон 2).
7. Замени {text} на текст из сцены.
8. Замени {anim} на нужную анимацию (wave, walk, idle).
9. Верни СТРОГО JSON:
{"key": "3d_person", "anim": "wave"}
Никаких объяснений!"""

import json
import re

def run(scene: dict, plan: dict, original_idea: str = "") -> str:
    c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
    c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#e94560"
    c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#ffffff"
    c3 = plan["palette"][3] if len(plan["palette"]) > 3 else "#16213e"
    
    user = f"Текст сцены: {scene.get('text', '')}. Запрос пользователя: {original_idea}"
    response = ask(SYSTEM_PROMPT, user, max_new_tokens=50).strip()
    
    template_key = "default"
    anim = "idle"
    
    # Пытаемся распарсить JSON от нейросети
    try:
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1:
            data = json.loads(response[start:end+1])
            template_key = data.get("key", "default")
            anim = data.get("anim", "idle")
    except:
        pass

    if template_key not in TEMPLATES:
        template_key = "default"
        
    object_html = TEMPLATES[template_key]
    
    # Подставляем цвета и анимацию
    html = BASE_HTML.replace("{text}", scene.get("text", ""))
    html = html.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{c3}", c3)
    html = html.replace("{object_html}", object_html)
    html = html.replace("{anim}", anim) # Передаем анимацию в JS
    
    return html

from qwen_llm import ask
import json
import re

TEMPLATES = {
    "3d_person": """
    <div class="character" style="position:relative; width:400px; height:500px; margin:0 auto;">
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

        const skinMat = new THREE.MeshStandardMaterial({ color: "{c1}", roughness: 0.7 });
        const shirtMat = new THREE.MeshStandardMaterial({ color: "{c2}", roughness: 0.8 });
        const pantsMat = new THREE.MeshStandardMaterial({ color: "#293d63", roughness: 0.8 });
        
        const root = new THREE.Group();
        scene.add(root);

        const pelvis = new THREE.Group(); pelvis.position.set(0, 1.0, 0); root.add(pelvis);
        const spine = new THREE.Group(); spine.position.set(0, 0.15, 0); pelvis.add(spine);
        const chest = new THREE.Group(); chest.position.set(0, 0.25, 0); spine.add(chest);
        const neck = new THREE.Group(); neck.position.set(0, 0.35, 0); chest.add(neck);
        const head = new THREE.Group(); head.position.set(0, 0.25, 0); neck.add(head);

        const armL = new THREE.Group(); armL.position.set(-0.36, 0.22, 0); chest.add(armL);
        const armR = new THREE.Group(); armR.position.set(0.36, 0.22, 0); chest.add(armR);

        const legL = new THREE.Group(); legL.position.set(-0.16, -0.05, 0); pelvis.add(legL);
        const legR = new THREE.Group(); legR.position.set(0.16, -0.05, 0); pelvis.add(legR);

        function addMesh(parent, geo, mat, y = 0, x = 0, z = 0) {
          const mesh = new THREE.Mesh(geo, mat); mesh.position.set(x, y, z); parent.add(mesh); return mesh;
        }

        addMesh(pelvis, new THREE.SphereGeometry(0.28, 16, 16), pantsMat).scale.set(1.1, 0.7, 0.9);
        addMesh(spine, new THREE.CylinderGeometry(0.26, 0.24, 0.35, 16), shirtMat, 0.1);
        addMesh(chest, new THREE.CylinderGeometry(0.26, 0.26, 0.35, 16), shirtMat, 0.1);
        addMesh(neck, new THREE.CylinderGeometry(0.09, 0.09, 0.2, 16), skinMat, 0.05);
        addMesh(head, new THREE.SphereGeometry(0.22, 24, 24), skinMat, 0.22);
        
        addMesh(head, new THREE.SphereGeometry(0.035, 12, 12), new THREE.MeshStandardMaterial({color: 0xffffff}), 0.24, -0.08, 0.19);
        addMesh(head, new THREE.SphereGeometry(0.035, 12, 12), new THREE.MeshStandardMaterial({color: 0xffffff}), 0.24, 0.08, 0.19);

        addMesh(armL, new THREE.CylinderGeometry(0.09, 0.08, 0.5, 16), skinMat, -0.25);
        addMesh(armR, new THREE.CylinderGeometry(0.09, 0.08, 0.5, 16), skinMat, -0.25);
        addMesh(legL, new THREE.CylinderGeometry(0.12, 0.1, 0.7, 16), pantsMat, -0.35);
        addMesh(legR, new THREE.CylinderGeometry(0.12, 0.1, 0.7, 16), pantsMat, -0.35);

        camera.position.set(0, 1.2, 4.5);
        camera.lookAt(0, 1.0, 0);

        const anim = "{anim}";
        let clock = new THREE.Clock();

        function animate() {
          requestAnimationFrame(animate);
          const time = clock.getElapsedTime();
          
          if (anim === "jump") {
            root.position.y = Math.abs(Math.sin(time * 3)) * 0.5; // Прыжок
            armL.rotation.z = Math.sin(time * 3) * 0.5;
            armR.rotation.z = -Math.sin(time * 3) * 0.5;
          } else if (anim === "wave") {
            armR.rotation.z = Math.sin(time * 6) * 0.5 - 1.5; // Машет
          } else if (anim === "walk") {
            legL.rotation.x = Math.sin(time * 5) * 0.4;
            legR.rotation.x = -Math.sin(time * 5) * 0.4;
          } else {
            chest.position.y = 0.25 + Math.sin(time * 2) * 0.01; // Дышит
          }

          renderer.render(scene, camera);
        }
        animate();
      })();
      </script>
    </div>
    """,
    "default": """
    <div class="character" style="width:100px; height:100px; background:{c1}; border-radius:20px;"></div>
    """
}

BASE_HTML = """
<!doctype html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: linear-gradient(135deg, {c0}, {c3}); height: 100vh; display: flex; align-items: center; justify-content: center; font-family: system-ui, sans-serif; }
  .text { position: absolute; top: 40px; width: 100%; text-align: center; font-size: 48px; font-weight: bold; color: {c2}; text-shadow: 0 4px 10px rgba(0,0,0,0.5); z-index: 10; }
</style>
</head>
<body>
  <div class="text">{text}</div>
  <div class="scene">{object_html}</div>
</body>
</html>
"""

SYSTEM_PROMPT = """Выбери шаблон и анимацию.
Ключи: 3d_person, default.
Анимации: jump (прыжок), wave (машет), walk (идет), idle (стоит).
Верни СТРОГО JSON: {"key": "3d_person", "anim": "jump"}"""

def run(scene: dict, plan: dict, original_idea: str = "") -> str:
    c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
    c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#e94560"
    c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#ffffff"
    c3 = plan["palette"][3] if len(plan["palette"]) > 3 else "#16213e"
    
    user = f"Текст: {scene.get('text', '')}. Запрос: {original_idea}"
    response = ask(SYSTEM_PROMPT, user, max_new_tokens=50).strip()
    
    template_key = "3d_person" # По умолчанию 3D
    anim = "idle"
    
    try:
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1:
            data = json.loads(response[start:end+1])
            template_key = data.get("key", "3d_person")
            anim = data.get("anim", "idle")
    except:
        pass

    if template_key not in TEMPLATES:
        template_key = "default"
        
    object_html = TEMPLATES[template_key]
    
    html = BASE_HTML.replace("{text}", scene.get("text", ""))
    html = html.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{c3}", c3)
    html = html.replace("{object_html}", object_html)
    html = html.replace("{anim}", anim)
    
    return html

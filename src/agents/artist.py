from qwen_llm import ask
import json

# Улучшенный 3D-персонаж с челюстью (простой липсинг) и спокойными анимациями
TEMPLATES = {
    "3d_person": """
    <div class="character" style="position:relative; width:420px; height:560px; margin:0 auto;">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
      <script>
      (function() {
        const container = document.currentScript.parentElement;
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(42, 420/560, 0.1, 100);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(420, 560);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        container.appendChild(renderer.domElement);

        // Мягкий свет
        scene.add(new THREE.HemisphereLight(0xddeeff, 0x443322, 1.15));
        const key = new THREE.DirectionalLight(0xfff0dd, 1.6);
        key.position.set(-2.5, 5, 4);
        scene.add(key);
        const fill = new THREE.DirectionalLight(0xaaccff, 0.45);
        fill.position.set(3, 2, -2);
        scene.add(fill);

        const skinMat = new THREE.MeshStandardMaterial({ color: "{c1}", roughness: 0.65, metalness: 0.05 });
        const shirtMat = new THREE.MeshStandardMaterial({ color: "{c2}", roughness: 0.75 });
        const pantsMat = new THREE.MeshStandardMaterial({ color: "#2a3a5c", roughness: 0.8 });
        const darkMat = new THREE.MeshStandardMaterial({ color: "#1a1a1a", roughness: 0.6 });

        const root = new THREE.Group();
        scene.add(root);

        // Иерархия тела
        const pelvis = new THREE.Group(); pelvis.position.set(0, 1.05, 0); root.add(pelvis);
        const spine = new THREE.Group(); spine.position.set(0, 0.18, 0); pelvis.add(spine);
        const chest = new THREE.Group(); chest.position.set(0, 0.28, 0); spine.add(chest);
        const neck = new THREE.Group(); neck.position.set(0, 0.38, 0); chest.add(neck);
        const head = new THREE.Group(); head.position.set(0, 0.22, 0); neck.add(head);

        const armL = new THREE.Group(); armL.position.set(-0.38, 0.2, 0); chest.add(armL);
        const armR = new THREE.Group(); armR.position.set(0.38, 0.2, 0); chest.add(armR);
        const legL = new THREE.Group(); legL.position.set(-0.15, -0.05, 0); pelvis.add(legL);
        const legR = new THREE.Group(); legR.position.set(0.15, -0.05, 0); pelvis.add(legR);

        function mesh(parent, geo, mat, y=0, x=0, z=0, sx=1, sy=1, sz=1) {
          const m = new THREE.Mesh(geo, mat);
          m.position.set(x, y, z);
          m.scale.set(sx, sy, sz);
          parent.add(m);
          return m;
        }

        // Тело
        mesh(pelvis, new THREE.SphereGeometry(0.3, 20, 20), pantsMat, 0, 0, 0, 1.15, 0.75, 0.95);
        mesh(spine, new THREE.CylinderGeometry(0.24, 0.26, 0.38, 18), shirtMat, 0.12);
        mesh(chest, new THREE.CylinderGeometry(0.27, 0.25, 0.4, 18), shirtMat, 0.12);
        mesh(neck, new THREE.CylinderGeometry(0.09, 0.1, 0.18, 14), skinMat, 0.06);

        // Голова
        mesh(head, new THREE.SphereGeometry(0.24, 28, 28), skinMat, 0.2);

        // Глаза
        mesh(head, new THREE.SphereGeometry(0.038, 12, 12), new THREE.MeshStandardMaterial({color:0xffffff}), 0.22, -0.09, 0.2);
        mesh(head, new THREE.SphereGeometry(0.038, 12, 12), new THREE.MeshStandardMaterial({color:0xffffff}), 0.22, 0.09, 0.2);
        mesh(head, new THREE.SphereGeometry(0.018, 10, 10), darkMat, 0.22, -0.09, 0.23);
        mesh(head, new THREE.SphereGeometry(0.018, 10, 10), darkMat, 0.22, 0.09, 0.23);

        // Челюсть / рот (для липсинга)
        const jaw = new THREE.Group();
        jaw.position.set(0, 0.08, 0.12);
        head.add(jaw);
        const mouth = mesh(jaw, new THREE.BoxGeometry(0.12, 0.04, 0.06), darkMat, 0, 0, 0.02);

        // Руки и ноги
        mesh(armL, new THREE.CylinderGeometry(0.085, 0.075, 0.55, 14), skinMat, -0.28);
        mesh(armR, new THREE.CylinderGeometry(0.085, 0.075, 0.55, 14), skinMat, -0.28);
        mesh(legL, new THREE.CylinderGeometry(0.11, 0.095, 0.75, 14), pantsMat, -0.38);
        mesh(legR, new THREE.CylinderGeometry(0.11, 0.095, 0.75, 14), pantsMat, -0.38);

        camera.position.set(0, 1.35, 5.0);
        camera.lookAt(0, 1.15, 0);

        const anim = "{anim}";
        const hasSpeech = {has_speech};  // true если есть текст озвучки
        let clock = new THREE.Clock();

        function animate() {
          requestAnimationFrame(animate);
          const t = clock.getElapsedTime();

          // --- Липсинг (простое открытие рта) ---
          if (hasSpeech) {
            // Рот открывается/закрывается с естественной частотой речи
            const talk = Math.max(0, Math.sin(t * 9.5)) * 0.7 + Math.max(0, Math.sin(t * 14.0)) * 0.3;
            jaw.rotation.x = talk * 0.28;
            mouth.scale.y = 0.6 + talk * 1.4;
          } else {
            jaw.rotation.x = 0;
            mouth.scale.y = 0.5;
          }

          // --- Анимации тела (медленные и естественные) ---
          if (anim === "jump") {
            // Нормальный прыжок: не слишком быстрый, с паузой в воздухе
            const cycle = (t * 1.1) % (Math.PI * 2);
            const jumpY = Math.max(0, Math.sin(cycle)) * 0.38;
            root.position.y = jumpY;
            // Руки чуть в стороны при прыжке
            armL.rotation.z = 0.25 + Math.sin(cycle) * 0.35;
            armR.rotation.z = -0.25 - Math.sin(cycle) * 0.35;
            // Ноги поджимаются
            legL.rotation.x = -jumpY * 1.2;
            legR.rotation.x = -jumpY * 1.2;
          } else if (anim === "wave") {
            armR.rotation.z = Math.sin(t * 4.2) * 0.45 - 1.35;
            armR.rotation.x = Math.sin(t * 4.2) * 0.15;
            // Лёгкое покачивание тела
            root.rotation.y = Math.sin(t * 0.6) * 0.08;
          } else if (anim === "walk") {
            // МЕДЛЕННАЯ ходьба (раньше было *5, теперь *2.2)
            const walkSpeed = 2.2;
            legL.rotation.x = Math.sin(t * walkSpeed) * 0.38;
            legR.rotation.x = -Math.sin(t * walkSpeed) * 0.38;
            armL.rotation.x = -Math.sin(t * walkSpeed) * 0.28;
            armR.rotation.x = Math.sin(t * walkSpeed) * 0.28;
            // Лёгкое покачивание корпуса
            pelvis.rotation.y = Math.sin(t * walkSpeed) * 0.06;
            root.position.y = Math.abs(Math.sin(t * walkSpeed * 2)) * 0.025;
          } else {
            // idle — спокойное дыхание + лёгкий поворот
            chest.position.y = 0.28 + Math.sin(t * 1.6) * 0.012;
            root.rotation.y = Math.sin(t * 0.55) * 0.12;
            armL.rotation.z = 0.12 + Math.sin(t * 1.3) * 0.04;
            armR.rotation.z = -0.12 - Math.sin(t * 1.3) * 0.04;
          }

          renderer.render(scene, camera);
        }
        animate();
      })();
      </script>
    </div>
    """,
    "2d_card": """
    <div class="card" style="
      width: 320px; height: 420px;
      background: linear-gradient(160deg, {c1}, {c3});
      border-radius: 28px;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      box-shadow: 0 20px 50px rgba(0,0,0,0.35);
      animation: floaty 3.5s ease-in-out infinite;
    ">
      <div style="
        width: 110px; height: 110px; border-radius: 50%;
        background: {c2}; margin-bottom: 24px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.25);
      "></div>
      <div style="
        color: white; font-size: 22px; font-weight: 700;
        text-align: center; padding: 0 20px; line-height: 1.3;
        text-shadow: 0 2px 8px rgba(0,0,0,0.4);
      ">{text}</div>
    </div>
    <style>
      @keyframes floaty {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-14px); }
      }
    </style>
    """,
    "default": """
    <div style="
      width: 180px; height: 180px; border-radius: 40px;
      background: linear-gradient(135deg, {c1}, {c2});
      box-shadow: 0 15px 40px rgba(0,0,0,0.3);
      animation: pulse 2.5s ease-in-out infinite;
    "></div>
    <style>
      @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.06); }
      }
    </style>
    """
}

BASE_HTML = """
<!doctype html>
<html>
<head>
<style>
  body {
    margin: 0; overflow: hidden;
    background: linear-gradient(135deg, {c0}, {c3});
    height: 100vh;
    display: flex; align-items: center; justify-content: center;
    font-family: system-ui, -apple-system, sans-serif;
  }
  .text {
    position: absolute; top: 48px; width: 90%; left: 5%;
    text-align: center; font-size: 42px; font-weight: 800;
    color: {c2}; text-shadow: 0 4px 16px rgba(0,0,0,0.45);
    z-index: 10; line-height: 1.2;
  }
</style>
</head>
<body>
  <div class="text">{text}</div>
  <div class="scene">{object_html}</div>
</body>
</html>
"""

SYSTEM_PROMPT = """Выбери шаблон и анимацию.
Ключи: 3d_person (человек), 2d_card, default.
Анимации для человека: jump, wave, walk, idle.
Если в идее есть человек / челик / персонаж / парень / девушка — всегда выбирай 3d_person.
Верни СТРОГО JSON: {"key": "3d_person", "anim": "wave"}"""

def run(scene: dict, plan: dict, original_idea: str = "") -> str:
    c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
    c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#e94560"
    c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#ffffff"
    c3 = plan["palette"][3] if len(plan["palette"]) > 3 else "#16213e"

    style = plan.get("style", "3d")
    idea_lower = (original_idea or "").lower()
    wants_person = any(w in idea_lower for w in [
        "человек", "челик", "персонаж", "парень", "девушка", "мужик",
        "женщина", "мужчина", "мальчик", "девочка", "герой", "человекa",
        "person", "man", "woman", "guy", "girl", "character"
    ])

    default_key = "3d_person" if (style == "3d" or wants_person) else "2d_card"

    user = f"Стиль: {style}. Текст сцены: {scene.get('text', '')}. Идея: {original_idea}"
    response = ask(SYSTEM_PROMPT, user, max_new_tokens=60).strip()

    template_key = default_key
    anim = "idle"

    try:
        start = response.find('{')
        end = response.rfind('}')
        if start != -1 and end != -1:
            data = json.loads(response[start:end+1])
            template_key = data.get("key", default_key)
            anim = data.get("anim", "idle")
    except Exception:
        pass

    if template_key not in TEMPLATES:
        template_key = default_key

    # Если просят человека — всегда 3d_person
    if wants_person:
        template_key = "3d_person"

    # В 2D режиме не форсируем 3d, если явно не просили человека
    if style == "2d" and not wants_person and template_key == "3d_person":
        template_key = "2d_card"

    # Есть ли текст для озвучки (включаем липсинг)
    narration = (scene.get("narration") or scene.get("text") or "").strip()
    has_speech = "true" if narration else "false"

    object_html = TEMPLATES[template_key]

    html = BASE_HTML.replace("{text}", scene.get("text", ""))
    html = html.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{c3}", c3)
    html = html.replace("{object_html}", object_html)
    html = html.replace("{anim}", anim)
    html = html.replace("{has_speech}", has_speech)

    return html

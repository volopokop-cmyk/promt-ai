from qwen_llm import ask
import json

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

        scene.add(new THREE.HemisphereLight(0xddeeff, 0x443322, 1.15));
        const key = new THREE.DirectionalLight(0xfff0dd, 1.6);
        key.position.set(-2.5, 5, 4); scene.add(key);
        const fill = new THREE.DirectionalLight(0xaaccff, 0.45);
        fill.position.set(3, 2, -2); scene.add(fill);

        const skinMat = new THREE.MeshStandardMaterial({ color: "{c1}", roughness: 0.65, metalness: 0.05 });
        const shirtMat = new THREE.MeshStandardMaterial({ color: "{c2}", roughness: 0.75 });
        const pantsMat = new THREE.MeshStandardMaterial({ color: "#2a3a5c", roughness: 0.8 });
        const darkMat = new THREE.MeshStandardMaterial({ color: "#2b1010", roughness: 0.55 });
        const lipMat = new THREE.MeshStandardMaterial({ color: "#c45c6a", roughness: 0.45 });

        const root = new THREE.Group(); scene.add(root);
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
          m.position.set(x, y, z); m.scale.set(sx, sy, sz); parent.add(m); return m;
        }

        mesh(pelvis, new THREE.SphereGeometry(0.3, 20, 20), pantsMat, 0, 0, 0, 1.15, 0.75, 0.95);
        mesh(spine, new THREE.CylinderGeometry(0.24, 0.26, 0.38, 18), shirtMat, 0.12);
        mesh(chest, new THREE.CylinderGeometry(0.27, 0.25, 0.4, 18), shirtMat, 0.12);
        mesh(neck, new THREE.CylinderGeometry(0.09, 0.1, 0.18, 14), skinMat, 0.06);
        mesh(head, new THREE.SphereGeometry(0.24, 28, 28), skinMat, 0.2);

        // глаза
        mesh(head, new THREE.SphereGeometry(0.038, 12, 12), new THREE.MeshStandardMaterial({color:0xffffff}), 0.22, -0.09, 0.2);
        mesh(head, new THREE.SphereGeometry(0.038, 12, 12), new THREE.MeshStandardMaterial({color:0xffffff}), 0.22, 0.09, 0.2);
        mesh(head, new THREE.SphereGeometry(0.018, 10, 10), new THREE.MeshStandardMaterial({color:0x1a1a1a}), 0.22, -0.09, 0.23);
        mesh(head, new THREE.SphereGeometry(0.018, 10, 10), new THREE.MeshStandardMaterial({color:0x1a1a1a}), 0.22, 0.09, 0.23);

        // === РОТ ===
        const jaw = new THREE.Group(); jaw.position.set(0, 0.06, 0.14); head.add(jaw);
        const upperLip = mesh(jaw, new THREE.BoxGeometry(0.11, 0.025, 0.04), lipMat, 0.018, 0, 0.02);
        const lowerLip = mesh(jaw, new THREE.BoxGeometry(0.11, 0.028, 0.04), lipMat, -0.012, 0, 0.02);
        const mouthHole = mesh(jaw, new THREE.BoxGeometry(0.09, 0.02, 0.03), darkMat, 0.002, 0, 0.015);

        mesh(armL, new THREE.CylinderGeometry(0.085, 0.075, 0.55, 14), skinMat, -0.28);
        mesh(armR, new THREE.CylinderGeometry(0.085, 0.075, 0.55, 14), skinMat, -0.28);
        mesh(legL, new THREE.CylinderGeometry(0.11, 0.095, 0.75, 14), pantsMat, -0.38);
        mesh(legR, new THREE.CylinderGeometry(0.11, 0.095, 0.75, 14), pantsMat, -0.38);

        camera.position.set(0, 1.35, 5.0);
        camera.lookAt(0, 1.15, 0);

        const anim = "{anim}";
        const lipCurve = {lip_curve}; // массив 0..1 по кадрам
        const fps = 15;
        let clock = new THREE.Clock();
        let start = performance.now() / 1000;

        function mouthOpen(v) {
          // v = 0..1
          const open = Math.max(0, Math.min(1, v));
          jaw.rotation.x = open * 0.32;
          lowerLip.position.y = -0.012 - open * 0.035;
          mouthHole.scale.y = 0.4 + open * 2.2;
          upperLip.scale.y = 1.0 - open * 0.15;
        }

        function animate() {
          requestAnimationFrame(animate);
          const t = clock.getElapsedTime();
          const elapsed = performance.now() / 1000 - start;
          const frame = Math.min(lipCurve.length - 1, Math.max(0, Math.floor(elapsed * fps)));
          const open = lipCurve.length ? lipCurve[frame] : 0;
          mouthOpen(open);

          if (anim === "jump") {
            const cycle = (t * 1.1) % (Math.PI * 2);
            const jumpY = Math.max(0, Math.sin(cycle)) * 0.38;
            root.position.y = jumpY;
            armL.rotation.z = 0.25 + Math.sin(cycle) * 0.35;
            armR.rotation.z = -0.25 - Math.sin(cycle) * 0.35;
            legL.rotation.x = -jumpY * 1.2;
            legR.rotation.x = -jumpY * 1.2;
          } else if (anim === "wave") {
            armR.rotation.z = Math.sin(t * 4.2) * 0.45 - 1.35;
            armR.rotation.x = Math.sin(t * 4.2) * 0.15;
            root.rotation.y = Math.sin(t * 0.6) * 0.08;
          } else if (anim === "walk") {
            const walkSpeed = 2.2;
            legL.rotation.x = Math.sin(t * walkSpeed) * 0.38;
            legR.rotation.x = -Math.sin(t * walkSpeed) * 0.38;
            armL.rotation.x = -Math.sin(t * walkSpeed) * 0.28;
            armR.rotation.x = Math.sin(t * walkSpeed) * 0.28;
            pelvis.rotation.y = Math.sin(t * walkSpeed) * 0.06;
            root.position.y = Math.abs(Math.sin(t * walkSpeed * 2)) * 0.025;
          } else {
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

    "2d_person": """
    <div class="char2d" style="position:relative; width:280px; height:480px; margin:0 auto;">
      <svg viewBox="0 0 280 480" width="280" height="480" xmlns="http://www.w3.org/2000/svg">
        <!-- тело -->
        <ellipse cx="140" cy="300" rx="70" ry="90" fill="{c2}"/>
        <!-- шея -->
        <rect x="125" y="190" width="30" height="40" rx="10" fill="{c1}"/>
        <!-- голова -->
        <circle cx="140" cy="140" r="62" fill="{c1}"/>
        <!-- волосы -->
        <path d="M78 130 Q140 40 202 130 Q190 95 140 85 Q90 95 78 130" fill="#3b2a1f"/>
        <!-- глаза -->
        <ellipse cx="118" cy="135" rx="12" ry="14" fill="#fff"/>
        <ellipse cx="162" cy="135" rx="12" ry="14" fill="#fff"/>
        <circle cx="120" cy="137" r="6" fill="#1a1a1a"/>
        <circle cx="164" cy="137" r="6" fill="#1a1a1a"/>
        <!-- брови -->
        <path d="M105 118 Q118 110 131 118" stroke="#3b2a1f" stroke-width="4" fill="none" stroke-linecap="round"/>
        <path d="M149 118 Q162 110 175 118" stroke="#3b2a1f" stroke-width="4" fill="none" stroke-linecap="round"/>
        <!-- нос -->
        <path d="M140 145 L135 160 Q140 164 145 160 Z" fill="#d4a07a" opacity="0.7"/>
        <!-- руки -->
        <rect id="armL" x="40" y="230" width="28" height="110" rx="14" fill="{c1}" transform="rotate(12 54 230)"/>
        <rect id="armR" x="212" y="230" width="28" height="110" rx="14" fill="{c1}" transform="rotate(-12 226 230)"/>
        <!-- ноги -->
        <rect x="105" y="380" width="28" height="90" rx="12" fill="#2a3a5c"/>
        <rect x="147" y="380" width="28" height="90" rx="12" fill="#2a3a5c"/>
        <!-- РОТ: верхняя и нижняя губа + дырка -->
        <g id="mouth" transform="translate(140,175)">
          <ellipse id="mouthHole" cx="0" cy="0" rx="18" ry="3" fill="#2b1010"/>
          <path id="upperLip" d="M-20 0 Q0 -6 20 0" stroke="#c45c6a" stroke-width="5" fill="none" stroke-linecap="round"/>
          <path id="lowerLip" d="M-20 0 Q0 8 20 0" stroke="#c45c6a" stroke-width="5" fill="none" stroke-linecap="round"/>
        </g>
      </svg>
      <script>
      (function() {
        const lipCurve = {lip_curve};
        const fps = 15;
        const anim = "{anim}";
        const hole = document.getElementById('mouthHole');
        const lower = document.getElementById('lowerLip');
        const armR = document.getElementById('armR');
        const start = performance.now() / 1000;

        function setMouth(v) {
          const open = Math.max(0, Math.min(1, v));
          hole.setAttribute('ry', String(3 + open * 14));
          lower.setAttribute('d', `M-20 0 Q0 ${8 + open * 16} 20 0`);
        }

        function tick() {
          const elapsed = performance.now() / 1000 - start;
          const frame = Math.min(lipCurve.length - 1, Math.max(0, Math.floor(elapsed * fps)));
          setMouth(lipCurve.length ? lipCurve[frame] : 0);

          // лёгкие анимации тела
          if (anim === 'wave' && armR) {
            const a = Math.sin(elapsed * 4.2) * 18 - 12;
            armR.setAttribute('transform', `rotate(${a} 226 230)`);
          } else if (anim === 'walk') {
            const root = document.querySelector('.char2d');
            if (root) root.style.transform = `translateY(${Math.sin(elapsed * 2.2) * 4}px)`;
          } else if (anim === 'jump') {
            const root = document.querySelector('.char2d');
            if (root) root.style.transform = `translateY(${-Math.max(0, Math.sin(elapsed * 1.1)) * 28}px)`;
          }
          requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
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
      <div style="width:110px;height:110px;border-radius:50%;background:{c2};margin-bottom:24px;box-shadow:0 8px 20px rgba(0,0,0,0.25);"></div>
      <div style="color:white;font-size:22px;font-weight:700;text-align:center;padding:0 20px;line-height:1.3;text-shadow:0 2px 8px rgba(0,0,0,0.4);">{text}</div>
    </div>
    <style>@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}</style>
    """,

    "default": """
    <div style="width:180px;height:180px;border-radius:40px;background:linear-gradient(135deg,{c1},{c2});box-shadow:0 15px 40px rgba(0,0,0,0.3);animation:pulse 2.5s ease-in-out infinite;"></div>
    <style>@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.06)}}</style>
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
Ключи: 3d_person, 2d_person, 2d_card, default.
Анимации: jump, wave, walk, idle.
Если просят человека — 3d_person или 2d_person (в зависимости от стиля).
Верни СТРОГО JSON: {"key": "3d_person", "anim": "wave"}"""

def run(scene: dict, plan: dict, original_idea: str = "", lip_curve: list | None = None) -> str:
    c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
    c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#e8b89a"  # более телесный по умолчанию
    c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#4a90d9"
    c3 = plan["palette"][3] if len(plan["palette"]) > 3 else "#16213e"

    style = plan.get("style", "3d")
    idea_lower = (original_idea or "").lower()
    wants_person = any(w in idea_lower for w in [
        "человек", "челик", "персонаж", "парень", "девушка", "мужик",
        "женщина", "мужчина", "мальчик", "девочка", "герой",
        "person", "man", "woman", "guy", "girl", "character"
    ])

    if style == "2d":
        default_key = "2d_person" if wants_person else "2d_card"
    else:
        default_key = "3d_person" if wants_person or style == "3d" else "2d_card"

    user = f"Стиль: {style}. Текст: {scene.get('text', '')}. Идея: {original_idea}"
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

    if wants_person:
        template_key = "2d_person" if style == "2d" else "3d_person"
    elif style == "2d" and template_key == "3d_person":
        template_key = "2d_person"
    elif style == "3d" and template_key == "2d_person":
        template_key = "3d_person"

    curve = lip_curve if lip_curve is not None else [0.0]
    lip_js = json.dumps(curve)

    object_html = TEMPLATES[template_key]
    html = BASE_HTML.replace("{text}", scene.get("text", ""))
    html = html.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{c3}", c3)
    html = html.replace("{object_html}", object_html)
    html = html.replace("{anim}", anim)
    html = html.replace("{lip_curve}", lip_js)
    return html

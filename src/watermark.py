import re

POSITIONS = [
    {"top": "24px",   "left": "24px"},
    {"top": "24px",   "right": "24px"},
    {"bottom": "24px", "right": "24px"},
    {"bottom": "24px", "left": "24px"},
    {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"},
]

STEP = 3.0

CSS = """
#wm-overlay {
  position: fixed; inset: 0; pointer-events: none; z-index: 9999;
}
#wm {
  position: absolute;
  opacity: 0;
  transition: opacity .6s ease, top .8s ease, left .8s ease,
              right .8s ease, bottom .8s ease, transform .8s ease;
}
/* Размер твоего логотипа */
#wm img {
  height: 100px; 
  width: auto;
  filter: drop-shadow(0px 5px 10px rgba(0,0,0,0.6));
}
"""

def _build_js(total_seconds: float) -> str:
    steps = max(1, int(total_seconds / STEP))
    seq = [POSITIONS[i % len(POSITIONS)] for i in range(steps)]
    return f"""
<script>
(function() {{
  const seq = {seq!r};
  const el = document.getElementById('wm');
  let i = 0;
  function apply(p) {{
    el.style.top = p.top || 'auto';
    el.style.left = p.left || 'auto';
    el.style.right = p.right || 'auto';
    el.style.bottom = p.bottom || 'auto';
    el.style.transform = p.transform || 'none';
  }}
  function tick() {{
    el.style.opacity = '0';
    setTimeout(() => {{
      apply(seq[i % seq.length]); i++;
      el.style.opacity = '1';
    }}, 600);
  }}
  apply(seq[0]); i = 1;
  setTimeout(() => {{ el.style.opacity = '1'; }}, 300);
  setInterval(tick, {int(STEP * 1000)});
}})();
</script>
"""

# ТВОЯ ПРЯМАЯ ССЫЛКА НА КАРТИНКУ (RAW)
GITHUB_RAW_LINK = "https://raw.githubusercontent.com/volopokop-cmyk/promt-ai/main/logo.jpg"

def inject(html: str, duration: float) -> str:
    overlay = (
        f"<style>{CSS}</style>"
        f'<div id="wm-overlay"><div id="wm"><img src="{GITHUB_RAW_LINK}" alt="Prompt AI"></div></div>'
        f"{_build_js(duration)}"
    )
    if re.search(r"</body>", html, re.I):
        return re.sub(r"</body>", overlay + "</body>", html, count=1, flags=re.I)
    return html + overlay

import re

POSITIONS = [
    {"top": "24px",   "left": "24px"},
    {"top": "24px",   "right": "24px"},
    {"bottom": "24px", "right": "24px"},
    {"bottom": "24px", "left": "24px"},
    {"bottom": "24px", "left": "50%", "transform": "translateX(-50%)"},
]

STEP = 2.5

CSS = """
#wm-overlay {
  position: fixed; inset: 0; pointer-events: none; z-index: 9999;
}
#wm {
  position: absolute;
  font: 600 20px/1 system-ui, Segoe UI, Roboto, sans-serif;
  letter-spacing: 0.08em;
  color: rgba(255,255,255,0.82);
  text-shadow: 0 2px 10px rgba(0,0,0,0.55), 0 0 1px rgba(0,0,0,0.9);
  padding: 8px 14px; border-radius: 999px;
  background: rgba(0,0,0,0.28);
  backdrop-filter: blur(6px);
  opacity: 0;
  transition: opacity .6s ease, top .8s ease, left .8s ease,
              right .8s ease, bottom .8s ease, transform .8s ease;
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

def inject(html: str, duration: float) -> str:
    overlay = (
        f"<style>{CSS}</style>"
        f'<div id="wm-overlay"><div id="wm">promt bot</div></div>'
        f"{_build_js(duration)}"
    )
    if re.search(r"</body>", html, re.I):
        return re.sub(r"</body>", overlay + "</body>", html, count=1, flags=re.I)
    return html + overlay

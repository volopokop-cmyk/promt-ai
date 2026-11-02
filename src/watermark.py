import re

CSS = """
#wm-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
}
#wm {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.7s ease, top 1.1s cubic-bezier(0.4, 0, 0.2, 1),
              left 1.1s cubic-bezier(0.4, 0, 0.2, 1),
              right 1.1s cubic-bezier(0.4, 0, 0.2, 1),
              bottom 1.1s cubic-bezier(0.4, 0, 0.2, 1),
              transform 1.1s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 6px 16px rgba(0,0,0,0.55));
}
#wm img {
  height: 72px;
  width: auto;
  display: block;
  border-radius: 12px;
}
.wm-text {
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  letter-spacing: 0.3px;
  white-space: nowrap;
  line-height: 1.1;
  margin-top: -6px;
  text-shadow:
    -1px -1px 0 rgba(0,0,0,0.85),
     1px -1px 0 rgba(0,0,0,0.85),
    -1px  1px 0 rgba(0,0,0,0.85),
     1px  1px 0 rgba(0,0,0,0.85),
     0 2px 8px rgba(0,0,0,0.7);
}
"""

def _build_js(total_seconds: float) -> str:
    # Красивый полёт по углам + лёгкий центр
    positions = [
        {"top": "28px",  "left": "28px",  "transform": "none"},
        {"top": "28px",  "right": "28px", "transform": "none"},
        {"bottom": "36px", "right": "28px", "transform": "none"},
        {"bottom": "36px", "left": "28px",  "transform": "none"},
        {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%) scale(1.05)"},
    ]
    step = 3.2
    steps = max(2, int(total_seconds / step))
    seq = [positions[i % len(positions)] for i in range(steps + 1)]

    return f"""
<script>
(function() {{
  const seq = {seq!r};
  const el = document.getElementById('wm');
  if (!el) return;
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
      apply(seq[i % seq.length]);
      i++;
      el.style.opacity = '0.92';
    }}, 650);
  }}

  // Появление через 1.2 сек после старта сцены
  setTimeout(() => {{
    apply(seq[0]);
    i = 1;
    el.style.opacity = '0.92';
  }}, 1200);

  setInterval(tick, {int(step * 1000)});
}})();
</script>
"""

GITHUB_RAW_LINK = "https://raw.githubusercontent.com/volopokop-cmyk/promt-ai/main/logo.jpg"

def inject(html: str, duration: float, username: str = "") -> str:
    """Вставляет красивую летающую вотермарку (лого + ник) прямо в HTML сцены."""
    name = (username or "").lstrip("@").strip()
    display_name = f"@{name}" if name else "Prompt AI"

    overlay = (
        f"<style>{CSS}</style>"
        f'<div id="wm-overlay"><div id="wm">'
        f'<img src="{GITHUB_RAW_LINK}" alt="logo">'
        f'<span class="wm-text">{display_name}</span>'
        f"</div></div>"
        f"{_build_js(duration)}"
    )

    if re.search(r"</body>", html, re.I):
        return re.sub(r"</body>", overlay + "</body>", html, count=1, flags=re.I)
    return html + overlay

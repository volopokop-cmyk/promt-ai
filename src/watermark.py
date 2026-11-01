import re

CSS = """
#wm-overlay {
  position: fixed; inset: 0; pointer-events: none; z-index: 9999;
}
#wm {
  position: absolute;
  display: flex;
  flex-direction: row;    
  align-items: flex-end; 
  opacity: 0;
  transition: opacity 0.6s ease, top 0.8s ease, left 0.8s ease, right 0.8s ease, bottom 0.8s ease;
}
#wm img {
  height: 80px; 
  width: auto;
  filter: drop-shadow(0 4px 10px rgba(0,0,0,0.8));
  display: block;
}
.wm-text {
  color: #ffffff;
  font-size: 18px;        
  font-weight: 800; 
  font-family: system-ui, -apple-system, sans-serif;
  white-space: nowrap;
  line-height: 1;
  margin-left: 5px;       
  margin-bottom: 20px;    
  text-shadow: 
    -1px -1px 0 #000,  
     1px -1px 0 #000,
    -1px  1px 0 #000,
     1px  1px 0 #000,
     0px  2px 5px rgba(0,0,0,0.9);
}
"""

def _build_js(total_seconds: float) -> str:
    steps = max(1, int(total_seconds / 3.0))
    positions = [
        {"top": "30px", "left": "30px"},
        {"top": "30px", "right": "30px"},
        {"bottom": "30px", "right": "30px"},
        {"bottom": "30px", "left": "30px"}
    ]
    seq = [positions[i % len(positions)] for i in range(steps + 2)]
    
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
  }}
  function tick() {{
    el.style.opacity = '0';
    setTimeout(() => {{
      apply(seq[i % seq.length]); 
      i++;
      el.style.opacity = '1';
    }}, 600);
  }}
  apply(seq[0]); i = 1;
  setTimeout(() => {{ el.style.opacity = '1'; }}, 300);
  setInterval(tick, 3000);
}})();
</script>
"""

GITHUB_RAW_LINK = "https://raw.githubusercontent.com/volopokop-cmyk/promt-ai/main/logo.jpg"

def inject(html: str, duration: float, username: str = "") -> str:
    display_name = f"@{username.lstrip('@')}" if username else ""
    
    overlay = (
        f"<style>{CSS}</style>"
        f'<div id="wm-overlay"><div id="wm">'
        f'<img src="{GITHUB_RAW_LINK}" alt="Logo">'
        f'<span class="wm-text">{display_name}</span>'
        f'</div></div>'
        f"{_build_js(duration)}"
    )
    
    if re.search(r"</body>", html, re.I):
        return re.sub(r"</body>", overlay + "</body>", html, count=1, flags=re.I)
    return html + overlay

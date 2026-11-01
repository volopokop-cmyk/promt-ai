import re

CSS = """
body { background: transparent; overflow: hidden; margin: 0; }
#wm {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0;
  transition: opacity 0.8s ease, top 0.8s ease, left 0.8s ease, right 0.8s ease, bottom 0.8s ease;
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
  margin-top: -22px;        
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
    # Позиции для полета: верх-лево, верх-право, низ-право, низ-лево, центр
    positions = [
        {"top": "30px", "left": "30px"},
        {"top": "30px", "right": "30px"},
        {"bottom": "30px", "right": "30px"},
        {"bottom": "30px", "left": "30px"},
        {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"}
    ]
    seq = [positions[i % len(positions)] for i in range(steps + 1)]
    
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
      apply(seq[i % seq.length]); 
      i++;
      el.style.opacity = '1';
    }}, 800);
  }}
  
  setTimeout(() => {{
    apply(seq[0]); 
    i = 1;
    el.style.opacity = '1';
  }}, 2000); // Ждем 2 секунды, чтобы видео успело прогрузиться
  
  setInterval(tick, 3000);
}})();
</script>
"""

GITHUB_RAW_LINK = "https://raw.githubusercontent.com/volopokop-cmyk/promt-ai/main/logo.jpg"

def inject(html: str, duration: float, username: str = "") -> str:
    display_name = f"@{username.lstrip('@')}" if username else ""
    
    # Мы не добавляем вотермарку в HTML, мы создаем отдельный HTML-файл для рендера
    wm_html = f"""
<!doctype html>
<html>
<head>
<style>{CSS}</style>
</head>
<body>
  <div id="wm">
    <img src="{GITHUB_RAW_LINK}" alt="Logo">
    <span class="wm-text">{display_name}</span>
  </div>
  {_build_js(duration)}
</body>
</html>
"""
    # Сохраняем этот HTML во временный файл, чтобы потом отрендерить его отдельно
    from pathlib import Path
    wm_path = Path("work/watermark.html")
    wm_path.parent.mkdir(exist_ok=True)
    wm_path.write_text(wm_html, encoding="utf-8")
    
    return html # Возвращаем оригинальный HTML сцены без вотермарки

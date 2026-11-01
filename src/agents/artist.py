from qwen_llm import ask

# --- БИБЛИОТЕКА 2D ШАБЛОНОВ ---
TEMPLATES_2D = {
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
    "person_run": """
    <div class="character" style="position:relative; width:200px; height:300px;">
      <div class="head" style="position:absolute; top:20px; left:50px; width:100px; height:100px; background:{c1}; border-radius:50%;"></div>
      <div class="body" style="position:absolute; top:120px; left:75px; width:50px; height:100px; background:{c1}; border-radius:20px; transform:rotate(15deg);"></div>
      <div class="arm run-arms" style="position:absolute; top:130px; left:30px; width:30px; height:100px; background:{c1}; border-radius:15px; transform-origin:top center;"></div>
      <div class="arm run-arms" style="position:absolute; top:130px; left:140px; width:30px; height:100px; background:{c1}; border-radius:15px; transform-origin:top center;"></div>
      <div class="leg run-legs" style="position:absolute; top:210px; left:50px; width:30px; height:90px; background:{c1}; border-radius:15px; transform-origin:top center;"></div>
      <div class="leg run-legs" style="position:absolute; top:210px; left:120px; width:30px; height:90px; background:{c1}; border-radius:15px; transform-origin:top center;"></div>
    </div>
    """,
    "person_sit": """
    <div class="character" style="position:relative; width:200px; height:250px;">
      <div class="head" style="position:absolute; top:0; left:50px; width:100px; height:100px; background:{c1}; border-radius:50%;"></div>
      <div class="body" style="position:absolute; top:100px; left:75px; width:50px; height:100px; background:{c1}; border-radius:20px;"></div>
      <div class="legs" style="position:absolute; top:190px; left:75px; width:100px; height:30px; background:{c1}; border-radius:15px;"></div>
      <div class="chair" style="position:absolute; top:190px; left:50px; width:100px; height:40px; background:{c1}; border-radius:10px;"></div>
    </div>
    """,
    "cat": """
    <div class="character" style="position:relative; width:150px; height:150px;">
      <div class="head" style="position:absolute; top:0; left:25px; width:100px; height:80px; background:{c1}; border-radius:40px;"></div>
      <div class="ear" style="position:absolute; top:-20px; left:30px; width:0; height:0; border-left:20px solid transparent; border-right:20px solid transparent; border-bottom:40px solid {c1};"></div>
      <div class="ear" style="position:absolute; top:-20px; left:80px; width:0; height:0; border-left:20px solid transparent; border-right:20px solid transparent; border-bottom:40px solid {c1};"></div>
      <div class="tail" style="position:absolute; top:80px; left:110px; width:50px; height:15px; background:{c1}; border-radius:10px; transform-origin:left center; animation: wag 1s infinite alternate;"></div>
    </div>
    """,
    "tree": """
    <div class="character" style="position:relative; width:200px; height:400px;">
      <div class="trunk" style="position:absolute; bottom:0; left:80px; width:40px; height:200px; background:{c1};"></div>
      <div class="leaves" style="position:absolute; top:0; left:0; width:200px; height:200px; background:{c1}; border-radius:50%; animation: sway 3s infinite alternate ease-in-out;"></div>
    </div>
    """,
    "flower": """
    <div class="character" style="position:relative; width:150px; height:300px;">
      <div class="stem" style="position:absolute; bottom:0; left:70px; width:10px; height:150px; background:{c1};"></div>
      <div class="petals" style="position:absolute; bottom:130px; left:30px; width:90px; height:90px; background:{c1}; border-radius:50%; border: 10px dashed {c2}; animation: spin 10s linear infinite;"></div>
    </div>
    """,
    "rocket": """
    <div class="character" style="position:relative; width:150px; height:400px;">
      <div class="body" style="position:absolute; bottom:50px; left:50px; width:50px; height:200px; background:{c1}; border-radius:50px 50px 10px 10px;"></div>
      <div class="flame" style="position:absolute; bottom:0; left:55px; width:40px; height:60px; background:{c2}; border-radius:50% 50% 50% 50% / 60% 60% 40% 40%; animation: flicker 0.2s infinite alternate;"></div>
    </div>
    """,
    "car": """
    <div class="character" style="position:relative; width:300px; height:150px;">
      <div class="body" style="position:absolute; bottom:20px; left:0; width:300px; height:80px; background:{c1}; border-radius: 30px 30px 10px 10px;"></div>
      <div class="wheel" style="position:absolute; bottom:0; left:50px; width:60px; height:60px; background:{c2}; border-radius:50%; animation: spin 1s linear infinite;"></div>
      <div class="wheel" style="position:absolute; bottom:0; left:190px; width:60px; height:60px; background:{c2}; border-radius:50%; animation: spin 1s linear infinite;"></div>
    </div>
    """,
    "planet": """
    <div class="character" style="position:relative; width:250px; height:250px;">
      <div class="ball" style="position:absolute; top:25px; left:25px; width:200px; height:200px; background:{c1}; border-radius:50%;"></div>
      <div class="ring" style="position:absolute; top:100px; left:0; width:250px; height:50px; border: 10px solid {c2}; border-radius:50%; transform: rotate(-20deg);"></div>
    </div>
    """,
    "default": """
    <div class="character" style="position:relative; width:100px; height:100px; background:{c1}; border-radius:20px; animation: float 2s infinite alternate;"></div>
    """
}

# Базовый каркас HTML со стилями и анимациями
BASE_HTML = """
<!doctype html>
<html>
<head>
<style>
  body { 
    margin: 0; overflow: hidden; background: linear-gradient(135deg, {c0}, {c3}); 
    height: 100vh; display: flex; align-items: center; justify-content: center; 
    font-family: system-ui, sans-serif; 
  }
  .text { 
    position: absolute; top: 50px; width: 100%; text-align: center; 
    font-size: 56px; font-weight: bold; color: {c2}; 
    text-shadow: 0 4px 10px rgba(0,0,0,0.5); z-index: 10; 
  }
  
  /* Общие анимации для шаблонов */
  @keyframes walkLegs { 0%, 100% { transform: rotate(-20deg); } 50% { transform: rotate(20deg); } }
  @keyframes walkArms { 0%, 100% { transform: rotate(20deg); } 50% { transform: rotate(-20deg); } }
  @keyframes runLegs { 0%, 100% { transform: rotate(-40deg); } 50% { transform: rotate(40deg); } }
  @keyframes runArms { 0%, 100% { transform: rotate(40deg); } 50% { transform: rotate(-40deg); } }
  @keyframes float { 0% { transform: translateY(0); } 100% { transform: translateY(-20px); } }
  @keyframes sway { 0% { transform: rotate(-5deg); } 100% { transform: rotate(5deg); } }
  @keyframes spin { 100% { transform: rotate(360deg); } }
  @keyframes flicker { 0% { opacity: 0.8; } 100% { opacity: 1; transform: scaleY(1.1); } }
  @keyframes wag { 0% { transform: rotate(-20deg); } 100% { transform: rotate(20deg); } }

  .walk-legs { animation: walkLegs 0.6s infinite ease-in-out; }
  .walk-arms { animation: walkArms 0.6s infinite ease-in-out; }
  .run-legs { animation: runLegs 0.4s infinite ease-in-out; }
  .run-arms { animation: runArms 0.4s infinite ease-in-out; }
</style>
</head>
<body>
  <div class="text">{text}</div>
  <div class="scene">
    {object_html}
  </div>
</body>
</html>
"""

SYSTEM_PROMPT = """Ты — умный ассистент-художник. Твоя задача — выбрать подходящий шаблон для сцены и заменить в нём переменные на цвета и текст.

Доступные шаблоны (ключи): person_walk, person_run, person_sit, cat, tree, flower, rocket, car, planet, default.

Правила:
1. Выбери ОДИН ключ шаблона, который лучше всего подходит к тексту сцены.
2. Замени {c0} на palette[0] (фон 1).
3. Замени {c1} на palette[1] (цвет объекта).
4. Замени {c2} на palette[2] (текст и акценты).
5. Замени {c3} на palette[3] (фон 2).
6. Замени {text} на текст из сцены.
7. Верни ТОЛЬКО имя ключа, например: person_run. Никаких объяснений, только название шаблона!"""

def run(scene: dict, plan: dict, original_idea: str = "") -> str:
    c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
    c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#e94560"
    c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#ffffff"
    c3 = plan["palette"][3] if len(plan["palette"]) > 3 else "#16213e"
    
    # Нейросеть выбирает шаблон
    user = f"Текст сцены: {scene.get('text', '')}. Запрос пользователя: {original_idea}"
    template_key = ask(SYSTEM_PROMPT, user, max_new_tokens=20).strip().lower()
    
    # Очищаем ответ от мусора (если нейросеть написала лишнее)
    for key in TEMPLATES_2D.keys():
        if key in template_key:
            template_key = key
            break
    else:
        template_key = "default"
        
    object_html = TEMPLATES_2D[template_key]
    
    # Собираем итоговый HTML
    html = BASE_HTML.replace("{text}", scene.get("text", ""))
    html = html.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{c3}", c3)
    html = html.replace("{object_html}", object_html)
    
    return html

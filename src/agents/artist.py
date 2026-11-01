from qwen_llm import ask

# Шаблон с анимированным человечком
BASE_2D = """
<!doctype html>
<html>
<head>
<style>
  body { margin: 0; overflow: hidden; background: {c0}; height: 100vh; display: flex; align-items: center; justify-content: center; font-family: system-ui, sans-serif; }
  
  .text { position: absolute; top: 50px; width: 100%; text-align: center; font-size: 56px; font-weight: bold; color: {c2}; text-shadow: 0 4px 10px rgba(0,0,0,0.5); z-index: 10; }
  
  /* Контейнер для персонажа */
  .character { position: relative; width: 200px; height: 300px; }
  
  /* Голова */
  .head { position: absolute; top: 0; left: 50px; width: 100px; height: 100px; background: {c1}; border-radius: 50%; }
  
  /* Туловище */
  .body { position: absolute; top: 100px; left: 75px; width: 50px; height: 120px; background: {c1}; border-radius: 20px; }
  
  /* Руки и ноги */
  .arm-left { position: absolute; top: 110px; left: 40px; width: 30px; height: 100px; background: {c1}; border-radius: 15px; transform-origin: top center; }
  .arm-right { position: absolute; top: 110px; left: 130px; width: 30px; height: 100px; background: {c1}; border-radius: 15px; transform-origin: top center; }
  
  .leg-left { position: absolute; top: 210px; left: 60px; width: 30px; height: 90px; background: {c1}; border-radius: 15px; transform-origin: top center; }
  .leg-right { position: absolute; top: 210px; left: 110px; width: 30px; height: 90px; background: {c1}; border-radius: 15px; transform-origin: top center; }

  /* АНИМАЦИИ (нейросеть будет их включать) */
  @keyframes walk {
    0%, 100% { transform: rotate(-20deg); }
    50% { transform: rotate(20deg); }
  }
  @keyframes wave {
    0%, 100% { transform: rotate(-30deg); }
    50% { transform: rotate(30deg); }
  }
  @keyframes jump {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-50px); }
  }
</style>
</head>
<body>
  <div class="text">{text}</div>
  
  <div class="character">
    <div class="head"></div>
    <div class="body"></div>
    <!-- Нейросеть добавит класс анимации сюда: class="arm-left wave" -->
    <div class="arm-left {anim_arm_left}"></div>
    <div class="arm-right {anim_arm_right}"></div>
    <div class="leg-left {anim_leg_left}"></div>
    <div class="leg-right {anim_leg_right}"></div>
  </div>
</body>
</html>
"""

SYSTEM_PROMPT = """Ты — аниматор. Твоя задача — взять шаблон и добавить в него цвета и анимации, чтобы персонаж двигался.

Доступные анимации:
- "walk" (ходьба - для ног)
- "wave" (махание - для рук)
- "jump" (прыжок - для всего тела)

Правила:
1. Замени {c0} на palette[0].
2. Замени {c1} на palette[1].
3. Замени {c2} на palette[2].
4. Замени {text} на текст.
5. Выбери анимацию для рук и ног в зависимости от текста:
   - Если текст про ходьбу/шаги: {anim_leg_left} = "walk", {anim_leg_right} = "walk"
   - Если текст про махание/привет: {anim_arm_left} = "wave" или {anim_arm_right} = "wave"
   - Если текст про прыжок: вместо <div class="character"> сделай <div class="character jump">
   - Если ничего не подходит, оставь пустые строки.
6. Верни ТОЛЬКО готовый HTML.

Шаблон:
{template}
"""

def run(scene: dict, plan: dict, original_idea: str = "") -> str:
    template = BASE_2D
    
    # Подставляем базовые цвета на случай, если нейросеть ошибется
    c0 = plan["palette"][0] if len(plan["palette"]) > 0 else "#1a1a2e"
    c1 = plan["palette"][1] if len(plan["palette"]) > 1 else "#e94560"
    c2 = plan["palette"][2] if len(plan["palette"]) > 2 else "#ffffff"
    
    html = template.replace("{c0}", c0).replace("{c1}", c1).replace("{c2}", c2).replace("{text}", scene.get("text", ""))
    
    # Просим нейросеть расставить анимации
    system = SYSTEM_PROMPT.replace("{template}", html)
    user = f"Текст сцены: {scene.get('text', '')}. Пользователь просит: {original_idea}"
    
    result = ask(system, user, max_new_tokens=2048)
    
    if "```" in result:
        result = result.split("```")[1]
        if result.startswith("html"): result = result[4:]
    result = result.strip()
    
    # Если нейросеть вернула мусор (не HTML), возвращаем простой шаблон
    if "<!doctype" not in result.lower():
        # По умолчанию машем руками
        result = html.replace("{anim_arm_left}", "wave").replace("{anim_arm_right}", "").replace("{anim_leg_left}", "").replace("{anim_leg_right}", "")
        
    return result

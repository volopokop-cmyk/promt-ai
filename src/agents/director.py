import json
from qwen_llm import ask_json

SYSTEM = """Ты — опытный режиссёр коротких анимационных видео.
На вход приходит сценарий (JSON) и пожелания пользователя.

Твоя задача — сделать технический план съёмки, который будет выглядеть профессионально.

Правила:
1. style — СТРОГО используй значение, которое передал пользователь ("2d" или "3d"). Не меняй его.
2. palette: ровно 4 красивых HEX-цвета [фон, основной акцент, текст, дополнительный]. Цвета должны хорошо сочетаться.
3. font: "sans" | "serif" | "mono".
4. camera: "static" | "zoom_in" | "zoom_out" | "pan_left" | "pan_right" | "orbit".
5. Количество сцен зависит от длительности:
   - 5–10 сек → 2–3 сцены
   - 11–20 сек → 3–4 сцены
   - 21–30 сек → 4–5 сцен
6. Каждая сцена:
   - text: короткий яркий заголовок (до 7 слов)
   - duration: реалистичная длительность в секундах
   - camera_move: движение камеры
   - transition: "cut" | "fade" | "slide"
   - lighting: "day" | "night" | "neon" | "soft" | "cinematic"
   - narration: текст озвучки (можно взять из сценария)

Верни ТОЛЬКО чистый JSON без markdown и пояснений:
{
  "style": "2d или 3d",
  "palette": ["#......", "#......", "#......", "#......"],
  "font": "sans",
  "camera": "zoom_in",
  "scenes": [
    {
      "text": "...",
      "duration": 3.5,
      "camera_move": "zoom_in",
      "transition": "fade",
      "lighting": "cinematic",
      "narration": "..."
    }
  ]
}"""

def run(script: dict, forced_style: str = "3d", total_duration: int = 10) -> dict:
    user = (
        f"Сценарий:\n{json.dumps(script, ensure_ascii=False)}\n\n"
        f"Требования пользователя:\n"
        f"- Стиль: {forced_style}\n"
        f"- Общая длительность видео: {total_duration} секунд\n"
        f"Сделай план строго в этом стиле и под эту длительность."
    )

    plan = ask_json(SYSTEM, user, max_new_tokens=1400)

    # Жёстко фиксируем стиль
    plan["style"] = forced_style if forced_style in ("2d", "3d") else "3d"

    if "palette" not in plan or len(plan["palette"]) < 3:
        plan["palette"] = ["#0f0f1a", "#e94560", "#ffffff", "#16213e"]

    scenes = plan.get("scenes", [])
    if not scenes:
        scenes = [{
            "text": script.get("title", "Видео")[:40],
            "duration": float(total_duration),
            "camera_move": "static",
            "transition": "fade",
            "lighting": "soft",
            "narration": ""
        }]
        plan["scenes"] = scenes

    for s in plan["scenes"]:
        s["duration"] = max(2.0, min(8.0, float(s.get("duration", 3.0))))

    return plan

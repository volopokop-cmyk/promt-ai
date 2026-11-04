import json
from qwen_llm import ask_json

SYSTEM = """Ты — режиссёр коротких анимационных видео.
Сохрани смысл сценария: несколько сцен с разными объектами и действиями.

Правила:
1. style — СТРОГО значение пользователя ("2d" или "3d").
2. palette: 4 HEX цвета.
3. Для КАЖДОЙ сцены обязательно сохрани:
   - visual: person|cat|dog|object|world|abstract
   - action: idle|walk|wave|jump|squat|stand|spin|bounce|look
   - text: короткий заголовок
   - narration: речь или ""
   - duration: секунды
4. Не склеивай разные объекты в одну сцену.
5. Если в сценарии человек, потом кошка — это РАЗНЫЕ сцены.

Верни ТОЛЬКО JSON:
{
  "style": "3d",
  "palette": ["#0f0f1a", "#e94560", "#ffffff", "#16213e"],
  "font": "sans",
  "camera": "static",
  "scenes": [
    {
      "text": "Приседает",
      "visual": "person",
      "action": "squat",
      "duration": 3.0,
      "camera_move": "static",
      "transition": "cut",
      "lighting": "soft",
      "narration": ""
    }
  ]
}"""

def _from_script(script: dict, forced_style: str, total_duration: int, max_scenes: int) -> dict:
    raw = (script.get("scenes") or [])[:max_scenes]
    if not raw:
        raw = [{"text": script.get("title", "Видео"), "visual": "object", "action": "idle", "narration": ""}]
    n = max(1, len(raw))
    base = max(1.5, total_duration / n)
    scenes = []
    for s in raw:
        scenes.append({
            "text": (s.get("text") or s.get("beat") or "Сцена")[:40],
            "visual": s.get("visual") or "object",
            "action": s.get("action") or "idle",
            "duration": float(base),
            "camera_move": "static",
            "transition": "cut",
            "lighting": "soft",
            "narration": s.get("narration") or "",
        })
    return {
        "style": forced_style,
        "palette": ["#0f0f1a", "#e94560", "#ffffff", "#16213e"],
        "font": "sans",
        "camera": "static",
        "scenes": scenes,
    }

def run(script: dict, forced_style: str = "3d", total_duration: int = 10,
        max_scenes: int = 6, use_llm: bool = True) -> dict:
    if not use_llm:
        return _from_script(script, forced_style, total_duration, max_scenes)

    user = (
        f"Сценарий:\n{json.dumps(script, ensure_ascii=False)}\n\n"
        f"Стиль: {forced_style}\n"
        f"Длительность: {total_duration} сек\n"
        f"Макс. сцен: {max_scenes}\n"
        f"Сохрани visual/action каждой сцены."
    )
    plan = ask_json(SYSTEM, user, max_new_tokens=1400)
    plan["style"] = forced_style if forced_style in ("2d", "3d") else "3d"
    if "palette" not in plan or len(plan.get("palette", [])) < 3:
        plan["palette"] = ["#0f0f1a", "#e94560", "#ffffff", "#16213e"]

    scenes = plan.get("scenes") or []
    if not scenes:
        return _from_script(script, forced_style, total_duration, max_scenes)

    # Подтянуть visual/action из сценария, если режиссёр потерял
    script_scenes = script.get("scenes") or []
    for i, s in enumerate(scenes[:max_scenes]):
        if i < len(script_scenes):
            s.setdefault("visual", script_scenes[i].get("visual", "object"))
            s.setdefault("action", script_scenes[i].get("action", "idle"))
            if not s.get("narration"):
                s["narration"] = script_scenes[i].get("narration") or ""
        s["visual"] = s.get("visual") or "object"
        s["action"] = s.get("action") or "idle"
        s["duration"] = max(1.5, min(8.0, float(s.get("duration", 3.0))))

    plan["scenes"] = scenes[:max_scenes]
    return plan

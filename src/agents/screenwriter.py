from qwen_llm import ask_json
import re

SYSTEM = """Ты — сценарист коротких видео с НЕСКОЛЬКИМИ сценами.

Главное: разбей идею пользователя на последовательные сцены по действиям и объектам.

Примеры:
«человек приседает, встаёт и видит кошку» →
1) visual=person, action=squat
2) visual=person, action=stand
3) visual=cat, action=idle

«два человека машут» →
1) visual=two_people, action=wave

Правила:
1. Каждая сцена = один главный объект/группа + одно действие.
2. visual: person | two_people | cat | dog | object | world | abstract
   - two_people — если явно двое/пара/два человека в ОДНОЙ сцене
3. action: idle | walk | wave | jump | squat | stand | spin | bounce | look
4. narration — ТОЛЬКО речь персонажа (если есть). Не копируй весь промпт.
5. Если речи нет — narration = "".
6. Число сцен: по количеству действий в идее, но в пределах длительности:
   - 5–10 сек → 2–3
   - 11–20 сек → 3–5
   - 21–30 сек → 4–6
7. Язык = язык пользователя. Без мата.

Верни ТОЛЬКО JSON:
{
  "title": "...",
  "logline": "...",
  "scenes": [
    {
      "beat": "действие",
      "mood": "спокойный",
      "visual": "person",
      "action": "squat",
      "text": "Короткий заголовок",
      "narration": ""
    }
  ]
}"""

_SPLIT = re.compile(r"[,;]|\s+и\s+|\s+потом\s+|\s+затем\s+|\s+после\s+|\s+then\s+|\s+and\s+", re.I)

_VISUAL_MAP = [
    (r"2\s*человек|два\s*человек|двое|два\s*парень|две\s*девуш|пара\b|together|two\s*people|couple", "two_people"),
    (r"кошк|кот(?!е)|cat|kitten", "cat"),
    (r"собак|пёс|пес|dog", "dog"),
    (r"человек|челик|парень|девушк|персонаж|person|man|woman|guy|girl", "person"),
    (r"город|лес|море|космос|мир|city|forest|space", "world"),
    (r"неон|абстрак|энерг|portal|neon", "abstract"),
]

_ACTION_MAP = [
    (r"присед|сед|squat", "squat"),
    (r"вста[её]т|встал|stand\b|встань", "stand"),
    (r"маш|wave|приветств", "wave"),
    (r"прыг|jump", "jump"),
    (r"ид[её]т|ходь|walk|бежит", "walk"),
    (r"крут|spin|враща", "spin"),
    (r"смотр|вид[ие]|look|sees?", "look"),
]

def _guess_visual(chunk: str) -> str:
    t = chunk.lower()
    for pat, vis in _VISUAL_MAP:
        if re.search(pat, t):
            return vis
    return "object"

def _guess_action(chunk: str) -> str:
    t = chunk.lower()
    for pat, act in _ACTION_MAP:
        if re.search(pat, t):
            return act
    return "idle"

def heuristic_script(idea: str, total_duration: int = 10, max_scenes: int = 4) -> dict:
    parts = [p.strip() for p in _SPLIT.split(idea) if p and p.strip()]
    if not parts:
        parts = [idea.strip() or "сцена"]
    parts = parts[:max_scenes]
    scenes = []
    for p in parts:
        scenes.append({
            "beat": "действие",
            "mood": "нейтральный",
            "visual": _guess_visual(p),
            "action": _guess_action(p),
            "text": p[:40],
            "narration": "",
        })
    if len(scenes) == 1:
        t = idea.lower()
        has_p = bool(re.search(r"человек|челик|person|парень|девушк", t))
        has_c = bool(re.search(r"кошк|кот|cat", t))
        has_two = bool(re.search(r"2\s*человек|два\s*человек|двое|two\s*people|couple", t))
        if has_two:
            scenes = [{
                "beat": "1", "mood": "", "visual": "two_people",
                "action": _guess_action(idea), "text": "Двое", "narration": "",
            }]
        elif has_p and has_c:
            scenes = [
                {"beat": "1", "mood": "", "visual": "person", "action": _guess_action(idea), "text": "Человек", "narration": ""},
                {"beat": "2", "mood": "", "visual": "cat", "action": "idle", "text": "Кошка", "narration": ""},
            ]
    return {"title": idea[:40], "logline": idea[:80], "scenes": scenes}

def run(idea: str, total_duration: int = 10, max_scenes: int = 6, use_llm: bool = True) -> dict:
    if not use_llm:
        return heuristic_script(idea, total_duration, max_scenes)

    user = (
        f"Идея: {idea}\n"
        f"Длительность: {total_duration} сек.\n"
        f"Максимум сцен: {max_scenes}.\n"
        f"Разбей на сцены. Если двое в одной сцене — visual=two_people."
    )
    data = ask_json(SYSTEM, user, max_new_tokens=1200)
    scenes = data.get("scenes") or []
    if not scenes:
        return heuristic_script(idea, total_duration, max_scenes)
    data["scenes"] = scenes[:max_scenes]
    return data

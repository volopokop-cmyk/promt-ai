import json
from qwen_llm import ask_json

SYSTEM = """Ты — режиссёр анимационного видео. На вход — сценарий (JSON).
Составь технический план съёмки.

Определи:
1. style: "3d" для полёта/космоса/объёма/вращения; "2d" для эмоций, типографики, инфографики, юмора.
2. palette: 4 HEX-цвета [фон, акцент, текст, деталь].
3. font: "sans"|"serif"|"mono".
4. camera: "static"|"zoom_in"|"zoom_out"|"pan_left"|"pan_right"|"orbit".
5. scenes: для каждой — text (до 8 слов), duration (2.0–6.0), camera_move, transition ("cut"|"fade"|"slide"), lighting ("day"|"night"|"neon"|"soft"), narration (из сценария).

Верни СТРОГО JSON без markdown:
{"style":"2d|3d","palette":["#...","#...","#...","#..."],"font":"sans","camera":"zoom_in",
 "scenes":[{"text":"...","duration":3.5,"camera_move":"zoom_in","transition":"fade",
            "lighting":"neon","narration":"..."}]}"""

def run(script: dict) -> dict:
    plan = ask_json(SYSTEM, json.dumps(script, ensure_ascii=False), max_new_tokens=1024)
    assert plan["style"] in ("2d", "3d")
    assert len(plan["palette"]) >= 3
    for s in plan["scenes"]:
        s["duration"] = max(2.0, min(6.0, float(s.get("duration", 3.0))))
    return plan

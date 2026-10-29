import asyncio
import json
import shutil
from pathlib import Path

from telegram import get_updates, send_message, send_video
from agents import screenwriter, director, artist, editor
from qwen_tts import synth
from watermark import inject

STATE = Path("state/offset.json")
WORK = Path("work")
OUT = Path("out")
MAX_UPDATES = 2

def load_offset():
    if STATE.exists():
        return json.loads(STATE.read_text()).get("offset")
    return None

def save_offset(offset):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({"offset": offset}))

def pipeline(idea: str, chat_id: int):
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(); OUT.mkdir(exist_ok=True)

    send_message(chat_id, "✍️ Сценарист пишет историю…")
    script = screenwriter.run(idea)

    send_message(chat_id, f"🎬 Режиссёр строит план: {script.get('title','')}")
    plan = director.run(script)

    send_message(chat_id, f"🎨 Художник рисует сцены ({plan['style'].upper()})…")
    scenes_html = []
    for sc in plan["scenes"]:
        html = artist.run(sc, plan)
        html = inject(html, float(sc["duration"]))
        scenes_html.append((html, sc["duration"]))

    send_message(chat_id, "🔊 Озвучиваю…")
    audio_parts = []
    for i, sc in enumerate(plan["scenes"]):
        p = WORK / f"a_{i}.wav"
        mood = script["scenes"][i].get("mood") if i < len(script["scenes"]) else None
        instruct = f"говори {mood}" if mood else None
        synth(sc["narration"], str(p), instruct=instruct)
        audio_parts.append(p)

    send_message(chat_id, "🎥 Рендерю кадры…")
    from render import render_all
    asyncio.run(render_all(scenes_html, WORK / "frames"))

    send_message(chat_id, "✂️ Монтаж…")
    mp4 = OUT / "video.mp4"
    editor.run(WORK / "frames", audio_parts, mp4)

    send_message(chat_id, "📤 Отправляю…")
    send_video(chat_id, str(mp4), caption=script.get("title", idea)[:200])

def main():
    offset = load_offset()
    updates = get_updates(offset)
    if not updates:
        print("нет сообщений"); return

    processed = 0
    for upd in updates:
        offset = upd["update_id"] + 1
        msg = upd.get("message")
        if not msg or "text" not in msg:
            continue
        chat_id, text = msg["chat"]["id"], msg["text"]
        if text.startswith("/start"):
            send_message(chat_id,
                "Привет! Я promt bot. Пришли идею — сделаю видео (2D или 3D).")
            continue
        try:
            pipeline(text, chat_id)
            processed += 1
        except Exception as e:
            send_message(chat_id, f"❌ {type(e).__name__}: {e}")
        if processed >= MAX_UPDATES:
            break
    save_offset(offset)

if __name__ == "__main__":
    main()

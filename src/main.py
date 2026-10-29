import asyncio
import json
import shutil
import time
from pathlib import Path
from collections import deque

from telegram import get_updates, send_message, send_video
from agents import screenwriter, director, artist, editor
from tts_engine import synth
from watermark import inject

STATE = Path("state/offset.json")
WORK = Path("work")
OUT = Path("out")

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
    print("Бот запущен. Слушаю сообщения и формирую очередь...")
    start_time = time.time()
    offset = load_offset()
    
    # Наша очередь задач (сообщений)
    queue = deque()

    # Работаем 5 часов 50 минут
    while time.time() - start_time < 21000:
        try:
            # 1. Проверяем новые сообщения (ждем до 10 секунд)
            updates = get_updates(offset, timeout=10)
            
            for upd in updates:
                offset = upd["update_id"] + 1
                save_offset(offset)
                
                msg = upd.get("message")
                if not msg or "text" not in msg:
                    continue
                    
                chat_id, text = msg["chat"]["id"], msg["text"]
                
                if text.startswith("/start"):
                    send_message(chat_id, "Привет! Я prompt bot. Пришли идею — сделаю видео (2D или 3D).")
                    continue
                
                # Добавляем в очередь и сразу отвечаем, чтобы человек не ждал
                queue.append({"chat_id": chat_id, "idea": text})
                send_message(chat_id, f"🎬 Принято в очередь! Ты {len(queue)}-й. Начинаю генерацию, как только освобожусь.")
            
            # 2. Если есть задачи в очереди и мы не заняты — берем одну
            if queue:
                task = queue.popleft()
                try:
                    pipeline(task["idea"], task["chat_id"])
                except Exception as e:
                    send_message(task["chat_id"], f"❌ Ошибка генерации: {type(e).__name__}: {e}")
                    
        except Exception as e:
            print(f"Ошибка сети: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

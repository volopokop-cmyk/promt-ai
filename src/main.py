import asyncio
import json
import shutil
import time
import threading
import re
from pathlib import Path
from collections import deque

from telegram import get_updates, send_message, send_video
from agents import screenwriter, director, artist, editor
from tts_engine import synth
from watermark import inject

STATE = Path("state/offset.json")
WORK = Path("work")
OUT = Path("out")

queue = deque()
queue_lock = threading.Lock()

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

    # 1. Узнаем формат (9:16 или 16:9)
    is_vertical = "9:16" in idea or "вертикальн" in idea.lower()
    
    # 2. Узнаем длительность
    duration_match = re.search(r'(\d+)\s*(сек|секунд)', idea.lower())
    total_duration = int(duration_match.group(1)) if duration_match else 15
    total_duration = max(3, min(60, total_duration))

    # 3. Определяем голос и язык из текста
    idea_lower = idea.lower()
    if "мужской" in idea_lower or "мужчина" in idea_lower or "парень" in idea_lower:
        selected_speaker = "Ryan" # Мужской голос
    else:
        selected_speaker = "Vivian" # Женский голос по умолчанию

    if "англ" in idea_lower or "english" in idea_lower:
        selected_language = "English"
    elif "китай" in idea_lower or "chinese" in idea_lower:
        selected_language = "Chinese"
    elif "япон" in idea_lower or "japanese" in idea_lower:
        selected_language = "Japanese"
    else:
        selected_language = "Russian"

    send_message(chat_id, "✍️ Сценарист пишет историю…")
    script = screenwriter.run(idea)

    send_message(chat_id, f"🎬 Режиссёр строит план: {script.get('title','')}")
    plan = director.run(script)

    plan["scenes"] = plan["scenes"][:3]
    duration_per_scene = total_duration / len(plan["scenes"])

    send_message(chat_id, f"🎨 Художник рисует сцены ({plan['style'].upper()})…")
    scenes_html = []
    for sc in plan["scenes"]:
        html = artist.run(sc, plan, original_idea=idea)
        html = inject(html, float(sc["duration"]))
        scenes_html.append((html, sc["duration"]))

    send_message(chat_id, f"🔊 Озвучиваю ({selected_language}, {selected_speaker})…")
    audio_parts = []
    for i, sc in enumerate(plan["scenes"]):
        p = WORK / f"a_{i}.wav"
        clean_text = script["scenes"][i].get("narration", "") if i < len(script["scenes"]) else sc.get("text", "")
        
        if not clean_text.strip():
            audio_parts.append(None)
            continue
            
        mood = script["scenes"][i].get("mood") if i < len(script["scenes"]) else None
        instruct = f"говори {mood}" if mood else None
        
        synth(clean_text, str(p), instruct=instruct, speaker=selected_speaker, language=selected_language)
        audio_parts.append(p)

    send_message(chat_id, "🎥 Рендерю кадры…")
    from render import render_all
    asyncio.run(render_all(scenes_html, WORK / "frames", is_vertical))

    send_message(chat_id, "✂️ Монтаж…")
    mp4 = OUT / "video.mp4"
    editor.run(WORK / "frames", audio_parts, mp4)

    send_message(chat_id, "📤 Отправляю…")
    send_video(chat_id, str(mp4), caption=script.get("title", idea)[:200])

def listener():
    offset = load_offset()
    while True:
        try:
            updates = get_updates(offset, timeout=10)
            for upd in updates:
                offset = upd["update_id"] + 1
                save_offset(offset)
                
                msg = upd.get("message")
                if not msg or "text" not in msg:
                    continue
                    
                chat_id, text = msg["chat"]["id"], msg["text"]
                
                if text.startswith("/start"):
                    send_message(chat_id, "Привет! Я prompt bot. Пришли идею — сделаю видео. Укажи формат (9:16 или 16:9), длительность и голос (мужской/женский).")
                    continue
                
                with queue_lock:
                    queue.append({"chat_id": chat_id, "idea": text})
                    pos = len(queue)
                send_message(chat_id, f"🎬 Принято в очередь! Ты {pos}-й. Начинаю генерацию, как только освобожусь.")
        except Exception as e:
            print(f"Ошибка в слушателе: {e}")
            time.sleep(5)

def worker():
    print("Генератор запущен...")
    while True:
        task = None
        with queue_lock:
            if queue:
                task = queue.popleft()
                
        if task:
            try:
                pipeline(task["idea"], task["chat_id"])
            except Exception as e:
                send_message(task["chat_id"], f"❌ Ошибка генерации: {type(e).__name__}: {e}")
        else:
            time.sleep(2)

def main():
    print("Бот запущен. Слушатель и генератор в работе...")
    start_time = time.time()
    t = threading.Thread(target=listener, daemon=True)
    t.start()
    
    while time.time() - start_time < 21000:
        worker()

if __name__ == "__main__":
    main()

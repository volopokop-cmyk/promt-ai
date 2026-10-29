import asyncio
import json
import shutil
import time
import threading
from pathlib import Path
from collections import deque

from telegram import get_updates, send_message, send_video
from agents import screenwriter, director, artist, editor
from tts_engine import synth
from watermark import inject

STATE = Path("state/offset.json")
WORK = Path("work")
OUT = Path("out")

# Глобальная очередь задач
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
        
        # Берем чистый текст для озвучки из сценария
        if i < len(script["scenes"]):
            # Если сценарист написал текст в narration — берем его
            clean_text = script["scenes"][i].get("narration", "")
        else:
            clean_text = ""
            
        # Если сценарист забыл написать текст, берем текст с экрана
        if not clean_text:
            clean_text = sc.get("text", "")
            
        # Если вообще пусто — пропускаем генерацию голоса для этой сцены
        if not clean_text.strip():
            audio_parts.append(None)
            continue
            
        mood = script["scenes"][i].get("mood") if i < len(script["scenes"]) else None
        instruct = f"говори {mood}" if mood else None
        
        print(f"Озвучиваю текст: '{clean_text}'") # Выведем в логи, что именно он говорит
        synth(clean_text, str(p), instruct=instruct)
        audio_parts.append(p)

    send_message(chat_id, "🎥 Рендерю кадры…")
    from render import render_all
    asyncio.run(render_all(scenes_html, WORK / "frames"))

    send_message(chat_id, "✂️ Монтаж…")
    mp4 = OUT / "video.mp4"
    editor.run(WORK / "frames", audio_parts, mp4)

    send_message(chat_id, "📤 Отправляю…")
    send_video(chat_id, str(mp4), caption=script.get("title", idea)[:200])

# ЭТА ФУНКЦИЯ РАБОТАЕТ В ФОНЕ (Слушатель)
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
                    send_message(chat_id, "Привет! Я prompt bot. Пришли идею — сделаю видео (2D или 3D).")
                    continue
                
                # Мгновенно отвечаем и кидаем в очередь
                with queue_lock:
                    queue.append({"chat_id": chat_id, "idea": text})
                    pos = len(queue)
                send_message(chat_id, f"🎬 Принято в очередь! Ты {pos}-й. Начинаю генерацию, как только освобожусь.")
        except Exception as e:
            print(f"Ошибка в слушателе: {e}")
            time.sleep(5)

# ЭТА ФУНКЦИЯ РАБОТАЕТ В ОСНОВНОМ ПОТОКЕ (Генератор)
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
            time.sleep(2) # Если очередь пуста — отдыхаем 2 секунды

def main():
    print("Бот запущен. Слушатель и генератор в работе...")
    start_time = time.time()
    
    # Запускаем слушателя в фоновом потоке
    t = threading.Thread(target=listener, daemon=True)
    t.start()
    
    # Работаем 5 часов 50 минут
    while time.time() - start_time < 21000:
        worker() # Генератор крутится в основном потоке

if __name__ == "__main__":
    main()

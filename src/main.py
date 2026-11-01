import asyncio
import json
import shutil
import time
import threading
import re
from pathlib import Path
from collections import deque

from telegram import get_updates, send_message, send_video, answer_callback
from agents import screenwriter, director, artist, editor
from tts_engine import synth
from watermark import inject

STATE = Path("state/offset.json")
WORK = Path("work")
OUT = Path("out")

queue = deque()
queue_lock = threading.Lock()
user_settings = {} # Здесь храним выбор пользователей

def load_offset():
    if STATE.exists():
        return json.loads(STATE.read_text()).get("offset")
    return None

def save_offset(offset):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({"offset": offset}))

# Функция для отправки меню
def send_menu(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "📱 9:16 (Shorts)", "callback_data": "fmt_9_16"}, {"text": "🖥 16:9 (YouTube)", "callback_data": "fmt_16_9"}],
            [{"text": "⏱ 5 сек", "callback_data": "dur_5"}, {"text": "⏱ 10 сек", "callback_data": "dur_10"}, {"text": "⏱ 15 сек", "callback_data": "dur_15"}],
            [{"text": "🗣 Мужской", "callback_data": "voice_male"}, {"text": "🗣 Женский", "callback_data": "voice_female"}],
            [{"text": "🇷🇺 RU", "callback_data": "lang_ru"}, {"text": "🇬🇧 EN", "callback_data": "lang_en"}],
            [{"text": "✅ Готово, я напишу идею", "callback_data": "done"}]
        ]
    }
    send_message(chat_id, "⚙️ Настрой генерацию видео с помощью кнопок ниже, а затем нажми 'Готово' и напиши идею.", reply_markup=keyboard)

def pipeline(idea: str, chat_id: int, settings: dict, username: str = ""):
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(); OUT.mkdir(exist_ok=True)

    is_vertical = settings.get("format", "9:16") == "9:16"
    total_duration = settings.get("duration", 10)
    
    selected_speaker = settings.get("speaker", "Vivian")
    selected_language = settings.get("language", "Russian")

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
        html = inject(html, float(sc["duration"]), username=username)
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
                
                # Ловим нажатия на кнопки
                if "callback_query" in upd:
                    cb = upd["callback_query"]
                    cb_id = cb["id"]
                    chat_id = cb["message"]["chat"]["id"]
                    data = cb["data"]
                    
                    answer_callback(cb_id) # Убираем часики на кнопке
                    
                    if chat_id not in user_settings:
                        user_settings[chat_id] = {"format": "9:16", "duration": 10, "speaker": "Vivian", "language": "Russian", "ready": False}
                        
                    if data.startswith("fmt_"):
                        user_settings[chat_id]["format"] = "9:16" if "9_16" in data else "16:9"
                    elif data.startswith("dur_"):
                        user_settings[chat_id]["duration"] = int(data.split("_")[1])
                    elif data.startswith("voice_"):
                        user_settings[chat_id]["speaker"] = "Ryan" if "male" in data else "Vivian"
                    elif data.startswith("lang_"):
                        user_settings[chat_id]["language"] = "Russian" if "ru" in data else "English"
                    elif data == "done":
                        user_settings[chat_id]["ready"] = True
                        send_message(chat_id, "✅ Настройки сохранены! Теперь напиши идею для видео.")
                        
                    continue
                
                # Ловим обычные сообщения
                msg = upd.get("message")
                if not msg or "text" not in msg:
                    continue
                    
                chat_id = msg["chat"]["id"]
                text = msg["text"]
                username = msg.get("from", {}).get("username", "")
                
                if text.startswith("/start"):
                    send_menu(chat_id)
                    continue
                
                # Проверяем, готов ли пользователь
                settings = user_settings.get(chat_id)
                if not settings or not settings.get("ready"):
                    send_message(chat_id, "⚠️ Сначала выбери настройки в меню (нажми /start, если его нет).")
                    continue
                
                # Сбрасываем готовность для следующего видео
                settings["ready"] = False
                
                with queue_lock:
                    queue.append({"chat_id": chat_id, "idea": text, "username": username, "settings": settings.copy()})
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
                pipeline(task["idea"], task["chat_id"], task["settings"], task["username"])
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

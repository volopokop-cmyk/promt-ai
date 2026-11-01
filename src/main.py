import asyncio
import json
import shutil
import time
import threading
import re
import os
import requests
from pathlib import Path
from collections import deque

from telegram import get_updates, send_message, send_video, answer_callback, edit_message_text
from agents import screenwriter, director, artist, editor
from tts_engine import synth
from watermark import inject

STATE = Path("state/offset.json")
WORK = Path("work")
OUT = Path("out")

queue = deque()
queue_lock = threading.Lock()
user_settings = {} 

def load_offset():
    if STATE.exists():
        return json.loads(STATE.read_text()).get("offset")
    return None

def save_offset(offset):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({"offset": offset}))

def get_menu(settings):
    f = settings.get("format", "9:16")
    d = settings.get("duration", 10)
    s = settings.get("speaker", "Vivian")
    l = settings.get("language", "Russian")

    keyboard = {
        "inline_keyboard": [
            [
                {"text": f"📱 9:16 (Shorts) {'✅' if f == '9:16' else ''}", "callback_data": "fmt_9_16", "style": "success" if f == '9:16' else "default"}, 
                {"text": f"🖥 16:9 (YouTube) {'✅' if f == '16:9' else ''}", "callback_data": "fmt_16_9", "style": "success" if f == '16:9' else "default"}
            ],
            [
                {"text": f"⏱ 5 сек {'✅' if d == 5 else ''}", "callback_data": "dur_5", "style": "success" if d == 5 else "default"}, 
                {"text": f"⏱ 10 сек {'✅' if d == 10 else ''}", "callback_data": "dur_10", "style": "success" if d == 10 else "default"}, 
                {"text": f"⏱ 15 сек {'✅' if d == 15 else ''}", "callback_data": "dur_15", "style": "success" if d == 15 else "default"}
            ],
            [
                {"text": f"🗣 Мужской {'✅' if s == 'Ryan' else ''}", "callback_data": "voice_male", "style": "success" if s == 'Ryan' else "default"}, 
                {"text": f"🗣 Женский {'✅' if s == 'Vivian' else ''}", "callback_data": "voice_female", "style": "success" if s == 'Vivian' else "default"}
            ],
            [
                {"text": f"🇷🇺 RU {'✅' if l == 'Russian' else ''}", "callback_data": "lang_ru", "style": "success" if l == 'Russian' else "default"}, 
                {"text": f"🇬🇧 EN {'✅' if l == 'English' else ''}", "callback_data": "lang_en", "style": "success" if l == 'English' else "default"}
            ],
            [
                {"text": "🔁 Повторить видео", "callback_data": "mode_repeat", "style": "primary"}
            ],
            [
                {"text": "✅ Готово, я напишу идею", "callback_data": "done", "style": "success"}
            ]
        ]
    }
    return keyboard

def progress_updater(chat_id, message_id, is_done_flag):
    percent = 0
    while percent < 99 and not is_done_flag[0]:
        time.sleep(6) 
        percent += 1
        bar = "█" * (percent // 10) + "░" * (10 - percent // 10)
        text = f"⏳ Генерация видео...\n\n[{bar}] {percent}%"
        try:
            edit_message_text(chat_id, message_id, text)
        except:
            pass

def pipeline(idea: str, chat_id: int, settings: dict, username: str = ""):
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(); OUT.mkdir(exist_ok=True)

    is_vertical = settings.get("format", "9:16") == "9:16"
    total_duration = settings.get("duration", 10)
    selected_speaker = settings.get("speaker", "Vivian")
    selected_language = settings.get("language", "Russian")

    msg = requests.post(f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage", json={"chat_id": chat_id, "text": "⏳ Генерация видео...\n\n[░░░░░░░░░░] 0%"}).json()
    message_id = msg["result"]["message_id"]
    
    is_done = [False]
    t = threading.Thread(target=progress_updater, args=(chat_id, message_id, is_done), daemon=True)
    t.start()

    try:
        script = screenwriter.run(idea)
        plan = director.run(script)
        plan["scenes"] = plan["scenes"][:3]
        duration_per_scene = total_duration / len(plan["scenes"])

        scenes_html = []
        for sc in plan["scenes"]:
            html = artist.run(sc, plan, original_idea=idea)
            html = inject(html, float(sc["duration"]), username=username)
            scenes_html.append((html, sc["duration"]))

        audio_parts = []
        for i, sc in enumerate(plan["scenes"]):
            p = WORK / f"a_{i}.wav"
            clean_text = script["scenes"][i].get("narration", "") if i < len(script["scenes"]) else sc.get("text", "")
            
            if not clean_text.strip():
                os.system(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 1 {p}")
                audio_parts.append(p)
                continue
                
            synth(clean_text, str(p), speaker=selected_speaker, language=selected_language)
            audio_parts.append(p)

        from render import render_all
        asyncio.run(render_all(scenes_html, WORK / "frames", is_vertical))

        mp4 = OUT / "video.mp4"
        editor.run(WORK / "frames", audio_parts, mp4)

        is_done[0] = True 
        edit_message_text(chat_id, message_id, "✅ Видео готово! Отправляю...")
        send_video(chat_id, str(mp4), caption=script.get("title", idea)[:200])
        
    except Exception as e:
        is_done[0] = True
        edit_message_text(chat_id, message_id, f"❌ Ошибка: {type(e).__name__}: {e}")

def listener():
    offset = load_offset()
    while True:
        try:
            updates = get_updates(offset, timeout=10)
            for upd in updates:
                offset = upd["update_id"] + 1
                save_offset(offset)
                
                if "callback_query" in upd:
                    cb = upd["callback_query"]
                    cb_id = cb["id"]
                    chat_id = cb["message"]["chat"]["id"]
                    message_id = cb["message"]["message_id"]
                    data = cb["data"]
                    
                    answer_callback(cb_id)
                    
                    if chat_id not in user_settings:
                        user_settings[chat_id] = {"format": "9:16", "duration": 10, "speaker": "Vivian", "language": "Russian", "ready": False, "mode": "text"}
                    
                    settings = user_settings[chat_id]
                    
                    if data.startswith("fmt_"):
                        settings["format"] = "9:16" if "9_16" in data else "16:9"
                    elif data.startswith("dur_"):
                        settings["duration"] = int(data.split("_")[1])
                    elif data.startswith("voice_"):
                        settings["speaker"] = "Ryan" if "male" in data else "Vivian"
                    elif data.startswith("lang_"):
                        settings["language"] = "Russian" if "ru" in data else "English"
                    elif data == "mode_repeat":
                        settings["mode"] = "repeat"
                        send_message(chat_id, "📹 Отправь видео и напиши в подписи, что на нём происходит (например: 'толстый кот машет лапой').")
                        continue
                    elif data == "done":
                        settings["ready"] = True
                        settings["mode"] = "text"
                        send_message(chat_id, "✅ Настройки сохранены! Теперь напиши идею для видео.")
                        continue
                        
                    new_keyboard = get_menu(settings)
                    edit_message_text(chat_id, message_id, "⚙️ Настрой генерацию видео с помощью кнопок ниже, а затем нажми 'Готово' и напиши идею.", reply_markup=new_keyboard)
                    continue
                
                msg = upd.get("message")
                if not msg:
                    continue
                
                chat_id = msg["chat"]["id"]
                username = msg.get("from", {}).get("username", "")
                settings = user_settings.get(chat_id, {})

                # Обработка видео
                if "video" in msg:
                    caption = msg.get("caption", "")
                    if not caption:
                        send_message(chat_id, "⚠️ Пожалуйста, добавь к видео текстовое описание (что на нем происходит), чтобы я мог это анимировать.")
                        continue
                    
                    if not settings or settings.get("mode") != "repeat":
                         send_message(chat_id, "⚠️ Сначала нажми 'Повторить видео' в меню (/start).")
                         continue
                         
                    # Запускаем генерацию по описанию из подписи
                    settings["ready"] = False
                    settings["mode"] = "text"
                    with queue_lock:
                        queue.append({"chat_id": chat_id, "idea": caption, "username": username, "settings": settings.copy()})
                        pos = len(queue)
                    send_message(chat_id, f"🎬 Принято в очередь! Ты {pos}-й. Начинаю генерацию, как только освобожусь.")
                    continue

                # Обработка текста
                if "text" not in msg:
                    continue
                    
                text = msg["text"]
                
                if text.startswith("/start"):
                    if chat_id not in user_settings:
                        user_settings[chat_id] = {"format": "9:16", "duration": 10, "speaker": "Vivian", "language": "Russian", "ready": False, "mode": "text"}
                    menu = get_menu(user_settings[chat_id])
                    send_message(chat_id, "⚙️ Настрой генерацию видео с помощью кнопок ниже, а затем нажми 'Готово' и напиши идею.", reply_markup=menu)
                    continue
                
                if not settings or not settings.get("ready"):
                    send_message(chat_id, "⚠️ Сначала выбери настройки в меню (нажми /start, если его нет).")
                    continue
                
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

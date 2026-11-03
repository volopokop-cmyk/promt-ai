import asyncio
import json
import shutil
import time
import threading
import os
import requests
from pathlib import Path
from collections import deque

from telegram import get_updates, send_message, send_video, answer_callback, edit_message_text
from agents import screenwriter, director, artist, editor
from tts_engine import synth
from watermark import inject
from lipsync import mouth_curve_from_wav

STATE = Path("state/offset.json")
WORK = Path("work")
OUT = Path("out")

queue = deque()
queue_lock = threading.Lock()
user_settings = {}

RUN_SECONDS = 6 * 3600 - 120

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
    st = settings.get("style", "3d")

    keyboard = {
        "inline_keyboard": [
            [
                {"text": f"📱 9:16 {'✅' if f == '9:16' else ''}", "callback_data": "fmt_9_16"},
                {"text": f"🖥 16:9 {'✅' if f == '16:9' else ''}", "callback_data": "fmt_16_9"}
            ],
            [
                {"text": f"⏱ 5с {'✅' if d == 5 else ''}", "callback_data": "dur_5"},
                {"text": f"⏱ 10с {'✅' if d == 10 else ''}", "callback_data": "dur_10"},
                {"text": f"⏱ 15с {'✅' if d == 15 else ''}", "callback_data": "dur_15"},
                {"text": f"⏱ 20с {'✅' if d == 20 else ''}", "callback_data": "dur_20"},
                {"text": f"⏱ 30с {'✅' if d == 30 else ''}", "callback_data": "dur_30"}
            ],
            [
                {"text": f"🎨 2D {'✅' if st == '2d' else ''}", "callback_data": "style_2d"},
                {"text": f"🧊 3D {'✅' if st == '3d' else ''}", "callback_data": "style_3d"}
            ],
            [
                {"text": f"🗣 Мужской {'✅' if s == 'Ryan' else ''}", "callback_data": "voice_male"},
                {"text": f"🗣 Женский {'✅' if s == 'Vivian' else ''}", "callback_data": "voice_female"}
            ],
            [
                {"text": f"🇷🇺 RU {'✅' if l == 'Russian' else ''}", "callback_data": "lang_ru"},
                {"text": f"🇬🇧 EN {'✅' if l == 'English' else ''}", "callback_data": "lang_en"}
            ],
            [{"text": "🔁 Повторить видео", "callback_data": "mode_repeat"}],
            [{"text": "✅ Готово — напишу идею", "callback_data": "done"}]
        ]
    }
    return keyboard

def progress_updater(chat_id, message_id, is_done_flag):
    percent = 0
    while percent < 99 and not is_done_flag[0]:
        time.sleep(5)
        percent = min(99, percent + 2)
        bar = "█" * (percent // 10) + "░" * (10 - percent // 10)
        try:
            edit_message_text(chat_id, message_id, f"⏳ Генерация видео...\n\n[{bar}] {percent}%")
        except Exception:
            pass

def pipeline(idea: str, chat_id: int, settings: dict, username: str = ""):
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    OUT.mkdir(exist_ok=True)

    is_vertical = settings.get("format", "9:16") == "9:16"
    total_duration = max(5, min(30, int(settings.get("duration", 10))))
    selected_speaker = settings.get("speaker", "Vivian")
    selected_language = settings.get("language", "Russian")
    forced_style = settings.get("style", "3d")

    msg = requests.post(
        f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage",
        json={"chat_id": chat_id, "text": "⏳ Генерация видео...\n\n[░░░░░░░░░░] 0%"}
    ).json()
    message_id = msg["result"]["message_id"]

    is_done = [False]
    t = threading.Thread(target=progress_updater, args=(chat_id, message_id, is_done), daemon=True)
    t.start()

    try:
        script = screenwriter.run(idea, total_duration=total_duration)
        plan = director.run(script, forced_style=forced_style, total_duration=total_duration)

        n_scenes = len(plan["scenes"])
        if n_scenes == 0:
            raise ValueError("Режиссёр не создал ни одной сцены")

        script_scenes = script.get("scenes", [])
        for i, sc in enumerate(plan["scenes"]):
            if i < len(script_scenes):
                narr = (script_scenes[i].get("narration") or "").strip()
                if narr:
                    sc["narration"] = narr
            sc["duration"] = max(2.0, min(8.0, float(sc.get("duration", total_duration / n_scenes))))

        current_sum = sum(sc["duration"] for sc in plan["scenes"])
        if current_sum > 0:
            scale = total_duration / current_sum
            for sc in plan["scenes"]:
                sc["duration"] = round(sc["duration"] * scale, 2)

        # 1) Сначала озвучка — чтобы построить липсинг по реальному аудио
        audio_parts = []
        lip_curves = []
        for i, sc in enumerate(plan["scenes"]):
            p = WORK / f"a_{i}.wav"
            clean_text = (sc.get("narration") or "").strip()
            if not clean_text and i < len(script_scenes):
                clean_text = (script_scenes[i].get("narration") or "").strip()
            if not clean_text:
                clean_text = (sc.get("text") or "").strip()

            if not clean_text:
                os.system(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t {sc['duration']} {p}")
            else:
                synth(clean_text, str(p), speaker=selected_speaker, language=selected_language)

            audio_parts.append(p)
            # Кривая рта по амплитуде WAV
            lip_curves.append(mouth_curve_from_wav(p, fps=15, duration=float(sc["duration"])))

        # 2) Рисуем сцены с липсингом
        scenes_html = []
        for i, sc in enumerate(plan["scenes"]):
            html = artist.run(sc, plan, original_idea=idea, lip_curve=lip_curves[i])
            html = inject(html, float(sc["duration"]), username=username)
            scenes_html.append((html, sc["duration"]))

        # 3) Рендер кадров
        from render import render_all
        asyncio.run(render_all(scenes_html, WORK / "frames", is_vertical))

        # 4) Монтаж
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
                        user_settings[chat_id] = {
                            "format": "9:16", "duration": 10, "speaker": "Vivian",
                            "language": "Russian", "style": "3d", "ready": False, "mode": "text"
                        }
                    settings = user_settings[chat_id]

                    if data.startswith("fmt_"):
                        settings["format"] = "9:16" if "9_16" in data else "16:9"
                    elif data.startswith("dur_"):
                        settings["duration"] = int(data.split("_")[1])
                    elif data.startswith("style_"):
                        settings["style"] = "2d" if "2d" in data else "3d"
                    elif data.startswith("voice_"):
                        settings["speaker"] = "Ryan" if "male" in data else "Vivian"
                    elif data.startswith("lang_"):
                        settings["language"] = "Russian" if "ru" in data else "English"
                    elif data == "mode_repeat":
                        settings["mode"] = "repeat"
                        send_message(chat_id, "📹 Отправь видео и напиши в подписи, что на нём происходит.")
                        continue
                    elif data == "done":
                        settings["ready"] = True
                        settings["mode"] = "text"
                        send_message(chat_id, "✅ Настройки сохранены! Теперь напиши идею для видео.")
                        continue

                    edit_message_text(
                        chat_id, message_id,
                        "⚙️ Настрой генерацию:\n• формат • длительность • 2D/3D • голос • язык\n\nПотом нажми «Готово» и напиши идею.",
                        reply_markup=get_menu(settings)
                    )
                    continue

                msg = upd.get("message")
                if not msg:
                    continue

                chat_id = msg["chat"]["id"]
                username = msg.get("from", {}).get("username", "")
                settings = user_settings.get(chat_id, {})

                if "video" in msg:
                    caption = msg.get("caption", "")
                    if not caption:
                        send_message(chat_id, "⚠️ Добавь к видео текстовое описание.")
                        continue
                    if not settings or settings.get("mode") != "repeat":
                        send_message(chat_id, "⚠️ Сначала нажми «Повторить видео» в меню (/start).")
                        continue
                    settings["ready"] = False
                    settings["mode"] = "text"
                    with queue_lock:
                        queue.append({"chat_id": chat_id, "idea": caption, "username": username, "settings": settings.copy()})
                        pos = len(queue)
                    send_message(chat_id, f"🎬 Принято в очередь! Ты {pos}-й.")
                    continue

                if "text" not in msg:
                    continue
                text = msg["text"]

                if text.startswith("/start"):
                    if chat_id not in user_settings:
                        user_settings[chat_id] = {
                            "format": "9:16", "duration": 10, "speaker": "Vivian",
                            "language": "Russian", "style": "3d", "ready": False, "mode": "text"
                        }
                    send_message(
                        chat_id,
                        "⚙️ Настрой генерацию:\n• формат • длительность • 2D/3D • голос • язык\n\nПотом нажми «Готово» и напиши идею.",
                        reply_markup=get_menu(user_settings[chat_id])
                    )
                    continue

                if not settings or not settings.get("ready"):
                    send_message(chat_id, "⚠️ Сначала выбери настройки в меню (нажми /start).")
                    continue

                settings["ready"] = False
                with queue_lock:
                    queue.append({"chat_id": chat_id, "idea": text, "username": username, "settings": settings.copy()})
                    pos = len(queue)
                send_message(chat_id, f"🎬 Принято в очередь! Ты {pos}-й.")

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
                pipeline(task["idea"], task["chat_id"], task["settings"], task.get("username", ""))
            except Exception as e:
                send_message(task["chat_id"], f"❌ Ошибка генерации: {type(e).__name__}: {e}")
        else:
            time.sleep(2)

def main():
    print(f"Бот запущен. Работает до {RUN_SECONDS // 3600} часов...")
    start_time = time.time()
    t = threading.Thread(target=listener, daemon=True)
    t.start()
    while time.time() - start_time < RUN_SECONDS:
        worker()
    print("Время работы истекло. Выход.")

if __name__ == "__main__":
    main()

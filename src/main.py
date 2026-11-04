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
from speech import build_scene_lines
from modes import get_mode, MODES

STATE = Path("state/offset.json")
WORK = Path("work")
OUT = Path("out")

queue = deque()
queue_lock = threading.Lock()
user_settings = {}

RUN_SECONDS = 6 * 3600 - 120

def _bot_id() -> int | None:
    try:
        return int(os.environ.get("BOT_TOKEN", "0").split(":")[0])
    except Exception:
        return None

BOT_ID = None

def get_bot_id() -> int | None:
    global BOT_ID
    if BOT_ID is None:
        BOT_ID = _bot_id()
    return BOT_ID

def is_group_chat(msg: dict) -> bool:
    t = (msg.get("chat") or {}).get("type", "private")
    return t in ("group", "supergroup")

def is_reply_to_bot(msg: dict) -> bool:
    reply = msg.get("reply_to_message")
    if not reply:
        return False
    frm = reply.get("from") or {}
    if not frm.get("is_bot"):
        return False
    bid = get_bot_id()
    if bid is not None and frm.get("id") is not None:
        return int(frm["id"]) == int(bid)
    return True

def display_label_from_user(from_user: dict | None, settings: dict | None = None) -> str:
    """
    Подпись для вотермарки:
    1) кастомный ник из настроек (если задан)
    2) @username
    3) first_name + last_name (акк без собаки)
    4) пусто → watermark поставит Prompt AI
    """
    settings = settings or {}
    custom = (settings.get("wm_name") or "").strip()
    if custom:
        return custom

    from_user = from_user or {}
    uname = (from_user.get("username") or "").strip()
    if uname:
        return f"@{uname.lstrip('@')}"

    first = (from_user.get("first_name") or "").strip()
    last = (from_user.get("last_name") or "").strip()
    full = (first + (" " + last if last else "")).strip()
    return full

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
    gm = settings.get("gen_mode", "classic")
    wm = (settings.get("wm_name") or "").strip()
    wm_btn = f"🏷 Ник: {wm[:12]}" if wm else "🏷 Ник: авто"

    def mode_btn(key, label):
        mark = "✅" if gm == key else ""
        return {"text": f"{label} {mark}".strip(), "callback_data": f"gmode_{key}"}

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
                mode_btn("classic", "🧠 Classic"),
                mode_btn("mini", "📦 Mini"),
            ],
            [
                mode_btn("fast", "⚡ Fast"),
                mode_btn("turbo", "🚀 Turbo"),
            ],
            [
                {"text": f"🗣 Мужской {'✅' if s == 'Ryan' else ''}", "callback_data": "voice_male"},
                {"text": f"🗣 Женский {'✅' if s == 'Vivian' else ''}", "callback_data": "voice_female"}
            ],
            [
                {"text": f"🇷🇺 RU {'✅' if l == 'Russian' else ''}", "callback_data": "lang_ru"},
                {"text": f"🇬🇧 EN {'✅' if l == 'English' else ''}", "callback_data": "lang_en"}
            ],
            [
                {"text": wm_btn, "callback_data": "wm_set"},
                {"text": "♻️ Сброс ника", "callback_data": "wm_clear"}
            ],
            [{"text": "🔁 Повторить видео", "callback_data": "mode_repeat"}],
            [{"text": "✅ Готово — напишу идею", "callback_data": "done"}]
        ]
    }
    return keyboard

def default_settings():
    return {
        "format": "9:16", "duration": 10, "speaker": "Vivian",
        "language": "Russian", "style": "3d", "ready": False,
        "mode": "text", "wm_name": "", "await_wm": False,
        "gen_mode": "classic",
    }

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

    mode_cfg = get_mode(settings.get("gen_mode", "classic"))
    is_vertical = settings.get("format", "9:16") == "9:16"
    total_duration = max(5, min(int(mode_cfg.get("duration_cap", 30)), int(settings.get("duration", 10))))
    selected_speaker = settings.get("speaker", "Vivian")
    selected_language = settings.get("language", "Russian")
    forced_style = settings.get("style", "3d")
    max_scenes = int(mode_cfg.get("max_scenes", 6))
    fps = int(mode_cfg.get("fps", 15))
    use_tts = bool(mode_cfg.get("tts", True))
    use_lipsync = bool(mode_cfg.get("lipsync", True))
    min_dur = float(mode_cfg.get("min_scene_dur", 1.5))
    max_dur = float(mode_cfg.get("max_scene_dur", 8.0))

    mode_label = mode_cfg.get("label", settings.get("gen_mode", "classic"))
    msg = requests.post(
        f"https://api.telegram.org/bot{os.environ['BOT_TOKEN']}/sendMessage",
        json={"chat_id": chat_id, "text": f"⏳ Генерация ({mode_label})...\n\n[░░░░░░░░░░] 0%"}
    ).json()
    message_id = msg["result"]["message_id"]

    is_done = [False]
    t = threading.Thread(target=progress_updater, args=(chat_id, message_id, is_done), daemon=True)
    t.start()

    try:
        script = screenwriter.run(
            idea,
            total_duration=total_duration,
            max_scenes=max_scenes,
            use_llm=bool(mode_cfg.get("use_llm_script", True)),
        )
        plan = director.run(
            script,
            forced_style=forced_style,
            total_duration=total_duration,
            max_scenes=max_scenes,
            use_llm=bool(mode_cfg.get("use_llm_director", True)),
        )

        n_scenes = len(plan["scenes"])
        if n_scenes == 0:
            raise ValueError("Режиссёр не создал ни одной сцены")

        script_scenes = script.get("scenes", [])
        for i, sc in enumerate(plan["scenes"]):
            sc["duration"] = max(min_dur, min(max_dur, float(sc.get("duration", total_duration / n_scenes))))

        current_sum = sum(sc["duration"] for sc in plan["scenes"])
        if current_sum > 0:
            scale = total_duration / current_sum
            for sc in plan["scenes"]:
                sc["duration"] = round(sc["duration"] * scale, 2)

        speech_lines = build_scene_lines(idea, script_scenes, plan["scenes"])
        for i, sc in enumerate(plan["scenes"]):
            sc["narration"] = speech_lines[i] if i < len(speech_lines) else ""

        audio_parts = []
        lip_curves = []
        for i, sc in enumerate(plan["scenes"]):
            p = WORK / f"a_{i}.wav"
            clean_text = (sc.get("narration") or "").strip()

            if not use_tts or not clean_text:
                os.system(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t {sc['duration']} '{p}'")
            else:
                synth(clean_text, str(p), speaker=selected_speaker, language=selected_language)

            audio_parts.append(p)
            if use_lipsync:
                lip_curves.append(mouth_curve_from_wav(p, fps=fps, duration=float(sc["duration"])))
            else:
                lip_curves.append([0.0])

        scenes_html = []
        for i, sc in enumerate(plan["scenes"]):
            html = artist.run(
                sc, plan,
                original_idea=idea,
                lip_curve=lip_curves[i],
                use_llm=bool(mode_cfg.get("use_llm_artist", True)),
            )
            html = inject(html, float(sc["duration"]), username=username)
            scenes_html.append((html, sc["duration"]))

        from render import render_all
        asyncio.run(render_all(scenes_html, WORK / "frames", is_vertical, fps=fps))

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
                        user_settings[chat_id] = default_settings()
                    settings = user_settings[chat_id]

                    if data.startswith("fmt_"):
                        settings["format"] = "9:16" if "9_16" in data else "16:9"
                    elif data.startswith("dur_"):
                        settings["duration"] = int(data.split("_")[1])
                    elif data.startswith("style_"):
                        settings["style"] = "2d" if "2d" in data else "3d"
                    elif data.startswith("gmode_"):
                        key = data.split("_", 1)[1]
                        if key in MODES:
                            settings["gen_mode"] = key
                            # подрезать длительность под cap режима
                            cap = int(MODES[key].get("duration_cap", 30))
                            if settings.get("duration", 10) > cap:
                                settings["duration"] = cap
                    elif data.startswith("voice_"):
                        settings["speaker"] = "Ryan" if "male" in data else "Vivian"
                    elif data.startswith("lang_"):
                        settings["language"] = "Russian" if "ru" in data else "English"
                    elif data == "wm_set":
                        settings["await_wm"] = True
                        settings["ready"] = False
                        send_message(
                            chat_id,
                            "🏷 Напиши ник для вотермарки (можно без @).\n"
                            "Например: Иван или @myname\n"
                            "Если у аккаунта нет username — просто имя тоже ок."
                        )
                        continue
                    elif data == "wm_clear":
                        settings["wm_name"] = ""
                        settings["await_wm"] = False
                        send_message(chat_id, "♻️ Ник сброшен. Будет браться из аккаунта автоматически.")
                    elif data == "mode_repeat":
                        settings["mode"] = "repeat"
                        send_message(chat_id, "📹 Отправь видео и напиши в подписи, что на нём происходит.")
                        continue
                    elif data == "done":
                        settings["ready"] = True
                        settings["mode"] = "text"
                        settings["await_wm"] = False
                        gm = settings.get("gen_mode", "classic")
                        label = MODES.get(gm, {}).get("label", gm)
                        send_message(
                            chat_id,
                            f"✅ Настройки сохранены! Режим: {label}\n"
                            "Теперь напиши идею для видео.\n\n"
                            "Пример: человек приседает, встаёт и видит кошку"
                        )
                        continue

                    edit_message_text(
                        chat_id, message_id,
                        "⚙️ Настрой генерацию:\n• формат • длительность • 2D/3D • режим • голос • язык • ник\n\n"
                        "Режимы:\n"
                        "🧠 Classic — полный ИИ, много сцен\n"
                        "📦 Mini — урезанный\n"
                        "⚡ Fast — быстро, эвристики\n"
                        "🚀 Turbo — максимально быстро\n\n"
                        "Потом нажми «Готово» и напиши идею.",
                        reply_markup=get_menu(settings)
                    )
                    continue

                msg = upd.get("message")
                if not msg:
                    continue

                if is_group_chat(msg) and not is_reply_to_bot(msg):
                    continue

                chat_id = msg["chat"]["id"]
                from_user = msg.get("from") or {}
                if chat_id not in user_settings:
                    user_settings[chat_id] = default_settings()
                settings = user_settings[chat_id]

                # Пользователь вводит свой ник для вотермарки
                if settings.get("await_wm") and "text" in msg:
                    text = (msg.get("text") or "").strip()
                    if text.startswith("/"):
                        settings["await_wm"] = False
                    else:
                        settings["wm_name"] = text[:40]
                        settings["await_wm"] = False
                        send_message(
                            chat_id,
                            f"✅ Ник для видео: {settings['wm_name']}\n"
                            "Можно снова открыть /start и нажать «Готово».",
                            reply_markup=get_menu(settings)
                        )
                        continue

                display_name = display_label_from_user(from_user, settings)

                if "video" in msg:
                    caption = msg.get("caption", "")
                    if not caption:
                        send_message(chat_id, "⚠️ Добавь к видео текстовое описание.")
                        continue
                    if settings.get("mode") != "repeat":
                        send_message(chat_id, "⚠️ Сначала нажми «Повторить видео» в меню (/start).")
                        continue
                    settings["ready"] = False
                    settings["mode"] = "text"
                    with queue_lock:
                        queue.append({
                            "chat_id": chat_id, "idea": caption,
                            "username": display_name, "settings": settings.copy()
                        })
                        pos = len(queue)
                    send_message(chat_id, f"🎬 Принято в очередь! Ты {pos}-й.")
                    continue

                if "text" not in msg:
                    continue
                text = msg["text"]

                if text.startswith("/start"):
                    prev_wm = settings.get("wm_name", "")
                    prev_mode = settings.get("gen_mode", "classic")
                    user_settings[chat_id] = default_settings()
                    user_settings[chat_id]["wm_name"] = prev_wm
                    user_settings[chat_id]["gen_mode"] = prev_mode
                    send_message(
                        chat_id,
                        "⚙️ Настрой генерацию:\n• формат • длительность • 2D/3D • режим • голос • язык • ник\n\n"
                        "Режимы:\n"
                        "🧠 Classic — полный ИИ (все агенты, lip-sync)\n"
                        "📦 Mini — меньше LLM\n"
                        "⚡ Fast — быстро без LLM-сценария\n"
                        "🚀 Turbo — мегабыстро, без озвучки\n\n"
                        "Потом нажми «Готово» и напиши идею.\n"
                        "Пример: человек приседает, встаёт и видит кошку\n\n"
                        "💡 Нет @username? Нажми «Ник» и напиши имя.\n"
                        "В группе — только reply на сообщение бота.",
                        reply_markup=get_menu(user_settings[chat_id])
                    )
                    continue

                if not settings.get("ready"):
                    send_message(chat_id, "⚠️ Сначала выбери настройки в меню (нажми /start).")
                    continue

                settings["ready"] = False
                with queue_lock:
                    queue.append({
                        "chat_id": chat_id, "idea": text,
                        "username": display_name, "settings": settings.copy()
                    })
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

import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset: int | None, timeout: int = 50): # <-- Добавили timeout
    params = {"timeout": timeout, "allowed_updates": '["message"]'}
    if offset is not None:
        params["offset"] = offset
    # Таймаут запроса должен быть больше, чем таймаут Telegram
    r = requests.get(f"{API}/getUpdates", params=params, timeout=timeout + 10)
    return r.json().get("result", [])

def send_message(chat_id: int, text: str):
    requests.post(f"{API}/sendMessage",
                  json={"chat_id": chat_id, "text": text[:4000]}, timeout=30)

def send_video(chat_id: int, path: str, caption: str = ""):
    with open(path, "rb") as f:
        requests.post(f"{API}/sendVideo",
                      data={"chat_id": chat_id, "caption": caption[:1000]},
                      files={"video": f}, timeout=300)

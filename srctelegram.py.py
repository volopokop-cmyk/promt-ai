import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset: int | None):
    params = {"timeout": 0, "allowed_updates": '["message"]'}
    if offset is not None:
        params["offset"] = offset
    r = requests.get(f"{API}/getUpdates", params=params, timeout=60)
    return r.json().get("result", [])

def send_message(chat_id: int, text: str):
    requests.post(f"{API}/sendMessage",
                  json={"chat_id": chat_id, "text": text[:4000]}, timeout=30)

def send_video(chat_id: int, path: str, caption: str = ""):
    with open(path, "rb") as f:
        requests.post(f"{API}/sendVideo",
                      data={"chat_id": chat_id, "caption": caption[:1000]},
                      files={"video": f}, timeout=300)
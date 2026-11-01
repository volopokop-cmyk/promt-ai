import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_updates(offset: int | None, timeout: int = 10):
    params = {"timeout": timeout, "allowed_updates": '["message", "callback_query"]'}
    if offset is not None:
        params["offset"] = offset
    r = requests.get(f"{API}/getUpdates", params=params, timeout=timeout + 10)
    return r.json().get("result", [])

def send_message(chat_id: int, text: str, reply_markup: dict = None):
    payload = {"chat_id": chat_id, "text": text[:4000]}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{API}/sendMessage", json=payload, timeout=30)

def edit_message_text(chat_id: int, message_id: int, text: str, reply_markup: dict = None):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text[:4000]}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{API}/editMessageText", json=payload, timeout=30)

def send_video(chat_id: int, path: str, caption: str = ""):
    with open(path, "rb") as f:
        requests.post(f"{API}/sendVideo",
                      data={"chat_id": chat_id, "caption": caption[:1000]},
                      files={"video": f}, timeout=300)

def answer_callback(callback_id: str):
    requests.post(f"{API}/answerCallbackQuery", json={"callback_query_id": callback_id})

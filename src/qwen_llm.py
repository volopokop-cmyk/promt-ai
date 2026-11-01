import os
import json
import re
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

# ЛУЧШАЯ МОДЕЛЬ ДЛЯ GITHUB (3B, влезает в 7GB RAM)
MODEL_REPO = "Qwen/Qwen2.5-3B-Instruct-GGUF"
MODEL_FILE = "qwen2.5-3b-instruct-q4_k_m.gguf"

_llm = None

def _load():
    global _llm
    if _llm is None:
        # Скачиваем модель (кэшируется в GitHub Actions)
        model_path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE)
        
        # Настройки для процессора GitHub (2 ядра)
        _llm = Llama(
            model_path=model_path,
            n_ctx=4096,       # Контекст (сколько текста помнит)
            n_threads=2,      # Используем 2 ядра
            n_batch=512,      
            verbose=False
        )

def ask(system: str, user: str, max_new_tokens: int = 1024) -> str:
    _load()
    # Формат промта для Qwen
    prompt = f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{user}<|im_end|>\n<|im_start|>assistant\n"
    
    output = _llm(
        prompt,
        max_tokens=max_new_tokens,
        temperature=0.7,
        top_p=0.9,
        stop=["<|im_end|>"],
        echo=False
    )
    
    return output['choices'][0]['text'].strip()

def ask_json(system: str, user: str, max_new_tokens: int = 1024) -> dict:
    raw = ask(system, user, max_new_tokens)
    
    # Логика починки JSON
    start = raw.find('{')
    end = raw.rfind('}')
    if start == -1 or end == -1:
        raise ValueError(f"Модель не выдала JSON: {raw[:300]}")
        
    json_str = raw[start:end+1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        json_str = json_str.replace("'", '"')
        try:
            return json.loads(json_str)
        except Exception:
            raise ValueError(f"Не удалось починить JSON: {e}\nТекст: {json_str[:300]}")

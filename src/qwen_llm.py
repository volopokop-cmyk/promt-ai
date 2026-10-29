import json
import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

_tokenizer = None
_model = None

def _load():
    global _tokenizer, _model
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, torch_dtype=torch.float32, low_cpu_mem_usage=True
        )
        _model.eval()

def ask(system: str, user: str, max_new_tokens: int = 1024) -> str:
    _load()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    text = _tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    inputs = _tokenizer([text], return_tensors="pt")
    with torch.no_grad():
        out = _model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=True, temperature=0.7, top_p=0.9,
        )
    gen = out[0][inputs["input_ids"].shape[1]:]
    return _tokenizer.decode(gen, skip_special_tokens=True).strip()

def ask_json(system: str, user: str, max_new_tokens: int = 1024) -> dict:
    raw = ask(system, user, max_new_tokens)
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError(f"LLM не вернул JSON: {raw[:300]}")
    return json.loads(m.group(0))

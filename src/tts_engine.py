import os
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

MODEL_NAME = os.getenv("QWEN_TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")
SPEAKER = os.getenv("QWEN_TTS_SPEAKER", "Vivian")
LANGUAGE = os.getenv("QWEN_TTS_LANGUAGE", "Russian")

_model = None

def _load():
    global _model
    if _model is None:
        _model = Qwen3TTSModel.from_pretrained(
            MODEL_NAME,
            device_map="cpu",
            dtype=torch.float32,
        )
        _model.model.eval()

def synth(text: str, out_wav: str, instruct: str | None = None):
    _load()
    kwargs = {"text": text, "language": LANGUAGE, "speaker": SPEAKER}
    if instruct:
        kwargs["instruct"] = instruct
    wavs, sr = _model.generate_custom_voice(**kwargs)
    sf.write(out_wav, wavs[0], sr)

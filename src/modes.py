"""Режимы генерации видео."""

# classic — полный пайплайн, всё как обычно
# mini    — урезанная генерация (меньше LLM/сцен)
# fast    — быстро: эвристики, меньше кадров
# turbo   — максимально быстро: минимум сцен, без озвучки

MODES = {
    "classic": {
        "label": "Classic",
        "use_llm_script": True,
        "use_llm_director": True,
        "use_llm_artist": True,
        "tts": True,
        "lipsync": True,
        "fps": 15,
        "max_scenes": 6,
        "min_scene_dur": 2.0,
        "max_scene_dur": 8.0,
        "duration_cap": 30,
    },
    "mini": {
        "label": "Mini",
        "use_llm_script": True,
        "use_llm_director": False,
        "use_llm_artist": False,
        "tts": True,
        "lipsync": False,
        "fps": 10,
        "max_scenes": 3,
        "min_scene_dur": 2.0,
        "max_scene_dur": 6.0,
        "duration_cap": 20,
    },
    "fast": {
        "label": "Fast",
        "use_llm_script": False,
        "use_llm_director": False,
        "use_llm_artist": False,
        "tts": True,
        "lipsync": False,
        "fps": 8,
        "max_scenes": 3,
        "min_scene_dur": 1.5,
        "max_scene_dur": 5.0,
        "duration_cap": 15,
    },
    "turbo": {
        "label": "Turbo",
        "use_llm_script": False,
        "use_llm_director": False,
        "use_llm_artist": False,
        "tts": False,
        "lipsync": False,
        "fps": 6,
        "max_scenes": 2,
        "min_scene_dur": 1.2,
        "max_scene_dur": 4.0,
        "duration_cap": 10,
    },
}

def get_mode(name: str) -> dict:
    return MODES.get((name or "classic").lower(), MODES["classic"])

import os
import subprocess
from pathlib import Path

def run(frames_dir: Path, audio_parts: list[Path], out_mp4: Path):
    """Собирает кадры + аудио в финальное видео.
    Вотермарка уже вшита в HTML-сцены, поэтому отдельный overlay не нужен.
    """
    full_audio = frames_dir.parent / "full.wav"
    valid_parts = [p for p in audio_parts if p is not None and p.exists()]

    if not valid_parts:
        os.system(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 10 '{full_audio}'")
    else:
        concat = frames_dir.parent / "concat.txt"
        concat.write_text("\n".join(f"file '{p.resolve()}'" for p in valid_parts))
        os.system(f"ffmpeg -y -f concat -safe 0 -i '{concat}' -c copy '{full_audio}'")

    frames = sorted(frames_dir.glob("f_*.png"))
    if not frames:
        raise RuntimeError("Нет кадров для монтажа!")

    seq = frames_dir / "seq"
    seq.mkdir(exist_ok=True)
    for i, f in enumerate(frames):
        target = seq / f"{i:06d}.png"
        if not target.exists():
            f.rename(target)

    # FPS должен совпадать с render.py (15)
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", "15",
        "-i", str(seq / "%06d.png"),
        "-i", str(full_audio),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(out_mp4),
    ], check=True)

    return out_mp4

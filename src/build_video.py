import subprocess
from pathlib import Path

def build(frames_dir: Path, audio: Path, out_mp4: Path):
    frames = sorted(frames_dir.glob("f_*.png"))
    if not frames:
        raise RuntimeError("нет кадров")
    seq = frames_dir / "seq"; seq.mkdir(exist_ok=True)
    for i, f in enumerate(frames):
        f.rename(seq / f"{i:06d}.png")
    subprocess.run([
        "ffmpeg", "-y", "-framerate", "30",
        "-i", str(seq / "%06d.png"),
        "-i", str(audio),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        str(out_mp4),
    ], check=True)

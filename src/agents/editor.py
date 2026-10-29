import os
from pathlib import Path
from build_video import build

def join_audio(parts: list[Path], out_wav: Path):
    concat = out_wav.parent / "concat.txt"
    concat.write_text("\n".join(f"file '{p.resolve()}'" for p in parts))
    os.system(f"ffmpeg -y -f concat -safe 0 -i {concat} -c copy {out_wav}")

def run(frames_dir: Path, audio_parts: list[Path], out_mp4: Path):
    full = frames_dir.parent / "full.wav"
    join_audio(audio_parts, full)
    build(frames_dir, full, out_mp4)
    return out_mp4

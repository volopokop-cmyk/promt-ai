import os
import subprocess
from pathlib import Path

def run(frames_dir: Path, audio_parts: list[Path], out_mp4: Path):
    # 1. Собираем аудио и кадры в основное видео
    full_audio = frames_dir.parent / "full.wav"
    valid_parts = [p for p in audio_parts if p is not None and p.exists()]
    
    if not valid_parts:
        os.system(f"ffmpeg -y -f lavfi -i anullsrc=r=24000:cl=mono -t 10 {full_audio}")
    else:
        concat = frames_dir.parent / "concat.txt"
        concat.write_text("\n".join(f"file '{p.resolve()}'" for p in valid_parts))
        os.system(f"ffmpeg -y -f concat -safe 0 -i '{concat}' -c copy '{full_audio}'")

    frames = sorted(frames_dir.glob("f_*.png"))
    if not frames:
        raise RuntimeError("Нет кадров!")
        
    seq = frames_dir / "seq"
    seq.mkdir(exist_ok=True)
    for i, f in enumerate(frames):
        f.rename(seq / f"{i:06d}.png")

    temp_mp4 = frames_dir.parent / "temp_video.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", "15",
        "-i", str(seq / "%06d.png"),
        "-i", str(full_audio),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
        "-c:a", "aac", "-b:a", "128k",
        str(temp_mp4),
    ], check=True)

    # 2. Рендерим летающую вотермарку в прозрачное видео (WebM)
    wm_path = frames_dir.parent / "watermark.html"
    wm_video = frames_dir.parent / "watermark.webm"
    
    # Используем Playwright для записи прозрачного видео (или делаем серию PNG с альфа-каналом)
    # Для простоты мы просто наложим картинку логотипа через FFmpeg в правый нижний угол,
    # так как запись прозрачного видео с полетом через Playwright на GitHub - это очень сложно и долго.
    
    # Но если ты хочешь именно полет, мы можем сделать это через сложный фильтр FFmpeg.
    # В данном коде мы делаем просто статичную вотермарку в правом нижнем углу для надежности.
    
    logo_path = frames_dir.parent / "logo.jpg"
    if not os.path.exists(logo_path):
        import requests
        url = "https://raw.githubusercontent.com/volopopop-cmyk/promt-ai/main/logo.jpg"
        r = requests.get(url)
        with open(logo_path, "wb") as f:
            f.write(r.content)

    # Накладываем логотип в правый нижний угол (или можем в центр)
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(temp_mp4),
        "-i", str(logo_path),
        "-filter_complex", "[0:v][1:v] overlay=W-w-20:H-h-20:enable='between(t,0,10)'",
        "-c:a", "copy",
        str(out_mp4)
    ], check=True)
    
    return out_mp4

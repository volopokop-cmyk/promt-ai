"""Строит кривую открытия рта по реальному аудио."""
from pathlib import Path
import numpy as np
import soundfile as sf

def mouth_curve_from_wav(path: str | Path, fps: int = 15, duration: float | None = None) -> list[float]:
    """Возвращает список значений 0..1 (открытие рта) на каждый кадр."""
    path = Path(path)
    if not path.exists():
        n = max(1, int((duration or 3.0) * fps))
        return [0.0] * n

    try:
        data, sr = sf.read(str(path), always_2d=False)
    except Exception:
        n = max(1, int((duration or 3.0) * fps))
        return [0.0] * n

    if data.ndim > 1:
        data = data.mean(axis=1)
    data = data.astype(np.float32)

    if duration is None:
        duration = len(data) / float(sr)
    n_frames = max(1, int(round(duration * fps)))
    samples_per_frame = max(1, int(sr / fps))

    curve = []
    for i in range(n_frames):
        start = i * samples_per_frame
        end = min(len(data), start + samples_per_frame)
        if start >= len(data) or end <= start:
            curve.append(0.0)
            continue
        chunk = data[start:end]
        # RMS энергия
        rms = float(np.sqrt(np.mean(chunk * chunk) + 1e-12))
        curve.append(rms)

    arr = np.array(curve, dtype=np.float32)
    # Нормализация + лёгкое сглаживание
    peak = float(arr.max()) if arr.size else 0.0
    if peak > 1e-6:
        arr = arr / peak
    else:
        arr = arr * 0.0

    # Сглаживание (moving average)
    if len(arr) >= 3:
        kernel = np.array([0.2, 0.6, 0.2], dtype=np.float32)
        arr = np.convolve(arr, kernel, mode="same")

    # Порог тишины + контраст
    arr = np.clip((arr - 0.08) / 0.85, 0.0, 1.0)
    arr = np.power(arr, 0.75)  # чуть мягче

    return [round(float(x), 4) for x in arr]

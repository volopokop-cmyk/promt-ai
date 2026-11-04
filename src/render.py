import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

DEFAULT_FPS = 15

async def render_scene(html: str, duration: float, out_dir: Path, idx: int, is_vertical: bool, fps: int = DEFAULT_FPS):
    frames = max(1, int(duration * fps))
    f = out_dir / f"scene_{idx}.html"
    f.write_text(html, encoding="utf-8")

    W, H = (720, 1280) if is_vertical else (1280, 720)

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = await browser.new_page(viewport={"width": W, "height": H})
        await page.goto(f.resolve().as_uri())
        await page.wait_for_timeout(400)
        delay = max(30, int(1000 / max(1, fps)))
        for i in range(frames):
            await page.screenshot(path=str(out_dir / f"f_{idx:02d}_{i:05d}.png"))
            await page.wait_for_timeout(delay)
        await browser.close()

async def render_all(scenes_html: list, out_dir: Path, is_vertical: bool = False, fps: int = DEFAULT_FPS):
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, (html, dur) in enumerate(scenes_html):
        await render_scene(html, dur, out_dir, i, is_vertical, fps=fps)

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

FPS = 15 # Уменьшили для скорости

async def render_scene(html: str, duration: float, out_dir: Path, idx: int, is_vertical: bool):
    frames = int(duration * FPS)
    f = out_dir / f"scene_{idx}.html"
    f.write_text(html, encoding="utf-8")

    # Настраиваем размеры
    W, H = (720, 1280) if is_vertical else (1280, 720)

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = await browser.new_page(viewport={"width": W, "height": H})
        await page.goto(f.resolve().as_uri())
        await page.wait_for_timeout(500)
        for i in range(frames):
            await page.screenshot(path=str(out_dir / f"f_{idx:02d}_{i:05d}.png"))
            await page.wait_for_timeout(int(1000 / FPS))
        await browser.close()

async def render_all(scenes_html: list, out_dir: Path, is_vertical: bool = False):
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, (html, dur) in enumerate(scenes_html):
        await render_scene(html, dur, out_dir, i, is_vertical)

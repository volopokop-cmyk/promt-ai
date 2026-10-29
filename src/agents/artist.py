from qwen_llm import ask

SYSTEM_2D = """Ты — фронтенд-художник. На вход — одна сцена (JSON) и палитра.
Верни ОДИН HTML-файл с инлайн CSS, красиво отрисовывающий сцену.

Требования:
- 1280x720, html/body без отступов, overflow:hidden.
- Фон palette[0], текст palette[2], акцент palette[1].
- Крупная типографика по центру (56–72px), fade-in + translateY.
- 2–3 декоративных CSS-элемента (круги, линии, градиенты).
- Только CSS @keyframes, без JS-событий.
- animation-duration: var(--dur).
- Без внешних ссылок.

Верни ТОЛЬКО HTML с <!doctype html>."""

SYSTEM_3D = """Ты — Three.js-художник. На вход — одна сцена (JSON) и палитра.
Верни ОДИН HTML-файл, рисующий объёмную сцену.

Требования:
- importmap: {"imports":{"three":"https://unpkg.com/three@0.160.0/build/three.module.js"}}
- <script type="module">import * as THREE from 'three';</script>
- 1280x720, renderer antialias, фон palette[0].
- 1 главный объект (сфера/куб/торус/конус) + 20–40 частиц.
- DirectionalLight + AmbientLight, цвет palette[1].
- Объект вращается, камера делает camera_move.
- HTML-оверлей с текстом сцены поверх canvas, fade-in.
- Без внешних ссылок кроме unpkg three.

Верни ТОЛЬКО HTML с <!doctype html>."""

def run(scene: dict, plan: dict) -> str:
    system = SYSTEM_3D if plan["style"] == "3d" else SYSTEM_2D
    user = (f"Сцена: {scene}\nПалитра: {plan['palette']}\n"
            f"Шрифт: {plan['font']}\nДлительность: {scene['duration']}s")
    html = ask(system, user, max_new_tokens=2048)
    if "```" in html:
        html = html.split("```")[1]
        if html.startswith("html"):
            html = html[4:]
    html = html.strip()
    if not html.lower().startswith("<!doctype"):
        html = "<!doctype html><html><body>" + html + "</body></html>"
    return html

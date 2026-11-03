"""Достаёт из идеи пользователя только то, что должен сказать персонаж."""
import re

QUOTE_RE = re.compile(
    r'[«"""‘’](.+?)[»"""‘’]',
    re.DOTALL,
)

SAY_RE = re.compile(
    r'(?:говорит|сказать|скажи|говори|произносит|шепчет|кричит|отвечает|asks?|says?|say|speak(?:s|ing)?)\s*[:\-–]?\s*(.+)$',
    re.IGNORECASE | re.DOTALL,
)

# Команды/описание, которые не надо озвучивать
META_WORDS = re.compile(
    r'\b(человек|челик|персонаж|парень|девушка|мужчина|женщина|мальчик|девочка|'
    r'2d|3d|вертикал\w*|горизонтал\w*|shorts?|youtube|'
    r'машет|идёт|идет|прыгает|ходит|стоит|бежит|'
    r'person|character|man|woman|guy|girl|wave|walk|jump|idle)\b',
    re.IGNORECASE,
)

def _clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.strip(' .,;:!?—–-')
    return text.strip()

def extract_spoken_line(idea: str) -> str | None:
    """
    Возвращает фразу для озвучки или None, если явной речи нет.
    Примеры:
      «человек говорит привет» → «привет»
      «челик говорит: как дела» → «как дела»
      'person says "hello world"' → 'hello world'
    """
    if not idea or not idea.strip():
        return None

    idea = idea.strip()

    # 1) Текст в кавычках — самый надёжный
    m = QUOTE_RE.search(idea)
    if m:
        q = _clean(m.group(1))
        if q:
            return q

    # 2) После «говорит / say / ...»
    m = SAY_RE.search(idea)
    if m:
        tail = _clean(m.group(1))
        # убрать кавычки, если остались
        tail = tail.strip('«»"""‘’')
        tail = _clean(tail)
        if tail:
            return tail

    return None

def is_probably_full_prompt(text: str, idea: str) -> bool:
    """True, если narration почти совпадает со всем промптом (плохо)."""
    if not text or not idea:
        return False
    a = re.sub(r'\W+', '', text.lower())
    b = re.sub(r'\W+', '', idea.lower())
    if not a or not b:
        return False
    # narration покрывает >70% промпта или наоборот
    return (len(a) >= 12 and (a in b or b in a) and min(len(a), len(b)) / max(len(a), len(b)) > 0.7)

def sanitize_narration(narration: str, idea: str) -> str:
    """Чистит narration от LLM: не весь промпт, не мусор."""
    if not narration:
        return ""
    n = _clean(narration)
    if not n:
        return ""
    if is_probably_full_prompt(n, idea):
        # Попробовать вытащить речь из промпта
        extracted = extract_spoken_line(idea)
        return extracted or ""
    # Если narration = весь idea без пробелов почти
    if n.lower() == idea.strip().lower():
        extracted = extract_spoken_line(idea)
        return extracted or ""
    return n

def build_scene_lines(idea: str, script_scenes: list, plan_scenes: list) -> list[str]:
    """
    Для каждой сцены — итоговый текст озвучки.
    Приоритет:
      1) явная фраза из промпта пользователя
      2) narration из сценария (очищенный)
      3) пусто (тишина), НЕ title/text сцены и НЕ весь промпт
    """
    extracted = extract_spoken_line(idea)
    n = len(plan_scenes)
    lines = [""] * n

    if extracted:
        # Одна фраза пользователя — кладём в первую сцену (или делим по предложениям)
        parts = re.split(r'(?<=[.!?…])\s+', extracted)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) == 1 or n == 1:
            lines[0] = extracted
        else:
            # Размазать предложения по сценам
            for i in range(min(n, len(parts))):
                lines[i] = parts[i]
            # Если предложений меньше сцен — остаток тишина
        return lines

    # Нет явной фразы — берём narration из сценария, но чистим
    for i in range(n):
        narr = ""
        if i < len(script_scenes):
            narr = (script_scenes[i].get("narration") or "").strip()
        if not narr and i < len(plan_scenes):
            narr = (plan_scenes[i].get("narration") or "").strip()
        narr = sanitize_narration(narr, idea)
        # Не подставляем text/title сцены — это заголовок, не речь
        lines[i] = narr

    return lines

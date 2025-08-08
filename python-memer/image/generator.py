# title_above.py
from typing import Optional, Union, Tuple, List
import os
from PIL import Image, ImageDraw, ImageFont

# --- Font helpers (ensure a scalable TTF so text isn't tiny) ---
def _candidate_fonts() -> List[str]:
    return [p for p in [
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ] if os.path.exists(p)]

def _load_font(size: int, font_path: Optional[str]) -> ImageFont.ImageFont:
    if font_path:
        try: return ImageFont.truetype(font_path, size)
        except Exception: pass
    for p in _candidate_fonts():
        try: return ImageFont.truetype(p, size)
        except Exception: pass
    return ImageFont.load_default()  # last resort

def _measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    try:
        l, t, r, b = draw.multiline_textbbox((0, 0), text, font=font, spacing=4, align="left")
        return r - l, b - t
    except AttributeError:
        return draw.multiline_textsize(text, font=font, spacing=4)

# --- Wrapping that also breaks very long words by characters ---
def _break_word(draw, word: str, font, max_w: int) -> List[str]:
    chunks, cur = [], ""
    for ch in word:
        test = cur + ch
        w, _ = _measure(draw, test, font)
        if w <= max_w or not cur:
            cur = test
        else:
            chunks.append(cur)
            cur = ch
    if cur:
        chunks.append(cur)
    return chunks

def _wrap_to_width(draw, text: str, font, max_w: int) -> str:
    words = text.split()
    if not words: return ""
    lines, line = [], ""
    for word in words:
        # If the whole word doesn't fit at all, split it
        parts = [word] if _measure(draw, word, font)[0] <= max_w else _break_word(draw, word, font, max_w)
        for part in parts:
            candidate = (line + " " + part) if line else part
            if _measure(draw, candidate, font)[0] <= max_w:
                line = candidate
            else:
                if line: lines.append(line)
                line = part
    if line: lines.append(line)
    return "\n".join(lines)

def _fit_text(draw, title, font_path, max_w, max_h, min_size, max_size, wrap=True):
    best = None
    lo, hi = min_size, max_size
    while lo <= hi:
        mid = (lo + hi) // 2
        font = _load_font(mid, font_path)
        text = _wrap_to_width(draw, title, font, max_w) if wrap else title
        w, h = _measure(draw, text, font)
        if w <= max_w and h <= max_h:
            best = (font, text); lo = mid + 2
        else:
            hi = mid - 2
    if best: return best
    font = _load_font(min_size, font_path)
    return font, _wrap_to_width(draw, title, font, max_w)

def add_title_above(
    img: Union[str, Image.Image],
    title: str,
    *,
    bar_ratio: float = 0.12,        # start with ~12% of image height
    bar_px: Optional[int] = None,   # or fix the bar height
    pad_x: int = 24,
    pad_y: int = 16,
    font_path: Optional[str] = None,
    min_font_px: int = 14,
    wrap: bool = True,
    expand_if_needed: bool = True,  # grow bar if the text still won't fit
    bar_color: str = "white",
    text_color: str = "black",
) -> Image.Image:
    base = Image.open(img) if isinstance(img, str) else img
    base = base.convert("RGBA")
    W, H = base.size
    bar_h = bar_px if bar_px is not None else max(1, int(H * bar_ratio))

    # temp canvas for measuring + drawing
    out = Image.new("RGBA", (W, H + bar_h), bar_color)
    out.paste(base, (0, bar_h), base if base.mode == "RGBA" else None)
    draw = ImageDraw.Draw(out)

    max_w = max(1, W - 2 * pad_x)
    max_h = max(1, bar_h - 2 * pad_y)

    font, text_to_draw = _fit_text(draw, title, font_path, max_w, max_h, min_font_px, max_h, wrap)
    tw, th = _measure(draw, text_to_draw, font)

    # If still taller than the bar, optionally expand the bar and refit to use bigger font
    if expand_if_needed and th + 2 * pad_y > bar_h:
        bar_h = th + 2 * pad_y
        out = Image.new("RGBA", (W, H + bar_h), bar_color)
        out.paste(base, (0, bar_h), base if base.mode == "RGBA" else None)
        draw = ImageDraw.Draw(out)
        max_h = bar_h - 2 * pad_y
        font, text_to_draw = _fit_text(draw, title, font_path, max_w, max_h, min_font_px, max_h, wrap)
        tw, th = _measure(draw, text_to_draw, font)

    # Draw centered text in the bar
    x = (W - tw) // 2
    y = (bar_h - th) // 2
    draw.multiline_text((x, y), text_to_draw, font=font, fill=text_color, spacing=4, align="center")
    return out

def add_title_above_file(input_path: str, title: str, output_path: str, **kwargs) -> None:
    img = add_title_above(input_path, title, **kwargs)
    if output_path.lower().endswith((".jpg", ".jpeg")):
        img = img.convert("RGB")
    img.save(output_path)

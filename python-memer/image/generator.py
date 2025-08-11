import os
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from pygifsicle import gifsicle

def _candidate_fonts() -> list[str]:
    """Return a list of existing font file paths to try in order."""
    return [
        p
        for p in [
            "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/noto/NotoSans-Regular.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
        if os.path.exists(p)
    ]


def _load_font(font_size_px: int, font_path: str | None) -> ImageFont.ImageFont:
    """Load a truetype font, falling back to common system fonts, then default."""
    if font_path:
        try:
            return ImageFont.truetype(font_path, font_size_px)
        except Exception:
            pass
    for candidate_path in _candidate_fonts():
        try:
            return ImageFont.truetype(candidate_path, font_size_px)
        except Exception:
            pass
    return ImageFont.load_default()


def _measure(
    draw_ctx: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont
) -> tuple[int, int]:
    """Measure multiline text (width, height) with PIL, using a safe fallback."""
    try:
        left, top, right, bottom = draw_ctx.multiline_textbbox(
            (0, 0), text, font=font, spacing=4, align="left"
        )
        return right - left, bottom - top
    except AttributeError:
        return draw_ctx.multiline_textsize(text, font=font, spacing=4)


def _break_word(
    draw_ctx: ImageDraw.ImageDraw,
    word: str,
    font: ImageFont.ImageFont,
    max_width_px: int,
) -> list[str]:
    """Break an overlong word into pieces that fit within max_width_px."""
    segments: list[str] = []
    current_segment = ""
    for ch in word:
        candidate = current_segment + ch
        width, _ = _measure(draw_ctx, candidate, font)
        if width <= max_width_px or not current_segment:
            current_segment = candidate
        else:
            segments.append(current_segment)
            current_segment = ch
    if current_segment:
        segments.append(current_segment)
    return segments


def _wrap(
    draw_ctx: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width_px: int,
) -> str:
    """Soft-wrap text to fit max_width_px, breaking long words as needed."""
    words = text.split()
    if not words:
        return ""
    lines: list[str] = []
    current_line = ""
    for word in words:
        parts = (
            [word]
            if _measure(draw_ctx, word, font)[0] <= max_width_px
            else _break_word(draw_ctx, word, font, max_width_px)
        )
        for part in parts:
            candidate_line = (current_line + " " + part) if current_line else part
            if _measure(draw_ctx, candidate_line, font)[0] <= max_width_px:
                current_line = candidate_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = part
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)


def _fit(
    draw_ctx: ImageDraw.ImageDraw,
    text: str,
    font_path: str | None,
    max_width_px: int,
    max_height_px: int,
    min_font_px: int,
    max_font_px: int,
    wrap_text: bool,
) -> tuple[ImageFont.ImageFont, str]:
    """
    Binary-search a font size that fits text within (max_width_px, max_height_px).
    Returns the chosen font and the (possibly wrapped) text.
    """
    best_fit: tuple[ImageFont.ImageFont, str] | None = None
    low_px, high_px = min_font_px, max_font_px
    while low_px <= high_px:
        mid_px = (low_px + high_px) // 2
        trial_font = _load_font(mid_px, font_path)
        trial_text = (
            _wrap(draw_ctx, text, trial_font, max_width_px) if wrap_text else text
        )
        width, height = _measure(draw_ctx, trial_text, trial_font)
        if width <= max_width_px and height <= max_height_px:
            best_fit = (trial_font, trial_text)
            low_px = mid_px + 2
        else:
            high_px = mid_px - 2
    if best_fit:
        return best_fit
    # Fallback to minimum font size if nothing fit
    fallback_font = _load_font(min_font_px, font_path)
    return fallback_font, _wrap(draw_ctx, text, fallback_font, max_width_px)


def _prepare_layout(
    frame_size: tuple[int, int],
    title_text: str,
    *,
    bar_height_ratio: float,
    bar_height_px: int | None,
    padding_x_px: int,
    padding_y_px: int,
    font_path: str | None,
    min_font_px: int,
    wrap_text: bool,
    bar_color: str,
    text_color: str,
) -> dict[str, Any]:
    """
    Compute the title bar layout and text placement.
    Returns a dict with explicit keys used by the compositor.
    """
    frame_width, frame_height = frame_size
    bar_height = (
        bar_height_px
        if bar_height_px is not None
        else max(1, int(frame_height * bar_height_ratio))
    )

    # Use a scratch canvas to measure text
    scratch_canvas = Image.new("RGB", (frame_width, frame_height), bar_color)
    draw_ctx = ImageDraw.Draw(scratch_canvas)

    text_max_width = max(1, frame_width - 2 * padding_x_px)
    text_max_height = max(1, bar_height - 2 * padding_y_px)

    font, wrapped_text = _fit(
        draw_ctx,
        title_text,
        font_path,
        text_max_width,
        text_max_height,
        min_font_px,
        text_max_height,
        wrap_text,
    )
    text_width, text_height = _measure(draw_ctx, wrapped_text, font)

    # If the text still doesn't fit vertically, expand bar_height
    if text_height + 2 * padding_y_px > bar_height:
        bar_height = text_height + 2 * padding_y_px
        text_max_height = bar_height - 2 * padding_y_px
        font, wrapped_text = _fit(
            draw_ctx,
            title_text,
            font_path,
            text_max_width,
            text_max_height,
            min_font_px,
            text_max_height,
            wrap_text,
        )
        text_width, text_height = _measure(draw_ctx, wrapped_text, font)

    text_x = (frame_width - text_width) // 2
    text_y = (bar_height - text_height) // 2

    return {
        "bar_height": bar_height,
        "font": font,
        "wrapped_text": wrapped_text,
        "text_xy": (text_x, text_y),
        "bar_color": bar_color,
        "text_color": text_color,
    }


def _compose_with_title(frame_rgb: Image.Image, layout: dict[str, Any]) -> Image.Image:
    """
    Create a new RGB image that adds a title bar above the input RGB frame.
    """
    frame_width, frame_height = frame_rgb.size
    bar_height: int = layout["bar_height"]

    # Create a taller canvas: title bar on top, original image below
    output_img = Image.new(
        "RGB", (frame_width, frame_height + bar_height), layout["bar_color"]
    )
    output_img.paste(frame_rgb, (0, bar_height))

    # Draw the title text inside the top bar
    draw_ctx = ImageDraw.Draw(output_img)
    draw_ctx.multiline_text(
        layout["text_xy"],
        layout["wrapped_text"],
        font=layout["font"],
        fill=layout["text_color"],
        spacing=4,
        align="center",
    )
    return output_img

def is_file_over_mb(filepath, mb_limit):
    """Check if file is larger than mb_limit MB."""
    file_size_bytes = os.path.getsize(filepath)
    file_size_mb = file_size_bytes / (1024 * 1024)
    return file_size_mb > mb_limit

def add_title_above_file(
    input_path: str,
    title: str,
    output_path: str,
    *,
    bar_height_ratio: float = 0.12,
    bar_height_px: int | None = None,
    padding_x: int = 24,
    padding_y: int = 16,
    font_path: str | None = None,
    min_font_px: int = 14,
    wrap_text: bool = True,
    bar_color: str = "white",
    text_color: str = "black",
) -> None:
    """
    Append a title bar on top of an image or animated GIF without cropping the original.
    The output is taller by the title bar height; GIFs preserve timing/palette and dedupe identical frames.
    """
    with Image.open(input_path) as input_img:
        is_gif = (
            input_img.format == "GIF" and getattr(input_img, "is_animated", False)
        ) or output_path.lower().endswith(".gif")

        if not is_gif:
            base_rgb = input_img.convert("RGB")
            img_width, img_height = base_rgb.size
            layout = _prepare_layout(
                (img_width, img_height),
                title,
                bar_height_ratio=bar_height_ratio,
                bar_height_px=bar_height_px,
                padding_x_px=padding_x,
                padding_y_px=padding_y,
                font_path=font_path,
                min_font_px=min_font_px,
                wrap_text=wrap_text,
                bar_color=bar_color,
                text_color=text_color,
            )
            output_img = _compose_with_title(base_rgb, layout)
            if output_path.lower().endswith((".jpg", ".jpeg")):
                output_img = output_img.convert("RGB")
            output_img.save(output_path)
            return

        # Animated GIF path
        gif_width, gif_height = input_img.size
        layout = _prepare_layout(
            (gif_width, gif_height),
            title,
            bar_height_ratio=bar_height_ratio,
            bar_height_px=bar_height_px,
            padding_x_px=padding_x,
            padding_y_px=padding_y,
            font_path=font_path,
            min_font_px=min_font_px,
            wrap_text=wrap_text,
            bar_color=bar_color,
            text_color=text_color,
        )

        num_frames: int = getattr(input_img, "n_frames", 1)
        frame_durations_ms: list[int] = []
        gif_loop_count = int(input_img.info.get("loop", 0))
        pending_duration_ms = 0

        # Establish a base palette to reuse (helps keep size stable)
        input_img.seek(0)
        base_palette_img = Image.new("P", (1, 1))
        if input_img.getpalette():
            base_palette_img.putpalette(input_img.getpalette())
        else:
            base_palette_img = input_img.convert("P")

        palettized_frames: list[Image.Image] = []
        previous_palettized_frame: Image.Image | None = None

        for frame_index in range(num_frames):
            input_img.seek(frame_index)
            frame_duration_ms = int(input_img.info.get("duration", 40))
            pending_duration_ms += frame_duration_ms

            frame_rgb = input_img.convert("RGB")
            frame_with_title_rgb = _compose_with_title(frame_rgb, layout)
            palettized_frame = frame_with_title_rgb.quantize(
                palette=base_palette_img, dither=Image.NONE
            )

            # Collapse exact duplicates to reduce size
            if (
                previous_palettized_frame is not None
                and palettized_frame.tobytes() == previous_palettized_frame.tobytes()
            ):
                continue

            palettized_frames.append(palettized_frame)
            frame_durations_ms.append(pending_duration_ms)
            pending_duration_ms = 0
            previous_palettized_frame = palettized_frame

        if pending_duration_ms and palettized_frames:
            frame_durations_ms[-1] += pending_duration_ms

        try:
            first_frame_pal = palettized_frames[0]
        except IndexError:
            # Degenerate case: fallback to a single frame
            first_frame_pal = input_img.convert("P")
            palettized_frames = [first_frame_pal]
            frame_durations_ms = [int(input_img.info.get("duration", 40))]

        # Ensure all frames share the same palette
        for frame in palettized_frames:
            frame.putpalette(base_palette_img.getpalette())

        save_kwargs = {
            "save_all": True,
            "append_images": palettized_frames[1:]
            if len(palettized_frames) > 1
            else [],
            "duration": frame_durations_ms
            if frame_durations_ms
            else [int(input_img.info.get("duration", 40))],
            "loop": gif_loop_count,
            "optimize": True,
            "disposal": 2,
        }

        if "transparency" in input_img.info:
            save_kwargs["transparency"] = input_img.info["transparency"]
        if "background" in input_img.info:
            save_kwargs["background"] = input_img.info["background"]

        first_frame_pal.save(output_path, **save_kwargs)
        if is_file_over_mb(output_path, 30):
            gifsicle(
                sources=[output_path],
                optimize=True,
                colors=128,
                options=["--verbose", "--lossy=50"]
            )

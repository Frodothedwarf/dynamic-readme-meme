import os

from PIL import Image, ImageDraw, ImageFont


def _candidate_fonts() -> list[str]:
    return [
        font_path_candidate
        for font_path_candidate in [
            "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/noto/NotoSans-Regular.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
        if os.path.exists(font_path_candidate)
    ]


def _load_font(font_size: int, font_path: str | None) -> ImageFont.ImageFont:
    if font_path:
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception:
            pass
    for candidate_path in _candidate_fonts():
        try:
            return ImageFont.truetype(candidate_path, font_size)
        except Exception:
            pass
    return ImageFont.load_default()


def _measure(
    drawing_context: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont
) -> tuple[int, int]:
    try:
        left, top, right, bottom = drawing_context.multiline_textbbox(
            (0, 0), text, font=font, spacing=4, align="left"
        )
        return right - left, bottom - top
    except AttributeError:
        return drawing_context.multiline_textsize(text, font=font, spacing=4)


def _break_word(
    drawing_context: ImageDraw.ImageDraw,
    word: str,
    text_font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    segments, current_segment = [], ""
    for character in word:
        test_segment = current_segment + character
        segment_width, _ = _measure(drawing_context, test_segment, text_font)
        if segment_width <= max_width or not current_segment:
            current_segment = test_segment
        else:
            segments.append(current_segment)
            current_segment = character
    if current_segment:
        segments.append(current_segment)
    return segments


def _wrap_to_width(
    drawing_context: ImageDraw.ImageDraw,
    text: str,
    text_font: ImageFont.ImageFont,
    max_width: int,
) -> str:
    words = text.split()
    if not words:
        return ""
    lines, current_line = [], ""
    for word in words:
        subparts = (
            [word]
            if _measure(drawing_context, word, text_font)[0] <= max_width
            else _break_word(drawing_context, word, text_font, max_width)
        )
        for subpart in subparts:
            line_candidate = (current_line + " " + subpart) if current_line else subpart
            if _measure(drawing_context, line_candidate, text_font)[0] <= max_width:
                current_line = line_candidate
            else:
                if current_line:
                    lines.append(current_line)
                current_line = subpart
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)


def _fit_text(
    drawing_context: ImageDraw.ImageDraw,
    title_text: str,
    font_path: str | None,
    max_width: int,
    max_height: int,
    min_font_size: int,
    max_font_size: int,
    wrap_text: bool = True,
):
    best_fit = None
    low_size, high_size = min_font_size, max_font_size
    while low_size <= high_size:
        test_size = (low_size + high_size) // 2
        test_font = _load_font(test_size, font_path)
        wrapped_text = (
            _wrap_to_width(drawing_context, title_text, test_font, max_width)
            if wrap_text
            else title_text
        )
        text_width, text_height = _measure(drawing_context, wrapped_text, test_font)
        if text_width <= max_width and text_height <= max_height:
            best_fit = (test_font, wrapped_text)
            low_size = test_size + 2
        else:
            high_size = test_size - 2
    if best_fit:
        return best_fit
    fallback_font = _load_font(min_font_size, font_path)
    return fallback_font, _wrap_to_width(
        drawing_context, title_text, fallback_font, max_width
    )


def add_title_above(
    image_or_path: str | Image.Image,
    title: str,
    *,
    bar_height_ratio: float = 0.12,
    bar_height_px: int | None = None,
    padding_x: int = 24,
    padding_y: int = 16,
    font_path: str | None = None,
    min_font_px: int = 14,
    wrap_text: bool = True,
    expand_bar_if_needed: bool = True,
    bar_color: str = "white",
    text_color: str = "black",
) -> Image.Image:
    base_image = (
        Image.open(image_or_path) if isinstance(image_or_path, str) else image_or_path
    )
    base_image = base_image.convert("RGBA")
    image_width, image_height = base_image.size
    bar_height = (
        bar_height_px
        if bar_height_px is not None
        else max(1, int(image_height * bar_height_ratio))
    )

    output_image = Image.new(
        "RGBA", (image_width, image_height + bar_height), bar_color
    )
    output_image.paste(
        base_image, (0, bar_height), base_image if base_image.mode == "RGBA" else None
    )
    drawing_context = ImageDraw.Draw(output_image)

    text_max_width = max(1, image_width - 2 * padding_x)
    text_max_height = max(1, bar_height - 2 * padding_y)

    title_font, wrapped_title_text = _fit_text(
        drawing_context,
        title,
        font_path,
        text_max_width,
        text_max_height,
        min_font_px,
        text_max_height,
        wrap_text,
    )
    title_width, title_height = _measure(
        drawing_context, wrapped_title_text, title_font
    )

    if expand_bar_if_needed and title_height + 2 * padding_y > bar_height:
        bar_height = title_height + 2 * padding_y
        output_image = Image.new(
            "RGBA", (image_width, image_height + bar_height), bar_color
        )
        output_image.paste(
            base_image,
            (0, bar_height),
            base_image if base_image.mode == "RGBA" else None,
        )
        drawing_context = ImageDraw.Draw(output_image)
        text_max_height = bar_height - 2 * padding_y
        title_font, wrapped_title_text = _fit_text(
            drawing_context,
            title,
            font_path,
            text_max_width,
            text_max_height,
            min_font_px,
            text_max_height,
            wrap_text,
        )
        title_width, title_height = _measure(
            drawing_context, wrapped_title_text, title_font
        )

    text_x = (image_width - title_width) // 2
    text_y = (bar_height - title_height) // 2
    drawing_context.multiline_text(
        (text_x, text_y),
        wrapped_title_text,
        font=title_font,
        fill=text_color,
        spacing=4,
        align="center",
    )
    return output_image


def _render_title_layout(
    frame_size: tuple[int, int],
    title: str,
    *,
    bar_height_ratio: float,
    bar_height_px: int | None,
    padding_x: int,
    padding_y: int,
    font_path: str | None,
    min_font_px: int,
    wrap_text: bool,
    expand_bar_if_needed: bool,
    bar_color: str,
    text_color: str,
) -> tuple[int, ImageFont.ImageFont, str, tuple[int, int]]:
    image_width, image_height = frame_size
    bar_height = (
        bar_height_px
        if bar_height_px is not None
        else max(1, int(image_height * bar_height_ratio))
    )
    temp_canvas = Image.new("RGBA", (image_width, image_height + bar_height), bar_color)
    drawing_context = ImageDraw.Draw(temp_canvas)

    text_max_width = max(1, image_width - 2 * padding_x)
    text_max_height = max(1, bar_height - 2 * padding_y)

    title_font, wrapped_title_text = _fit_text(
        drawing_context,
        title,
        font_path,
        text_max_width,
        text_max_height,
        min_font_px,
        text_max_height,
        wrap_text,
    )
    title_width, title_height = _measure(
        drawing_context, wrapped_title_text, title_font
    )

    if expand_bar_if_needed and title_height + 2 * padding_y > bar_height:
        bar_height = title_height + 2 * padding_y
        temp_canvas = Image.new(
            "RGBA", (image_width, image_height + bar_height), bar_color
        )
        drawing_context = ImageDraw.Draw(temp_canvas)
        text_max_height = bar_height - 2 * padding_y
        title_font, wrapped_title_text = _fit_text(
            drawing_context,
            title,
            font_path,
            text_max_width,
            text_max_height,
            min_font_px,
            text_max_height,
            wrap_text,
        )
        title_width, title_height = _measure(
            drawing_context, wrapped_title_text, title_font
        )

    text_x = (image_width - title_width) // 2
    text_y = (bar_height - title_height) // 2
    return bar_height, title_font, wrapped_title_text, (text_x, text_y)


def _process_frame_with_layout(
    frame_rgba: Image.Image,
    layout_tuple: tuple[int, ImageFont.ImageFont, str, tuple[int, int]],
    *,
    bar_color: str,
    text_color: str,
) -> Image.Image:
    frame_width, frame_height = frame_rgba.size
    bar_height, title_font, wrapped_title_text, (text_x, text_y) = layout_tuple
    composed_frame = Image.new(
        "RGBA", (frame_width, frame_height + bar_height), bar_color
    )
    composed_frame.paste(frame_rgba, (0, bar_height), frame_rgba)
    drawing_context = ImageDraw.Draw(composed_frame)
    drawing_context.multiline_text(
        (text_x, text_y),
        wrapped_title_text,
        font=title_font,
        fill=text_color,
        spacing=4,
        align="center",
    )
    return composed_frame


def _save_gif(
    frames_rgba_list: list[Image.Image],
    frame_durations_ms: list[int],
    loop_count: int,
    output_path: str,
) -> None:
    palette_frames = [
        frame.convert(
            "P", palette=Image.ADAPTIVE, colors=256, dither=Image.FLOYDSTEINBERG
        )
        for frame in frames_rgba_list
    ]
    first_frame, remaining_frames = palette_frames[0], palette_frames[1:]
    first_frame.save(
        output_path,
        save_all=True,
        append_images=remaining_frames,
        duration=frame_durations_ms,
        loop=loop_count,
        optimize=True,
        disposal=2,
    )


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
    expand_bar_if_needed: bool = True,
    bar_color: str = "white",
    text_color: str = "black",
) -> None:
    with Image.open(input_path) as source_image:
        is_animated_gif = (
            source_image.format == "GIF" and getattr(source_image, "is_animated", False)
        ) or output_path.lower().endswith(".gif")

        if is_animated_gif:
            output_frames_rgba: list[Image.Image] = []
            frame_durations_ms: list[int] = []
            frame_width, frame_height = source_image.size

            title_layout = _render_title_layout(
                (frame_width, frame_height),
                title,
                bar_height_ratio=bar_height_ratio,
                bar_height_px=bar_height_px,
                padding_x=padding_x,
                padding_y=padding_y,
                font_path=font_path,
                min_font_px=min_font_px,
                wrap_text=wrap_text,
                expand_bar_if_needed=expand_bar_if_needed,
                bar_color=bar_color,
                text_color=text_color,
            )

            for frame_index in range(getattr(source_image, "n_frames", 1)):
                source_image.seek(frame_index)
                frame_rgba = source_image.convert("RGBA")
                composed_frame_rgba = _process_frame_with_layout(
                    frame_rgba, title_layout, bar_color=bar_color, text_color=text_color
                )
                output_frames_rgba.append(composed_frame_rgba)
                frame_durations_ms.append(source_image.info.get("duration", 40))

            loop_count = source_image.info.get("loop", 0)
            _save_gif(output_frames_rgba, frame_durations_ms, loop_count, output_path)
            return

        single_image_with_title = add_title_above(
            source_image,
            title,
            bar_height_ratio=bar_height_ratio,
            bar_height_px=bar_height_px,
            padding_x=padding_x,
            padding_y=padding_y,
            font_path=font_path,
            min_font_px=min_font_px,
            wrap_text=wrap_text,
            expand_bar_if_needed=expand_bar_if_needed,
            bar_color=bar_color,
            text_color=text_color,
        )
        if output_path.lower().endswith((".jpg", ".jpeg")):
            single_image_with_title = single_image_with_title.convert("RGB")
        single_image_with_title.save(output_path)

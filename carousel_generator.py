import os
from PIL import Image, ImageDraw, ImageFont

# ── КОНСТАНТЫ ДИЗАЙНА ──────────────────────────────────────────────────────
CANVAS_W = 1080
CANVAS_H = 1350
BG_COLOR = "#1F2833"
PRIMARY_COLOR = "#66FCF1"
ACCENT_COLOR = "#45A29E"
MUTED_COLOR = "#C5C6C7"
SLIDE_NUM_COLOR = "#45A29E"
PADDING = 80
LINE_SPACING = 1.4

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD    = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ── ДАННЫЕ СЛАЙДОВ ─────────────────────────────────────────────────────────
SLIDES = [
    {
        "type": "HOOK",
        "title": "GPT vs Gemini:\nкто реально мощнее?",
        "subtitle": "6 фактов, которые изменят твоё мнение",
    },
    {
        "type": "CONTENT",
        "title": "Контекст: Gemini в 8 раз больше",
        "bullets": [
            "GPT-4: до 128K токенов",
            "Gemini 1.5 Pro: до 1 млн токенов",
            "Разница — целая книга за один запрос",
        ],
    },
    {
        "type": "CONTENT",
        "title": "Мультимодальность из коробки",
        "bullets": [
            "Gemini работает с видео нативно",
            "GPT — только через отдельные модели",
            "Google обучал на аудио, видео и тексте сразу",
        ],
    },
    {
        "type": "CONTENT",
        "title": "Данные: Gemini — в реальном времени",
        "bullets": [
            "GPT знает мир до даты среза обучения",
            "Gemini имеет доступ к поиску Google",
            "Актуальность — критична для бизнеса",
        ],
    },
    {
        "type": "CONTENT",
        "title": "Стоимость: GPT-4o дороже",
        "bullets": [
            "GPT-4o: $5 за 1M токенов (input)",
            "Gemini 1.5 Pro: $3.5 за 1M токенов",
            "Gemini Flash почти бесплатен",
        ],
    },
    {
        "type": "SUMMARY",
        "title": "Gemini побеждает по цифрам",
        "text": "Контекст, цена, реальное время — Gemini впереди.\nGPT силён в экосистеме и тонкой настройке.",
    },
    {
        "type": "CTA",
        "symbol": "✦",
        "title": "Сохрани — пригодится при выборе AI",
        "subtitle": "Подпишись, каждую неделю разбираем AI-инструменты",
    },
]


# ── УТИЛИТЫ ────────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def wrap_text(draw, text, font, max_width):
    """Разбивает текст на строки, не превышающие max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            test = current + " " + word
            w = draw.textbbox((0, 0), test, font=font)[2]
            if w <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit_text_to_box(draw, text, font_path, max_width, max_height,
                    size_max=90, size_min=18):
    for size in range(size_max, size_min - 1, -2):
        font = ImageFont.truetype(font_path, size)
        lines = wrap_text(draw, text, font, max_width)
        total_height = sum(
            draw.textbbox((0, 0), line, font=font)[3] for line in lines
        ) * LINE_SPACING
        if total_height <= max_height:
            return font, lines
    font = ImageFont.truetype(font_path, size_min)
    return font, wrap_text(draw, text, font, max_width)


def draw_text_lines(draw, lines, font, x, y, color, center=False, canvas_w=CANVAS_W):
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lh = bbox[3] - bbox[1]
        if center:
            lw = bbox[2] - bbox[0]
            draw.text(((canvas_w - lw) // 2, y), line, font=font, fill=color)
        else:
            draw.text((x, y), line, font=font, fill=color)
        y += int(lh * LINE_SPACING)
    return y


# ── ФОНОВЫЙ ЭФФЕКТ ─────────────────────────────────────────────────────────

def draw_background(image, draw, slide_type):
    accent = hex_to_rgb(ACCENT_COLOR)

    # Уголки-акценты (очень тонкие)
    corner_len = 120
    lw = 2
    alpha_color = accent + (38,)  # ~15% opacity — нужен RGBA режим

    # Верхний левый
    draw.line([(PADDING - 20, PADDING - 20), (PADDING - 20 + corner_len, PADDING - 20)], fill=ACCENT_COLOR, width=lw)
    draw.line([(PADDING - 20, PADDING - 20), (PADDING - 20, PADDING - 20 + corner_len)], fill=ACCENT_COLOR, width=lw)
    # Нижний правый
    draw.line([(CANVAS_W - PADDING + 20 - corner_len, CANVAS_H - PADDING + 20),
               (CANVAS_W - PADDING + 20, CANVAS_H - PADDING + 20)], fill=ACCENT_COLOR, width=lw)
    draw.line([(CANVAS_W - PADDING + 20, CANVAS_H - PADDING + 20 - corner_len),
               (CANVAS_W - PADDING + 20, CANVAS_H - PADDING + 20)], fill=ACCENT_COLOR, width=lw)

    if slide_type == "HOOK":
        # Крупный декоративный круг за текстом
        overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        cx, cy = CANVAS_W // 2, CANVAS_H // 2
        r = 380
        od.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                   outline=accent + (28,), width=3)
        r2 = 480
        od.ellipse([(cx - r2, cy - r2), (cx + r2, cy + r2)],
                   outline=accent + (14,), width=2)
        image.paste(Image.alpha_composite(image, overlay), (0, 0))


# ── РЕНДЕР СЛАЙДОВ ─────────────────────────────────────────────────────────

def render_slide(slide_data, slide_num, total_slides):
    image = Image.new("RGBA", (CANVAS_W, CANVAS_H), hex_to_rgb(BG_COLOR) + (255,))
    draw = ImageDraw.Draw(image)

    draw_background(image, draw, slide_data["type"])
    draw = ImageDraw.Draw(image)  # обновляем после paste

    stype = slide_data["type"]
    content_w = CANVAS_W - 2 * PADDING

    # ── HOOK ──────────────────────────────────────────────────────────────
    if stype == "HOOK":
        title_font, title_lines = fit_text_to_box(
            draw, slide_data["title"], FONT_BOLD,
            max_width=content_w, max_height=460,
            size_max=88, size_min=40
        )
        subtitle_font = ImageFont.truetype(FONT_REGULAR, 32)

        # Высоты блоков
        title_h = sum(draw.textbbox((0,0), l, font=title_font)[3] for l in title_lines) * LINE_SPACING
        line_gap = 30
        dec_line_h = 4 + line_gap * 2
        sub_lines = wrap_text(draw, slide_data["subtitle"], subtitle_font, content_w)
        sub_h = sum(draw.textbbox((0,0), l, font=subtitle_font)[3] for l in sub_lines) * LINE_SPACING

        total_h = title_h + dec_line_h + sub_h
        start_y = (CANVAS_H - total_h) // 2

        # Заголовок
        y = draw_text_lines(draw, title_lines, title_font,
                             PADDING, int(start_y), PRIMARY_COLOR, center=True)

        # Декоративная линия
        y += line_gap
        lx = (CANVAS_W - 200) // 2
        draw.rectangle([(lx, y), (lx + 200, y + 4)], fill=ACCENT_COLOR)
        y += 4 + line_gap

        # Подзаголовок
        draw_text_lines(draw, sub_lines, subtitle_font,
                        PADDING, y, MUTED_COLOR, center=True)

    # ── CONTENT ───────────────────────────────────────────────────────────
    elif stype == "CONTENT":
        title_font, title_lines = fit_text_to_box(
            draw, slide_data["title"], FONT_BOLD,
            max_width=content_w, max_height=180,
            size_max=52, size_min=28
        )
        y = PADDING
        y = draw_text_lines(draw, title_lines, title_font, PADDING, y, ACCENT_COLOR)
        y += 18
        draw.rectangle([(PADDING, y), (CANVAS_W - PADDING, y + 2)], fill=PRIMARY_COLOR)
        y += 30

        bullet_font = ImageFont.truetype(FONT_REGULAR, 36)
        for bullet in slide_data["bullets"]:
            bullet_text = "\u25b8  " + bullet
            b_lines = wrap_text(draw, bullet_text, bullet_font, content_w - 30)
            y = draw_text_lines(draw, b_lines, bullet_font, PADDING + 10, y, PRIMARY_COLOR)
            y += 20

    # ── SUMMARY ───────────────────────────────────────────────────────────
    elif stype == "SUMMARY":
        title_font, title_lines = fit_text_to_box(
            draw, slide_data["title"], FONT_BOLD,
            max_width=content_w, max_height=180,
            size_max=62, size_min=32
        )
        y = PADDING
        y = draw_text_lines(draw, title_lines, title_font, PADDING, y, PRIMARY_COLOR)
        y += 20
        draw.rectangle([(PADDING, y), (CANVAS_W - PADDING, y + 2)], fill=ACCENT_COLOR)
        y += 40

        text_font, text_lines = fit_text_to_box(
            draw, slide_data["text"], FONT_REGULAR,
            max_width=content_w, max_height=CANVAS_H - y - PADDING - 80,
            size_max=40, size_min=22
        )
        # Вертикальное центрирование в нижней половине
        text_h = sum(draw.textbbox((0,0), l, font=text_font)[3] for l in text_lines) * LINE_SPACING
        mid = CANVAS_H // 2
        text_y = max(y, mid + (CANVAS_H - mid - int(text_h)) // 2)
        draw_text_lines(draw, text_lines, text_font, PADDING, int(text_y), MUTED_COLOR)

    # ── CTA ───────────────────────────────────────────────────────────────
    elif stype == "CTA":
        symbol_font = ImageFont.truetype(FONT_BOLD, 90)
        title_font, title_lines = fit_text_to_box(
            draw, slide_data["title"], FONT_BOLD,
            max_width=content_w, max_height=260,
            size_max=60, size_min=28
        )
        subtitle_font = ImageFont.truetype(FONT_REGULAR, 28)
        sub_lines = wrap_text(draw, slide_data["subtitle"], subtitle_font, content_w)

        sym_bbox = draw.textbbox((0, 0), slide_data["symbol"], font=symbol_font)
        sym_h = sym_bbox[3] - sym_bbox[2]
        title_h = sum(draw.textbbox((0,0), l, font=title_font)[3] for l in title_lines) * LINE_SPACING
        sub_h = sum(draw.textbbox((0,0), l, font=subtitle_font)[3] for l in sub_lines) * LINE_SPACING
        total_h = 90 + 40 + title_h + 40 + sub_h
        start_y = (CANVAS_H - total_h) // 2

        # Символ
        sym_w = draw.textbbox((0, 0), slide_data["symbol"], font=symbol_font)[2]
        draw.text(((CANVAS_W - sym_w) // 2, int(start_y)), slide_data["symbol"],
                  font=symbol_font, fill=ACCENT_COLOR)
        y = int(start_y) + 100 + 40

        y = draw_text_lines(draw, title_lines, title_font,
                             PADDING, y, PRIMARY_COLOR, center=True)
        y += 40
        draw_text_lines(draw, sub_lines, subtitle_font,
                        PADDING, y, MUTED_COLOR, center=True)

    # Номер слайда (все слайды)
    num_font = ImageFont.truetype(FONT_REGULAR, 24)
    num_text = f"{slide_num}/{total_slides}"
    nb = draw.textbbox((0, 0), num_text, font=num_font)
    draw.text((CANVAS_W - PADDING - (nb[2] - nb[0]),
               CANVAS_H - PADDING // 2 - (nb[3] - nb[1])),
              num_text, font=num_font, fill=SLIDE_NUM_COLOR)

    return image.convert("RGB")


# ── MAIN ───────────────────────────────────────────────────────────────────

def main():
    output_dir = "carousel_output"
    os.makedirs(output_dir, exist_ok=True)
    total = len(SLIDES)

    type_labels = {"HOOK": "HOOK", "CONTENT": "CONTENT", "SUMMARY": "SUMMARY", "CTA": "CTA"}

    for i, slide in enumerate(SLIDES):
        img = render_slide(slide, i + 1, total)
        filename = os.path.join(output_dir, f"slide_{str(i+1).zfill(2)}.png")
        img.save(filename, "PNG", optimize=True)
        print(f"✓ Сохранён: {filename}  [{slide['type']}]")

    print()
    print("╔══════════════════════════════════════════╗")
    print("║        КАРУСЕЛЬ ГОТОВА ✓                 ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Тема: Чем GPT хуже Gemini               ║")
    print(f"║  Слайдов создано: {total}                      ║")
    print("║  Папка: ./carousel_output/               ║")
    print("║  Размер: 1080×1350px (4:5)               ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Файлы:                                  ║")
    for i, slide in enumerate(SLIDES):
        label = slide["type"]
        print(f"║  → slide_{str(i+1).zfill(2)}.png  [{label}]{'            '[len(label):]}║")
    print("╚══════════════════════════════════════════╝")


if __name__ == "__main__":
    main()

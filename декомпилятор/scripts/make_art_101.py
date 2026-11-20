#!/usr/bin/env python3
"""Арт для Parcoobe 1.0.1: логотип с объёмом и новые двери.

Делает и складывает в --out:
    sName.png      — титульный кадр 1920x1080 (PARCOOBE, объём, тень, «Version 1.0.1»)
    sDoor.png      — спрайт открытой двери 64x64
    sClosedoor.png — спрайт закрытой двери 64x64
    texture0.png   — текстурная страница 2048x2048 со всеми правками

Использование:
    python3 make_art_101.py --source ../../source --out /tmp/art
Требуется Pillow и шрифты BebasNeue.ttf / PixelifySans.ttf рядом со скриптом.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

BG = (22, 22, 22)
FILL = (255, 216, 157)
EXTRUDE = (196, 140, 66)
EXTRUDE_DARK = (126, 84, 36)
SHADOW = (8, 8, 8)
GREEN = (150, 235, 130)
WORD = "PARCOOBE"
VERSION_TEXT = "Version 2.0.1"

# оригинальные положения/ширины букв PARCOOB в sName (чтобы сохранить ритм)
ORIG_WIDTHS = [185, 207, 186, 184, 187, 187, 185]
ORIG_CAP = 347
ORIG_Y = 260
LETTER_GAP = 33


def _shade(color, k):
    return tuple(max(0, min(255, int(c * k))) for c in color)


def build_logo(font_path, version_font_path):
    w, h = 1920, 1080
    canvas = Image.new("RGBA", (w, h), BG + (255,))

    widths = ORIG_WIDTHS + [ORIG_WIDTHS[-1]]          # P A R C O O B E
    total = sum(widths) + LETTER_GAP * (len(widths) - 1)
    x = (w - total) // 2
    cap = ORIG_CAP

    word = Image.new("L", (w, h), 0)
    for ch, lw in zip(WORD, widths):
        glyph = ImageFont.truetype(font_path, 1000)
        tmp = Image.new("L", (1400, 1400), 0)
        ImageDraw.Draw(tmp).text((100, 100), ch, font=glyph, fill=255)
        arr = np.array(tmp) > 128
        if not arr.any():
            x += lw + LETTER_GAP
            continue
        yy, xx = np.where(arr)
        crop = tmp.crop((xx.min(), yy.min(), xx.max() + 1, yy.max() + 1))
        crop = crop.resize((lw, cap), Image.LANCZOS)
        word.paste(crop, (x, ORIG_Y), crop)
        x += lw + LETTER_GAP

    def draw_layer(color, mask, dx=0, dy=0, alpha=1.0):
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        m = Image.new("L", (w, h), 0)
        m.paste(mask, (dx, dy))
        if alpha < 1.0:
            m = m.point(lambda v: int(v * alpha))
        ov.paste(Image.new("RGBA", (w, h), color + (255,)), (0, 0), m)
        return ov

    # 1. мягкая тень от всего слова
    shadow = word.filter(ImageFilter.GaussianBlur(20))
    canvas = Image.alpha_composite(canvas, draw_layer(SHADOW, shadow, 8, 26, 0.85))

    # 2. объём (экструзия вниз-вправо)
    depth = 16
    for i in range(depth, 0, -1):
        k = 1.0 - 0.028 * (depth - i)
        col = _shade(EXTRUDE if i > depth // 2 else EXTRUDE_DARK, k)
        canvas = Image.alpha_composite(canvas, draw_layer(col, word, int(i * 0.72), int(i * 1.2)))

    # 3. золотое свечение вокруг букв
    for radius, color, alpha in ((30, (118, 82, 32), 0.9), (13, (168, 118, 44), 0.9)):
        canvas = Image.alpha_composite(
            canvas, draw_layer(color, word.filter(ImageFilter.GaussianBlur(radius)), 0, 0, alpha))
    # 4. фаска: тёмный кант и светлый верхний край
    canvas = Image.alpha_composite(canvas, draw_layer((255, 238, 200), word, -2, -3, 0.9))
    canvas = Image.alpha_composite(canvas, draw_layer(FILL, word))

    # 4. подпись версии
    vfont = ImageFont.truetype(version_font_path, 84)
    try:
        vfont.set_variation_by_name("Bold")
    except Exception:
        pass
    tmp = Image.new("L", (1400, 200), 0)
    ImageDraw.Draw(tmp).text((10, 10), VERSION_TEXT, font=vfont, fill=255)
    arr = np.array(tmp) > 100
    yy, xx = np.where(arr)
    vtxt = tmp.crop((xx.min(), yy.min(), xx.max() + 1, yy.max() + 1))
    vtxt = vtxt.resize((int(vtxt.width * 0.95), int(vtxt.height * 0.95)), Image.LANCZOS)
    vx = (w - vtxt.width) // 2
    vy = ORIG_Y + cap + 70
    canvas = Image.alpha_composite(
        canvas, draw_layer((40, 120, 40), vtxt.filter(ImageFilter.GaussianBlur(10)), vx, vy, 0.9))
    canvas = Image.alpha_composite(canvas, draw_layer(GREEN, vtxt, vx, vy))

    return canvas.convert("RGB")


def _door(closed):
    w = h = 64
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    frame = (74, 46, 24, 255)
    frame_hi = (110, 70, 36, 255)
    wood = (96, 58, 28, 255) if not closed else (72, 44, 22, 255)
    wood_hi = (128, 82, 40, 255) if not closed else (96, 60, 30, 255)
    wood_lo = (58, 34, 16, 255) if not closed else (44, 26, 12, 255)

    d.rectangle([0, 0, 63, 63], fill=frame)
    d.rectangle([2, 2, 61, 61], fill=frame_hi)
    d.rectangle([6, 6, 57, 63], fill=wood)
    for px in (6, 20, 34, 48):
        d.line([(px, 6), (px, 63)], fill=wood_lo)
        d.line([(px + 1, 6), (px + 1, 63)], fill=wood_hi)
    d.rectangle([6, 6, 57, 10], fill=wood_lo)
    d.rectangle([6, 6, 57, 8], fill=wood_hi)
    # ручка
    d.ellipse([44, 28, 52, 36], fill=(214, 170, 74, 255))
    d.ellipse([46, 30, 50, 34], fill=(255, 226, 140, 255))
    if closed:
        # замок и поперечная планка
        d.rectangle([8, 30, 40, 40], fill=(84, 52, 24, 255))
        d.rectangle([8, 30, 40, 32], fill=wood_hi)
        d.rectangle([20, 33, 30, 42], fill=(190, 150, 60, 255))
        d.rectangle([23, 36, 27, 39], fill=(40, 28, 12, 255))
    else:
        d.rectangle([8, 12, 56, 14], fill=wood_hi)
        d.rectangle([8, 50, 56, 52], fill=wood_lo)
    return img


def main():
    ap = argparse.ArgumentParser()
    base = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--source", default=os.path.join(base, "..", "..", "source"))
    ap.add_argument("--out", default=os.path.join(base, "art_out"))
    ap.add_argument("--word-font", default=os.path.join(base, "BebasNeue.ttf"))
    ap.add_argument("--version-font", default=os.path.join(base, "PixelifySans.ttf"))
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    logo = build_logo(args.word_font, args.version_font)
    logo.save(os.path.join(args.out, "sName.png"))

    door = _door(False)
    closed = _door(True)
    door.save(os.path.join(args.out, "sDoor.png"))
    closed.save(os.path.join(args.out, "sClosedoor.png"))

    page = Image.open(os.path.join(args.source, "textures", "Texture 0.png")).convert("RGBA")
    page.paste(logo.convert("RGBA"), (2, 2))            # sName
    page.paste(door, (138, 1942))                        # sDoor
    page.paste(closed, (1682, 1218))                     # sClosedoor
    page.save(os.path.join(args.out, "texture0.png"))
    print("готово:", args.out)


if __name__ == "__main__":
    main()

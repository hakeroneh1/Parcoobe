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

import art_tiles

BG = (22, 22, 22)
FILL = (255, 216, 157)
EXTRUDE = (196, 140, 66)
EXTRUDE_DARK = (126, 84, 36)
SHADOW = (8, 8, 8)
GREEN = (150, 235, 130)
WORD = "PARCOOBE"
VERSION_TEXT = "Version 2.0.6"

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


def _seamless_wall():
    """Кладка 64x64 без чёрной рамки по краям: соседние тайлы стыкуются без швов."""
    w = h = 64
    img = Image.new("RGBA", (w, h), (34, 20, 10, 255))
    d = ImageDraw.Draw(img)
    bw, bh, gap = 30, 14, 2
    y = 0
    row = 0
    while y < h:
        offset = 0 if row % 2 == 0 else -(bw + gap) // 2
        x = offset
        while x < w:
            x0 = max(0, x)
            x1 = min(w, x + bw)
            if x1 > x0:
                d.rectangle([x0, y, x1, y + bh], fill=(171, 108, 45, 255))
                d.line([(x0, y), (x1, y)], fill=(228, 144, 61, 255))
                d.line([(x0, y + bh), (x1, y + bh)], fill=(113, 71, 30, 255))
            x += bw + gap
        y += bh + gap
        row += 1
    return img



def _fin_screen(page2, title_font):
    """Финальный экран: только заголовок «Спасибо за прохождение» и подпись версии.

    Заголовок вырезается из оригинальной картинки sFin (нарисован от руки,
    кириллица в игровом шрифте отсутствует), длинная простыня текста убирается.
    """
    src = page2.crop((2, 726, 2 + 1280, 726 + 720))
    top = src.crop((0, 0, 1280, 110))
    arr = np.array(top.convert("RGB")).astype(int).sum(axis=2)
    ys, xs = np.where(arr > 120)          # всё, что не чёрный фон
    if len(xs) == 0:
        raise SystemExit("не нашёл заголовок на sFin")
    title = src.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    title = title.resize((int(title.width * 0.72), int(title.height * 0.72)), Image.LANCZOS)

    img = Image.new("RGBA", (1280, 720), (18, 16, 20, 255))
    x = (1280 - title.width) // 2
    y = 250 - title.height // 2
    img.alpha_composite(title, (x, y))

    d = ImageDraw.Draw(img)
    sub = ImageFont.truetype(title_font, 96)
    for text, fy, col in (("PARCOOBE", 430, (150, 235, 130)),
                          (VERSION_TEXT.upper(), 540, (200, 200, 200)),
                          ("SKR.SH/SEZ10UVOWVU", 620, (120, 120, 120))):
        tmp = Image.new("L", (1200, 200), 0)
        ImageDraw.Draw(tmp).text((10, 10), text, font=sub, fill=255)
        bb = tmp.getbbox()
        cut = tmp.crop(bb)
        k = 0.72 if fy < 600 else 0.34
        cut = cut.resize((int(cut.width * k), int(cut.height * k)), Image.LANCZOS)
        img.alpha_composite(Image.merge("RGBA", (Image.new("L", cut.size, col[0]),
                                                Image.new("L", cut.size, col[1]),
                                                Image.new("L", cut.size, col[2]),
                                                cut)),
                            ((1280 - cut.width) // 2, fy))
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
    page2 = Image.open(os.path.join(args.source, "textures", "Texture 2.png")).convert("RGBA")
    page1 = Image.open(os.path.join(args.source, "textures", "Texture 1.png")).convert("RGBA")
    page.paste(logo.convert("RGBA"), (2, 2))            # sName
    # свои тайлы: кладка, шипы, батут (всё рисуется с нуля, стыкуется без швов)
    wall_tile = art_tiles.brick_tile()
    wall_tile.save(os.path.join(args.out, "sWall.png"))
    page.paste(wall_tile, (682, 1946))                   # sWall

    spikes = art_tiles.spikes_tile()
    spikes.save(os.path.join(args.out, "sDanger.png"))
    page.paste(spikes, (534, 1810))                      # sDanger

    pad = art_tiles.pad_tile()
    pad.save(os.path.join(args.out, "sJumpplatform.png"))
    page.paste(pad, (2, 2010))                           # sJumpplatform

    # стена на фоне — та же кладка, но тёмная
    bg_wall = art_tiles.tile_bricks(1280, 720, base=(58, 62, 80), mortar=(18, 20, 30))
    bg_wall.save(os.path.join(args.out, "bricks_background.png"))
    page.paste(bg_wall, (2, 1086))                       # bricks_background
    page.paste(door, (138, 1942))                        # sDoor
    page.paste(closed, (1682, 1218))                     # sClosedoor
    page.save(os.path.join(args.out, "texture0.png"))

    # финальный экран: короткий заголовок вместо простыни текста (sFin на Texture 2)
    page2.paste(_fin_screen(page2, args.version_font), (2, 726))
    page2.save(os.path.join(args.out, "texture2.png"))

    # своё ночное небо вместо оригинального dead_city (Texture 1, 2,2 1280x720)
    sky = art_tiles.city_background()
    sky.save(os.path.join(args.out, "dead_city.png"))
    page1.paste(sky, (2, 2))
    page1.save(os.path.join(args.out, "texture1.png"))
    print("готово:", args.out)


if __name__ == "__main__":
    main()

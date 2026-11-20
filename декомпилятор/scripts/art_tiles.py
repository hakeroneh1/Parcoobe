#!/usr/bin/env python3
"""Свои тайлы и фоны для Parcoobe 2.0.4 (без оригинальной графики).

Всё рисуется процедурно, поэтому тайлы стыкуются без швов:
    brick_tile()        — кладка 64x64 для стен (oWall -> sWall)
    brick_tile_bg()     — та же кладка, но тёмная, для стены на фоне (bricks_background)
    spikes_tile()       — шипы 64x64 для oDanger (sDanger)
    pad_tile()          — батут 64x32 (sJumpplatform, origin 32,32)
    night_background()  — ночное небо с луной, звёздами и городом 1280x720 (dead_city)

Кладка рисуется с переносом через край: кирпич, вылезающий за правую границу,
дублируется слева, поэтому при тайлинге швов не видно.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter


def _shade(color, k):
    return tuple(max(0, min(255, int(c * k))) for c in color)


def brick_tile(w=64, h=64, base=(154, 96, 46), mortar=(38, 24, 14), seed=7):
    """Кладка 64x64 без швов: 3 ряда кирпича со смещением, перенос через край."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h), mortar + (255,))
    d = ImageDraw.Draw(img)
    row_h = h // 3
    brick_w = w // 2
    for row in range(3):
        y = row * row_h
        offset = 0 if row % 2 == 0 else brick_w // 2
        for i in range(-1, 3):
            x = i * brick_w + offset
            colour = _shade(base, 0.86 + rnd.random() * 0.28)
            x0, x1 = x + 1, x + brick_w - 2
            y0, y1 = y + 1, y + row_h - 2
            # перенос через край — залог бесшовности
            for dx in (-w, 0, w):
                a, b = x0 + dx, x1 + dx
                if b < 0 or a > w:
                    continue
                d.rectangle([a, y0, b, y1], fill=colour + (255,))
                d.line([(a, y0), (b, y0)], fill=_shade(colour, 1.22) + (255,))
                d.line([(a, y1), (b, y1)], fill=_shade(colour, 0.68) + (255,))
                d.line([(a, y0), (a, y1)], fill=_shade(colour, 0.8) + (255,))
                d.line([(b, y0), (b, y1)], fill=_shade(colour, 0.8) + (255,))
    # мелкая крошка, чтобы стена не выглядела пластиковой
    for _ in range(90):
        px, py = rnd.randrange(w), rnd.randrange(h)
        c = _shade(base, 0.7 + rnd.random() * 0.5)
        d.point((px, py), fill=c + (255,))
    return img


def tile_bricks(w, h, base, mortar, seed=11, scale=1):
    """Большая стена из той же кладки (для фонового слоя)."""
    t = brick_tile(base=base, mortar=mortar, seed=seed)
    if scale != 1:
        t = t.resize((t.width * scale, t.height * scale), Image.NEAREST)
    img = Image.new("RGBA", (w, h), mortar + (255,))
    for y in range(0, h, t.height):
        for x in range(0, w, t.width):
            img.alpha_composite(t, (x, y))
    return img


def spikes_tile(w=64, h=64):
    """Шипы: тёмное основание и 4 стальных зуба с бликом."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    plate = (46, 40, 48, 255)
    d.rectangle([0, h - 14, w - 1, h - 1], fill=plate)
    d.line([(0, h - 14), (w - 1, h - 14)], fill=(74, 66, 78, 255))
    for i in range(4):
        cx = i * (w // 4) + w // 8
        top = 8 + (i % 2) * 3
        d.polygon([(cx - w // 10, h - 14), (cx, top), (cx + w // 10, h - 14)],
                  fill=(198, 202, 214, 255))
        d.line([(cx, top), (cx - w // 18, h - 14)], fill=(236, 240, 250, 255))
        d.line([(cx, top), (cx + w // 18, h - 14)], fill=(120, 124, 140, 255))
    return img


def pad_tile(w=64, h=32):
    """Батут: тёмная рама, пружина и яркая площадка."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([2, h - 8, w - 3, h - 1], fill=(40, 52, 34, 255))
    d.rectangle([6, h - 22, w - 7, h - 9], fill=(58, 74, 48, 255))
    for i in range(6):
        x = 8 + i * 8
        d.line([(x, h - 10), (x + 4, h - 20)], fill=(150, 235, 130, 255))
        d.line([(x + 4, h - 20), (x + 8, h - 10)], fill=(96, 170, 84, 255))
    d.rectangle([4, 0, w - 5, 6], fill=(150, 235, 130, 255))
    d.rectangle([4, 0, w - 5, 2], fill=(206, 255, 190, 255))
    return img


def night_background(w=1280, h=720, seed=2024):
    """Своё ночное небо: градиент, луна, звёзды и силуэт города.

    Горизонтальный перенос: всё, что выходит за край, дублируется с другой стороны,
    поэтому слой можно тайлить по горизонтали.
    """
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    # небо
    top = (10, 12, 26)
    bottom = (74, 38, 40)
    bands = 180
    for i in range(bands):
        t = i / (bands - 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * (t ** 0.85)) for j in range(3))
        y0 = int(h * 0.62 * i / bands)
        y1 = int(h * 0.62 * (i + 1) / bands) + 1
        d.rectangle([0, y0, w, y1], fill=c + (255,))

    # звёзды
    for _ in range(260):
        x = rnd.randrange(w)
        y = rnd.randrange(int(h * 0.55))
        r = rnd.choice([1, 1, 1, 2])
        k = rnd.random()
        col = (235, 235, 250) if k > 0.4 else (200, 210, 255)
        a = int(120 + 135 * rnd.random())
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))

    # луна с ореолом
    mx, my, mr = int(w * 0.77), int(h * 0.17), 44
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([mx - mr * 3, my - mr * 3, mx + mr * 3, my + mr * 3],
                                 fill=(255, 240, 200, 46))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(28)))
    d = ImageDraw.Draw(img)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(246, 240, 214, 255))
    d.ellipse([mx - mr + 10, my - mr + 6, mx - mr + 34, my - mr + 28], fill=(228, 222, 200, 255))
    d.ellipse([mx + 4, my + 8, mx + 26, my + 30], fill=(228, 222, 200, 255))

    # дальний город
    def skyline(color, base_y, min_h, max_h, step, width_dev):
        x = 0
        while x < w:
            bw = int(step * (0.6 + rnd.random() * width_dev))
            bh = rnd.randrange(min_h, max_h)
            for dx in (-w, 0, w):
                d.rectangle([x + dx, base_y - bh, x + dx + bw, h], fill=color + (255,))
            # окна
            for wy in range(base_y - bh + 14, h - 20, 26):
                for wx in range(x + 6, x + bw - 6, 16):
                    if rnd.random() < 0.22:
                        c = (250, 210, 120, 255) if rnd.random() < 0.7 else (150, 200, 250, 255)
                        d.rectangle([wx, wy, wx + 6, wy + 10], fill=c)
            x += bw + rnd.randrange(4, 16)

    skyline((26, 24, 34), int(h * 0.78), 120, 300, 90, 0.8)
    skyline((16, 15, 22), int(h * 0.86), 60, 190, 70, 0.9)

    # земля
    d.rectangle([0, h - 40, w, h], fill=(12, 11, 16, 255))
    return img

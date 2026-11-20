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
    """Кладка 64x64 без швов: 4 ряда по 16 px, кирпич 32x14, раствор 2 px.

    Все размеры делят 64 нацело, поэтому на стыке тайлов не остаётся полосы раствора
    (именно из-за этого раньше были видны «разрывы» между кирпичами).
    """
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h), mortar + (255,))
    d = ImageDraw.Draw(img)
    row_h = 32
    brick_w = 32
    for row in range(h // row_h):
        y = row * row_h
        offset = 0 if row % 2 == 0 else brick_w // 2
        for k in range(-1, (w // brick_w) + 1):
            x = k * brick_w + offset
            colour = _shade(base, 0.88 + rnd.random() * 0.24)
            for dx in (-w, 0, w):
                x0, x1 = x + dx + 1, x + dx + brick_w - 2
                y0, y1 = y + 1, y + row_h - 2
                if x1 < 0 or x0 >= w:
                    continue
                d.rectangle([max(x0, 0), y0, min(x1, w - 1), y1], fill=colour + (255,))
                d.line([(max(x0, 0), y0), (min(x1, w - 1), y0)], fill=_shade(colour, 1.20) + (255,))
                d.line([(max(x0, 0), y1), (min(x1, w - 1), y1)], fill=_shade(colour, 0.70) + (255,))
    for _ in range(70):
        px, py = rnd.randrange(w), rnd.randrange(h)
        d.point((px, py), fill=_shade(base, 0.7 + rnd.random() * 0.45) + (255,))
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
    """Батут: металлическая рама, толстая пружина и светящаяся площадка."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # основание
    d.rectangle([1, h - 7, w - 2, h - 1], fill=(28, 34, 26, 255))
    d.rectangle([1, h - 7, w - 2, h - 6], fill=(58, 72, 52, 255))
    # пружина
    for i in range(7):
        x = 6 + i * 8
        d.line([(x, h - 8), (x + 4, h - 16)], fill=(196, 214, 190, 255), width=2)
        d.line([(x + 4, h - 16), (x + 8, h - 8)], fill=(126, 148, 122, 255), width=2)
    # площадка
    d.rectangle([2, 4, w - 3, 12], fill=(96, 168, 86, 255))
    d.rectangle([2, 4, w - 3, 7], fill=(150, 235, 130, 255))
    d.rectangle([2, 4, w - 3, 5], fill=(214, 255, 198, 255))
    # блики по краям
    d.line([(2, 12), (w - 3, 12)], fill=(52, 96, 48, 255))
    return img



def city_background(w=1280, h=720, seed=77):
    """Фон в стиле оригинала: тёмный коричневый градиент, дымка и чёрный силуэт города.

    Без луны и звёзд — только мрачная дымка, трубы, краны и крыши, как в исходной игре.
    """
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)

    # небо: от почти чёрного сверху к тёмно-красной дымке у горизонта
    top = (7, 5, 6)
    bottom = (96, 34, 22)
    bands = 220
    for i in range(bands):
        t = i / (bands - 1)
        c = tuple(int(top[j] + (bottom[j] - top[j]) * (t ** 1.6)) for j in range(3))
        y0 = int(h * 0.66 * i / bands)
        y1 = int(h * 0.66 * (i + 1) / bands) + 1
        d.rectangle([0, y0, w, y1], fill=c + (255,))

    # дымка над городом
    haze = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse([-w // 4, int(h * 0.30), w + w // 4, int(h * 0.78)], fill=(150, 58, 34, 60))
    img.alpha_composite(haze.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(img)

    def tower(x, bw, bh, colour):
        y0 = int(h * 0.80) - bh
        for dx in (-w, 0, w):
            d.rectangle([x + dx, y0, x + dx + bw, h], fill=colour + (255,))
        return y0

    # дальний ряд: низкие дома
    x = -20
    while x < w:
        bw = rnd.randrange(40, 110)
        bh = rnd.randrange(30, 120)
        tower(x, bw, bh, (26, 15, 12))
        x += bw + rnd.randrange(6, 26)

    # средний ряд: трубы и баки
    x = -10
    while x < w:
        bw = rnd.randrange(30, 80)
        bh = rnd.randrange(80, 210)
        top_y = tower(x, bw, bh, (16, 9, 8))
        # труба
        if rnd.random() < 0.55:
            px = x + rnd.randrange(4, max(5, bw - 8))
            d.rectangle([px, top_y - rnd.randrange(10, 40), px + 6, top_y], fill=(16, 9, 8, 255))
        x += bw + rnd.randrange(10, 40)

    # ближний ряд: крыши с зубцами и кранами
    x = -30
    while x < w:
        bw = rnd.randrange(70, 180)
        bh = rnd.randrange(150, 290)
        top_y = tower(x, bw, bh, (9, 5, 5))
        # зубцы
        for k in range(rnd.randrange(2, 6)):
            zx = x + rnd.randrange(4, max(5, bw - 10))
            d.rectangle([zx, top_y - 8, zx + 12, top_y], fill=(9, 5, 5, 255))
        # кран
        if rnd.random() < 0.35:
            cx = x + bw // 2
            d.line([(cx, top_y), (cx, top_y - 70)], fill=(9, 5, 5, 255), width=4)
            d.line([(cx - 40, top_y - 60), (cx + 46, top_y - 60)], fill=(9, 5, 5, 255), width=4)
            d.line([(cx + 40, top_y - 60), (cx + 40, top_y - 30)], fill=(9, 5, 5, 255), width=2)
        x += bw + rnd.randrange(4, 24)

    # земля
    d.rectangle([0, int(h * 0.80), w, h], fill=(6, 4, 4, 255))
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

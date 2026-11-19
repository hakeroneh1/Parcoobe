#!/usr/bin/env python3
"""Перерисовать титульный логотип игры: PARCOOB -> PARCOOBE.

Логотип в игре — это спрайт `sName`: картинка 1920x1080 внутри текстурной страницы
`Texture 0` по смещению (2,2). Скрипт берёт оригинальный кадр спрайта, стирает
старое слово, рисует новое тем же стилем (золотая заливка + оранжевое свечение,
шрифт Bebas Neue), сохраняет подпись «Alpha 0.0.11» и складывает готовые файлы:

    sName.png       — новый кадр спрайта (1920x1080)
    texture0.png    — текстурная страница 2048x2048 с вклеенным логотипом

Дальше страница подставляется в data.win:

    ../run.sh replace ../build/data.win \
        --textures "Texture 0=texture0.png" --output ../build/data.win

Требуется Pillow и файл шрифта Bebas Neue (BebasNeue.ttf) рядом или в --font.
Использование:
    python3 rebuild_logo.py --source ../../source --out /tmp/logo
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

BG = (22, 22, 22)
FILL = (255, 216, 157)
GLOW = [(26, (120, 84, 34), 0.95), (14, (160, 112, 38), 0.95), (6, (210, 158, 60), 1.0)]
WORD = "PARCOOBE"


def build(source_dir, font_path, out_dir):
    sprite = os.path.join(source_dir, "sprites", "sName_0.png")
    page_path = os.path.join(source_dir, "textures", "Texture 0.png")

    src = Image.open(sprite).convert("RGB")
    w, h = src.size
    a = np.array(src).astype(int)

    # границы старого слова: плотная золотая заливка
    strong = (a[..., 0] > 200) & (a[..., 1] > 140) & (a[..., 2] < 160)
    ys, xs = np.where(strong)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    cap_h = y1 - y0 + 1
    center_x = (x0 + x1) // 2
    old_w = x1 - x0 + 1

    # новое слово
    probe = ImageFont.truetype(font_path, 1000)
    tmp = Image.new("L", (9000, 2200), 0)
    ImageDraw.Draw(tmp).text((100, 100), WORD, font=probe, fill=255)
    arr = np.array(tmp) > 128
    yy, xx = np.where(arr)
    text = tmp.crop((xx.min(), yy.min(), xx.max() + 1, yy.max() + 1))

    new_cap = int(round(cap_h * 0.945))
    word_w = int(round(old_w * 7 / 6.0 * (new_cap / float(cap_h))))
    mask = text.resize((word_w, new_cap), Image.LANCZOS)
    pos = (center_x - word_w // 2, y0 + (cap_h - new_cap) // 2)

    def layer(color, m, scale_alpha=1.0):
        ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ov.paste(Image.new("RGBA", (w, h), color), (0, 0),
                 m.point(lambda v, s=scale_alpha: int(v * s)))
        return ov

    glyph = Image.new("L", (w, h), 0)
    glyph.paste(mask, pos)

    canvas = Image.new("RGBA", (w, h), BG + (255,))
    for radius, color, alpha in sorted(GLOW, reverse=True):
        canvas = Image.alpha_composite(
            canvas, layer(color, glyph.filter(ImageFilter.GaussianBlur(radius)), alpha))
    canvas = Image.alpha_composite(canvas, layer(FILL + (255,), glyph, 1.0))
    out = canvas.convert("RGB")

    # вернуть оригинальную подпись «Alpha 0.0.11» (зелёные пиксели и их ореол)
    oa = np.array(src).astype(int)
    green = (oa[..., 1] > oa[..., 0] + 18) & (oa[..., 1] > oa[..., 2] + 18)
    gm = Image.fromarray((green * 255).astype(np.uint8))
    halo = gm.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(3))
    sub = Image.fromarray(np.maximum(np.array(halo), np.array(gm)).astype(np.uint8))
    out.paste(src, (0, 0), sub)

    os.makedirs(out_dir, exist_ok=True)
    sprite_out = os.path.join(out_dir, "sName.png")
    out.save(sprite_out)

    page = Image.open(page_path).convert("RGBA")
    page.paste(out.convert("RGBA"), (2, 2))
    page_out = os.path.join(out_dir, "texture0.png")
    page.save(page_out)

    print(f"готово: {sprite_out}, {page_out}")
    return sprite_out, page_out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=os.path.join(os.path.dirname(__file__), "..", "..", "source"))
    ap.add_argument("--font", default=os.path.join(os.path.dirname(__file__), "BebasNeue.ttf"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "logo_out"))
    args = ap.parse_args()
    build(os.path.abspath(args.source), os.path.abspath(args.font), os.path.abspath(args.out))

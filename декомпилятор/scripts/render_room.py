#!/usr/bin/env python3
"""Собрать PNG-превью комнаты из декомпилированных данных.

Берёт source/rooms/<room>.json, source/metadata/objects.json, source/metadata/sprites.json
и PNG-кадры спрайтов из source/sprites/, рисует инстансы на фоне цвета комнаты.

Пример:
    python3 render_room.py lvl_1 out.png
"""
import json
import os
import sys

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "source"))


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    room_name = sys.argv[1] if len(sys.argv) > 1 else "lvl_1"
    out_path = sys.argv[2] if len(sys.argv) > 2 else f"{room_name}.png"

    room = load(os.path.join("rooms", f"{room_name}.json"))
    objects = {o["name"]: o for o in load(os.path.join("metadata", "objects.json"))}
    sprites = {s["name"]: s for s in load(os.path.join("metadata", "sprites.json"))}

    width, height = int(room["width"]), int(room["height"])
    bg = room.get("background_color") or 0xFF000000
    canvas = Image.new("RGBA", (width, height),
                       ((bg >> 16) & 0xFF, (bg >> 8) & 0xFF, bg & 0xFF, 0xFF))

    drawn = 0
    for inst in room["instances"]:
        obj = objects.get(inst["object"])
        if not obj or not obj.get("sprite"):
            continue
        sp = sprites.get(obj["sprite"])
        if not sp:
            continue
        frame = os.path.join(ROOT, "sprites", f"{sp['name']}_0.png")
        if not os.path.exists(frame):
            continue

        img = Image.open(frame).convert("RGBA")
        sx = inst.get("scale_x", 1) or 1
        sy = inst.get("scale_y", 1) or 1
        if sx != 1 or sy != 1:
            img = img.resize((max(1, int(img.width * sx)), max(1, int(img.height * sy))),
                             Image.NEAREST)

        x = inst["x"] - int(sp["origin_x"] * sx)
        y = inst["y"] - int(sp["origin_y"] * sy)
        canvas.alpha_composite(img, (x, y))
        drawn += 1

    canvas.convert("RGB").save(out_path)
    print(f"{room_name}: {drawn} инстансов -> {out_path}")


if __name__ == "__main__":
    main()

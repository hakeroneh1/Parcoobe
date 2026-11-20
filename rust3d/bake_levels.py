#!/usr/bin/env python3
"""Запекание уровней из source/rooms/*.json в rust3d/assets/levels.json.

Берёт только то, что нужно 3D-клиенту: геометрию стен, опасности, батуты, двери,
врагов и точку старта игрока. Координаты — в «пикселях» комнаты (1 px = 1 юнит).
"""
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOMS = os.path.join(ROOT, "source", "rooms")
META = os.path.join(ROOT, "source", "metadata")
OUT = os.path.join(ROOT, "rust3d", "assets", "levels.json")

LEVELS = ["lvl_1", "lvl_2", "lvl_3", "lvl_4", "lvl_5", "lvl_6", "lvl_7", "lvl_8",
          "chapter_1", "chapter_2"]

OBJECT_KIND = {
    "oWall": "walls",
    "oDanger": "hazards",
    "oJumpplatform": "jumps",
    "oDoor": "doors",
    "oDoorHard": "doors",
    "oDoor2player": "doors",
    "oDoorlevelselect": "doors",
    "oDoorSkins": "doors",
    "oNext": "doors",
    "oClosedoor": "closes",
    "oMushroomBleb": "enemies",
}


def main():
    sprites = {s["name"]: s for s in json.load(open(os.path.join(META, "sprites.json")))}
    objects = {o["name"]: o for o in json.load(open(os.path.join(META, "objects.json")))}

    levels = []
    for name in LEVELS:
        room = json.load(open(os.path.join(ROOMS, name + ".json")))
        data = {
            "name": name,
            "width": room["width"],
            "height": room["height"],
            "bg": room["background_color"],
            "start": [0.0, 0.0],
            "walls": [], "hazards": [], "jumps": [],
            "doors": [], "closes": [], "enemies": [],
        }
        for inst in room["instances"]:
            obj = inst["object"]
            if obj == "oPlayer":
                data["start"] = [float(inst["x"]), float(inst["y"])]
                continue
            kind = OBJECT_KIND.get(obj)
            if not kind:
                continue
            sprite_name = (objects.get(obj) or {}).get("sprite")
            sp = sprites.get(sprite_name) if sprite_name else None
            if not sp:
                continue
            sx = inst.get("scale_x", 1.0) or 1.0
            sy = inst.get("scale_y", 1.0) or 1.0
            x = inst["x"] - sp["origin_x"] * sx
            y = inst["y"] - sp["origin_y"] * sy
            w = sp["width"] * sx
            h = sp["height"] * sy
            data[kind].append([round(x, 2), round(y, 2), round(w, 2), round(h, 2)])
        # комнаты без игрока или без стен пропускаем
        if data["start"] == [0.0, 0.0] or not data["walls"]:
            print("skip", name)
            continue
        levels.append(data)
        print(name, "walls", len(data["walls"]), "hazards", len(data["hazards"]),
              "doors", len(data["doors"]), "enemies", len(data["enemies"]))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"levels": levels}, f, separators=(",", ":"))
    print("->", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()

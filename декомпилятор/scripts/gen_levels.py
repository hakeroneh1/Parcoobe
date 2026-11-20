#!/usr/bin/env python3
"""Генерация уровней lvl_1..lvl_5 (5 штук с нуля, сетка 32 px).

Пишет уровни/lvl_N.json в формате, который читает build_101.csx:
    [[object_name, x, y, scale_x, scale_y], ...]

Геометрия — как в оригинальных комнатах:
  комната 1280x720 (40 x 22 клеток по 32 px);
  oWall/oDanger/oDoor — origin (0,0), спрайт 64x64, scale 0.5 -> клетка 32x32;
  пол — нижняя клетка, её верх = 688 (row 21);
  игрок стоит на полу: y = 688, scale 0.5 (как в Menu и оригинальном lvl_1);
  батут — origin (32,32), ставится центром на поверхность (y = 688);
  дверь — 64x96 (scale 1.0 x 1.5), стоит на полу: x = 1184, y = 592.

Запуск из корня репозитория:  python3 декомпилятор/scripts/gen_levels.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "уровни")

T = 32
COLS, ROWS = 40, 22
FLOOR_ROW = ROWS - 1          # 21
FLOOR_Y = FLOOR_ROW * T + 16  # 688 — как в оригинальных комнатах

PLAYER_Y = FLOOR_Y            # как в оригинале: игрок стоит ровно на полу
DOOR_X, DOOR_Y = 1184, 592


def blank():
    """Пустая комната: потолок, пол, боковые стены."""
    g = [[" "] * COLS for _ in range(ROWS)]
    for c in range(COLS):
        g[0][c] = "#"
        g[FLOOR_ROW][c] = "#"
    for r in range(ROWS):
        g[r][0] = "#"
        g[r][COLS - 1] = "#"
    return g


def fill(g, row, c1, c2, ch="#"):
    for c in range(c1, c2 + 1):
        if 0 <= c < COLS and 0 <= row < ROWS:
            g[row][c] = ch


def block(g, row1, row2, c1, c2, ch="#"):
    for r in range(row1, row2 + 1):
        fill(g, r, c1, c2, ch)


def pit(g, c1, c2):
    """Дырка в полу (пустота), чтобы падать вниз было чем."""
    fill(g, FLOOR_ROW, c1, c2, " ")


def spikes(g, c1, c2):
    """Шипы на полу: стоят вровень с полом, как в оригинальных уровнях."""
    fill(g, FLOOR_ROW, c1, c2, "^")


def convert(name, g, player_col, pads=(), enemies=()):
    inst = []
    for r in range(ROWS):
        for c in range(COLS):
            ch = g[r][c]
            x, y = c * T, r * T + 16
            if ch == "#":
                inst.append(["oWall", x, y, 0.5, 0.5])
            elif ch == "^":
                inst.append(["oDanger", x, y, 0.5, 0.5])
    for (c, surface_row) in pads:
        # батут — origin в центре, центр ставим на поверхность (как в оригинале)
        inst.append(["oJumpplatform", c * T + T // 2, surface_row * T + 16, 0.5, 0.5])
    for (c, surface_row) in enemies:
        # гриб стоит на поверхности: спрайт 64x64 scale 0.75 -> 48 px
        inst.append(["oMushroomBleb", c * T + T // 2, surface_row * T + 16 - 24, 0.75, 0.75])
    inst.append(["oDoor", DOOR_X, DOOR_Y, 1.0, 1.5])
    inst.append(["oPlayer", player_col * T + T // 2, PLAYER_Y, 0.5, 0.5])
    return {"name": name, "width": COLS * T, "height": ROWS * T, "instances": inst}


def lvl_1():
    """Обучение: ровный пол, ступеньки, один батут, немного шипов."""
    g = blank()
    block(g, 17, 18, 8, 12)
    block(g, 14, 15, 14, 18)
    block(g, 11, 12, 22, 26)
    spikes(g, 30, 31)
    return convert("lvl_1", g, 2, pads=[(5, FLOOR_ROW)])


def lvl_2():
    """Две ямы и полка над ними: прыжки через пустоту."""
    g = blank()
    pit(g, 12, 15)
    pit(g, 26, 29)
    block(g, 18, 18, 12, 15)
    block(g, 18, 18, 26, 29)
    spikes(g, 20, 21)
    return convert("lvl_2", g, 2, pads=[(7, FLOOR_ROW), (31, FLOOR_ROW)])


def lvl_3():
    """Три полосы шипов и платформы, чтобы их перепрыгивать."""
    g = blank()
    spikes(g, 8, 10)
    spikes(g, 17, 19)
    spikes(g, 25, 27)
    block(g, 17, 18, 12, 14)
    block(g, 17, 18, 21, 23)
    block(g, 14, 15, 29, 32)
    return convert("lvl_3", g, 2, pads=[(13, FLOOR_ROW), (30, FLOOR_ROW)])


def lvl_4():
    """Подъём по полкам и яма перед дверью."""
    g = blank()
    pit(g, 30, 33)
    block(g, 18, 18, 6, 10)
    block(g, 15, 15, 12, 17)
    block(g, 12, 12, 19, 24)
    block(g, 9, 9, 26, 32)
    spikes(g, 20, 21)
    return convert("lvl_4", g, 2, pads=[(4, FLOOR_ROW), (14, 18), (28, 9)])


def lvl_5():
    """Финал: две ямы, шипы, батуты."""
    g = blank()
    pit(g, 9, 12)
    pit(g, 22, 25)
    spikes(g, 16, 17)
    spikes(g, 30, 31)
    block(g, 17, 18, 9, 12)
    block(g, 15, 15, 18, 21)
    block(g, 12, 12, 26, 29)
    return convert("lvl_5", g, 2, pads=[(6, FLOOR_ROW), (27, 15)])


LEVELS = [lvl_1, lvl_2, lvl_3, lvl_4, lvl_5]


def main():
    os.makedirs(OUT, exist_ok=True)
    for make in LEVELS:
        lv = make()
        path = os.path.join(OUT, lv["name"] + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(lv, f, ensure_ascii=False, indent=1)
        print(lv["name"], len(lv["instances"]), "инстансов")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Генерация уровней lvl_1..lvl_5: широкие комнаты, сетка 32 px.

Пишет уровни/lvl_N.json в формате, который читает build_101.csx:
    [[object_name, x, y, scale_x, scale_y], ...]

Геометрия — как в оригинальных комнатах:
  клетка 32 px, пол в нижней клетке, её верх = 688;
  oWall/oDanger/oDoor — origin (0,0), спрайт 64x64, scale 0.5 -> клетка 32x32;
  игрок стоит на полу: y = 688, scale 0.5;
  батут — origin (32,32), центр ставится на поверхность;
  дверь — 64x96 (scale 1.0 x 1.5), стоит на полу справа.

Комнаты шире экрана (2560 / 3200 px): в игре включён вид, который едет за игроком
(см. build_101.csx), поэтому уровень длиннее экрана.

Запуск из корня репозитория:  python3 декомпилятор/scripts/gen_levels.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "уровни")

T = 32
ROWS = 22
FLOOR_ROW = ROWS - 1          # 21 -> верх пола 688
FLOOR_Y = FLOOR_ROW * T + 16  # 688
DOOR_W, DOOR_H = 64, 96

# прыжок: vsp = -10, grv = 0.3, walksp = 4  ->  ~5 клеток вверх, ~8 в длину
MAX_PIT = 4                   # ямы не шире 4 клеток (128 px)
MAX_RISE = 4                  # ступеньки не выше 4 клеток (128 px)


class Level:
    def __init__(self, name, cols):
        self.name = name
        self.cols = cols
        self.g = [[" "] * cols for _ in range(ROWS)]
        self.pads = []        # (col, surface_row)
        self._frame()

    def _frame(self):
        g = self.g
        for c in range(self.cols):
            g[0][c] = "#"
            g[FLOOR_ROW][c] = "#"
        for r in range(ROWS):
            g[r][0] = "#"
            g[r][self.cols - 1] = "#"

    # --- примитивы -----------------------------------------------------
    def wall(self, row1, row2, c1, c2):
        for r in range(row1, row2 + 1):
            for c in range(c1, c2 + 1):
                if 0 <= r < ROWS and 0 <= c < self.cols:
                    self.g[r][c] = "#"

    def plat(self, row, c1, c2):
        self.wall(row, row, c1, c2)

    def pit(self, c1, c2=None):
        c2 = c1 if c2 is None else c2
        for c in range(c1, c2 + 1):
            self.g[FLOOR_ROW][c] = " "

    def spikes(self, c1, c2=None):
        c2 = c1 if c2 is None else c2
        for c in range(c1, c2 + 1):
            self.g[FLOOR_ROW][c] = "^"

    def pad(self, col, surface_row=FLOOR_ROW):
        self.pads.append((col, surface_row))

    # --- результат -----------------------------------------------------
    def to_json(self, player_col=2, enemies=(), two_players=False):
        inst = []
        for r in range(ROWS):
            for c in range(self.cols):
                ch = self.g[r][c]
                x, y = c * T, r * T + 16
                if ch == "#":
                    inst.append(["oWall", x, y, 0.5, 0.5])
                elif ch == "^":
                    inst.append(["oDanger", x, y, 0.5, 0.5])
        for (c, row) in self.pads:
            inst.append(["oJumpplatform", c * T + T // 2, row * T + 16, 0.5, 0.5])
        for (c, row) in enemies:
            # origin у спрайта (0,0): ставим так, чтобы низ (48 px) стоял на поверхности
            inst.append(["oMushroomBleb", c * T - 8, row * T + 16 - 48, 0.75, 0.75])
        door_x = (self.cols - 3) * T
        inst.append(["oDoor", door_x, FLOOR_Y - DOOR_H, 1.0, 1.5])
        if two_players:
            inst.append(["oPlayer_1", player_col * T + T // 2, FLOOR_Y, 0.5, 0.5])
            inst.append(["oPlayer_2", (player_col + 3) * T + T // 2, FLOOR_Y, 0.5, 0.5])
        else:
            inst.append(["oPlayer", player_col * T + T // 2, FLOOR_Y, 0.5, 0.5])
        return {"name": self.name, "width": self.cols * T, "height": ROWS * T + 16,
                "instances": inst}


def lvl_1():
    """Обучение на две ширины экрана: ровный пол, ступеньки, яма, пара шипов."""
    L = Level("lvl_1", 80)
    enemies = [(46, FLOOR_ROW), (58, FLOOR_ROW), (72, FLOOR_ROW)]
    L.plat(17, 8, 14)
    L.plat(14, 16, 22)
    L.plat(11, 26, 31)
    L.spikes(34, 35)
    L.pit(42, 45)
    L.plat(18, 42, 45)          # мостик над ямой
    L.pad(38)
    L.spikes(52, 54)
    L.pad(62)
    L.plat(16, 64, 70)
    L.spikes(74, 75)
    return L.to_json(enemies=enemies)


def lvl_2():
    """Две ямы, шипы по полу и полкам, батуты перед длинными полосами."""
    L = Level("lvl_2", 80)
    L.pit(10, 13)
    L.plat(18, 10, 13)
    L.spikes(18, 20)
    L.plat(17, 16, 21)
    L.plat(14, 24, 30)
    L.pad(26)
    L.pit(28, 31)
    L.spikes(34, 36)
    L.plat(13, 34, 38)
    L.pad(40)
    L.spikes(44, 47)
    L.plat(14, 48, 54)
    L.pit(54, 57)
    L.plat(18, 54, 57)
    L.pad(58)
    L.spikes(62, 65)
    L.plat(16, 60, 66)
    return L.to_json(enemies=[(22, FLOOR_ROW), (50, FLOOR_ROW), (72, FLOOR_ROW)])


def lvl_3():
    """Плотнее: шипы вперемешку с ямами, прыжки по узким полкам."""
    L = Level("lvl_3", 80)
    L.spikes(8, 10)
    L.pit(14, 17)
    L.plat(15, 14, 17)
    L.spikes(20, 22)
    L.plat(17, 18, 23)
    L.pad(24)
    L.pit(26, 29)
    L.spikes(32, 35)
    L.plat(13, 30, 36)
    L.pad(38)
    L.spikes(40, 42)
    L.pit(44, 47)
    L.plat(18, 44, 47)
    L.plat(14, 48, 54)
    L.spikes(50, 53)
    L.pad(56)
    L.pit(58, 61)
    L.spikes(64, 67)
    L.plat(16, 62, 68)
    return L.to_json(enemies=[(12, FLOOR_ROW), (36, FLOOR_ROW), (62, FLOOR_ROW), (74, FLOOR_ROW)])


def lvl_4():
    """Подъём: длинная лестница полок с шипами и батутами, дверь внизу справа."""
    L = Level("lvl_4", 80)
    L.spikes(6, 8)
    L.pad(4)
    L.plat(18, 10, 15)
    L.plat(15, 16, 21)
    L.plat(12, 22, 28)
    L.pad(27)
    L.spikes(30, 32)
    L.plat(9, 30, 36)
    L.plat(12, 38, 44)
    L.spikes(46, 49)
    L.pit(52, 55)
    L.plat(17, 52, 55)
    L.pad(50)
    L.plat(14, 58, 64)
    L.spikes(60, 63)
    L.pad(68)
    L.plat(15, 66, 71)
    L.spikes(75, 76)
    return L.to_json(enemies=[(14, FLOOR_ROW), (24, FLOOR_ROW), (36, FLOOR_ROW), (44, FLOOR_ROW),
                              (58, FLOOR_ROW), (70, FLOOR_ROW), (77, FLOOR_ROW)])


def lvl_5():
    """Финал: всё сразу — ямы, шипы, батуты; уровень шире (3200)."""
    L = Level("lvl_5", 100)
    L.spikes(8, 11)
    L.pit(14, 17)
    L.plat(18, 14, 17)
    L.spikes(20, 23)
    L.pad(18)
    L.plat(15, 22, 28)
    L.pit(30, 33)
    L.plat(17, 30, 33)
    L.pad(34)
    L.spikes(36, 39)
    L.plat(13, 40, 46)
    L.spikes(42, 45)
    L.pit(48, 51)
    L.pad(52)
    L.spikes(54, 58)
    L.plat(16, 54, 60)
    L.pit(62, 65)
    L.plat(18, 62, 65)
    L.pad(66)
    L.spikes(68, 71)
    L.plat(14, 72, 78)
    L.pit(82, 85)
    L.pad(80)
    L.spikes(88, 91)
    return L.to_json(enemies=[(10, FLOOR_ROW), (30, FLOOR_ROW), (52, FLOOR_ROW), (72, FLOOR_ROW), (94, FLOOR_ROW)])



def chapter_1():
    """Короткий вход после меню: пол, батут, дверь."""
    L = Level("chapter_1", 60)
    L.plat(17, 10, 16)
    L.spikes(26, 27)
    L.pit(34, 37)
    L.plat(18, 34, 37)
    L.pad(42)
    return L.to_json()


def chapter_2():
    """Переход ко второму акту."""
    L = Level("chapter_2", 60)
    L.spikes(12, 14)
    L.pit(22, 25)
    L.plat(18, 22, 25)
    L.pad(30)
    L.plat(15, 38, 44)
    L.spikes(48, 50)
    return L.to_json()


def lvl_6():
    """Второй акт, легче финала: подъём по полкам и полосы шипов."""
    L = Level("lvl_6", 80)
    L.spikes(8, 10)
    L.plat(17, 6, 12)
    L.pit(16, 19)
    L.plat(18, 16, 19)
    L.pad(22)
    L.spikes(26, 29)
    L.plat(14, 24, 30)
    L.pit(34, 37)
    L.spikes(40, 43)
    L.plat(16, 38, 44)
    L.pad(48)
    L.spikes(52, 55)
    L.plat(13, 50, 56)
    L.pit(60, 63)
    L.plat(18, 60, 63)
    L.pad(66)
    L.spikes(70, 73)
    L.pad(74)
    L.spikes(76, 77)
    return L.to_json(enemies=[(12, FLOOR_ROW), (22, FLOOR_ROW), (36, FLOOR_ROW), (48, FLOOR_ROW),
                              (62, FLOOR_ROW), (74, FLOOR_ROW), (78, FLOOR_ROW)])


def lvl_7():
    """Плотный второй акт: батуты над шипами, узкие полки."""
    L = Level("lvl_7", 80)
    L.pad(4)
    L.spikes(8, 11)
    L.plat(15, 6, 12)
    L.pit(14, 17)
    L.spikes(20, 23)
    L.plat(18, 14, 17)
    L.pad(18)
    L.plat(12, 22, 28)
    L.spikes(30, 33)
    L.pit(36, 39)
    L.plat(17, 36, 39)
    L.pad(42)
    L.spikes(46, 49)
    L.plat(14, 44, 50)
    L.pit(54, 57)
    L.spikes(60, 64)
    L.plat(16, 58, 64)
    L.pad(68)
    L.spikes(72, 75)
    L.pad(66)
    L.spikes(77, 78)
    return L.to_json(enemies=[(10, FLOOR_ROW), (24, FLOOR_ROW), (40, FLOOR_ROW), (56, FLOOR_ROW),
                              (68, FLOOR_ROW), (76, FLOOR_ROW), (79, FLOOR_ROW)])


def lvl_8():
    """Финал второго акта — самый злой: 3200 px, ямы и шипы подряд."""
    L = Level("lvl_8", 100)
    L.spikes(6, 9)
    L.pad(4)
    L.pit(12, 15)
    L.plat(18, 12, 15)
    L.spikes(18, 21)
    L.plat(15, 16, 22)
    L.pad(24)
    L.pit(26, 29)
    L.spikes(32, 36)
    L.plat(13, 30, 36)
    L.pit(40, 43)
    L.plat(17, 40, 43)
    L.pad(44)
    L.spikes(48, 52)
    L.plat(12, 46, 52)
    L.pit(56, 59)
    L.spikes(62, 66)
    L.plat(16, 60, 66)
    L.pad(68)
    L.pit(72, 75)
    L.spikes(78, 82)
    L.plat(14, 76, 82)
    L.pad(84)
    L.spikes(88, 92)
    L.pad(86)
    L.spikes(95, 96)
    return L.to_json(enemies=[(10, FLOOR_ROW), (20, FLOOR_ROW), (28, FLOOR_ROW), (38, FLOOR_ROW),
                              (46, FLOOR_ROW), (60, FLOOR_ROW), (66, FLOOR_ROW), (80, FLOOR_ROW),
                              (94, FLOOR_ROW), (97, FLOOR_ROW)])


def p2(name, cols, spikes_at, pits_at, plats, pads):
    """Кооперативный уровень на двоих (те же правила)."""
    L = Level(name, cols)
    for (c1, c2) in spikes_at:
        L.spikes(c1, c2)
    for (c1, c2) in pits_at:
        L.pit(c1, c2)
    for (row, c1, c2) in plats:
        L.plat(row, c1, c2)
    for c in pads:
        L.pad(c)
    return L.to_json(two_players=True)


def two_player_levels():
    return [
        p2("p2_lvl_1", 80, [(12, 14), (28, 30)], [(20, 23)],
           [(18, 20, 23), (17, 34, 40)], [10, 32, 50, 62]),
        p2("p2_lvl_2", 80, [(10, 13), (24, 27), (40, 43)], [(16, 19), (34, 37)],
           [(18, 16, 19), (18, 34, 37), (15, 46, 52)], [8, 30, 44, 58]),
        p2("p2_lvl_3", 80, [(8, 11), (22, 25), (36, 39), (52, 55)], [(14, 17), (30, 33), (44, 47)],
           [(18, 14, 17), (18, 30, 33), (18, 44, 47), (14, 56, 62)], [6, 20, 42, 50]),
        p2("p2_lvl_4", 80, [(6, 10), (20, 24), (34, 38), (48, 52), (62, 66)],
           [(12, 15), (28, 31), (42, 45), (56, 59)],
           [(18, 12, 15), (18, 28, 31), (18, 42, 45), (18, 56, 59), (13, 66, 72)], [4, 26, 40, 54]),
        p2("p2_lvl_5", 100, [(8, 12), (22, 26), (36, 40), (50, 54), (64, 68), (78, 82), (90, 94)],
           [(14, 17), (28, 31), (42, 45), (56, 59), (70, 73), (84, 87)],
           [(18, 14, 17), (18, 28, 31), (18, 42, 45), (18, 56, 59), (18, 70, 73), (18, 84, 87)],
           [6, 20, 34, 48, 62, 76]),
    ]



LEVELS = [chapter_1, lvl_1, lvl_2, lvl_3, lvl_4, lvl_5, chapter_2, lvl_6, lvl_7, lvl_8]


# имена комнат для парных уровней (в data.win они называются p_2_lvl_N)
P2_NAMES = {"p2_lvl_1": "p_2_lvl_1", "p2_lvl_2": "p_2_lvl_2", "p2_lvl_3": "p_2_lvl_3",
            "p2_lvl_4": "p_2_lvl_4", "p2_lvl_5": "p_2_lvl_5"}


def main():
    os.makedirs(OUT, exist_ok=True)
    todo = [make() for make in LEVELS] + two_player_levels()
    for lv in todo:
        lv["name"] = P2_NAMES.get(lv["name"], lv["name"])
        path = os.path.join(OUT, lv["name"] + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(lv, f, ensure_ascii=False, indent=1)
        print("%-6s %6d px, %d инстансов" % (lv["name"], lv["width"], len(lv["instances"])))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Сборка Parcoobe 1.0.1 из data.win версии 1.0.0.

Что делает:
  1. добавляет события oName (Step и Draw GUI) и убирает из меню старые кнопки;
  2. компилирует GML-моды из mod/ в байткод и подставляет в объекты игроков;
  3. подменяет текстурную страницу (логотип с объёмом, новый сабтайтл, двери).

Запуск из корня репозитория:
    python3 декомпилятор/scripts/build_101.py
Нужен собранный декомпилятор (./декомпилятор/build.sh) и арт (make_art_101.py).
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLI = os.path.join(ROOT, "декомпилятор", "UndertaleModTool", "UndertaleModCli",
                   "bin", "Release", "net10.0", "UndertaleModCli.dll")
ORIGINAL = os.path.join(ROOT, "original", "data.win")
MOD = os.path.join(ROOT, "mod")
SRC = os.path.join(ROOT, "source")
ART = os.path.join(ROOT, "декомпилятор", "scripts", "art_out")


def run(*args):
    cmd = ["dotnet", CLI] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout[-3000:])
        print(res.stderr[-3000:])
        raise SystemExit("команда упала: " + " ".join(cmd))
    for line in res.stdout.splitlines():
        if any(k in line for k in ("event:", "removed", "ERROR", "error")):
            print("  " + line)
    return res.stdout


MARKER = "// Parcoobe 1.0.1 — инициализация"


def base_create(path):
    """Create-событие без ранее вставленного блока инициализации."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if MARKER in text:
        text = text[:text.index(MARKER)]
    return text.rstrip() + "\n"


def concat(dst, *parts):
    with open(dst, "w", encoding="utf-8") as out:
        for p in parts:
            if p.endswith(".gml") and os.path.basename(p).startswith("Create_0"):
                out.write(base_create(p))
            else:
                with open(p, encoding="utf-8") as f:
                    out.write(f.read())
            out.write("\n")
    return dst


def main():
    tmp = tempfile.mkdtemp(prefix="parcoobe101_")

    print("0/4 переименование 1.0.0")
    base = os.path.join(tmp, "base.win")
    run("load", ORIGINAL,
        "--scripts", os.path.join(ROOT, "декомпилятор", "scripts", "rename_to_parcoobe.csx"),
        "--output", base, "--overwrite")

    create_single = concat(os.path.join(tmp, "create_single.gml"),
                           os.path.join(SRC, "objects", "oPlayer", "Create_0.gml"),
                           os.path.join(MOD, "01_init.gml"))
    create_p1 = concat(os.path.join(tmp, "create_p1.gml"),
                       os.path.join(SRC, "objects", "oPlayer_1", "Create_0.gml"),
                       os.path.join(MOD, "01_init.gml"))
    create_p2 = concat(os.path.join(tmp, "create_p2.gml"),
                       os.path.join(SRC, "objects", "oPlayer_2", "Create_0.gml"),
                       os.path.join(MOD, "01_init.gml"))

    print("1/4 события и новые уровни")
    os.environ["LEVELS_DIR"] = os.path.join(ROOT, "уровни")
    step_a = os.path.join(tmp, "a.win")
    run("load", base, "--scripts",
        os.path.join(ROOT, "декомпилятор", "scripts", "build_101.csx"),
        "--output", step_a, "--overwrite")

    print("2/4 компиляция модов")
    step_b = os.path.join(tmp, "b.win")
    run("replace", step_a,
        "--code", "gml_Object_oName_Step_0=" + os.path.join(MOD, "05_menu_step.gml"),
        "--code", "gml_Object_oName_Draw_64=" + os.path.join(MOD, "06_menu_draw.gml"),
        "--code", "gml_Object_oName_Other_62=" + os.path.join(MOD, "07_async_http.gml"),
        "--code", "gml_Object_oPlayer_Collision_6d1efe77_b359_4bce_920b_b0511e55783a=" + os.path.join(MOD, "08_door_chain.gml"),
        "--code", "gml_Object_oPlayer_Create_0=" + create_single,
        "--code", "gml_Object_oPlayer_Step_0=" + os.path.join(MOD, "02_step_single.gml"),
        "--code", "gml_Object_oPlayer_1_Create_0=" + create_p1,
        "--code", "gml_Object_oPlayer_1_Step_0=" + os.path.join(MOD, "03_step_p1.gml"),
        "--code", "gml_Object_oPlayer_2_Create_0=" + create_p2,
        "--code", "gml_Object_oPlayer_2_Step_0=" + os.path.join(MOD, "04_step_p2.gml"),
        "--output", step_b)

    print("3/4 текстурная страница")
    tex = os.path.join(ART, "texture0.png")
    if not os.path.exists(tex):
        raise SystemExit("нет " + tex + " — сначала запусти make_art_101.py")
    run("replace", step_b, "--textures", "Texture 0=" + tex,
        "--output", os.path.join(ROOT, "build", "data.win"))

    print("готово: build/data.win")
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

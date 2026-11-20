#!/usr/bin/env python3
"""Сборка одного exe: лаунчер + упакованные данные игры.

Кладёт в build/Parcoobe-Single.exe файл, внутри которого лежат
Parcoobe.exe (раннер GameMaker), data.win, музыка и шрифт.
При запуске распаковывается в %LOCALAPPDATA%\\Parcoobe\\game и запускает игру.

Запуск из корня репозитория:
    python3 tools/build_single_exe.py
Нужен кросс-компилятор x86_64-w64-mingw32-gcc.
"""
import os
import shutil
import subprocess
import struct
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUILD = os.path.join(ROOT, "build")
TOOLS = os.path.join(ROOT, "tools")
LAUNCHER_SRC = os.path.join(TOOLS, "parcoobe_launcher.c")
LAUNCHER_EXE = os.path.join(TOOLS, "parcoobe_launcher.exe")
OUT = os.path.join(BUILD, "Parcoobe-Single.exe")
MAGIC = b"PCOBSPL1"
TRAILER = 24

# порядок важен только для читаемости: exe первым, дальше данные
PAYLOAD = ["Parcoobe.exe", "data.win", "StayPixelRegular-EaOxl.ttf",
           "music_1.ogg", "music_2.ogg", "music_3.ogg", "music_4.ogg"]


def build_launcher():
    cc = shutil.which("x86_64-w64-mingw32-gcc")
    if not cc:
        sys.exit("нет x86_64-w64-mingw32-gcc (apt install mingw-w64)")
    cmd = [cc, "-O2", "-municode", "-mwindows", "-s",
           "-o", LAUNCHER_EXE, LAUNCHER_SRC]
    print("+", " ".join(cmd))
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        sys.exit("кросс-компиляция не удалась")


def payload_bytes():
    out = bytearray()
    for name in PAYLOAD:
        path = os.path.join(BUILD, name)
        if not os.path.exists(path):
            sys.exit("нет файла " + path)
        data = open(path, "rb").read()
        raw = name.encode("utf-8")
        out += struct.pack("<I", len(raw)) + raw + struct.pack("<Q", len(data)) + data
        print("  %-28s %8d байт" % (name, len(data)))
    return bytes(out)


def main():
    if not os.path.exists(os.path.join(BUILD, "data.win")):
        sys.exit("сначала собери data.win (декомпилятор/scripts/build_101.py)")
    build_launcher()

    body = payload_bytes()
    launcher = open(LAUNCHER_EXE, "rb").read()

    with open(OUT, "wb") as f:
        f.write(launcher)
        offset = f.tell()
        f.write(body)
        f.write(MAGIC)
        f.write(struct.pack("<Q", offset))
        f.write(struct.pack("<Q", len(body)))

    print("готово: %s (%d МБ)" % (OUT, os.path.getsize(OUT) // (1024 * 1024)))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Склеивает уровни/*.json в один assets/levels.json для Rust-версии."""
import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ORDER = ["chapter_1", "lvl_1", "lvl_2", "lvl_3", "lvl_4", "lvl_5",
         "chapter_2", "lvl_6", "lvl_7", "lvl_8",
         "p_2_lvl_1", "p_2_lvl_2", "p_2_lvl_3", "p_2_lvl_4", "p_2_lvl_5"]

def main():
    levels = []
    for name in ORDER:
        path = os.path.join(ROOT, "уровни", name + ".json")
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        levels.append(d)
    out = os.path.join(ROOT, "rust", "assets", "levels.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(levels, f, ensure_ascii=False)
    print("levels:", len(levels), "->", out, os.path.getsize(out) // 1024, "КБ")

if __name__ == "__main__":
    main()

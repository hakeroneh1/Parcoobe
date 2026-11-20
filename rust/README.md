# Parcoobe на Rust

Полная переписка игры с GameMaker на Rust (крэйт `macroquad`). Один exe, внешних ассетов нет:
все текстуры и фон рисуются процедурно в рантайме, уровни вшиты в бинарник.

## Что умеет

* меню (`NEW GAME`, `LEVEL SELECT`, `SETTINGS`, `QUIT`), заставка и экран финала;
* **15 уровней** (`chapter_1`, `lvl_1..lvl_8`, `chapter_2`, `p_2_lvl_1..5`) из `уровни/*.json`
  (`tools/bake_levels.py` склеивает их в `assets/levels.json`);
* физика как в GML-версии: `walksp 4`, `grv 0.3`, прыжок `-10`, батут `-17`;
* камера едет за игроком, комнаты шире экрана (1920–3200 px);
* шипы, ямы, батуты, двери с переходом на следующий уровень;
* грибы `oMushroomBleb` патрулируют: разворот у стены, у шипов и на краю платформы;
* скины (5 цветов, клавиша `K`), сохраняются в `parcoobe.cfg` рядом с exe;
* настройки: `F1` — панель, переназначение клавиш, сохранение в `parcoobe.cfg`;
* музыка: 4 вшитых трека, переключаются по актам.

## Сборка

```bash
cd rust
cargo build --release                        # Linux
cargo build --release --target x86_64-pc-windows-gnu   # Windows (нужен mingw-w64)
```

Готовый файл: `target/x86_64-pc-windows-gnu/release/parcoobe.exe` (≈1.7 МБ, ничего рядом не нужно).

## Структура

```
src/main.rs           вся игра: рендер, физика, меню, настройки
tools/bake_levels.py  уровни/*.json -> assets/levels.json
assets/levels.json    вшитые уровни
assets/ui.ttf         шрифт с кириллицей
assets/music_*.ogg    музыка (вшивается в exe)
```

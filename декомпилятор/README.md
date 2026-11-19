# Декомпилятор (UndertaleModTool CLI)

Здесь лежит инструмент, которым получен исходник `Parcoobe`, и скрипты, которые мы к нему написали.

* **UndertaleModTool** — открытый (GPL-3.0) разборщик `data.win` GameMaker Studio 1/2:
  https://github.com/UnderminersTeam/UndertaleModTool
* В этой папке — только нужные для консольной сборки проекты: `UndertaleModCli` (CLI),
  `UndertaleModLib` (сама библиотека/декомпилятор) и `Underanalyzer` (дизассемблер/декомпилятор GML).
  Исходники взяты из upstream-ветки `master` (осень 2026), GUI-часть и тесты не включены.
* Добавлены наши скрипты:
  * `scripts/export_source.csx` — выгружает комнаты и метаданные (объекты, спрайты, звуки, шрифты,
    пути, переменные, функции, текстурные страницы) в JSON/PNG-проект;
  * `scripts/rename_to_parcoobe.csx` — переименование игры `Parcoob` → `Parcoobe` прямо в `data.win`;
  * `scripts/rebuild_logo.py` — перерисовка титульного логотипа `PARCOOB` → `PARCOOBE` (Pillow + Bebas Neue);
  * `scripts/make_art_101.py` — арт версии 1.0.1: логотип с объёмом и тенью, подпись `Version 1.0.1`,
    новые спрайты дверей (Pillow + Bebas Neue / Pixelify Sans);
  * `scripts/build_101.csx` — добавление событий `oName` (Step и Draw GUI), удаление старых кнопок меню,
    сдвиг дверей-выходов в кадр;
  * `scripts/build_101.py` — полная сборка 1.0.1: переименование, события, компиляция `mod/*.gml`, текстуры;
  * `scripts/render_room.py` — рендер PNG-превью комнаты из выгруженных данных (Pillow).

## Сборка

Нужен .NET SDK 10 (в Ubuntu 26.04: `sudo apt install dotnet-sdk-10.0`).

```bash
./build.sh
```

Появится `UndertaleModTool/UndertaleModCli/bin/Release/net10.0/UndertaleModCli.dll`.

## Использование

```bash
# информация о data.win
./run.sh info ../original/data.win

# выгрузить ВСЕ 148 code entries (декомпилированный GML)
./run.sh dump ../original/data.win -o /tmp/dump -c UMT_DUMP_ALL

# выгрузить спрайты, текстуры и строки
./run.sh dump ../original/data.win -o /tmp/dump --sprites -t -s

# выгрузить комнаты и метаданные нашими скриптами
EXPORT_ROOT=/tmp/source ./run.sh load ../original/data.win --scripts scripts/export_source.csx

# переименовать игру в Parcoobe (создать новый data.win)
./run.sh load ../original/data.win \
    --scripts scripts/rename_to_parcoobe.csx \
    --output ../build/data.win --overwrite

# перерисовать логотип и вклеить его в текстурную страницу
python3 scripts/rebuild_logo.py --source <выгрузка спрайтов/текстур> --out /tmp/logo
../run.sh replace ../build/data.win --textures "Texture 0=/tmp/logo/texture0.png" \
    --output ../build/data.win
```

## Как это было сделано для Parcoobe (по шагам)

1. `PARCOOB.rar` со страницы GameJolt (ссылка на Google Drive) → `Parcoob.exe` + `data.win`.
2. `./build.sh` — сборка UTMT CLI.
3. `./run.sh info ../original/data.win` — GMS2, bytecode 17, YYC выключен, 148 code entries.
4. `./run.sh dump ../original/data.win -o dump -c UMT_DUMP_ALL` — GML по всем событиям объектов и скриптам.
5. `EXPORT_ROOT=... ./run.sh load ../original/data.win --scripts scripts/export_source.csx` — комнаты и метаданные.
6. `./run.sh dump ... --sprites -t -s` — PNG спрайтов и текстурных страниц, `strings.txt`.
7. `./run.sh load ../original/data.win --scripts scripts/rename_to_parcoobe.csx --output ../build/data.win --overwrite`
   — новый `data.win` с именем `Parcoobe`.
8. `python3 scripts/rebuild_logo.py` + `./run.sh replace ... --textures "Texture 0=texture0.png"` — новый
   титульный логотип `PARCOOBE` в текстурной странице.
9. Готовые GML разложены по `objects/<объект>/<событие>.gml` и `scripts/<скрипт>.gml`
   (события коллизий переименованы из GUID в `Collision_with_<объект>.gml` по данным `metadata/objects.json`).

## Сборка версии 1.0.1

```bash
./build.sh                                     # собрать UTMT CLI
python3 scripts/make_art_101.py                # нарисовать логотип и двери
python3 scripts/build_101.py                   # собрать build/data.win
```

Скрипт `build_101.py` берёт `original/data.win`, применяет переименование в `Parcoobe`, затем добавляет
события, компилирует GML из каталога `mod/` (управление, меню, панель настроек) и подменяет текстурную
страницу. GML-моды — обычный GameMaker-код, его можно править и пересобирать.

## Ограничения

* Декомпилятор восстанавливает GML из байткода эвристически: логика верна, но имена локальных
  переменных, структура `if`/`switch` и порядок выражений могут отличаться от авторских исходников.
* `.yy`-файлы проекта (ресурсы GMS2) в `data.win` не хранятся, поэтому в `source/` их нет:
  вместо них — JSON-описания комнат/объектов и PNG всех кадров. Собрать это обратно в `yyp`
  можно, но вручную.
* Комнаты отрисованы нашим `render_room.py` по координатам инстансов; тайловые слои и эффекты
  в превью не рисуются.
* Шрифт `font_pix` в игре — демо-версия (вместо цифр и кириллицы рисует заглушку), поэтому интерфейс
  панели управления сделан на английском и без цифр; версия вынесена в картинку логотипа.

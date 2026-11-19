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
8. Готовые GML разложены по `objects/<объект>/<событие>.gml` и `scripts/<скрипт>.gml`
   (события коллизий переименованы из GUID в `Collision_with_<объект>.gml` по данным `metadata/objects.json`).

## Ограничения

* Декомпилятор восстанавливает GML из байткода эвристически: логика верна, но имена локальных
  переменных, структура `if`/`switch` и порядок выражений могут отличаться от авторских исходников.
* `.yy`-файлы проекта (ресурсы GMS2) в `data.win` не хранятся, поэтому в `source/` их нет:
  вместо них — JSON-описания комнат/объектов и PNG всех кадров. Собрать это обратно в `yyp`
  можно, но вручную.
* Комнаты отрисованы нашим `render_room.py` по координатам инстансов; тайловые слои и эффекты
  в превью не рисуются.

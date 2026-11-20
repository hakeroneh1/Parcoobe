# Моды Parcoobe 2.0.2

GML-код, который вставляется в `data.win` при сборке (`декомпилятор/scripts/build_101.py`).

| Файл | Куда попадает | Что делает |
|---|---|---|
| `01_init.gml` | дописывается в Create `oPlayer`, `oPlayer_1`, `oPlayer_2` | глобальные настройки управления, значения по умолчанию, чтение `parcoobe.ini` |
| `02_step_single.gml` | Step `oPlayer` (одиночная игра) | чтение ввода через раскладку игрока 1 + оригинальная физика |
| `03_step_p1.gml` | Step `oPlayer_1` (2 игрока, P1) | то же для игрока 1 |
| `04_step_p2.gml` | Step `oPlayer_2` (2 игрока, P2) | то же для игрока 2 |
| `05_menu_step.gml` | Step `oName` (комната Menu) | кнопка MENU, открытие панели по `F1`, навигация, переназначение клавиш, сохранение ini |
| `06_menu_draw.gml` | Draw GUI `oName` | отрисовка кнопки MENU, панели `CONTROLS`, плашки обновления |
| `07_async_http.gml` | Other → Async HTTP `oName` | разбор ответа `http_get` для авто-обновления |
| `08_door_chain.gml` | Collision `oPlayer` с `oDoor` | явная цепочка комнат при входе в дверь: `Menu → lvl_1 → lvl_2 → lvl_3 → lvl_4 → lvl_5 → fin` |

Настройки по умолчанию: P1 — `A`/`D`, прыжок `Space` и `W`; P2 — `←`/`→`, прыжок `Numpad 0` и `↑`.
Геймпад: крестовина/стик, `A` (face one) и правый бампер.

Игра умеет: клавиатура + клавиатура (два набора клавиш), клавиатура + геймпад, два геймпада,
геймпад + клавиатура. Различать две физические клавиатуры GameMaker на Windows не умеет — поэтому
«две клавиатуры» это два набора клавиш на одной.

## Уровни

`lvl_1..lvl_5` не разложены по объектам вручную: они собираются из `уровни/*.json`
скриптом `декомпилятор/scripts/gen_levels.py` (сетка 32 px, комната 1280x720) и вставляются
в комнаты при сборке (`build_101.csx`). Правки геометрии — в `gen_levels.py`, потом:

```bash
python3 декомпилятор/scripts/gen_levels.py     # уровни/*.json
python3 декомпилятор/scripts/build_101.py      # build/data.win
python3 tools/build_single_exe.py              # build/Parcoobe-Single.exe
```

// Parcoobe 1.0.1 — инициализация настроек управления.
// Этот блок дописывается в Create-события oPlayer / oPlayer_1 / oPlayer_2.
if (!variable_global_exists("pco_v"))
{
    global.pco_v = 1;
    global.pco_dev = array_create(3, 0);   // 0 = клавиатура, 1 = геймпад
    global.pco_pad = array_create(3, 0);   // какой слот геймпада у игрока
    global.pco_kb = array_create(12, 0);   // слоты 0..3 — игрок 1, 4..7 — игрок 2
    global.pco_gp = array_create(12, 0);

    // игрок 1: A / D / Space / W
    global.pco_kb[0] = ord("A");
    global.pco_kb[1] = ord("D");
    global.pco_kb[2] = vk_space;
    global.pco_kb[3] = ord("W");
    // игрок 2: стрелки / Numpad 0 / стрелка вверх
    global.pco_kb[4] = vk_left;
    global.pco_kb[5] = vk_right;
    global.pco_kb[6] = vk_numpad0;
    global.pco_kb[7] = vk_up;

    // геймпады: крестовина, A и правый бампер
    var i;
    for (i = 0; i < 4; i++)
    {
        global.pco_gp[i * 4 + 0] = gp_padl;
        global.pco_gp[i * 4 + 1] = gp_padr;
        global.pco_gp[i * 4 + 2] = gp_face1;
        global.pco_gp[i * 4 + 3] = gp_shoulderr;
    }

    // автоподбор слотов геймпадов
    global.pco_pad[1] = -1;
    global.pco_pad[2] = -1;
    for (i = 0; i < 12; i++)
    {
        if (gamepad_is_connected(i))
        {
            if (global.pco_pad[1] < 0)
            {
                global.pco_pad[1] = i;
            }
            else if (global.pco_pad[2] < 0)
            {
                global.pco_pad[2] = i;
            }
        }
    }
    if (global.pco_pad[1] < 0)
    {
        global.pco_pad[1] = 0;
    }
    if (global.pco_pad[2] < 0)
    {
        global.pco_pad[2] = global.pco_pad[1];
    }

    global.pco_ui = 0;        // открыто ли меню настроек
    global.pco_sel = 0;       // выбранная строка
    global.pco_bind = -1;     // индекс слота, для которого ждём нажатие
    global.pco_player = 1;    // какого игрока настраиваем
    global.pco_snd = 1;       // звук включён
    global.pco_dirty = 0;

    // авто-обновление
    global.pco_ver = "2.0.1";
    global.pco_upd_auto = 1;      // проверять обновления при запуске
    global.pco_upd_checked = 0;   // проверка уже выполнена
    global.pco_upd = 0;           // найдено обновление
    global.pco_upd_ver = "";      // версия обновления
    global.pco_req = -1;          // id текущего http-запроса
    global.pco_upd_url = "https://raw.githubusercontent.com/hakeroneh1/Parcoobe/main/version.txt";
    global.pco_upd_page = "https://github.com/hakeroneh1/Parcoobe/releases/latest";
    global.pco_msg = "";          // сообщение о результате проверки
    global.pco_msg_t = 0;         // сколько кадров его показывать

    // сохранённые настройки
    if (file_exists("parcoobe.ini"))
    {
        ini_open("parcoobe.ini");
        var pco_j;
        for (pco_j = 0; pco_j < 8; pco_j++)
        {
            global.pco_kb[pco_j] = ini_read_real("keys", "kb" + string(pco_j), global.pco_kb[pco_j]);
            global.pco_gp[pco_j] = ini_read_real("keys", "gp" + string(pco_j), global.pco_gp[pco_j]);
        }
        global.pco_dev[1] = ini_read_real("dev", "p1", 0);
        global.pco_dev[2] = ini_read_real("dev", "p2", 0);
        global.pco_snd = ini_read_real("misc", "sound", 1);
        global.pco_upd_auto = ini_read_real("misc", "update", 1);
        ini_close();
        audio_master_gain(global.pco_snd);
    }
}

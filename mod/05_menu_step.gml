// Parcoobe 2.0.4 — меню настроек управления (oName, комната Menu).
var pco_rows = 10;
var pco_bx1 = 1120;
var pco_by1 = 32;
var pco_bx2 = 1256;
var pco_by2 = 84;

// Enter в меню — начать игру (клик мышью тоже работает)
if (global.pco_ui == 0 && keyboard_check_pressed(vk_enter))
{
    room_goto(lvl_1);
}

// клик по NEW GAME / CHAPTER SELECT — старт игры
if (mouse_check_button_pressed(mb_left) && global.pco_ui == 0)
{
    var pco_cx = device_mouse_x_to_gui(0);
    var pco_cy = device_mouse_y_to_gui(0);
    // NEW GAME (спрайт sNewgame 128x128 в точке 992,576)
    if (pco_cx >= 992 && pco_cx <= 1120 && pco_cy >= 576 && pco_cy <= 704)
    {
        room_goto(lvl_1);
    }
    // CHAPTER SELECT
    if (pco_cx >= 160 && pco_cx <= 288 && pco_cy >= 576 && pco_cy <= 704)
    {
        room_goto(lvl_1);
    }
}

// кнопка SETTINGS мышью
if (mouse_check_button_pressed(mb_left))
{
    var pco_mx = device_mouse_x_to_gui(0);
    var pco_my = device_mouse_y_to_gui(0);
    if (pco_mx >= 24 && pco_mx <= 200 && pco_my >= 32 && pco_my <= 84)
    {
        global.pco_ui = 1 - global.pco_ui;
        global.pco_bind = -1;
        global.pco_sel = 0;
    }
}

// F1 — открыть/закрыть
if (keyboard_check_pressed(vk_f1))
{
    global.pco_ui = 1 - global.pco_ui;
    global.pco_bind = -1;
    global.pco_sel = 0;
}

if (global.pco_ui == 1)
{
    var pco_sel = global.pco_sel;
    if (global.pco_bind < 0)
    {
        if (keyboard_check_pressed(vk_up))
        {
            global.pco_sel = (pco_sel + pco_rows - 1) % pco_rows;
        }
        if (keyboard_check_pressed(vk_down))
        {
            global.pco_sel = (pco_sel + 1) % pco_rows;
        }
        if (keyboard_check_pressed(vk_enter))
        {
            if (pco_sel == 0)
            {
                global.pco_player = 3 - global.pco_player;
            }
            else if (pco_sel == 1)
            {
                global.pco_dev[global.pco_player] = 1 - global.pco_dev[global.pco_player];
                global.pco_dirty = 1;
            }
            else if (pco_sel >= 2 && pco_sel <= 5)
            {
                global.pco_bind = pco_sel - 2;
            }
            else if (pco_sel == 6)
            {
                global.pco_snd = 1 - global.pco_snd;
                audio_master_gain(global.pco_snd);
                global.pco_dirty = 1;
            }
            else if (pco_sel == 7)
            {
                global.pco_upd_auto = 1 - global.pco_upd_auto;
                global.pco_dirty = 1;
                if (global.pco_upd_auto == 1 && global.pco_upd_checked == 0 && global.pco_req < 0)
                {
                    global.pco_req = http_get(global.pco_upd_url);
                }
            }
            else if (pco_sel == 8)
            {
                // CHECK NOW
                if (global.pco_req < 0)
                {
                    global.pco_upd_checked = 0;
                    global.pco_msg = "CHECKING";
                    global.pco_msg_t = 240;
                    global.pco_req = http_get(global.pco_upd_url);
                }
            }
            else
            {
                global.pco_ui = 0;
            }
        }
        if (keyboard_check_pressed(vk_escape))
        {
            global.pco_ui = 0;
        }
    }
    else
    {
        // ждём нажатие клавиши или кнопки геймпада
        var pco_p = global.pco_player;
        var pco_slot = (pco_p - 1) * 4 + global.pco_bind;
        var pco_i;
        if (global.pco_dev[pco_p] == 1)
        {
            var pco_gp = global.pco_pad[pco_p];
            for (pco_i = 32769; pco_i <= 32784; pco_i++)
            {
                if (gamepad_button_check_pressed(pco_gp, pco_i))
                {
                    global.pco_gp[pco_slot] = pco_i;
                    global.pco_bind = -1;
                    global.pco_dirty = 1;
                    break;
                }
            }
        }
        else
        {
            for (pco_i = 1; pco_i < 256; pco_i++)
            {
                if (pco_i == 1 || pco_i == 2 || pco_i == 4 || pco_i == 5 || pco_i == 6 || pco_i == 27)
                {
                    continue;
                }
                if (keyboard_check_pressed(pco_i))
                {
                    global.pco_kb[pco_slot] = pco_i;
                    global.pco_bind = -1;
                    global.pco_dirty = 1;
                    break;
                }
            }
        }
        if (keyboard_check_pressed(vk_escape))
        {
            global.pco_bind = -1;
        }
    }
}

// ── сохранение настроек
if (global.pco_dirty == 1)
{
    var pco_w;
    ini_open("parcoobe.ini");
    for (pco_w = 0; pco_w < 8; pco_w++)
    {
        ini_write_real("keys", "kb" + string(pco_w), global.pco_kb[pco_w]);
        ini_write_real("keys", "gp" + string(pco_w), global.pco_gp[pco_w]);
    }
    ini_write_real("dev", "p1", global.pco_dev[1]);
    ini_write_real("dev", "p2", global.pco_dev[2]);
    ini_write_real("misc", "sound", global.pco_snd);
    ini_close();
    global.pco_dirty = 0;
}

// ── авто-обновление: первый запрос при входе в меню и открытие страницы релизов
if (global.pco_upd_auto == 1 && global.pco_upd_checked == 0 && global.pco_req < 0)
{
    global.pco_req = http_get(global.pco_upd_url);
}
if (global.pco_upd == 1 && global.pco_ui == 0 && keyboard_check_pressed(ord("U")))
{
    url_open(global.pco_upd_page);
}

// таймер сообщения
if (global.pco_msg_t > 0)
{
    global.pco_msg_t -= 1;
    if (global.pco_msg_t == 0)
    {
        global.pco_msg = "";
    }
}

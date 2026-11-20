// Parcoobe 2.0.4 — панель CONTROLS прямо в уровнях (F1 работает везде).
// Подключается в Step игроков (кроме комнаты Menu, там панелью занимается oName).
if (room != Menu)
{
    var pco_rows = 10;   // столько же строк, сколько в меню

    // F1 открывает и закрывает панель; Esc закрывает
    if (keyboard_check_pressed(vk_f1))
    {
        global.pco_ui = 1 - global.pco_ui;
        global.pco_bind = -1;
        global.pco_sel = 0;
    }
    if (global.pco_ui == 1 && keyboard_check_pressed(vk_escape) && global.pco_bind < 0)
    {
        global.pco_ui = 0;
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
}

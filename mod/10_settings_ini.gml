// Parcoobe 2.0.4 — сохранение настроек (вызывается из Step игроков в уровнях).
if (room != Menu)
{
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
}

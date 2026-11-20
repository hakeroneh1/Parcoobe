// Parcoobe 2.0.6 — отрисовка панели CONTROLS в уровнях (Draw GUI игроков).
if (room != Menu)
{
    draw_set_font(font_pix);
    draw_set_alpha(1);
    if (global.pco_ui == 0)
    {
        // кнопка настроек в левом верхнем углу — мышью или F1
        draw_set_colour(make_colour_rgb(170, 28, 38));
        draw_rectangle(16, 16, 216, 64, false);
        draw_set_colour(make_colour_rgb(70, 20, 24));
        draw_rectangle(16, 16, 216, 64, true);
        draw_set_colour(c_white);
        draw_set_halign(fa_center);
        draw_set_valign(fa_middle);
        draw_text_transformed(116, 40, "SETTINGS", 1.5, 1.5, 0);

        draw_set_colour(make_colour_rgb(190, 190, 190));
        draw_set_halign(fa_left);
        draw_set_valign(fa_top);
        draw_text_transformed(20, 690, "F1 SETTINGS    K SKIN", 1.0, 1.0, 0);
    }
    if (global.pco_ui == 1)
    {
        var pco_p = global.pco_player;
        var pco_b = (pco_p - 1) * 4;
        var pco_j;
        var pco_kk;
        var pco_bb;
        var pco_nm;
        var pco_names = array_create(4, "");

        for (pco_j = 0; pco_j < 4; pco_j++)
        {
            pco_nm = "";
            if (global.pco_dev[pco_p] == 1)
            {
                pco_bb = global.pco_gp[pco_b + pco_j];
                if (pco_bb == gp_face1) { pco_nm = "FACE ONE"; }
                else if (pco_bb == gp_face2) { pco_nm = "FACE TWO"; }
                else if (pco_bb == gp_face3) { pco_nm = "FACE THREE"; }
                else if (pco_bb == gp_face4) { pco_nm = "FACE FOUR"; }
                else if (pco_bb == gp_padl) { pco_nm = "PAD LEFT"; }
                else if (pco_bb == gp_padr) { pco_nm = "PAD RIGHT"; }
                else if (pco_bb == gp_padu) { pco_nm = "PAD UP"; }
                else if (pco_bb == gp_padd) { pco_nm = "PAD DOWN"; }
                else if (pco_bb == gp_shoulderl) { pco_nm = "SHOULDER L"; }
                else if (pco_bb == gp_shoulderr) { pco_nm = "SHOULDER R"; }
                else if (pco_bb == gp_start) { pco_nm = "START"; }
                else if (pco_bb == gp_select) { pco_nm = "SELECT"; }
                else { pco_nm = "BUTTON"; }
            }
            else
            {
                pco_kk = global.pco_kb[pco_b + pco_j];
                if (pco_kk == vk_left) { pco_nm = "LEFT"; }
                else if (pco_kk == vk_right) { pco_nm = "RIGHT"; }
                else if (pco_kk == vk_up) { pco_nm = "UP"; }
                else if (pco_kk == vk_down) { pco_nm = "DOWN"; }
                else if (pco_kk == vk_space) { pco_nm = "SPACE"; }
                else if (pco_kk == vk_enter) { pco_nm = "ENTER"; }
                else if (pco_kk == vk_shift) { pco_nm = "SHIFT"; }
                else if (pco_kk == vk_control) { pco_nm = "CTRL"; }
                else if (pco_kk == vk_alt) { pco_nm = "ALT"; }
                else if (pco_kk == vk_tab) { pco_nm = "TAB"; }
                else if (pco_kk == vk_backspace) { pco_nm = "BACKSPACE"; }
                else if (pco_kk == vk_numpad0) { pco_nm = "NUM PAD ZERO"; }
                else if (pco_kk == vk_numpad1) { pco_nm = "NUM PAD ONE"; }
                else if (pco_kk == vk_numpad2) { pco_nm = "NUM PAD TWO"; }
                else if (pco_kk >= 65 && pco_kk <= 90) { pco_nm = chr(pco_kk); }
                else if (pco_kk >= 48 && pco_kk <= 57) { pco_nm = "DIGIT"; }
                else { pco_nm = "KEY"; }
            }
            pco_names[pco_j] = pco_nm;
        }

        // ── панель
        draw_set_colour(make_colour_rgb(10, 10, 10));
        draw_rectangle(150, 56, 1130, 668, false);
        draw_set_colour(make_colour_rgb(230, 200, 120));
        draw_rectangle(150, 56, 1130, 668, true);
        draw_set_colour(make_colour_rgb(70, 70, 70));
        draw_rectangle(154, 60, 1126, 664, true);

        draw_set_colour(make_colour_rgb(240, 200, 120));
        draw_text_transformed(176, 76, "CONTROLS", 2.8, 2.8, 0);
        draw_set_colour(make_colour_rgb(150, 150, 150));
        draw_text_transformed(176, 126, "ARROWS SELECT   ENTER CHANGE   ESC BACK", 1.6, 1.6, 0);

        var pco_i = 0;
        var pco_y = 176;
        var pco_lbl = "";
        var pco_val = "";
        var pco_col = c_white;

        for (pco_i = 0; pco_i < 10; pco_i++)
        {
            pco_col = c_white;
            if (global.pco_sel == pco_i)
            {
                pco_col = make_colour_rgb(255, 220, 120);
                draw_set_alpha(0.18);
                draw_set_colour(c_white);
                draw_rectangle(166, pco_y - 6, 1114, pco_y + 34, false);
                draw_set_alpha(1);
            }

            if (pco_i == 0)
            {
                pco_lbl = "PLAYER";
                if (pco_p == 1) { pco_val = "ONE"; } else { pco_val = "TWO"; }
            }
            else if (pco_i == 1)
            {
                pco_lbl = "DEVICE";
                if (global.pco_dev[pco_p] == 1) { pco_val = "GAMEPAD"; } else { pco_val = "KEYBOARD"; }
            }
            else if (pco_i == 2)
            {
                pco_lbl = "LEFT";
                pco_val = pco_names[0];
            }
            else if (pco_i == 3)
            {
                pco_lbl = "RIGHT";
                pco_val = pco_names[1];
            }
            else if (pco_i == 4)
            {
                pco_lbl = "JUMP";
                pco_val = pco_names[2];
            }
            else if (pco_i == 5)
            {
                pco_lbl = "JUMP TWO";
                pco_val = pco_names[3];
            }
            else if (pco_i == 6)
            {
                pco_lbl = "SOUND";
                if (global.pco_snd == 1) { pco_val = "ON"; } else { pco_val = "OFF"; }
            }
            else if (pco_i == 7)
            {
                pco_lbl = "AUTO UPDATE";
                if (global.pco_upd_auto == 1) { pco_val = "ON"; } else { pco_val = "OFF"; }
            }
            else if (pco_i == 8)
            {
                pco_lbl = "CHECK NOW";
                pco_val = "";
            }
            else
            {
                pco_lbl = "BACK";
                pco_val = "";
            }

            draw_set_colour(pco_col);
            draw_text_transformed(186, pco_y, pco_lbl, 2.2, 2.2, 0);
            draw_set_colour(make_colour_rgb(230, 230, 230));
            draw_text_transformed(560, pco_y, pco_val, 2.2, 2.2, 0);
            pco_y += 48;
        }

        if (global.pco_bind >= 0)
        {
            draw_set_alpha(0.8);
            draw_set_colour(c_black);
            draw_rectangle(150, 56, 1130, 668, false);
            draw_set_alpha(1);
            draw_set_colour(make_colour_rgb(255, 230, 150));
            draw_set_halign(fa_center);
            draw_text_transformed(640, 320, "PRESS A KEY", 3, 3, 0);
            draw_text_transformed(640, 386, "OR A GAMEPAD BUTTON", 2, 2, 0);
            draw_text_transformed(640, 440, "ESC CANCEL", 1.6, 1.6, 0);
            draw_set_halign(fa_left);
        }
    }

    // сообщение о проверке обновления — только в панели, чтобы не лезло в меню
    if (global.pco_ui == 1 && global.pco_msg_t > 0 && global.pco_msg != "")
    {
        draw_set_colour(make_colour_rgb(20, 40, 70));
        draw_rectangle(320, 618, 960, 656, false);
        draw_set_colour(make_colour_rgb(150, 200, 255));
        draw_rectangle(320, 618, 960, 656, true);
        draw_set_halign(fa_center);
        draw_text_transformed(640, 628, global.pco_msg, 1.5, 1.5, 0);
        draw_set_halign(fa_left);
    }

    // баннер «доступно обновление»
    if (global.pco_upd == 1 && global.pco_ui == 0)
    {
        draw_set_colour(make_colour_rgb(20, 60, 20));
        draw_rectangle(300, 660, 980, 712, false);
        draw_set_colour(make_colour_rgb(140, 240, 140));
        draw_rectangle(300, 660, 980, 712, true);
        draw_set_halign(fa_center);
        draw_text_transformed(640, 672, "NEW VERSION AVAILABLE", 1.8, 1.8, 0);
        draw_text_transformed(640, 692, "PRESS U TO DOWNLOAD", 1.4, 1.4, 0);
        draw_set_halign(fa_left);
    }
}

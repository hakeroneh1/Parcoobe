// Parcoobe 2.0.5 — скины игрока: цвет куба, выбор по K, сохраняется в ini.
if (!variable_global_exists("pco_skins"))
{
    global.pco_skins = 5;
    global.pco_skin_col = array_create(5, c_white);
    global.pco_skin_col[0] = c_white;                        // обычный
    global.pco_skin_col[1] = make_colour_rgb(255, 120, 120); // красный
    global.pco_skin_col[2] = make_colour_rgb(140, 235, 140); // зелёный
    global.pco_skin_col[3] = make_colour_rgb(130, 180, 255); // синий
    global.pco_skin_col[4] = make_colour_rgb(220, 150, 255); // фиолетовый
    global.pco_skin = 0;
}
if (!variable_global_exists("pco_skin"))
{
    global.pco_skin = 0;
}

if (global.pco_ui == 0 && keyboard_check_pressed(ord("K")))
{
    global.pco_skin = (global.pco_skin + 1) mod global.pco_skins;
    global.pco_dirty = 1;
}

if (global.pco_ui == 0)
{
    image_blend = global.pco_skin_col[global.pco_skin];
}
else
{
    image_blend = c_white;
}

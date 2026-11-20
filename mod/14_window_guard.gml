// Parcoobe 2.0.6 — страховка от Alt-Tab: после возврата фокуса окно возвращается
// к нормальному размеру, GUI и surface пересобираются. Без display_reset/window_center —
// в раннере 2.2.2 они на этой сборке роняют процесс.
if (!variable_global_exists("pco_blur"))
{
    global.pco_blur = 0;
}

if (!window_has_focus())
{
    global.pco_blur = 1;
}
else if (global.pco_blur == 1)
{
    global.pco_blur = 0;
    if (!window_get_fullscreen())
    {
        window_set_size(1280, 720);
    }
    display_set_gui_size(1280, 720);
}

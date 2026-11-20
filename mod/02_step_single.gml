// Parcoobe 2.0.2 — Step одиночного игрока (oPlayer, слот игрока 1).
// F11 — полный экран
if (keyboard_check_pressed(vk_f11))
{
    window_set_fullscreen(!window_get_fullscreen());
}

var pco_p = 1;
var pco_b = 0;
if (global.pco_ui == 1)
{
    key_left = 0;
    key_right = 0;
    key_jump = 0;
}
else if (global.pco_dev[pco_p] == 1)
{
    var pco_g = global.pco_pad[pco_p];
    var pco_ax = gamepad_axis_value(pco_g, gp_axislh);
    key_left = gamepad_button_check(pco_g, global.pco_gp[pco_b]) || pco_ax < -0.4;
    key_right = gamepad_button_check(pco_g, global.pco_gp[pco_b + 1]) || pco_ax > 0.4;
    key_jump = gamepad_button_check_pressed(pco_g, global.pco_gp[pco_b + 2]) || gamepad_button_check_pressed(pco_g, global.pco_gp[pco_b + 3]);
}
else
{
    key_left = keyboard_check(global.pco_kb[pco_b]);
    key_right = keyboard_check(global.pco_kb[pco_b + 1]);
    key_jump = keyboard_check_pressed(global.pco_kb[pco_b + 2]) || keyboard_check_pressed(global.pco_kb[pco_b + 3]);
}

var move = key_right - key_left;
hsp = move * walksp;
vsp += grv;
if (place_meeting(x, y + 1, oWall) && key_jump)
{
    vsp = -10;
}
if (place_meeting(x + hsp, y, oWall))
{
    while (!place_meeting(x + sign(hsp), y, oWall))
    {
        x += sign(hsp);
    }
    hsp = 0;
}
x += hsp;
if (place_meeting(x, y + vsp, oWall))
{
    while (!place_meeting(x, y + sign(vsp), oWall))
    {
        y += sign(vsp);
    }
    vsp = 0;
}
y += vsp;
if (place_meeting(x, y + vsp, oJumpplatform))
{
    vsp = -17;
}
// страховка: не провалиться за нижнюю границу комнаты
if (y > room_height + 64)
{
    room_restart();
}
if (isDeath == 1)
{
    room_restart();
}
if (isDeath == 1 && global.hard == 1)
{
    room_goto(chapter_1);
    audio_stop_sound(music_1);
    audio_stop_sound(music_4);
    audio_stop_sound(music_3);
    global.hard = 0;
}
if (key_right)
{
    sprite_index = sPlayerright;
    part_particles_create(global.partSystem, x, y + 32, global.partDS, 4);
}
if (key_left)
{
    sprite_index = sPlayerleft;
}
if (room == fin)
{
    alarm[0] = -1;
}
if (alarm_get(alarm) == 0)
{
    game_end();
}

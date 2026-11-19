key_left = keyboard_check(vk_left);
key_right = keyboard_check(vk_right);
key_jump = keyboard_check_pressed(vk_numpad0);
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
if (isDeath2 == 1)
{
    room_restart();
    audio_stop_sound(music_3);
}
if (keyboard_check(vk_right))
{
    sprite_index = s2Playerright;
}
if (keyboard_check(vk_left))
{
    sprite_index = s2Playerleft;
}
if (room == fin)
{
    alarm[0] = -1;
}
if (alarm_get(alarm) == 0)
{
    game_end();
}

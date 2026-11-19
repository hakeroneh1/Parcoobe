hsp = 0;
vsp = 0;
grv = 0.3;
walksp = 4;
isDeath2 = 0;
if (room == p_2_lvl_1)
{
    audio_play_sound(music_3, 1000, true);
}
if (room == p_2_lvl_2)
{
    audio_play_sound(music_3, 1000, true);
}
if (room == p_2_lvl_3)
{
    audio_play_sound(music_3, 1000, true);
}
if (room == p_2_lvl_4)
{
    audio_play_sound(music_3, 1000, true);
}
if (room == p_2_lvl_5)
{
    audio_play_sound(music_3, 1000, true);
}
if (room == Menu)
{
    audio_play_sound(music_1, 1000, true);
}
else
{
    audio_stop_sound(music_1);
}
sprite_index = s2Playerright;
alarm = 10;
alarm[0] = alarm;

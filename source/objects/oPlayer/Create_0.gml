hsp = 0;
vsp = 0;
grv = 0.3;
walksp = 4;
isDeath = 0;
global.partSystem = part_system_create();
part_system_depth(global.partSystem, -1);
global.partDS = part_type_create();
part_type_life(global.partDS, 20, 40);
part_type_shape(global.partDS, 0);
part_type_size(global.partDS, 2, 3, -0.01, 0);
part_type_speed(global.partDS, 3, 5, 0, 0);
part_type_gravity(global.partDS, 0.07, 270);
part_type_color_mix(global.partDS, 8421504, 65535);
if (room == chapter_1)
{
    audio_play_sound(music_4, 1000, true);
}
if (room == Menu)
{
    audio_play_sound(music_1, 1000, true);
}
else
{
    audio_stop_sound(music_1);
}
sprite_index = sPlayerfront;
alarm = 10;
alarm[0] = alarm;

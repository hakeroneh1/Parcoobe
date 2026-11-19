/// @DnDAction : YoYo Games.Common.Execute_Code
/// @DnDVersion : 1
/// @DnDHash : 5EB2D6F6
/// @DnDArgument : "code" "hsp = 0;$(13_10)vsp = 0;$(13_10)grv = 0.3;$(13_10)walksp = 4;$(13_10)isDeath1 = false;$(13_10)$(13_10)$(13_10)//music$(13_10)$(13_10)if room = p_2_lvl_1$(13_10)audio_play_sound(music_3, 1000, true)$(13_10)$(13_10)$(13_10)if room = p_2_lvl_2 $(13_10)audio_play_sound(music_3, 1000, true)$(13_10)$(13_10)if room = p_2_lvl_3 $(13_10)audio_play_sound(music_3, 1000, true)$(13_10)$(13_10)if room = p_2_lvl_4 $(13_10)audio_play_sound(music_3, 1000, true)$(13_10)$(13_10)if room = p_2_lvl_5$(13_10)audio_play_sound(music_3, 1000, true)$(13_10)$(13_10)if room = Menu$(13_10)audio_play_sound(music_1, 1000, true)$(13_10)else $(13_10)audio_stop_sound(music_1);$(13_10)$(13_10)$(13_10)sprite_index = sPlayerfront$(13_10)$(13_10)alarm =10$(13_10)alarm[0] = alarm $(13_10)"
hsp = 0;
vsp = 0;
grv = 0.3;
walksp = 4;
isDeath1 = false;


//music

if room = p_2_lvl_1
audio_play_sound(music_3, 1000, true)


if room = p_2_lvl_2 
audio_play_sound(music_3, 1000, true)

if room = p_2_lvl_3 
audio_play_sound(music_3, 1000, true)

if room = p_2_lvl_4 
audio_play_sound(music_3, 1000, true)

if room = p_2_lvl_5
audio_play_sound(music_3, 1000, true)

if room = Menu
audio_play_sound(music_1, 1000, true)
else 
audio_stop_sound(music_1);


sprite_index = sPlayerfront

alarm =10
alarm[0] = alarm
/// @DnDAction : YoYo Games.Common.Execute_Code
/// @DnDVersion : 1
/// @DnDHash : 3AC4B96F
/// @DnDArgument : "code" "if (teamplay < 1)$(13_10)teamplay = teamplay + 1 $(13_10)else$(13_10)room_goto_next()$(13_10)audio_stop_sound(music_3)"
if (teamplay < 1)
teamplay = teamplay + 1 
else
room_goto_next()
audio_stop_sound(music_3)
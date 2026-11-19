/// @DnDAction : YoYo Games.Common.Execute_Code
/// @DnDVersion : 1
/// @DnDHash : 19BE396F
/// @DnDArgument : "code" "//moving$(13_10)key_left = keyboard_check (vk_left);$(13_10)key_right = keyboard_check (vk_right);$(13_10)key_jump = keyboard_check_pressed(vk_numpad0);$(13_10)$(13_10)var move = key_right - key_left;$(13_10)$(13_10)hsp = move * walksp;$(13_10)vsp = vsp + grv$(13_10)$(13_10)//jump$(13_10)if (place_meeting(x , y + 1 , oWall)) && (key_jump)$(13_10){$(13_10)	vsp = -10$(13_10)}$(13_10)$(13_10)//stopplayer$(13_10)if (place_meeting(x + hsp, y , oWall))$(13_10){$(13_10)	while (!place_meeting(x + sign(hsp) , y , oWall))$(13_10)	{$(13_10)		x = x + sign(hsp)$(13_10)	}$(13_10)	hsp = 0$(13_10)}$(13_10)$(13_10)x = x + hsp;$(13_10)$(13_10)//ground$(13_10)$(13_10)if (place_meeting(x , y + vsp , oWall))$(13_10){$(13_10)	while (!place_meeting(x , y + sign(vsp) , oWall))$(13_10)	{$(13_10)		y = y + sign(vsp)$(13_10)	}$(13_10)	vsp = 0$(13_10)}$(13_10)$(13_10)y = y + vsp$(13_10)$(13_10)//jump platform$(13_10)$(13_10)if (place_meeting(x , y + vsp , oJumpplatform))$(13_10){$(13_10)	vsp = -17$(13_10)}$(13_10)$(13_10)$(13_10)$(13_10)//death$(13_10)$(13_10)if (isDeath2 = true)$(13_10){$(13_10) room_restart()$(13_10) audio_stop_sound(music_3)$(13_10)}$(13_10)$(13_10)//animation$(13_10)if keyboard_check(vk_right)$(13_10){$(13_10)	sprite_index = s2Playerright$(13_10)}$(13_10)$(13_10)$(13_10)if keyboard_check(vk_left)$(13_10){$(13_10)	sprite_index = s2Playerleft$(13_10)}$(13_10)$(13_10)if room = fin $(13_10)alarm[0] =-1$(13_10)$(13_10)if alarm_get(alarm)=0$(13_10)game_end()$(13_10)$(13_10)$(13_10)$(13_10)$(13_10)$(13_10)$(13_10)$(13_10)$(13_10)"
//moving
key_left = keyboard_check (vk_left);
key_right = keyboard_check (vk_right);
key_jump = keyboard_check_pressed(vk_numpad0);

var move = key_right - key_left;

hsp = move * walksp;
vsp = vsp + grv

//jump
if (place_meeting(x , y + 1 , oWall)) && (key_jump)
{
	vsp = -10
}

//stopplayer
if (place_meeting(x + hsp, y , oWall))
{
	while (!place_meeting(x + sign(hsp) , y , oWall))
	{
		x = x + sign(hsp)
	}
	hsp = 0
}

x = x + hsp;

//ground

if (place_meeting(x , y + vsp , oWall))
{
	while (!place_meeting(x , y + sign(vsp) , oWall))
	{
		y = y + sign(vsp)
	}
	vsp = 0
}

y = y + vsp

//jump platform

if (place_meeting(x , y + vsp , oJumpplatform))
{
	vsp = -17
}



//death

if (isDeath2 = true)
{
 room_restart()
 audio_stop_sound(music_3)
}

//animation
if keyboard_check(vk_right)
{
	sprite_index = s2Playerright
}


if keyboard_check(vk_left)
{
	sprite_index = s2Playerleft
}

if room = fin 
alarm[0] =-1

if alarm_get(alarm)=0
game_end()
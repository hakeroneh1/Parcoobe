key_left = keyboard_check(vk_right);
key_right = keyboard_check(vk_left);
key_jump = keyboard_check_pressed(vk_space);
var move = key_right - key_left;
hsp = move * walksp;
vsp += grv;
if (place_meeting(x + hsp, y, oWall))
{
    while (!place_meeting(x + sign(hsp), y, oWall))
    {
        x += sign(hsp);
    }
    hsp = 0;
}
if (place_meeting(x + hsp, y, oDanger))
{
    while (!place_meeting(x + sign(hsp), y, oDanger))
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
if (place_meeting(x, y + vsp, oDanger))
{
    while (!place_meeting(x, y + sign(vsp), oDanger))
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

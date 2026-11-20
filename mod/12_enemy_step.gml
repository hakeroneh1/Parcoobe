// Parcoobe 2.0.4 — грибы ходят сами: патруль по платформе, разворот у стены/шипов и на краю.
if (!variable_instance_exists(id, "pco_dir"))
{
    pco_dir = choose(-1, 1);
    if (!variable_instance_exists(id, "walksp")) { walksp = 1.6; }
    if (!variable_instance_exists(id, "grv")) { grv = 0.3; }
    if (!variable_instance_exists(id, "vsp")) { vsp = 0; }
}

hsp = pco_dir * 1.2;   // грибы медленнее игрока
vsp += grv;

var pco_nx = x + hsp;
var pco_blocked = place_meeting(pco_nx, y, oWall) || place_meeting(pco_nx, y, oDanger);
var pco_ground_now = place_meeting(x, y + 1, oWall) || place_meeting(x, y + 1, oDanger);
var pco_ground_next = place_meeting(pco_nx, y + 1, oWall) || place_meeting(pco_nx, y + 1, oDanger);

if (pco_blocked)
{
    pco_dir = -pco_dir;
    hsp = 0;
}
else if (pco_ground_now && !pco_ground_next)
{
    // впереди обрыв — разворот, чтобы не падать в яму
    pco_dir = -pco_dir;
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
    vsp = -12;
}

image_xscale = (pco_dir < 0) ? -0.75 : 0.75;

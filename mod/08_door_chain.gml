// Parcoobe 2.0.3 — вход в дверь: явная цепочка уровней.
if (room == Menu)
{
    room_goto(lvl_1);
}
else if (room == lvl_1)
{
    room_goto(lvl_2);
}
else if (room == lvl_2)
{
    room_goto(lvl_3);
}
else if (room == lvl_3)
{
    room_goto(lvl_4);
}
else if (room == lvl_4)
{
    room_goto(lvl_5);
}
else if (room == lvl_5)
{
    room_goto(fin);
}
else
{
    room_goto_next();
}
audio_stop_sound(music_3);

if (room == Menu)
{
    room_goto(chapter_1);
}
else
{
    room_goto_next();
}
if (room == lvl_8 && global.hard == 1)
{
    room_goto(finwtf);
}
if (room == lvl_8 && global.hard == 0)
{
    room_goto(fin);
}

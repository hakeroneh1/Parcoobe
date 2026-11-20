// Parcoobe 2.0.6 — переходы: один маршрут на всю игру, с затемнением.
transition_steps = 16;
transition_color = c_black;
transition_kind = 3;            // fade out -> fade in

if (room == Menu)                   { room_goto(chapter_1); }
else if (room == chapter_1)         { room_goto(lvl_1); }
else if (room == lvl_1)             { room_goto(lvl_2); }
else if (room == lvl_2)             { room_goto(lvl_3); }
else if (room == lvl_3)             { room_goto(lvl_4); }
else if (room == lvl_4)             { room_goto(lvl_5); }
else if (room == lvl_5)             { room_goto(chapter_2); }
else if (room == chapter_2)         { room_goto(lvl_6); }
else if (room == lvl_6)             { room_goto(lvl_7); }
else if (room == lvl_7)             { room_goto(lvl_8); }
else if (room == lvl_8)             { room_goto(fin); }
else                                { room_goto_next(); }

audio_stop_sound(music_1);
audio_stop_sound(music_2);
audio_stop_sound(music_3);
audio_stop_sound(music_4);

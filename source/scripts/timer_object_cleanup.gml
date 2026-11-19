var _obj = (argument_count == 1) ? argument[0] : id;
ds_map_destroy(_obj.timers);
ds_list_destroy(_obj.active_timers);

var _owner = (argument_count == 3) ? argument[0] : id;
var _index = (argument_count == 3) ? argument[1] : argument[0];
var _all = (argument_count == 3) ? argument[2] : argument[1];
for (var i = 0; i < ds_list_size(_owner.active_timers); i++)
{
    var _active_timer = ds_list_find_value(_owner.active_timers, i);
    var _timer_data = _active_timer[3];
    var _timer_index = _timer_data[1];
    if (_timer_index == _index)
    {
        ds_list_delete(_owner.active_timers, i);
        i--;
        if (!_all)
        {
            break;
        }
    }
}
ds_map_delete(_owner.timers, string(_index));
return 1;

var _owner = (argument_count == 2) ? argument[0] : id;
var _index = (argument_count == 2) ? argument[1] : argument[0];
var _all = 1;
for (var i = 0; i < ds_list_size(_owner.active_timers); i++)
{
    var _active_timer = ds_list_find_value(_owner.active_timers, i);
    var _timer_data = _active_timer[3];
    var _timer_time = _active_timer[0];
    var _timer_dir = _active_timer[1];
    var _timer_start_time = _active_timer[2];
    var _timer_index = _timer_data[1];
    if (_timer_index == _index)
    {
        ds_list_replace(_owner.active_timers, i, [_timer_time, _timer_dir, _timer_start_time, _timer_data, 0]);
    }
    if (!_all)
    {
        return 1;
    }
}
return 1;

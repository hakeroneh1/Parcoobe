var _owner = (argument_count == 4) ? argument[0] : id;
var _index = (argument_count == 4) ? argument[1] : argument[0];
var _iter = (argument_count == 4) ? argument[3] : argument[2];
var _all = (argument_count == 4) ? argument[4] : argument[3];
for (var i = 0; i < ds_list_size(_owner.active_timers); i++)
{
    var _active_timer = ds_list_find_value(_owner.active_timers, i);
    var _active_timer_time = _active_timer[0];
    var _active_timer_dir = _active_timer[1];
    var _active_timer_data = _active_timer[3];
    var _active_timer_active = _active_timer[4];
    var _active_timer_start_time = _active_timer[2];
    var _active_timer_index = _active_timer_data[1];
    if (_active_timer_index == _index)
    {
        ds_list_set(_owner.active_timers, i, [_active_timer_time, _active_timer_dir, _active_timer_start_time, _active_timer_data, _active_timer_active, _iter]);
        if (!_all)
        {
            return 1;
        }
    }
}
return 1;

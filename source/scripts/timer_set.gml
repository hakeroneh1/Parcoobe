var _owner = (argument_count == 3) ? argument[0] : id;
var _index = (argument_count == 3) ? argument[1] : argument[0];
var _time = (argument_count == 3) ? argument[2] : argument[1];
var _dir = 1;
var _all = 0;
var _found = 0;
for (var i = 0; i < ds_list_size(_owner.active_timers); i++)
{
    var _active_timer = ds_list_find_value(_owner.active_timers, i);
    var _active_timer_data = _active_timer[3];
    var _active_timer_active = _active_timer[4];
    var _active_timer_iter = _active_timer[5];
    var _active_timer_index = _active_timer_data[1];
    if (_active_timer_index == _index)
    {
        if (_dir == 1)
        {
            ds_list_set(_owner.active_timers, i, [_time, _dir, _time, _active_timer_data, _active_timer_active, _active_timer_iter]);
        }
        else
        {
            ds_list_set(_owner.active_timers, i, [0, _dir, _time, _active_timer_data, _active_timer_active, _active_timer_iter]);
        }
        _found = 1;
        if (!_all)
        {
            return 1;
        }
    }
}
if (!_found)
{
    return timer_start_ext(_owner, _index, _time, _dir);
}
return 0;

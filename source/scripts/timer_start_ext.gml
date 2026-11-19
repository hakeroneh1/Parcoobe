var _owner = (argument_count == 4) ? argument[0] : id;
var _index = (argument_count == 4) ? argument[1] : argument[0];
var _time = (argument_count == 4) ? argument[2] : argument[1];
var _dir = (argument_count == 4) ? argument[3] : argument[2];
var _timer_data = ds_map_find_value(_owner.timers, string(_index));
var _instances = _timer_data[6];
var _count = 0;
for (var i = 0; i < ds_list_size(_owner.active_timers); i++)
{
    var _active_timer = ds_list_find_value(_owner.active_timers, i);
    var _active_timer_data = _active_timer[3];
    var _active_timer_index = _active_timer_data[1];
    if (_active_timer_index == _index)
    {
        _count++;
    }
}
if (_count < _instances)
{
    if (_dir == 1)
    {
        ds_list_add(_owner.active_timers, [_time, _dir, _time, _timer_data, 1, 0]);
    }
    else
    {
        ds_list_add(_owner.active_timers, [0, _dir, _time, _timer_data, 1, 0]);
    }
    return 1;
}
return 0;

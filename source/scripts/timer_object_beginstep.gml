var _obj = (argument_count == 1) ? argument[0] : id;
for (var i = 0; i < ds_list_size(_obj.active_timers); i++)
{
    var _active_timer = ds_list_find_value(_obj.active_timers, i);
    var _timer_time = _active_timer[0];
    var _timer_dir = _active_timer[1];
    var _timer_time_start = _active_timer[2];
    var _timer_data = _active_timer[3];
    var _timer_active = _active_timer[4];
    var _timer_iteration = _active_timer[5];
    var _timer_speed = _timer_data[2];
    var _timer_endaction = _timer_data[4];
    var _timer_index = _timer_data[1];
    var _timer_mod = _timer_data[5];
    var _max_iterations = _timer_data[7];
    var _exec_dir = _timer_data[8];
    if (_timer_active && _timer_time > -1)
    {
        var _endaction = 0;
        if (_timer_dir == 0)
        {
            if (_timer_time >= _timer_time_start)
            {
                _timer_time = _timer_time_start;
                _endaction = 1;
                if (_exec_dir == 0 || _exec_dir == 2)
                {
                    _timer_iteration++;
                }
            }
            else
            {
                _timer_time += _timer_speed;
            }
        }
        else if (_timer_time <= 0)
        {
            _timer_time = 0;
            _endaction = 1;
            if (_exec_dir == 1 || _exec_dir == 2)
            {
                _timer_iteration++;
            }
        }
        else
        {
            _timer_time -= _timer_speed;
        }
        ds_list_replace(_obj.active_timers, i, [_timer_time, _timer_dir, _timer_time_start, _timer_data, _timer_active, _timer_iteration]);
        if (_endaction)
        {
            if ((_timer_dir == _exec_dir || _exec_dir == 2) && (_timer_iteration % _timer_mod) == 0)
            {
                var _data = ds_map_find_value(_obj.timers, string(_timer_index));
                var _script = _data[3];
                if (_script != undefined && _script != -4 && script_exists(_script))
                {
                    script_execute(_script);
                    if (!instance_exists(id))
                    {
                        exit;
                    }
                    if (floor(_timer_iteration / _timer_mod) >= _max_iterations && _max_iterations > -1)
                    {
                        ds_list_delete(_obj.active_timers, i);
                        i--;
                        exit;
                    }
                }
            }
            switch (_timer_endaction)
            {
                case 0:
                    ds_list_delete(_obj.active_timers, i);
                    i--;
                    break;
                case 2:
                    var _new_dir = (_timer_dir == 1) ? 0 : 1;
                    ds_list_replace(_obj.active_timers, i, [_timer_time, _new_dir, _timer_time_start, _timer_data, _timer_active, _timer_iteration]);
                    break;
                case 1:
                    if (_timer_dir == 1)
                    {
                        ds_list_replace(_obj.active_timers, i, [_timer_time_start, _timer_dir, _timer_time_start, _timer_data, _timer_active, _timer_iteration]);
                    }
                    else
                    {
                        ds_list_replace(_obj.active_timers, i, [0, _timer_dir, _timer_time_start, _timer_data, _timer_active, _timer_iteration]);
                    }
                    break;
                case 3:
                    ds_list_delete(_obj.active_timers, i);
                    i--;
                    if (i == ds_list_size(_obj.active_timers))
                    {
                        var _index = _timer_data[1];
                        ds_map_delete(_obj.timers, string(_index));
                    }
                    break;
            }
        }
    }
    else if (_timer_time == -1)
    {
        ds_list_delete(_obj.active_timers, i);
        i--;
    }
}

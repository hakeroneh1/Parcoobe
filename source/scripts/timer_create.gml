var _index = argument[0];
var _script = argument[1];
var _owner = id;
var _speed = 1;
var _endaction = 0;
var _modulo = 1;
var _instances = 1;
var _max_iters = -1;
var _exec_dir = 1;
if (ds_map_exists(_owner.timers, string(_index)))
{
    show_debug_message("ERROR in script: timer_create() -- timer with index: " + string(_index) + " already exists. Please use a unique index when creating a timer.");
    return undefined;
}
var _timer = [_owner, _index, abs(_speed), _script, _endaction, _modulo, _instances, _max_iters, _exec_dir];
ds_map_set(_owner.timers, string(_index), _timer);
return _timer;

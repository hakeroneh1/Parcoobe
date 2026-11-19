var _owner = (argument_count == 9) ? argument[0] : id;
var _index = (argument_count == 9) ? argument[1] : argument[0];
var _speed = (argument_count == 9) ? argument[2] : argument[1];
var _script = (argument_count == 9) ? argument[3] : argument[2];
var _endaction = (argument_count == 9) ? argument[4] : argument[3];
var _modulo = (argument_count == 9) ? argument[5] : argument[4];
var _instances = (argument_count == 9) ? argument[6] : argument[5];
var _max_iters = (argument_count == 9) ? argument[7] : argument[6];
var _exec_dir = (argument_count == 9) ? argument[8] : argument[7];
if (ds_map_exists(_owner.timers, string(_index)))
{
    show_debug_message("ERROR in script: timer_create() -- timer with index: " + string(_index) + " already exists. Please use a unique index when creating a timer.");
    return undefined;
}
var _timer = [_owner, _index, abs(_speed), _script, _endaction, _modulo, _instances, _max_iters, _exec_dir];
ds_map_set(_owner.timers, string(_index), _timer);
return _timer;

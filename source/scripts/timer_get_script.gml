var _owner = (argument_count == 2) ? argument[0] : id;
var _index = (argument_count == 2) ? argument[1] : argument[0];
var _data = ds_map_find_value(_owner.timers, string(_index));
return _data[3];

// Parcoobe — авто-обновление: разбор ответа http_get (Async - HTTP).
if (ds_map_exists(async_load, "id"))
{
    var pco_id = ds_map_find_value(async_load, "id");
    if (pco_id == global.pco_req)
    {
        global.pco_req = -1;
        global.pco_upd_checked = 1;

        var pco_status = 0;
        if (ds_map_exists(async_load, "status"))
        {
            pco_status = ds_map_find_value(async_load, "status");
        }

        var pco_log = file_text_open_write("update.log");
        file_text_write_string(pco_log, "status=" + string(pco_status));
        if (ds_map_exists(async_load, "result"))
        {
            file_text_write_string(pco_log, " result=" + string(ds_map_find_value(async_load, "result")));
        }
        file_text_close(pco_log);

        if (pco_status != 1)
        {
            global.pco_msg = "UPDATE CHECK FAILED";
            global.pco_msg_t = 240;
        }

        if (pco_status == 1 && ds_map_exists(async_load, "result"))
        {
            var pco_s = string(ds_map_find_value(async_load, "result"));
            // обрезаем пробелы и переводы строк
            while (string_length(pco_s) > 0)
            {
                var pco_c = string_char_at(pco_s, string_length(pco_s));
                if (pco_c == " " || pco_c == "\n" || pco_c == "\r" || pco_c == "\t")
                {
                    pco_s = string_copy(pco_s, 1, string_length(pco_s) - 1);
                }
                else
                {
                    break;
                }
            }
            if (pco_s != "" && pco_s != global.pco_ver)
            {
                global.pco_upd = 1;
                global.pco_upd_ver = pco_s;
                global.pco_msg = "UPDATE FOUND";
            }
            else
            {
                global.pco_upd = 0;
                global.pco_msg = "YOU HAVE THE LATEST VERSION";
            }
            global.pco_msg_t = 240;
        }
    }
}

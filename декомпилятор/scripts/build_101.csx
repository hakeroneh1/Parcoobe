using System;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;

// 1. Добавляем oName Step и Draw GUI (их в оригинале нет — на них висит меню настроек).
void AddEvent(string objName, string codeName, int evType, uint evSubtype)
{
    var obj = Data.GameObjects.ByName(objName);
    var code = Data.Code.ByName(codeName);
    if (code == null)
    {
        code = new UndertaleCode();
        code.Name = Data.Strings.MakeString(codeName);
        Data.Code.Add(code);
    }
    var list = obj.Events[evType];
    if (list.Any(e => e.EventSubtype == evSubtype))
        return;
    var ev = new UndertaleGameObject.Event();
    ev.EventSubtype = evSubtype;
    var act = new UndertaleGameObject.EventAction();
    act.CodeId = code;
    ev.Actions.Add(act);
    list.Add(ev);
    Console.WriteLine("event: " + objName + " type=" + evType + " sub=" + evSubtype + " -> " + codeName);
}

AddEvent("oName", "gml_Object_oName_Step_0", 3, 0);
AddEvent("oName", "gml_Object_oName_Draw_64", 8, 64);
AddEvent("oName", "gml_Object_oName_Other_62", 7, 62);   // Async - HTTP
AddEvent("oPlayer", "gml_Object_oPlayer_Draw_64", 8, 64);      // панель CONTROLS в уровнях
AddEvent("oPlayer_1", "gml_Object_oPlayer_1_Draw_64", 8, 64);
AddEvent("oPlayer_2", "gml_Object_oPlayer_2_Draw_64", 8, 64);


// 1b. В меню вместо стрелок — клавиши A и D (по умолчанию ходят на A/D)
if (!string.IsNullOrEmpty(Environment.GetEnvironmentVariable("LEVELS_DIR")))
{
    var menu = Data.Rooms.ByName("Menu");
    if (menu != null)
    {
        var aObj = Data.GameObjects.ByName("oButtonA");
        var dObj = Data.GameObjects.ByName("oButtonD");
        var leftObj = Data.GameObjects.ByName("oButtonLeft");
        var rightObj = Data.GameObjects.ByName("oButtonRight");
        int swapped = 0;
        foreach (var layer in menu.Layers)
        {
            if (layer.InstancesData == null) continue;
            foreach (var go in layer.InstancesData.Instances)
            {
                if (go.ObjectDefinition == leftObj) { go.ObjectDefinition = aObj; swapped++; }
                else if (go.ObjectDefinition == rightObj) { go.ObjectDefinition = dObj; swapped++; }
            }
        }
        foreach (var go in menu.GameObjects)
        {
            if (go.ObjectDefinition == leftObj) go.ObjectDefinition = aObj;
            else if (go.ObjectDefinition == rightObj) go.ObjectDefinition = dObj;
        }
        Console.WriteLine("menu keys swapped: " + swapped);
    }
}

// 2. Полная переделка уровней: lvl_1..lvl_5 собираются с нуля из LEVELS_DIR/*.json
string levelsDir = Environment.GetEnvironmentVariable("LEVELS_DIR");
if (!string.IsNullOrEmpty(levelsDir))
{
    var doorObj = Data.GameObjects.ByName("oDoor");
    var wallObj = Data.GameObjects.ByName("oWall");
    var dangerObj = Data.GameObjects.ByName("oDanger");
    var jumpObj = Data.GameObjects.ByName("oJumpplatform");
    var playerObj = Data.GameObjects.ByName("oPlayer");
    var enemyObj = Data.GameObjects.ByName("oMushroomBleb");
    var p1Obj = Data.GameObjects.ByName("oPlayer_1");
    var p2Obj = Data.GameObjects.ByName("oPlayer_2");

    foreach (var name in new[] { "chapter_1", "lvl_1", "lvl_2", "lvl_3", "lvl_4", "lvl_5",
                                 "chapter_2", "lvl_6", "lvl_7", "lvl_8",
                                 "p_2_lvl_1", "p_2_lvl_2", "p_2_lvl_3", "p_2_lvl_4", "p_2_lvl_5" })
    {
        string file = System.IO.Path.Combine(levelsDir, name + ".json");
        if (!System.IO.File.Exists(file))
            continue;
        var doc = System.Text.Json.JsonDocument.Parse(System.IO.File.ReadAllText(file));
        var list = doc.RootElement.GetProperty("instances");
        var room = Data.Rooms.ByName(name);
        if (room == null) { Console.WriteLine("no room " + name); continue; }

        foreach (var layer in room.Layers)
            if (layer.InstancesData != null)
                layer.InstancesData.Instances.Clear();
        room.GameObjects.Clear();

        UndertaleRoom.Layer instLayer = null;
        foreach (var layer in room.Layers)
            if (layer.InstancesData != null) { instLayer = layer; break; }
        if (instLayer == null)
        {
            instLayer = new UndertaleRoom.Layer
            {
                LayerName = Data.Strings.MakeString("Instances"),
                LayerId = 200,
                LayerType = UndertaleRoom.LayerType.Instances,
                LayerDepth = 0,
                IsVisible = true,
                Data = new UndertaleRoom.Layer.LayerInstancesData(),
            };
            room.Layers.Add(instLayer);
        }

        int count = 0;
        foreach (var inst in list.EnumerateArray())
        {
            string objName = inst[0].GetString();
            int x = (int)System.Math.Round((double)inst[1].GetSingle());
            int y = (int)System.Math.Round((double)inst[2].GetSingle());
            float sx = inst[3].GetSingle();
            float sy = inst[4].GetSingle();
            UndertaleGameObject def = null;
            if (objName == "oWall") def = wallObj;
            else if (objName == "oDanger") def = dangerObj;
            else if (objName == "oJumpplatform") def = jumpObj;
            else if (objName == "oDoor") def = doorObj;
            else if (objName == "oPlayer") def = playerObj;
            else if (objName == "oPlayer_1") def = p1Obj;
            else if (objName == "oPlayer_2") def = p2Obj;
            else if (objName == "oMushroomBleb") def = enemyObj;
            if (def == null)
                continue;
            var go = new UndertaleRoom.GameObject
            {
                ObjectDefinition = def,
                X = x,
                Y = y,
                ScaleX = sx,
                ScaleY = sy,
                InstanceID = ++Data.GeneralInfo.LastObj,
                Color = 0xFFFFFFFF,
            };
            room.GameObjects.Add(go);
            instLayer.InstancesData.Instances.Add(go);
            count++;
        }
        // размер комнаты берём из JSON: уровни шире экрана
        room.Width = doc.RootElement.GetProperty("width").GetUInt32();
        room.Height = doc.RootElement.GetProperty("height").GetUInt32();

        // вид, который едет за игроком: без флага EnableViews камера не создаётся
        room.Flags |= UndertaleRoom.RoomEntryFlags.EnableViews;
        var view = room.Views[0];
        view.Enabled = true;
        view.ViewX = 0;
        view.ViewY = 0;
        view.ViewWidth = 1280;
        view.ViewHeight = 720;
        view.PortX = 0;
        view.PortY = 0;
        view.PortWidth = 1280;
        view.PortHeight = 720;
        view.BorderX = 320;
        view.BorderY = 96;
        view.SpeedX = -1;
        view.SpeedY = -1;
        view.ObjectId = playerObj;

        // фон: город тайлится по горизонтали и едет медленнее комнаты (параллакс)
        var citySprite = Data.Sprites.ByName("dead_city");
        int bgDepth = 0;
        foreach (var layer in room.Layers)
        {
            if (layer.BackgroundData != null)
            {
                layer.BackgroundData.Sprite = citySprite;
                layer.BackgroundData.TiledHorizontally = true;
                layer.BackgroundData.TiledVertically = false;
                layer.BackgroundData.Color = 0xFFFFFFFF;
                layer.HSpeed = 0.55f;
                layer.VSpeed = 0.0f;
                bgDepth = System.Math.Max(bgDepth, layer.LayerDepth);
            }
        }

        // позади города — слой кладки, ещё медленнее: на фоне всегда есть фактура
        if (!room.Layers.Any(l => l.LayerName.Content == "BGBack"))
        {
            var bd = new UndertaleRoom.Layer.LayerBackgroundData();
            bd.Sprite = Data.Sprites.ByName("bricks_background");
            bd.TiledHorizontally = true;
            bd.TiledVertically = false;
            bd.Stretch = false;
            bd.Color = 0x60241820;
            var back = new UndertaleRoom.Layer
            {
                LayerName = Data.Strings.MakeString("BGBack"),
                LayerId = 500,
                LayerType = UndertaleRoom.LayerType.Background,
                LayerDepth = bgDepth + 100,
                IsVisible = true,
                HSpeed = 0.25f,
                VSpeed = 0.0f,
                Data = bd,
            };
            room.Layers.Add(back);
        }

        room.SetupRoom(false, false);
        Console.WriteLine("rebuilt " + name + ": " + count + " instances, " + room.Width + "x" + room.Height + ", view=" + view.Enabled);
    }
}

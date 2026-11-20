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

// 2. Выравниваем позиции тайлов по целым пикселям: дробные координаты
//    (59.0 / 27.2 и т.п.) давали швы между текстурами стен.
int snapped = 0;
foreach (var room in Data.Rooms)
{
    void Snap(UndertaleRoom.GameObject inst)
    {
        string name = inst.ObjectDefinition?.Name?.Content;
        if (name == null)
            return;
        bool tile = name == "oWall" || name == "oDanger" || name == "oDoor"
                 || name == "oClosedoor" || name == "oDoorHard" || name == "oDoorlevelselect"
                 || name == "oDoorSkins" || name == "oDoor2player" || name == "oJumpplatform";
        if (!tile)
            return;
        int nx = (int)System.Math.Round((double)inst.X);
        int ny = (int)System.Math.Round((double)inst.Y);
        if (nx != inst.X || ny != inst.Y)
        {
            inst.X = nx;
            inst.Y = ny;
            snapped++;
        }
    }
    foreach (var layer in room.Layers)
        if (layer.InstancesData != null)
            foreach (var inst in layer.InstancesData.Instances)
                Snap(inst);
    if (room.GameObjects != null)
        foreach (var inst in room.GameObjects)
            Snap(inst);
}
Console.WriteLine("snapped tile positions: " + snapped);

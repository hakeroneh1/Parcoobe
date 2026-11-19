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

// 2. Убираем из комнаты Menu старые кнопки: выход (X) и звук — вместо них кнопка MENU.
var menu = Data.Rooms.ByName("Menu");
bool IsButton(UndertaleRoom.GameObject inst)
{
    string name = inst.ObjectDefinition?.Name?.Content;
    return name == "oExitbutton" || name == "oSound_button";
}

int removed = 0;
foreach (var layer in menu.Layers)
{
    var data = layer.InstancesData;
    if (data == null)
        continue;
    for (int i = data.Instances.Count - 1; i >= 0; i--)
    {
        if (IsButton(data.Instances[i]))
        {
            data.Instances.RemoveAt(i);
            removed++;
        }
    }
}
// в GMS2 у комнаты есть ещё и плоский список инстансов (по нему тоже создаются объекты)
if (menu.GameObjects != null)
{
    var ids = new System.Collections.Generic.List<uint>();
    for (int i = menu.GameObjects.Count - 1; i >= 0; i--)
    {
        if (IsButton(menu.GameObjects[i]))
        {
            ids.Add(menu.GameObjects[i].InstanceID);
            menu.GameObjects.RemoveAt(i);
            removed++;
        }
    }
    if (ids.Count > 0 && menu.InstanceCreationOrderIDs != null)
    {
        var order = menu.InstanceCreationOrderIDs.InstanceIDs;
        for (int i = order.Count - 1; i >= 0; i--)
            if (ids.Contains(order[i]))
                order.RemoveAt(i);
    }
}
Console.WriteLine("removed menu buttons: " + removed);

// 3. Двери-выходы справа стояли за краем экрана (x=1280) — сдвигаем их в кадр,
//    чтобы входы были видны и в них можно было войти, не уходя за границу комнаты.
int movedDoors = 0;
foreach (var room in Data.Rooms)
{
    void FixDoor(UndertaleRoom.GameObject inst)
    {
        string name = inst.ObjectDefinition?.Name?.Content;
        if (name != null && name.StartsWith("oDoor") && inst.X >= 1280)
        {
            inst.X = 1216;
            movedDoors++;
        }
    }
    foreach (var layer in room.Layers)
        if (layer.InstancesData != null)
            foreach (var inst in layer.InstancesData.Instances)
                FixDoor(inst);
    if (room.GameObjects != null)
        foreach (var inst in room.GameObjects)
            FixDoor(inst);
}
Console.WriteLine("moved doors into view: " + movedDoors);

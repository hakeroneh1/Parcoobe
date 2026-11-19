// Экспорт метаданных проекта Parcoob из data.win в текстовый вид.
// Запуск: dotnet UndertaleModCli.dll load <data.win> --scripts export_source.csx
// Куда писать: переменная окружения EXPORT_ROOT (по умолчанию ./export).

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;
using UndertaleModLib;
using UndertaleModLib.Models;

string root = Environment.GetEnvironmentVariable("EXPORT_ROOT");
if (string.IsNullOrEmpty(root))
    root = Path.Combine(Environment.CurrentDirectory, "export");

foreach (string sub in new[] { "rooms", "metadata", "sounds" })
    Directory.CreateDirectory(Path.Combine(root, sub));

var jsonSettings = new JsonSerializerSettings { Formatting = Formatting.Indented, NullValueHandling = NullValueHandling.Ignore };
Action<string, object> save = (rel, obj) =>
    File.WriteAllText(Path.Combine(root, rel), JsonConvert.SerializeObject(obj, jsonSettings), new UTF8Encoding(false));

string S(UndertaleString s) => s?.Content;

// ---------------------------------------------------------------- general
var general = new Dictionary<string, object>
{
    ["project_name"] = S(Data.GeneralInfo.Name),
    ["file_name"] = S(Data.GeneralInfo.FileName),
    ["config"] = S(Data.GeneralInfo.Config),
    ["game_maker_2"] = Data.IsGameMaker2(),
    ["bytecode_version"] = Data.GeneralInfo.BytecodeVersion,
    ["runtime"] = $"{Data.GeneralInfo.Major}.{Data.GeneralInfo.Minor}.{Data.GeneralInfo.Release}.{Data.GeneralInfo.Build}",
    ["window_width"] = Data.GeneralInfo.DefaultWindowWidth,
    ["window_height"] = Data.GeneralInfo.DefaultWindowHeight,
    ["counts"] = new Dictionary<string, int>
    {
        ["objects"] = Data.GameObjects.Count,
        ["sprites"] = Data.Sprites.Count,
        ["sounds"] = Data.Sounds.Count,
        ["rooms"] = Data.Rooms.Count,
        ["scripts"] = Data.Scripts.Count,
        ["fonts"] = Data.Fonts.Count,
        ["paths"] = Data.Paths.Count,
        ["code"] = Data.Code.Count,
        ["strings"] = Data.Strings.Count,
    },
    ["room_order"] = Data.Rooms.Select(r => S(r.Name)).ToList(),
};
save("metadata/general.json", general);

// ---------------------------------------------------------------- objects
var objects = new List<object>();
foreach (var go in Data.GameObjects)
{
    var events = new List<object>();
    for (int type = 0; type < go.Events.Count; type++)
    {
        var evList = go.Events[type];
        if (evList == null)
            continue;
        foreach (var ev in evList)
        {
            if (ev == null)
                continue;
            var codes = new List<string>();
            if (ev.Actions != null)
                foreach (var action in ev.Actions)
                    if (action?.CodeId != null)
                        codes.Add(S(action.CodeId.Name));
            events.Add(new Dictionary<string, object>
            {
                ["event_type"] = ((EventType)type).ToString(),
                ["event_subtype"] = ev.EventSubtype,
                ["code_entries"] = codes,
            });
        }
    }

    objects.Add(new Dictionary<string, object>
    {
        ["name"] = S(go.Name),
        ["sprite"] = S(go.Sprite?.Name),
        ["parent"] = S(go.ParentId?.Name),
        ["visible"] = go.Visible,
        ["solid"] = go.Solid,
        ["persistent"] = go.Persistent,
        ["depth"] = go.Depth,
        ["physics"] = go.UsesPhysics,
        ["events"] = events,
    });
}
save("metadata/objects.json", objects);

// ---------------------------------------------------------------- sprites
var sprites = new List<object>();
foreach (var sp in Data.Sprites)
{
    var frames = new List<object>();
    foreach (var te in sp.Textures)
    {
        var tpi = te?.Texture;
        frames.Add(new Dictionary<string, object>
        {
            ["page_target_x"] = tpi?.TargetX ?? 0,
            ["page_target_y"] = tpi?.TargetY ?? 0,
            ["page_source_x"] = tpi?.SourceX ?? 0,
            ["page_source_y"] = tpi?.SourceY ?? 0,
            ["page_width"] = tpi?.SourceWidth ?? 0,
            ["page_height"] = tpi?.SourceHeight ?? 0,
        });
    }

    sprites.Add(new Dictionary<string, object>
    {
        ["name"] = S(sp.Name),
        ["width"] = sp.Width,
        ["height"] = sp.Height,
        ["origin_x"] = sp.OriginX,
        ["origin_y"] = sp.OriginY,
        ["margin_left"] = sp.MarginLeft,
        ["margin_right"] = sp.MarginRight,
        ["margin_top"] = sp.MarginTop,
        ["margin_bottom"] = sp.MarginBottom,
        ["transparent"] = sp.Transparent,
        ["smooth"] = sp.Smooth,
        ["preload"] = sp.Preload,
        ["playback_speed"] = sp.GMS2PlaybackSpeed,
        ["frame_count"] = frames.Count,
        ["frames"] = frames,
    });
}
save("metadata/sprites.json", sprites);

// ---------------------------------------------------------------- sounds
var sounds = new List<object>();
foreach (var snd in Data.Sounds)
{
    byte[] audio = snd.AudioFile?.Data;
    string embeddedFile = null;
    if (audio != null && audio.Length > 4)
    {
        string ext = ".bin";
        if (audio[0] == (byte)'O' && audio[1] == (byte)'g' && audio[2] == (byte)'g' && audio[3] == (byte)'S') ext = ".ogg";
        else if (audio[0] == (byte)'R' && audio[1] == (byte)'I' && audio[2] == (byte)'F' && audio[3] == (byte)'F') ext = ".wav";
        else if (audio[0] == 0xFF && audio[1] == 0xFB) ext = ".mp3";
        embeddedFile = "sounds/" + S(snd.Name) + ext;
        File.WriteAllBytes(Path.Combine(root, embeddedFile), audio);
    }

    sounds.Add(new Dictionary<string, object>
    {
        ["name"] = S(snd.Name),
        ["type"] = S(snd.Type),
        ["file"] = S(snd.File),
        ["flags"] = snd.Flags.ToString(),
        ["volume"] = snd.Volume,
        ["pitch"] = snd.Pitch,
        ["preload"] = snd.Preload,
        ["embedded_audio_size"] = audio?.Length ?? 0,
        ["exported_file"] = embeddedFile,
    });
}
save("metadata/sounds.json", sounds);

// ---------------------------------------------------------------- fonts
var fonts = new List<object>();
foreach (var f in Data.Fonts)
{
    fonts.Add(new Dictionary<string, object>
    {
        ["name"] = S(f.Name),
        ["display_name"] = S(f.DisplayName),
        ["em_size"] = f.EmSize,
        ["bold"] = f.Bold,
        ["italic"] = f.Italic,
        ["range_start"] = f.RangeStart,
        ["range_end"] = f.RangeEnd,
        ["glyph_count"] = f.Glyphs.Count,
    });
}
save("metadata/fonts.json", fonts);

// ---------------------------------------------------------------- paths
var paths = new List<object>();
foreach (var p in Data.Paths)
{
    var points = new List<object>();
    foreach (var pt in p.Points)
        points.Add(new Dictionary<string, object> { ["x"] = pt.X, ["y"] = pt.Y, ["speed"] = pt.Speed });
    paths.Add(new Dictionary<string, object>
    {
        ["name"] = S(p.Name),
        ["smooth"] = p.IsSmooth,
        ["closed"] = p.IsClosed,
        ["precision"] = p.Precision,
        ["points"] = points,
    });
}
save("metadata/paths.json", paths);

// ---------------------------------------------------------------- rooms
foreach (var room in Data.Rooms)
{
    var layers = new List<object>();
    var instances = new List<object>();
    int tileCount = 0;

    foreach (var layer in room.Layers)
    {
        var layerInfo = new Dictionary<string, object>
        {
            ["name"] = S(layer.LayerName),
            ["type"] = layer.LayerType.ToString(),
            ["depth"] = layer.LayerDepth,
            ["visible"] = layer.IsVisible,
        };

        if (layer.InstancesData != null)
        {
            layerInfo["instance_count"] = layer.InstancesData.Instances.Count;
            foreach (var inst in layer.InstancesData.Instances)
            {
                instances.Add(new Dictionary<string, object>
                {
                    ["object"] = S(inst.ObjectDefinition?.Name),
                    ["layer"] = S(layer.LayerName),
                    ["x"] = inst.X,
                    ["y"] = inst.Y,
                    ["scale_x"] = inst.ScaleX,
                    ["scale_y"] = inst.ScaleY,
                    ["rotation"] = inst.Rotation,
                    ["color"] = inst.Color,
                    ["instance_id"] = inst.InstanceID,
                    ["creation_code"] = S(inst.CreationCode?.Name),
                });
            }
        }
        else if (layer.TilesData != null)
        {
            int n = 0;
            var tileData = layer.TilesData.TileData;
            if (tileData != null)
                foreach (var row in tileData)
                    if (row != null)
                        n += row.Length;
            tileCount += n;
            layerInfo["tile_count"] = n;
        }
        else if (layer.BackgroundData != null)
        {
            layerInfo["background"] = S(layer.BackgroundData.Sprite?.Name);
        }

        layers.Add(layerInfo);
    }

    // instances могут лежать только в новом формате слоёв, но у GMS2 бывает и старый список
    if (instances.Count == 0 && room.GameObjects != null)
    {
        foreach (var inst in room.GameObjects)
        {
            instances.Add(new Dictionary<string, object>
            {
                ["object"] = S(inst.ObjectDefinition?.Name),
                ["layer"] = null,
                ["x"] = inst.X,
                ["y"] = inst.Y,
                ["scale_x"] = inst.ScaleX,
                ["scale_y"] = inst.ScaleY,
                ["rotation"] = inst.Rotation,
                ["color"] = inst.Color,
                ["instance_id"] = inst.InstanceID,
                ["creation_code"] = S(inst.CreationCode?.Name),
            });
        }
    }

    var roomInfo = new Dictionary<string, object>
    {
        ["name"] = S(room.Name),
        ["caption"] = S(room.Caption),
        ["width"] = room.Width,
        ["height"] = room.Height,
        ["speed"] = room.Speed,
        ["persistent"] = room.Persistent,
        ["background_color"] = room.BackgroundColor,
        ["draw_background_color"] = room.DrawBackgroundColor,
        ["creation_code"] = S(room.CreationCodeId?.Name),
        ["instances"] = instances,
        ["instance_count"] = instances.Count,
        ["tile_count"] = tileCount,
        ["layers"] = layers,
    };
    save("rooms/" + (S(room.Name) ?? ("room_" + room.Name)) + ".json", roomInfo);
}

// ---------------------------------------------------------------- variables / functions
var variables = new List<object>();
foreach (var v in Data.Variables)
    variables.Add(new Dictionary<string, object>
    {
        ["name"] = S(v.Name),
        ["instance_type"] = v.InstanceType.ToString(),
        ["var_id"] = v.VarID,
        ["occurrences"] = v.Occurrences,
    });
save("metadata/variables.json", variables);

var functions = new List<object>();
foreach (var f in Data.Functions)
    functions.Add(new Dictionary<string, object>
    {
        ["name"] = S(f.Name),
        ["classification"] = f.Classification.ToString(),
        ["occurrences"] = f.Occurrences,
    });
save("metadata/functions.json", functions);

// ---------------------------------------------------------------- texture page items
var tpis = new List<object>();
for (int i = 0; i < Data.TexturePageItems.Count; i++)
{
    var tpi = Data.TexturePageItems[i];
    int pageIndex = -1;
    for (int t = 0; t < Data.EmbeddedTextures.Count; t++)
        if (ReferenceEquals(Data.EmbeddedTextures[t], tpi.TexturePage)) { pageIndex = t; break; }
    tpis.Add(new Dictionary<string, object>
    {
        ["index"] = i,
        ["texture_page"] = pageIndex,
        ["target_x"] = tpi.TargetX,
        ["target_y"] = tpi.TargetY,
        ["source_x"] = tpi.SourceX,
        ["source_y"] = tpi.SourceY,
        ["source_width"] = tpi.SourceWidth,
        ["source_height"] = tpi.SourceHeight,
        ["bounding_width"] = tpi.BoundingWidth,
        ["bounding_height"] = tpi.BoundingHeight,
    });
}
save("metadata/texture_page_items.json", tpis);

Console.WriteLine($"Exported to: {root}");

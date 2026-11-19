// Переименование игры Parcoob -> Parcoobe прямо в data.win.
// Запуск: dotnet UndertaleModCli.dll load <data.win> --scripts rename_to_parcoobe.csx --output <out data.win> --overwrite

using System;
using System.Collections.Generic;
using UndertaleModLib;
using UndertaleModLib.Models;

var replacements = new Dictionary<string, string>(StringComparer.Ordinal)
{
    ["Parcoob"] = "Parcoobe",
    ["PARCOOB"] = "PARCOOBE",
};

int changed = 0;
foreach (var str in Data.Strings)
{
    if (str == null || str.Content == null)
        continue;

    if (replacements.TryGetValue(str.Content, out string replacement))
    {
        Console.WriteLine($"rename string #{changed}: '{str.Content}' -> '{replacement}'");
        str.Content = replacement;
        changed++;
    }
}

Console.WriteLine($"Replaced {changed} string(s).");

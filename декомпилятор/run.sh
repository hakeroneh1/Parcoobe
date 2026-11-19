#!/usr/bin/env bash
# Запуск собранного UndertaleModTool CLI.
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
DLL="$DIR/UndertaleModTool/UndertaleModCli/bin/Release/net10.0/UndertaleModCli.dll"

if [ ! -f "$DLL" ]; then
    echo "Декомпилятор не собран. Запустите ./build.sh" >&2
    exit 1
fi

exec dotnet "$DLL" "$@"

#!/usr/bin/env bash
# Сборка декомпилятора (UndertaleModTool CLI) из исходников.
# Требуется .NET SDK 10 (в Ubuntu: apt install dotnet-sdk-10.0).
set -euo pipefail

cd "$(dirname "$0")/UndertaleModTool"
dotnet build UndertaleModCli/UndertaleModCli.csproj -c Release -v m

echo
echo "Готово: декомпилятор/UndertaleModTool/UndertaleModCli/bin/Release/net10.0/UndertaleModCli.dll"
echo "Запуск: ./run.sh <команда> ...  (например: ./run.sh info ../original/data.win)"

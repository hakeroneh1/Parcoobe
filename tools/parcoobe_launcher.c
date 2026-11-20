/*
 * Parcoobe — лаунчер «один exe».
 *
 * К хвосту этого файла приклеен архив (см. tools/build_single_exe.py):
 *   entries:  uint32 name_len, name (UTF-8), uint64 size, size байт данных
 *   trailer:  "PCOBSPL1" (8), uint64 payload_offset, uint64 payload_size
 *
 * Что делает: распаковывает содержимое в %LOCALAPPDATA%\Parcoobe\<версия>\
 * и запускает оттуда Parcoobe.exe, дожидаясь его завершения.
 *
 * Сборка: x86_64-w64-mingw32-gcc -O2 -mwindows -o Parcoobe.exe parcoobe_launcher.c
 */
#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define TRAILER_MAGIC "PCOBSPL1"
#define TRAILER_SIZE 24

static void fail(const wchar_t *what)
{
    wchar_t msg[512];
    _snwprintf(msg, 512, L"Parcoobe: %ls\n\nКод ошибки: %lu", what, GetLastError());
    MessageBoxW(NULL, msg, L"Parcoobe", MB_ICONERROR | MB_OK);
    ExitProcess(1);
}

static uint32_t rd32(const unsigned char *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint64_t rd64(const unsigned char *p)
{
    return (uint64_t)rd32(p) | ((uint64_t)rd32(p + 4) << 32);
}

static int file_size_matches(const wchar_t *path, uint64_t size)
{
    WIN32_FILE_ATTRIBUTE_DATA fad;
    if (!GetFileAttributesExW(path, GetFileExInfoStandard, &fad))
        return 0;
    if (fad.nFileSizeHigh != (DWORD)(size >> 32) || fad.nFileSizeLow != (DWORD)(size & 0xFFFFFFFF))
        return 0;
    return 1;
}

static void write_file(const wchar_t *path, const unsigned char *data, uint64_t size)
{
    if (file_size_matches(path, size))
        return;
    HANDLE h = CreateFileW(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE)
        fail(path);
    uint64_t left = size;
    const unsigned char *p = data;
    while (left > 0)
    {
        DWORD chunk = (DWORD)(left > (1u << 20) ? (1u << 20) : left);
        DWORD written = 0;
        if (!WriteFile(h, p, chunk, &written, NULL) || written != chunk)
        {
            CloseHandle(h);
            fail(L"запись файла");
        }
        p += chunk;
        left -= chunk;
    }
    CloseHandle(h);
}

static void mkdir_tree(const wchar_t *path)
{
    wchar_t tmp[MAX_PATH];
    wcsncpy_s(tmp, MAX_PATH, path, _TRUNCATE);
    for (wchar_t *p = tmp; *p; p++)
    {
        if (*p == L'\\' || *p == L'/')
        {
            wchar_t save = *p;
            *p = 0;
            if (tmp[0] && !CreateDirectoryW(tmp, NULL) && GetLastError() != ERROR_ALREADY_EXISTS)
                ; /* промежуточный каталог мог уже существовать */
            *p = save;
        }
    }
    if (!CreateDirectoryW(tmp, NULL) && GetLastError() != ERROR_ALREADY_EXISTS)
        fail(tmp);
}

int WINAPI wWinMain(HINSTANCE hInst, HINSTANCE hPrev, PWSTR cmdline, int show)
{
    (void)hInst;
    (void)hPrev;
    (void)cmdline;
    (void)show;
    wchar_t exe_path[MAX_PATH];
    if (!GetModuleFileNameW(NULL, exe_path, MAX_PATH))
        fail(L"не удалось определить путь к exe");

    HANDLE h = CreateFileW(exe_path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING,
                           FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE)
        fail(L"не удалось открыть сам exe");

    LARGE_INTEGER fsize;
    if (!GetFileSizeEx(h, &fsize) || fsize.QuadPart < TRAILER_SIZE)
        fail(L"файл слишком мал");

    unsigned char trailer[TRAILER_SIZE];
    LARGE_INTEGER pos;
    DWORD got = 0;
    pos.QuadPart = fsize.QuadPart - TRAILER_SIZE;
    SetFilePointerEx(h, pos, NULL, FILE_BEGIN);
    if (!ReadFile(h, trailer, TRAILER_SIZE, &got, NULL) || got != TRAILER_SIZE)
        fail(L"не удалось прочитать хвост");
    if (memcmp(trailer, TRAILER_MAGIC, 8) != 0)
    {
        MessageBoxW(NULL, L"Внутри exe нет данных игры (файл повреждён или это не Parcoobe).",
                    L"Parcoobe", MB_ICONERROR | MB_OK);
        CloseHandle(h);
        return 1;
    }

    uint64_t payload_offset = rd64(trailer + 8);
    uint64_t payload_size = rd64(trailer + 16);
    if (payload_offset + payload_size > (uint64_t)fsize.QuadPart)
        fail(L"повреждённый архив");

    unsigned char *payload = (unsigned char *)malloc((size_t)payload_size);
    if (!payload)
        fail(L"нет памяти");
    pos.QuadPart = (LONGLONG)payload_offset;
    SetFilePointerEx(h, pos, NULL, FILE_BEGIN);
    uint64_t left = payload_size;
    unsigned char *p = payload;
    while (left > 0)
    {
        DWORD chunk = (DWORD)(left > (1u << 20) ? (1u << 20) : left);
        if (!ReadFile(h, p, chunk, &got, NULL) || got != chunk)
            fail(L"не удалось прочитать архив");
        p += chunk;
        left -= chunk;
    }
    CloseHandle(h);

    /* каталог распаковки: %LOCALAPPDATA%\Parcoobe\game */
    wchar_t dir[MAX_PATH];
    DWORD n = GetEnvironmentVariableW(L"LOCALAPPDATA", dir, MAX_PATH);
    if (n == 0 || n >= MAX_PATH)
        fail(L"нет переменной LOCALAPPDATA");
    wcscat_s(dir, MAX_PATH, L"\\Parcoobe\\game");
    mkdir_tree(dir);

    /* разбор архива */
    uint64_t off = 0;
    while (off + 4 <= payload_size)
    {
        uint32_t name_len = rd32(payload + off);
        off += 4;
        if (name_len == 0 || name_len > 260 || off + name_len + 8 > payload_size)
            break;
        wchar_t name[300];
        for (uint32_t i = 0; i < name_len; i++)
            name[i] = (wchar_t)payload[off + i];
        name[name_len] = 0;
        off += name_len;
        uint64_t size = rd64(payload + off);
        off += 8;
        if (off + size > payload_size)
            break;
        wchar_t path[MAX_PATH];
        _snwprintf(path, MAX_PATH, L"%ls\\%ls", dir, name);
        write_file(path, payload + off, size);
        off += size;
    }
    free(payload);

    /* запуск игры */
    wchar_t game[MAX_PATH];
    _snwprintf(game, MAX_PATH, L"%ls\\Parcoobe.exe", dir);
    wchar_t cmd[MAX_PATH + 8];
    _snwprintf(cmd, MAX_PATH + 8, L"\"%ls\"", game);

    STARTUPINFOW si;
    PROCESS_INFORMATION pi;
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    ZeroMemory(&pi, sizeof(pi));
    if (!CreateProcessW(game, cmd, NULL, NULL, FALSE, 0, NULL, dir, &si, &pi))
        fail(L"не удалось запустить игру");

    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code = 0;
    GetExitCodeProcess(pi.hProcess, &code);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return (int)code;
}

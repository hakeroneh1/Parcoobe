#!/usr/bin/env python3
"""Генерация чиптюн-саундтреков для Parcoobe (2.0.4).

Три зацикленных трека в духе оригинала (тёмный платформер, 8-бит):
    music_2 — «Under the Dead City»: медленная минорная арпеджио-тема;
    music_3 — «Rusted Pipes»: напряжённый бас и редкие аккорды;
    music_4 — «Last Sprint»: быстрый боевой луп.

Пишет WAV во временный каталог и кодирует в OGG (ffmpeg), потому что игра
подхватывает внешние music_N.ogg рядом с exe.

Запуск:  python3 tools/make_music.py [--out build]
"""
import argparse
import math
import os
import struct
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100


def env(n, attack=0.004, decay=0.12, sustain=0.6, release=0.08, gate=1.0):
    """Простая ADSR-огибающая длиной n сэмплов."""
    a = max(1, int(attack * SR))
    d = max(1, int(decay * SR))
    r = max(1, int(release * SR))
    s_start = a + d
    g = int(n * min(1.0, max(0.05, gate)))
    e = np.ones(n)
    e[:min(a, n)] = np.linspace(0, 1, min(a, n))
    if s_start < n:
        k = min(d, n - a)
        e[a:a + k] = np.linspace(1, sustain, k)
        e[a + k:] = sustain
    tail = min(r, n)
    e[n - tail:] *= np.linspace(1, 0, tail)
    if g < n:
        e[g:] *= np.linspace(1, 0, n - g) ** 2
    return e


def square(freq, dur, duty=0.5, vol=0.25):
    n = int(SR * dur)
    t = np.arange(n) / SR
    ph = (t * freq) % 1.0
    wave_ = np.where(ph < duty, 1.0, -1.0)
    return wave_ * vol * env(n)


def triangle(freq, dur, vol=0.25):
    n = int(SR * dur)
    t = np.arange(n) / SR
    ph = (t * freq) % 1.0
    wave_ = 4 * np.abs(ph - 0.5) - 1
    return wave_ * vol * env(n)


def noise(dur, vol=0.2, decay=0.05):
    n = int(SR * dur)
    rnd = np.random.default_rng(int(dur * 1000) % 9973)
    x = rnd.normal(0, 1, n)
    e = np.exp(-np.linspace(0, 1, n) / max(0.02, decay))
    return x * vol * e


def note(semitones_from_a4):
    return 440.0 * (2 ** (semitones_from_a4 / 12.0))


# ноты относительно A4 (0 = A4)
def seq(*names):
    table = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3,
             "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    flats = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    out = []
    for n in names:
        name, octv = n[:-1], int(n[-1])
        name = flats.get(name, name)
        out.append(table[name] + (octv - 4) * 12)
    return out


def build_track(path, bpm, bars, chords, lead, bass, drums=True, seed=1):
    """Собирает луп: аккорды (треугольник), лид (квадрат), бас (квадрат), шум-барабаны."""
    beat = 60.0 / bpm
    bar = beat * 4
    total = bar * bars
    buf = np.zeros(int(SR * total) + SR)

    def add(sig, at):
        i = int(at * SR)
        buf[i:i + len(sig)] += sig

    for b in range(bars):
        t0 = b * bar
        chord = chords[b % len(chords)]
        # аккорд: арпеджио по 8-м
        for k in range(8):
            nt = chord[k % len(chord)]
            add(triangle(note(nt + 12), beat / 2 * 0.92, vol=0.10), t0 + k * beat / 2)
        # лид
        ln = lead[b % len(lead)]
        if ln is not None:
            add(square(note(ln), bar * 0.9, duty=0.35, vol=0.14), t0)
        # бас
        bn = bass[b % len(bass)]
        add(square(note(bn - 24), beat * 1.8, duty=0.5, vol=0.18), t0)
        add(square(note(bn - 24), beat * 1.6, duty=0.5, vol=0.14), t0 + beat * 2)
        if drums:
            for k in range(4):
                add(noise(0.06, vol=0.10 if k % 2 else 0.16), t0 + k * beat)
            if b % 2 == 1:
                add(noise(0.12, vol=0.08, decay=0.09), t0 + bar - beat * 0.5)

    # мягкое затухание к концу и в начало — луп без щелчка
    fade = int(SR * 0.02)
    buf[:fade] *= np.linspace(0, 1, fade)
    buf[-fade:] *= np.linspace(1, 0, fade)

    peak = np.max(np.abs(buf)) or 1.0
    pcm = (buf / peak * 0.85 * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


TRACKS = {
    "music_2": dict(
        bpm=96, bars=16, seed=2,
        chords=[seq("A2", "C3", "E3"), seq("F2", "A2", "C3"),
                seq("G2", "B2", "D3"), seq("E2", "G2", "B2")],
        lead=[None, None, None, seq("E4")[0], None, None, None, seq("C4")[0]],
        bass=[seq("A1")[0], seq("F1")[0], seq("G1")[0], seq("E1")[0]]),
    "music_3": dict(
        bpm=104, bars=16, seed=3,
        chords=[seq("D2", "F2", "A2"), seq("D2", "F2", "A2"),
                seq("Bb1", "D2", "F2"), seq("C2", "E2", "G2")],
        lead=[None, seq("D4")[0], None, None, seq("F4")[0], None, None, None],
        bass=[seq("D1")[0], seq("D1")[0], seq("Bb0")[0], seq("C1")[0]]),
    "music_4": dict(
        bpm=132, bars=16, seed=4,
        chords=[seq("E2", "G2", "B2"), seq("C2", "E2", "G2"),
                seq("D2", "F2", "A2"), seq("B1", "D2", "F2")],
        lead=[seq("E4")[0], None, seq("G4")[0], None,
              seq("C4")[0], None, seq("D4")[0], None],
        bass=[seq("E1")[0], seq("C1")[0], seq("D1")[0], seq("B0")[0]]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    only = set(filter(None, args.only.split(",")))

    with tempfile.TemporaryDirectory() as tmp:
        for name, cfg in TRACKS.items():
            if only and name not in only:
                continue
            wav = os.path.join(tmp, name + ".wav")
            build_track(wav, cfg["bpm"], cfg["bars"], cfg["chords"], cfg["lead"],
                        cfg["bass"], seed=cfg["seed"])
            out = os.path.join(args.out, name + ".ogg")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                            "-c:a", "libvorbis", "-q:a", "4", out], check=True)
            print("%-8s %6.1f c -> %s (%d КБ)" % (
                name, cfg["bars"] * 4 * 60.0 / cfg["bpm"], out,
                os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()

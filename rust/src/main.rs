#![windows_subsystem = "windows"]
//! Parcoobe — платформер на Rust.
//!
//! Полная переписка игры с GameMaker на Rust (macroquad): меню, 15 уровней,
//! камера, двери, шипы, батуты, грибы-патрульные, скины, настройки.
//! Все текстуры и фон рисуются процедурно в рантайме — внешних ассетов нет.

use macroquad::prelude::*;
use macroquad::audio::{load_sound_from_bytes, play_sound, stop_sound, PlaySoundParams, Sound};
use serde::Deserialize;
use std::collections::HashMap;
use std::fs;

const VIEW_W: f32 = 1280.0;
const VIEW_H: f32 = 720.0;
const TILE: f32 = 32.0;

const WALK: f32 = 4.0;
const GRAV: f32 = 0.3;
const JUMP_V: f32 = -10.0;
const PAD_V: f32 = -17.0;
const PLAYER_W: f32 = 32.0;
const PLAYER_H: f32 = 32.0;

const VERSION: &str = "3.0.0";

// ─────────────────────────────────────────────────────── данные уровней

#[derive(Deserialize, Clone)]
struct RawLevel {
    name: String,
    width: f32,
    height: f32,
    instances: Vec<Vec<serde_json::Value>>,
}

#[derive(Clone)]
struct Enemy {
    pos: Vec2,
    dir: f32,
    vsp: f32,
}

#[derive(Clone, Default)]
struct Level {
    name: String,
    width: f32,
    height: f32,
    walls: Vec<Rect>,
    spikes: Vec<Rect>,
    pads: Vec<Rect>,
    door: Rect,
    spawn: Vec2,
    enemies: Vec<Enemy>,
}

fn rect_from(a: &[serde_json::Value]) -> Rect {
    let x = a[1].as_f64().unwrap_or(0.0) as f32;
    let y = a[2].as_f64().unwrap_or(0.0) as f32;
    let sx = a[3].as_f64().unwrap_or(1.0) as f32;
    let sy = a[4].as_f64().unwrap_or(1.0) as f32;
    match a[0].as_str().unwrap_or("") {
        "oWall" | "oDanger" => Rect::new(x, y, 64.0 * sx, 64.0 * sy),
        "oJumpplatform" => Rect::new(x - 32.0 * sx, y - 16.0 * sy, 64.0 * sx, 32.0 * sy),
        "oDoor" => Rect::new(x, y, 64.0 * sx, 96.0 * sy),
        "oMushroomBleb" => Rect::new(x, y, 64.0 * sx, 64.0 * sy),
        _ => Rect::new(x, y, 64.0 * sx, 64.0 * sy),
    }
}

fn load_level(raw: &RawLevel) -> Level {
    let mut lv = Level {
        name: raw.name.clone(),
        width: raw.width,
        height: raw.height,
        door: Rect::new(raw.width - 96.0, 592.0, 64.0, 96.0),
        spawn: vec2(80.0, 688.0),
        ..Default::default()
    };
    for inst in &raw.instances {
        let kind = inst[0].as_str().unwrap_or("");
        let r = rect_from(inst);
        match kind {
            "oWall" => lv.walls.push(r),
            "oDanger" => lv.spikes.push(r),
            "oJumpplatform" => lv.pads.push(r),
            "oDoor" => lv.door = r,
            "oPlayer" | "oPlayer_1" => {
                lv.spawn = vec2(
                    inst[1].as_f64().unwrap_or(80.0) as f32,
                    inst[2].as_f64().unwrap_or(688.0) as f32,
                )
            }
            "oMushroomBleb" => lv.enemies.push(Enemy {
                pos: vec2(
                    inst[1].as_f64().unwrap_or(0.0) as f32,
                    inst[2].as_f64().unwrap_or(0.0) as f32,
                ),
                dir: 1.0,
                vsp: 0.0,
            }),
            _ => {}
        }
    }
    lv
}

// ─────────────────────────────────────────────────────── игрок

struct Player {
    pos: Vec2,
    vsp: f32,
    on_ground: bool,
    dead: bool,
    skin: usize,
}

impl Player {
    fn new(spawn: Vec2, skin: usize) -> Self {
        Self { pos: spawn, vsp: 0.0, on_ground: false, dead: false, skin }
    }

    fn rect(&self) -> Rect {
        Rect::new(self.pos.x - PLAYER_W / 2.0, self.pos.y - PLAYER_H, PLAYER_W, PLAYER_H)
    }
}

/// Строгое пересечение: касание краями пересечением НЕ считается.
/// (macroquad Rect::overlaps использует <=/>=, из-за чего игрок «прилипал» к полу.)
fn overlaps(a: Rect, b: Rect) -> bool {
    a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y
}

fn hits(rects: &[Rect], r: Rect) -> bool {
    rects.iter().any(|w| overlaps(r, *w))
}

// ─────────────────────────────────────────────────────── текстуры

struct Art {
    brick: Texture2D,
    spikes: Texture2D,
    pad: Texture2D,
    door: Texture2D,
    player: Texture2D,
    enemy: Texture2D,
    background: Texture2D,
}

fn tex_from(img: &Image) -> Texture2D {
    let t = Texture2D::from_image(img);
    t.set_filter(FilterMode::Nearest);
    t
}

struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u32 {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        (self.0 >> 33) as u32
    }
    fn f(&mut self) -> f32 {
        (self.next() % 10_000) as f32 / 10_000.0
    }
    fn range(&mut self, a: i32, b: i32) -> i32 {
        a + (self.next() % ((b - a).max(1) as u32)) as i32
    }
}

fn shade(c: (u8, u8, u8), k: f32) -> Color {
    Color::new(
        (c.0 as f32 * k).clamp(0.0, 255.0) / 255.0,
        (c.1 as f32 * k).clamp(0.0, 255.0) / 255.0,
        (c.2 as f32 * k).clamp(0.0, 255.0) / 255.0,
        1.0,
    )
}

fn make_brick() -> Image {
    let (w, h) = (64u16, 64u16);
    let mut img = Image::gen_image_color(w, h, shade((38, 24, 14), 1.0));
    let mut rng = Rng(7);
    let row_h = 32;
    let brick_w = 32;
    for row in 0..(h as i32 / row_h) {
        let y = row * row_h;
        let offset = if row % 2 == 0 { 0 } else { brick_w / 2 };
        for k in -1..3 {
            let x = k * brick_w + offset;
            let v = 0.88 + rng.f() * 0.24;
            let base = shade((154, 96, 46), v);
            for dx in [-64i32, 0, 64] {
                let x0 = x + dx + 1;
                let x1 = x + dx + brick_w - 2;
                let y0 = y + 1;
                let y1 = y + row_h - 2;
                for py in y0..y1 {
                    for px in x0..x1 {
                        if px >= 0 && px < w as i32 && py >= 0 && py < h as i32 {
                            img.set_pixel(px as u32, py as u32, base);
                        }
                    }
                }
                // блик сверху и тень снизу
                for px in x0..x1 {
                    if px >= 0 && px < w as i32 {
                        img.set_pixel(px as u32, y0 as u32, shade((154, 96, 46), v * 1.2));
                        img.set_pixel(px as u32, (y1 - 1) as u32, shade((154, 96, 46), v * 0.7));
                    }
                }
            }
        }
    }
    img
}

fn make_spikes() -> Image {
    let (w, h) = (64u16, 64u16);
    let mut img = Image::gen_image_color(w, h, Color::new(0.0, 0.0, 0.0, 0.0));
    // основание
    for py in (h as i32 - 14)..h as i32 {
        for px in 0..w as i32 {
            img.set_pixel(px as u32, py as u32, shade((46, 40, 48), 1.0));
        }
    }
    for i in 0..4 {
        let cx = i * 16 + 8;
        let top = 8 + (i % 2) * 3;
        for py in top..(h as i32 - 14) {
            let t = (py - top) as f32 / ((h as i32 - 14 - top) as f32);
            let half = (t * 6.0) as i32 + 1;
            for px in (cx - half)..(cx + half) {
                if px >= 0 && px < w as i32 {
                    let c = if px < cx { shade((232, 238, 250), 1.0) } else { shade((150, 156, 176), 1.0) };
                    img.set_pixel(px as u32, py as u32, c);
                }
            }
        }
    }
    img
}

fn make_pad() -> Image {
    let (w, h) = (64u16, 32u16);
    let mut img = Image::gen_image_color(w, h, Color::new(0.0, 0.0, 0.0, 0.0));
    for py in (h as i32 - 7)..h as i32 {
        for px in 1..w as i32 - 1 {
            img.set_pixel(px as u32, py as u32, shade((30, 36, 28), 1.0));
        }
    }
    // пружина
    for i in 0..7 {
        let x = 6 + i * 8;
        for k in 0..8 {
            let px = x + k / 2;
            let py = h as i32 - 8 - k;
            if px >= 0 && px < w as i32 && py >= 0 && py < h as i32 {
                img.set_pixel(px as u32, py as u32, shade((196, 214, 190), 1.0));
            }
        }
    }
    // площадка
    for py in 4..12 {
        for px in 2..w as i32 - 2 {
            let c = match py {
                4 | 5 => shade((214, 255, 198), 1.0),
                6 | 7 => shade((150, 235, 130), 1.0),
                _ => shade((96, 168, 86), 1.0),
            };
            img.set_pixel(px as u32, py as u32, c);
        }
    }
    img
}

fn make_door() -> Image {
    let (w, h) = (64u16, 96u16);
    let mut img = Image::gen_image_color(w, h, Color::new(0.0, 0.0, 0.0, 0.0));
    for py in 0..h as i32 {
        for px in 0..w as i32 {
            let c = if px < 4 || px >= w as i32 - 4 || py < 4 {
                shade((74, 46, 24), 1.0)
            } else if px < 8 {
                shade((110, 70, 36), 1.0)
            } else {
                shade((96, 58, 28), 1.0)
            };
            img.set_pixel(px as u32, py as u32, c);
        }
    }
    for py in 0..h as i32 {
        for px in [20i32, 34, 48] {
            img.set_pixel(px as u32, py as u32, shade((58, 34, 16), 1.0));
        }
    }
    // ручка
    for py in 44..52 {
        for px in 46..54 {
            img.set_pixel(px as u32, py as u32, shade((214, 170, 74), 1.0));
        }
    }
    img
}

fn make_player() -> Image {
    let (w, h) = (32u16, 32u16);
    let mut img = Image::gen_image_color(w, h, Color::new(0.0, 0.0, 0.0, 0.0));
    for py in 0..h as i32 {
        for px in 0..w as i32 {
            let edge = px < 2 || px >= w as i32 - 2 || py < 2 || py >= h as i32 - 2;
            let c = if edge { shade((214, 168, 62), 1.0) } else { shade((255, 216, 102), 1.0) };
            img.set_pixel(px as u32, py as u32, c);
        }
    }
    // глаза
    for py in 10..16 {
        for px in 7..11 {
            img.set_pixel(px, py, shade((70, 190, 210), 1.0));
        }
        for px in 21..25 {
            img.set_pixel(px, py, shade((70, 190, 210), 1.0));
        }
    }
    // рот
    for px in 12..20 {
        img.set_pixel(px, 22, shade((120, 84, 30), 1.0));
    }
    img
}

fn make_enemy() -> Image {
    let (w, h) = (48u16, 48u16);
    let mut img = Image::gen_image_color(w, h, Color::new(0.0, 0.0, 0.0, 0.0));
    let mut rng = Rng(31);
    for py in 0..h as i32 {
        for px in 0..w as i32 {
            let dx = (px as f32 - 24.0) / 22.0;
            let dy = (py as f32 - 30.0) / 17.0;
            if dx * dx + dy * dy < 1.0 {
                let v = 0.75 + rng.f() * 0.5;
                img.set_pixel(px as u32, py as u32, shade((96, 128, 66), v));
            }
        }
    }
    // глаза
    for py in 20..24 {
        for px in 16..19 {
            img.set_pixel(px, py, shade((240, 240, 230), 1.0));
        }
        for px in 28..31 {
            img.set_pixel(px, py, shade((240, 240, 230), 1.0));
        }
    }
    img
}

fn make_background() -> Image {
    let (w, h) = (VIEW_W as u16, VIEW_H as u16);
    let mut img = Image::gen_image_color(w, h, BLACK);
    let mut rng = Rng(77);
    // небо: градиент к тёмно-красной дымке
    for py in 0..h {
        let t = (py as f32 / (h as f32 * 0.66)).min(1.0);
        let k = t.powf(1.6);
        let r = 7.0 + (96.0 - 7.0) * k;
        let g = 5.0 + (34.0 - 5.0) * k;
        let b = 6.0 + (22.0 - 6.0) * k;
        for px in 0..w {
            img.set_pixel(px as u32, py as u32, Color::new(r / 255.0, g / 255.0, b / 255.0, 1.0));
        }
    }
    // дальние и ближние силуэты
    let mut skyline = |base_y: f32, min_h: i32, max_h: i32, step: i32, col: (u8, u8, u8), rng: &mut Rng| {
        let mut x = -20;
        while x < w as i32 {
            let bw = rng.range(step, step * 3);
            let bh = rng.range(min_h, max_h);
            let top = base_y as i32 - bh;
            for py in top.max(0)..h as i32 {
                for px in x..(x + bw).min(w as i32) {
                    if px >= 0 {
                        img.set_pixel(px as u32, py as u32, shade(col, 1.0));
                    }
                }
            }
            if rng.f() < 0.4 {
                let px0 = x + bw / 2;
                if px0 >= 0 && px0 < w as i32 {
                    for py in (top - 60).max(0)..top {
                        img.set_pixel(px0 as u32, py as u32, shade(col, 1.0));
                        if px0 + 30 < w as i32 {
                            img.set_pixel((px0 + 30) as u32, py as u32, shade(col, 1.0));
                        }
                    }
                    let arm = (top - 60).max(0);
                    for px in (px0 - 30).max(0)..(px0 + 40).min(w as i32) {
                        img.set_pixel(px as u32, arm as u32, shade(col, 1.0));
                    }
                }
            }
            x += bw + rng.range(4, 26);
        }
    };
    skyline(h as f32 * 0.80, 40, 130, 50, (26, 15, 12), &mut rng);
    skyline(h as f32 * 0.82, 90, 240, 70, (14, 8, 7), &mut rng);
    // земля
    for py in (h as f32 * 0.86) as i32..h as i32 {
        for px in 0..w as i32 {
            img.set_pixel(px as u32, py as u32, shade((6, 4, 4), 1.0));
        }
    }
    img
}

// ─────────────────────────────────────────────────────── настройки

#[derive(Clone)]
struct Config {
    skin: usize,
    keys: HashMap<String, KeyCode>,
    sound: bool,
}

impl Default for Config {
    fn default() -> Self {
        let mut keys = HashMap::new();
        keys.insert("left".to_string(), KeyCode::A);
        keys.insert("right".to_string(), KeyCode::D);
        keys.insert("jump".to_string(), KeyCode::Space);
        keys.insert("jump2".to_string(), KeyCode::W);
        Self { skin: 0, keys, sound: true }
    }
}

fn cfg_path() -> std::path::PathBuf {
    std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|d| d.join("parcoobe.cfg")))
        .unwrap_or_else(|| std::path::PathBuf::from("parcoobe.cfg"))
}

fn load_config() -> Config {
    let mut cfg = Config::default();
    if let Ok(text) = fs::read_to_string(cfg_path()) {
        for line in text.lines() {
            let mut it = line.splitn(2, '=');
            let (k, v) = match (it.next(), it.next()) {
                (Some(k), Some(v)) => (k.trim(), v.trim()),
                _ => continue,
            };
            match k {
                "skin" => cfg.skin = v.parse().unwrap_or(0),
                "sound" => cfg.sound = v != "0",
                "left" | "right" | "jump" | "jump2" => {
                    if let Some(code) = key_from_name(v) {
                        cfg.keys.insert(k.to_string(), code);
                    }
                }
                _ => {}
            }
        }
    }
    cfg
}

fn save_config(cfg: &Config) {
    let mut out = String::new();
    out.push_str(&format!("skin={}\n", cfg.skin));
    out.push_str(&format!("sound={}\n", if cfg.sound { 1 } else { 0 }));
    for (k, name) in [("left", "left"), ("right", "right"), ("jump", "jump"), ("jump2", "jump2")] {
        if let Some(code) = cfg.keys.get(k) {
            out.push_str(&format!("{}={}\n", name, key_name(*code)));
        }
    }
    let _ = fs::write(cfg_path(), out);
}

fn key_name(k: KeyCode) -> String {
    format!("{:?}", k)
}

fn key_from_name(s: &str) -> Option<KeyCode> {
    ALL_KEYS.iter().find(|k| key_name(**k) == s).copied()
}

const ALL_KEYS: &[KeyCode] = &[
    KeyCode::A, KeyCode::B, KeyCode::C, KeyCode::D, KeyCode::E, KeyCode::F, KeyCode::G,
    KeyCode::H, KeyCode::I, KeyCode::J, KeyCode::K, KeyCode::L, KeyCode::M, KeyCode::N,
    KeyCode::O, KeyCode::P, KeyCode::Q, KeyCode::R, KeyCode::S, KeyCode::T, KeyCode::U,
    KeyCode::V, KeyCode::W, KeyCode::X, KeyCode::Y, KeyCode::Z,
    KeyCode::Space, KeyCode::Up, KeyCode::Down, KeyCode::Left, KeyCode::Right,
    KeyCode::LeftShift, KeyCode::Enter, KeyCode::Tab, KeyCode::Comma, KeyCode::Period,
];

// ─────────────────────────────────────────────────────── игра

enum Screen {
    Menu,
    Select,
    Settings,
    Play(usize),
    Fin,
}

struct Game {
    font: Option<Font>,
    art: Art,
    levels: Vec<Level>,
    cfg: Config,
    screen: Screen,
    menu_sel: usize,
    select_sel: usize,
    settings_sel: usize,
    waiting_key: Option<String>,
    player: Player,
    level_idx: usize,
    cam_x: f32,
    dead_timer: f32,
    tracks: Vec<Sound>,
    music_idx: usize,
}

const MENU_ITEMS: [&str; 4] = ["NEW GAME", "LEVEL SELECT", "SETTINGS", "QUIT"];
const SETTINGS_ROWS: [&str; 6] = ["LEFT", "RIGHT", "JUMP", "JUMP TWO", "SKIN", "BACK"];

impl Game {
    fn start_level(&mut self, idx: usize) {
        self.level_idx = idx.min(self.levels.len() - 1);
        let lv = &self.levels[self.level_idx];
        self.player = Player::new(lv.spawn, self.cfg.skin);
        self.cam_x = 0.0;
        self.dead_timer = 0.0;
        self.screen = Screen::Play(self.level_idx);
        self.restart_enemies(self.level_idx);
        self.play_music_for(self.level_idx);
    }

    fn restart_enemies(&mut self, idx: usize) {
        if let Some(raw_spawn) = self.levels.get(idx) {
            let enemies = raw_spawn.enemies.clone();
            self.levels[idx].enemies = enemies;
        }
    }

    fn play_music_for(&mut self, idx: usize) {
        let track = if idx >= 10 { 3 } else if idx >= 6 { 2 } else if idx >= 3 { 1 } else { 0 };
        if self.music_idx == track || self.tracks.is_empty() {
            return;
        }
        if let Some(s) = self.tracks.get(self.music_idx) {
            stop_sound(s);
        }
        self.music_idx = track;
        if let Some(s) = self.tracks.get(track) {
            play_sound(s, PlaySoundParams { looped: true, volume: 0.35 });
        }
    }
}

fn window_conf() -> Conf {
    Conf {
        window_title: "Parcoobe".to_owned(),
        window_width: VIEW_W as i32,
        window_height: VIEW_H as i32,
        window_resizable: false,
        high_dpi: true,
        sample_count: 0,
        ..Default::default()
    }
}

fn skin_colors() -> [Color; 5] {
    [
        WHITE,
        Color::new(1.0, 0.47, 0.47, 1.0),
        Color::new(0.55, 0.92, 0.55, 1.0),
        Color::new(0.51, 0.70, 1.0, 1.0),
        Color::new(0.86, 0.59, 1.0, 1.0),
    ]
}

#[macroquad::main(window_conf)]
async fn main() {
    let raw: Vec<RawLevel> = {
        let text = include_str!("../assets/levels.json");
        serde_json::from_str(text).expect("levels.json")
    };
    let levels: Vec<Level> = raw.iter().map(load_level).collect();

    let art = Art {
        brick: tex_from(&make_brick()),
        spikes: tex_from(&make_spikes()),
        pad: tex_from(&make_pad()),
        door: tex_from(&make_door()),
        player: tex_from(&make_player()),
        enemy: tex_from(&make_enemy()),
        background: tex_from(&make_background()),
    };

    let cfg = load_config();
    let mut tracks: Vec<Sound> = Vec::new();
    for bytes in [
        &include_bytes!("../assets/music_1.ogg")[..],
        &include_bytes!("../assets/music_2.ogg")[..],
        &include_bytes!("../assets/music_3.ogg")[..],
        &include_bytes!("../assets/music_4.ogg")[..],
    ] {
        if let Ok(s) = load_sound_from_bytes(bytes).await {
            tracks.push(s);
        }
    }
    if let Some(s) = tracks.first() {
        play_sound(s, PlaySoundParams { looped: true, volume: 0.35 });
    }

    let font = load_ttf_font_from_bytes(include_bytes!("../assets/ui.ttf"))
        .ok();

    let mut game = Game {
        font,
        art,
        levels,
        cfg: cfg.clone(),
        screen: Screen::Menu,
        menu_sel: 0,
        select_sel: 0,
        settings_sel: 0,
        waiting_key: None,
        player: Player::new(vec2(80.0, 688.0), cfg.skin),
        level_idx: 0,
        cam_x: 0.0,
        dead_timer: 0.0,
        tracks,
        music_idx: 0,
    };

    loop {
        let dt = get_frame_time().min(1.0 / 30.0);
        update(&mut game, dt);
        draw(&mut game);
        next_frame().await;
    }
}

fn update(g: &mut Game, dt: f32) {
    match g.screen {
        Screen::Menu => {
            if is_key_pressed(KeyCode::Down) {
                g.menu_sel = (g.menu_sel + 1) % MENU_ITEMS.len();
            }
            if is_key_pressed(KeyCode::Up) {
                g.menu_sel = (g.menu_sel + MENU_ITEMS.len() - 1) % MENU_ITEMS.len();
            }
            if is_key_pressed(KeyCode::Enter) || is_key_pressed(KeyCode::Space) {
                match g.menu_sel {
                    0 => g.start_level(0),
                    1 => g.screen = Screen::Select,
                    2 => g.screen = Screen::Settings,
                    _ => std::process::exit(0),
                }
            }
        }
        Screen::Select => {
            if is_key_pressed(KeyCode::Down) {
                g.select_sel = (g.select_sel + 1) % g.levels.len();
            }
            if is_key_pressed(KeyCode::Up) {
                g.select_sel = (g.select_sel + g.levels.len() - 1) % g.levels.len();
            }
            if is_key_pressed(KeyCode::Enter) {
                let idx = g.select_sel;
                g.start_level(idx);
            }
            if is_key_pressed(KeyCode::Escape) {
                g.screen = Screen::Menu;
            }
        }
        Screen::Settings => {
            update_settings(g);
        }
        Screen::Play(idx) => {
            update_play(g, idx, dt);
        }
        Screen::Fin => {
            if is_key_pressed(KeyCode::Enter) || is_key_pressed(KeyCode::Escape) {
                g.screen = Screen::Menu;
            }
        }
    }
}

fn update_settings(g: &mut Game) {
    if g.waiting_key.is_some() {
        for k in ALL_KEYS {
            if is_key_pressed(*k) {
                let slot = g.waiting_key.clone().unwrap();
                g.cfg.keys.insert(slot, *k);
                save_config(&g.cfg);
                g.waiting_key = None;
                break;
            }
        }
        if is_key_pressed(KeyCode::Escape) {
            g.waiting_key = None;
        }
        return;
    }
    if is_key_pressed(KeyCode::Down) {
        g.settings_sel = (g.settings_sel + 1) % SETTINGS_ROWS.len();
    }
    if is_key_pressed(KeyCode::Up) {
        g.settings_sel = (g.settings_sel + SETTINGS_ROWS.len() - 1) % SETTINGS_ROWS.len();
    }
    if is_key_pressed(KeyCode::Escape) {
        g.screen = Screen::Menu;
        return;
    }
    if is_key_pressed(KeyCode::Enter) {
        match g.settings_sel {
            0 => g.waiting_key = Some("left".to_string()),
            1 => g.waiting_key = Some("right".to_string()),
            2 => g.waiting_key = Some("jump".to_string()),
            3 => g.waiting_key = Some("jump2".to_string()),
            4 => {
                g.cfg.skin = (g.cfg.skin + 1) % 5;
                g.player.skin = g.cfg.skin;
                save_config(&g.cfg);
            }
            _ => g.screen = Screen::Menu,
        }
    }
}

fn update_play(g: &mut Game, idx: usize, dt: f32) {
    if is_key_pressed(KeyCode::Escape) {
        g.screen = Screen::Menu;
        return;
    }
    if is_key_pressed(KeyCode::F1) {
        g.settings_sel = 0;
        g.screen = Screen::Settings;
        return;
    }
    if is_key_pressed(KeyCode::K) {
        g.cfg.skin = (g.cfg.skin + 1) % 5;
        g.player.skin = g.cfg.skin;
        save_config(&g.cfg);
    }

    if g.player.dead {
        g.dead_timer -= dt;
        if g.dead_timer <= 0.0 {
            g.start_level(idx);
        }
        return;
    }

    let lv = g.levels[idx].clone();
    let left = *g.cfg.keys.get("left").unwrap_or(&KeyCode::A);
    let right = *g.cfg.keys.get("right").unwrap_or(&KeyCode::D);
    let jump = *g.cfg.keys.get("jump").unwrap_or(&KeyCode::Space);
    let jump2 = *g.cfg.keys.get("jump2").unwrap_or(&KeyCode::W);

    let dir = (is_key_down(right) as i32 - is_key_down(left) as i32) as f32;
    let want_jump = is_key_pressed(jump) || is_key_pressed(jump2);

    let mut steps = (dt * 60.0).round().max(1.0) as i32;
    if steps > 4 {
        steps = 4;
    }
    for _ in 0..steps {
        let mut p = &mut g.player;
        let mut hsp = dir * WALK;
        p.vsp += GRAV;
        if p.on_ground && want_jump {
            p.vsp = JUMP_V;
        }

        let feet = |x: f32, y: f32| Rect::new(x - PLAYER_W / 2.0, y - PLAYER_H, PLAYER_W, PLAYER_H);

        if hits(&lv.walls, feet(p.pos.x + hsp, p.pos.y)) {
            let s = hsp.signum();
            while !hits(&lv.walls, feet(p.pos.x + s, p.pos.y)) {
                p.pos.x += s;
            }
            hsp = 0.0;
        }
        p.pos.x += hsp;

        if hits(&lv.walls, feet(p.pos.x, p.pos.y + p.vsp)) {
            let s = p.vsp.signum();
            while !hits(&lv.walls, feet(p.pos.x, p.pos.y + s)) && s != 0.0 {
                p.pos.y += s;
            }
            p.vsp = 0.0;
            p.on_ground = true;
        } else {
            p.on_ground = false;
        }
        p.pos.y += p.vsp;

        // батут
        for pad in &lv.pads {
            if overlaps(feet(p.pos.x, p.pos.y), *pad) && p.vsp >= 0.0 {
                p.vsp = PAD_V;
            }
        }
        // смерть и границы
        if hits(&lv.spikes, feet(p.pos.x, p.pos.y)) || p.pos.y > lv.height + 64.0 {
            p.dead = true;
            g.dead_timer = 0.8;
        }
        // дверь
        if overlaps(feet(p.pos.x, p.pos.y), lv.door) {
            let next = idx + 1;
            if next < g.levels.len() {
                g.start_level(next);
            } else {
                g.screen = Screen::Fin;
            }
            return;
        }
    }

    // грибы: патруль
    for e in g.levels[idx].enemies.iter_mut() {
        let r = Rect::new(e.pos.x, e.pos.y, 48.0, 48.0);
        let step = e.dir * 1.2;
        let ahead = Rect::new(e.pos.x + step, e.pos.y, 48.0, 48.0);
        let blocked = hits(&lv.walls, ahead) || hits(&lv.spikes, ahead);
        let ground_now = hits(&lv.walls, Rect::new(e.pos.x, e.pos.y + 49.0, 48.0, 8.0));
        let ground_next = hits(&lv.walls, Rect::new(e.pos.x + step, e.pos.y + 49.0, 48.0, 8.0));
        if blocked || (ground_now && !ground_next) {
            e.dir = -e.dir;
        } else {
            e.pos.x += step;
        }
        e.vsp += GRAV;
        if hits(&lv.walls, Rect::new(e.pos.x, e.pos.y + e.vsp, 48.0, 48.0)) {
            e.vsp = 0.0;
            let mut y = e.pos.y;
            while !hits(&lv.walls, Rect::new(e.pos.x, y + 1.0, 48.0, 48.0)) && y < lv.height {
                y += 1.0;
            }
            e.pos.y = y;
        } else {
            e.pos.y += e.vsp;
        }
        // столкновение с игроком
        if overlaps(r, g.player.rect()) && !g.player.dead {
            g.player.dead = true;
            g.dead_timer = 0.8;
        }
    }

    // камера
    let max_x = (lv.width - VIEW_W).max(0.0);
    g.cam_x = (g.player.pos.x - VIEW_W / 2.0).clamp(0.0, max_x);
}

fn text(g: &Game, txt: &str, x: f32, y: f32, size: f32, color: Color) {
    if let Some(font) = &g.font {
        let p = TextParams { font: Some(font), font_size: size as u16, color, ..Default::default() };
        draw_text_ex(txt, x, y, p);
    } else {
        draw_text(txt, x, y, size, color);
    }
}

fn draw(g: &mut Game) {
    clear_background(BLACK);
    draw_texture_ex(
        &g.art.background,
        0.0,
        0.0,
        WHITE,
        DrawTextureParams { dest_size: Some(vec2(VIEW_W, VIEW_H)), ..Default::default() },
    );

    match &g.screen {
        Screen::Menu => draw_menu(g),
        Screen::Select => draw_select(g),
        Screen::Settings => {
            if let Screen::Play(idx) = g.screen {
                draw_world(g, idx);
            } else {
                draw_menu(g);
            }
            draw_settings(g);
        }
        Screen::Play(idx) => draw_world(g, *idx),
        Screen::Fin => draw_fin(g),
    }
}

fn draw_menu(g: &Game) {
    draw_rectangle(140.0, 60.0, 1000.0, 300.0, Color::new(0.05, 0.05, 0.06, 0.92));
    text(g, "PARCOOBE", 300.0, 200.0, 130.0, Color::new(1.0, 0.85, 0.62, 1.0));
    text(g, &format!("Version {}", VERSION), 560.0, 260.0, 30.0, Color::new(0.59, 0.92, 0.51, 1.0));

    for (i, item) in MENU_ITEMS.iter().enumerate() {
        let y = 420.0 + i as f32 * 60.0;
        let sel = i == g.menu_sel;
        let col = if sel { Color::new(1.0, 0.36, 0.36, 1.0) } else { Color::new(0.85, 0.85, 0.85, 1.0) };
        if sel {
            draw_rectangle(360.0, y - 34.0, 560.0, 46.0, Color::new(0.14, 0.05, 0.05, 0.9));
        }
        text(g, item, 400.0, y, 40.0, col);
    }
    text(g, "ARROWS SELECT   ENTER OK", 400.0, 690.0, 22.0, Color::new(0.6, 0.6, 0.6, 1.0));
}

fn draw_select(g: &Game) {
    draw_rectangle(240.0, 40.0, 800.0, 640.0, Color::new(0.05, 0.05, 0.06, 0.94));
    text(g, "LEVEL SELECT", 380.0, 100.0, 46.0, Color::new(1.0, 0.85, 0.62, 1.0));
    let start = g.select_sel.saturating_sub(6);
    for (n, i) in (start..g.levels.len()).take(12).enumerate() {
        let y = 170.0 + n as f32 * 38.0;
        let sel = i == g.select_sel;
        let col = if sel { Color::new(1.0, 0.36, 0.36, 1.0) } else { WHITE };
        if sel {
            draw_rectangle(300.0, y - 26.0, 680.0, 32.0, Color::new(0.14, 0.05, 0.05, 0.9));
        }
        text(g, &format!("{:02}  {}", i + 1, g.levels[i].name), 320.0, y, 26.0, col);
    }
    text(g, "ESC BACK", 320.0, 660.0, 22.0, Color::new(0.6, 0.6, 0.6, 1.0));
}

fn draw_world(g: &Game, idx: usize) {
    let lv = &g.levels[idx];
    let cam = Camera2D {
        target: vec2(g.cam_x + VIEW_W / 2.0, VIEW_H / 2.0),
        zoom: vec2(2.0 / VIEW_W, 2.0 / VIEW_H),
        ..Default::default()
    };
    set_camera(&cam);

    for w in &lv.walls {
        draw_texture_ex(
            &g.art.brick,
            w.x,
            w.y,
            WHITE,
            DrawTextureParams { dest_size: Some(vec2(w.w, w.h)), ..Default::default() },
        );
    }
    for s in &lv.spikes {
        draw_texture_ex(
            &g.art.spikes,
            s.x,
            s.y,
            WHITE,
            DrawTextureParams { dest_size: Some(vec2(s.w, s.h)), ..Default::default() },
        );
    }
    for p in &lv.pads {
        draw_texture_ex(
            &g.art.pad,
            p.x,
            p.y,
            WHITE,
            DrawTextureParams { dest_size: Some(vec2(p.w, p.h)), ..Default::default() },
        );
    }
    draw_texture_ex(
        &g.art.door,
        lv.door.x,
        lv.door.y,
        WHITE,
        DrawTextureParams { dest_size: Some(vec2(lv.door.w, lv.door.h)), ..Default::default() },
    );
    for e in &lv.enemies {
        draw_texture_ex(
            &g.art.enemy,
            e.pos.x,
            e.pos.y,
            WHITE,
            DrawTextureParams {
                dest_size: Some(vec2(48.0, 48.0)),
                flip_x: e.dir < 0.0,
                ..Default::default()
            },
        );
    }
    let tint = skin_colors()[g.player.skin.min(4)];
    draw_texture_ex(
        &g.art.player,
        g.player.pos.x - PLAYER_W / 2.0,
        g.player.pos.y - PLAYER_H,
        tint,
        DrawTextureParams { dest_size: Some(vec2(PLAYER_W, PLAYER_H)), ..Default::default() },
    );

    set_default_camera();
    draw_hud(g, idx);
}

fn draw_hud(g: &Game, idx: usize) {
    draw_rectangle(16.0, 16.0, 200.0, 48.0, Color::new(0.67, 0.11, 0.15, 1.0));
    text(g, "SETTINGS", 34.0, 50.0, 26.0, WHITE);
    text(g, "F1 SETTINGS    K SKIN", 20.0, 706.0, 18.0, Color::new(0.75, 0.75, 0.75, 1.0));
    text(g, &format!("{}   {}/{}", g.levels[idx].name, idx + 1, g.levels.len()), 1000.0, 40.0, 20.0,
              Color::new(0.8, 0.8, 0.8, 1.0));
}

fn draw_settings(g: &Game) {
    draw_rectangle(140.0, 70.0, 1000.0, 560.0, Color::new(0.03, 0.03, 0.04, 0.96));
    draw_rectangle_lines(140.0, 70.0, 1000.0, 560.0, 2.0, Color::new(0.8, 0.7, 0.4, 1.0));
    text(g, "CONTROLS", 180.0, 130.0, 44.0, Color::new(0.9, 0.72, 0.35, 1.0));
    if let Some(slot) = &g.waiting_key {
        text(g, &format!("PRESS A KEY FOR {}  (ESC CANCEL)", slot.to_uppercase()), 180.0, 180.0, 24.0, WHITE);
    } else {
        text(g, "ARROWS SELECT   ENTER CHANGE   ESC BACK", 180.0, 180.0, 22.0,
                  Color::new(0.65, 0.65, 0.65, 1.0));
    }
    for (i, row) in SETTINGS_ROWS.iter().enumerate() {
        let y = 250.0 + i as f32 * 52.0;
        let sel = i == g.settings_sel;
        if sel {
            draw_rectangle(170.0, y - 32.0, 940.0, 44.0, Color::new(0.16, 0.16, 0.18, 1.0));
        }
        let col = if sel { Color::new(0.95, 0.78, 0.3, 1.0) } else { WHITE };
        text(g, row, 190.0, y, 28.0, col);
        let value = match i {
            0 => key_name(*g.cfg.keys.get("left").unwrap_or(&KeyCode::A)),
            1 => key_name(*g.cfg.keys.get("right").unwrap_or(&KeyCode::D)),
            2 => key_name(*g.cfg.keys.get("jump").unwrap_or(&KeyCode::Space)),
            3 => key_name(*g.cfg.keys.get("jump2").unwrap_or(&KeyCode::W)),
            4 => format!("COLOR {}", g.cfg.skin + 1),
            _ => String::new(),
        };
        text(g, &value, 600.0, y, 28.0, col);
    }
}

fn draw_fin(g: &Game) {
    let _ = g;
    text(g, "СПАСИБО ЗА ПРОХОЖДЕНИЕ", 260.0, 300.0, 46.0, Color::new(1.0, 0.85, 0.30, 1.0));
    text(g, "PARCOOBE", 500.0, 400.0, 40.0, Color::new(0.59, 0.92, 0.51, 1.0));
    text(g, &format!("VERSION {}", VERSION), 520.0, 470.0, 30.0, WHITE);
    text(g, "ENTER — В МЕНЮ", 520.0, 560.0, 24.0, Color::new(0.7, 0.7, 0.7, 1.0));
}

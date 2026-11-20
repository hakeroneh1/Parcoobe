#![cfg_attr(target_os = "windows", windows_subsystem = "windows")]

//! Parcoobe 3D — 3D-версия платформера Parcoobe.
//!
//! Два режима камеры (F5): классический вид сбоку и вид от первого лица.
//! Управление переназначается (F1) и сохраняется рядом с exe в `parcoobe3d.cfg`.
//! Все ресурсы вкомпилированы в бинарник — на выходе один exe.

use macroquad::prelude::*;
use serde::{Deserialize, Serialize};

// ─────────────────────────── данные уровней ───────────────────────────

#[derive(Deserialize, Clone)]
struct LevelData {
    name: String,
    width: f32,
    height: f32,
    bg: u32,
    start: [f32; 2],
    walls: Vec<[f32; 4]>,
    hazards: Vec<[f32; 4]>,
    jumps: Vec<[f32; 4]>,
    doors: Vec<[f32; 4]>,
    closes: Vec<[f32; 4]>,
    enemies: Vec<[f32; 4]>,
}

#[derive(Deserialize)]
struct LevelsFile {
    levels: Vec<LevelData>,
}

fn load_levels() -> Vec<LevelData> {
    let data = include_str!("../assets/levels.json");
    let file: LevelsFile = serde_json::from_str(data).expect("levels.json");
    file.levels
}

// ─────────────────────────── текстуры ───────────────────────────

struct Art {
    wall: Texture2D,
    wall_bg: Texture2D,
    hazard: Texture2D,
    player_front: Texture2D,
    player_right: Texture2D,
    player_left: Texture2D,
    enemy: Texture2D,
    door: Texture2D,
    closed: Texture2D,
    jump: Texture2D,
}

fn tex(bytes: &[u8]) -> Texture2D {
    let t = Texture2D::from_file_with_format(bytes, Some(ImageFormat::Png));
    t.set_filter(FilterMode::Nearest);
    t
}

impl Art {
    fn load() -> Art {
        Art {
            wall: tex(include_bytes!("../assets/sWall_0.png")),
            wall_bg: tex(include_bytes!("../assets/sWall_background_0.png")),
            hazard: tex(include_bytes!("../assets/sDanger_brick_0.png")),
            player_front: tex(include_bytes!("../assets/sPlayerfront_0.png")),
            player_right: tex(include_bytes!("../assets/sPlayerright_0.png")),
            player_left: tex(include_bytes!("../assets/sPlayerleft_0.png")),
            enemy: tex(include_bytes!("../assets/sMushroomZomb_0.png")),
            door: tex(include_bytes!("../assets/sDoor_0.png")),
            closed: tex(include_bytes!("../assets/sClosedoor_0.png")),
            jump: tex(include_bytes!("../assets/sJumpplatform_0.png")),
        }
    }
}

// ─────────────────────────── управление ───────────────────────────

const SLOT_TITLES: [&str; 6] = ["LEFT", "RIGHT", "FORWARD", "BACK", "JUMP", "CAMERA"];

const ALL_KEYS: &[KeyCode] = &[
    KeyCode::A, KeyCode::B, KeyCode::C, KeyCode::D, KeyCode::E, KeyCode::F, KeyCode::G,
    KeyCode::H, KeyCode::I, KeyCode::J, KeyCode::K, KeyCode::L, KeyCode::M, KeyCode::N,
    KeyCode::O, KeyCode::P, KeyCode::Q, KeyCode::R, KeyCode::S, KeyCode::T, KeyCode::U,
    KeyCode::V, KeyCode::W, KeyCode::X, KeyCode::Y, KeyCode::Z,
    KeyCode::Key0, KeyCode::Key1, KeyCode::Key2, KeyCode::Key3, KeyCode::Key4,
    KeyCode::Key5, KeyCode::Key6, KeyCode::Key7, KeyCode::Key8, KeyCode::Key9,
    KeyCode::Left, KeyCode::Right, KeyCode::Up, KeyCode::Down,
    KeyCode::Space, KeyCode::Enter, KeyCode::Tab,
    KeyCode::LeftShift, KeyCode::RightShift, KeyCode::LeftControl, KeyCode::RightControl,
    KeyCode::LeftAlt, KeyCode::RightAlt,
    KeyCode::Comma, KeyCode::Period, KeyCode::Minus, KeyCode::Equal, KeyCode::Semicolon,
    KeyCode::Apostrophe, KeyCode::Slash, KeyCode::Backslash, KeyCode::GraveAccent,
    KeyCode::LeftBracket, KeyCode::RightBracket,
    KeyCode::Backspace, KeyCode::Delete, KeyCode::Insert,
    KeyCode::Home, KeyCode::End, KeyCode::PageUp, KeyCode::PageDown,
    KeyCode::Kp0, KeyCode::Kp1, KeyCode::Kp2, KeyCode::Kp3, KeyCode::Kp4,
    KeyCode::Kp5, KeyCode::Kp6, KeyCode::Kp7, KeyCode::Kp8, KeyCode::Kp9,
    KeyCode::F1, KeyCode::F2, KeyCode::F3, KeyCode::F4, KeyCode::F5, KeyCode::F6,
    KeyCode::F7, KeyCode::F8, KeyCode::F9, KeyCode::F10, KeyCode::F11, KeyCode::F12,
];

fn key_from_name(name: &str) -> KeyCode {
    match name {
        "Space" => KeyCode::Space,
        "Enter" => KeyCode::Enter,
        "Escape" => KeyCode::Escape,
        "Tab" => KeyCode::Tab,
        "Left" => KeyCode::Left,
        "Right" => KeyCode::Right,
        "Up" => KeyCode::Up,
        "Down" => KeyCode::Down,
        "LeftShift" => KeyCode::LeftShift,
        "RightShift" => KeyCode::RightShift,
        "LeftControl" => KeyCode::LeftControl,
        "RightControl" => KeyCode::RightControl,
        "LeftAlt" => KeyCode::LeftAlt,
        "RightAlt" => KeyCode::RightAlt,
        "Comma" => KeyCode::Comma,
        "Period" => KeyCode::Period,
        "Minus" => KeyCode::Minus,
        "Equal" => KeyCode::Equal,
        "Semicolon" => KeyCode::Semicolon,
        "Apostrophe" => KeyCode::Apostrophe,
        "Slash" => KeyCode::Slash,
        "Backslash" => KeyCode::Backslash,
        "GraveAccent" => KeyCode::GraveAccent,
        "LeftBracket" => KeyCode::LeftBracket,
        "RightBracket" => KeyCode::RightBracket,
        "Backspace" => KeyCode::Backspace,
        "Delete" => KeyCode::Delete,
        "Insert" => KeyCode::Insert,
        "Home" => KeyCode::Home,
        "End" => KeyCode::End,
        "PageUp" => KeyCode::PageUp,
        "PageDown" => KeyCode::PageDown,
        other => ALL_KEYS
            .iter()
            .copied()
            .find(|k| key_to_name(*k).as_deref() == Some(other))
            .unwrap_or(KeyCode::Space),
    }
}

fn key_to_name(key: KeyCode) -> Option<&'static str> {
    let name = match key {
        KeyCode::Space => "Space",
        KeyCode::Enter => "Enter",
        KeyCode::Escape => "Escape",
        KeyCode::Tab => "Tab",
        KeyCode::Left => "Left",
        KeyCode::Right => "Right",
        KeyCode::Up => "Up",
        KeyCode::Down => "Down",
        KeyCode::LeftShift => "LeftShift",
        KeyCode::RightShift => "RightShift",
        KeyCode::LeftControl => "LeftControl",
        KeyCode::RightControl => "RightControl",
        KeyCode::LeftAlt => "LeftAlt",
        KeyCode::RightAlt => "RightAlt",
        KeyCode::Comma => "Comma",
        KeyCode::Period => "Period",
        KeyCode::Minus => "Minus",
        KeyCode::Equal => "Equal",
        KeyCode::Semicolon => "Semicolon",
        KeyCode::Apostrophe => "Apostrophe",
        KeyCode::Slash => "Slash",
        KeyCode::Backslash => "Backslash",
        KeyCode::GraveAccent => "GraveAccent",
        KeyCode::LeftBracket => "LeftBracket",
        KeyCode::RightBracket => "RightBracket",
        KeyCode::Backspace => "Backspace",
        KeyCode::Delete => "Delete",
        KeyCode::Insert => "Insert",
        KeyCode::Home => "Home",
        KeyCode::End => "End",
        KeyCode::PageUp => "PageUp",
        KeyCode::PageDown => "PageDown",
        KeyCode::A => "A", KeyCode::B => "B", KeyCode::C => "C", KeyCode::D => "D",
        KeyCode::E => "E", KeyCode::F => "F", KeyCode::G => "G", KeyCode::H => "H",
        KeyCode::I => "I", KeyCode::J => "J", KeyCode::K => "K", KeyCode::L => "L",
        KeyCode::M => "M", KeyCode::N => "N", KeyCode::O => "O", KeyCode::P => "P",
        KeyCode::Q => "Q", KeyCode::R => "R", KeyCode::S => "S", KeyCode::T => "T",
        KeyCode::U => "U", KeyCode::V => "V", KeyCode::W => "W", KeyCode::X => "X",
        KeyCode::Y => "Y", KeyCode::Z => "Z",
        KeyCode::Key0 => "0", KeyCode::Key1 => "1", KeyCode::Key2 => "2",
        KeyCode::Key3 => "3", KeyCode::Key4 => "4", KeyCode::Key5 => "5",
        KeyCode::Key6 => "6", KeyCode::Key7 => "7", KeyCode::Key8 => "8",
        KeyCode::Key9 => "9",
        KeyCode::Kp0 => "Kp0", KeyCode::Kp1 => "Kp1", KeyCode::Kp2 => "Kp2",
        KeyCode::Kp3 => "Kp3", KeyCode::Kp4 => "Kp4", KeyCode::Kp5 => "Kp5",
        KeyCode::Kp6 => "Kp6", KeyCode::Kp7 => "Kp7", KeyCode::Kp8 => "Kp8",
        KeyCode::Kp9 => "Kp9",
        KeyCode::F1 => "F1", KeyCode::F2 => "F2", KeyCode::F3 => "F3",
        KeyCode::F4 => "F4", KeyCode::F5 => "F5", KeyCode::F6 => "F6",
        KeyCode::F7 => "F7", KeyCode::F8 => "F8", KeyCode::F9 => "F9",
        KeyCode::F10 => "F10", KeyCode::F11 => "F11", KeyCode::F12 => "F12",
        _ => return None,
    };
    Some(name)
}

#[derive(Serialize, Deserialize, Clone)]
struct Controls {
    left: String,
    right: String,
    forward: String,
    back: String,
    jump: String,
    camera: String,
}

impl Default for Controls {
    fn default() -> Self {
        Controls {
            left: "A".into(),
            right: "D".into(),
            forward: "W".into(),
            back: "S".into(),
            jump: "Space".into(),
            camera: "F5".into(),
        }
    }
}

impl Controls {
    fn load() -> Controls {
        std::fs::read_to_string(cfg_path())
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_default()
    }
    fn save(&self) {
        if let Ok(s) = serde_json::to_string_pretty(self) {
            let _ = std::fs::write(cfg_path(), s);
        }
    }
    fn name(&self, slot: usize) -> &str {
        match slot {
            0 => &self.left,
            1 => &self.right,
            2 => &self.forward,
            3 => &self.back,
            4 => &self.jump,
            _ => &self.camera,
        }
    }
    fn set(&mut self, slot: usize, name: String) {
        match slot {
            0 => self.left = name,
            1 => self.right = name,
            2 => self.forward = name,
            3 => self.back = name,
            4 => self.jump = name,
            _ => self.camera = name,
        }
    }
    fn key(&self, slot: usize) -> KeyCode {
        key_from_name(self.name(slot))
    }
}

fn cfg_path() -> std::path::PathBuf {
    std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        .unwrap_or_else(|| std::path::PathBuf::from("."))
        .join("parcoobe3d.cfg")
}

// ─────────────────────────── физика ───────────────────────────

const GRAVITY: f32 = 1080.0;
const WALK: f32 = 240.0;
const JUMP_V: f32 = -600.0;
const BOUNCE_V: f32 = -1020.0;
const PLAYER_W: f32 = 30.0;
const PLAYER_H: f32 = 54.0;

struct Player {
    x: f32,
    y: f32,
    vx: f32,
    vy: f32,
    on_ground: bool,
    facing: f32,
    dead_time: f32,
}

impl Player {
    fn spawn(l: &LevelData) -> Player {
        Player {
            x: l.start[0],
            y: l.start[1],
            vx: 0.0,
            vy: 0.0,
            on_ground: false,
            facing: 1.0,
            dead_time: 0.0,
        }
    }
    fn rect(&self) -> [f32; 4] {
        [self.x - PLAYER_W * 0.5, self.y - PLAYER_H, PLAYER_W, PLAYER_H]
    }
}

fn overlaps(a: [f32; 4], b: [f32; 4]) -> bool {
    a[0] < b[0] + b[2] && a[0] + a[2] > b[0] && a[1] < b[1] + b[3] && a[1] + a[3] > b[1]
}

fn any_overlap(rect: [f32; 4], list: &[[f32; 4]]) -> bool {
    list.iter().any(|r| overlaps(rect, *r))
}

fn step_player(p: &mut Player, level: &LevelData, left: bool, right: bool, jump: bool, dt: f32) {
    if p.dead_time > 0.0 {
        p.dead_time -= dt;
        if p.dead_time <= 0.0 {
            p.x = level.start[0];
            p.y = level.start[1];
            p.vx = 0.0;
            p.vy = 0.0;
        }
        return;
    }
    let mut move_x = 0.0;
    if left {
        move_x -= 1.0;
    }
    if right {
        move_x += 1.0;
    }
    if move_x != 0.0 {
        p.facing = move_x;
    }
    p.vx = move_x * WALK;
    p.vy = (p.vy + GRAVITY * dt).min(1600.0);

    let dx = p.vx * dt;
    if dx != 0.0 {
        let mut probe = p.rect();
        probe[0] += dx;
        if any_overlap(probe, &level.walls) {
            let step = if dx > 0.0 { 1.0 } else { -1.0 };
            loop {
                let mut t = p.rect();
                t[0] += step;
                if any_overlap(t, &level.walls) {
                    break;
                }
                p.x += step;
            }
        } else {
            p.x += dx;
        }
    }

    let dy = p.vy * dt;
    if dy != 0.0 {
        let mut probe = p.rect();
        probe[1] += dy;
        if any_overlap(probe, &level.walls) {
            let step = if dy > 0.0 { 1.0 } else { -1.0 };
            loop {
                let mut t = p.rect();
                t[1] += step;
                if any_overlap(t, &level.walls) {
                    break;
                }
                p.y += step;
            }
            if dy > 0.0 {
                p.on_ground = true;
            }
            p.vy = 0.0;
        } else {
            p.y += dy;
        }
    }

    if jump && p.on_ground {
        p.vy = JUMP_V;
    }

    let feet = [p.x - PLAYER_W * 0.5, p.y - 4.0, PLAYER_W, 8.0];
    if any_overlap(feet, &level.jumps) {
        p.vy = BOUNCE_V;
    }

    if any_overlap(p.rect(), &level.hazards) {
        p.dead_time = 0.5;
        p.vx = 0.0;
        p.vy = 0.0;
    }
}

// ─────────────────────────── 3D-геометрия ───────────────────────────

const CORRIDOR: f32 = 96.0;
const TILE: f32 = 64.0;

fn push_quad(v: &mut Vec<Vertex>, i: &mut Vec<u16>, p: [Vec3; 4], uv: [Vec2; 4], c: Color) {
    let base = v.len() as u16;
    for k in 0..4 {
        v.push(Vertex::new2(p[k], uv[k], c));
    }
    i.extend_from_slice(&[base, base + 1, base + 2, base, base + 2, base + 3]);
}

fn box_mesh(rects: &[[f32; 4]], texture: Texture2D) -> Mesh {
    let mut v = Vec::new();
    let mut i = Vec::new();
    let (z0, z1) = (-CORRIDOR, CORRIDOR);
    for r in rects {
        let (x, y, w, h) = (r[0], r[1], r[2].max(1.0), r[3].max(1.0));
        let (x0, x1) = (x, x + w);
        let (y0, y1) = (y, y + h);
        let u1 = (w / TILE).max(1.0);
        let v1 = (h / TILE).max(1.0);
        push_quad(&mut v, &mut i,
            [vec3(x0, y0, z1), vec3(x1, y0, z1), vec3(x1, y1, z1), vec3(x0, y1, z1)],
            [vec2(0.0, 0.0), vec2(u1, 0.0), vec2(u1, v1), vec2(0.0, v1)], WHITE);
        push_quad(&mut v, &mut i,
            [vec3(x1, y0, z0), vec3(x0, y0, z0), vec3(x0, y1, z0), vec3(x1, y1, z0)],
            [vec2(0.0, 0.0), vec2(u1, 0.0), vec2(u1, v1), vec2(0.0, v1)], WHITE);
        push_quad(&mut v, &mut i,
            [vec3(x0, y0, z0), vec3(x1, y0, z0), vec3(x1, y0, z1), vec3(x0, y0, z1)],
            [vec2(0.0, 0.0), vec2(u1, 0.0), vec2(u1, 1.0), vec2(0.0, 1.0)], WHITE);
        push_quad(&mut v, &mut i,
            [vec3(x0, y1, z1), vec3(x1, y1, z1), vec3(x1, y1, z0), vec3(x0, y1, z0)],
            [vec2(0.0, 0.0), vec2(u1, 0.0), vec2(u1, 1.0), vec2(0.0, 1.0)], WHITE);
        push_quad(&mut v, &mut i,
            [vec3(x0, y0, z0), vec3(x0, y0, z1), vec3(x0, y1, z1), vec3(x0, y1, z0)],
            [vec2(0.0, 0.0), vec2(1.0, 0.0), vec2(1.0, v1), vec2(0.0, v1)], WHITE);
        push_quad(&mut v, &mut i,
            [vec3(x1, y0, z1), vec3(x1, y0, z0), vec3(x1, y1, z0), vec3(x1, y1, z1)],
            [vec2(0.0, 0.0), vec2(1.0, 0.0), vec2(1.0, v1), vec2(0.0, v1)], WHITE);
    }
    Mesh { vertices: v, indices: i, texture: Some(texture) }
}

fn corridor_mesh(level: &LevelData, texture: Texture2D) -> Mesh {
    let mut v = Vec::new();
    let mut i = Vec::new();
    let (w, h) = (level.width, level.height);
    // пол и потолок — плитка 64x64 по X и по Z
    let mut x = 0.0;
    while x < w {
        let nx = (x + TILE).min(w);
        let mut z = -CORRIDOR;
        while z < CORRIDOR {
            let nz = (z + TILE).min(CORRIDOR);
            push_quad(&mut v, &mut i,
                [vec3(x, h, z), vec3(nx, h, z), vec3(nx, h, nz), vec3(x, h, nz)],
                [vec2(0.0, 0.0), vec2(1.0, 0.0), vec2(1.0, 1.0), vec2(0.0, 1.0)], WHITE);
            push_quad(&mut v, &mut i,
                [vec3(x, 0.0, nz), vec3(nx, 0.0, nz), vec3(nx, 0.0, z), vec3(x, 0.0, z)],
                [vec2(0.0, 0.0), vec2(1.0, 0.0), vec2(1.0, 1.0), vec2(0.0, 1.0)], WHITE);
            z = nz;
        }
        x = nx;
    }
    // боковые стены коридора — плитка 64x64 по X и по Y
    for z in [-CORRIDOR, CORRIDOR] {
        let mut x = 0.0;
        while x < w {
            let nx = (x + TILE).min(w);
            let mut y = 0.0;
            while y < h {
                let ny = (y + TILE).min(h);
                if z < 0.0 {
                    push_quad(&mut v, &mut i,
                        [vec3(x, y, z), vec3(nx, y, z), vec3(nx, ny, z), vec3(x, ny, z)],
                        [vec2(0.0, 0.0), vec2(1.0, 0.0), vec2(1.0, 1.0), vec2(0.0, 1.0)], WHITE);
                } else {
                    push_quad(&mut v, &mut i,
                        [vec3(nx, y, z), vec3(x, y, z), vec3(x, ny, z), vec3(nx, ny, z)],
                        [vec2(0.0, 0.0), vec2(1.0, 0.0), vec2(1.0, 1.0), vec2(0.0, 1.0)], WHITE);
                }
                y = ny;
            }
            x = nx;
        }
    }
    Mesh { vertices: v, indices: i, texture: Some(texture) }
}

fn billboard_mesh(list: &[[f32; 4]], texture: Texture2D) -> Mesh {
    let mut v = Vec::new();
    let mut i = Vec::new();
    for r in list {
        let (x0, y0, w, h) = (r[0], r[1], r[2], r[3]);
        push_quad(&mut v, &mut i,
            [vec3(x0, y0, 0.0), vec3(x0 + w, y0, 0.0), vec3(x0 + w, y0 + h, 0.0), vec3(x0, y0 + h, 0.0)],
            [vec2(0.0, 0.0), vec2(1.0, 0.0), vec2(1.0, 1.0), vec2(0.0, 1.0)], WHITE);
    }
    Mesh { vertices: v, indices: i, texture: Some(texture) }
}

// ─────────────────────────── мир ───────────────────────────

struct World {
    level: LevelData,
    player: Player,
    walls3d: Mesh,
    hazards3d: Mesh,
    doors3d: Mesh,
    jumps3d: Mesh,
    enemy3d: Mesh,
    floor3d: Mesh,
}

impl World {
    fn new(level: LevelData, art: &Art) -> World {
        let walls3d = box_mesh(&level.walls, art.wall.clone());
        let hazards3d = box_mesh(&level.hazards, art.hazard.clone());
        let mut doors = level.doors.clone();
        doors.extend(level.closes.iter().copied());
        let doors3d = box_mesh(&doors, art.door.clone());
        let jumps3d = box_mesh(&level.jumps, art.jump.clone());
        let enemy3d = billboard_mesh(&level.enemies, art.enemy.clone());
        let floor3d = corridor_mesh(&level, art.wall.clone());
        let player = Player::spawn(&level);
        World { level, player, walls3d, hazards3d, doors3d, jumps3d, enemy3d, floor3d }
    }
}

fn argb(c: u32) -> Color {
    Color::new(
        ((c >> 16) & 0xFF) as f32 / 255.0,
        ((c >> 8) & 0xFF) as f32 / 255.0,
        (c & 0xFF) as f32 / 255.0,
        1.0,
    )
}

fn window_conf() -> Conf {
    Conf {
        window_title: "Parcoobe 3D".to_owned(),
        window_width: 1280,
        window_height: 720,
        high_dpi: false,
        ..Default::default()
    }
}

// ─────────────────────────── отрисовка ───────────────────────────

fn draw_menu(levels: &[LevelData], sel: usize, first_person: bool) {
    draw_text("PARCOOBE 3D", 60.0, 96.0, 64.0, Color::new(1.0, 0.85, 0.62, 1.0));
    draw_text("VERSION 2.0", 64.0, 136.0, 24.0, Color::new(0.6, 0.9, 0.6, 1.0));

    let mut y = 210.0;
    for (i, l) in levels.iter().enumerate() {
        let color = if i == sel {
            Color::new(1.0, 0.9, 0.4, 1.0)
        } else {
            Color::new(0.8, 0.8, 0.8, 1.0)
        };
        let mark = if i == sel { "> " } else { "  " };
        draw_text(&format!("{}{}", mark, l.name.to_uppercase()), 80.0, y, 30.0, color);
        y += 40.0;
    }

    let cam = if first_person { "FIRST PERSON" } else { "SIDE VIEW" };
    draw_text(&format!("CAMERA: {} (F5)", cam), 60.0, screen_height() - 76.0, 22.0,
              Color::new(0.7, 0.7, 0.7, 1.0));
    draw_text("ENTER PLAY   UP/DOWN LEVEL   F1 CONTROLS   ESC QUIT",
              60.0, screen_height() - 40.0, 22.0, Color::new(0.7, 0.7, 0.7, 1.0));
}

fn draw_side(w: &World, art: &Art) {
    // Y в комнате растёт вниз, как в GameMaker: подбираем знак zoom под это
    let cam = Camera2D {
        zoom: vec2(2.0 / w.level.width, 2.0 / w.level.height),
        target: vec2(w.level.width * 0.5, w.level.height * 0.5),
        ..Default::default()
    };
    set_camera(&cam);

    draw_rectangle(0.0, 0.0, w.level.width, w.level.height, argb(w.level.bg));

    for r in &w.level.walls {
        draw_texture_ex(&art.wall, r[0], r[1], WHITE, DrawTextureParams {
            dest_size: Some(vec2(r[2], r[3])), ..Default::default()
        });
    }
    for r in &w.level.hazards {
        draw_texture_ex(&art.hazard, r[0], r[1], WHITE, DrawTextureParams {
            dest_size: Some(vec2(r[2], r[3])), ..Default::default()
        });
    }
    for r in &w.level.jumps {
        draw_texture_ex(&art.jump, r[0], r[1], WHITE, DrawTextureParams {
            dest_size: Some(vec2(r[2], r[3])), ..Default::default()
        });
    }
    for r in &w.level.closes {
        draw_texture_ex(&art.closed, r[0], r[1], WHITE, DrawTextureParams {
            dest_size: Some(vec2(r[2], r[3])), ..Default::default()
        });
    }
    for r in &w.level.doors {
        draw_texture_ex(&art.door, r[0], r[1], WHITE, DrawTextureParams {
            dest_size: Some(vec2(r[2], r[3])), ..Default::default()
        });
    }
    for r in &w.level.enemies {
        draw_texture_ex(&art.enemy, r[0], r[1], WHITE, DrawTextureParams {
            dest_size: Some(vec2(r[2], r[3])), ..Default::default()
        });
    }

    let p = &w.player;
    let t = if p.vx < -1.0 {
        &art.player_left
    } else if p.vx > 1.0 {
        &art.player_right
    } else {
        &art.player_front
    };
    draw_texture_ex(t, p.x - 32.0, p.y - 64.0, WHITE, DrawTextureParams {
        dest_size: Some(vec2(64.0, 64.0)), ..Default::default()
    });

    set_default_camera();
}

fn draw_first_person(w: &World) {
    let p = &w.player;
    let eye = vec3(p.x, p.y - 56.0, 0.0);
    let dir = if p.facing >= 0.0 { 1.0 } else { -1.0 };
    let cam = Camera3D {
        position: eye,
        target: eye + vec3(dir * 100.0, 0.0, 0.0),
        up: vec3(0.0, -1.0, 0.0),
        fovy: 75f32.to_radians(),
        z_near: 0.5,
        z_far: 5000.0,
        ..Default::default()
    };
    set_camera(&cam);
    draw_mesh(&w.floor3d);
    draw_mesh(&w.walls3d);
    draw_mesh(&w.hazards3d);
    draw_mesh(&w.jumps3d);
    draw_mesh(&w.doors3d);
    draw_mesh(&w.enemy3d);
    set_default_camera();
}

fn draw_ui(controls: &Controls, sel: usize, binding: Option<usize>) {
    let (sw, sh) = (screen_width(), screen_height());
    draw_rectangle(60.0, 60.0, sw - 120.0, sh - 120.0, Color::new(0.0, 0.0, 0.0, 0.93));
    draw_rectangle_lines(60.0, 60.0, sw - 120.0, sh - 120.0, 2.0, Color::new(0.9, 0.8, 0.4, 1.0));
    draw_text("CONTROLS", 90.0, 112.0, 42.0, Color::new(1.0, 0.85, 0.5, 1.0));
    draw_text("UP/DOWN SELECT   ENTER REBIND   ESC CLOSE", 90.0, 146.0, 20.0,
              Color::new(0.6, 0.6, 0.6, 1.0));

    let mut y = 205.0;
    for i in 0..SLOT_TITLES.len() {
        let color = if sel == i {
            Color::new(1.0, 0.9, 0.4, 1.0)
        } else {
            Color::new(0.85, 0.85, 0.85, 1.0)
        };
        draw_text(SLOT_TITLES[i], 100.0, y, 28.0, color);
        draw_text(controls.name(i), 430.0, y, 28.0, WHITE);
        y += 44.0;
    }
    let color = if sel == SLOT_TITLES.len() {
        Color::new(1.0, 0.9, 0.4, 1.0)
    } else {
        Color::new(0.85, 0.85, 0.85, 1.0)
    };
    draw_text("RESET DEFAULTS", 100.0, y, 28.0, color);

    if binding.is_some() {
        draw_rectangle(60.0, 60.0, sw - 120.0, sh - 120.0, Color::new(0.0, 0.0, 0.0, 0.82));
        draw_text("PRESS A KEY...", sw * 0.5 - 150.0, sh * 0.5, 44.0,
                  Color::new(1.0, 0.9, 0.5, 1.0));
    }
}

// ─────────────────────────── главный цикл ───────────────────────────

#[derive(Clone, Copy, PartialEq)]
enum Screen {
    Menu,
    Play,
}

#[macroquad::main(window_conf)]
async fn main() {
    let levels = load_levels();
    let art = Art::load();
    let mut controls = Controls::load();

    let mut screen = Screen::Menu;
    let mut first_person = false;
    let mut menu_sel = 0usize;
    let mut ui_open = false;
    let mut ui_sel = 0usize;
    let mut binding: Option<usize> = None;
    let mut world: Option<World> = None;
    let mut next_level: Option<String> = None;

    loop {
        let dt = get_frame_time().min(0.05);

        // ── глобальные клавиши
        if is_key_pressed(KeyCode::Escape) {
            if ui_open {
                ui_open = false;
                binding = None;
            } else if world.is_some() {
                world = None;
                screen = Screen::Menu;
            } else {
                std::process::exit(0);
            }
        }
        if is_key_pressed(KeyCode::F1) {
            ui_open = !ui_open;
            binding = None;
            ui_sel = 0;
        }
        if is_key_pressed(controls.key(5)) {
            first_person = !first_person;
        }

        // ── меню
        if let Screen::Menu = screen {
            if !ui_open {
                if is_key_pressed(KeyCode::Down) {
                    menu_sel = (menu_sel + 1) % levels.len();
                }
                if is_key_pressed(KeyCode::Up) {
                    menu_sel = (menu_sel + levels.len() - 1) % levels.len();
                }
                if is_key_pressed(KeyCode::Enter) {
                    world = Some(World::new(levels[menu_sel].clone(), &art));
                    screen = Screen::Play;
                }
            }
        }

        // ── переназначение
        if ui_open {
            if let Some(slot) = binding {
                for &key in ALL_KEYS {
                    if is_key_pressed(key) {
                        if let Some(name) = key_to_name(key) {
                            controls.set(slot, name.to_string());
                            controls.save();
                        }
                        binding = None;
                        break;
                    }
                }
            } else {
                let rows = SLOT_TITLES.len() + 1;
                if is_key_pressed(KeyCode::Down) {
                    ui_sel = (ui_sel + 1) % rows;
                }
                if is_key_pressed(KeyCode::Up) {
                    ui_sel = (ui_sel + rows - 1) % rows;
                }
                if is_key_pressed(KeyCode::Enter) {
                    if ui_sel < SLOT_TITLES.len() {
                        binding = Some(ui_sel);
                    } else {
                        controls = Controls::default();
                        controls.save();
                    }
                }
            }
        }

        // ── игра
        if screen == Screen::Play {
          if let Some(w) = world.as_mut() {
            if !ui_open {
                let mut left = is_key_down(controls.key(0));
                let mut right = is_key_down(controls.key(1));
                if first_person {
                    if is_key_down(controls.key(2)) {
                        if w.player.facing > 0.0 {
                            right = true;
                        } else {
                            left = true;
                        }
                    }
                    if is_key_down(controls.key(3)) {
                        if w.player.facing > 0.0 {
                            left = true;
                        } else {
                            right = true;
                        }
                    }
                }
                let jump = is_key_pressed(controls.key(4));
                step_player(&mut w.player, &w.level, left, right, jump, dt);

                let pr = w.player.rect();
                if w.level.doors.iter().any(|d| overlaps(pr, *d)) {
                    next_level = Some(w.level.name.clone());
                }
            }
          }
        }

        // ── смена уровня по двери
        if let Some(name) = next_level.take() {
            let idx = levels.iter().position(|l| l.name == name).unwrap_or(0);
            let next = (idx + 1) % levels.len();
            world = Some(World::new(levels[next].clone(), &art));
        }

        // ── отрисовка
        clear_background(Color::new(0.02, 0.02, 0.02, 1.0));
        match screen {
            Screen::Menu => draw_menu(&levels, menu_sel, first_person),
            Screen::Play => {
                if let Some(w) = world.as_ref() {
                    if first_person {
                        draw_first_person(w);
                    } else {
                        draw_side(w, &art);
                    }
                    let cam = if first_person { "FIRST PERSON" } else { "SIDE" };
                    draw_text(
                        &format!("{}   {}   F5 CAMERA   F1 CONTROLS   ESC MENU",
                                 w.level.name.to_uppercase(), cam),
                        20.0, 30.0, 22.0, Color::new(1.0, 1.0, 1.0, 0.85),
                    );
                }
            }
        }
        if ui_open {
            draw_ui(&controls, ui_sel, binding);
        }

        next_frame().await;
    }
}

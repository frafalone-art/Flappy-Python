import pygame
import random
import datetime
import math
import json
import os
try:
    import numpy as np
except Exception:
    np = None

# ---------------- PATHS ----------------

BASE_DIR = os.path.dirname(__file__)

IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
SND_DIR = os.path.join(BASE_DIR, "assets", "sounds")
DATA_DIR = os.path.join(os.path.expanduser("~"), "FlappyPython")
CHAR_FILE = os.path.join(DATA_DIR, "characters.json")

LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")

# ---------------- LEADERBOARD ----------------

def load_scores():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)["scores"]
    return []


def save_scores(new_score):
    scores = load_scores()
    scores.append(new_score)
    scores = sorted(scores, reverse=True)[:5]
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump({"scores": scores}, f)


def load_characters():
    # Four characters: first unlocked by default, others locked until thresholds
    defaults = {"is_unlocked": [True, False, False, False], "thresholds": [0, 25, 50, 100], "unlock_all": True, "selected": 0}
    if os.path.exists(CHAR_FILE):
        try:
            with open(CHAR_FILE, "r") as f:
                data = json.load(f)
                # force unlock_all true now and persist
                data["unlock_all"] = True
                data["is_unlocked"] = [True] * len(data.get("is_unlocked", defaults["is_unlocked"]))
                # ensure selected is valid
                data.setdefault("selected", 0)
                try:
                    save_characters(data)
                except Exception:
                    pass
                return data
        except Exception:
            return defaults
    else:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CHAR_FILE, "w") as f:
            json.dump(defaults, f)
        return defaults


def save_characters(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CHAR_FILE, "w") as f:
        json.dump(data, f)


def update_unlocks(score):
    data = load_characters()
    changed = False
    for i, th in enumerate(data.get("thresholds", [])):
        if score >= th and not data["is_unlocked"][i]:
            data["is_unlocked"][i] = True
            changed = True
    if changed:
        save_characters(data)


# ---------------- INIT ----------------
# initialize mixer before pygame to ensure sndarray audio format matches
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIDTH, HEIGHT = 390, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Python")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 30, bold=True)
font_small = pygame.font.SysFont("Arial", 20, bold=True)

# ---------------- TUNING ----------------

# Larghezza dell'hitbox dei tubi (in px). Regola questo valore giocando,
# non è calcolato a tavolino.
PIPE_HITBOX_WIDTH = 28

# I nuovi asset (tubo e pavimento) sono pixel art 32px, moltiplicati per
# questo fattore intero per restare nitidi (niente smoothing che sfoca
# i pixel).
ASSET_SCALE = 3

PIPE_TARGET_HEIGHT = 600  # come prima: copre tutto lo schermo
# Background margin so it doesn't overlap the ground; smaller -> background stretches up
BG_MARGIN = 0

# Dimensione unica per tutti i personaggi (menu, gioco, schermata characters)
CHAR_SIZE = 64


def build_tiled_column(tile, target_height):
    """Ripete verticalmente un tile (già scalato) fino a superare
    target_height, poi ritaglia all'altezza esatta. Nessuna distorsione:
    il tile non viene mai stirato, solo ripetuto."""
    tw, th = tile.get_size()
    count = math.ceil(target_height / th)
    column = pygame.Surface((tw, th * count), pygame.SRCALPHA)
    for i in range(count):
        column.blit(tile, (0, i * th))
    return column.subsurface((0, 0, tw, target_height)).copy()


def build_tiled_row(tile, target_width):
    """Come build_tiled_column ma in orizzontale, per il pavimento."""
    tw, th = tile.get_size()
    count = math.ceil(target_width / tw)
    row = pygame.Surface((tw * count, th), pygame.SRCALPHA)
    for i in range(count):
        row.blit(tile, (i * tw, 0))
    return row.subsurface((0, 0, target_width, th)).copy()


def cover_scale(surf, target_w, target_h, zoom=1.2, anchor_y=1.0):
    """Scala l'immagine mantenendo le proporzioni finché copre interamente
    (target_w, target_h), poi ritaglia. Evita lo stiramento che si avrebbe
    scalando larghezza e altezza in modo indipendente.
    zoom > 1 dà margine extra da ritagliare; anchor_y controlla dove
    tagliare in verticale (0 = tieni la parte alta, 1 = tieni la parte
    bassa — qui a 1.0 per mostrare più skyline e meno cielo vuoto)."""
    sw, sh = surf.get_size()
    scale = max(target_w / sw, target_h / sh) * zoom
    new_w, new_h = round(sw * scale), round(sh * scale)
    scaled = pygame.transform.smoothscale(surf, (new_w, new_h))
    x = (new_w - target_w) // 2
    y = round((new_h - target_h) * anchor_y)
    result = pygame.Surface((target_w, target_h))
    result.blit(scaled, (0, 0), area=pygame.Rect(x, y, target_w, target_h))
    return result


def fit_inside(surf, max_w, max_h):
    sw, sh = surf.get_size()
    scale = min(max_w / sw, max_h / sh)
    new_w, new_h = max(1, int(sw * scale)), max(1, int(sh * scale))
    return pygame.transform.smoothscale(surf, (new_w, new_h))


# ---------------- LOAD ASSETS ----------------

def img(name):
    return os.path.join(IMG_DIR, name)

def snd(name):
    return os.path.join(SND_DIR, name)

try:
    logo         = pygame.image.load(img("FlappyBird.png")).convert()
    logo.set_colorkey((0, 0, 0))
    logo = logo.convert_alpha()

    # Load raw backgrounds now; we'll scale them after ground height is known
    _raw_bg_day = pygame.image.load(img("background_day.png")).convert()
    _raw_bg_night = pygame.image.load(img("background_night.png")).convert()

    ground_tile  = pygame.image.load(img("ground.png")).convert_alpha()
    ground_tile  = pygame.transform.scale(
                       ground_tile,
                       (ground_tile.get_width() * ASSET_SCALE,
                        ground_tile.get_height() * ASSET_SCALE))
    img_ground   = build_tiled_row(ground_tile, WIDTH)
    GROUND_Y     = HEIGHT - img_ground.get_height()

    # Now scale backgrounds so they cover the area above the ground,
    # slightly shorter than the full GROUND_Y so the ground is visible.
    target_bg_h = max(1, GROUND_Y - BG_MARGIN)
    # zoom leggermente >1 per evitare un filo di bordo scoperto ai lati
    # della finestra dovuto agli arrotondamenti dello scaling
    img_bg_day = cover_scale(_raw_bg_day, WIDTH, target_bg_h, zoom=1.03, anchor_y=1.0)
    img_bg_night = cover_scale(_raw_bg_night, WIDTH, target_bg_h, zoom=1.03, anchor_y=1.0)

    # Try bird.png first, fall back to bird.jpeg
    try:
        img_bird = pygame.image.load(img("bird.png")).convert_alpha()
    except:
        img_bird = pygame.image.load(img("bird.jpeg")).convert()
        img_bird.set_colorkey(img_bird.get_at((0, 0)))  

    img_bird = pygame.transform.scale(img_bird, (46, 46))

    pipe_tile    = pygame.image.load(img("pipe.png")).convert_alpha()
    pipe_tile    = pygame.transform.scale(
                       pipe_tile,
                       (pipe_tile.get_width() * ASSET_SCALE,
                        pipe_tile.get_height() * ASSET_SCALE))
    img_pipe     = build_tiled_column(pipe_tile, PIPE_TARGET_HEIGHT)

    _tmp_go = pygame.image.load(img("game_over.png")).convert()
    _tmp_go.set_colorkey((0, 0, 0))
    _tmp_go = _tmp_go.convert_alpha()
    img_game_over = fit_inside(_tmp_go, 250, 150)

    sfx_flap  = pygame.mixer.Sound(snd("battito.wav"))
    sfx_death = pygame.mixer.Sound(snd("sconfitta.wav"))
    sfx_point = pygame.mixer.Sound(snd("punto.wav"))
    # lower sfx slightly so music is more audible
    sfx_flap.set_volume(0.6)
    # restore death sound to full volume
    sfx_death.set_volume(1.0)
    sfx_point.set_volume(0.6)

    # Load character images (four). Nomi reali dei file in assets/images:
    # 1=bird.png, 2=snake_red.png, 3=snake_yellow.png, 4=snake_black.png
    print(f"[characters] loading from: {IMG_DIR}")
    try:
        print(f"[characters] files found there: {os.listdir(IMG_DIR)}")
    except Exception as e:
        print(f"[characters] cannot list {IMG_DIR}: {e}")
    char_img_names = ["bird.png", "snake_red.png", "snake_yellow.png", "snake_black.png"]
    img_chars = []
    for name in char_img_names:
        try:
            im = pygame.image.load(img(name)).convert_alpha()
            im = fit_inside(im, CHAR_SIZE, CHAR_SIZE)
        except Exception as e:
            print(f"[characters] could not load {img(name)}: {e}")
            im = None
        img_chars.append(im)
    # helper: tint fallback from base bird image when a char image is missing
    def tint_fallback(surf, color):
        try:
            base = pygame.transform.scale(img_bird, (CHAR_SIZE, CHAR_SIZE)).copy()
            tint = pygame.Surface(base.get_size(), pygame.SRCALPHA)
            tint.fill(color + (0,))
            base.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            return base
        except Exception:
            return None
    # ensure skins exist by tinting the base if missing
    # order: green, red, yellow, black
    skin_colors = [(34, 139, 34), (220, 30, 30), (240, 220, 30), (30, 30, 30)]
    for i in range(4):
        if img_chars[i] is None:
            img_chars[i] = tint_fallback(img_bird, skin_colors[i])
    # current selected character index (persisted in characters.json)
    try:
        current_char = load_characters().get("selected", 0)
    except Exception:
        current_char = 0

    # procedural SFX will be generated later after function definitions

except Exception as e:
    print(f"Asset loading error: {e}")
    pygame.quit()
    raise SystemExit


def get_selected_skin():
    """Personaggio attualmente selezionato, usato sia nel menu che in gioco
    così sono sempre identici (stessa immagine, stessa dimensione)."""
    try:
        sel = load_characters().get("selected", 0)
        if 0 <= sel < len(img_chars) and img_chars[sel] is not None:
            return img_chars[sel]
    except Exception:
        pass
    return pygame.transform.scale(img_bird, (CHAR_SIZE, CHAR_SIZE))


# ---------------- CLASSES ----------------


# ---------------- MUSIC (procedural) ----------------
def generate_tone(freq, duration, volume=0.2, sample_rate=44100):
    if np is None:
        return None
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # simple sawtooth-ish happy timbre using additive synthesis
    wave = (0.6 * np.sin(2 * np.pi * freq * t)
            + 0.3 * np.sin(2 * np.pi * freq * 2 * t)
            + 0.1 * np.sin(2 * np.pi * freq * 3 * t))
    # soft envelope
    env = np.minimum(1.0, np.linspace(0, 1, int(sample_rate * 0.02)))
    if len(env) < len(wave):
        env = np.pad(env, (0, len(wave) - len(env)), 'constant', constant_values=(1.0,))
    wave = wave * env
    # stereo
    stereo = np.column_stack((wave, wave))
    audio = np.int16(stereo * volume * 32767)
    return audio


def start_procedural_music(bpm=140):
    if np is None:
        return
    sample_rate = 44100
    beat_sec = 60.0 / bpm
    # a simple happy progression (C - G - Am - F) in Hz (C4,G3,A3,F3-ish)
    freqs = [261.63, 196.00, 220.00, 174.61]
    bars = []
    for f in freqs:
        # arpeggio over 2 beats each
        seg = np.zeros((0, 2), dtype=np.int16)
        for note in [f, f * 1.25, f * 1.5, f * 2.0]:
            # louder generated tones so music is audible compared to SFX
            tone = generate_tone(note, beat_sec * 0.5, volume=0.6, sample_rate=sample_rate)
            if tone is not None:
                seg = np.vstack((seg, tone)) if seg.size else tone
        bars.append(seg)
    loop = np.vstack(bars)
    try:
        snd = pygame.sndarray.make_sound(loop.copy())
        snd.set_volume(0.8)
        snd.play(loops=-1)
    except Exception:
        pass


# ---------------- PROCEDURAL SFX ----------------
def make_sound_from_array(arr, sample_rate=44100):
    try:
        return pygame.sndarray.make_sound(arr.copy())
    except Exception:
        return None


def generate_chirp(start_hz, end_hz, duration, volume=0.7, sample_rate=44100):
    if np is None:
        return None
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    freqs = np.linspace(start_hz, end_hz, t.size)
    wave = np.sin(2 * np.pi * freqs * t)
    # quick attack-decay envelope
    env = np.ones_like(wave)
    atk = int(sample_rate * 0.005)
    dec = int(sample_rate * 0.02)
    env[:atk] = np.linspace(0, 1, atk)
    env[-dec:] = np.linspace(1, 0, dec)
    wave = wave * env
    stereo = np.column_stack((wave, wave))
    audio = np.int16(stereo * volume * 32767)
    return audio


def generate_hiss(duration=0.12, volume=0.5, sample_rate=44100):
    if np is None:
        return None
    count = int(sample_rate * duration)
    # white noise
    noise = np.random.normal(0, 1, count)
    # high-pass-ish by subtracting low-freq moving average
    kernel = np.ones(50) / 50.0
    low = np.convolve(noise, kernel, mode='same')
    hp = noise - low
    # envelope
    env = np.ones_like(hp)
    atk = max(1, int(0.01 * sample_rate))
    env[:atk] = np.linspace(0, 1, atk)
    env[-int(0.02 * sample_rate):] = np.linspace(1, 0, int(0.02 * sample_rate))
    hp = hp * env
    stereo = np.column_stack((hp, hp))
    audio = np.int16(stereo * volume * 32767)
    return audio


# initialize procedural music and SFX (only if numpy available)
proc_point = None
proc_hiss = None
if np is not None:
    try:
        start_procedural_music(140)
    except Exception:
        pass
    try:
        chirp_arr = generate_chirp(700, 1200, 0.12, volume=0.8)
        if chirp_arr is not None:
            proc_point = make_sound_from_array(chirp_arr)
            if proc_point:
                proc_point.set_volume(0.9)
    except Exception:
        proc_point = None
    try:
        hiss_arr = generate_hiss(0.12, volume=0.6)
        if hiss_arr is not None:
            proc_hiss = make_sound_from_array(hiss_arr)
            if proc_hiss:
                proc_hiss.set_volume(0.9)
    except Exception:
        proc_hiss = None

class Bird:

    def __init__(self):
        self.x = 100
        self.y = 300
        self.vel = 0
        self.active = True

    def update(self):
        if self.active:
            self.vel += 0.5
            self.y += self.vel

    def draw(self):
        angle = max(-25, min(90, -self.vel * 4))
        skin = get_selected_skin()
        rotated = pygame.transform.rotate(skin, angle)
        screen.blit(rotated, rotated.get_rect(center=(self.x, self.y)))


class WorldManager:

    def __init__(self):
        self.bg_x = 0
        self.ground_x = 0

    def update(self, active):
        if active:
            self.bg_x -= 1
            self.ground_x -= 3
            # wrap based on current background width
            bg = img_bg_day
            bg_w = bg.get_width()
            if self.bg_x <= -bg_w: self.bg_x = 0
            if self.ground_x <= -WIDTH: self.ground_x = 0

    def draw(self, daytime):
        bg = img_bg_day if daytime else img_bg_night
        bg_w, bg_h = bg.get_size()
        # align lower border of background with ground (sit on top of ground)
        y = GROUND_Y - bg_h
        screen.blit(bg, (self.bg_x, y))
        screen.blit(bg, (self.bg_x + bg_w, y))

    def draw_ground(self):
        screen.blit(img_ground, (self.ground_x, GROUND_Y))
        screen.blit(img_ground, (self.ground_x + WIDTH, GROUND_Y))


class PipeManager:

    def __init__(self):
        self.pipes = []
        self.timer = 0
        self.score = 0

    def spawn(self):
        h = random.randint(150, 350)
        gap = 165
        self.pipes.append({"x": WIDTH + 50, "y": h,       "type": "top",    "passed": False})
        self.pipes.append({"x": WIDTH + 50, "y": h + gap, "type": "bottom"})

    def update(self, active):
        if active:
            for p in self.pipes: p["x"] -= 3
            self.pipes = [p for p in self.pipes if p["x"] > -100]


class Menu:

    MEDALS  = ["1", "2", "3", "4.", "5."]

    def __init__(self):
        self.timer = 0
        self.logo = fit_inside(logo, 300, 100)

    def update(self):
        self.timer += 1

    def draw_button(self, text, y, color):
        rect = pygame.Rect(WIDTH // 2 - 130, y, 260, 50)
        pygame.draw.rect(screen, color, rect, border_radius=12)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=12)
        txt = font.render(text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=rect.center))
        return rect

    def draw(self, daytime):
        world.draw(daytime)
        world.draw_ground()

        # Logo
        screen.blit(self.logo, self.logo.get_rect(center=(WIDTH // 2, 110)))

        # Floating character: stesso identico sprite (e stessa dimensione,
        # CHAR_SIZE) del personaggio usato in gioco da Bird.draw()
        skin = get_selected_skin()
        bird_y = 230 + math.sin(self.timer * 0.05) * 15
        angle  = math.sin(self.timer * 0.05) * 15
        rotated = pygame.transform.rotate(skin, angle)
        screen.blit(rotated, rotated.get_rect(center=(WIDTH // 2, bird_y)))

        # Buttons (dynamically positioned above the ground)
        button_h = 50
        spacing = 12
        count = 4
        total_h = count * button_h + (count - 1) * spacing
        start_y = GROUND_Y - total_h - 20
        if start_y < 160:
            start_y = 160

        r_play = self.draw_button("  PLAY", start_y, (34, 139, 34))
        r_leaderboard = self.draw_button("LEADERBOARD", start_y + (button_h + spacing) * 1, (30, 100, 180))
        r_chars = self.draw_button("CHARACTERS", start_y + (button_h + spacing) * 2, (128, 0, 128))
        r_credits = self.draw_button("CREDITS", start_y + (button_h + spacing) * 3, (100, 100, 100))

        return r_play, r_leaderboard, r_chars, r_credits


class LeaderboardScreen:

    MEDALS = ["1", "2", "3", "4.", "5."]
    COLORS = [
        (255, 215,   0),  # gold
        (192, 192, 192),  # silver
        (205, 127,  50),  # bronze
        (255, 255, 255),
        (255, 255, 255),
    ]

    def draw(self, daytime):
        world.draw(daytime)
        world.draw_ground()

        panel = pygame.Surface((340, 340), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        screen.blit(panel, (25, 110))

        title = font.render("  LEADERBOARD", True, (255, 220, 0))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 140)))

        scores = load_scores()
        if scores:
            for i, score in enumerate(scores):
                row = font.render(f"{self.MEDALS[i]}  {score}", True, self.COLORS[i])
                screen.blit(row, row.get_rect(center=(WIDTH // 2, 200 + i * 50)))
        else:
            txt = font_small.render("No scores yet!", True, (200, 200, 200))
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, 280)))

        btn = pygame.Rect(WIDTH // 2 - 100, 470, 200, 45)
        pygame.draw.rect(screen, (100, 100, 100), btn, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), btn, 2, border_radius=10)
        screen.blit(font.render("← BACK", True, (255, 255, 255)),
                    font.render("← BACK", True, (255, 255, 255)).get_rect(center=btn.center))
        return btn


class CreditsScreen:

    def draw(self, daytime):
        world.draw(daytime)
        world.draw_ground()

        panel = pygame.Surface((340, 320), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        screen.blit(panel, (25, 120))

        title = font.render("CREDITS", True, (255, 220, 0))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        lines = [
            "Built with Python",
            "and pygame",
            "",
            "Graphics by messmeme & MegaCrash",
            "Sounds on pixabay.com",
            "",
            "A personal project",
            "to learn programming",
            "Dev: Francesco Falone",
            "v2.0.0",
        ]
        for i, line in enumerate(lines):
            txt = font_small.render(line, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, 190 + i * 24)))

        btn = pygame.Rect(WIDTH // 2 - 100, 460, 200, 45)
        pygame.draw.rect(screen, (100, 100, 100), btn, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), btn, 2, border_radius=10)
        screen.blit(font.render("← BACK", True, (255, 255, 255)),
                    font.render("← BACK", True, (255, 255, 255)).get_rect(center=btn.center))
        return btn


class CharacterScreen:

    def draw(self, daytime):
        world.draw(daytime)
        world.draw_ground()

        panel = pygame.Surface((340, 380), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        screen.blit(panel, (25, 90))

        title = font.render("CHARACTERS", True, (255, 220, 0))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        data = load_characters()
        unlocked = data.get("is_unlocked", [True, False, False, False])
        thresholds = data.get("thresholds", [0, 25, 50, 100])
        selected = data.get("selected", 0)

        box_w, box_h = 140, 120
        start_x = 40
        start_y = 150
        gap_x = 20
        gap_y = 20

        boxes = []
        for i in range(4):
            col = i % 2
            row = i // 2
            x = start_x + col * (box_w + gap_x)
            y = start_y + row * (box_h + gap_y)
            rect = pygame.Rect(x, y, box_w, box_h)
            boxes.append(rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, border_radius=8)
            # border: yellow if selected, black otherwise
            border_color = (255, 215, 0) if i == selected else (0, 0, 0)
            pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)

            if unlocked[i]:
                # show character images if available
                try:
                    char_im = img_chars[i] if i < len(img_chars) and img_chars[i] is not None else None
                except Exception:
                    char_im = None
                if char_im is None:
                    char_im = pygame.transform.scale(img_bird, (CHAR_SIZE, CHAR_SIZE))
                screen.blit(char_im, char_im.get_rect(center=rect.center))
            else:
                txt = font_small.render(f"Unlocked at {thresholds[i]}", True, (200, 200, 200))
                screen.blit(txt, txt.get_rect(center=rect.center))

        btn = pygame.Rect(WIDTH // 2 - 100, 480, 200, 45)
        pygame.draw.rect(screen, (100, 100, 100), btn, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), btn, 2, border_radius=10)
        screen.blit(font.render("← BACK", True, (255, 255, 255)),
                    font.render("← BACK", True, (255, 255, 255)).get_rect(center=btn.center))
        return btn, boxes


# ---------------- SETUP ----------------

bird   = Bird()
world  = WorldManager()
pipes  = PipeManager()
menu   = Menu()
leaderboard    = LeaderboardScreen()
credits_screen = CreditsScreen()
character_screen = CharacterScreen()

state = "menu"  # "menu" | "game" | "game_over" | "leaderboard" | "credits"


# ---------------- MAIN LOOP ----------------

while True:

    dt = clock.tick(60)
    hour    = datetime.datetime.now().hour
    daytime = 6 <= hour < 19

    # --- EVENTS ---
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if state == "menu":
                state = "game"
            elif state == "game":
                if bird.active:
                    bird.vel = -9
                    # play procedural hiss if available, else flap SFX
                    try:
                        if 'proc_hiss' in globals() and proc_hiss:
                            proc_hiss.play()
                        else:
                            sfx_flap.play()
                    except Exception:
                        try:
                            sfx_flap.play()
                        except Exception:
                            pass
            elif state == "game_over":
                bird  = Bird()
                world = WorldManager()
                pipes = PipeManager()
                state = "game"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state == "game_over":
                bird  = Bird()
                world = WorldManager()
                pipes = PipeManager()
                state = "menu"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state == "menu":
                r_play, r_lb, r_chars, r_credits = menu.draw(daytime)
                if r_play.collidepoint(event.pos):        state = "game"
                elif r_lb.collidepoint(event.pos):        state = "leaderboard"
                elif r_chars.collidepoint(event.pos):     state = "characters"
                elif r_credits.collidepoint(event.pos):   state = "credits"
            elif state == "leaderboard":
                if leaderboard.draw(daytime).collidepoint(event.pos):
                    state = "menu"
            elif state == "credits":
                if credits_screen.draw(daytime).collidepoint(event.pos):
                    state = "menu"
            elif state == "characters":
                btn, boxes = character_screen.draw(daytime)
                if btn.collidepoint(event.pos):
                    state = "menu"
                else:
                    # check boxes for selection
                    for i, r in enumerate(boxes):
                        if r.collidepoint(event.pos):
                            data = load_characters()
                            data["selected"] = i
                            save_characters(data)
                            break

    # --- LOGIC ---
    if state == "menu":
        menu.update()
        world.update(True)

    elif state == "game":
        # pygame.mixer.music.unpause()
        world.update(bird.active)
        bird.update()
        pipes.timer += dt
        if pipes.timer > 1500:
            pipes.spawn()
            pipes.timer = 0
        pipes.update(bird.active)

        b_hit = pygame.Rect(bird.x - 14, bird.y - 14, 28, 28)
        for p in pipes.pipes:
            if p["type"] == "top":
                p_hit = pygame.Rect(p["x"] - PIPE_HITBOX_WIDTH // 2, 0,
                                     PIPE_HITBOX_WIDTH, p["y"])
                if p["x"] < bird.x and not p["passed"]:
                    pipes.score += 1
                    p["passed"] = True
                    # play procedural point (chirp) if available, else file SFX
                    try:
                        if 'proc_point' in globals() and proc_point:
                            proc_point.play()
                        else:
                            sfx_point.play()
                    except Exception:
                        try:
                            sfx_point.play()
                        except Exception:
                            pass
            else:
                p_hit = pygame.Rect(p["x"] - PIPE_HITBOX_WIDTH // 2, p["y"],
                                     PIPE_HITBOX_WIDTH, HEIGHT - p["y"])

            if b_hit.colliderect(p_hit) and bird.active:
                bird.active = False
                sfx_death.play()
                save_scores(pipes.score)
                update_unlocks(pipes.score)

        if bird.y < 0 or bird.y + 15 > GROUND_Y:
            if bird.active:
                bird.active = False
                sfx_death.play()
                save_scores(pipes.score)
                update_unlocks(pipes.score)

        if not bird.active:
            state = "game_over"
            # pygame.mixer.music.pause()

    # --- DRAW ---
    if state == "menu":
        menu.draw(daytime)

    elif state == "leaderboard":
        leaderboard.draw(daytime)

    elif state == "credits":
        credits_screen.draw(daytime)

    elif state == "characters":
        character_screen.draw(daytime)

    elif state in ("game", "game_over"):
        world.draw(daytime)

        for p in pipes.pipes:
            if p["type"] == "top":
                flipped = pygame.transform.flip(img_pipe, False, True)
                screen.blit(flipped, flipped.get_rect(midbottom=(p["x"], p["y"])))
            else:
                screen.blit(img_pipe, img_pipe.get_rect(midtop=(p["x"], p["y"])))

        world.draw_ground()
        bird.draw()

        score_color = (0, 120, 255) if daytime else (255, 255, 255)
        score_txt = font.render(f"Score: {pipes.score}", True, score_color)
        screen.blit(score_txt, (20, 20))

        if state == "game_over":
            screen.blit(img_game_over, (WIDTH // 2 - 125, HEIGHT // 2 - 250))

            msg = font.render(f"SCORE: {pipes.score}", True, (0, 0, 0))
            screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))

            # Record — gold if new best
            scores = load_scores()
            record = scores[0] if scores else 0
            record_color = (255, 215, 0) if pipes.score == record else (0, 0, 0)
            rec_txt = font.render(f" BEST: {record}", True, record_color)
            screen.blit(rec_txt, rec_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

            retry = font.render("SPACE TO RESTART", True, (0, 0, 0))
            screen.blit(retry, retry.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))
            back_to_menu = font.render("ESC TO THE MENU", True, (0, 0, 0))
            screen.blit(back_to_menu, back_to_menu.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

    pygame.display.update()

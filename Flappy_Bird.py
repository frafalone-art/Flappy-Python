import pygame
import random
import datetime
import math
import json
import os

# ---------------- PATHS ----------------

BASE_DIR = os.path.dirname(__file__)

IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
SND_DIR = os.path.join(BASE_DIR, "assets", "sounds")
DATA_DIR = os.path.join(BASE_DIR, "data")

LEADERBOARD_FILE = os.path.join(
    DATA_DIR,
    "leaderboard.json"
)

# ---------------- LEADERBOARD ----------------

def load_scores():

    if os.path.exists(LEADERBOARD_FILE):

        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)["scores"]

    return []


def save_scores(new_score):

    scores = load_scores()

    scores.append(new_score)

    scores = sorted(
        scores,
        reverse=True
    )[:5]

    os.makedirs(DATA_DIR, exist_ok=True)

    with open(LEADERBOARD_FILE, "w") as f:

        json.dump(
            {"scores": scores},
            f
        )


# ---------------- INIT ----------------

pygame.init()

WIDTH = 390
HEIGHT = 600

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Flappy Python"
)

clock = pygame.time.Clock()

font = pygame.font.SysFont(
    "Arial",
    30,
    bold=True
)

font_small = pygame.font.SysFont(
    "Arial",
    20,
    bold=True
)

# ---------------- LOAD ASSETS ----------------

try:

    logo = pygame.image.load(
        os.path.join(
            IMG_DIR,
            "FlappyBird.png"
        )
    ).convert_alpha()

    img_bg_day = pygame.image.load(
        os.path.join(
            IMG_DIR,
            "background_day.png"
        )
    ).convert()

    img_bg_night = pygame.image.load(
        os.path.join(
            IMG_DIR,
            "background_night.png"
        )
    ).convert()

    img_bg_day = pygame.transform.scale(
        img_bg_day,
        (WIDTH, HEIGHT)
    )

    img_bg_night = pygame.transform.scale(
        img_bg_night,
        (WIDTH, HEIGHT)
    )

    img_ground = pygame.image.load(
        os.path.join(
            IMG_DIR,
            "ground.png"
        )
    ).convert_alpha()

    img_ground = pygame.transform.scale(
        img_ground,
        (WIDTH, 100)
    )

    # bird extension = .jpeg

    img_bird = pygame.image.load(
        os.path.join(
            IMG_DIR,
            "bird.jpeg"
        )
    ).convert()

    img_bird.set_colorkey(
        img_bird.get_at((0, 0))
    )

    img_bird = pygame.transform.scale(
        img_bird,
        (50, 60)
    )

    img_pipe = pygame.image.load(
        os.path.join(
            IMG_DIR,
            "pipe.png"
        )
    ).convert_alpha()

    img_pipe = pygame.transform.scale(
        img_pipe,
        (100, 600)
    )

    img_game_over = pygame.image.load(
        os.path.join(
            IMG_DIR,
            "game_over.png"
        )
    ).convert_alpha()

    img_game_over = pygame.transform.scale(
        img_game_over,
        (250, 150)
    )

    sfx_flap = pygame.mixer.Sound(
        os.path.join(
            SND_DIR,
            "battito.wav"
        )
    )

    sfx_death = pygame.mixer.Sound(
        os.path.join(
            SND_DIR,
            "defeat.wav"
        )
    )

    sfx_point = pygame.mixer.Sound(
        os.path.join(
            SND_DIR,
            "point.wav"
        )
    )

    pygame.mixer.music.load(
        os.path.join(
            SND_DIR,
            "musica.mp3"
        )
    )

    pygame.mixer.music.play(-1)

except Exception as e:

    print(f"Asset loading error: {e}")

    pygame.quit()

    raise SystemExit


# ---------------- CLASSES ----------------

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

        angle = max(
            -25,
            min(
                90,
                -self.vel * 4
            )
        )

        rotated = pygame.transform.rotate(
            img_bird,
            angle
        )

        rect = rotated.get_rect(
            center=(self.x, self.y)
        )

        screen.blit(rotated, rect)


class WorldManager:

    def __init__(self):

        self.bg_x = 0

        self.ground_x = 0

        self.bg_speed = 1

        self.ground_speed = 3

    def update(self, active):

        if active:

            self.bg_x -= self.bg_speed

            self.ground_x -= self.ground_speed

            if self.bg_x <= -WIDTH:
                self.bg_x = 0

            if self.ground_x <= -WIDTH:
                self.ground_x = 0

    def draw(self, daytime):

        img_bg = (
            img_bg_day
            if daytime
            else img_bg_night
        )

        screen.blit(
            img_bg,
            (self.bg_x, 0)
        )

        screen.blit(
            img_bg,
            (self.bg_x + WIDTH, 0)
        )

    def draw_ground(self):

        screen.blit(
            img_ground,
            (self.ground_x, 500)
        )

        screen.blit(
            img_ground,
            (self.ground_x + WIDTH, 500)
        )


class PipeManager:

    def __init__(self):

        self.pipes = []

        self.timer = 0

        self.score = 0

    def spawn(self):

        h = random.randint(150, 350)

        gap = 165

        self.pipes.append({
            "x": WIDTH + 50,
            "y": h,
            "type": "top",
            "passed": False
        })

        self.pipes.append({
            "x": WIDTH + 50,
            "y": h + gap,
            "type": "bottom"
        })

    def update(self, active):

        if active:

            for p in self.pipes:
                p["x"] -= 3

            self.pipes = [
                p for p in self.pipes
                if p["x"] > -100
            ]


class Menu:

    def __init__(self):

        self.timer = 0

        self.logo = pygame.transform.scale(
            logo,
            (300, 100)
        )

    def update(self):

        self.timer += 1

    def draw_button(
        self,
        text,
        y,
        color
    ):

        rect = pygame.Rect(
            WIDTH // 2 - 130,
            y,
            260,
            50
        )

        pygame.draw.rect(
            screen,
            color,
            rect,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            rect,
            2,
            border_radius=12
        )

        txt = font.render(
            text,
            True,
            (255, 255, 255)
        )

        screen.blit(
            txt,
            txt.get_rect(center=rect.center)
        )

        return rect

    def draw(self, daytime):

        world.draw(daytime)

        world.draw_ground()

        screen.blit(
            self.logo,
            self.logo.get_rect(
                center=(WIDTH // 2, 110)
            )
        )

        bird_y = 230 + math.sin(
            self.timer * 0.05
        ) * 15

        angle = math.sin(
            self.timer * 0.05
        ) * 15

        rotated = pygame.transform.rotate(
            img_bird,
            angle
        )

        screen.blit(
            rotated,
            rotated.get_rect(
                center=(WIDTH // 2, bird_y)
            )
        )

        r_play = self.draw_button(
            "▶ PLAY",
            320,
            (34, 139, 34)
        )

        r_leaderboard = self.draw_button(
            "LEADERBOARD",
            390,
            (30, 100, 180)
        )

        r_credits = self.draw_button(
            "CREDITS",
            460,
            (100, 100, 100)
        )

        return (
            r_play,
            r_leaderboard,
            r_credits
        )


class LeaderboardScreen:

    def draw(self, daytime):

        world.draw(daytime)

        world.draw_ground()

        panel = pygame.Surface(
            (340, 340),
            pygame.SRCALPHA
        )

        panel.fill((0, 0, 0, 170))

        screen.blit(panel, (25, 110))

        title = font.render(
            "LEADERBOARD",
            True,
            (255, 220, 0)
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 140)
            )
        )

        scores = load_scores()

        if scores:

            for i, score in enumerate(scores):

                txt = font.render(
                    f"{i+1}. {score}",
                    True,
                    (255, 255, 255)
                )

                screen.blit(
                    txt,
                    txt.get_rect(
                        center=(
                            WIDTH // 2,
                            210 + i * 50
                        )
                    )
                )

        else:

            txt = font_small.render(
                "No scores yet!",
                True,
                (200, 200, 200)
            )

            screen.blit(
                txt,
                txt.get_rect(
                    center=(WIDTH // 2, 280)
                )
            )

        return self.draw_back()

    def draw_back(self):

        rect = pygame.Rect(
            WIDTH // 2 - 100,
            470,
            200,
            45
        )

        pygame.draw.rect(
            screen,
            (100, 100, 100),
            rect,
            border_radius=10
        )

        txt = font.render(
            "← BACK",
            True,
            (255, 255, 255)
        )

        screen.blit(
            txt,
            txt.get_rect(center=rect.center)
        )

        return rect


class CreditsScreen:

    def draw(self, daytime):

        world.draw(daytime)

        world.draw_ground()

        panel = pygame.Surface(
            (340, 320),
            pygame.SRCALPHA
        )

        panel.fill((0, 0, 0, 160))

        screen.blit(panel, (25, 120))

        title = font.render(
            "CREDITS",
            True,
            (255, 220, 0)
        )

        screen.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 150)
            )
        )

        lines = [
            "Built with Python",
            "and pygame",
            "",
            "Personal learning project",
            "",
            "Developer:",
            "Francesco Falone"
        ]

        for i, line in enumerate(lines):

            txt = font_small.render(
                line,
                True,
                (255, 255, 255)
            )

            screen.blit(
                txt,
                txt.get_rect(
                    center=(
                        WIDTH // 2,
                        210 + i * 30
                    )
                )
            )

        return self.draw_back()

    def draw_back(self):

        rect = pygame.Rect(
            WIDTH // 2 - 100,
            470,
            200,
            45
        )

        pygame.draw.rect(
            screen,
            (100, 100, 100),
            rect,
            border_radius=10
        )

        txt = font.render(
            "← BACK",
            True,
            (255, 255, 255)
        )

        screen.blit(
            txt,
            txt.get_rect(center=rect.center)
        )

        return rect


# ---------------- SETUP ----------------

bird = Bird()

world = WorldManager()

pipes = PipeManager()

menu = Menu()

leaderboard = LeaderboardScreen()

credits_screen = CreditsScreen()

state = "menu"

# ---------------- LOOP ----------------

while True:

    dt = clock.tick(60)

    hour = datetime.datetime.now().hour

    daytime = 6 <= hour < 19

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()

            raise SystemExit

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
        ):

            if state == "menu":

                state = "game"

            elif state == "game":

                if bird.active:

                    bird.vel = -9

                    sfx_flap.play()

            elif state == "game_over":

                bird = Bird()

                world = WorldManager()

                pipes = PipeManager()

                state = "game"

        if event.type == pygame.MOUSEBUTTONDOWN:

            if state == "menu":

                r_play, r_lb, r_credits = menu.draw(daytime)

                if r_play.collidepoint(event.pos):
                    state = "game"

                elif r_lb.collidepoint(event.pos):
                    state = "leaderboard"

                elif r_credits.collidepoint(event.pos):
                    state = "credits"

            elif state == "leaderboard":

                if leaderboard.draw(daytime).collidepoint(event.pos):
                    state = "menu"

            elif state == "credits":

                if credits_screen.draw(daytime).collidepoint(event.pos):
                    state = "menu"

    # ---------- GAME ----------

    if state == "menu":

        menu.update()

        world.update(True)

    elif state == "game":

        world.update(bird.active)

        bird.update()

        pipes.timer += dt

        if pipes.timer > 1500:

            pipes.spawn()

            pipes.timer = 0

        pipes.update(bird.active)

        b_hit = pygame.Rect(
            bird.x - 12,
            bird.y - 15,
            24,
            30
        )

        for p in pipes.pipes:

            if p["type"] == "top":

                p_hit = pygame.Rect(
                    p["x"] - 25,
                    0,
                    50,
                    p["y"]
                )

                if (
                    p["x"] < bird.x
                    and not p["passed"]
                ):

                    pipes.score += 1

                    p["passed"] = True

                    sfx_point.play()

            else:

                p_hit = pygame.Rect(
                    p["x"] - 25,
                    p["y"],
                    50,
                    HEIGHT - p["y"]
                )

            if (
                b_hit.colliderect(p_hit)
                and bird.active
            ):

                bird.active = False

                sfx_death.play()

                save_scores(pipes.score)

        if bird.y < 0 or bird.y + 15 > 500:

            if bird.active:

                bird.active = False

                sfx_death.play()

                save_scores(pipes.score)

        if not bird.active:

            state = "game_over"

    # ---------- DRAW ----------

    if state == "menu":

        menu.draw(daytime)

    elif state == "leaderboard":

        leaderboard.draw(daytime)

    elif state == "credits":

        credits_screen.draw(daytime)

    elif state in ("game", "game_over"):

        world.draw(daytime)

        for p in pipes.pipes:

            if p["type"] == "top":

                img = pygame.transform.flip(
                    img_pipe,
                    False,
                    True
                )

                screen.blit(
                    img,
                    img.get_rect(
                        midbottom=(p["x"], p["y"])
                    )
                )

            else:

                screen.blit(
                    img_pipe,
                    img_pipe.get_rect(
                        midtop=(p["x"], p["y"])
                    )
                )

        world.draw_ground()

        bird.draw()

        score_txt = font.render(
            f"Score: {pipes.score}",
            True,
            (255, 255, 255)
        )

        screen.blit(score_txt, (20, 20))

        if state == "game_over":

            screen.blit(
                img_game_over,
                (WIDTH // 2 - 125, 120)
            )

            retry = font.render(
                "SPACE TO RESTART",
                True,
                (0, 0, 0)
            )

            screen.blit(
                retry,
                retry.get_rect(
                    center=(WIDTH // 2, 300)
                )
            )

    pygame.display.update()

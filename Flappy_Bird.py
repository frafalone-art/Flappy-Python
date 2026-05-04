import pygame
import random
import datetime
import math
import json
import os

# --- LEADERBOARD ---
def carica_punteggi():
    if os.path.exists("leaderboard.json"):
        with open("leaderboard.json", "r") as f:
            return json.load(f)["scores"]
    else:
        return []

def salva_punteggi(nuovo_score):
    scores = carica_punteggi()
    scores.append(nuovo_score)
    scores = sorted(scores, reverse=True)[:5]
    with open("leaderboard.json", "w") as f:
        json.dump({"scores": scores}, f)

# --- INIZIALIZZAZIONE ---
pygame.init()
WIDTH, HEIGHT = 390, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Python")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30, bold=True)
font_small = pygame.font.SysFont("Arial", 20, bold=True)

# --- CARICAMENTO ASSET ---
try:
    logo = pygame.image.load("FlappyBird.png").convert_alpha()
    img_sfondo_g = pygame.image.load("Sfondo.png").convert()
    img_sfondo_n = pygame.image.load("notte.png").convert()
    img_sfondo_g = pygame.transform.scale(img_sfondo_g, (WIDTH, HEIGHT))
    img_sfondo_n = pygame.transform.scale(img_sfondo_n, (WIDTH, HEIGHT))

    img_pavimento = pygame.image.load("Pavimento.png").convert_alpha()
    img_pavimento = pygame.transform.scale(img_pavimento, (WIDTH, 100))

    img_uccello = pygame.image.load("uccelo.jpeg").convert()
    img_uccello.set_colorkey(img_uccello.get_at((0, 0)))
    img_uccello = pygame.transform.scale(img_uccello, (50, 60))

    img_tubo = pygame.transform.scale(pygame.image.load("Tubo verticale.png").convert_alpha(), (100, 600))
    game_over_img = pygame.transform.scale(pygame.image.load("Game Over.png").convert_alpha(), (250, 150))

    battito = pygame.mixer.Sound("battito.wav")
    sconfitta = pygame.mixer.Sound("sconfitta.wav")
    punto = pygame.mixer.Sound("punto.wav")
    pygame.mixer.music.load("musica.mp3")
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"Errore: {e}"); pygame.quit(); exit()


# --- CLASSI ---

class Uccello:
    def __init__(self):
        self.x, self.y = 100, 300
        self.vel = 0
        self.active = True

    def aggiorna(self):
        if self.active:
            self.vel += 0.5
            self.y += self.vel

    def disegna(self):
        angolo = max(-25, min(90, -self.vel * 4))
        img_rot = pygame.transform.rotate(img_uccello, angolo)
        screen.blit(img_rot, img_rot.get_rect(center=(self.x, self.y)))


class GestoreMondo:
    def __init__(self):
        self.sfondo_x = 0
        self.pavimento_x = 0
        self.vel_sfondo = 1
        self.vel_pavimento = 3

    def aggiorna(self, attivo):
        if attivo:
            self.sfondo_x -= self.vel_sfondo
            self.pavimento_x -= self.vel_pavimento
            if self.sfondo_x <= -WIDTH: self.sfondo_x = 0
            if self.pavimento_x <= -WIDTH: self.pavimento_x = 0

    def disegna(self, giorno):
        img_sfondo = img_sfondo_g if giorno else img_sfondo_n
        screen.blit(img_sfondo, (self.sfondo_x, 0))
        screen.blit(img_sfondo, (self.sfondo_x + WIDTH, 0))

    def disegna_pavimento(self):
        screen.blit(img_pavimento, (self.pavimento_x, 500))
        screen.blit(img_pavimento, (self.pavimento_x + WIDTH, 500))


class GestoreTubi:
    def __init__(self):
        self.lista = []
        self.timer = 0
        self.score = 0

    def spawn(self):
        h = random.randint(150, 350); gap = 165
        self.lista.append({'x': WIDTH + 50, 'y': h, 'tipo': 'su', 'superato': False})
        self.lista.append({'x': WIDTH + 50, 'y': h + gap, 'tipo': 'giu'})

    def aggiorna(self, attivo):
        if attivo:
            for t in self.lista: t['x'] -= 3
            self.lista = [t for t in self.lista if t['x'] > -100]


class Menu:
    def __init__(self):
        self.timer = 0
        self.logo = pygame.transform.scale(logo, (300, 100))

    def aggiorna(self):
        self.timer += 1

    def disegna_pulsante(self, testo, y, colore):
        rect = pygame.Rect(WIDTH // 2 - 130, y, 260, 50)
        pygame.draw.rect(screen, colore, rect, border_radius=12)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=12)
        txt = font.render(testo, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=rect.center))
        return rect

    def disegna(self, giorno):
        mondo.disegna(giorno)
        mondo.disegna_pavimento()

        screen.blit(self.logo, self.logo.get_rect(center=(WIDTH // 2, 110)))

        uccello_y = 230 + math.sin(self.timer * 0.05) * 15
        angolo = math.sin(self.timer * 0.05) * 15
        img_rot = pygame.transform.rotate(img_uccello, angolo)
        screen.blit(img_rot, img_rot.get_rect(center=(WIDTH // 2, uccello_y)))

        r_gioca       = self.disegna_pulsante("  GIOCA",    320, (34, 139, 34))
        r_personaggi  = self.disegna_pulsante("PERSONAGGI",  385, (30, 100, 180))
        r_leaderboard = self.disegna_pulsante("LEADERBOARD", 450, (30, 100, 180))
        r_crediti     = self.disegna_pulsante("CREDITI",     515, (100, 100, 100))

        return r_gioca, r_personaggi, r_leaderboard, r_crediti


class SchermataLeaderboard:
    MEDAGLIE = ["1", "2", "3", "4.", "5."]
    COLORI   = [
        (255, 215,   0),  # oro
        (192, 192, 192),  # argento
        (205, 127,  50),  # bronzo
        (255, 255, 255),  # bianco
        (255, 255, 255),
    ]

    def disegna(self, giorno):
        mondo.disegna(giorno)
        mondo.disegna_pavimento()

        pannello = pygame.Surface((340, 340), pygame.SRCALPHA)
        pannello.fill((0, 0, 0, 170))
        screen.blit(pannello, (25, 110))

        titolo = font.render("  LEADERBOARD", True, (255, 220, 0))
        screen.blit(titolo, titolo.get_rect(center=(WIDTH // 2, 140)))

        scores = carica_punteggi()
        if scores:
            for i, score in enumerate(scores):
                colore  = self.COLORI[i]
                medaglia = self.MEDAGLIE[i]
                riga = font.render(f"{medaglia}  {score}", True, colore)
                screen.blit(riga, riga.get_rect(center=(WIDTH // 2, 200 + i * 50)))
        else:
            vuoto = font_small.render("Nessun punteggio ancora!", True, (200, 200, 200))
            screen.blit(vuoto, vuoto.get_rect(center=(WIDTH // 2, 280)))

        rect_back = pygame.Rect(WIDTH // 2 - 100, 460, 200, 45)
        pygame.draw.rect(screen, (100, 100, 100), rect_back, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), rect_back, 2, border_radius=10)
        back_txt = font.render("← INDIETRO", True, (255, 255, 255))
        screen.blit(back_txt, back_txt.get_rect(center=rect_back.center))
        return rect_back


class SchermataCrediti:
    def disegna(self, giorno):
        mondo.disegna(giorno)
        mondo.disegna_pavimento()

        pannello = pygame.Surface((340, 320), pygame.SRCALPHA)
        pannello.fill((0, 0, 0, 160))
        screen.blit(pannello, (25, 120))

        titolo = font.render("CREDITI", True, (255, 220, 0))
        screen.blit(titolo, titolo.get_rect(center=(WIDTH // 2, 150)))

        righe = [
            "Sviluppato con Python",
            "e pygame",
            "",
            "Grafica: asset custom",
            "Musica: asset custom",
            "",
            "Un progetto personale",
            "per imparare a programmare",
            "Dev: Francesco Falone",
        ]
        for i, riga in enumerate(righe):
            txt = font_small.render(riga, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, 200 + i * 27)))

        rect_back = pygame.Rect(WIDTH // 2 - 100, 460, 200, 45)
        pygame.draw.rect(screen, (100, 100, 100), rect_back, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), rect_back, 2, border_radius=10)
        back_txt = font.render("← INDIETRO", True, (255, 255, 255))
        screen.blit(back_txt, back_txt.get_rect(center=rect_back.center))
        return rect_back


# --- SETUP ---
bird = Uccello()
mondo = GestoreMondo()
tubi = GestoreTubi()
menu = Menu()
leaderboard = SchermataLeaderboard()
crediti = SchermataCrediti()
stato = "menu"  # "menu" | "gioco" | "game_over" | "leaderboard" | "crediti"

# --- LOOP PRINCIPALE ---
while True:
    dt = clock.tick(60)
    ora = datetime.datetime.now().hour
    giorno = 6 <= ora < 19

    # --- EVENTI ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if stato == "menu":
                stato = "gioco"
            elif stato == "gioco":
                if bird.active:
                    bird.vel = -9
                    battito.play()
            elif stato == "game_over":
                bird = Uccello()
                mondo = GestoreMondo()
                tubi = GestoreTubi()
                stato = "gioco"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if stato == "menu":
                r_gioca, r_personaggi, r_lb, r_crediti_btn = menu.disegna(giorno)
                if r_gioca.collidepoint(event.pos):
                    stato = "gioco"
                elif r_lb.collidepoint(event.pos):
                    stato = "leaderboard"
                elif r_crediti_btn.collidepoint(event.pos):
                    stato = "crediti"
            elif stato == "leaderboard":
                rect_back = leaderboard.disegna(giorno)
                if rect_back.collidepoint(event.pos):
                    stato = "menu"
            elif stato == "crediti":
                rect_back = crediti.disegna(giorno)
                if rect_back.collidepoint(event.pos):
                    stato = "menu"

    # --- LOGICA ---
    if stato == "menu":
        menu.aggiorna()
        mondo.aggiorna(True)

    elif stato == "gioco":
        pygame.mixer.music.unpause()
        mondo.aggiorna(bird.active)
        bird.aggiorna()
        tubi.timer += dt
        if tubi.timer > 1500:
            tubi.spawn()
            tubi.timer = 0
        tubi.aggiorna(bird.active)

        b_hit = pygame.Rect(bird.x - 12, bird.y - 15, 24, 30)
        for t in tubi.lista:
            if t['tipo'] == 'su':
                t_hit = pygame.Rect(t['x'] - 25, 0, 50, t['y'])
                if t['x'] < bird.x and not t['superato']:
                    tubi.score += 1
                    t['superato'] = True
                    punto.play()
            else:
                t_hit = pygame.Rect(t['x'] - 25, t['y'], 50, HEIGHT - t['y'])

            if b_hit.colliderect(t_hit) and bird.active:
                bird.active = False
                sconfitta.play()
                salva_punteggi(tubi.score)

        if bird.y < 0 or bird.y + 15 > 500:
            if bird.active:
                bird.active = False
                sconfitta.play()
                salva_punteggi(tubi.score)

        if not bird.active:
            stato = "game_over"
            pygame.mixer.music.pause()

    # --- DISEGNO ---
    if stato == "menu":
        menu.disegna(giorno)

    elif stato == "leaderboard":
        leaderboard.disegna(giorno)

    elif stato == "crediti":
        crediti.disegna(giorno)

    elif stato in ("gioco", "game_over"):
        mondo.disegna(giorno)

        for t in tubi.lista:
            if t['tipo'] == 'su':
                img = pygame.transform.flip(img_tubo, False, True)
                screen.blit(img, img.get_rect(midbottom=(t['x'], t['y'])))
            else:
                screen.blit(img_tubo, img_tubo.get_rect(midtop=(t['x'], t['y'])))

        mondo.disegna_pavimento()
        bird.disegna()

        punti = font.render(f"Punti: {tubi.score}", True, (255, 255, 255))
        screen.blit(punti, (20, 20))

        if stato == "game_over":
            screen.blit(game_over_img, (WIDTH // 2 - 125, HEIGHT // 2 - 250))

            msg = font.render(f"SCORE: {tubi.score}", True, (0, 0, 0))
            screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80)))

            # Record in oro se hai appena battuto il record, nero altrimenti
            scores = carica_punteggi()
            record = scores[0] if scores else 0
            colore_record = (255, 215, 0) if tubi.score == record else (0, 0, 0)
            rec_txt = font.render(f" RECORD: {record}", True, colore_record)
            screen.blit(rec_txt, rec_txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

            retry = font.render("SPAZIO PER RESTART", True, (0, 0, 0))
            screen.blit(retry, retry.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))

    pygame.display.update()
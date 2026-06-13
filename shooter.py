import pygame
import random
import sys
import math

pygame.init()

WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

WHITE   = (255, 255, 255)
BLACK   = (5, 5, 20)
YELLOW  = (255, 230, 0)
RED     = (255, 60, 60)
ORANGE  = (255, 140, 0)
CYAN    = (0, 220, 255)
GREEN   = (60, 255, 100)
PURPLE  = (180, 60, 255)
GREY    = (120, 120, 120)

font_big  = pygame.font.Font(None, 64)
font_med  = pygame.font.Font(None, 38)
font_sm   = pygame.font.Font(None, 26)

# Stars background
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(120)]


def draw_stars(scroll):
    for i, (x, y, size) in enumerate(stars):
        ny = (y + scroll) % HEIGHT
        stars[i] = (x, ny, size)
        brightness = 100 + size * 50
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, int(ny)), size)


def draw_ship(surface, x, y, color):
    pts = [
        (x, y - 22),
        (x - 14, y + 14),
        (x - 6,  y + 6),
        (x + 6,  y + 6),
        (x + 14, y + 14),
    ]
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.polygon(surface, WHITE, pts, 1)
    # engine glow
    pygame.draw.circle(surface, ORANGE, (x, y + 10), 5)


def draw_enemy(surface, x, y, etype, frame):
    if etype == 0:  # basic red saucer
        pygame.draw.ellipse(surface, RED,    (x-18, y-8, 36, 16))
        pygame.draw.ellipse(surface, ORANGE, (x-8,  y-14, 16, 12))
        pygame.draw.ellipse(surface, RED,    (x-18, y-8, 36, 16), 1)
    elif etype == 1:  # spinning triangle
        angle = frame * 3
        r = math.radians(angle)
        pts = []
        for i in range(3):
            a = r + math.radians(i * 120)
            pts.append((x + int(18 * math.cos(a)), y + int(18 * math.sin(a))))
        pygame.draw.polygon(surface, PURPLE, pts)
        pygame.draw.polygon(surface, WHITE,  pts, 1)
    elif etype == 2:  # boss diamond
        pygame.draw.polygon(surface, (255, 80, 0), [(x, y-26),(x+20,y),(x,y+26),(x-20,y)])
        pygame.draw.polygon(surface, YELLOW,       [(x, y-26),(x+20,y),(x,y+26),(x-20,y)], 2)


class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.randint(-10, 10)
        self.y = y + random.randint(-10, 10)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, 1)
        self.life = random.randint(20, 40)
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, int(255 * self.life / 40))
        c = tuple(min(255, v) for v in self.color)
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.size)


def explode(x, y, particles, color=ORANGE):
    for _ in range(22):
        particles.append(Particle(x, y, color))


def menu_screen():
    while True:
        screen.fill(BLACK)
        draw_stars(0.5)
        screen.blit(font_big.render("SPACE",   True, CYAN),   (WIDTH//2 - 90, 180))
        screen.blit(font_big.render("SHOOTER", True, YELLOW), (WIDTH//2 - 115, 248))
        screen.blit(font_med.render("Click or SPACE to Play", True, WHITE), (WIDTH//2 - 145, 360))
        screen.blit(font_sm.render("Arrow Keys = Move",      True, GREY),  (WIDTH//2 - 80, 430))
        screen.blit(font_sm.render("SPACE = Shoot",          True, GREY),  (WIDTH//2 - 60, 458))
        screen.blit(font_sm.render("Survive the waves!",     True, GREY),  (WIDTH//2 - 75, 486))
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return


def game_over_screen(score, wave):
    while True:
        screen.fill(BLACK)
        draw_stars(0.3)
        screen.blit(font_big.render("GAME OVER", True, RED),              (WIDTH//2 - 140, 220))
        screen.blit(font_med.render(f"Score: {score}",   True, YELLOW),   (WIDTH//2 - 80,  310))
        screen.blit(font_med.render(f"Wave:  {wave}",    True, CYAN),     (WIDTH//2 - 60,  356))
        screen.blit(font_med.render("SPACE = Restart",   True, WHITE),    (WIDTH//2 - 110, 430))
        screen.blit(font_med.render("Q     = Quit",      True, GREY),     (WIDTH//2 - 75,  476))
        pygame.display.flip()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: return True
                if event.key == pygame.K_q:     return False


def spawn_wave(wave):
    enemies = []
    count = 4 + wave
    has_boss = wave % 4 == 0 and wave > 0
    for i in range(count):
        etype = 1 if wave >= 3 and random.random() < 0.3 else 0
        x = random.randint(30, WIDTH - 30)
        y = random.randint(-300, -40)
        speed = 1.5 + wave * 0.3 + random.uniform(0, 0.5)
        hp = 1 + (wave // 3)
        enemies.append({"x": float(x), "y": float(y), "speed": speed,
                        "hp": hp, "etype": etype, "shoot_cd": random.randint(280, 500)})
    if has_boss:
        enemies.append({"x": float(WIDTH // 2), "y": -80.0, "speed": 0.8,
                        "etype": 2, "hp": 12 + wave * 2, "shoot_cd": 50, "dir": 1})
    return enemies


menu_screen()

while True:
    # ── game state ──────────────────────────────────────────
    px, py     = float(WIDTH // 2), float(HEIGHT - 80)
    player_hp  = 5
    score      = 0
    wave       = 1
    frame      = 0
    star_scroll = 0.0
    shoot_cd   = 0
    bullets    = []   # player bullets
    e_bullets  = []   # enemy bullets
    particles  = []
    enemies    = spawn_wave(wave)
    invincible = 0    # frames of invincibility after hit

    running = True
    while running:
        clock.tick(60)
        frame += 1
        star_scroll += 1.2

        # ── input ───────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        spd = 5
        if keys[pygame.K_LEFT]  and px > 20:         px -= spd
        if keys[pygame.K_RIGHT] and px < WIDTH - 20: px += spd
        if keys[pygame.K_UP]    and py > HEIGHT//2:  py -= spd
        if keys[pygame.K_DOWN]  and py < HEIGHT - 20: py += spd
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            bullets.append({"x": px, "y": py - 24})
            shoot_cd = 12

        shoot_cd = max(0, shoot_cd - 1)
        if invincible > 0: invincible -= 1

        # ── update bullets ──────────────────────────────────
        bullets  = [b for b in bullets  if b["y"] > -10]
        e_bullets = [b for b in e_bullets if 0 < b["y"] < HEIGHT + 10]
        for b in bullets:   b["y"] -= 9
        for b in e_bullets:
            b["x"] += b["vx"]
            b["y"] += b["vy"]

        # ── update enemies ──────────────────────────────────
        for e in enemies:
            e["y"] += e["speed"]
            if e.get("etype") == 2:  # boss sways
                e["x"] += e.get("dir", 1) * 1.2
                if e["x"] > WIDTH - 30 or e["x"] < 30:
                    e["dir"] = -e.get("dir", 1)

            e["shoot_cd"] -= 1
            if e["shoot_cd"] <= 0 and e["y"] > 0:
                e["shoot_cd"] = random.randint(280, 480)
                dx = px - e["x"]
                dy = py - e["y"]
                dist = max(1, math.hypot(dx, dy))
                speed_e = 1.8 if e.get("etype") == 2 else 1.3
                e_bullets.append({"x": e["x"], "y": e["y"],
                                   "vx": dx / dist * speed_e,
                                   "vy": dy / dist * speed_e})

        # ── bullet vs enemy ─────────────────────────────────
        dead_bullets = set()
        dead_enemies = set()
        for bi, b in enumerate(bullets):
            for ei, e in enumerate(enemies):
                if abs(b["x"] - e["x"]) < 20 and abs(b["y"] - e["y"]) < 20:
                    e["hp"] -= 1
                    dead_bullets.add(bi)
                    if e["hp"] <= 0:
                        explode(e["x"], e["y"], particles,
                                YELLOW if e.get("etype") == 2 else ORANGE)
                        pts = 30 if e.get("etype") == 2 else (20 if e.get("etype") == 1 else 10)
                        score += pts
                        dead_enemies.add(ei)
        bullets  = [b for i, b in enumerate(bullets)  if i not in dead_bullets]
        enemies  = [e for i, e in enumerate(enemies)  if i not in dead_enemies]

        # ── enemy/bullet vs player ───────────────────────────
        if invincible == 0:
            for e in enemies:
                if abs(e["x"] - px) < 22 and abs(e["y"] - py) < 22:
                    player_hp -= 1
                    invincible = 90
                    explode(px, py, particles, CYAN)
                    break
            for b in e_bullets:
                if abs(b["x"] - px) < 14 and abs(b["y"] - py) < 14:
                    player_hp -= 1
                    invincible = 60
                    explode(px, py, particles, CYAN)
                    e_bullets.remove(b)
                    break

        if player_hp <= 0:
            running = False

        # enemies off screen = lose a life
        for e in list(enemies):
            if e["y"] > HEIGHT + 40:
                enemies.remove(e)
                player_hp -= 1
                invincible = max(invincible, 30)

        # ── next wave ───────────────────────────────────────
        if not enemies:
            wave += 1
            score += wave * 50
            enemies = spawn_wave(wave)

        # ── particles ───────────────────────────────────────
        for p in particles: p.update()
        particles = [p for p in particles if p.life > 0]

        # ── draw ────────────────────────────────────────────
        screen.fill(BLACK)
        draw_stars(star_scroll)

        for p in particles: p.draw(screen)

        for b in bullets:
            pygame.draw.rect(screen, CYAN, (int(b["x"]) - 2, int(b["y"]) - 8, 4, 12))
            pygame.draw.rect(screen, WHITE, (int(b["x"]) - 1, int(b["y"]) - 10, 2, 4))

        for b in e_bullets:
            pygame.draw.circle(screen, RED, (int(b["x"]), int(b["y"])), 4)

        for e in enemies:
            draw_enemy(screen, int(e["x"]), int(e["y"]), e.get("etype", 0), frame)
            # hp bar for boss
            if e.get("etype") == 2:
                max_hp = 12 + wave * 2
                bar_w  = int(60 * e["hp"] / max_hp)
                pygame.draw.rect(screen, GREY,   (int(e["x"]) - 30, int(e["y"]) - 36, 60, 6))
                pygame.draw.rect(screen, YELLOW, (int(e["x"]) - 30, int(e["y"]) - 36, bar_w, 6))

        # player (blink when invincible)
        if invincible == 0 or (invincible // 6) % 2 == 0:
            draw_ship(screen, int(px), int(py), CYAN)

        # HUD
        screen.blit(font_med.render(f"Score: {score}", True, YELLOW), (8, 8))
        screen.blit(font_med.render(f"Wave: {wave}",   True, CYAN),   (8, 40))
        hearts = "♥ " * player_hp + "♡ " * (5 - player_hp)
        screen.blit(font_med.render(hearts, True, RED), (WIDTH - 130, 8))

        pygame.display.flip()

    explode(px, py, particles, CYAN)

    if not game_over_screen(score, wave):
        break


pygame.quit()
import pygame, sys, random, math
pygame.init()

W, H = 620, 520
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Tap! - Rhythm Clicker")
clock = pygame.time.Clock()

BIG  = pygame.font.Font(None, 72)
MED  = pygame.font.Font(None, 42)
SM   = pygame.font.Font(None, 28)
BG   = (12, 12, 28)
COLS = [(255,60,60),(0,210,255),(255,215,0),(80,255,130),(255,80,180),(160,80,255),(255,140,0)]

CR = 36          # circle radius
LIFE = 95        # frames before miss
SPAWN = 52       # frames between spawns

class Circle:
    def __init__(self, num):
        self.x   = random.randint(CR+40, W-CR-40)
        self.y   = random.randint(CR+70, H-CR-30)
        self.col = random.choice(COLS)
        self.num = num
        self.age = 0
        self.state = "alive"   # alive / hit / miss
        self.label = ""
        self.lt = 0

    def ring_r(self):
        t = min(1.0, self.age / LIFE)
        return int(CR * (2.6 - 1.6*t))

    def try_click(self, mx, my):
        if math.hypot(mx-self.x, my-self.y) > CR+24: return 0
        diff = abs(self.ring_r() - CR)
        if diff < 5:   pts, self.label = 300, "PERFECT!"
        elif diff < 14: pts, self.label = 150, "GREAT!"
        elif diff < 25: pts, self.label = 75,  "GOOD"
        else:           pts, self.label = 20,  "EARLY"
        self.state = "hit"; self.lt = 50; return pts

    def update(self):
        self.age += 1
        if self.lt > 0: self.lt -= 1
        if self.state == "alive" and self.age > LIFE + 15:
            self.state = "miss"; self.label = "MISS"; self.lt = 40

    def draw(self):
        if self.state == "miss" and self.lt <= 0: return
        fade = self.lt / 50 if self.state != "alive" else 1.0
        c = tuple(int(v * fade) for v in self.col)
        if self.state == "alive":
            pygame.draw.circle(screen, c, (self.x, self.y), CR)
            pygame.draw.circle(screen, (255,255,255), (self.x, self.y), CR, 2)
            rr = self.ring_r()
            closeness = 1 - abs(rr - CR) / (CR * 1.6)
            rc = tuple(int(a + (255-a)*closeness*0.6) for a in self.col)
            pygame.draw.circle(screen, rc, (self.x, self.y), rr, 3)
            n = SM.render(str(self.num), True, (255,255,255))
            screen.blit(n, (self.x-n.get_width()//2, self.y-n.get_height()//2))
        if self.lt > 0 and self.label:
            lc = (255,220,0) if "PERFECT" in self.label else \
                 (100,255,130) if "GREAT" in self.label else \
                 (200,220,255) if "GOOD" in self.label else \
                 (255,80,80)
            t = SM.render(self.label, True, lc)
            screen.blit(t, (self.x-t.get_width()//2, self.y-CR-28))

best = 0
while True:
    circles = []
    score = combo = num = spawn_t = 0
    misses = 0
    timer = 60 * 35  # 35 seconds

    # intro
    for _ in range(150):
        clock.tick(60)
        screen.fill(BG)
        screen.blit(BIG.render("TAP!", True, (0,210,255)),      (W//2-70,  H//2-90))
        screen.blit(MED.render("Click circles as the ring",True,(255,255,255)),(W//2-175,H//2-10))
        screen.blit(MED.render("shrinks to match them!",   True,(255,255,255)),(W//2-155,H//2+35))
        screen.blit(SM.render( "Click or key to start",    True,(160,160,210)),(W//2-95, H//2+90))
        if best: screen.blit(SM.render(f"Best: {best}",True,(255,215,0)),(W//2-45,H//2+120))
        pygame.display.flip()
        skip = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN): skip = True
        if skip: break

    while timer > 0:
        clock.tick(60)
        timer -= 1; spawn_t += 1

        # spawn
        if spawn_t >= SPAWN:
            spawn_t = 0; num += 1
            circles.append(Circle(num))

        # events
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                hit_any = False
                for c in sorted(circles, key=lambda c: c.num):
                    if c.state == "alive":
                        pts = c.try_click(mx, my)
                        if pts:
                            combo += 1
                            score += pts * (1 + combo//5)
                            hit_any = True; break
                if not hit_any:
                    combo = 0

        # update + track misses
        for c in circles:
            was = c.state
            c.update()
            if c.state == "miss" and was == "alive":
                misses += 1; combo = 0
        circles = [c for c in circles if not (c.state=="miss" and c.lt<=0)]

        # draw
        screen.fill(BG)
        for c in circles: c.draw()

        # HUD
        secs = timer // 60
        pygame.draw.rect(screen, (30,30,60), (10,10,W-20,34), border_radius=8)
        pygame.draw.rect(screen, (0,160,255),(10,10,int((W-20)*timer/(60*35)),34), border_radius=8)
        screen.blit(SM.render(f"{secs}s", True, (255,255,255)),              (W//2-14, 17))
        screen.blit(SM.render(f"Score: {score}", True, (255,220,0)),         (14, 52))
        screen.blit(SM.render(f"Combo: x{combo}", True, (80,255,130)),       (14, 76))
        screen.blit(SM.render(f"Misses: {misses}", True, (255,80,80)),       (W-130, 52))
        if best: screen.blit(SM.render(f"Best: {best}", True,(180,180,255)),(W-110, 76))
        pygame.display.flip()

    best = max(best, score)

    # result
    grade = "S" if misses==0 else "A" if misses<3 else "B" if misses<7 else "C"
    gc    = (255,220,0) if grade=="S" else (0,210,255) if grade=="A" else (80,255,130)
    for _ in range(300):
        clock.tick(60)
        screen.fill(BG)
        screen.blit(BIG.render(f"Grade: {grade}", True, gc),               (W//2-140, H//2-100))
        screen.blit(MED.render(f"Score:  {score}", True, (255,255,255)),   (W//2-100, H//2-20))
        screen.blit(MED.render(f"Misses: {misses}", True, (255,80,80)),    (W//2-100, H//2+30))
        screen.blit(SM.render( "Click or key to play again", True,(160,160,210)),(W//2-130,H//2+90))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN): _ = 300; break
        else: continue
        break

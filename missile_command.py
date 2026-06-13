import pygame, sys, random, math
pygame.init()

W, H = 640, 520
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Missile Command")
clock  = pygame.time.Clock()
F  = pygame.font.Font(None, 30)
BF = pygame.font.Font(None, 62)

GY       = H - 50
CITY_XS  = [80, 165, 250, 390, 475, 560]
SILO_XS  = [30, 320, 610]
AMMO_MAX = 10

def txt(s,c,x,y,fnt=F):
    t=fnt.render(s,True,c); screen.blit(t,(x-t.get_width()//2,y))

# ── game objects stored as plain lists ─────────────────────
# enemy:  [x, y, tx, ty, speed, alive, trail[]]
# pmiss:  [x, y, tx, ty, vx, vy, exploding, exp_r]
# expl:   [x, y, r, max_r]  (finished explosions still expanding)

while True:
    cities  = [True]*6
    ammo    = [AMMO_MAX]*3
    wave    = 1
    score   = 0
    enemies = []
    pmiss   = []
    spawn_t = 60

    def spawn_enemy():
        sx = float(random.randint(20, W-20))
        tx = float(random.choice(CITY_XS + SILO_XS))
        spd = 0.6 + wave*0.12 + random.uniform(0, 0.3)
        d   = math.hypot(tx-sx, GY)
        return [sx, 0.0, tx, float(GY), (tx-sx)/d*spd, GY/d*spd, True, []]

    quota    = 8   # enemies to spawn this wave
    spawned  = 0

    running = True
    while running:
        clock.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                if my >= GY: continue
                # find nearest silo that has ammo
                silos_with_ammo = [i for i in range(3) if ammo[i] > 0]
                if not silos_with_ammo: continue
                si = min(silos_with_ammo, key=lambda i: abs(SILO_XS[i]-mx))
                sx = float(SILO_XS[si])
                sy = float(GY - 25)
                d  = max(1, math.hypot(mx-sx, my-sy))
                vx, vy = (mx-sx)/d*9, (my-sy)/d*9
                pmiss.append([sx, sy, float(mx), float(my), vx, vy, False, 0.0])
                ammo[si] -= 1

        # spawn enemies
        spawn_t -= 1
        if spawn_t <= 0 and spawned < quota:
            enemies.append(spawn_enemy())
            spawned += 1
            spawn_t = max(18, 70 - wave*6)

        # move enemies
        for e in enemies:
            if not e[6]: continue
            e[7].append((int(e[0]), int(e[1])))
            if len(e[7]) > 20: e[7].pop(0)
            e[0] += e[4]; e[1] += e[5]
            if e[1] >= GY:
                e[6] = False
                for i,cx in enumerate(CITY_XS):
                    if abs(e[0]-cx) < 32: cities[i] = False
                for i,sx in enumerate(SILO_XS):
                    if abs(e[0]-sx) < 28: ammo[i] = 0

        # move player missiles
        for p in pmiss:
            if p[6]:  # exploding
                p[7] += 2.5
            else:
                p[0] += p[4]; p[1] += p[5]
                if math.hypot(p[0]-p[2], p[1]-p[3]) < 10:
                    p[6] = True  # start exploding

        # collision: player explosion hits enemy
        for p in pmiss:
            if not p[6]: continue
            er = p[7]
            for e in enemies:
                if e[6] and math.hypot(p[0]-e[0], p[1]-e[1]) < er + 5:
                    e[6] = False
                    score += 100 + wave*10
                    e[7].clear()

        # cleanup
        enemies = [e for e in enemies if e[6] or len(e[7])>0]
        for e in enemies:
            if not e[6] and e[7]: e[7].pop(0)
        pmiss = [p for p in pmiss if not (p[6] and p[7]>58)]

        # next wave — only when all enemies spawned and all dead
        if spawned >= quota and not any(e[6] for e in enemies):
            wave += 1; score += wave*300
            quota = 8 + wave*2; spawned = 0
            enemies = []; spawn_t = 90
            for i in range(3):
                ammo[i] = min(ammo[i]+6, AMMO_MAX)

        if not any(cities): running = False

        # ── draw ─────────────────────────────────────────────
        screen.fill((4, 4, 18))

        # static stars
        for i in range(80):
            sx2 = (i*97+13)%W; sy2 = (i*53+7)%(GY-10)
            pygame.draw.circle(screen,(80,80,110),(sx2,sy2),1)

        # enemy trails + missiles
        for e in enemies:
            for k,pt in enumerate(e[7]):
                t = k/max(1,len(e[7]))
                pygame.draw.circle(screen,(int(255*t),int(40*t),int(20*t)),pt,2)
            if e[6]:
                pygame.draw.circle(screen,(255,80,60),(int(e[0]),int(e[1])),5)

        # player missiles + explosions
        for p in pmiss:
            if p[6]:
                r = int(p[7])
                t = r/58
                c = (int(255*(1-t*0.5)), int(220*(1-t*0.7)), int(80*(1-t)))
                if r>0: pygame.draw.circle(screen, c, (int(p[0]),int(p[1])), r, 3)
                pygame.draw.circle(screen,(255,255,180),(int(p[0]),int(p[1])),max(1,r//3))
            else:
                pygame.draw.line(screen,(0,255,140),
                    (int(p[0]-p[4]),int(p[1]-p[5])),(int(p[0]),int(p[1])),2)
                pygame.draw.circle(screen,(200,255,160),(int(p[0]),int(p[1])),3)

        # ground
        pygame.draw.rect(screen,(20,45,20),(0,GY,W,H-GY))
        pygame.draw.line(screen,(50,160,50),(0,GY),(W,GY),2)

        # cities
        for i,cx in enumerate(CITY_XS):
            if cities[i]:
                pygame.draw.rect(screen,(60,120,200),(cx-18,GY-26,36,26))
                pygame.draw.rect(screen,(80,160,255),(cx-13,GY-36,10,11))
                pygame.draw.rect(screen,(80,160,255),(cx+3, GY-36,10,11))
            else:
                pygame.draw.rect(screen,(70,35,15),(cx-18,GY-10,36,10))

        # silos
        for i,sx in enumerate(SILO_XS):
            pygame.draw.polygon(screen,(90,90,110),[(sx,GY-28),(sx-14,GY),(sx+14,GY)])
            for j in range(ammo[i]):
                pygame.draw.rect(screen,(0,220,100),(sx-22+j*5,GY+4,4,8),border_radius=2)

        # cursor crosshair
        mx,my = pygame.mouse.get_pos()
        pygame.draw.line(screen,(0,200,80),(mx-10,my),(mx+10,my),1)
        pygame.draw.line(screen,(0,200,80),(mx,my-10),(mx,my+10),1)
        pygame.draw.circle(screen,(0,200,80),(mx,my),8,1)

        # HUD
        screen.blit(F.render(f"Score: {score}",True,(255,220,0)),(8,8))
        screen.blit(F.render(f"Wave: {wave}", True,(0,200,255)),(8,34))
        cities_left = sum(cities)
        screen.blit(F.render(f"Cities: {cities_left}",True,(100,200,255)),(W-130,8))
        txt("CLICK to fire",(120,120,160),W//2,8)

        pygame.display.flip()

    # game over screen
    while True:
        screen.fill((4,4,18))
        txt("GAME OVER",(255,60,60),W//2,180,BF)
        txt(f"Score: {score}",(255,220,0),W//2,270)
        txt(f"Wave reached: {wave}",(0,200,255),W//2,310)
        txt("SPACE = Play Again    Q = Quit",(180,180,200),W//2,380)
        pygame.display.flip(); clock.tick(60)
        quit_game = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE: quit_game = False; break
                if ev.key == pygame.K_q: pygame.quit(); sys.exit()
        else: continue
        break

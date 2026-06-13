import pygame, sys, random, math
pygame.init()
W, H = 500, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()
F = pygame.font.Font(None, 36)
stars = [(random.randint(0,W), random.randint(0,H)) for _ in range(100)]

def txt(s, c, x, y): t=F.render(s,True,c); screen.blit(t,(x-t.get_width()//2,y))
def ship(x, y, c):
    pygame.draw.polygon(screen, c, [(x,y-20),(x-13,y+13),(x+13,y+13)])
    pygame.draw.circle(screen, (255,140,0), (x, y+8), 5)

while True:
    px, py = W//2, H-70
    lives, score, wave = 5, 0, 1
    bullets, ebullets, enemies = [], [], []
    scd = inv = 0

    def spawn():
        return [{"x":float(random.randint(30,W-30)),"y":float(random.randint(-250,-30)),
                 "vy":1.5+wave*0.2,"scd":random.randint(120,220)} for _ in range(4+wave)]
    enemies = spawn()

    running = True
    while running:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and px>20:    px -= 5
        if keys[pygame.K_RIGHT] and px<W-20:  px += 5
        if keys[pygame.K_UP]    and py>H//2:  py -= 5
        if keys[pygame.K_DOWN]  and py<H-20:  py += 5
        if keys[pygame.K_SPACE] and scd<=0:   bullets.append([float(px),float(py)]); scd=12
        scd = max(0, scd-1); inv = max(0, inv-1)

        for b in bullets:  b[1] -= 10
        for b in ebullets: b[0]+=b[2]; b[1]+=b[3]
        bullets  = [b for b in bullets  if b[1]>0]
        ebullets = [b for b in ebullets if 0<b[1]<H]

        for e in enemies:
            e["y"] += e["vy"]
            e["scd"] -= 1
            if e["scd"]<=0 and e["y"]>0:
                dx,dy = px-e["x"], py-e["y"]; d=max(1,math.hypot(dx,dy))
                ebullets.append([e["x"],e["y"],dx/d*2.2,dy/d*2.2])
                e["scd"] = random.randint(120,220)

        dead_b, dead_e = set(), set()
        for bi,b in enumerate(bullets):
            for ei,e in enumerate(enemies):
                if abs(b[0]-e["x"])<18 and abs(b[1]-e["y"])<18:
                    dead_b.add(bi); dead_e.add(ei); score+=10
        bullets  = [b for i,b in enumerate(bullets)  if i not in dead_b]
        enemies  = [e for i,e in enumerate(enemies)  if i not in dead_e]

        if inv==0:
            if any(abs(b[0]-px)<14 and abs(b[1]-py)<14 for b in ebullets):
                lives-=1; inv=80; ebullets=[]
            if any(abs(e["x"]-px)<22 and abs(e["y"]-py)<22 for e in enemies):
                lives-=1; inv=80

        enemies = [e for e in enemies if e["y"]<H+30]
        if not enemies: wave+=1; score+=wave*50; enemies=spawn()
        if lives<=0: running=False

        # draw
        screen.fill((5,5,20))
        for sx,sy in stars: pygame.draw.circle(screen,(120,120,140),(sx,(sy+2)%H),1); stars[stars.index((sx,sy))]=(sx,(sy+2)%H)
        for b in bullets:  pygame.draw.rect(screen,(0,220,255),(int(b[0])-2,int(b[1])-8,4,10))
        for b in ebullets: pygame.draw.circle(screen,(255,60,60),(int(b[0]),int(b[1])),4)
        for e in enemies:
            pygame.draw.ellipse(screen,(220,60,60),(int(e["x"])-16,int(e["y"])-7,32,14))
            pygame.draw.ellipse(screen,(255,120,0),(int(e["x"])-7,int(e["y"])-12,14,10))
        if inv==0 or (inv//6)%2==0: ship(int(px),int(py),(0,210,255))
        screen.blit(F.render(f"Score:{score}",True,(255,220,0)),(8,8))
        screen.blit(F.render("♥ "*lives,True,(255,60,60)),(W-160,8))
        screen.blit(F.render(f"Wave:{wave}",True,(0,210,255)),(8,38))
        pygame.display.flip()

    while True:
        screen.fill((5,5,20))
        txt("GAME OVER",(255,60,60),W//2,220); txt(f"Score: {score}",(255,220,0),W//2,290)
        txt("SPACE = Restart  Q = Quit",(200,200,200),W//2,360)
        pygame.display.flip(); clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key==pygame.K_SPACE: break
                if e.key==pygame.K_q: pygame.quit(); sys.exit()
        else: continue
        break

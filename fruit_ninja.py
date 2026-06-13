import pygame, sys, random, math
pygame.init()

W, H = 600, 650
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Fruit Ninja")
clock = pygame.time.Clock()
BF = pygame.font.Font(None, 80)
F  = pygame.font.Font(None, 40)
SM = pygame.font.Font(None, 28)

FRUITS = [
    {"col": (50,180,50),  "inn": (220,50,70),   "r": 34},
    {"col": (255,130,0),  "inn": (255,200,60),  "r": 28},
    {"col": (210,30,30),  "inn": (255,160,160), "r": 26},
    {"col": (240,220,0),  "inn": (255,240,120), "r": 24},
    {"col": (130,50,190), "inn": (190,120,255), "r": 22},
]

def seg_circle(ax,ay,bx,by,cx,cy,r):
    dx,dy=bx-ax,by-ay; fx,fy=ax-cx,ay-cy
    a=dx*dx+dy*dy
    if a==0: return False
    b=2*(fx*dx+fy*dy); c=fx*fx+fy*fy-r*r
    d=b*b-4*a*c
    if d<0: return False
    sq=math.sqrt(d)
    return 0<=(-b-sq)/(2*a)<=1 or 0<=(-b+sq)/(2*a)<=1

def draw_fruit(x,y,r,col,inn,angle=0):
    ix,iy=int(x),int(y)
    pygame.draw.circle(screen,col,(ix,iy),r)
    pygame.draw.circle(screen,inn,(ix,iy),r-7)
    pygame.draw.circle(screen,(255,255,255),(ix,iy),r,2)
    # shine
    pygame.draw.circle(screen,(255,255,255),(ix-r//3,iy-r//3),r//5)

def draw_half(x,y,r,col,inn,side,angle):
    s=pygame.Surface((r*2+4,r*2+4),pygame.SRCALPHA)
    cx=r+2; cy=r+2
    pygame.draw.circle(s,col,(cx,cy),r)
    pygame.draw.circle(s,inn,(cx,cy),r-7)
    pygame.draw.circle(s,(255,255,255),(cx,cy),r,2)
    # mask one side
    mask=pygame.Surface((r*2+4,r*2+4),pygame.SRCALPHA)
    mask.fill((0,0,0,0))
    if side=='L': pygame.draw.rect(mask,(0,0,0,255),(cx,0,r+4,r*2+4))
    else:         pygame.draw.rect(mask,(0,0,0,255),(0,0,cx,r*2+4))
    s.blit(mask,(0,0),special_flags=pygame.BLEND_RGBA_MIN)
    rot=pygame.transform.rotate(s,angle)
    screen.blit(rot,(int(x)-rot.get_width()//2,int(y)-rot.get_height()//2))

def splash(x,y,col,particles):
    for _ in range(14):
        a=random.uniform(0,2*math.pi); spd=random.uniform(2,7)
        particles.append({"x":float(x),"y":float(y),"vx":math.cos(a)*spd,
                          "vy":math.sin(a)*spd-3,"col":col,"life":30})

best=0
while True:
    fruits=[]; halves=[]; particles=[]; blade=[]
    score=0; misses=0; combo=0; combo_t=0
    spawn_t=60; slicing=False

    while misses<3:
        clock.tick(60)
        mx,my=pygame.mouse.get_pos()
        prev=(blade[-1] if blade else None)

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN: slicing=True; blade.clear()
            if ev.type==pygame.MOUSEBUTTONUP:   slicing=False; blade.clear()

        if slicing: blade.append((mx,my))
        if len(blade)>14: blade.pop(0)

        # spawn
        spawn_t-=1
        if spawn_t<=0:
            ft=random.choice(FRUITS)
            is_bomb=random.random()<0.15
            sx=random.randint(80,W-80)
            vx=random.uniform(-3,3)
            vy=random.uniform(-16,-11)
            fruits.append({"x":float(sx),"y":float(H+ft["r"]),"vx":vx,"vy":vy,
                           "r":ft["r"],"col":ft["col"],"inn":ft["inn"],
                           "bomb":is_bomb,"rot":0,"rs":random.uniform(-3,3)})
            spawn_t=max(25,70-score//3)

        # move fruits
        for f in fruits:
            f["x"]+=f["vx"]; f["y"]+=f["vy"]; f["vy"]+=0.4; f["rot"]+=f["rs"]

        # slice detection
        sliced=set()
        if slicing and prev and blade:
            px,py=prev
            for i,f in enumerate(fruits):
                if f.get("sliced"): continue
                if seg_circle(px,py,mx,my,f["x"],f["y"],f["r"]):
                    f["sliced"]=True
                    sliced.add(i)
                    if f["bomb"]:
                        misses=3; break
                    combo+=1; combo_t=60
                    pts=10*max(1,combo//2)
                    score+=pts
                    splash(f["x"],f["y"],f["col"],particles)
                    # two halves
                    for sd,vxd in [('L',-3),('R',3)]:
                        halves.append({"x":f["x"],"y":f["y"],"vx":vxd+f["vx"],
                                       "vy":f["vy"]-2,"r":f["r"],"col":f["col"],
                                       "inn":f["inn"],"side":sd,"angle":f["rot"],"life":55})

        # missed fruits (fell off bottom)
        for f in fruits:
            if f["y"]>H+f["r"]+10 and not f.get("sliced") and not f["bomb"]:
                misses+=1; combo=0

        fruits=[f for f in fruits if f["y"]<=H+f["r"]+10 and not f.get("sliced")]
        for h in halves: h["x"]+=h["vx"]; h["y"]+=h["vy"]; h["vy"]+=0.45; h["life"]-=1; h["angle"]+=3
        halves=[h for h in halves if h["life"]>0]
        for p in particles: p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=0.3; p["life"]-=1
        particles=[p for p in particles if p["life"]>0]
        if combo_t>0: combo_t-=1
        else: combo=0

        # ── draw ──────────────────────────────────────────────
        screen.fill((15,5,30))
        # gradient bg
        for i in range(0,H,4):
            t=i/H
            c=(int(15+t*20),int(5+t*10),int(30+t*30))
            pygame.draw.line(screen,c,(0,i),(W,i))

        for h in halves:
            draw_half(h["x"],h["y"],h["r"],h["col"],h["inn"],h["side"],h["angle"])
        for p in particles:
            t=p["life"]/30
            c=tuple(int(v*t) for v in p["col"])
            pygame.draw.circle(screen,c,(int(p["x"]),int(p["y"])),max(1,int(4*t)))
        for f in fruits:
            if f["bomb"]:
                pygame.draw.circle(screen,(20,20,20),(int(f["x"]),int(f["y"])),f["r"])
                pygame.draw.circle(screen,(60,60,60),(int(f["x"]),int(f["y"])),f["r"],3)
                pygame.draw.circle(screen,(255,80,0),(int(f["x"]),int(f["y"]-f["r"])),5)
                screen.blit(SM.render("BOMB",True,(255,60,60)),(int(f["x"])-22,int(f["y"])-8))
            else:
                draw_fruit(f["x"],f["y"],f["r"],f["col"],f["inn"],f["rot"])

        # blade trail
        if len(blade)>1:
            for i in range(1,len(blade)):
                t=i/len(blade)
                c=(int(255*t),int(255*t),int(200*t))
                w=max(1,int(t*4))
                pygame.draw.line(screen,c,blade[i-1],blade[i],w)
            pygame.draw.circle(screen,(255,255,255),blade[-1],3)

        # HUD
        screen.blit(F.render(f"Score: {score}",True,(255,220,0)),(8,8))
        lives_str="❤ "*( 3-misses)+"🖤"*misses
        screen.blit(SM.render(lives_str,True,(255,80,80)),(W-160,12))
        if combo>1 and combo_t>0:
            cs=BF.render(f"x{combo} COMBO!",True,(255,220,0))
            cs.set_alpha(min(255,combo_t*6))
            screen.blit(cs,(W//2-cs.get_width()//2,H//2-60))
        screen.blit(SM.render("Slice fruits! Avoid BOMBS",True,(140,100,180)),(W//2-120,H-30))

        pygame.display.flip()

    # game over
    best=max(best,score)
    while True:
        screen.fill((15,5,30))
        t=BF.render("GAME OVER",True,(255,60,60)); screen.blit(t,(W//2-t.get_width()//2,180))
        screen.blit(F.render(f"Score: {score}"   ,True,(255,220,0)),(W//2-80,290))
        screen.blit(F.render(f"Best:  {best}"    ,True,(180,180,255)),(W//2-75,335))
        screen.blit(SM.render("SPACE = Play Again   Q = Quit",True,(180,160,220)),(W//2-145,410))
        pygame.display.flip(); clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_SPACE: break
                if ev.key==pygame.K_q: pygame.quit(); sys.exit()
        else: continue
        break

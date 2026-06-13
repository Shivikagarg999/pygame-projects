import pygame,sys,random,math
pygame.init()
W,H=700,520;screen=pygame.display.set_mode((W,H));clock=pygame.time.Clock()
pygame.display.set_caption("Shooting Range");pygame.mouse.set_visible(False)
F=pygame.font.Font(None,36);BF=pygame.font.Font(None,64);SM=pygame.font.Font(None,26)
def sp():
    k=random.choices(["r","g","b"],[70,15,15])[0];r={"r":28,"g":18,"b":25}[k]
    i=random.randint(0,3);spd={"r":2.5,"g":4.5,"b":2.0}[k]+random.uniform(0,1)
    x,y=[(-r,random.randint(0,H)),(W+r,random.randint(0,H)),(random.randint(0,W),-r),(random.randint(0,W),H+r)][i]
    dx,dy=[(1,0),(-1,0),(0,1),(0,-1)][i]
    return{"x":float(x),"y":float(y),"vx":dx*spd,"vy":dy*spd,"r":r,"k":k,"rot":0}
def dt(t):
    x,y,r=int(t["x"]),int(t["y"]),t["r"]
    if t["k"]=="b":
        pygame.draw.circle(screen,(25,25,25),(x,y),r);pygame.draw.circle(screen,(80,80,80),(x,y),r,3)
        pygame.draw.line(screen,(200,160,0),(x,y-r),(x+5,y-r-10),3);pygame.draw.circle(screen,(255,180,0),(x+5,y-r-10),4)
        s=SM.render("BOMB",True,(255,50,50));screen.blit(s,(x-s.get_width()//2,y-8))
    elif t["k"]=="g":
        [pygame.draw.circle(screen,c,(x,y),s)for c,s in[((200,160,0),r),((255,230,80),r-6),((255,255,180),r-12)]]
        [pygame.draw.line(screen,(255,220,0),(x,y),(x+int(math.cos(math.radians(t["rot"]+i*72))*(r-3)),y+int(math.sin(math.radians(t["rot"]+i*72))*(r-3))),2)for i in range(5)]
    else:
        [pygame.draw.circle(screen,c,(x,y),s)for c,s in[((180,30,30),r),((255,60,60),r-6),((255,255,255),r-13),((180,30,30),r-19)]if s>0]
        pygame.draw.circle(screen,(180,180,180),(x,y),r,2)
while True:
    tg=[sp()for _ in range(3)];pa=[];po=[];score=shots=hits=combo=mc=0;timer=3600
    while timer>0:
        clock.tick(60);timer-=1;mx,my=pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:pygame.quit();sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN:
                shots+=1;got=False
                for t in tg:
                    if math.hypot(mx-t["x"],my-t["y"])<t["r"]+5:
                        tg.remove(t);got=True
                        if t["k"]=="b":
                            score=max(0,score-20);combo=0;po.append([t["x"],t["y"],"-20",(255,50,50),50])
                            for _ in range(15):pa.append([t["x"],t["y"],random.uniform(-4,4),random.uniform(-4,4),(255,120,0),25])
                        else:
                            combo+=1;mc=max(mc,combo);mult=3 if combo>=10 else 2 if combo>=5 else 1
                            pts=(25 if t["k"]=="g" else 10)*mult;score+=pts;hits+=1
                            col=(255,220,0)if t["k"]=="g"else(255,100,100)
                            po.append([t["x"],t["y"],f"+{pts}"+(f" x{mult}!"if mult>1 else""),col,50])
                            for _ in range(10):pa.append([t["x"],t["y"],random.uniform(-3,3),random.uniform(-4,1),col,20])
                        break
                if not got:combo=0
        tg=[t for t in tg if -60<t["x"]<W+60 and -60<t["y"]<H+60]
        while len(tg)<3+min(3,score//150):tg.append(sp())
        for t in tg:t["x"]+=t["vx"];t["y"]+=t["vy"];t["rot"]+=3
        for p in pa:p[0]+=p[2];p[1]+=p[3];p[3]+=0.3;p[5]-=1
        pa=[p for p in pa if p[5]>0];[pp.__setitem__(1,pp[1]-1.5)or pp.__setitem__(4,pp[4]-1)for pp in po];po=[p for p in po if p[4]>0]
        screen.fill((18,12,8))
        for i in range(0,H,30):pygame.draw.line(screen,(28,18,8),(0,i),(W,i))
        for i in range(0,W,W//4):pygame.draw.line(screen,(38,25,10),(i,0),(i,H))
        for t in tg:dt(t)
        for p in pa:ft=p[5]/20;pygame.draw.circle(screen,tuple(int(c*ft)for c in p[4]),(int(p[0]),int(p[1])),max(1,int(3*ft)))
        for pp in po:s=SM.render(pp[2],True,pp[3]);s.set_alpha(int(255*pp[4]/50));screen.blit(s,(int(pp[0])-s.get_width()//2,int(pp[1])))
        sc=timer//60;pygame.draw.rect(screen,(10,8,5),(0,0,W,40));bw=int((W-160)*sc/60)
        
        tc=(60,200,60)if sc>15 else(255,140,0)if sc>8 else(220,40,40)
        pygame.draw.rect(screen,(40,28,12),(80,8,W-160,24),border_radius=5);pygame.draw.rect(screen,tc,(80,8,bw,24),border_radius=5)
        screen.blit(F.render(f"Score:{score}",True,(255,220,0)),(4,6));screen.blit(SM.render(f"{sc}s",True,(255,255,255)),(W//2-12,10))
        screen.blit(SM.render(f"Acc:{int(hits/max(1,shots)*100)}%  x{3 if combo>=10 else 2 if combo>=5 else 1}",True,(180,180,180)),(W-200,12))
        pygame.draw.circle(screen,(0,220,0),(mx,my),20,2);[pygame.draw.line(screen,(0,220,0),(mx+dx*8,my+dy*8),(mx+dx*28,my+dy*28),2)for dx,dy in[(-1,0),(1,0),(0,-1),(0,1)]]
        pygame.draw.circle(screen,(0,255,0),(mx,my),3);pygame.display.flip()
    while True:
        screen.fill((18,12,8));t=BF.render("TIME'S UP!",True,(255,220,0));screen.blit(t,(W//2-t.get_width()//2,120))
        for i,(lbl,col)in enumerate([(f"Score:{score}",(255,255,255)),(f"Accuracy:{int(hits/max(1,shots)*100)}%",(60,220,80)),(f"Hits:{hits}/{shots}",(180,180,255)),(f"Best Combo:x{mc}",(255,180,0))]):
            s=F.render(lbl,True,col);screen.blit(s,(W//2-s.get_width()//2,230+i*46))
        s=SM.render("SPACE=Play Again  Q=Quit",True,(140,140,140));screen.blit(s,(W//2-s.get_width()//2,430));pygame.display.flip();clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:pygame.quit();sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_SPACE:break
                if ev.key==pygame.K_q:pygame.quit();sys.exit()
        else:continue
        break

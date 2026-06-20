import pygame,sys,random,math,ctypes
try:ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
except Exception:
    try:ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:ctypes.windll.user32.SetProcessDPIAware()
        except Exception:pass
pygame.init()
screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN);SW,SH=screen.get_size();clock=pygame.time.Clock()
pygame.display.set_caption("MiniCraft");F=pygame.font.Font(None,24);BF=pygame.font.Font(None,40)

BS=32;CW,CH=260,80
# 0=air 1=grass 2=dirt 3=stone 4=wood 5=leaves 6=sand 7=water
# 8=cobble 9=plank 10=brick 11=glass 12=gravel 13=coal 14=chest 15=torch
COLS=[(0,0,0),(76,153,0),(139,90,43),(120,120,120),(101,67,33),(34,139,34),
      (194,178,128),(64,164,223),(90,90,90),(180,140,80),(160,60,55),(200,230,245),
      (110,105,100),(50,50,50),(160,110,40),(255,200,80)]
NAMES=["","Grass","Dirt","Stone","Wood","Leaves","Sand","Water","Cobble","Plank","Brick","Glass","Gravel","Coal","Chest","Torch"]
SOLID={1,2,3,4,5,6,8,9,10,11,12,13,14}
HOTBAR=[1,2,3,8,9,10,11,6,4,5]

def set_b(w,x,y,b):
    if 0<=x<CW and 0<=y<CH:w[x][y]=b
def get_b(w,x,y):
    if 0<=x<CW and 0<=y<CH:return w[x][y]
    return 3

def gen_house(w,x,h):
    # wooden house 9 wide 5 tall
    for dx in range(9):
        for dy in range(5):
            b=4 if dx in(0,8) or dy in(0,4) else 0
            if dy==4:b=4
            set_b(w,x+dx,h-dy-1,b)
    # plank floor
    for dx in range(9):set_b(w,x+dx,h,9)
    # door
    set_b(w,x+4,h-1,0);set_b(w,x+4,h-2,0)
    # windows
    set_b(w,x+2,h-2,11);set_b(w,x+6,h-2,11)
    # roof (leaves)
    for lv in range(4):
        for dx in range(-lv,9+lv):set_b(w,x+4+dx-4,h-5-lv,5 if lv<2 else 4)
    # chest inside
    set_b(w,x+1,h-1,14);set_b(w,x+7,h-1,15)

def gen_ruin(w,x,h):
    for dx in range(7):
        for dy in range(random.randint(2,5)):
            if random.random()>0.25:set_b(w,x+dx,h-dy-1,8)
    # broken roof bits
    for dx in range(3,5):
        if random.random()>0.4:set_b(w,x+dx,h-5,8)

def gen_dungeon(w,x,y):
    # stone brick room underground
    W2,H2=12,7
    for dx in range(W2):
        for dy in range(H2):
            b=3 if dx in(0,W2-1) or dy in(0,H2-1) else 0
            set_b(w,x+dx,y+dy,b)
    # floor & ceiling
    for dx in range(W2):set_b(w,x+dx,y,10);set_b(w,x+dx,y+H2-1,10)
    # chests & torches
    set_b(w,x+2,y+H2-2,14);set_b(w,x+W2-3,y+H2-2,14)
    set_b(w,x+1,y+1,15);set_b(w,x+W2-2,y+1,15)
    # entrance shaft
    for dy in range(y):
        if get_b(w,x+W2//2,dy)==3 or get_b(w,x+W2//2,dy)==2:set_b(w,x+W2//2,dy,0)

def gen_cave(w,x,y,length):
    cx,cy=x,y
    for _ in range(length):
        r=random.randint(2,4)
        for dx in range(-r,r+1):
            for dy in range(-r,r+1):
                if dx*dx+dy*dy<=r*r and get_b(w,cx+dx,cy+dy) in{2,3,12,13}:
                    set_b(w,cx+dx,cy+dy,0)
        cx+=random.randint(-2,2);cy+=random.randint(-1,2)
        cx=max(1,min(CW-2,cx));cy=max(15,min(CH-5,cy))

def gen():
    w=[[0]*CH for _ in range(CW)]
    hs=[]
    for x in range(CW):
        h=int(32+9*math.sin(x*0.05)+5*math.sin(x*0.13+1)+random.randint(-1,1))
        h=max(10,min(55,h));hs.append(h)
        w[x][h]=1
        for y in range(h+1,min(h+4,CH)):w[x][y]=2
        for y in range(h+4,CH):
            w[x][y]=13 if random.random()<0.04 else(12 if random.random()<0.04 else 3)
    # trees
    for x in range(3,CW-3):
        if random.random()<0.06 and w[x][hs[x]]==1:
            h=hs[x]
            for ty in range(h-5,h):w[x][ty]=4
            for lx in range(x-2,x+3):
                for ly in range(h-7,h-3):
                    if 0<=lx<CW and 0<=ly<CH and w[lx][ly]==0:w[lx][ly]=5
    # structures on surface
    placed=[]
    for x in range(10,CW-15):
        if any(abs(x-p)<15 for p in placed):continue
        h=hs[x]
        r=random.random()
        if r<0.04:gen_house(w,x,h);placed.append(x)
        elif r<0.08:gen_ruin(w,x,h);placed.append(x)
    # underground caves
    for _ in range(25):
        x=random.randint(5,CW-5);y=random.randint(hs[x]+8,CH-8)
        gen_cave(w,x,y,random.randint(20,60))
    # dungeons
    for _ in range(6):
        x=random.randint(10,CW-25);y=random.randint(45,CH-12)
        gen_dungeon(w,x,y)
    return w,hs

world,hs=gen()
spx=CW//2;spy=next(y for y in range(CH) if world[spx][y]!=0)-3
px,py=float(spx*BS),float(spy*BS);pvx=pvy=0.0;on_g=False
sel=0;prev_sel=0;item_popup_t=0;PW,PH=BS-4,BS*2-2
particles=[];msgs=[];HF=pygame.font.Font(None,32);PF=pygame.font.Font(None,48);CF=pygame.font.Font(None,20)
inv={}
mobs=[];mob_spawn_t=150;health=100;hit_cd=0

def is_solid(x,y):
    gx,gy=int(x)//BS,int(y)//BS
    return not(0<=gx<CW and 0<=gy<CH) or world[gx][gy] in SOLID

def col_x(dx):
    global px
    px+=dx
    for oy in[2,PH//2,PH-2]:
        for ox in[0,PW]:
            if is_solid(px+ox,py+oy):
                px=(int((px+PW)//BS)*BS-PW-1)if dx>0 else((int(px//BS)+1)*BS);return

def col_y(dy):
    global py,pvy,on_g
    py+=dy;on_g=False
    for ox in[2,PW-2]:
        if is_solid(px+ox,py+PH):
            py=int((py+PH)//BS)*BS-PH;pvy=0;on_g=True;return
        if is_solid(px+ox,py):
            py=(int(py//BS)+1)*BS;pvy=0;return

def mob_step(m,dt):
    nx=m["x"]+m["vx"]*dt
    blocked=any(is_solid(nx+ox,m["y"]+oy) for oy in[2,PH//2,PH-2] for ox in[0,PW])
    if blocked:
        if m["on_g"]:m["vy"]=-480
    else:
        m["x"]=nx
    m["vy"]=min(m["vy"]+1200*dt,900)
    ny=m["y"]+m["vy"]*dt;m["on_g"]=False
    for ox in[2,PW-2]:
        if is_solid(m["x"]+ox,ny+PH):
            ny=int((ny+PH)//BS)*BS-PH;m["vy"]=0;m["on_g"]=True;break
        if is_solid(m["x"]+ox,ny):
            ny=(int(ny//BS)+1)*BS;m["vy"]=0;break
    m["y"]=ny

def draw_block(b,x,y,sz=BS):
    if b==0:return
    c=COLS[b];pygame.draw.rect(screen,c,(x,y,sz,sz))
    if b==1:pygame.draw.rect(screen,(56,180,56),(x,y,sz,6))
    if b==5:pygame.draw.rect(screen,(0,100,0),(x,y,sz,sz))
    if b==11:  # glass - draw frame only
        pygame.draw.rect(screen,(180,210,240),(x,y,sz,sz))
        pygame.draw.rect(screen,(220,240,255),(x+4,y+4,sz-8,sz-8))
    if b==13:  # coal ore
        pygame.draw.rect(screen,(120,120,120),(x,y,sz,sz))
        for ox,oy in[(4,4),(sz-10,8),(8,sz-10),(sz-8,sz-8)]:
            pygame.draw.rect(screen,(20,20,20),(x+ox,y+oy,5,5))
    if b==14:  # chest
        pygame.draw.rect(screen,(140,90,30),(x,y,sz,sz))
        pygame.draw.rect(screen,(100,60,20),(x,y+sz//3,sz,sz//3))
        pygame.draw.circle(screen,(200,160,0),(x+sz//2,y+sz//2),4)
    if b==15:  # torch - draw as flame
        pygame.draw.rect(screen,(139,90,43),(x+sz//2-3,y+sz//3,6,sz//2))
        pygame.draw.circle(screen,(255,200,0),(x+sz//2,y+sz//4),6)
        pygame.draw.circle(screen,(255,120,0),(x+sz//2,y+sz//4),4)
    if b not in{11,13,14,15}:
        sh=pygame.Surface((sz,sz),pygame.SRCALPHA);sh.fill((0,0,0,35))
        pygame.draw.rect(sh,(255,255,255,25),(0,0,sz,3));screen.blit(sh,(x,y))
    pygame.draw.rect(screen,(0,0,0),(x,y,sz,sz),1)

camx=camy=0
while True:
    dt=min(clock.tick(60)/1000,0.05)
    mx,my=pygame.mouse.get_pos()
    wmx=int((mx+camx)//BS);wmy=int((my+camy)//BS)

    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:pygame.quit();sys.exit()
        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_ESCAPE:pygame.quit();sys.exit()
            for i in range(10):
                if ev.key==pygame.K_0+i+1:sel=i%10
        if ev.type==pygame.MOUSEWHEEL:sel=(sel-ev.y)%len(HOTBAR)
        if ev.type==pygame.MOUSEBUTTONDOWN:
            d=math.hypot(wmx*BS+BS//2-(px+PW//2),wmy*BS+BS//2-(py+PH//2))
            if d<BS*6 and 0<=wmx<CW and 0<=wmy<CH:
                if ev.button==1:
                    hit=None
                    for m in mobs:
                        if math.hypot((mx+camx)-(m["x"]+PW/2),(my+camy)-(m["y"]+PH/2))<BS:hit=m;break
                    if hit:
                        hit["hp"]-=1
                        for _ in range(8):particles.append([hit["x"]+PW/2,hit["y"]+PH/2,random.uniform(-3,3),random.uniform(-5,0),(120,40,40),18])
                    elif world[wmx][wmy] in SOLID:
                        bb=world[wmx][wmy]
                        c=COLS[bb]
                        if bb==14:msgs.append(["** Chest found! **",90,(255,220,0)])
                        inv[bb]=inv.get(bb,0)+1
                        world[wmx][wmy]=0
                        for _ in range(10):particles.append([wmx*BS+BS//2,wmy*BS+BS//2,random.uniform(-3,3),random.uniform(-5,0),c,22])
                elif ev.button==3 and world[wmx][wmy]==0:
                    if inv.get(HOTBAR[sel],0)>0:
                        world[wmx][wmy]=HOTBAR[sel];inv[HOTBAR[sel]]-=1
                    else:
                        msgs.append([f"No {NAMES[HOTBAR[sel]]} left!",40,(255,80,80)])

    if sel!=prev_sel:item_popup_t=100;prev_sel=sel
    keys=pygame.key.get_pressed()
    pvx=(-300 if keys[pygame.K_a] or keys[pygame.K_LEFT] else 300 if keys[pygame.K_d] or keys[pygame.K_RIGHT] else 0)
    if(keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP])and on_g:pvy=-720
    pvy=min(pvy+1200*dt,900)
    col_x(pvx*dt);col_y(pvy*dt)

    mob_spawn_t-=1
    if mob_spawn_t<=0 and len(mobs)<8:
        side=random.choice([-1,1]);gx=max(2,min(CW-3,int(px//BS)+side*random.randint(15,28)))
        sy=(hs[gx]-3)*BS
        mobs.append({"x":float(gx*BS),"y":float(sy),"vx":0.0,"vy":0.0,"on_g":False,"hp":3,"dir":random.choice([-1,1]),"wander_t":0})
        mob_spawn_t=random.randint(180,300)

    mobs=[m for m in mobs if m["hp"]>0]
    for m in mobs:
        dx=px-m["x"]
        if abs(dx)<400:
            m["vx"]=120 if dx>0 else -120
        else:
            m["wander_t"]-=1
            if m["wander_t"]<=0:
                m["dir"]=random.choice([-1,0,1]);m["wander_t"]=random.randint(60,150)
            m["vx"]=m["dir"]*50
        mob_step(m,dt)

    if hit_cd>0:hit_cd-=1
    for m in mobs:
        if hit_cd<=0 and abs((m["x"]+PW/2)-(px+PW/2))<PW and abs((m["y"]+PH/2)-(py+PH/2))<PH:
            health=max(0,health-15);hit_cd=45
            msgs.append(["Ouch!",30,(255,60,60)])

    if health<=0:
        px,py=float(spx*BS),float(spy*BS);pvx=pvy=0.0;health=100
        msgs.append(["You died! Respawned.",60,(255,80,80)])

    camx=int(max(0,min(px-SW//2+PW//2,CW*BS-SW)))
    camy=int(max(0,min(py-SH//2+PH//2,CH*BS-SH)))

    # sky
    for y in range(0,SH,3):
        t=y/SH;pygame.draw.rect(screen,(int(100+35*t),int(175+25*t),int(240-30*t)),(0,y,SW,3))
    # clouds
    for i in range(8):
        cx2=(i*320-camx//3)%SW+(-80);cy2=30+i%3*25
        pygame.draw.ellipse(screen,(255,255,255),(cx2,cy2,130,35));pygame.draw.ellipse(screen,(255,255,255),(cx2+25,cy2-15,80,35))

    # blocks
    sx2=max(0,camx//BS);ex2=min(CW,sx2+SW//BS+2)
    sy2=max(0,camy//BS);ey2=min(CH,sy2+SH//BS+2)
    for gx in range(sx2,ex2):
        for gy in range(sy2,ey2):
            b=world[gx][gy]
            if b:draw_block(b,gx*BS-camx,gy*BS-camy)

    # torch light effect (orange glow behind torches)
    for gx in range(sx2,ex2):
        for gy in range(sy2,ey2):
            if world[gx][gy]==15:
                gl=pygame.Surface((BS*5,BS*5),pygame.SRCALPHA)
                pygame.draw.circle(gl,(255,180,0,40),(BS*2+BS//2,BS*2+BS//2),BS*2)
                screen.blit(gl,(gx*BS-camx-BS*2,gy*BS-camy-BS*2))

    # particles
    for p in particles:
        p[0]+=p[2];p[1]+=p[3];p[3]+=0.4;p[5]-=1
        if p[5]>0:pygame.draw.rect(screen,p[4],(int(p[0]-camx),int(p[1]-camy),4,4))
    particles=[p for p in particles if p[5]>0]

    # mobs
    for m in mobs:
        mlx,mly=int(m["x"]-camx),int(m["y"]-camy)
        pygame.draw.rect(screen,(40,110,40),(mlx,mly,PW,PH))
        pygame.draw.rect(screen,(150,200,150),(mlx+3,mly-12,PW-6,12))
        pygame.draw.circle(screen,(255,0,0),(mlx+8,mly-6),2);pygame.draw.circle(screen,(255,0,0),(mlx+16,mly-6),2)

    # player
    plx,ply=int(px-camx),int(py-camy)
    pygame.draw.rect(screen,(70,130,180),(plx,ply,PW,PH))
    pygame.draw.rect(screen,(255,220,180),(plx+3,ply-14,PW-6,14))
    pygame.draw.circle(screen,(30,30,30),(plx+8,ply-7),3);pygame.draw.circle(screen,(255,255,255),(plx+9,ply-8),1)
    pygame.draw.circle(screen,(30,30,30),(plx+16,ply-7),3);pygame.draw.circle(screen,(255,255,255),(plx+17,ply-8),1)

    # highlight
    if 0<=wmx<CW and 0<=wmy<CH:
        s2=pygame.Surface((BS,BS),pygame.SRCALPHA);s2.fill((255,255,255,70));screen.blit(s2,(wmx*BS-camx,wmy*BS-camy))
        pygame.draw.rect(screen,(255,255,255),(wmx*BS-camx,wmy*BS-camy,BS,BS),2)

    # hotbar
    hbw=len(HOTBAR)*44;hbx=SW//2-hbw//2
    cur_name=NAMES[HOTBAR[sel]]
    # "Holding" label above hotbar
    hl=F.render(f"Holding:  {cur_name}",True,(255,255,200))
    screen.blit(hl,(SW//2-hl.get_width()//2,SH-72))
    pygame.draw.rect(screen,(0,0,0),(hbx-4,SH-54,hbw+8,50),border_radius=6)
    for i,bt in enumerate(HOTBAR):
        bx2=hbx+i*44;by2=SH-52
        pygame.draw.rect(screen,(50,50,50),(bx2,by2,40,40),border_radius=3)
        draw_block(bt,bx2+4,by2+4,32)
        pygame.draw.rect(screen,(255,220,0)if i==sel else(80,80,80),(bx2,by2,40,40),2,border_radius=3)
        screen.blit(F.render(str((i+1)%10),True,(200,200,200)),(bx2+2,by2+2))
        cnt=inv.get(bt,0)
        ct=CF.render(str(cnt),True,(255,255,255)if cnt>0 else(150,60,60))
        screen.blit(ct,(bx2+38-ct.get_width(),by2+38-ct.get_height()))
    # item switch popup (fades out after switching)
    if item_popup_t>0:
        alpha=min(255,item_popup_t*5);item_popup_t-=1
        ps=PF.render(f"[ {cur_name} x{inv.get(HOTBAR[sel],0)} ]",True,(255,220,80))
        ps.set_alpha(alpha);screen.blit(ps,(SW//2-ps.get_width()//2,SH//2+80))

    # crosshair
    pygame.draw.line(screen,(255,255,255),(SW//2-10,SH//2),(SW//2+10,SH//2),2)
    pygame.draw.line(screen,(255,255,255),(SW//2,SH//2-10),(SW//2,SH//2+10),2)

    # HUD
    pygame.draw.rect(screen,(0,0,0),(0,0,SW,22))
    depth=max(0,wmy-hs[max(0,min(wmx,CW-1))])
    screen.blit(F.render(f"[{NAMES[HOTBAR[sel]]}]  LClick=Break/Attack  RClick=Place  Scroll/1-0=Switch  Depth:{depth}  | Explore: Houses, Ruins, Dungeons!",True,(220,220,220)),(4,3))
    hbx3,hby3=SW-166,4
    screen.blit(CF.render("HP",True,(255,255,255)),(hbx3-22,hby3-1))
    pygame.draw.rect(screen,(60,0,0),(hbx3,hby3,150,14))
    pygame.draw.rect(screen,(220,30,30),(hbx3,hby3,int(150*health/100),14))
    pygame.draw.rect(screen,(255,255,255),(hbx3,hby3,150,14),1)

    # messages
    for m in msgs:
        t=BF.render(m[0],True,m[2]);t.set_alpha(min(255,m[1]*4));screen.blit(t,(SW//2-t.get_width()//2,SH//2-80));m[1]-=1
    msgs=[m for m in msgs if m[1]>0]

    pygame.display.flip()
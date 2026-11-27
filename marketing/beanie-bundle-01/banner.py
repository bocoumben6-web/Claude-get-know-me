# Shopify-Banner „Beanie Bundle 01“ – Aufruf: python3 banner.py <bundlepreis> [einzelpreis]
import sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R='/home/user/Claude-get-know-me/'
D=R+'marketing/beanie-bundle-01/'
PRICE=sys.argv[1] if len(sys.argv)>1 else None
SINGLE=float(sys.argv[2]) if len(sys.argv)>2 else 30.0
FULL=3*SINGLE
ANTON=R+'assets/fonts/Anton-Regular.ttf'; BEBAS=R+'assets/fonts/BebasNeue-Regular.ttf'
BLUE=(2,9,176); BLUE_HI=(40,70,255); WHITE=(245,244,240)
def fmt(v): v=float(v); return (f'{v:.0f}' if v==int(v) else f'{v:.2f}'.replace('.',','))+' €'
pct=None if PRICE is None else round((1-float(PRICE.replace(',','.'))/FULL)*100)
beanies=[Image.open(R+f'mockups/beanies-drop-26/beanie-{n}-freigestellt.png').convert('RGBA') for n in ['black','camo-vorne','white']]
Lg=Image.open(R+'assets/logo.png').convert('RGBA')

def bg(W,H):
    t=cv2.imread(D+'hintergrund-kratzer.jpg'); h,w=t.shape[:2]; s=max(W/w,H/h)
    t=cv2.resize(t,(int(w*s)+1,int(h*s)+1),interpolation=cv2.INTER_CUBIC)
    y0=(t.shape[0]-H)//2; x0=(t.shape[1]-W)//2; t=t[y0:y0+H,x0:x0+W].astype(np.float32)
    t=cv2.cvtColor(t,cv2.COLOR_BGR2RGB)*0.85
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    vig=1-0.55*np.clip(((xx-W/2)/(W*0.62))**2+((yy-H/2)/(H*0.7))**2,0,1)
    return t*vig[...,None]

def glow(img,cx,cy,rx,ry,strength):
    H,W=img.shape[:2]; yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    g=np.exp(-(((xx-cx)/rx)**2+((yy-cy)/ry)**2))
    return img+np.array(BLUE_HI,np.float32)*g[...,None]*strength

def paste_beanies(im,cx,base_y,height,gap):
    # 3 beanies side by side, middle one slightly larger + in front
    sizes=[0.92,1.0,0.92]; ws=[]; scaled=[]
    for b,sz in zip(beanies,sizes):
        h=int(height*sz); w=int(b.width*h/b.height); scaled.append(b.resize((w,h),Image.LANCZOS)); ws.append(w)
    total=sum(ws)+2*gap; x=cx-total//2; pos=[]
    for s,w in zip(scaled,ws): pos.append(x); x+=w+gap
    order=[0,2,1]
    for i in order:
        s=scaled[i]; px=pos[i]; py=base_y-s.height
        a=np.array(s)[...,3].astype(np.float32)/255
        sh=Image.fromarray((a*255*0.85).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(6,s.height//30)))
        shadow=Image.new('RGBA',s.size,(0,0,0,0)); shadow.putalpha(sh)
        im.alpha_composite(shadow,(px+s.width//60,py+s.height//25))
        im.alpha_composite(s,(px,py))
    return pos, ws

def text(d,xy,t,font,size,fill,anchor='mm',spacing=0):
    f=ImageFont.truetype(font,size); d.text(xy,t,font=f,fill=fill,anchor=anchor); return f

def lavish_word(im,x,y,size,anchor_center=True):
    # brush-L logo + "AVISH" in Anton, like the Beanie-Week graphic
    f=ImageFont.truetype(ANTON,size); d=ImageDraw.Draw(im)
    capH=f.getbbox('A')[3]-f.getbbox('A')[1]
    l=Lg.resize((int(Lg.width*capH*1.08/Lg.height),int(capH*1.08)),Image.LANCZOS)
    wtxt=d.textlength('AVISH',font=f); total=l.width+int(size*0.02)+wtxt
    x0=int(x-total/2) if anchor_center else x
    top=y-capH//2
    im.alpha_composite(l,(x0,top-int(capH*0.04)))
    d.text((x0+l.width+int(size*0.02),top-f.getbbox('A')[1]),'AVISH',font=f,fill=WHITE)

def pill(d,cx,cy,t,size,fg=WHITE,bgc=BLUE,padx=0.45,pady=0.22,font=ANTON):
    f=ImageFont.truetype(font,size); bb=d.textbbox((0,0),t,font=f)
    w=bb[2]-bb[0]; h=bb[3]-bb[1]; px=int(size*padx); py=int(size*pady)
    d.rectangle((cx-w//2-px,cy-h//2-py,cx+w//2+px,cy+h//2+py),fill=bgc)
    d.text((cx,cy),t,font=f,fill=fg,anchor='mm')

def price_line(d,cx,cy,size):
    old=fmt(FULL); new=fmt(PRICE.replace(',','.')) if PRICE else '?? €'
    f1=ImageFont.truetype(BEBAS,int(size*0.62)); f2=ImageFont.truetype(ANTON,size)
    w1=d.textlength('STATT '+old,font=f1); w2=d.textlength('NUR '+new,font=f2); gap=size*0.5
    x=cx-(w1+gap+w2)/2
    d.text((x,cy),'STATT '+old,font=f1,fill=(170,170,175),anchor='lm')
    sb=d.textbbox((x,cy),'STATT '+old,font=f1,anchor='lm'); ox=x+d.textlength('STATT ',font=f1)
    d.line((ox-4,cy+2,sb[2]+4,cy-2),fill=BLUE_HI,width=max(3,size//14))
    d.text((x+w1+gap,cy),'NUR '+new,font=f2,fill=WHITE,anchor='lm')

def desktop():
    W,H=2400,1200
    a=bg(W,H); a=glow(a,W*0.285,H*0.62,W*0.28,H*0.26,0.55)
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA')
    paste_beanies(im,int(W*0.285),int(H*0.80),int(H*0.40),-int(H*0.025))
    d=ImageDraw.Draw(im); cx=int(W*0.745)
    lavish_word(im,cx,int(H*0.15),110)
    text(d,(cx,int(H*0.255)),'BEANIE WEEK · FREITAG 27.11',BEBAS,64,(200,200,205))
    pill(d,cx,int(H*0.38),'BUNDLE 01',70)
    text(d,(cx,int(H*0.53)),'3 BEANIES. 1 PREIS.',ANTON,92,WHITE)
    big=f'-{pct}%' if pct is not None else '-??%'
    f=ImageFont.truetype(ANTON,250)
    gl=Image.new('L',(W,H),0); ImageDraw.Draw(gl).text((cx,int(H*0.735)),big,font=f,anchor='mm',fill=255)
    gl=gl.filter(ImageFilter.GaussianBlur(28)); glayer=Image.new('RGBA',(W,H),BLUE_HI+(0,)); glayer.putalpha(gl.point(lambda v:int(v*0.8)))
    im.alpha_composite(glayer); d=ImageDraw.Draw(im)
    d.text((cx,int(H*0.735)),big,font=f,anchor='mm',fill=BLUE_HI)
    price_line(d,cx,int(H*0.91),78)
    return im.convert('RGB')

def mobile():
    W,H=1080,1350
    a=bg(W,H); a=glow(a,W*0.5,H*0.27,W*0.42,H*0.16,0.55)
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA')
    d=ImageDraw.Draw(im)
    lavish_word(im,W//2,int(H*0.06),62)
    text(d,(W//2,int(H*0.115)),'BEANIE WEEK · FREITAG 27.11',BEBAS,40,(200,200,205))
    paste_beanies(im,W//2,int(H*0.47),int(H*0.29),-int(H*0.02))
    d=ImageDraw.Draw(im)
    pill(d,W//2,int(H*0.55),'BUNDLE 01',52)
    text(d,(W//2,int(H*0.645)),'3 BEANIES. 1 PREIS.',ANTON,82,WHITE)
    big=f'-{pct}%' if pct is not None else '-??%'
    f=ImageFont.truetype(ANTON,220)
    gl=Image.new('L',(W,H),0); ImageDraw.Draw(gl).text((W//2,int(H*0.80)),big,font=f,anchor='mm',fill=255)
    gl=gl.filter(ImageFilter.GaussianBlur(24)); glayer=Image.new('RGBA',(W,H),BLUE_HI+(0,)); glayer.putalpha(gl.point(lambda v:int(v*0.8)))
    im.alpha_composite(glayer); d=ImageDraw.Draw(im)
    d.text((W//2,int(H*0.80)),big,font=f,anchor='mm',fill=BLUE_HI)
    price_line(d,W//2,int(H*0.935),60)
    return im.convert('RGB')

tag='' if PRICE else '-VORSCHAU'
desktop().save(D+f'banner-desktop-2400x1200{tag}.jpg',quality=93)
mobile().save(D+f'banner-mobil-1080x1350{tag}.jpg',quality=93)
print('pct',pct)

# Pop-up Tisch-Flyer A5 (148 x 210 mm, 300 dpi) – python3 flyer.py [preis]
import sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R='/home/user/Claude-get-know-me/'; D=R+'marketing/popup-flyer/'
PRICE=sys.argv[1] if len(sys.argv)>1 else None
ANTON=R+'assets/fonts/Anton-Regular.ttf'; BEBAS=R+'assets/fonts/BebasNeue-Regular.ttf'
BLUE=(2,9,176); BLUE_HI=(40,70,255); WHITE=(245,244,240)
W,H=1748,2480
# background: scratched black + vignette + blue glow behind the product
t=cv2.imread(R+'marketing/beanie-bundle-01/hintergrund-kratzer.jpg'); h,w=t.shape[:2]; s=max(W/w,H/h)
t=cv2.resize(t,(int(w*s)+1,int(h*s)+1),interpolation=cv2.INTER_CUBIC)[:H,:W]
a=cv2.cvtColor(t,cv2.COLOR_BGR2RGB).astype(np.float32)*0.8
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
a*= (1-0.5*np.clip(((xx-W/2)/(W*0.65))**2+((yy-H/2)/(H*0.6))**2,0,1))[...,None]
a+=np.array(BLUE_HI,np.float32)*np.exp(-(((xx-W/2)/(W*0.42))**2+((yy-H*0.43)/(H*0.17))**2))[...,None]*0.5
im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGBA'); d=ImageDraw.Draw(im)
def T(xy,txt,font,size,fill=WHITE,anchor='mm'):
    f=ImageFont.truetype(font,size); d.text(xy,txt,font=f,fill=fill,anchor=anchor); return f
def pill(cx,cy,txt,size,fg=WHITE,bgc=BLUE):
    f=ImageFont.truetype(ANTON,size); bb=d.textbbox((0,0),txt,font=f); w=bb[2]-bb[0]; h=bb[3]-bb[1]
    px=int(size*0.45); py=int(size*0.24); d.rectangle((cx-w//2-px,cy-h//2-py,cx+w//2+px,cy+h//2+py),fill=bgc); d.text((cx,cy),txt,font=f,fill=fg,anchor='mm')
def rounded(img,r):
    m=Image.new('L',img.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,img.width-1,img.height-1),r,fill=255); img=img.convert('RGBA'); img.putalpha(m); return img
def drop(img,x,y,blur=30,off=18,op=170):
    a=img.split()[3].point(lambda v:int(v*op/255)); sh=Image.new('RGBA',img.size,(0,0,0,0)); sh.putalpha(a)
    pad=blur*3; big=Image.new('RGBA',(img.width+2*pad,img.height+2*pad),(0,0,0,0)); big.alpha_composite(sh,(pad,pad))
    im.alpha_composite(big.filter(ImageFilter.GaussianBlur(blur)),(x-pad,y-pad+off)); im.alpha_composite(img,(x,y))
# header: brush-L + AVISH
Lg=Image.open(R+'assets/logo.png').convert('RGBA')
f=ImageFont.truetype(ANTON,120); capH=f.getbbox('A')[3]-f.getbbox('A')[1]
l=Lg.resize((int(Lg.width*capH*1.08/Lg.height),int(capH*1.08)),Image.LANCZOS)
tw=d.textlength('AVISH',font=f); x0=int(W/2-(l.width+4+tw)/2); top=105
im.alpha_composite(l,(x0,top)); d.text((x0+l.width+4,top-f.getbbox('A')[1]),'AVISH',font=f,fill=WHITE)
pill(W//2,322,'POP-UP',56)
T((W//2,480),'SNR FLANNEL',ANTON,175)
T((W//2,598),'STILL NOT REACHABLE.',BEBAS,76,(200,200,205))
# product card (real product photo on Lavish gray)
ph=Image.open(D+'flanell-original.png').convert('RGB').crop((0,110,963,1010))
cw=1120; ph=ph.resize((cw,int(ph.height*cw/ph.width)),Image.LANCZOS)
card=rounded(ph,36); cy=660
drop(card,(W-cw)//2,cy)
yb=cy+card.height
if PRICE:
    pill(W//2+cw//2-200,yb-10,PRICE,96,fg=WHITE,bgc=BLUE)
# QR cards
def qr_card(path,crop,label,sub,cx,cy,size=560):
    q=Image.open(path).convert('RGB')
    if 'paypal' in path: ImageDraw.Draw(q).rectangle((862,862,q.width,q.height),fill=(255,255,255))
    if crop: q=q.crop(crop)
    q=q.resize((size,int(q.height*size/q.width)),Image.LANCZOS)
    pad=40; cardh=q.height+2*pad+150
    c=Image.new('RGB',(size+2*pad,cardh),(255,255,255)); c.paste(q,(pad,pad))
    cd=ImageDraw.Draw(c); fl=ImageFont.truetype(ANTON,70); fs=ImageFont.truetype(BEBAS,50)
    cd.text((c.width//2,q.height+pad+55),label,font=fl,fill=BLUE,anchor='mm')
    cd.text((c.width//2,q.height+pad+118),sub,font=fs,fill=(60,60,70),anchor='mm')
    c=rounded(c,36); drop(c,cx-c.width//2,cy,blur=20,off=10,op=140); return c
qy=yb+55
qr_card(D+'qr-paypal.jpg',None,'PAY HERE','SCAN · PAYPAL',W//2-290,qy,380)
qr_card(D+'qr-instagram.jpg',(100,40,610,550),'FOLLOW US','@LLLAVISHCLO',W//2+290,qy,380)
T((W//2,H-48),'PICK YOUR PIECE  ·  SCAN & PAY  ·  TAG US',BEBAS,46,(200,200,205))
out=im.convert('RGB')
name='flyer-snr-flannel-A5'+('' if PRICE else '')
out.save(D+name+'.png'); out.save(D+name+'.pdf',resolution=300)
out.resize((W//2,H//2)).save('/tmp/claude-0/-home-user-Claude-get-know-me/7bd8ffaf-4328-57e9-93a7-5533880e7614/scratchpad/flyer_prev.jpg')
print('qr bottom', qy)

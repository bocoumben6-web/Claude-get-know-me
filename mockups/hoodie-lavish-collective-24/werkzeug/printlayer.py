import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
S=2; H,W=1250*S,1450*S
rng=np.random.default_rng(5)
ANTON='/tmp/claude-0/-home-user-Claude-get-know-me/7bd8ffaf-4328-57e9-93a7-5533880e7614/scratchpad/fonts/Anton-Regular.ttf'
BEBAS='/home/user/Claude-get-know-me/assets/fonts/BebasNeue-Regular.ttf'
def text_mask(txt,font,box,size=400):
    f=ImageFont.truetype(font,size); im=Image.new('L',(size*len(txt)+200,size*2),0)
    ImageDraw.Draw(im).text((50,50),txt,font=f,fill=255)
    a=np.array(im); ys,xs=np.where(a>0); a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
    x0,y0,x1,y1=[v*S for v in box]
    out=np.zeros((H,W),np.float32); out[y0:y1,x0:x1]=cv2.resize(a,(x1-x0,y1-y0),interpolation=cv2.INTER_AREA)/255
    return out
def grunge(scale,thr,amt):
    n=cv2.resize(rng.standard_normal((H//scale+2,W//scale+2)).astype(np.float32),(W,H),interpolation=cv2.INTER_CUBIC)
    sp=rng.random((H,W)).astype(np.float32)
    sp=cv2.GaussianBlur((sp>0.985).astype(np.float32),(0,0),1.2)*3
    return np.clip(1-amt*(np.clip(n-thr,0,1)*2+sp*(n>thr-0.8)),0,1)
# tonal LAVISH / COLLECTIVE (darker olive ink, low contrast)
lav=text_mask('LAVISH',ANTON,(605,580,857,645))
col=text_mask('COLLECTIVE',ANTON,(603,650,850,692))
fade=np.clip(1-(np.mgrid[0:H,0:W][0]/S-650)/60,0.35,1)   # COLLECTIVE fades out toward bottom
tonal=np.clip(lav+col*fade*(np.mgrid[0:H,0:W][0]>=650*S),0,1)*grunge(6,1.3,0.35)
# 2 / 4 off-white numbers, distressed
two=text_mask('2',BEBAS,(791,561,838,658)); four=text_mask('4',BEBAS,(786,678,836,773))
xx=np.mgrid[0:H,0:W][1].astype(np.float32)/S
side=np.clip((xx-800)/35,0,1)**1.5                       # distress heavier toward right edge of the numbers
sp=cv2.GaussianBlur((rng.random((H,W))>0.84).astype(np.float32),(0,0),0.9)
sp2=cv2.GaussianBlur((rng.random((H,W))>0.97).astype(np.float32),(0,0),1.6)
dis=np.clip((sp*2.0+sp2*2.6)*(0.15+0.85*side),0,1)
nums=np.clip(two+four,0,1)*(1-dis)
# EST. 2024 badge
x0,y0,x1,y1=[v*S for v in (691,712,775,748)]
bd=Image.new('L',(W,H),0); ImageDraw.Draw(bd).rounded_rectangle((x0,y0,x1,y1),radius=7*S,fill=255)
badge=np.array(bd).astype(np.float32)/255
est=text_mask('EST. 2024',BEBAS,(700,720,766,741))
badge=badge*(1-0.6*np.clip(cv2.GaussianBlur((rng.random((H,W))>0.97).astype(np.float32),(0,0),0.9)*2,0,1))
np.save('p_tonal.npy',tonal); np.save('p_nums.npy',nums); np.save('p_badge.npy',badge); np.save('p_est.npy',est)

import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
rng=np.random.default_rng(11)
S=2
lab0=np.load('labels.npy'); garment0=np.load('garment.npy'); hole0=np.load('hole.npy'); outline0=np.load('outline.npy')
H0,W0=lab0.shape; H,W=H0*S,W0*S
def up(m,sig=2.5):
    f=cv2.resize(m.astype(np.float32),(W,H),interpolation=cv2.INTER_LINEAR)
    f=cv2.GaussianBlur(f,(0,0),sig); return np.clip((f-0.5)*3+0.5,0,1)
parts={'hood':21,'body':36,'sleeveL':105,'sleeveR':121,'cuffL':278,'cuffR':282,'hem':292}
others=np.isin(lab0,[v for k,v in parts.items() if k!='hood'])
others=cv2.dilate(others.astype(np.uint8),np.ones((9,9)))>0
yy0=np.mgrid[0:H0,0:W0][0]
hood0=garment0&~hole0&~others&(yy0<400)
lab0=lab0.copy(); lab0[hood0]=21
sm=lambda m: cv2.GaussianBlur(m.astype(np.float32),(0,0),3)>0.5
garment0=sm(garment0)
P={k:up(cv2.dilate((lab0==v).astype(np.uint8),np.ones((5,5)))&garment0) for k,v in parts.items()}
G=up(garment0,3.0); HO=up(hole0,2.0)
# pocket mask from outline subset
po=outline0.copy(); po[:840]=0; po[1065:]=0; po[:, :500]=0; po[:, 980:]=0
po=cv2.morphologyEx(po.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((9,9)))
c,_=cv2.findContours(po,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); pk=np.zeros_like(po); cv2.drawContours(pk,[max(c,key=cv2.contourArea)],-1,1,-1)
PK=up(pk)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def noise(scale,oct=3,ax=1.0,ay=1.0):
    out=np.zeros((H,W),np.float32); a=1
    for o in range(oct):
        s=max(2,int(scale/(2**o)))
        n=rng.standard_normal((int(H//(s*ay))+3,int(W//(s*ax))+3)).astype(np.float32)
        out+=a*cv2.resize(n,(W,H),interpolation=cv2.INTER_CUBIC); a*=0.55
    return out/out.std()
def dist(m,r):
    d=cv2.distanceTransform((m>0.5).astype(np.uint8),cv2.DIST_L2,5); return 1-np.exp(-d/r)
# ---------- shading (puff per panel, seams) ----------
puff=np.zeros((H,W),np.float32)
for k,m in P.items(): puff=np.maximum(puff,dist(m,(28 if 'cuff' in k or k=='hem' else 55)*S/2)*(m>0.5))
pk_puff=dist(PK,30)
puff=np.where(PK>0.5,0.55+0.45*pk_puff*puff.clip(0.6,1),puff)
shade=0.74+0.26*puff
# seams from outlines
edge0=cv2.dilate((~garment0).astype(np.uint8),np.ones((15,15)))>0
holeedge=cv2.dilate(hole0.astype(np.uint8),np.ones((13,13)))>0
inner_ol=outline0&~edge0&~holeedge; inner_ol[:340]=False
ol=up(inner_ol,1.2)
seam=cv2.GaussianBlur(ol,(0,0),1.6)
shade*=1-0.35*seam
hl=np.roll(np.roll(cv2.GaussianBlur(ol,(0,0),2.5),3,0),2,1)
shade*=1+0.06*np.clip(hl-seam,0,1)
# pocket casts soft shadow on body
psh=cv2.GaussianBlur(np.roll(PK,7,0),(0,0),7)*(1-PK)
shade*=1-0.22*psh
# creases (soft folds)
def crease(p0,p1,w,a):
    p0=np.array(p0,np.float32)*S; p1=np.array(p1,np.float32)*S
    d=p1-p0; L=np.linalg.norm(d); u=d/L
    t=np.clip(((xx-p0[0])*u[0]+(yy-p0[1])*u[1])/L,0,1)
    px=p0[0]+t*d[0]; py=p0[1]+t*d[1]
    r=np.hypot(xx-px,yy-py); taper=np.clip(np.sin(np.pi*t),0,1)**0.7
    return a*taper*(np.exp(-(r/(w*S))**2)-0.6*np.exp(-((r-w*S*1.3)/(w*S*0.8))**2))
fold=np.zeros((H,W),np.float32)
for c in [((330,560),(420,640),9,0.10),((250,640),(360,720),10,0.09),((180,760),(290,820),9,0.12),((120,850),(230,900),8,0.12),((90,900),(190,950),7,0.1),
          ((1150,560),(1060,640),9,0.10),((1230,650),(1120,720),10,0.09),((1300,760),(1190,820),9,0.12),((1350,860),(1250,900),8,0.12),((1390,920),(1290,960),7,0.1),
          ((480,600),(560,720),12,0.06),((990,600),(910,720),12,0.06),((470,1020),(990,1030),10,0.05),((520,330),(600,300),8,0.06)]:
    fold+=crease(*c)
shade*=1-fold
# ---------- base color + sand wash ----------
base=np.array([74,82,34],np.float32)       # olive (design ~77/86/34)
faded=np.array([150,152,116],np.float32)    # sun/sand-faded olive
wash=0.55*noise(320,3)+0.4*noise(110,2,ax=2.2)+0.18*noise(28,2,ax=3)
wash=(wash-wash.mean())/wash.std()
gy=(yy-yy[G>0.5].min())/(np.ptp(yy[G>0.5])+1)
rib=np.zeros((H,W),np.float32); ribm=np.zeros((H,W),np.float32)
for k in ['cuffL','cuffR','hem']: ribm=np.maximum(ribm,P[k])
F=np.clip(0.66-0.40*gy+0.22*wash,0,1)                 # 0..1 fade amount
F*=0.35+0.65*puff                                 # seams/edges keep dye
F*=1-0.55*ribm                                    # ribbing stays darker
F*=1-0.45*fold.clip(0,1)/0.12
F=np.clip(F*0.85,0,1)
col=base[None,None]*(1-F[...,None])+faded[None,None]*F[...,None]
# ribbing texture
for k,m in [('cuffL',P['cuffL']),('cuffR',P['cuffR']),('hem',P['hem'])]:
    ys,xs=np.where(m>0.5); pts=np.stack([xs,ys],1).astype(np.float32); mu=pts.mean(0)
    _,_,vt=np.linalg.svd(pts-mu,full_matrices=False); ax=vt[0]
    u=(xx-mu[0])*ax[0]+(yy-mu[1])*ax[1]
    rib+=m*np.cos(2*np.pi*u/(4.2*S))
fleece=cv2.GaussianBlur(rng.standard_normal((H,W)).astype(np.float32),(0,0),0.9); fleece/=fleece.std()
heather=noise(6,2)
lum=shade*(1+0.10*rib)*(1+0.025*fleece+0.02*heather)
img=col*lum[...,None]
# ---------- hood opening ----------
hd=dist(HO,40)
inside=np.array([44,49,22],np.float32)*(0.55+0.45*np.clip((yy-yy[HO>0.5].min())/((yy[HO>0.5].max()-yy[HO>0.5].min())+1),0,1))[...,None]
waffle=(np.cos(2*np.pi*xx/(5*S))*np.cos(2*np.pi*yy/(5*S)))
inside=inside*(1+0.08*waffle)[...,None]*(0.75+0.25*hd)[...,None]
img=img*(1-HO[...,None])+inside*HO[...,None]
# rim highlight around opening
rim=cv2.GaussianBlur(cv2.dilate((HO>0.5).astype(np.uint8),np.ones((9,9))).astype(np.float32)-(HO>0.5),(0,0),3)
img*= (1+0.12*rim)[...,None]
np.save('img_noprint.npy',img); np.save('G.npy',np.maximum(G,HO)); np.save('shade.npy',shade); np.save('F.npy',F); np.save('rib.npy',rib)
print('ok',H,W)

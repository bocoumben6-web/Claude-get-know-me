import cv2, numpy as np
O='/home/user/Claude-get-know-me/mockups/hoodie-lavish-collective-24/'
img=np.load('img_final.npy'); G=np.load('G.npy')
ys,xs=np.where(G>0.02); y0,y1,x0,x1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
img=img[y0:y1,x0:x1]; G=G[y0:y1,x0:x1]
# transparent PNG
rgba=np.dstack([cv2.cvtColor(np.clip(img,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR),(G*255).astype(np.uint8)])
cv2.imwrite(O+'hoodie-olive-freigestellt.png',rgba)
# Lavish gray 3:4
TW,TH=2400,3200
yy,xx=np.mgrid[0:TH,0:TW].astype(np.float32)
bgv=229-7*np.clip((yy/TH-0.75)/0.25,0,1)**1.5-3*((xx-TW/2)/TW)**2*4
bg=np.dstack([bgv-0.5,bgv,bgv+0.5])  # RGB
s=TW*0.82/img.shape[1]
im=cv2.resize(img.astype(np.float32),None,fx=s,fy=s,interpolation=cv2.INTER_AREA); a=cv2.resize(G,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
h,w=a.shape; ox=(TW-w)//2; oy=int(TH*0.46-h/2)
A=np.zeros((TH,TW),np.float32); A[oy:oy+h,ox:ox+w]=a
F=np.zeros((TH,TW,3),np.float32); F[oy:oy+h,ox:ox+w]=im
sh1=cv2.GaussianBlur(np.roll(A,26,0),(0,0),45); sh2=cv2.GaussianBlur(np.roll(A,6,0),(0,0),6)
c=bg*(1-0.14*sh1-0.18*sh2)[...,None]
c=c*(1-A[...,None])+F*A[...,None]
c+=np.random.default_rng(2).standard_normal((TH,TW,1))*1.6
out=cv2.cvtColor(np.clip(c,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)
cv2.imwrite(O+'hoodie-olive-grau-3x4.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,94])
cv2.imwrite('final_prev.jpg',cv2.resize(out,(900,1200)))

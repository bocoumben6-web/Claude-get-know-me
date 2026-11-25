import cv2, numpy as np
im=cv2.imread('/home/user/Claude-get-know-me/mockups/hoodie-lavish-collective-24/design/design-foto.jpg')[430:1680]
hsv=cv2.cvtColor(cv2.GaussianBlur(im,(0,0),1.5),cv2.COLOR_BGR2HSV).astype(int)
H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
green=(H>22)&(H<50)&(S>70)
dark=(V<52)
gray=(S<40)&(V>120)&(V<215)
def fill(m):
    c,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    o=np.zeros(m.shape,np.uint8); cv2.drawContours(o,[max(c,key=cv2.contourArea)],-1,1,-1); return o>0
g=cv2.morphologyEx(green.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((5,5)))
n,l,st,_=cv2.connectedComponentsWithStats(g); i=1+np.argmax(st[1:,4]); g=l==i
garment=fill(cv2.dilate(g.astype(np.uint8),np.ones((7,7)))>0)
garment=cv2.erode(garment.astype(np.uint8),np.ones((3,3)))>0
hole=gray&garment
n,l,st,_=cv2.connectedComponentsWithStats(hole.astype(np.uint8)); i=1+np.argmax(st[1:,4]); hole=fill(l==i)
outline=dark&garment&~hole
outline=cv2.morphologyEx(outline.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((3,3)))>0
# print inks (exclude from outline logic)
ink=(S<60)&(V>170)&garment&~hole
inner=garment&~cv2.dilate(outline.astype(np.uint8),np.ones((5,5)))&~cv2.dilate(hole.astype(np.uint8),np.ones((5,5)))
n,l,st,cen=cv2.connectedComponentsWithStats(inner.astype(np.uint8),connectivity=4)
np.save('garment.npy',garment); np.save('hole.npy',hole); np.save('outline.npy',outline); np.save('labels.npy',l)
vis=np.zeros(im.shape,np.uint8); rng=np.random.default_rng(0)
for k in range(1,n):
    if st[k,4]>800:
        vis[l==k]=rng.integers(60,255,3); print(k,st[k],cen[k].astype(int))
vis[outline]=0; vis[hole]=(128,128,128)
cv2.imwrite('parts.jpg',cv2.resize(vis,(725,625)))

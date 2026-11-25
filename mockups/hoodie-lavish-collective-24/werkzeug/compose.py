import cv2, numpy as np
img=np.load('img_noprint.npy'); G=np.load('G.npy'); shade=np.load('shade.npy'); rib=np.load('rib.npy')
tonal=np.load('p_tonal.npy'); nums=np.load('p_nums.npy'); badge=np.load('p_badge.npy'); est=np.load('p_est.npy')
H,W=G.shape
fleece=cv2.GaussianBlur(np.random.default_rng(9).standard_normal((H,W)).astype(np.float32),(0,0),0.8)
tex=(shade*(1+0.03*fleece))[...,None]
# tonal: darkens fabric (dye-like), fades with wash
t=cv2.GaussianBlur(tonal,(0,0),0.7)[...,None]*0.72
tink=np.array([58,66,24],np.float32)
img=img*(1-t)+tink*tex*t
ink=np.array([226,224,204],np.float32)
a=cv2.GaussianBlur(np.clip(nums+badge,0,1),(0,0),0.7)[...,None]*0.93
img=img*(1-a)+ink*tex*a
estc=np.array([92,98,48],np.float32)
e=cv2.GaussianBlur(est,(0,0),0.6)[...,None]*(badge[...,None]>0.3)
img=img*(1-e)+estc*tex*e
np.save('img_final.npy',np.clip(img,0,255))
o=img*G[...,None]+np.array([229,228,228])*(1-G[...,None])
o=cv2.cvtColor(np.clip(o,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)
cv2.imwrite('prev.jpg',cv2.resize(o,(1160,1000))); cv2.imwrite('zoom.jpg',o[1000:1600,1100:1800])

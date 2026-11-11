import cv2, numpy as np, subprocess, sys
W,H=576,1024
dec=subprocess.Popen(["ffmpeg","-loglevel","error","-i","src.mp4","-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","bgr24","-s","576x1024","-r","30","-i","-",
 "-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-crf","12","-preset","fast","clean.mp4"],stdin=subprocess.PIPE)
k=np.ones((3,3),np.uint8); i=0
while True:
    buf=dec.stdout.read(W*H*3)
    if len(buf)<W*H*3: break
    f=np.frombuffer(buf,np.uint8).reshape(H,W,3).copy()
    b,g,r=[f[:,:,c].astype(int) for c in range(3)]
    m=np.zeros((H,W),np.uint8)
    yel=(r>140)&(g>100)&(b<130)&(r-b>70)
    band=np.zeros_like(yel); band[595:715,30:546]=True
    ym=(yel&band).astype(np.uint8)
    # shadow: dark pixels right/below yellow
    near=cv2.dilate(ym,np.ones((7,7),np.uint8))
    dark=((r+g+b)<200)&(near>0)
    m|=ym|dark.astype(np.uint8)
    if i<72:
        bei=(r>225)&(g>212)&(b>190)&(r-b>8)
        reg=np.zeros_like(bei); reg[130:370,60:520]=True
        m|=(bei&reg).astype(np.uint8)
    m=cv2.dilate(m*255,k,iterations=2)
    if m.any(): f=cv2.inpaint(f,m,4,cv2.INPAINT_TELEA)
    enc.stdin.write(f.tobytes()); i+=1
enc.stdin.close(); enc.wait(); print("frames",i)

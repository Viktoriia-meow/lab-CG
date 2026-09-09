import numpy as np
from PIL import Image 
from math import floor
v=[]
f=[]
file=open('model.obj')
for s in file:
    s1=s.split()
    if (s1[0]=='v'):
        v.append(s1[1:4])
    if(s1[0]=='f'):
        s2=s1[1].split('/')
        s3=s1[2].split('/')
        s4=s1[3].split('/')
        f.append([int(s2[0]),int(s3[0]),int(s4[0])])
v=[list(map(float,k)) for k in v]

img_mat=np.zeros((1000,1000,3), dtype=np.uint8)
x0,y0,x1,y1=12.0,18.0,200.0,100.0

def line(img_mat,x0,x1,y0,y1):
     dmax=max(abs(floor(x0)-floor(x1)),abs(floor(y0)-floor(y1))) #наиб расстояние по осям
     L=dmax+1 #кол-во точек
     if L==1:
         img_mat[floor(y0),floor(x0)]=[255,0,255]
         return
     dx=(x1-x0)/(L-1)
     dy=(y1-y0)/(L-1)
     for _ in range (L):
        img_mat[floor(y0),floor(x0)]=[255,0,255]
        x0+=dx
        y0+=dy
    

for i in range(len(v)):
    x=v[i][0]*5000-300
    y=-v[i][1]*5000
    img_mat[floor(y),floor(x)]=[255,0,255]


for i in range(len(f)):
    x0=v[f[i][0]-1][0]*5000-300
    y0=-v[f[i][0]-1][1]*5000
    x1=v[f[i][1]-1][0]*5000-300
    y1=-v[f[i][1]-1][1]*5000
    x2=v[f[i][2]-1][0]*5000-300
    y2=v[f[i][2]-1][0]*5000
    line(img_mat,x0,x1,y0,y1)
    line(img_mat,x0,x2,y0,y2)
    line(img_mat,x1,x2,y1,y2)

img=Image.fromarray (img_mat)
img.save('img.png')
import numpy as np
from PIL import Image 
from math import floor
from math import ceil
import random
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
z_buf = np.full((1000,1000),10**10,dtype = np.float32)
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
    

# for i in range(len(v)):
#     x=v[i][0]*5000-300
#     y=-v[i][1]*5000
#     img_mat[floor(y),floor(x)]=[255,0,255]


# for i in range(len(f)):
#     x0=v[f[i][0]-1][0]*5000-300
#     y0=-v[f[i][0]-1][1]*5000
#     x1=v[f[i][1]-1][0]*5000-300
#     y1=-v[f[i][1]-1][1]*5000
#     x2=v[f[i][2]-1][0]*5000-300
#     y2=v[f[i][2]-1][0]*5000
#     line(img_mat,x0,x1,y0,y1)
#     line(img_mat,x0,x2,y0,y2)
#     line(img_mat,x1,x2,y1,y2)
def triangle(x0,y0,z0,x1,y1,z1,x2,y2,z2):
    xmin = floor(min(x0, x1, x2))
    ymin = floor(min(y0, y1, y2))
    if (xmin < 0): xmin = 0
    if (ymin < 0): ymin = 0
    xmax = ceil(max(x0, x1, x2))
    ymax = ceil(max(y0, y1, y2))
    if (xmax >1000): xmax = 1000
    if (ymax >1000): ymax = 1000
    zbuff = 10**10
    r = -230*cut_nofacegran(x0,y0,z0,x1,y1,z1,x2,y2,z2)
    g = 0
    b = -230*cut_nofacegran(x0,y0,z0,x1,y1,z1,x2,y2,z2)
    for x in range(xmin,xmax):
        for y in range(ymin,ymax):
            l1, l2,l3 = lambdas(x,y,x0,y0,x1,y1,x2,y2)
            if l1>=0 and l2>0 and l3>0 and cut_nofacegran(x0,y0,z0,x1,y1,z1,x2,y2,z2) :
                z = l1*z0 + l2*z1 + l3*z2
                if z > z_buf[y,x]:continue
                elif z < z_buf[y,x]:
                    img_mat[y,x]=[r,g,b]
                    z_buf[y,x] = z

def lambdas(x,y,x0,y0,x1,y1,x2,y2):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return [lambda0, lambda1, lambda2]

def normal(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2):
    v1 = (X1-X2, Y1-Y2, Z1-Z2)
    v2 = (X1-X0, Y1-Y0, Z1-Z0)
    return np.cross(v1,v2)

def cut_nofacegran(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2):
    n = normal(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2)
    a=np.dot(n,[0,0,1])
    b=np.linalg.norm(n)* np.linalg.norm([0,0,1])
    return a/b


for i in range(len(f)):
    x0=v[f[i][0]-1][0]*4000+830
    y0=-v[f[i][0]-1][1]*4000+1000
    x1=v[f[i][1]-1][0]*4000+830
    y1=-v[f[i][1]-1][1]*4000+1000
    x2=v[f[i][2]-1][0]*4000+830
    y2=-v[f[i][2]-1][1]*4000+1000
    z0=v[f[i][0]-1][2]*4000+830
    z1=v[f[i][1]-1][2]*4000+830
    z2=v[f[i][2]-1][2]*4000+830
    triangle(x0,y0,z0,x1,y1,z1,x2,y2,z2)


img=Image.fromarray (img_mat)
img.save('img.png')

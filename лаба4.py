import numpy as np
from PIL import Image,ImageTk 
from math import floor
from math import ceil
from numba import njit
import tkinter as tk 
import random
v=[]
f=[]

height = 1000
width = 1000
scale = 4000

img_mat=np.zeros((height,width,3), dtype=np.uint8)
z_buf = np.full((height,width),10**10,dtype = np.float32)
x0,y0,x1,y1=12.0,18.0,200.0,100.0

def Rotation(angX, angY, angZ, v, tx, ty, tz):
    Rx = np.array([[1, 0, 0], [0, np.cos(angX), np.sin(angX)], [0, -np.sin(angX), np.cos(angX)]])
    Ry = np.array([[np.cos(angY), 0, np.sin(angY)], [0, 1, 0], [-np.sin(angY), 0, np.cos(angY)]])
    Rz = np.array([[np.cos(angZ), np.sin(angZ), 0], [-np.sin(angZ), np.cos(angZ), 0], [0, 0, 1]])
    R = Rx @ Ry @ Rz
    v_non = v @ R.T + np.array([tx, ty, tz])
    return v_non



@njit(cache=True)
def render_model(img_mat,zbuf, cx,cy, scale, v, f, flag_proection):
    img_mat[...] = 0
    zbuf[...] = np.inf
    height,width = img_mat.shape[0:2]
    for i in range(len(f)):
        x0, y0, z0 = v[f[i][0]-1][0], v[f[i][0]-1][1], v[f[i][0]-1][2]
        x1, y1, z1 = v[f[i][1]-1][0], v[f[i][1]-1][1], v[f[i][1]-1][2]
        x2, y2, z2 = v[f[i][2]-1][0], v[f[i][2]-1][1], v[f[i][2]-1][2] 
        if flag_proection == True:
            px0, py0 = (x0 * scale) + width/2, -(y0 * scale ) +  height/2
            px1, py1 = (x1 * scale) + width/2, -(y1 * scale) +  height/2
            px2, py2 = (x2 * scale) + width/2, -(y2 * scale) +  height/2
        if flag_proection == False:
            px0, py0 = (x0 * scale) / z0 + width/2, -(y0 * scale ) / z0 +  height/2
            px1, py1 = (x1 * scale) / z1 + width/2, -(y1 * scale) / z1 +  height/2
            px2, py2 = (x2 * scale) / z2 + width/2, -(y2 * scale) / z2 +  height/2
        cosinus = cut_nofacegran(x0, y0, z0,x1, y1, z1, x2, y2, z2)
        triangle(px0,py0,z0,px1,py1,z1,px2,py2,z2,cosinus,img_mat,zbuf)
@njit(cache=True)
def triangle(px0,py0,z0,px1,py1,z1,px2,py2,z2,cosinus,img_mat,zbuf):
        if cosinus <= 0:return
        height,width = img_mat.shape[0:2]
        xmin = floor(min(px0, min(px1, px2)))
        ymin = floor(min(py0,min( py1, py2)))
        if (xmin < 0): xmin = 0
        if (ymin < 0): ymin = 0
        xmax = ceil(max(px0, max(px1, px2)))
        ymax = ceil(max(py0, max(py1, py2)))
        if (xmax > width): xmax = width
        if (ymax > height): ymax = height
        zbuff= 10**10
        rgb = int(230*cosinus)
        rgb = max(0,min(255, rgb))
        color = [rgb,0,rgb]
        
        for x in range(xmin,xmax):
            for y in range(ymin,ymax):
                l1, l2,l3 = lambdas(x,y,px0,py0,px1,py1,px2,py2)
                if l1>=0 and l2>0 and l3>0 and cut_nofacegran(px0,py0,z0,px1,py1,z1,px2,py2,z2) :
                    z = l1*z0 + l2*z1 + l3*z2
                    if z > zbuf[y,x]:continue
                    elif z < zbuf[y,x]:
                        img_mat[y,x]= color
                        zbuf[y,x] = z
@njit(cache=True)
def lambdas(x,y,x0,y0,x1,y1,x2,y2):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return [lambda0, lambda1, lambda2]
@njit(cache=True)
def normal(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2):
    ux, uy, uz = X1-X2, Y1-Y2, Z1-Z2
    vx, vy, vz = X1-X0, Y1-Y0, Z1-Z0

    nx = uy*vz - uz*vy
    ny = uz*vx - ux*vz
    nz = ux*vy - uy*vx

    return [-nx, -ny, -nz]
@njit(cache=True)
def cut_nofacegran(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2):
    n = normal(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2)

    a = n[2]
    b = np.sqrt(n[0]*n[0] + n[1]*n[1] + n[2]*n[2])

    if b == 0: return 0.0

    return a/b


class Scene :
    def __init__(self,file):
        self.v = []
        self.f = []
        for s in file:
            s1=s.split()
            if (s1[0]=='v'):
                self.v.append(s1[1:4])
            if(s1[0]=='f'):
                s2=s1[1].split('/')
                s3=s1[2].split('/')
                s4=s1[3].split('/')
                self.f.append([int(s2[0]),int(s3[0]),int(s4[0])])
        self.v=np.array(self.v,dtype=np.float64)
        self.f=np.array(self.f,dtype=np.int32)

class Renderer : 
    def __init__(self, width, height, scale):
        self.height, self.width = height, width
        self.scale = scale

        self.img_mat = np.zeros((height, width, 3), dtype=np.uint8)
        self.z_buf = np.full((height, width), np.inf, dtype=np.float32)

        self.cx = self.width / 2.0
        self.cy = self.height / 2.0
        self.angX = 0.0
        self.angY = 0.0
        self.angZ = 0.0
        self.tx = 0.0
        self.ty = 0.0
        self.tz = 1.0
        self.flag_proection = True
    def Render(self, scene):
        v = Rotation(self.angX, self.angY, self.angZ, scene.v, self.tx, self.ty, self.tz)
        render_model(self.img_mat, self.z_buf,self.cx, self.cy, self.scale, v, scene.f, self.flag_proection)


class App:
    def __init__(self, scene, renderer, win_w = 900, win_h = 900):
        self.scene = scene
        self.renderer = renderer

        # Оставляем как есть
        # Окно верхнего уровня
        self.root = tk.Tk()
        # Размеры окна
        self.root.geometry(f"{win_w}x{win_h}")
        # Область для рисования внутри окна
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.focus_set()
        # Обновление изображения при изменении размеров окна
        self.canvas.bind('<Configure>', lambda e: self._refit())
        # Привязка обработчика клавиш
        self.root.bind('<Key>', self.on_key)

        # Изображение внутри окна
        self.photo = None
        self.full_image = None

        self.render()
    def on_key(self, event):
        k = event.keysym

        if k == 'Left':
            self.renderer.tx -= 0.01
        elif k == 'Right':
            self.renderer.tx += 0.01
        elif k == '=':
            self.renderer.scale *= 1.1
        elif k == '-':
            self.renderer.scale /= 1.1
        elif k == 'Up':
            self.renderer.ty += 0.01
        elif k == 'Down':
            self.renderer.ty -= 0.01
        elif k == 'm':
            self.renderer.tz += 0.01
        elif k == 'n':
            self.renderer.tz -= 0.01
        elif k == 'a':
            self.renderer.angX -= 0.1
        elif k == 'd':
            self.renderer.angX += 0.1
        elif k == 'w':
            self.renderer.angY += 0.1
        elif k == 's':
            self.renderer.angY -= 0.1
        elif k == 't':
            self.renderer.angZ += 0.1
        elif k == 'r':
            self.renderer.angZ -= 0.1
        elif k == '0':
            self.renderer.flag_proection = not(self.renderer.flag_proection)
        elif k == 'space':
            Image.fromarray(self.renderer.img_mat).save('sphere.png')
            return 'break'
        else:
            return

        self.render()
        # Не обрабатываем дальше – return 'brake'
        return 'break'
    def render(self):
        self.renderer.Render(self.scene)
        self.full_image = Image.fromarray(self.renderer.img_mat)
        self._refit()

    # скопировать как есть
    def _refit(self):
        # Если ещё не отрендерилось, пропускаем
        if self.full_image is None: return
        # Ширина и высота области для рисования
        ww = self.canvas.winfo_width()
        wh = self.canvas.winfo_height()
        # Если вдруг сделали область слишком маленькой
        if ww < 10 or wh < 10: return
        # Вписать с сохранением пропорций
        s = min(ww / self.renderer.width, wh / self.renderer.height)
        dw = max(1, int(self.renderer.width * s))
        dh = max(1, int(self.renderer.height * s))
        disp = self.full_image.resize((dw, dh), Image.BILINEAR)
        # Очень важно сохранить ImageTk.PhotoImage(disp) в поле класса
        # Если оно будет локальным, то удалится после выхода сборщиком мусора
        self.photo = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(ww // 2, wh // 2, image=self.photo)   
            # скопировать как есть
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    file = open('model.obj')
    scene = Scene(file)
    renderer = Renderer(1000,1000,4000)
    App(scene, renderer).run()

# img=Image.fromarray (renderer.img_mat)
# img.save('img.png')



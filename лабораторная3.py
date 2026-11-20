import numpy as np
from PIL import Image,ImageTk 
from math import floor
from math import ceil
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

def render_model(scene,img_mat,zbuf, cx,cy, scale, v, f):
    img_mat[...] = 0
    zbuf[...] = np.inf
    height,width = img_mat.shape[0:2]
    for i in range(len(f)):
        x0, y0, z0 = v[f[i][0]-1][0], v[f[i][0]-1][1], v[f[i][0]-1][2]
        x1, y1, z1 = v[f[i][1]-1][0], v[f[i][1]-1][1], v[f[i][1]-1][2]
        x2, y2, z2 = v[f[i][2]-1][0], v[f[i][2]-1][1], v[f[i][2]-1][2] 
        px0, py0 = x0 * scale + width/2, -y0 * scale +  height/2
        px1, py1 = x1 * scale + width/2, -y1 * scale +  height/2
        px2, py2 = x2 * scale + width/2, -y2 * scale +  height/2
        cosinus = cut_nofacegran(x0, y0, z0,x1, y1, z1, x2, y2, z2)
        triangle(px0,py0,z0,px1,py1,z1,px2,py2,z2,cosinus,img_mat,zbuf)
        
def triangle(px0,py0,z0,px1,py1,z1,px2,py2,z2,cosinus,img_mat,zbuf):
        if cosinus <= 0:return
        xmin = floor(min(px0, px1, px2))
        ymin = floor(min(py0, py1, py2))
        if (xmin < 0): xmin = 0
        if (ymin < 0): ymin = 0
        xmax = ceil(max(px0, px1, px2))
        ymax = ceil(max(py0, py1, py2))
        if (xmax > width): xmax = width
        if (ymax > width): ymax = width
        zbuff = 10**10
        rgb = int(230*cosinus)
        rgb = max(0,min(255, rgb))
        color = [rgb,0,rgb]
        
        for x in range(xmin,xmax):
            for y in range(ymin,ymax):
                l1, l2,l3 = lambdas(x,y,px0,py0,px1,py1,px2,py2)
                if l1>=0 and l2>0 and l3>0 and cut_nofacegran(px0,py0,z0,px1,py1,z1,px2,py2,z2) :
                    z = l1*z0 + l2*z1 + l3*z2
                    if z > z_buf[y,x]:continue
                    elif z < z_buf[y,x]:
                        img_mat[y,x]= color
                        z_buf[y,x] = z

def lambdas(x,y,x0,y0,x1,y1,x2,y2):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda2 = 1.0 - lambda0 - lambda1
    return [lambda0, lambda1, lambda2]

def normal(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2):
    v1 = (X1-X2, Y1-Y2, Z1-Z2)
    v2 = (X1-X0, Y1-Y0, Z1-Z0)
    return -np.cross(v1,v2)

def cut_nofacegran(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2):
    n = normal(X0,Y0,Z0,X1,Y1,Z1,X2,Y2,Z2)
    a=np.dot(n,[0,0,1])
    b=np.linalg.norm(n)* np.linalg.norm([0,0,1])
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
        self.v=[list(map(float,k)) for k in self.v]

class Renderer : 
    def __init__(self, width, height, scale):
        self.height, self.width = height, width
        self.scale = scale     
        self.img_mat = np.zeros((height,width,3), dtype=np.uint8)
        self.z_buf = np.full((height,width),np.inf,dtype = np.float32)
        self.cx = self.width / 2.0
        self.cy = self.height / 2.0
    def Render(self,scene):
        render_model(scene, self.img_mat, self.z_buf, self.cx, self.cy, self.scale, scene.v, scene.f )

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

        if k == 'plus':
            self.renderer.scale *= 1.1
        elif k == 'minus':
            self.renderer.scale /= 1.1
        elif k == 'q':
            self.scene.diffuse /= 1.1
        elif k == 'w':
            self.scene.diffuse *= 1.1
        elif k == 'a':
            self.scene.specular /= 1.1
        elif k == 's':
            self.scene.specular *= 1.1
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



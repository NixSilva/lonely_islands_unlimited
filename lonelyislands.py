#!/usr/bin/env python2

import pyglet
import sys
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *
from noise import pnoise2
import math
import random
import numpy as np


class Player:
    def __init__(self):
        self.position = np.asarray([0.0, 0.0, 0.0])
        self.rotation = np.asarray([0.0, 0.0])
        self.velocity = np.asarray([0.0, 0.0, 0.0])
        self.mvector  = np.asarray([0.0, 0.0])
        self.norm_vector  = np.asarray([0.0, 0.0])
        self.height = 0.5
        self.speed = 0.1

    def update(self, dt):
        l = np.sqrt(sum(np.asarray(self.mvector)**2))
        if l == 0.0:
            self.norm_vector = (0.0, 0.0)
        else:
            self.norm_vector =  self.mvector / l
        rot = math.degrees(math.atan2(*self.mvector)) + self.rotation[0]
        m = 0.1
        dz = -math.sin(math.radians(rot))*l*m
        dx = -math.cos(math.radians(rot))*l*m
        ratio = 0.02
        ratio2 = 50
        floor = get_v(self.position[0], self.position[2])
        dy = self.velocity[1]
        if self.position[1] >  floor + self.height:
            dy += -0.01
        else:
            dy = 0.0
            self.position[1] = floor + self.height
        self.velocity = [dx, dy, dz]
        self.position += [i * self.speed for i in self.velocity]

def vec(*args):
    return (GLfloat * len(args))(*args)

def update(dt):
    player.update(dt)

window = pyglet.window.Window(600, 600)

label = pyglet.text.Label()

@window.event
def on_mouse_motion(x, y, dx, dy):
    m = 0.15
    x, y = player.rotation
    x, y = x + dx * m, y + dy * m
    y = max(-90, min(90, y))
    x = x - 360.0 if x >= 360.0 else x
    x = x + 360.0 if x < 0.0 else x
    player.rotation = (x, y)

@window.event
def on_key_press(symbol, modifiers):
    if   symbol == key.W:
        player.mvector[0] += 1
    elif symbol == key.S:
        player.mvector[0] -= 1
    elif symbol == key.A:
        player.mvector[1] += 1
    elif symbol == key.D:
        player.mvector[1] -= 1

@window.event
def on_key_release(symbol, modifiers):
    if   symbol == key.W:
        player.mvector[0] -= 1
    elif symbol == key.S:
        player.mvector[0] += 1
    elif symbol == key.A:
        player.mvector[1] -= 1
    elif symbol == key.D:
        player.mvector[1] += 1

def set_2d():
    width = window.width
    height = window.height
    glDisable(GL_DEPTH_TEST)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def set_3d():
    width = window.width
    height = window.height

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT1)
    glMaterialfv(GL_FRONT, GL_SHININESS, vec(50.0));
    glMaterialfv(GL_FRONT, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0));
    glMaterialfv(GL_FRONT, GL_DIFFUSE, vec(1.0, 1.0, 1.0, 1.0));
    glMaterialfv(GL_FRONT, GL_AMBIENT, vec(1.0, 1.0, 1.0, 1.0));
    glLightfv(GL_LIGHT1, GL_AMBIENT, vec(0.1, 0.1, 0.1, 1.0))
    glLightfv(GL_LIGHT1, GL_DIFFUSE, vec(0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT1, GL_POSITION, vec(100.0, 100.0, 100.0, 1.0))
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE);
    glEnable(GL_COLOR_MATERIAL);

    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, vec(0.7, 0.7, 0.7, 1))
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_DENSITY, 0.55)
    glFogf(GL_FOG_START, 0.0)
    glFogf(GL_FOG_END, 30.0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glClearColor(0.7, 0.7, 0.7, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width/float(height), 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y = player.rotation
    glRotatef(x, 0, 1, 0)
    glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
    x, y, z = player.position
    glTranslatef(-x, -y, -z)

@window.event
def on_resize(width, height):
    set_3d()
    return pyglet.event.EVENT_HANDLED

@window.event
def on_draw():
    set_3d()
    terrain_batch.draw()
    batch_test.draw()
    set_2d()
    label.text = str(pyglet.clock.get_fps())
    #label.text = str(player.rotation)
    label.draw()

def get_v(x, z):
    ratio = 0.02
    ratio2 = 50.0
    #return 0.0
    return pnoise2(x*ratio, z*ratio, 4)*ratio2

def get_n(x, z):
    d = 0.01
    dydx = (get_v(x+d, z) - get_v(x-d, z)) / (2 * d)
    dydz = (get_v(x, z+d) - get_v(x, z-d)) / (2 * d)
    n = -np.cross([1.0, dydx, 0.0], [0.0, dydz, 1.0])
    return list(n)

def create_mesh(batch, lx, ly, d = 1):
    w = int(lx) * 2 * d + 1
    h = int(ly) * 2 * d + 1
    listx = np.linspace(-lx,lx, w)
    listy = np.linspace(-ly,ly, h)
    v = []
    n = []
    c = []
    for i in listx:
        for j in listy:
            y = get_v(i, j)
            vv = [i, y, j]
            nn = get_n(i,j)
            v += vv
            n += nn
            vn = [a+b for a,b in zip(vv,nn)]
            if y > 10.0:
                c += [255, 255, 255]
            elif y > 7.0:
                c += [255, 120, 0]
            elif y > 1.0:
                c += [0, 255, 0]
                if random.random() > 0.5:
                    add_tree(batch, i, y, j)
            elif y > 0.0:
                c += [255, 255, 150]
            else:
                c += [0, 0, 255]
    index = []
    for i in range(0,w-1):
        for j in range(0,h-1):
            index += [i+j*w, i+j*w+1, i+j*w+w+1, i+j*w+w]
    batch.add_indexed(w*h, GL_QUADS, None, index,
            ('v3f/static', v), ('n3f/static', n), ('c3B/static', c))

def add_tree(batch, x, y, z):
    batch.add(6, GL_TRIANGLES, None,
            ('v3f/static', (
                -0.2+x, y, 0.0+z,
                0.0+x, y+0.4, 0.0+z,
                0.2+x, y, 0.0+z,
                0.0+x, y,-0.2+z, 
                0.0+x, y+0.4, 0.0+z, 
                0.0+x, y, 0.2+z, 
                )),
            ('c3B/static', (
                0, 255, 0,
                0, 255, 0,
                0, 255, 0,
                0, 255, 0,
                0, 255, 0,
                0, 255, 0,
                )),
            ('n3f/static',(
                0.0, 0.0, 1.0,
                0.0, 0.0, 1.0,
                0.0, 0.0, 1.0,
                1.0, 0.0, 0.0,
                1.0, 0.0, 0.0,
                1.0, 0.0, 0.0,
                )))

if __name__ == '__main__':
    window.set_fullscreen(True)
    player = Player()
    pyglet.clock.schedule_interval(update, 1/120.0)
    terrain_batch = pyglet.graphics.Batch()
    batch_test = pyglet.graphics.Batch()
    n = 20.0
    create_mesh(terrain_batch, n, n, d=1)
    terrain_batch.add_indexed(4, GL_QUADS, None, [0, 1, 2, 3], 
            ('v3f/static', (-n,0,-n, -n,0,n, n,0,n, n,0,-n,)),
            ('c3B/static', (0,0,255, 0,0,255, 0,0,255, 0,0,255,)),
            ('n3f/static', (0,1,0, 0,1,0, 0,1,0, 0,1,0,)))
    window.set_exclusive_mouse(True)
    pyglet.app.run()

import pyglet
import math
import sys
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse


class Window(pyglet.window.Window):

    def __init__(self, player, world, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        self.player = player
        self.world = world

    def vec(self, *args):
        return (GLfloat * len(args))(*args)

    def on_mouse_motion(self, x, y, dx, dy):
        m = 0.15
        x, y = self.player.rotation
        x, y = x + dx * m, y + dy * m
        y = max(-90, min(90, y))
        x = x - 360.0 if x >= 360.0 else x
        x = x + 360.0 if x < 0.0 else x
        self.player.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self.player.mvector[0] += 1
        elif symbol == key.S:
            self.player.mvector[0] -= 1
        elif symbol == key.A:
            self.player.mvector[1] += 1
        elif symbol == key.D:
            self.player.mvector[1] -= 1
        elif symbol == key.F11:
            self.set_fullscreen(False)
        elif symbol == key.ESCAPE:
            sys.exit(0)
            #TODO: Use super key routine

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W:
            self.player.mvector[0] -= 1
        elif symbol == key.S:
            self.player.mvector[0] += 1
        elif symbol == key.A:
            self.player.mvector[1] -= 1
        elif symbol == key.D:
            self.player.mvector[1] += 1

    def set_2d(self):
        width = self.width
        height = self.height
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_light(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT1)
        glMaterialfv(GL_FRONT, GL_SHININESS, self.vec(50.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.vec(1.0, 1.0, 1.0, 1.0))
        glMaterialfv(GL_FRONT, GL_DIFFUSE, self.vec(1.0, 1.0, 1.0, 1.0))
        glMaterialfv(GL_FRONT, GL_AMBIENT, self.vec(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, self.vec(0.1, 0.1, 0.1, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, self.vec(0.5, 0.5, 0.5, 1.0))
        glLightfv(GL_LIGHT1, GL_SPECULAR, self.vec(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT1, GL_POSITION, self.vec(100.0, 100.0, 100.0, 1.0))
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)

    def set_fog(self):
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, self.vec(0.7, 0.7, 0.7, 1))
        glHint(GL_FOG_HINT, GL_DONT_CARE)
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_DENSITY, 0.55)
        glFogf(GL_FOG_START, 0.0)
        glFogf(GL_FOG_END, 30.0)

    def set_3d(self):
        width = self.width
        height = self.height

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
        x, y = self.player.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.player.position
        glTranslatef(-x, -y, -z)

    def on_resize(self, width, height):
        self.set_light()
        #self.set_fog()
        self.set_3d()
        return pyglet.event.EVENT_HANDLED

    def on_draw(self):
        self.set_3d()
        self.world.draw()
        #batch_test.draw()
        self.set_2d()
        #label.text = str(pyglet.clock.get_fps())
        #label.text = str(self.player.rotation)
        #label.draw()

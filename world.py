from pyglet.graphics import Batch
from pyglet.gl import *
from noise import pnoise2
import numpy as np
import threading
import time


class World:
    def __init__(self):
        self.current_lists = {}
        self.old_lists = {}
        self.zone_size = 20.0
        self.zone_x = None
        self.zone_z = None
        self.terrain_batch = Batch()
        self.sea_batch = Batch()

    def gen_terrain(self, mutex, x, z, patch_size=0.5):
        zone_size = self.zone_size
        w = zone_size / patch_size + 1
        assert w == int(w)
        w = int(w)
        xmin = (x - 0.5) * zone_size
        xmax = (x + 0.5) * zone_size
        zmin = (z - 0.5) * zone_size
        zmax = (z + 0.5) * zone_size
        v = []
        v_sea = []
        n = []
        c = []
        for i in np.linspace(xmin, xmax, w):
            time.sleep(0.2)
            for j in np.linspace(zmin, zmax, w):
                y = self.get_v(i, j)
                vv = [i, y, j]
                vv_sea = [i, 0.0, j]
                nn = self.get_n(i, j)
                v += vv
                v_sea += vv_sea
                n += nn
                if y > 10.0:
                    c += [255, 255, 255]
                elif y > 7.0:
                    c += [255, 120, 0]
                elif y > 1.0:
                    c += [0, 255, 0]
                elif y > 0.0:
                    c += [255, 255, 150]
                else:
                    c += [0, 0, 255]
        index = []
        for i in range(0, w-1):
            for j in range(0, w-1):
                index += [
                    i + j * w,
                    i + j * w + 1,
                    i + j * w + 1 + w,
                    i + j * w + w]
        data = [index, v, n, c, v_sea]
        mutex.acquire()
        self.current_lists[(x, z)] = data
        mutex.release()
        #np.savez('save/{0}_{1}.npz'.format(x,z), data)

    def draw(self):
        self.terrain_batch.draw()
        self.sea_batch.draw()

    def zone_lists_changed(self):
        tmp_lists = self.current_lists.copy()
        if tmp_lists != self.old_lists:
            self.old_lists = self.current_lists.copy()
            return True
        return False

    def zone_changed(self):
        size = self.zone_size
        player_x = int(np.floor(self.player.position[0] / size + 0.5))
        player_z = int(np.floor(self.player.position[2] / size + 0.5))
        return (player_x != self.zone_x or player_z != self.zone_z)

    def draw_terrain(self):
        self.terrain_batch = Batch()
        tmp_lists = self.current_lists.copy()
        for i in tmp_lists:
            l = tmp_lists[i]
            w2 = len(l[1]) / 3
            vlist = self.terrain_batch.add_indexed(
                w2, GL_QUADS, None, l[0],
                ('v3f/static', l[1]), ('n3f/static', l[2]),
                ('c3B/static', l[3]))

    def draw_sea(self):
        self.sea_batch = Batch()
        tmp_lists = self.current_lists.copy()
        for i in tmp_lists:
            l = tmp_lists[i]
            w2 = len(l[4]) / 3
            n = [0, 0, 255] * w2
            vlist = self.sea_batch.add_indexed(
                w2, GL_QUADS, None, l[0],
                ('v3f/static', l[4]), ('n3f/static', n),
                ('c3B/static', l[3]))

    def draw_sea_simple(self):
        tmp_lists = self.current_lists.copy()
        v = [minx, 0, minz, minx, 0, maxz, maxx, 0, maxz, maxx, 0, minz]
        n = [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]
        c = [0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255]
        self.sea_batch = Batch()
        self.sea_batch.add(4, GL_QUADS, None, ('v3f/static', v),
                           ('n3f/static', n), ('c3B/static', c))

    def update_batch(self):
        self.draw_sea()
        self.draw_terrain()

    def update_zone_lists(self):
        size = self.zone_size
        player_x = int(np.floor(self.player.position[0] / size + 0.5))
        player_z = int(np.floor(self.player.position[2] / size + 0.5))
        new_set = set()
        for i in range(player_x - 1, player_x + 2):
            for j in range(player_z - 1, player_z + 2):
                new_set.add((i, j))

        to_be_deleted = set()
        for i in self.current_lists:
            if i not in new_set:
                to_be_deleted.add(i)

        mutex = threading.Lock()
        for i in new_set:
            if i not in self.current_lists:
                x, z = i
                print 'Generating:', i
                threading.Thread(
                    target=self.gen_terrain,
                    args=(mutex, x, z)).start()

        for i in to_be_deleted:
            self.current_lists.pop(i)

        self.zone_x = player_x
        self.zone_z = player_z

    def update(self, dt):
        if self.zone_lists_changed():
            self.update_batch()
        if self.zone_changed():
            self.update_zone_lists()
        return

    def get_v(self, x, z):
        ratio = 0.02
        ratio2 = 50.0
        #return 0.0
        return pnoise2(x*ratio, z*ratio, 4)*ratio2

    def get_n(self, x, z):
        d = 0.01
        dydx = (self.get_v(x+d, z) - self.get_v(x-d, z)) / (2 * d)
        dydz = (self.get_v(x, z+d) - self.get_v(x, z-d)) / (2 * d)
        n = -np.cross([1.0, dydx, 0.0], [0.0, dydz, 1.0])
        return list(n)

    def add_tree(self, batch, x, y, z):
        batch.add(
            6, GL_TRIANGLES, None,
            ('v3f/static', (
                -0.2+x, y, 0.0+z,
                0.0+x, y+0.4, 0.0+z,
                0.2+x, y, 0.0+z,
                0.0+x, y, -0.2+z,
                0.0+x, y+0.4, 0.0+z,
                0.0+x, y, 0.2+z,)),
            ('c3B/static', (
                0, 255, 0,
                0, 255, 0,
                0, 255, 0,
                0, 255, 0,
                0, 255, 0,
                0, 255, 0,)),
            ('n3f/static', (
                0.0, 0.0, 1.0,
                0.0, 0.0, 1.0,
                0.0, 0.0, 1.0,
                1.0, 0.0, 0.0,
                1.0, 0.0, 0.0,
                1.0, 0.0, 0.0,)))

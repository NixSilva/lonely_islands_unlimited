import math
import numpy as np

class Player:
    def __init__(self):
        self.position = np.asarray([0.0, 0.0, 0.0])
        self.rotation = np.asarray([0.0, 0.0])
        self.velocity = np.asarray([0.0, 0.0, 0.0])
        self.mvector  = np.asarray([0.0, 0.0])
        self.norm_vector  = np.asarray([0.0, 0.0])
        self.height = 1.8
        self.speed = 0.5

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
        floor = self.world.get_v(self.position[0], self.position[2])
        dy = self.velocity[1]
        if self.position[1] >  floor + self.height:
            dy += -0.01
        else:
            dy = 0.0
            self.position[1] = floor + self.height
        self.velocity = [dx, dy, dz]
        self.position += [i * self.speed for i in self.velocity]


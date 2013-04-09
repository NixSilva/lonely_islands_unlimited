#!/usr/bin/env python2

import window
import world
import player
import pyglet


def update(dt):
    player.update(dt)
    world.update(dt)

if __name__ == '__main__':
    player = player.Player()
    world = world.World()
    world.player = player
    player.world = world
    window = window.Window(player, world)
    window.set_fullscreen(True)
    pyglet.clock.schedule_interval(update, 1/120.0)
    #label = pyglet.text.Label()
    window.set_exclusive_mouse(True)
    pyglet.app.run()

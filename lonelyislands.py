#!/usr/bin/env python2

import li_window
import li_world
import li_player
import pyglet


def update(dt):
    player.update(dt)
    world.update(dt)

if __name__ == '__main__':
    player = li_player.Player()
    world = li_world.World()
    world.player = player
    player.world = world
    window = li_window.Window(player, world)
    window.set_fullscreen(True)
    pyglet.clock.schedule_interval(update, 1/120.0)
    #label = pyglet.text.Label()
    window.set_exclusive_mouse(True)
    pyglet.app.run()

# pylint: disable=W0611
'''
Wintab Input Provider
===============================
Using the Android Joystickprovider as a base since there is no good explanation about the workings of
Event Providers in Kivy.
Not yet finished.
'''
__all__ = ('WintabMotionEventProvider', )

import os

# try:
#     import android  # NOQA
# except ImportError:
#     if 'KIVY_DOC' not in os.environ:
#         raise Exception('Wintab lib not found.')

from kivy.logger import Logger
from kivy.input.provider import MotionEventProvider
from kivy.input.factory import MotionEventFactory
from kivy.input.shape import ShapeRect
from kivy.input.motionevent import MotionEvent
#import pygame.joystick
import wintab32
from ctypes import windll


class WintabMotionEvent(MotionEvent):

    def depack(self, args):
        self.is_touch = True
        self.sx = args['x']
        self.sy = args['y']
        self.profile = ['pos']
        if 'size_w' in args and 'size_h' in args:
            self.shape = ShapeRect()
            self.shape.width = args['size_w']
            self.shape.height = args['size_h']
            self.profile.append('shape')
        if 'pressure' in args:
            self.pressure = args['pressure']
            self.profile.append('pressure')
        super(WintabMotionEvent, self).depack(args)

    def __str__(self):
        return '<WintabMotionEvent id=%d pos=(%f, %f) device=%s>' \
            % (self.id, self.sx, self.sy, self.device)


class WintabMotionEventProvider(MotionEventProvider):

    def __init__(self, device, args):
        super(WintabMotionEventProvider, self).__init__(device, args)
        self.touches = {}
        self.uid = 0
        self.window = None
        self.status = None
        self.tablet = None
        self.hwnd = None

    def start(self):
        self.hwnd = windll.user32.GetActiveWindow()
        self.tablet = wintab32.WintabInput(self.hwnd)

    def stop(self):
        self.tablet.close()

    def update(self, dispatch_fn):
        if not self.window:
            from kivy.core.window import Window
            self.window = Window
        w, h = self.window.system_size
        touches = self.touches

        for joy in self.joysticks:
            jid = joy.get_id()
            pressed = joy.get_button(0)
            if pressed or jid in touches:
                x = joy.get_axis(0) * 32768. / w
                y = 1. - (joy.get_axis(1) * 32768. / h)

                # python for android do * 1000.
                pressure = joy.get_axis(2) / 1000.
                radius = joy.get_axis(3) / 1000.

                # new touche ?
                if pressed and jid not in touches:
                    self.uid += 1
                    touch = WintabMotionEvent(self.device, self.uid,
                                            [x, y, pressure, radius])
                    touches[jid] = touch
                    dispatch_fn('begin', touch)
                # update touch
                elif pressed:
                    touch = touches[jid]
                    # avoid same touch position
                    if (touch.sx == x and touch.sy == y
                        and touch.pressure == pressure):
                        continue
                    touch.move([x, y, pressure, radius])
                    dispatch_fn('update', touch)
                # disapear
                elif not pressed and jid in touches:
                    touch = touches[jid]
                    touch.move([x, y, pressure, radius])
                    touch.update_time_end()
                    dispatch_fn('end', touch)
                    touches.pop(jid)

MotionEventFactory.register('Wintab', WintabMotionEventProvider)

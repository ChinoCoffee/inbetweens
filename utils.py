import numpy as np

from enum import Enum
from functools import partial

import matplotlib.path as mpath
Path = mpath.Path


def sort_ccw(coords):

    curve_start_coords = np.append(coords[0:1], coords[4::3], axis=0)
    assert len(curve_start_coords) == 11, len(curve_start_coords)

    thetas = np.arctan2(curve_start_coords.T[0], curve_start_coords.T[1])
    idx = np.argmin(thetas)

    if idx == 0:
        idx = 0
    elif idx == 1:
        idx = 4
    else:
        idx = 4 + 3 * (idx - 1)
    #print(idx)   # check

    new_coords = np.append(coords[idx:], coords[:idx], axis=0)

    if thetas[0] > thetas[1] or thetas[0] > thetas[2]:
        # dirty_hack
        # print("X")   # check
        #new_coords = new_coords[::-1]
        pass

    return new_coords


def normalize_coords(coords, scale=0.02):
    coords = np.array(coords)
    coords -= np.mean(coords, axis=0)   # x-y mean

    # sort counter-clockwise order
    # coords = sort_ccw(coords)   # [FIXME]

    coords *= np.array([scale, -scale])
    return coords


class Curve(object):

    def __init__(self, coords, close=True):

        coords = list(coords)
        commands = [Path.MOVETO] + [Path.CURVE4] * (len(coords) - 1)

        if close:
            coords.append(coords[0])
            commands.append(Path.CLOSEPOLY)

        self.path = Path(coords, commands)


class DragState(Enum):

    MOVING = 1
    RELEASED = 2


class UIController(object):

    STATE_MANIFOLD = 'm'

    def __init__(self, num_curves, fig, callback_drag, callback_keyevent):

        self.drag_state = DragState.RELEASED
        self.drawing_state = 0

        self.drag_event = None

        self.callback_drag = callback_drag
        self.callback_keyevent = callback_keyevent

        fig.canvas.mpl_connect('button_press_event', partial(self.press.__func__, self))
        fig.canvas.mpl_connect('button_release_event', partial(self.release.__func__, self))
        fig.canvas.mpl_connect('motion_notify_event', partial(self.motion.__func__, self))
        fig.canvas.mpl_connect('key_press_event', partial(self.keyevent.__func__, self))

        self.num_curves = num_curves

    def keyevent(self, event):
        if event.key.isdigit():
            i = int(event.key) - 1
            if i < self.num_curves:
                self.drawing_state = i

        elif event.key == self.STATE_MANIFOLD:
            self.drawing_state = self.STATE_MANIFOLD

        self.callback_keyevent(event)

        if self.drag_event:
            self.fire_callback_drag(self.drag_event)

    def fire_callback_drag(self, event):
        if event:
            self.drag_event = event
        self.callback_drag(event, self.drawing_state)

    def motion(self, event):
        if self.drag_state == DragState.MOVING:
            self.fire_callback_drag(event)

    def press(self, event):
        """
        print(event)
        for attr in dir(event):
            print(getattr(event, attr))
        """
        if event.dblclick:
            self.drag_state = DragState.RELEASED
            return
        self.drag_state = DragState.MOVING
        self.fire_callback_drag(event)

    def release(self, event):
        self.drag_state = DragState.RELEASED
        self.fire_callback_drag(event)

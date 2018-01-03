import numpy as np
from scipy.spatial import ConvexHull

import GPy

import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from svg.path import parse_path


from utils import Curve, UIController


Path = mpath.Path
fig, ax = plt.subplots()
ax.set(xlim=[0, 1], ylim=[0, 1], aspect=1)



def prepare_curves(filename, scale=0.01):
    data = (
        (
            (0.10, 0.10), (0.10, 0.20), (0.20, 0.10), (0.00, 0.30),
            (0.30, 0.50), (0.90, 0.40), (0.30, 0.60)
        ),
        (
            (0.60, 0.70), (0.20, 0.30), (0.50, 0.10), (0.60, 0.20),
            (0.20, 0.40), (0.20, 0.50), (0.20, 0.60)
        ),
        (
            (0.60, 0.70), (0.20, 0.30), (0.50, 0.10), (0.60, 0.20),
            (0.20, 0.40), (0.20, 0.50), (0.20, 0.60)
        ),
        (
            (0.60, 0.70), (0.20, 0.30), (0.50, 0.10), (0.60, 0.20),
            (0.20, 0.40), (0.20, 0.50), (0.20, 0.60)
        ),
    )

    #return list(map(lambda coords: Curve(coords), data))


    curves = []

    with open(filename) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

        for path in soup.find_all('path'):
            raw_curves = []

            for obj in parse_path(path.attrs['d']):

                if obj.__class__.__name__ == 'Line':
                    coords = (
                        (obj.start.real, obj.start.imag),
                        (obj.start.real, obj.start.imag),
                        (obj.end.real,   obj.end.imag),
                        (obj.end.real,   obj.end.imag),
                    )
                elif obj.__class__.__name__ == 'CubicBezier':
                    coords = (
                        (obj.start.real,    obj.start.imag),
                        (obj.control1.real, obj.control1.imag),
                        (obj.control2.real, obj.control2.imag),
                        (obj.end.real,      obj.end.imag),
                    )
                else:
                    raise ValueError("Unknown type %s" % obj)   # Arc

                raw_curves.append(Curve(coords))

        # normalize
        print(raw_curves)
        return raw_curves



test_curves = prepare_curves('test_curves.svg')


def draw(event, drawing_state):

    background = fig.canvas.copy_from_bbox(ax.bbox)
    fig.canvas.restore_region(background)

    ax.cla()
    ax.set(xlim=[0, 1], ylim=[0, 1], aspect=1)

    if drawing_state == UIController.STATE_MANIFOLD:
        # draw manifold
        ax.plot(event.xdata, event.ydata, "ro")

    elif isinstance(drawing_state, int):
        path = test_curves[drawing_state]
        pathpatch = mpatches.PathPatch(
            path,
            facecolor='b',
            alpha=0.1,
            transform=ax.transData)
        ax.add_patch(pathpatch)

    fig.canvas.blit(ax.bbox)
    fig.canvas.draw()


def keyevent(event):
    pass


controller = UIController(len(test_curves), fig, draw, keyevent)


plt.show()

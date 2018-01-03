import numpy as np
from scipy.spatial import ConvexHull

import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from svg.path import parse_path


from utils import Curve, UIController, normalize_coords
from manifold import calculate_manifold
from procrustes import procrustes_analyze


Path = mpath.Path
#fig, (ax, ax_manifold) = plt.subplots(1, 2)
fig, ax = plt.subplots()
ax.set(xlim=[-0.5, 0.5], ylim=[-0.5, 0.5], aspect=1)


def prepare_coords(filename, scale=0.02):

    with open(filename) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

        result = []

        for idx, path in enumerate(soup.find_all('path')):

            contour = []

            for i, obj in enumerate(parse_path(path.attrs['d'])):

                if obj.__class__.__name__ == 'Line':
                    coords = [
                        (obj.start.real, obj.start.imag),
                        (obj.start.real, obj.start.imag),
                        (obj.end.real,   obj.end.imag),
                        (obj.end.real,   obj.end.imag),
                    ]
                elif obj.__class__.__name__ == 'CubicBezier':
                    coords = [
                        (obj.start.real,    obj.start.imag),
                        (obj.control1.real, obj.control1.imag),
                        (obj.control2.real, obj.control2.imag),
                        (obj.end.real,      obj.end.imag),
                    ]
                else:
                    raise ValueError("Unknown type %s" % obj)   # Arc

                if i == 0:
                    contour.extend(coords)
                else:
                    contour.extend(coords[1:])

            # Number of all contours' points should be the same
            #print(idx, len(parse_path(path.attrs['d'])), len(contour))

            # normalize
            contour = normalize_coords(contour, scale)
            result.append(contour)

        return result


print("reading svg file...")
test_coords = prepare_coords('test_curves.svg')
print("procrustes analysis start.")
normalized_coords, analyzer = procrustes_analyze(test_coords)
print("result shape", normalized_coords.shape)


# Calculate
X = []
for xycoords in np.copy(normalized_coords):
    X.append(xycoords.flatten())
    X.append(xycoords.flatten())   # [FIXME] too small samples?


model, X_mean = calculate_manifold(X)
L = range(len(test_coords))
#print(model)

#model.plot_latent(label=L)
#plt.savefig('bezier_gplvm.png')

CURVES = []
for coords in test_coords:
    CURVES.append(Curve(coords))



def draw(event, drawing_state):

    background = fig.canvas.copy_from_bbox(ax.bbox)
    fig.canvas.restore_region(background)

    ax.cla()
    ax.set(xlim=[-0.5, 0.5], ylim=[-0.5, 0.5], aspect=1)

    if drawing_state == UIController.STATE_MANIFOLD:
        #model.plot_latent(label=L, ax=ax)
        model.plot_latent(ax=ax)   # [FIXME] duplicated call
        xl, yl = ax.get_xlim(), ax.get_ylim()
        ax_scale = 3.00

        model.plot_latent(ax=ax, plot_limits=(
            xl[0] * ax_scale, xl[1] * ax_scale, yl[0] * ax_scale, yl[1] * ax_scale
        ))
        ax.set(
            xlim=[xl[0] * ax_scale, xl[1] * ax_scale],
            ylim=[yl[0] * ax_scale, yl[1] * ax_scale],
            aspect=1)

        # draw manifold
        if event.xdata and event.ydata:
            ax.plot(event.xdata, event.ydata, "ro")

        # unknown value -> confidence?
        #print([event.xdata, event.ydata])
        new_curve, unknown_value = model.predict(np.array([[event.xdata, event.ydata]]))
        new_curve = new_curve[0]
        new_curve += X_mean

        # draw predicted curve
        coords = np.column_stack([new_curve[::2], new_curve[1::2]])

        #print(coords)
        avg = lambda t: (t[0] + t[1]) * 0.5
        #print(xl[0] * ax_scale, xl[1] * ax_scale, yl[0] * ax_scale, yl[1] * ax_scale)

        scale = min(xl[1] - xl[0], yl[1] - yl[0]) * ax_scale
        coords *= np.array([scale, scale])
        coords += np.array([avg(xl) * ax_scale, avg(yl) * ax_scale])

        new_curve = Curve(coords)
        pathpatch = mpatches.PathPatch(
            new_curve.path,
            facecolor=(0.1, 0.8, 0.7),
            alpha=0.7,
            transform=ax.transData)
        ax.add_patch(pathpatch)

    elif isinstance(drawing_state, int):
        path = CURVES[drawing_state].path
        pathpatch = mpatches.PathPatch(
            path,
            facecolor=(0.1, 0.8, 0.7),
            alpha=0.7,
            transform=ax.transData)
        ax.add_patch(pathpatch)

    fig.canvas.blit(ax.bbox)
    fig.canvas.draw()


def keyevent(event):
    pass


controller = UIController(len(CURVES), fig, draw, keyevent)


plt.show()

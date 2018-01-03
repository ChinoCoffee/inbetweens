import numpy as np

from transformations import GeneralizedProcrustesAnalyzer as GPA


class RotoppPoint(object):
    def __init__(self, center, left, right):
        self.center = center
        self.left = left
        self.right = right

    def __repr__(self):
        return f"<RotoppPoint L=[%.2f,%.2f] C=[%.2f,%.2f] R=[%.2f,%.2f]>" % (
            self.left[0], self.left[1],
            self.center[0], self.center[1],
            self.right[0], self.right[1]
        )

    @staticmethod
    def coords2rotopp(coords):
        # [WARNING] only work with closed contour
        return (coords[:-1]).flatten()

    @staticmethod
    def rotopp2coords(data):
        xycoords = data.reshape(len(data) // 2, 2)
        return np.append(xycoords, [xycoords[0]], axis=0)

    @classmethod
    def from_coords(cls, coords):
        num_points = (len(coords) - 4) // 3 + 1
        assert len(coords) == (num_points - 1) * 3 + 4
        data = coords[:-1]
        result = []
        for i in range(num_points):
            ci = 0 if i == 0 else (i - 1) * 3 + 4
            li = ci - 1
            ri = ci + 1
            result.append(
                cls(left=data[li],
                    center=data[ci],
                    right=data[ri])
            )
        return result


def procrustes_analyze(splines):
    data = [RotoppPoint.coords2rotopp(coords) for coords in splines]

    gpa = GPA()
    gpa.setMat(data)
    gpa.solve()

    normalized_splines = gpa.getNormalizedSpline()
    print(normalized_splines.shape)

    result = np.array([RotoppPoint.rotopp2coords(coords) for coords in normalized_splines])

    return result, gpa

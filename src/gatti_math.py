import numpy as np
from math import log10, floor


def siground(x, dc):
    return round(x, -int(floor(log10(abs(x)))) + dc)

def relto(obj: np.array, cam_xy: np.array, cam_z: float):
    return (obj - cam_xy) * cam_z

def absto(obj: np.array, cam_xy: np.array, cam_z: float):
    return (obj / cam_z + cam_xy)

def minmax(l: np.array, m: np.array, u: np.array):
    return np.array(
        x=min(max(l[0], m[0]), u[0]),
        y=min(max(l[1], m[1]), u[1])
    )

def in_box(nw: np.array, p: np.array, se: np.array):
    return nw[0] < p[0] < se[0] and nw[1] < p[1] < se[1]


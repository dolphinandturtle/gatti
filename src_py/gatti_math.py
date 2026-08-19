import numpy as np
from math import log10, floor


def siground(x, dc):
    return round(x, -int(floor(log10(abs(x)))) + dc)

def relto(obj: np.array, cam_xy: np.array, cam_z: float):
    return (obj - cam_xy) * cam_z

def absto(obj: np.array, cam_xy: np.array, cam_z: float):
    return (obj / cam_z + cam_xy)

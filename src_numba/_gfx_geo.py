import numpy as np
import numba as nb
from numba.pycc import CC


cc = CC("gatti_geo")


''' WARNING:

The following monolithic function, although un-pythonic, was made
with the good intent of being fast by:
  - avoiding python's loops for the numerous blits
  - scale in place instead of allocating new surfaces (pygame)

with this in mind proceed with caution, this function can SEGFAULT
the program.

TIPS (for developers):
  - when modifying the following function use '@nb.jit(boundscheck=True)'
'''


@cc.export("point_in_box", "u4(f8[:], f8[:,:], u4)")
@nb.jit(nopython=True, parallel=True, fastmath=True)
def point_in_box(
        cur_xy: np.array,
        img_box_gl: np.array,
        img_count: int
):
    if img_count == 0:
        return 0
    
    indeces = (img_count + 1) * np.ones((img_count,), np.uint32)
    for i in nb.prange(img_count):
        if (img_box_gl[i][0] < cur_xy[0] < img_box_gl[i][0] + img_box_gl[i][2] and
            img_box_gl[i][1] < cur_xy[1] < img_box_gl[i][1] + img_box_gl[i][3]):
            indeces[i] -= i + 1
    m = min(indeces)
    if m > img_count:
        return img_count
    else:
        return img_count - m


if __name__ == "__main__":
    cc.compile()

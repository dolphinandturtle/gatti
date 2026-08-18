import numba as nb
import numpy as np


@nb.njit(parallel=True)
def blit(px_src: np.array, rect_src: np.array, rect_trg: np.array, px_trg: np.array):
    oi_src, oj_src, rows_src, cols_src = rect_src
    oi_trg, oj_trg, rows_trg, cols_trg = rect_trg
    rows_fac = (rows_src - 1) / (rows_trg - 1)
    cols_fac = (cols_src - 1) / (cols_trg - 1)
    for i in nb.prange(rows_trg):
        for j in range(cols_trg):
            for k in range(3):
                px_trg[(i + oi_trg), (j + oj_trg), k] = px_src[oi_src + round(i * rows_fac), oj_src + round(j * cols_fac), k]
    

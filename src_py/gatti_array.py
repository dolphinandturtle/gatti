import numpy as np


def np_array_concat(base: np.array, ext: np.array) -> np.array:
    base_dynamic, *base_static = base.shape
    ext_dynamic, *ext_static = ext.shape
    # check for equal "higher order" SHAPE and equal TYPE
    assert len(base_static) == len(ext_static), f"Incompatible shape {len(base_static)}d vs. {len(ext_static)}d"
    assert all(n == m for n, m in zip(base_static, ext_static)), f"Incompatible size {base_static} vs. {ext_static}"
    assert base.dtype == ext.dtype, f"Incompatible type {base.dtype} vs. {ext.dtype}"

    # allocate new array
    new = np.zeros((base_dynamic + ext_dynamic, *base_static), base.dtype)

    # copy data from base
    new[:base_dynamic] = base

    # write data from extension
    new[base_dynamic:] = ext

    return new

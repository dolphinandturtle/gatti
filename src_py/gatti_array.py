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


def np_array_pop(arr: np.array, rg: tuple(int)) -> np.array:
    len_dyn, *len_sta = arr.shape
    assert 0 <= rg[0] <= rg[1] <= len_dyn, f"Popping range is 'out-of-range' 0 <= {rg[0]=} <= {rg[1]=} <= {len_dyn=}"

    diff = rg[1] - rg[0]

    # allocate new array
    new = np.zeros((len_dyn - diff, *len_sta), arr.dtype)

    # copy partial data
    new[:rg[0]] = arr[:rg[0]]

    # perform popping operation
    new[rg[0]:] = arr[rg[1]:len_dyn]

    return new


def np_array_swap(arr: np.array, rg: tuple(int)):
    len, *_shape = arr.shape
    assert 0 <= rg[0] <= rg[1] <= len, f"Popping range is 'out-of-range' 0 <= {rg[0]=} <= {rg[1]=} <= {len=}"

    diff = rg[1] - rg[0]

    # allocate temporary array
    swap = np.zeros((diff, *_shape), arr.dtype)

    # copy swap data
    swap[:] = arr[rg[0]:rg[1]]

    # perform swapping operation
    arr[rg[0]:len-diff] = arr[rg[1]:len]
    arr[len-diff:] = swap

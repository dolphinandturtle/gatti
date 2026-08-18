# built-in
from enum import Enum, auto
from dataclasses import dataclass
from time import perf_counter

# vendored
import numpy as np
import numba as nb
import pygame as pg

# local
import gatti_params as gp
import gatti_colors as gc
import gatti_state as gs
import gatti_math as gm
import gatti_gfx as gg


class Action(Enum):
    FLOAT = auto()
    IMAGE = auto()
    BOARD = auto()
    SCRAP = auto()


@dataclass(slots=True)
class GattiBoard:
    pixels: np.array
    assoc: np.array
    # count of the images (equals to 'n')
    img_count: int

    img_width: np.array
    img_height: np.array
    
    # each identifier references a unique image source (total n.shape of (n,))
    img_id: np.array

    # list of the local geometry of 'n' images (total np.shape of (n, 4))
    img_box_lo: np.array

    # list of the global geometry of 'n' images (total np.shape of (n, 4))
    img_box_gl: np.array

    # camera
    cam_xy: np.array
    cam_z: float

    @classmethod
    def empty(cls):
        return cls(
            pixels=np.zeros((0,), dtype=np.uint8),
            assoc=np.zeros((0,), dtype=np.uint32),
            img_count=0,
            img_width=np.zeros((0,), dtype=np.uint32),
            img_height=np.zeros((0,), dtype=np.uint32),
            img_id=np.zeros((0,), dtype=np.uint32),
            img_box_lo=np.zeros((0, 4), dtype=np.float64),
            img_box_gl=np.zeros((0, 4), dtype=np.float64),
            cam_xy=np.array([0.0, 0.0], dtype=np.float64),
            cam_z=1.0
        )

    def add(self, px: np.array, id: int, box_gl: np.array):

        if self.assoc.shape[0] <= id:
            self.assoc = np_array_concat(self.assoc, np.zeros(id + 1, np.uint32))
        self.assoc[id] = self.pixels.shape[0]

        self.pixels = np_array_concat(self.pixels, px.flatten())
        self.img_id = np_array_concat(self.img_id, np.array([id], dtype=np.uint32))
        self.img_width = np_array_concat(self.img_width, np.array([px.shape[0]], dtype=np.uint32))
        self.img_height = np_array_concat(self.img_height, np.array([px.shape[1]], dtype=np.uint32))
        self.img_box_gl = np_array_concat(self.img_box_gl, np.array([box_gl], np.float64))
        self.img_box_lo = np_array_concat(self.img_box_lo, np.array([[0, 0, px.shape[0], px.shape[1]]], np.float64))

        self.img_count += 1

    def run(self, screen: pg.Surface, imgmap: list[pg.Surface]):
        bg_color = gc.BG_MOVE
        running = True

        cur_pos = np.array(pg.mouse.get_pos(), np.float64)
        cur_dpos = np.zeros((2,), np.float64)
        cur_dz = 0.0
        action = (Action.FLOAT, Action.FLOAT)
        focused = self.img_count

        while running:
            t = perf_counter()
            # write actions
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        focused = mouse_in_box(gm.absto(cur_pos, self.cam_xy, self.cam_z), self.img_box_gl, self.img_count)
                
                if event.type == pg.MOUSEMOTION:
                    cur_dpos[0] = event.pos[0] - cur_pos[0]
                    cur_dpos[1] = event.pos[1] - cur_pos[1]
                    cur_pos[0], cur_pos[1] = event.pos
                    if event.buttons[0] and focused < self.img_count:
                        self.img_box_gl[focused,:2] += cur_dpos / self.cam_z
                    elif event.buttons[0] and focused == self.img_count:
                        self.cam_xy -= cur_dpos / self.cam_z

                if event.type == pg.MOUSEWHEEL:
                    if focused < self.img_count:
                        cur_proj = gm.absto(cur_pos, self.cam_xy, self.cam_z)
                        self.img_box_gl[focused][0:2] = gm.absto(self.img_box_gl[focused][0:2] - cur_proj, cur_proj, 1.0 - event.y * 0.05)
                        self.img_box_gl[focused][2:4] /= 1.0 - event.y * 0.05

                    if focused == self.img_count:
                        dz = 1.0 - event.y * 0.05
                        self.cam_xy += cur_pos * (1 - dz) / self.cam_z
                        self.cam_z /= dz
                
                # check for transition events, they are triggered by a keyboard press
                if event.type == pg.KEYDOWN:
                    # exit program if the ESC key is pressed
                    if event.key == pg.K_ESCAPE:
                        return gs.GattiState.EXIT

                    # exit program if the ESC key is pressed
                    elif event.key == pg.K_s:
                        return gs.GattiState.SEARCH

            # draw background
            screen.fill(bg_color)
            screen.lock()

            # draw grid
            draw_grid(self.cam_xy, self.cam_z, pg.surfarray.pixels3d(screen))

            # draw images
            draw(
                self.pixels,
                self.assoc,
                self.img_count,
                self.img_id,
                self.img_height,
                self.img_box_lo,
                self.img_box_gl,
                self.cam_xy,
                self.cam_z,
                pg.surfarray.pixels3d(screen),
                screen.get_width(),
                screen.get_height(),
            )
            screen.unlock()
            pg.display.update()
            print(perf_counter() - t)


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

@nb.jit(nopython=True, parallel=True)
def mouse_in_box(
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

@nb.jit(nopython=True, parallel=True)
def draw(
        pixels: np.array,
        assoc: np.array,
        img_count: int,
        img_id: np.array,
        img_height: np.array,
        img_box_lo: np.array,
        img_box_gl: np.array,
        cam_xy: np.array,
        cam_z: float,
        screen: np.array,
        screen_width: int,
        screen_height: int
):
    OFFSET_RGB = 3
    for i in range(img_count):
        id = img_id[i]

        # local (lo) and global (gl)
        # column offset (x), row offset (y), column range (w) and row range (h)
        x_lo = img_box_lo[i, 0]
        y_lo = img_box_lo[i, 1]
        w_lo = img_box_lo[i, 2]
        h_lo = img_box_lo[i, 3]
        x_gl = img_box_gl[i, 0]
        y_gl = img_box_gl[i, 1]
        w_gl = img_box_gl[i, 2] * cam_z
        h_gl = img_box_gl[i, 3] * cam_z

        # cull pixels outside of the screen
        x_screen = (x_gl - cam_xy[0]) * cam_z
        y_screen = (y_gl - cam_xy[1]) * cam_z
        x_clip = min(max(x_screen, 0), screen_width)
        y_clip = min(max(y_screen, 0), screen_height)
        w_clip = int(min(max(w_gl + x_screen, 0), screen_width) - x_clip)
        h_clip = int(min(max(h_gl + y_screen, 0), screen_height) - y_clip)

        # scaling factors
        h_fac = (h_lo - 1) / (h_gl - 1)
        w_fac = (w_lo - 1) / (w_gl - 1)
        h_lo_max = img_height[i]

        for y_rel in nb.prange(h_clip):
            for x_rel in range(w_clip):
                for ch in range(OFFSET_RGB):
                    screen[round(x_clip + x_rel), round(y_clip + y_rel), ch] = pixels[
                        assoc[id] +
                        (h_lo_max * OFFSET_RGB * round(x_lo + (x_clip - x_screen + x_rel) * w_fac)) +
                        (OFFSET_RGB * round(y_lo + (y_clip - y_screen + y_rel) * h_fac)) +
                        ch
                    ]


#@nb.jit(nopython=True, parallel=True)
@nb.jit(boundscheck=True)
def draw_grid(
        cam_xy: np.array,
        cam_z: float,
        screen: np.array
):
    start_col = cam_xy[0] - (cam_xy[0] % gp.GRID_SPACING)
    start_row = cam_xy[1] - (cam_xy[1] % gp.GRID_SPACING)

    n_col = min(int(gp.WIDTH / gp.GRID_SPACING / cam_z) + 1, gp.WIDTH)
    n_row = min(int(gp.HEIGHT / gp.GRID_SPACING / cam_z) + 1, gp.WIDTH)

    t = (1 - 1 / (cam_z + 1)) ** 2
    # griglia
    for i in nb.prange(n_col - 1):
        col = int((start_col + (i + 1) * gp.GRID_SPACING - cam_xy[0]) * cam_z)
        for row in range(gp.HEIGHT):
            screen[col, row, 0] = int(t * 255 + (1-t) * 34)
            screen[col, row, 1] = int(t * 255 + (1-t) * 39)
            screen[col, row, 2] = int(t * 255 + (1-t) * 34)

    for j in nb.prange(n_row - 1):
        row = int((start_row + (j + 1) * gp.GRID_SPACING - cam_xy[1]) * cam_z)
        for col in range(gp.WIDTH):
            screen[col, row, 0] = int(t * 255 + (1-t) * 34)
            screen[col, row, 1] = int(t * 255 + (1-t) * 39)
            screen[col, row, 2] = int(t * 255 + (1-t) * 34)

    # bordi sud-est
    col = int((start_col + n_col * gp.GRID_SPACING - cam_xy[0]) * cam_z)
    if col < gp.WIDTH:
        for row in range(gp.HEIGHT):
            screen[col, row, 0] = int(t * 255 + (1-t) * 34)
            screen[col, row, 1] = int(t * 255 + (1-t) * 39)
            screen[col, row, 2] = int(t * 255 + (1-t) * 34)

    row = int((start_row + n_row * gp.GRID_SPACING - cam_xy[1]) * cam_z)
    if row < gp.HEIGHT:
        for col in range(gp.WIDTH):
            screen[col, row, 0] = int(t * 255 + (1-t) * 34)
            screen[col, row, 1] = int(t * 255 + (1-t) * 39)
            screen[col, row, 2] = int(t * 255 + (1-t) * 34)

# built-in
import os
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
from gatti_gfx import draw, draw_grid, mouse_in_box


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
            assoc=np.full((0,), np.iinfo(np.uint32).max, dtype=np.uint32),
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
            self.assoc = np_array_concat(self.assoc, np.full((id + 1,), np.iinfo(np.uint32).max, dtype=np.uint32))

        if self.assoc[id] == np.iinfo(np.uint32).max:
            self.assoc[id] = self.pixels.shape[0]
            self.pixels = np_array_concat(self.pixels, px.flatten())

        self.img_id = np_array_concat(self.img_id, np.array([id], dtype=np.uint32))
        self.img_width = np_array_concat(self.img_width, np.array([px.shape[0]], dtype=np.uint32))
        self.img_height = np_array_concat(self.img_height, np.array([px.shape[1]], dtype=np.uint32))
        self.img_box_gl = np_array_concat(self.img_box_gl, np.array([box_gl], np.float64))
        self.img_box_lo = np_array_concat(self.img_box_lo, np.array([[0, 0, px.shape[0], px.shape[1]]], np.float64))

        self.img_count += 1

    def run(self, screen: pg.Surface):
        bg_color = gc.BG_MOVE
        running = True

        cur_pos = np.array(pg.mouse.get_pos(), np.float64)
        cur_dpos = np.zeros((2,), np.float64)
        cur_dz = 0.0
        action = (Action.FLOAT, Action.FLOAT)
        focused = self.img_count

        clock = pg.time.Clock()

        while running:
            t = perf_counter()
            # write actions
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        focused = mouse_in_box(gm.absto(cur_pos, self.cam_xy, self.cam_z), self.img_box_gl, self.img_count)
                    elif event.button == 3:
                        focused = self.img_count
                
                if event.type == pg.MOUSEMOTION:
                    cur_dpos[0] = event.pos[0] - cur_pos[0]
                    cur_dpos[1] = event.pos[1] - cur_pos[1]
                    cur_pos[0], cur_pos[1] = event.pos
                    if event.buttons[0] and focused < self.img_count:
                        self.img_box_gl[focused,:2] += cur_dpos / self.cam_z
                    elif (event.buttons[0] or event.buttons[2]) and focused == self.img_count:
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

                    elif event.mod == pg.KMOD_LCTRL and event.key == pg.K_v:
                        return gs.GattiState.CLIP

            # draw background
            screen.fill(bg_color)
            screen.lock()

            # draw grid
            draw_grid(screen.get_width(), screen.get_height(), gp.GRID_SPACING, self.cam_xy, self.cam_z, pg.surfarray.pixels3d(screen))

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
            clock.tick(60)


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

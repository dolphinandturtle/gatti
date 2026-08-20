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
import gatti_array as ga
from gatti_gfx import draw, draw_grid, mouse_in_box


class Action(Enum):
    FLOAT = auto()
    IMAGE = auto()
    BOARD = auto()
    SCRAP = auto()


@dataclass(slots=True)
class GattiBoard:
    # count of the images (equals to 'n')
    img_count: int
    
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
            img_count=0,
            img_id=np.zeros((0,), dtype=np.uint32),
            img_box_lo=np.zeros((0, 4), dtype=np.float64),
            img_box_gl=np.zeros((0, 4), dtype=np.float64),
            cam_xy=np.array([0.0, 0.0], dtype=np.float64),
            cam_z=1.0
        )

    def add(self, id: int, screen: np.array):
        scale_rel = 0.5 * screen.get_width() / srf.get_width()
        scale_abs = scale_rel / self.cam_z
        pos_rel = (np.array(screen.get_size()) - np.array(srf.get_size())  * scale_rel) / 2
        pos_abs = gm.absto(pos_rel, self.cam_xy, self.cam_z)

        self.img_id = ga.np_array_concat(self.img_id, np.array([id], dtype=np.uint32))
        self.img_box_gl = ga.np_array_concat(self.img_box_gl, np.array([pos_abs[0], pos_abs[1], scale_abs * srf.get_width(), scale_abs * srf.get_height()], np.float64))
        self.img_box_lo = ga.np_array_concat(self.img_box_lo, np.array([[0, 0, px.shape[0], px.shape[1]]], np.float64))
        self.img_count += 1

    def run(self, screen: pg.Surface, px_data: np.array, px_assoc: np.array, px_shape: np.array):
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
                px_data,
                px_assoc,
                px_shape,
                self.img_count,
                self.img_id,
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

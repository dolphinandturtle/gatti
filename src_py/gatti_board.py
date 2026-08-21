# built-in
import os
from enum import Enum, auto
from dataclasses import dataclass

# vendored
import numpy as np
import numba as nb
import pygame as pg

# local
import gatti_params as gp
import gatti_colors as gc
import gatti_state as gs
import gatti_array as ga
from gatti_gfx import draw_frames, draw_grid
from gatti_geo import point_in_box


class Action(Enum):
    FLOAT = auto()
    PAN = auto()
    ZOOM = auto()


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

    def add(self, id: int, px_shape: np.array, screen: np.array):
        scale_rel = 0.5 * screen.get_width() / px_shape[id][0]
        scale_abs = scale_rel / self.cam_z
        pos_rel = (np.array(screen.get_size()) - px_shape[id] * scale_rel) / 2
        pos_abs = pos_rel / self.cam_z + self.cam_xy

        self.img_id = ga.np_array_concat(self.img_id, np.array([id], dtype=np.uint32))
        self.img_box_gl = ga.np_array_concat(self.img_box_gl, np.array([[pos_abs[0], pos_abs[1], scale_abs * px_shape[id][0], scale_abs * px_shape[id][1]]], np.float64))
        self.img_box_lo = ga.np_array_concat(self.img_box_lo, np.array([[0, 0, px_shape[id][0], px_shape[id][1]]], np.float64))
        self.img_count += 1

    def run(self, screen: pg.Surface, px_data: np.array, px_assoc: np.array, px_shape: np.array):
        bg_color = gc.BG_MOVE

        cur_pos = np.array(pg.mouse.get_pos(), np.float64)
        cur_dpos = np.zeros((2,), np.float64)
        cur_y = 0

        action = Action.FLOAT
        target = self.img_count

        clock = pg.time.Clock()

        while True:

            cur_dpos[0] = 0
            cur_dpos[1] = 0
            cur_y = 0

            for event in pg.event.get():

                if event.type == pg.MOUSEMOTION:
                    cur_dpos[0] += event.rel[0] / self.cam_z
                    cur_dpos[1] += event.rel[1] / self.cam_z
                    cur_pos[0] = event.pos[0] / self.cam_z + self.cam_xy[0]
                    cur_pos[1] = event.pos[1] / self.cam_z + self.cam_xy[1]

                if event.type == pg.MOUSEBUTTONDOWN:
                    action = Action.PAN

                    if event.button == 1:
                        target = point_in_box(cur_pos, self.img_box_gl, self.img_count)

                    elif event.button == 3:
                        target = self.img_count

                if event.type == pg.MOUSEBUTTONUP:
                    action = Action.FLOAT
                
                if event.type == pg.MOUSEWHEEL:
                    action = Action.ZOOM
                    cur_y += event.y

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return gs.GattiState.EXIT

                    elif event.key == pg.K_s:
                        return gs.GattiState.SEARCH

                    elif event.mod == pg.KMOD_LCTRL and event.key == pg.K_v:
                        return gs.GattiState.CLIP

            # panning and zooming the board
            if target == self.img_count:
                # panning
                if action == Action.PAN:
                    self.cam_xy -= cur_dpos

                # zooming relative to the cursor center
                elif action == Action.ZOOM:
                    dz = 1.0 - cur_y * 0.05
                    self.cam_xy += (cur_pos - self.cam_xy) * (1 - dz)
                    self.cam_z /= dz

            # panning, zooming and deleting images
            elif target < self.img_count:
                # panning
                if action == Action.PAN:
                    self.img_box_gl[target,:2] += cur_dpos

                # zooming relative to the cursor center
                elif action == Action.ZOOM:
                    self.img_box_gl[target][0:2] -= cur_pos
                    self.img_box_gl[target] /= (1.0 - cur_y * 0.05)
                    self.img_box_gl[target][0:2] += cur_pos

            # handled by pygame
            screen.fill(bg_color)

            # not handled by pygame (handled by custom rasterizer)
            screen.lock()
            px_screen = pg.surfarray.pixels3d(screen)
            w_screen, h_screen = screen.get_size()
            draw_grid(w_screen, h_screen, gp.GRID_SPACING, self.cam_xy, self.cam_z, px_screen)
            draw_frames(px_data, px_assoc, px_shape, self.img_count, self.img_id, self.img_box_lo, self.img_box_gl, self.cam_xy, self.cam_z, px_screen, w_screen, h_screen)
            screen.unlock()

            pg.display.update()
            clock.tick(60)

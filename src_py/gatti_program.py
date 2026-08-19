import numpy as np
import pygame as pg
from dataclasses import dataclass

import gatti_math as gm
import gatti_colors as gc
from gatti_board import GattiBoard
from gatti_search import GattiSearch
from gatti_splash  import GattiSplash
from gatti_state import GattiState


GATTI_ID = 0

@dataclass(slots=True)
class GattiProgram:
    state: GattiState
    board: GattiBoard
    search: GattiSearch
    splash: GattiSplash

    @classmethod
    def empty(cls):
        return cls(GattiState.SPLASH, GattiBoard.empty(), GattiSearch.empty(), GattiSplash.empty())

    def run(self, screen):
        global GATTI_ID
        while True:
            match self.state:

                case GattiState.SPLASH:
                    # entering the SPLASH state and waiting for termination to read transition
                    size_screen = np.array(screen.get_size())
                    size_splash = size_screen * 0.67
                    pos_splash = (size_screen - size_splash) / 2

                    # placeholder for background
                    bg = pg.Surface(screen.get_size())
                    bg.fill(gc.BG_SPLASH)

                    self.state = self.splash.run(screen, pg.font.SysFont("Calibri", 44), pg.font.SysFont("Calibri", 24), pg.font.SysFont("Calibri", 16), bg, pos_splash, size_splash)

                case GattiState.SEARCH:
                    # fast gaussian blur (3-pass) of the board
                    bg = pg.transform.box_blur(screen, 3)
                    bg = pg.transform.box_blur(bg, 5)
                    bg = pg.transform.box_blur(bg, 7)

                    # layer solid color over blur
                    layer = pg.Surface(screen.get_size())
                    layer.fill(gc.BG_SEARCH)
                    layer.set_alpha(100)
                    bg.blit(layer, (0, 0))

                    # entering the SEARCH state and waiting for termination to read transition
                    self.state = self.search.run(screen, pg.font.SysFont("Calibri", 24), bg, np.array(screen.get_size()) / 2)

                    # transition from search query to board
                    if self.state == GattiState.BOARD:

                        # load the searched image
                        srf = pg.image.load(self.search.result).convert_alpha()

                        # add image to center of the board with half-screen-width scale
                        scale_rel = 0.5 * screen.get_width() / srf.get_width()
                        scale_abs = scale_rel / self.board.cam_z
                        pos_rel = (np.array(screen.get_size()) - np.array(srf.get_size())  * scale_rel) / 2
                        pos_abs = gm.absto(pos_rel, self.board.cam_xy, self.board.cam_z)
                        self.board.add(
                            px=pg.surfarray.array3d(srf),
                            id=GATTI_ID,
                            box_gl=np.array([pos_abs[0], pos_abs[1], scale_abs * srf.get_width(), scale_abs * srf.get_height()], np.float64)
                        )
                        GATTI_ID += 1

                case GattiState.BOARD:
                    # entering the BOARD state and waiting for termination to read transition
                    self.state = self.board.run(screen)

                case GattiState.EXIT:
                    # exit the program
                    break

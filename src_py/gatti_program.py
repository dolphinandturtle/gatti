import os
import numpy as np
import pygame as pg
from dataclasses import dataclass
from subprocess import call

import gatti_colors as gc
import gatti_array as ga
from gatti_board import GattiBoard
from gatti_search import GattiSearch
from gatti_splash  import GattiSplash
from gatti_state import GattiState


@dataclass(slots=True)
class GattiProgram:
    px_data: np.array
    px_assoc: np.array
    px_shape: np.array
    id_src: dict[str, int]
    id_count: int

    state: GattiState
    board: GattiBoard
    search: GattiSearch
    splash: GattiSplash

    @classmethod
    def empty(cls):
        return cls(
            px_data=np.zeros((0,), dtype=np.uint8),
            px_assoc=np.zeros((0,), dtype=np.uint32),
            px_shape=np.zeros((0, 2), dtype=np.uint32),
            id_src=dict(),
            id_count=0,
            state=GattiState.SPLASH,
            board=GattiBoard.empty(),
            search=GattiSearch.empty(),
            splash=GattiSplash.empty()
        )

    def add(self, path: str) -> int:
        if path in self.id_src:
            return self.id_src[path]
        else:
            try:
                srf = pg.image.load(path)
            except pg.error:
                return self.id_count + 1

            # linear ID assignment mechanism
            id = self.id_count
            self.id_count += 1

            # associate id to image inside the pool of pixel data
            self.px_assoc = ga.np_array_concat(self.px_assoc, np.zeros((id + 1,), dtype=np.uint32))
            self.px_assoc[id] = self.px_data.shape[0]

            # add pixel information of the new image (referenced by the path)
            srf = pg.image.load(path)
            new_px_data = pg.surfarray.array3d(srf).flatten()
            new_px_shape = np.array(srf.get_size(), dtype=np.uint32)
            self.px_data = ga.np_array_concat(self.px_data, np.array(new_px_data, dtype=np.uint8))
            self.px_shape = ga.np_array_concat(self.px_shape, np.array([new_px_shape], dtype=np.uint32))
            
            # associate path to id
            self.id_src[path] = id

            return id

    def run(self, screen):
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
                        id = self.add(self.search.result)
                        if id < self.id_count:
                            self.board.add(id, self.px_shape, screen)
                        else:
                            print("Unsupported image format")

                case GattiState.BOARD:
                    # entering the BOARD state and waiting for termination to read transition
                    self.state = self.board.run(screen, self.px_data, self.px_assoc, self.px_shape)

                case GattiState.CLIP:
                    with open(f"tmp_{self.id_count}.png", "wb") as file:
                        call(["xclip", "-selection", "clipboard", "-o"], stdout=file)

                    id = self.add(os.path.abspath(f"tmp_{self.id_count}.png"))
                    if id < self.id_count:
                        self.board.add(id, self.px_shape, screen)
                    else:
                        print("Unsupported image format")

                    self.state = GattiState.BOARD

                case GattiState.EXIT:
                    # exit the program
                    break

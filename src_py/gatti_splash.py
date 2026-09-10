import sys
import numpy as np

import json
import tarfile
import os
import pygame as pg
from dataclasses import dataclass


import gatti_state as gs


if getattr(sys, 'frozen', False):
    cwd, thisfile = os.path.split(__file__)
else:
    cwd, thisfile = os.path.split(sys.argv[0])

with open(os.path.join(cwd, "path"), "r") as file:
    path = os.path.join(*(line for line in file), "about.json")

with open(path, "r") as file:
    ABOUT = json.load(file)
    VERSION = ABOUT["version"]
    CREDITS = ABOUT["credits"]



@dataclass(slots=True)
class GattiSplash:
    recents: list[str]
    index: int
    use_recents: bool

    @classmethod
    def empty(cls):
        return cls(
            recents = [],
            index = 0,
            use_recents = False
        )

    def run(self, screen: pg.Surface, font_title: pg.font.Font, font_subtitle: pg.font.Font, font_credits: pg.font.Font, bg: pg.Surface, pos: np.array, size: np.array):
        # global padding
        gpad = np.array(screen.get_size()) * 0.01

        try:
            with open("/home/gabri/.config/gatti/recents.json", "r") as f:
                self.recents = json.load(f)
        except FileNotFoundError:
            pass

        binding={pg.K_1:0, pg.K_KP1:0, pg.K_2:1, pg.K_KP2:1, pg.K_3:2, pg.K_KP3:2, pg.K_4:3, pg.K_KP4:3, pg.K_5:4, pg.K_KP5:4}

        while True:

            # draw background
            screen.blit(bg, (0, 0))

            # frame (place-holder)
            rect = (pos[0], pos[1], size[0], size[1])
            pg.draw.rect(screen, "#ff0000", rect)

            # title
            title = font_title.render("gatti", True, "#ffffff")
            screen.blit(title, pos + gpad)

            # version
            version = font_subtitle.render(VERSION, True, "#ffffff")
            padding = np.array([title.get_width() * 0.1, 0])
            offset = np.array(title.get_size()) - np.array([0, version.get_height()])
            screen.blit(version, pos + offset + padding + gpad)

            # credits
            for i, agent in enumerate(CREDITS):
                offset = np.array([0, i * font_credits.get_height() + font_title.get_height()])
                name, role = agent["name"], agent["role"]
                handle = font_credits.render(f"by {name}", True, "#ffffff")
                screen.blit(handle, pos + offset + gpad)

            # self.recents
            i=0
            for file in self.recents:
                offset = np.array([0,10+ i * font_credits.get_height() + font_title.get_height() + len(CREDITS)*font_credits.get_height()])
                handle = font_credits.render(f"{i+1}--{file}",True,"#ffffff")
                screen.blit(handle, pos + gpad + offset)
                i += 1

            self.index=len(self.recents)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    # exit splash-screen enter board
                    if event.key == pg.K_SPACE:
                        return gs.GattiState.BOARD

                    # exit program
                    elif event.key == pg.K_ESCAPE:
                        return gs.GattiState.EXIT
                    elif (event.key in binding) and binding[event.key]<len(self.recents):
                        self.index = binding[event.key]
                        self.use_recents = True
                        return gs.GattiState.BOARD

            pg.display.update()

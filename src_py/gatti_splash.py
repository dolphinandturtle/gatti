import sys
import numpy as np

import json
import os
import pygame as pg
from dataclasses import dataclass

import gatti_state as gs


cwd, thisfile = os.path.split(sys.argv[0])
with open(os.path.join(cwd, "about.json"), "r") as file:
    ABOUT = json.load(file)
    VERSION = ABOUT["version"]
    CREDITS = ABOUT["credits"]


@dataclass(slots=True)
class GattiSplash:

    @classmethod
    def empty(cls):
        return cls()

    def run(self, screen: pg.Surface, font_title: pg.font.Font, font_subtitle: pg.font.Font, font_credits: pg.font.Font, bg: pg.Surface, pos: np.array, size: np.array):
        # global padding
        gpad = np.array(screen.get_size()) * 0.01

        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    # exit splash-screen enter board
                    if event.key == pg.K_SPACE:
                        return gs.GattiState.BOARD

                    # exit program
                    elif event.key == pg.K_ESCAPE:
                        return gs.GattiState.EXIT
                
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

            pg.display.update()

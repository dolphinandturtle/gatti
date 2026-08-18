import numpy as np

import os
import pygame as pg
from dataclasses import dataclass

import gatti_math as gm
import gatti_colors as gc
import gatti_state as gs


@dataclass(slots=True)
class GattiSearch:
    part: str
    walk: str
    hint: list[str]
    index: int

    @classmethod
    def empty(cls):
        return cls(part="", walk=os.path.abspath(""), hint=[], index=0)

    @property
    def result(self):
        return os.path.join(self.walk, self.part)

    def genhint(self):

        LEGAL = [".jpg", ".jpeg", ".png", ".webp"]

        # only some specific names are worth exploring
        self.hint = sorted((
            name for name in os.listdir(self.walk)

            # filter unrecognized formats (that aren't directories)
            if (any(fmt in name for fmt in LEGAL) or os.path.isdir(os.path.join(self.walk, name)))

        ), key=lambda t: pselev(self.part, t))

    def run(self, screen, font, bg, pos):

        self.genhint()

        while True:
            for event in pg.event.get():

                # ignore non-keyboard input
                if event.type != pg.KEYDOWN:
                    continue

                # pop latest user-input character if the BACKSPACE key is pressed
                if event.key == pg.K_BACKSPACE:
                    if len(self.part) > 0:
                        self.part = self.part[:-1]
                    else:
                        self.walk, _ = os.path.split(self.walk)
                        
                # roll through hints
                elif event.key == pg.K_TAB:
                    self.index = (self.index + 1) % len(self.hint)

                # process user-input if the RETURN key is pressed and a possible match exists
                elif event.key == pg.K_RETURN:

                    # this conditional is separated from the previous so that RETURN wouldn't be read as unicode
                    if len(self.hint) == 0:
                        continue

                    # fit user-input to nearest hint and extend walk
                    self.part = self.hint[self.index]

                    # transition to the BOARD if the walk can no longer be extended otherwise generate new hints
                    if not os.path.isdir(os.path.join(self.walk, self.part)):
                        return gs.GattiState.BOARD
                    else:
                        self.walk = os.path.join(self.walk, self.part)
                        self.part = ""

                # exit program if the ESC key is pressed
                elif event.key == pg.K_ESCAPE:
                    return gs.GattiState.EXIT

                # append user-input if the pressed key ALPHA-NUMERICAL
                else:
                    self.part += event.unicode
                    self.index = 0

                self.genhint()

            # draw background
            screen.blit(bg, (0, 0))

            # draw search box (active buffer)
            text = os.path.join(self.walk, self.part)
            pos_box = pos - np.array(font.size(text)) / 2
            srf = font.render(text, antialias=True, color=gc.TEXT)
            screen.blit(srf, pos_box)
            
            # draw search box (completion hints)
            fade = 255 / 2
            for i, p in enumerate(self.hint[self.index:] + self.hint[:self.index]):

                # fade out rendered text
                text = os.path.join(self.walk, p)
                srf = font.render(text, antialias=True, color=gc.TEXT)
                srf.set_alpha(fade)

                # blit text in a cascading fashion under the active buffer
                pos_box = pos - np.array(font.size(text)) / 2
                pos_offset = np.array([0, font.get_height() * (i+1)])
                screen.blit(srf, pos_box + pos_offset)

                fade /= 2
        
            pg.display.update()


# https://en.wikipedia.org/wiki/Levenshtein_distance
def pselev(s, t):

    v0 = [i for i in range(0, len(t) + 1)]
    v1 = [0 for i in range(0, len(t) + 1)]

    for i in range(len(s)):
        v1[0] = i + 1
        for j in range(len(t)):
            deletionCost = v0[j+1] + 1

            # the original levenshtein has an insertion cost of 1 instead of 0
            insertionCost = v1[j] + 0

            if s[i] == t[j]:
                substitutionCost = v0[j]
            else:
                substitutionCost = v0[j] + 1

            v1[j+1] = min(deletionCost, insertionCost, substitutionCost)

        v0, v1 = v1, v0

    return v0[len(t)]

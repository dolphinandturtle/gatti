import json
import numpy as np
import gatti_params as gp


def css_to_rgb(css: str):
    return np.array([
        int(css[1:3], base=16),
        int(css[3:5], base=16),
        int(css[5:7], base=16)
    ], dtype=np.uint8)


with open(gp.THEME, "r") as file:
    palette = json.load(file)
    BG_TRAVEL = css_to_rgb(palette["background-travel"])
    BG_MOVE = css_to_rgb(palette["background-move"])
    BG_SEARCH = css_to_rgb(palette["background-search"])
    BG_SPLASH = css_to_rgb(palette["background-splash"])
    TEXT = css_to_rgb(palette["text"])
    GRID_COLOR = css_to_rgb(palette["grid"])

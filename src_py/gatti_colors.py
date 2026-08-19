import json
import gatti_params as gp


with open(gp.THEME, "r") as file:
    palette = json.load(file)
    BG_TRAVEL = palette["background-travel"]
    BG_MOVE = palette["background-move"]
    BG_SEARCH = palette["background-search"]
    BG_SPLASH = palette["background-splash"]
    TEXT = palette["text"]
    GRID_COLOR = palette["grid"]

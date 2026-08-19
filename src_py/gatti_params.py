import sys
import os
import json


cwd, thisfile = os.path.split(sys.argv[0])
with open(os.path.join(cwd, "path"), "r") as file:
    path = os.path.join(*(line for line in file), "settings.json")

with open(path, "r") as file:
    settings = json.load(file)
    WIDTH = settings["width"]
    HEIGHT = settings["height"]
    THEME = settings["theme"]
    GRID_SPACING = settings["grid_spacing"]

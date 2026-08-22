import json
import tarfile
import pygame as pg

from io import BytesIO
import sys

import gatti_params as gp
import gatti_state as gs
from gatti_program import GattiProgram
from gatti_serialization import load_program
from gatti_serialization import dump_program


# protect script from getting imported
if __name__ != "__main__":
    print("This python script shouldn't be imported")
    sys.exit(0)

# initialize graphics library and windowing
pg.init()
pg.display.set_caption("gatti")
screen = pg.display.set_mode((gp.WIDTH, gp.HEIGHT))

# initialize blank program
prog = GattiProgram.empty()

path_save = ".gatti.tmp"
try:
    # supply the save specified in the argument as the one to be loaded
    if len(sys.argv) == 2:
        path_save = sys.argv[1]
        with tarfile.open(path_save, "r:gz") as tar:
            data = json.load(tar.extractfile("board.json"))
            load_program(prog, data)
        prog.state = gs.GattiState.BOARD

    # to many arguments
    elif len(sys.argv) > 2:
        print("To many arguments were supplied")
        sys.exit(0)

except FileNotFoundError as e:
    print(e)
    # create a save using the supplied argument
    print(f"Couldn't find {path_save}, creating a new instance")


prog.run(screen)


# saving the latest program state
with tarfile.open(path_save, "w:gz") as tar:

    # dump program state
    save = dump_program(prog)

    # dump BOARD state onto a json (virtual)
    data = BytesIO(json.dumps(save, indent=4).encode("utf-8"))
    meta = tarfile.TarInfo("board.json")
    meta.size = data.getbuffer().nbytes
    tar.addfile(meta, data)

# save last program instance identifier
with open(".save", "w") as file:
    file.write(path_save)


pg.quit()
sys.exit()

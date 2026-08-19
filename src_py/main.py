import json
import tarfile
import pygame as pg

from io import BytesIO
from sys import argv

import gatti_params as gp
from gatti_program import GattiProgram
from gatti_serialization import load_program
from gatti_serialization import dump_program


# protect script from getting imported
if __name__ != "__main__":
    print("This python script shouldn't be imported")
    exit()


# initialize graphics library and windowing
pg.init()
pg.display.set_caption("gatti")
screen = pg.display.set_mode((gp.WIDTH, gp.HEIGHT))

# initialize blank program
prog = GattiProgram.empty()


try:
    # supply the save specified in the argument as the one to be loaded
    if len(argv) == 2:
        path_save = argv[1]
        with tarfile.open(path_save, "r:gz") as tar:
            data_cam = json.load(tar.extractfile("camera.json"))
            data_img = json.load(tar.extractfile("board.json"))
            load_program(prog, data_cam, data_img)

    # to many arguments
    elif len(argv) > 2:
        print("To many arguments were supplied")
        exit()

except FileNotFoundError:
    # create a save using the supplied argument
    print(f"Couldn't find {path_save}, creating a new instance")


prog.run(screen)


# saving the latest program state
with tarfile.open(path_save, "w:gz") as tar:

    # dump program state
    save = dump_program(prog)

    # dump CAMERA state onto a json (virtual)
    data = BytesIO(json.dumps(save["camera"], indent=4).encode("utf-8"))
    meta = tarfile.TarInfo("camera.json")
    meta.size = data.getbuffer().nbytes
    tar.addfile(meta, data)

    # dump BOARD state onto a json (virtual)
    data = BytesIO(json.dumps(save["board"], indent=4).encode("utf-8"))
    meta = tarfile.TarInfo("board.json")
    meta.size = data.getbuffer().nbytes
    tar.addfile(meta, data)

# save last program instance identifier
with open(".save", "w") as file:
    file.write(path_save)


pg.quit()
exit()

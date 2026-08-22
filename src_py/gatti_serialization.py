import numpy as np


def load_program(prog, d):
    # load image data
    for src in d["sources"]:
        prog.add(src)

    img_count = len(d["frames"])

    # initialize
    prog.board.img_count = 0
    prog.board.img_id = np.zeros((img_count,), dtype=np.uint32)
    prog.board.img_box_lo = np.zeros((img_count, 4), dtype=np.float64)
    prog.board.img_box_gl = np.zeros((img_count, 4), dtype=np.float64)
    prog.board.cam_xy = np.zeros((2,), dtype=np.float64)
    prog.board.cam_z = 1.0

    # load arangement data
    if img_count > 0:
        prog.board.img_count = img_count
        prog.board.img_id[:] = [f["id"] for f in d["frames"]]
        prog.board.img_box_lo[:] = [[f["local"]["x"], f["local"]["y"], f["local"]["w"], f["local"]["h"]] for f in d["frames"]]
        prog.board.img_box_gl[:] = [[f["global"]["x"], f["global"]["y"], f["global"]["w"], f["global"]["h"]] for f in d["frames"]]
        prog.board.cam_xy[:] = [d["camera"]["x"], d["camera"]["y"]]
        prog.board.cam_z = d["camera"]["z"]


def dump_program(prog):
    return {
        "sources": prog.id_src,
        "camera": {
            "x": float(prog.board.cam_xy[0]),
            "y": float(prog.board.cam_xy[1]),
            "z": float(prog.board.cam_z)
        },
        "frames": [{
            "id": int(prog.board.img_id[i]),
            "local": {
                "x": float(prog.board.img_box_lo[i][0]),
                "y": float(prog.board.img_box_lo[i][1]),
                "w": float(prog.board.img_box_lo[i][2]),
                "h": float(prog.board.img_box_lo[i][3])
            },
            "global": {
                "x": float(prog.board.img_box_gl[i][0]),
                "y": float(prog.board.img_box_gl[i][1]),
                "w": float(prog.board.img_box_gl[i][2]),
                "h": float(prog.board.img_box_gl[i][3])
            }
        } for i in range(prog.board.img_count)]
    }

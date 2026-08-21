import numpy as np


def load_program(prog, d):
    # load image data
    for src in d["sources"]:
        prog.add(src)

    # load arangement data
    prog.board.img_count = len(d["frames"])
    prog.board.img_id = np.array([f["id"] for f in d["frames"]], dtype=np.uint32)
    prog.board.img_box_lo = np.array([[f["local"]["x"], f["local"]["y"], f["local"]["w"], f["local"]["h"]] for f in d["frames"]], dtype=np.float64)
    prog.board.img_box_gl = np.array([[f["global"]["x"], f["global"]["y"], f["global"]["w"], f["global"]["h"]] for f in d["frames"]], dtype=np.float64)
    prog.board.cam_xy = np.array([d["camera"]["x"], d["camera"]["y"]], dtype=np.float64)
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

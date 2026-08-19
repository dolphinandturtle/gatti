import numpy as np
import pygame as pg
import gatti_math as gm


def load_program(prog, data_cam, data_img):

    for img in data_img:
        prog.board.add(
            path=img["path"],
            srf=pg.image.load(img["path"]).convert_alpha(),
            pos=np.array([img["position"]["x"], img["position"]["y"]]),
            scale=img["scale"]
        )

    # loading camera data
    prog.board.cam_xy = np.array([data_cam["position"]["x"], data_cam["position"]["y"]])
    prog.board.cam_z = data_cam["scale"]


def dump_program(prog):
    return {
        "camera": {
            "x": prog.board.cam_xy[0],
            "y": prog.board.cam_xy[1],
            "z": prog.board.cam_z
        },
        "board": [{
            "id": prog.board.img_path[i],
            "local": {
                "x": prog.board.img_box_lo[i][0],
                "y": prog.board.img_box_lo[i][1],
                "width": prog.board.img_box_lo[i][2],
                "height": prog.board.img_box_lo[i][3]
            },
            "global": {
                "x": prog.board.img_box_gl[i][0],
                "y": prog.board.img_box_gl[i][1],
                "width": prog.board.img_box_gl[i][2],
                "height": prog.board.img_box_gl[i][3]
            }
        } for i in range(prog.board.img_count)]
    }

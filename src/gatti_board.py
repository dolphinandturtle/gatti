import pygame as pg
from time import perf_counter
import sys
from dataclasses import dataclass, astuple

import gatti_params as gp
import gatti_colors as gc
import gatti_state as gs
import gatti_math as gm


@dataclass(slots=True)
class GattiBoard:
    # Variables (camera)
    cam_pos: gm.Vec2
    cam_scale: float
    old_scale: float
    # Variables (images)
    img_count: int
    img_path: list[str]
    img_pos: list[gm.Vec2]
    img_crop_pos: list[gm.Vec2]
    img_srf_on: list[pg.Surface]
    img_srf_off: list[pg.Surface]
    img_size_on: list[gm.Vec2]
    img_size_off: list[gm.Vec2]
    img_scale: list[float]
    ifoc: int
    grid: pg.Surface

    @classmethod
    def empty(cls):
        return cls(
            cam_pos=gm.Vec2(0.0, 0.0),
            cam_scale=1.0,
            old_scale=0.0,
            img_count=0,
            img_path=[],
            img_pos=[],
            img_crop_pos=[],
            img_srf_on=[],
            img_srf_off=[],
            img_size_on=[],
            img_size_off=[],
            img_scale=[],
            ifoc=0,
            grid=None
        )

    def add(self, path, srf, pos, scale):
        self.img_path.append(path)
        self.img_pos.append(pos)
        self.img_crop_pos.append(gm.Vec2(0, 0))
        self.img_srf_on.append(pg.transform.smoothscale_by(srf, scale * self.cam_scale))
        self.img_srf_off.append(srf)
        self.img_size_on.append(gm.Vec2(*srf.get_size()) * scale)
        self.img_size_off.append(gm.Vec2(*srf.get_size()))
        self.img_scale.append(scale)
        self.img_count += 1

    def scale_lazy(self, iimg, screen):

        # edge-edge description of image screen-rectangle (north-west and south-east)
        pos_nw = gm.relto(self.img_pos[iimg], self.cam_pos, self.cam_scale)
        pos_se = pos_nw + self.img_size_on[iimg] * self.cam_scale

        # project rectangle edges onto nearest screen edge
        pos_nw_clip = gm.minmax(gm.Vec2(0, 0), pos_nw, gm.Vec2(*screen.get_size()))
        pos_se_clip = gm.minmax(gm.Vec2(0, 0), pos_se, gm.Vec2(*screen.get_size()))

        # edge-lenght description of image absolute-rectangle before scaling
        scale_total = self.cam_scale * self.img_scale[iimg]
        pos_clip = gm.minmax(gm.Vec2(0, 0), (pos_nw_clip - pos_nw) / scale_total, self.img_size_off[iimg])
        size_clip = gm.minmax(gm.Vec2(0, 0), (pos_se_clip - pos_nw_clip) / scale_total, self.img_size_off[iimg])
        rect = (pos_clip.x, pos_clip.y, size_clip.x, size_clip.y)

        # image rectangle absolute edge after scaling
        self.img_crop_pos[iimg] = pos_clip * self.img_scale[iimg]

        # image portion that is out-of-scope is cropped away then the remaining is scaled
        self.img_srf_on[iimg] = pg.transform.smoothscale_by(self.img_srf_off[iimg].subsurface(rect), scale_total)

    def run(self, screen, font_hud):


        self.grid = pg.Surface((3 * gp.WIDTH, 3 * gp.HEIGHT))
        running = True
        bg_color = gc.BG_MOVE

        win = 32
        samples = [0] * win
        while running:

            spf = perf_counter()

            for event in pg.event.get():

                # globally pan the environment if no image is left clicked or by arbitrary right click
                if event.type == pg.MOUSEMOTION and ((event.buttons[0] and self.ifoc == self.img_count) or event.buttons[2]):
                    self.cam_pos -= gm.Vec2(*event.rel) / self.cam_scale
                    for i in range(self.img_count):
                        nw = gm.absto(gm.Vec2(0, 0), self.cam_pos, self.cam_scale)
                        se = gm.absto(gm.Vec2(*screen.get_size()), self.cam_pos, self.cam_scale)
                        if not (
                                gm.in_box(nw, self.img_pos[i], se) and
                                gm.in_box(nw, self.img_pos[i] + self.img_size_on[i], se)
                        ):
                            self.scale_lazy(i, screen)

                # globally scale the environment if no image is focused
                elif event.type == pg.MOUSEWHEEL and self.ifoc == self.img_count:

                    # the mouse cursor is used as the center of the zoom (fixed point)
                    dz = 1.0 - event.y * 0.05
                    self.cam_pos += gm.Vec2(*pg.mouse.get_pos()) * (1 - dz) / self.cam_scale
                    self.cam_scale /= dz

                    for i in range(self.img_count):
                        self.scale_lazy(i, screen)

                # unfocus an image by right click
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                    self.ifoc = self.img_count
                    bg_color = gc.BG_TRAVEL

                # focus an image by left click
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:

                    # if the cursor isn't clicking an image set the focus out of scale
                    self.ifoc = self.img_count
                    bg_color = gc.BG_TRAVEL

                    # check if cursor (projected into the image space) is contained inside any image
                    for i in reversed(range(self.img_count)):

                        cur_proj = gm.absto(gm.Vec2(*event.pos), self.cam_pos, self.cam_scale)
                        if gm.in_box(self.img_pos[i], cur_proj, self.img_pos[i] + self.img_size_on[i]):
                            # push focused image to the top layer
                            self.img_pos.append(self.img_pos.pop(i))
                            self.img_path.append(self.img_path.pop(i))
                            self.img_crop_pos.append(self.img_crop_pos.pop(i))
                            self.img_srf_on.append(self.img_srf_on.pop(i))
                            self.img_srf_off.append(self.img_srf_off.pop(i))
                            self.img_size_on.append(self.img_size_on.pop(i))
                            self.img_size_off.append(self.img_size_off.pop(i))
                            self.img_scale.append(self.img_scale.pop(i))

                            # set focused image index
                            self.ifoc = self.img_count - 1
                            bg_color = gc.BG_MOVE

                            # lower image opacity
                            self.img_srf_off[self.ifoc].set_alpha(100)
                            self.img_srf_on[self.ifoc].set_alpha(100)

                            break

                # higher image opacity of focused image when mouse button is being let go of
                elif self.ifoc < self.img_count and event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    self.img_srf_off[self.ifoc].set_alpha(255)
                    self.img_srf_on[self.ifoc].set_alpha(255)

                # pan an image by the dragged distance if an image is focused and the cursor is dragging
                elif self.ifoc < self.img_count and event.type == pg.MOUSEMOTION and event.buttons[0]:
                    self.img_pos[self.ifoc] += gm.Vec2(*event.rel) / self.cam_scale
                    nw = gm.absto(gm.Vec2(0, 0), self.cam_pos, self.cam_scale)
                    se = gm.absto(gm.Vec2(*screen.get_size()), self.cam_pos, self.cam_scale)
                    if not (
                            gm.in_box(nw, self.img_pos[self.ifoc], se) and
                            gm.in_box(nw, self.img_pos[self.ifoc] + self.img_size_on[self.ifoc], se)
                    ):
                        self.scale_lazy(self.ifoc, screen)

                # scale the image if an image is foucsed and the mouse-wheel is rolling
                elif self.ifoc < self.img_count and event.type == pg.MOUSEWHEEL:

                    # the mouse cursor is used as the center of the zoom (fixed point)
                    cur_proj = gm.absto(gm.Vec2(*pg.mouse.get_pos()), self.cam_pos, self.cam_scale)
                    img_pos_rel = self.img_pos[self.ifoc] - cur_proj
                    self.img_pos[self.ifoc] = gm.absto(img_pos_rel, cur_proj, 1.0 - event.y * 0.05)
                    self.img_scale[self.ifoc] /= 1.0 - event.y * 0.05
                    self.img_size_on[self.ifoc] = self.img_size_off[self.ifoc] * self.img_scale[self.ifoc]

                    # update the scales locally
                    self.scale_lazy(self.ifoc, screen)

                # delete the image if an image is focused and the X key is pressed
                elif self.ifoc < self.img_count and event.type == pg.KEYDOWN and event.key == pg.K_x:
                    self.img_path.pop(self.ifoc)
                    self.img_srf_on.pop(self.ifoc)
                    self.img_srf_off.pop(self.ifoc)
                    self.img_pos.pop(self.ifoc)
                    self.img_size_on.pop(self.ifoc)
                    self.img_size_off.pop(self.ifoc)
                    self.img_scale.pop(self.ifoc)
                    self.img_count -= 1

                # check for transition events, they are triggered by a keyboard press
                if event.type == pg.KEYDOWN:

                    # switch to searching if the S key is pressed
                    if event.key == pg.K_s:
                        return gs.GattiState.SEARCH

                    # exit program if the ESC key is pressed
                    if event.key == pg.K_ESCAPE:
                        return gs.GattiState.EXIT

            # update grid
            if (self.old_scale != self.cam_scale):

                GRID_SPACING_scale=gp.GRID_SPACING * self.cam_scale

                if (self.grid.get_width() < gp.WIDTH + GRID_SPACING_scale or self.grid.get_height() < gp.HEIGHT + GRID_SPACING_scale):
                    self.grid = pg.Surface((gp.WIDTH + GRID_SPACING_scale, gp.HEIGHT + GRID_SPACING_scale))

                n_col = int(gp.WIDTH / gp.GRID_SPACING / self.cam_scale)
                n_row = int(gp.HEIGHT / gp.GRID_SPACING / self.cam_scale)

                # fill background color
                self.grid.fill(bg_color)

                for i in range(n_col + 2):
                    col = i * gp.GRID_SPACING * self.cam_scale
                    pg.draw.line(self.grid, gc.GRID_COLOR, (col, 0), (col, gp.HEIGHT+2 * GRID_SPACING_scale))

                for j in range(n_row + 2):
                    row = j * gp.GRID_SPACING * self.cam_scale
                    pg.draw.line(self.grid, gc.GRID_COLOR, (0, row), (gp.WIDTH+2 * GRID_SPACING_scale, row))
                self.old_scale = self.cam_scale

            # draw background & grid
            start_col = self.cam_pos.x - (self.cam_pos.x % gp.GRID_SPACING)
            start_row = self.cam_pos.y - (self.cam_pos.y % gp.GRID_SPACING)
            start = gm.Vec2(start_col,start_row)
            pos_grid = gm.relto(start,self.cam_pos,self.cam_scale)
            screen.blit(self.grid, astuple(pos_grid))

            # draw images
            for i in range(0, self.img_count):
                pos_screen = gm.relto(self.img_pos[i] + self.img_crop_pos[i], self.cam_pos, self.cam_scale)
                screen.blit(self.img_srf_on[i], astuple(pos_screen))

            # draw milliseconds per frame
            samples.pop(0)
            samples.append(perf_counter() - spf)
            mspf_avg = str(gm.siground(100 * sum(samples) / win, 2)).ljust(5, '0')
            msrf_spf = font_hud.render(f"mspf: {mspf_avg}", True, "#ffffff")
            pos_hud = gm.Vec2(0, screen.get_height()) - gm.Vec2(0, 3 * font_hud.get_height())
            screen.blit(msrf_spf, (pos_hud.x, pos_hud.y))

            # loaded pixel count
            srf_pixels = font_hud.render(f"pixels(loaded): {sum(srf.get_width() * srf.get_height() for srf in self.img_srf_off)}", True, "#ffffff")
            pos_hud = gm.Vec2(0, screen.get_height()) - gm.Vec2(0, 2 * font_hud.get_height())
            screen.blit(srf_pixels, (pos_hud.x, pos_hud.y))

            # rendered pixel count
            srf_pixels = font_hud.render(f"pixels(render): {sum(srf.get_width() * srf.get_height() for srf in self.img_srf_on)}", True, "#ffffff")
            pos_hud = gm.Vec2(0, screen.get_height()) - gm.Vec2(0, font_hud.get_height())
            screen.blit(srf_pixels, (pos_hud.x, pos_hud.y))

            pg.display.update()

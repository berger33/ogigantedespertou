#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/animia/rig_p1_03.py — cena v7 'AMIGOS REPTILIANOS' (p1_03).

Rig estrutural 100% overlays (poster imutável, nada inpaintado):
  * vapor sobe das 3 canecas (puffs aditivos sobre o vapor baked);
  * olhos do papel de parede piscam escalonados (pálpebra cor da parede);
  * winks neon do papel pulsam em sequência;
  * luzes da cidade tremeluzem na janela;
  * luminária verde pulsa;
  * brilho de 'tim-tim' no choque das canecas (k10);
  * varredura de reflexo nos óculos do reptiliano.
N=30 @ 5 fps, 6 s, loop perfeito. Personagem nunca cortado.
Ver docs/ANIM_V7_RIG.md.
"""
from __future__ import annotations
import math
import os

import numpy as np
from PIL import Image, ImageDraw

from riglib import N, BaseRig, bump, finalize, smooth

HERE = os.path.dirname(os.path.abspath(__file__))
POSTER = os.path.normpath(os.path.join(
    HERE, '../../src/assets/anim/p1_03/poster.webp'))
OUT = os.path.normpath(os.path.join(
    HERE, '../../src/assets/anim/p1_03/v7'))
TAU = 2 * math.pi

STEAM = [(293, 150, 0), (340, 148, 10), (365, 258, 20)]   # x, y_boca, fase
LAMP = (562, 71)
EYES = [(60, 57, 20, 10, 5), (155, 57, 20, 10, 13), (521, 53, 12, 7, 21)]
WINKS = [(157, 16, 6), (95, 92, 16), (8, 82, 26)]
CITY = [(247, 105, 4), (255, 127, 10), (327, 100, 16), (336, 112, 22),
        (243, 141, 28)]
LENSES = [(439, 105, 13), (472, 107, 14)]
CLINK = (318, 158)


class Rig(BaseRig):
    def __init__(self):
        p = np.asarray(Image.open(POSTER).convert('RGB'))
        super().__init__(p)
        self.base = p.copy()
        H, W, _ = p.shape
        yy, xx = np.mgrid[0:H, 0:W]
        self.lens_mask = np.zeros((H, W), bool)
        for (cx, cy, r) in LENSES:
            self.lens_mask |= (xx - cx) ** 2 + (yy - cy) ** 2 <= (r - 1) ** 2
        self.wall = {e[:2]: ((p[e[1], e[0] - e[2] - 8].astype(int) +
                              p[e[1], e[0] + e[2] + 8].astype(int)) // 2)
                     for e in EYES}

    # ------------------------------------------------------------- peças
    def _puffs(self, out, x0, y0, phase):
        for i in range(3):
            s = ((k_cache + phase) / N + i / 3) % 1.0
            y = y0 - 8 - 52 * s
            x = x0 + 5 * math.sin(s * TAU * 1.5 + i * 2.1)
            al = math.sin(math.pi * s) * 0.26
            r = 3 + 4 * s
            self.glow(out, x, y, r, r * 1.4, (170, 240, 160), al)

    def _blink(self, out, ex, ey, rx, ry, k0):
        k = k_cache
        if not (k0 <= k <= k0 + 4):
            return
        t = (k - k0) / 4
        c = math.sin(math.pi * min(1, t))          # 0->1->0
        if c <= 0.03:
            return
        col = self.wall[(ex, ey)]
        top = ey - ry
        cy = top + ry * c
        d = ImageDraw.Draw(img_buf)
        d.ellipse([ex - rx, cy - ry * c, ex + rx, cy + ry * c],
                  fill=tuple(int(v) for v in col))
        if c > 0.8:
            d.line([ex - rx + 3, cy + ry * c - 1, ex + rx - 3, cy + ry * c - 1],
                   fill=(18, 34, 26), width=2)
        a = np.asarray(img_buf)
        m = a[..., 3:4] / 255.0
        out[:] = (a[..., :3] * m + out * (1 - m)).astype(np.uint8)
        img_buf.paste((0, 0, 0, 0), (0, 0) + img_buf.size)

    def frame(self, k):
        global k_cache, img_buf
        k_cache = k % N
        k = k_cache
        img_buf = Image.new('RGBA', (self.W, self.H))
        out = self.base.copy()

        # vapor das canecas
        for (x0, y0, ph) in STEAM:
            self._puffs(out, x0, y0, ph)

        # luminária pulsa (2 ciclos)
        self.glow(out, LAMP[0], LAMP[1], 30, 30, (90, 255, 140),
                  0.05 + 0.04 * math.sin(TAU * 2 * k / N))

        # olhos do papel piscam
        for (ex, ey, rx, ry, k0) in EYES:
            self._blink(out, ex, ey, rx, ry, k0)

        # winks neon pulsam
        for (wx, wy, c) in WINKS:
            self.glow(out, wx, wy, 7, 5, (57, 255, 140),
                      0.30 * bump(k, c, 1.4))

        # cidade tremeluz
        for (cx, cy, c) in CITY:
            a = bump(k, c, 0.9) * 0.8
            if a > 0.02:
                self.star(out, cx, cy, 1, a, (250, 240, 170))

        # tim-tim das canecas
        self.star(out, CLINK[0], CLINK[1], 4, bump(k, 10, 1.0) * 0.95)
        self.ring(out, CLINK[0], CLINK[1], 4 + 6 * bump(k, 10.5, 1.2), 1.0,
                  (240, 255, 230), 0.35 * bump(k, 10.5, 1.2), width=1)

        # reflexo varre os óculos k16-20
        if 16 <= k <= 20:
            t = (k - 16) / 4
            off = -18 + 36 * smooth(t)
            band = np.zeros_like(out[..., 0], float)
            for (cx, cy, r) in LENSES:
                u = (np.arange(self.W) - (cx + off)) / 3.0
                stripe = np.exp(-u ** 2)
                band = np.maximum(band, stripe[None, :])
            m = (band * self.lens_mask * 0.55)[..., None]
            out[:] = np.clip(out * (1 - m) + 235 * m, 0, 255).astype(np.uint8)
        return out


def main():
    rig = Rig()
    frames, closure, qa = finalize(
        rig, OUT, meta_extra=dict(mission='p1_03',
                                  label='AMIGOS REPTILIANOS',
                                  beats='vapor sobe; olhos do papel piscam; '
                                        'winks neon; cidade tremeluz; '
                                        'luminária pulsa; tim-tim; reflexo '
                                        'nos óculos'))
    print('closure', qa['Q1_loop_closure'],
          'bytes', qa['Q6_entrega']['bytes'])


if __name__ == '__main__':
    main()

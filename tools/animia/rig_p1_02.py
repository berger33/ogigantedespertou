#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/animia/rig_p1_02.py — cena v7 'PLANTAR FAKE NEWS' (p1_02).

Rig estrutural: poster imutável + overlays periódicos (N=30 @ 5 fps, 6 s).
Beats: neon do jornal pulsa; luminária pulsa em antifase; 3 folhas de
"notícia" voam do jornal para as prateleiras da banca (plantio), com pouso
(anéis + flash da pilha + folha absorvida); dois brilhos na manchete.
Personagem nunca cortado — 100% overlays. Ver docs/ANIM_V7_RIG.md.
"""
from __future__ import annotations
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from riglib import N, BaseRig, bump, contact_sheet, finalize, lerp, smooth

HERE = os.path.dirname(os.path.abspath(__file__))
POSTER = os.path.normpath(os.path.join(
    HERE, '../../src/assets/anim/p1_02/poster.webp'))
OUT = os.path.normpath(os.path.join(
    HERE, '../../src/assets/anim/p1_02/v7'))
TAU = 2 * math.pi

# ---------------------------------------------------------------- geometria
# jornal grande (núcleo branco + neon verde): (206,78)-(432,336)
# luminária verde: x>=496, y 83-235
# prateleiras da banca (topo das pilhas): y 82 / 155 / 239, x 46-173


def _blur_mask(mask, radius=3):
    img = Image.fromarray((mask * 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(radius)),
                      dtype=float) / 255.0


def _sheet_sprite():
    """Folha de jornal em miniatura (RGBA)."""
    sp = Image.new('RGBA', (18, 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(sp)
    d.rectangle([0, 0, 17, 13], fill=(238, 240, 235, 255),
                outline=(120, 126, 118), width=1)
    d.line([2, 3, 15, 3], fill=(70, 76, 70), width=1)      # manchete
    d.line([2, 6, 15, 6], fill=(150, 156, 150), width=1)   # texto
    d.line([2, 9, 11, 9], fill=(150, 156, 150), width=1)
    return np.asarray(sp)


def bez(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


class Rig(BaseRig):
    def __init__(self):
        poster = np.asarray(Image.open(POSTER).convert('RGB'))
        super().__init__(poster)
        self.base = poster.copy()
        r, g, b = (poster[..., 0].astype(int), poster[..., 1].astype(int),
                   poster[..., 2].astype(int))
        green = (g > 140) & (g - r > 60) & (g - b > 60)
        # neon só do jornal (janela ao redor do papel)
        pm = np.zeros_like(green)
        pm[76:340, 198:436] = green[76:340, 198:436]
        self.paper_glow = _blur_mask(pm, 3)
        # luminária (lado direito, acima da mesa)
        lm = np.zeros_like(green)
        lm[80:240, 490:640] = green[80:240, 490:640]
        self.lamp_glow = _blur_mask(lm, 4)
        self.sheet = _sheet_sprite()
        # (k0, k1, origem, controle, pouso, topo_pilha_y)
        self.sheets = [
            (2, 8, (224, 108), (158, 58), (105, 80), 82),
            (10, 16, (220, 150), (150, 108), (108, 153), 155),
            (18, 24, (218, 208), (148, 178), (110, 237), 239),
        ]

    # ----------------------------------------------------------- overlays
    def _layer(self, out, mask, alpha, color):
        if alpha <= 0.004:
            return
        a = (mask * alpha)[..., None]
        col = np.array(color, float)
        out[:] = np.clip(out * (1 - a) + col * a, 0, 255).astype(np.uint8)

    def _sheet_flight(self, out, k, k0, k1, src, ctl, dst, shelf_y):
        if k0 <= k <= k1:
            t = smooth((k - k0) / (k1 - k0))
            x, y = bez(src, ctl, dst, t)
            ang = 18 * math.sin(TAU * (k - k0) / 8)
            spr = np.asarray(Image.fromarray(self.sheet).rotate(
                ang, expand=True, resample=Image.BICUBIC))
            alpha = min(1.0, (k - k0) / 1.0) if k > k0 else 0.55
            self.paste(out, spr, x, y - spr.shape[0] / 2,
                       scale=lerp(0.7, 1.0, t), alpha=alpha)
        # pouso: folha absorvida + anéis + flash da pilha
        if k1 <= k <= k1 + 3:
            w = k - k1
            a = 0.85 * (1 - w / 3.5)
            self.paste(out, self.sheet, dst[0], dst[1] - 7, alpha=a)
        if k1 <= k <= k1 + 2:
            w = k - k1
            self.ring(out, dst[0], dst[1], 4 + w * 4, 0.6,
                      (235, 255, 240), 0.45 * (1 - w / 2.6), width=2)
        flash = bump(k, k1 + 1, 1.3) * 0.20
        if flash > 0.01:
            y0, y1 = shelf_y, min(self.H - 1, shelf_y + 6)
            reg = out[y0:y1 + 1, 52:168].astype(float)
            out[y0:y1 + 1, 52:168] = np.clip(
                reg * (1 - flash) + 255 * flash, 0, 255).astype(np.uint8)

    def _perim(self, u):
        """Ponto no perímetro do neon do jornal (sentido horário)."""
        x0, y0, x1, y1 = 206, 78, 432, 336
        w, h = x1 - x0, y1 - y0
        p = u * 2 * (w + h)
        if p < w:
            return (x0 + p, y0)
        p -= w
        if p < h:
            return (x1, y0 + p)
        p -= h
        if p < w:
            return (x1 - p, y1)
        return (x0, y1 - (p - w))

    def frame(self, k):
        k = k % N  # frame(30) == frame(0) bit-a-bit
        out = self.base.copy()
        # fagulha correndo o neon (muda todo quadro; evita merge no encoder)
        sx, sy = self._perim(k / N)
        self.star(out, sx, sy, 2, 0.7, (190, 255, 215))
        # neon do jornal: 2 ciclos por loop
        self._layer(out, self.paper_glow,
                    0.10 + 0.08 * math.sin(TAU * 2 * k / N), (57, 255, 156))
        # luminária em antifase
        self._layer(out, self.lamp_glow,
                    0.10 + 0.07 * math.sin(TAU * 2 * k / N + math.pi),
                    (120, 255, 170))
        # plantio das 3 folhas
        for (k0, k1, src, ctl, dst, shelf_y) in self.sheets:
            self._sheet_flight(out, k, k0, k1, src, ctl, dst, shelf_y)
        # brilhos na manchete (janela fechada: longe das bordas do loop)
        self.star(out, 240, 132, 3, bump(k, 6, 1.2) * 0.9)
        self.star(out, 388, 196, 3, bump(k, 21, 1.2) * 0.9)
        return out


def main():
    rig = Rig()
    frames, closure, qa = finalize(
        rig, OUT, meta_extra=dict(mission='p1_02',
                                  label='PLANTAR FAKE NEWS',
                                  beats='neon do jornal pulsa (2 ciclos); '
                                        'luminária em antifase; 3 folhas '
                                        'plantadas na banca c/ pouso+flash; '
                                        'brilhos na manchete'))
    print('closure', qa['Q1_loop_closure'],
          'bytes', qa['Q6_entrega']['bytes'])


if __name__ == '__main__':
    main()

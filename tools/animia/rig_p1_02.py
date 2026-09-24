#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/animia/rig_p1_02.py — cena v7 'PLANTAR FAKE NEWS' (p1_02), arte 2.

Arte nova gerada no estilo do jogo (estufa de fake news: rotativa com
volante, planta-jornal, cientista regando). Rig estrutural: base imutável
reconstruída nos vãos móveis + overlays periódicos interpolados
(N=30 @ 5 fps, 6 s, loop perfeito):
  * volante: raios+cubo recortados giram 360°/loop sobre o vão reconstruído;
  * impressão: folha da slot desliza, destaca, voa pra pilha; nova folha nasce;
  * planta-jornal balança ±2° (rotação em canvas cheio, pivô no solo);
  * gotas do regador caem no vaso (2 fases);
  * ondas de rádio da antena (anéis periódicos);
  * lâmpadas vermelho/verde alternam; neon da planta pulsa; brilho na manchete.
Personagem nunca cortado. Ver docs/ANIM_V7_RIG.md.
"""
from __future__ import annotations
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from riglib import N, BaseRig, bump, finalize, lerp, smooth

HERE = os.path.dirname(os.path.abspath(__file__))
POSTER = os.path.normpath(os.path.join(
    HERE, '../../src/assets/anim/p1_02/poster.webp'))
OUT = os.path.normpath(os.path.join(
    HERE, '../../src/assets/anim/p1_02/v7'))
TAU = 2 * math.pi

# geometria medida (640x360)
WCX, WCY, WRX, WRY = 73.5, 188.5, 54.5, 69.5      # aro frontal do volante
ORX, ORY = 45.0, 60.0                              # vão interno (abertura)
SLOT_Y = 266                                       # topo da abertura da slot
STACK_LAND = (244, 236)
ROSE = (302, 262)
SOIL = (327, 281)
ANT = (176, 20)
LAMP_R = (162, 186)
LAMP_G = (187, 185)
PLANT_PIV = (327, 282)
PLANT_BB = (240, 60, 394, 282)


def _feather(m, r=1):
    img = Image.fromarray((m * 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(r)),
                      dtype=float) / 255.0


def _ellipse(shape, cx, cy, rx, ry):
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2


class Rig(BaseRig):
    def __init__(self):
        p = np.asarray(Image.open(POSTER).convert('RGB')).astype(int)
        self.orig = p.copy()
        base = p.copy()
        H, W, _ = p.shape

        # ================= volante: reconstrói o vão =================
        def edge_x(y):  # borda esquerda da máquina atrás do volante
            return 92.5 + (y - 188) * 0.02

        e = _ellipse((H, W), WCX, WCY, ORX, ORY)
        open_m = e <= 1.0
        ys, xs = np.nonzero(open_m)
        for y in range(ys.min(), ys.max() + 1):
            row = np.nonzero(open_m[y])[0]
            if len(row) == 0:
                continue
            left = p[y, 18:26].mean(axis=0)     # parede teal
            right = p[y, 143:149].mean(axis=0)  # painel/rolo da máquina
            ex = edge_x(y)
            for x in row:
                if abs(x - ex) <= 1:
                    base[y, x] = (24, 26, 24)
                elif x < ex:
                    base[y, x] = left
                else:
                    base[y, x] = right
        # sombra interna no vão (profundidade)
        band = (e <= 1.0) & (e >= 0.80)
        base[band] = (base[band] * 0.80).astype(int)

        # sprite dos raios em canvas cheio (máscara: vermelho + outlines)
        x0, y0 = int(WCX - ORX - 3), int(WCY - ORY - 3)
        x1, y1 = int(WCX + ORX + 3), int(WCY + ORY + 3)
        crop = p[y0:y1, x0:x1]
        r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]
        ecr = _ellipse(crop.shape[:2], crop.shape[1] / 2, crop.shape[0] / 2,
                       ORX, ORY)
        red_m = (r - g > 35) & (r - b > 35) & (ecr <= 0.98)
        dark_m = (r < 75) & (g < 75) & (b < 75) & (ecr <= 0.98)
        spok = red_m | dark_m
        alpha = _feather(spok, 0.7)
        canvas = np.zeros((H, W, 4), np.uint8)
        canvas[y0:y1, x0:x1, :3] = crop
        canvas[y0:y1, x0:x1, 3] = (alpha * 255).astype(np.uint8)
        self.spoke_canvas = canvas

        # ================= slot sem folha =================
        dark = p[270, 126]
        for y in range(258, 278):
            for x in range(128, 209):
                if 124 <= x <= 196:
                    base[y, x] = dark
                elif x < 124:
                    base[y, x] = p[y, 120]
                else:
                    base[y, x] = p[y, 199]
        for y in range(278, 314):
            for x in range(128, 209):
                t = (x - 128) / 81.0
                base[y, x] = p[y, 124] * (1 - t) + p[y, 204] * t
        for y in range(278, 314):
            base[y, 130:206] = (base[y, 130:206] * 0.92).astype(int)

        sx0, sy0, sx1, sy1 = 128, 258, 218, 314
        scrop = p[sy0:sy1, sx0:sx1]
        r, g, b = scrop[..., 0], scrop[..., 1], scrop[..., 2]
        shm = (r > 110) | ((r < 85) & (g < 85) & (b < 85))
        sa = _feather(shm, 0.7)
        self.sheet = np.dstack([scrop, (sa * 255).astype(np.uint8)]
                               ).astype(np.uint8)
        self.sheet_home = (sx0, sy0)

        # ================= planta: parede por plano ajustado =================
        bb = PLANT_BB
        reg = p[bb[1]:bb[3], bb[0]:bb[2]]
        r, g, b = reg[..., 0], reg[..., 1], reg[..., 2]
        pm = ((r > 120) | ((g - r > 25) & (g > 90)) |
              ((r < 60) & (g < 75) & (b < 75)))
        for _ in range(3):
            pm |= np.roll(pm, 1, 0) & np.roll(pm, -1, 0)
            pm |= np.roll(pm, 1, 1) & np.roll(pm, -1, 1)
        hole_c = pm.copy()
        for _ in range(2):
            hm = hole_c.copy()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                hm |= np.roll(hole_c, dy, 0) | np.roll(hole_c, dx, 1)
            hole_c = hm
        hole = np.zeros((H, W), bool)
        hole[bb[1]:bb[3], bb[0]:bb[2]] = hole_c
        # amostras de parede ao redor do bbox -> plano c+ax+by por canal
        pts = []
        for x in range(bb[0], bb[2], 4):
            for y in (50, 53, 56):
                pts.append((x, y))
        for y in range(bb[1], bb[3], 4):
            for x in (230, 233, 236):
                pts.append((x, y))
        for y in range(60, 140, 4):
            for x in (398, 401, 404):
                pts.append((x, y))
        for y in (284, 286):
            for x in list(range(240, 290, 4)) + list(range(368, 394, 4)):
                pts.append((x, y))
        A = np.array([[x, y, 1.0] for x, y in pts])
        cols = np.array([p[y, x] for x, y in pts], float)
        coef, *_ = np.linalg.lstsq(A, cols, rcond=None)
        yy, xx = np.mgrid[0:H, 0:W]
        plane = np.clip(xx[..., None] * coef[0] + yy[..., None] * coef[1] +
                        coef[2], 0, 255)
        # aplica o plano no buraco
        for c in range(3):
            lay = plane[..., c]
            base[..., c] = np.where(hole, np.round(lay), base[..., c])

        pa = _feather(pm, 1.0)
        pcanvas = np.zeros((H, W, 4), np.uint8)
        pcanvas[bb[1]:bb[3], bb[0]:bb[2], :3] = reg
        pcanvas[bb[1]:bb[3], bb[0]:bb[2], 3] = (pa * 255).astype(np.uint8)
        self.plant_canvas = pcanvas
        halo = (p[..., 1] > 120) & (p[..., 1] - p[..., 0] > 40)
        hm = np.zeros_like(halo)
        hm[bb[1]:bb[3], bb[0]:bb[2]] = halo[bb[1]:bb[3], bb[0]:bb[2]]
        self.halo = _feather(hm, 3)

        super().__init__(base.astype(np.uint8))
        self.base = base.astype(np.uint8)

    # ------------------------------------------------------------ helpers
    def _layer(self, out, mask, alpha, color):
        if alpha <= 0.004:
            return
        a = (mask * alpha)[..., None]
        col = np.array(color, float)
        out[:] = np.clip(out * (1 - a) + col * a, 0, 255).astype(np.uint8)

    def _rot_layer(self, out, canvas, center, ang):
        """Rotaciona um canvas RGBA cheio em torno de `center` e compõe."""
        im = Image.fromarray(canvas).rotate(
            ang, center=center, expand=False, resample=Image.BICUBIC)
        a = np.asarray(im)
        al = (a[..., 3:4] / 255.0)
        out[:] = np.clip(a[..., :3] * al + out * (1 - al), 0,
                         255).astype(np.uint8)

    def _drop(self, out, k, off):
        kk = (k + off) % N
        if 0 <= kk <= 6:
            if kk <= 2:
                s = smooth(kk / 2)
                x, y = ROSE[0], ROSE[1] + 3
                al = 0.4 + 0.5 * s
            else:
                t = smooth((kk - 2) / 4)
                x = lerp(ROSE[0], SOIL[0], t)
                y = lerp(ROSE[1] + 3, SOIL[1], t * t)
                al = 0.9
            dim = Image.new('RGBA', (9, 12))
            d = ImageDraw.Draw(dim)
            d.ellipse([2, 3, 7, 10], fill=(140, 200, 225, int(255 * al)))
            d.ellipse([3, 4, 4, 6], fill=(220, 240, 250, int(200 * al)))
            self.paste(out, np.asarray(dim), x - 4, y - 6, alpha=1.0)
        if kk in (6, 7):
            self.ring(out, SOIL[0], SOIL[1], 3 + (kk - 6) * 3, 0.4,
                      (160, 210, 230), 0.35 * (1 - (kk - 6) / 2.5), width=1)

    def _slot_sheet(self, out, off_x, off_y):
        hx, hy = self.sheet_home
        h, w = self.sheet.shape[:2]
        X0, Y0 = hx + int(round(off_x)), hy + int(round(off_y))
        Yc = max(Y0, SLOT_Y - 4)
        X, Y = max(0, X0), max(0, Yc)
        XE, YE = min(self.W, X0 + w), min(self.H, Y0 + h)
        if XE <= X or YE <= Y:
            return
        sx, sy = X - X0, Yc - Y0
        reg = out[Y:YE, X:XE].astype(float)
        spc = self.sheet[sy:sy + (YE - Y), sx:sx + (XE - X), :3].astype(float)
        aa = (self.sheet[sy:sy + (YE - Y), sx:sx + (XE - X), 3:4] / 255.0)
        out[Y:YE, X:XE] = (spc * aa + reg * (1 - aa)).astype(np.uint8)

    # ------------------------------------------------------------ frame
    def frame(self, k):
        k = k % N
        out = self.base.copy()

        # volante: 360° por loop (12°/quadro)
        self._rot_layer(out, self.spoke_canvas, (WCX, WCY), -12.0 * k)

        # folha da slot: desliza, destaca, voa; nova nasce
        if k <= 5:
            off_y = 0 if k <= 2 else smooth((k - 2) / 3) * 8
            self._slot_sheet(out, 0, off_y)
        elif k <= 12:
            t = smooth((k - 6) / 6)
            x = lerp(172, STACK_LAND[0], t)
            y = lerp(268, STACK_LAND[1], t) - 26 * math.sin(math.pi * t)
            ang = 14 * math.sin(math.pi * t)
            sp = np.asarray(Image.fromarray(self.sheet).rotate(
                ang, expand=True, resample=Image.BICUBIC))
            self.paste(out, sp, x - sp.shape[1] / 2, y - sp.shape[0] / 2,
                       alpha=1.0 if k <= 10 else 1 - (k - 10) / 2.5)
        if k >= 13:
            grow = smooth((k - 13) / 16)
            self._slot_sheet(out, 0, -46 * (1 - grow))
        if 12 <= k <= 14:
            w = k - 12
            self.ring(out, STACK_LAND[0], STACK_LAND[1] + 6, 3 + w * 4, 0.5,
                      (240, 245, 235), 0.4 * (1 - w / 3), width=2)

        # planta balança ±2° (1 ciclo), pivô no solo
        self._rot_layer(out, self.plant_canvas, PLANT_PIV,
                        2.0 * math.sin(TAU * k / N))

        # gotas do regador (2 fases)
        self._drop(out, k, 0)
        self._drop(out, k, 15)

        # ondas da antena (2 anéis defasados)
        for off in (0, 15):
            kk = (k + off) % N
            t = kk / 15
            self.ring(out, ANT[0], ANT[1], 3 + t * 22, 1.0,
                      (150, 255, 190), 0.35 * (1 - t), width=1)

        # lâmpadas alternadas
        self.glow(out, LAMP_R[0], LAMP_R[1], 7, 7, (255, 70, 60),
                  0.16 + 0.16 * math.sin(TAU * k / N))
        self.glow(out, LAMP_G[0], LAMP_G[1], 7, 7, (70, 255, 120),
                  0.16 + 0.16 * math.sin(TAU * k / N + math.pi))

        # neon da planta pulsa + brilho na manchete
        self._layer(out, self.halo, 0.06 + 0.05 * math.sin(TAU * 2 * k / N),
                    (57, 255, 156))
        self.star(out, 268, 92, 3, bump(k, 7, 1.2) * 0.9)
        self.star(out, 372, 140, 3, bump(k, 22, 1.2) * 0.9)
        return out


def main():
    rig = Rig()
    frames, closure, qa = finalize(
        rig, OUT, meta_extra=dict(mission='p1_02',
                                  label='PLANTAR FAKE NEWS',
                                  arte='gerada no estilo do jogo (estufa de '
                                       'fake news)',
                                  beats='volante 360°/loop; folha imprime, '
                                        'destaca e voa pra pilha; planta '
                                        'balança; gotas do regador; ondas da '
                                        'antena; lâmpadas alternadas; neon '
                                        'pulsa'))
    print('closure', qa['Q1_loop_closure'],
          'bytes', qa['Q6_entrega']['bytes'])


if __name__ == '__main__':
    main()

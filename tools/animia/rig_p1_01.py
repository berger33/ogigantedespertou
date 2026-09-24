#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/rig_p1_01.py — RIG v7 da missão p1_01 “COMPRAR COM CRIPTO” 💻

Cena: conspiracionista no laptop; gráfico de cripto sobe; ele dá “enter”, uma
moeda voa do laptop até o gráfico (pump flash); vapor do café sobe contínuo;
luz da lâmpada e glow da tela pulsam. Personagem NUNCA é recortado — 100%
overlays periódicos sobre a base imutável (vapor inpaintado).

30 quadros @ 5 fps, 6 s, loop perfeito (frame 30 ≡ 0).

Uso: python3 tools/animia/rig_p1_01.py [--root src/assets/anim]
"""
from __future__ import annotations
import argparse, math, os

import numpy as np
from PIL import Image, ImageDraw

import importlib.util
_here = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('riglib', os.path.join(_here, 'riglib.py'))
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

# retângulo do plot do gráfico (cobre a linha original; botões/números ficam)
CH_X0, CH_Y0, CH_X1, CH_Y1 = 437, 0, 598, 48
PAT = 80.0          # período do padrão da linha (2 ciclos na tela)


def line_y(x, shift):
    u = (x + shift) / PAT
    return (26 - 9 * math.sin(2 * math.pi * u)
            - 6 * math.sin(4 * math.pi * u + 1.3)
            - 3 * math.sin(6 * math.pi * u + 2.1)
            - 2 * math.sin(14 * math.pi * u))


def bez(t, p0, p1, p2):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1])


class Rig(L.BaseRig):
    def __init__(self, mission_dir):
        poster = np.asarray(
            Image.open(os.path.join(mission_dir, 'poster.webp')).convert('RGB')
        ).astype(np.uint8)
        super().__init__(poster)
        # vapor original some da base (vira vapor procedural periódico)
        R, G, B = (poster[..., i].astype(int) for i in range(3))
        bright = (R > 150) & (G > 150) & (B > 140)
        bb = np.zeros_like(bright)
        bb[293:322, 478:542] = True
        steam = bright & bb
        steam = L.ring_of(steam, 1)
        self.base = L.inpaint_region(poster, steam)
        # cor de fundo da tela por linha (coluna limpa à esquerda do plot)
        self.screen_col = poster[CH_Y0:CH_Y1 + 1, 433:436].astype(float).mean(axis=1)

    def frame(self, k):
        k = k % L.N
        out = self.base.copy().astype(float)
        pump = L.bump(k, 15, 2.0)
        enter = L.bump(k, 11, 1.6)
        # glow da tela no rosto (flicker de digitação + pulso do enter)
        self.glow(out, 300, 195, 90, 60, (126, 240, 140),
                  .05 + .06 * enter + .015 * math.sin(2 * L.TAU * k / L.N))
        # lâmpada: pulso quente lento
        self.glow(out, 95, 125, 70, 45, (255, 190, 80),
                  .05 + .02 * math.sin(L.TAU * k / L.N))
        # vapor do café: puffs que sobem em ciclo contínuo
        for (xc, ph) in ((500, 0.0), (517, 0.5)):
            for i in range(6):
                s = (i / 6 + k / L.N + ph) % 1.0
                y = 316 - 46 * s
                x = xc + 5 * math.sin(L.TAU * (s * 1.5 + ph))
                self.glow(out, x, y, 2.5 + 3.5 * s, 3 + 4 * s,
                          (228, 233, 228), math.sin(math.pi * s) * .38)
        # sparkles de digitação no teclado
        for (x, y, f, ph, sz) in ((172, 334, 1, .0, 3), (216, 342, 2, 1.7, 3),
                                  (256, 337, 1, 3.9, 4)):
            a = max(0.0, math.sin(L.TAU * f * k / L.N + ph)) ** 3 * .7
            if a > .02:
                self.star(out, x, y, sz, a, color=(240, 255, 235))
        # ---- vetor: gráfico + moeda
        d = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        dr = ImageDraw.Draw(d)
        # fundo da tela (por linha) + grade
        for y in range(CH_Y0, CH_Y1 + 1):
            c = tuple(int(v) for v in self.screen_col[y - CH_Y0])
            dr.line([CH_X0, y, CH_X1, y], fill=c)
        for gx in (470, 503, 536, 569):
            dr.line([gx, CH_Y0, gx, CH_Y1], fill=(21, 50, 30))
        for gy in (12, 24, 36):
            dr.line([CH_X0, gy, CH_X1, gy], fill=(21, 50, 30))
        # linha ticker rolando p/ esquerda (1 padrão por loop => fecha exato)
        shift = PAT * k / L.N
        hot = min(1.0, pump * 1.2)
        col = (int(126 + 90 * hot), 255, int(120 + 80 * hot))
        pts = [(x, line_y(x, shift)) for x in range(CH_X0, CH_X1 + 1, 2)]
        dr.line(pts, fill=(35, 110, 45), width=4)
        dr.line(pts, fill=col, width=2)
        hx, hy = pts[-1]
        blink = .6 + .4 * math.sin(2 * L.TAU * k / L.N)
        dr.ellipse([hx - 3, hy - 3, hx + 3, hy + 3],
                   fill=(int(180 + 60 * blink), 255, int(160 + 60 * blink)))
        # moeda voa laptop → gráfico (k10–14)
        if 10 <= k <= 14:
            t = (k - 10) / 4
            cx, cy = bez(L.ease_in(t, 1.2), (330, 175), (430, 120), (555, 25))
            a = min(1, (k - 9) / 1.0)
            r = 7
            dr.ellipse([cx - r, cy - r, cx + r, cy + r],
                       fill=(232, 190, 74), outline=(40, 30, 12), width=2)
            dr.polygon([(cx, cy - 4), (cx + 3, cy), (cx, cy + 4), (cx - 3, cy)],
                       fill=(255, 240, 180))
        out = np.asarray(d).astype(float)
        # anel no impacto da moeda
        for off in (0, 1):
            kk = k - (14 + off)
            if 0 <= kk <= 4:
                self.ring(out, 566, 22, 4 + kk * 3, 1.0, (160, 255, 170),
                          .5 * (1 - kk / 5), width=2)
        return np.clip(out, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='src/assets/anim')
    args = ap.parse_args()
    mdir = os.path.join(args.root, 'p1_01')
    out = os.path.join(mdir, 'v7')
    rig = Rig(mdir)
    frames, closure, qa = L.finalize(rig, out, meta_extra=dict(
        id='p1_01', label='COMPRAR COM CRIPTO',
        anchor='poster.webp (personagem intocado)',
        beats=[
         'k00–09 · digita: flicker da tela, sparkles no teclado, ticker rolando',
         'k10–14 · ENTER: moeda de cripto voa do laptop até o gráfico',
         'k14–17 · pump flash + anel no impacto; linha brilha',
         'k18–29 · glow assenta; vapor do café sobe contínuo; lâmpada pulsa',
        ]))
    print('closure', qa['Q1_loop_closure'], 'bytes', qa['Q6_entrega']['bytes'])


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/recolor_v7.py — veneno verde (pedido do dono, set/2026).

Recolore o poster-âncora de p5_02:
  * líquido da pipeta + glow ao redor → verde (hue shift −45°, S/V preservados)
  * gota central → verde, colada de volta SEM halo baked (o glow vira overlay
    procedural no rig) — recorte limpo: interior + outline, nada da beirada
  * água do tanque, gota da torneira e copinho → intocados (continuam ciano)

Idempotente: se o líquido da pipeta já estiver verde, não faz nada.
Uso: python3 tools/animia/recolor_v7.py --mission p5_02
"""
from __future__ import annotations
import argparse, os

import numpy as np
from PIL import Image, ImageFilter

import importlib.util
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('rig', os.path.join(_here, 'rig_v7.py'))
rigmod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rigmod)

GREEN_PROBE = (300, 168)  # pixel do líquido da pipeta


def hue_shift(im, mask, dh=-32):
    """Shift de matiz só na máscara (PIL HSV), preserva S/V e outlines."""
    hsv = np.asarray(Image.fromarray(im).convert('HSV')).astype(int)
    hsv[..., 0] = np.where(mask, (hsv[..., 0] + dh) % 256, hsv[..., 0])
    return np.asarray(Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mission', default='p5_02')
    ap.add_argument('--root', default='src/assets/anim')
    args = ap.parse_args()
    p = os.path.join(args.root, args.mission, 'poster.webp')
    im = np.asarray(Image.open(p).convert('RGB')).astype(np.uint8)

    # idempotência: líquido da pipeta já verde? (G bem maior que B)
    r, g, b = im[GREEN_PROBE[1], GREEN_PROBE[0]].astype(int)
    if g - b > 40:
        print('já verde — nada a fazer', (r, g, b))
        return

    # 1) líquido da pipeta + glow: bbox restrito, jamais toca tanque/torneira
    mask_a = np.zeros(im.shape[:2], bool)
    mask_a[75:206, 195:350] = True
    R, G, B = im[..., 0].astype(int), im[..., 1].astype(int), im[..., 2].astype(int)
    mask_a &= (G - R >= 70) & (G >= 130)
    im = hue_shift(im, mask_a)

    # 2) gota central: recorta limpo ANTES, inpaint o furo, recolore o sprite e
    #    cola de volta SEM halo baked (o glow vira overlay procedural no rig)
    sil = rigmod.drop_silhouette(im.shape[0], im.shape[1])
    dm = rigmod.tight_drop_mask(im, 296, 200, 362, 270, sil)
    ys, xs = np.nonzero(dm)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    sprite = im[y0:y1 + 1, x0:x1 + 1].copy()
    sm = dm[y0:y1 + 1, x0:x1 + 1]
    sprite = hue_shift(sprite, sm)
    im = rigmod.inpaint_hole(im, 296, 200, 362, 270)   # somee o halo ciano
    amask = Image.fromarray((sm * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(.6))
    rgba = np.dstack([sprite, np.asarray(amask)]).astype(np.uint8)
    base = Image.fromarray(im)
    base.paste(Image.fromarray(rgba), (x0, y0), Image.fromarray(np.asarray(amask)))
    im = np.asarray(base)

    Image.fromarray(im).save(p, quality=90)
    px = im[GREEN_PROBE[1], GREEN_PROBE[0]].astype(int)
    print('poster recolocado → líquido pipeta agora', tuple(px))


if __name__ == '__main__':
    main()

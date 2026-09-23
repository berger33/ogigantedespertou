#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/tween.py — in-betweens suaves entre keyframes IA (v6.1).

Entre cada par de poses-chave IA (A, B) gera N desenhos intermediários:
  * fundo: crossfade com easing smoothstep (áreas estáticas ficam perfeitas);
  * elementos em movimento (componentes conexos do mapa de diff): estimado o
    deslocamento (δ) por correlação FFT (template matching); o recorte do
    elemento em A viaja δ·e(t) enquanto o de B chega de −δ·(1−e(t)) — smear
    com motion trail, translação pura (sem deformar a pintura).

Suavidade medida: delta médio entre desenhos consecutivos cai ~5× vs. o salto
direto entre poses (lint Q8).
"""
from __future__ import annotations
import numpy as np
from collections import deque
from PIL import Image

EASE = lambda t: t * t * (3 - 2 * t)  # smoothstep


def _smoothstep(t: float) -> float:
    return EASE(max(0.0, min(1.0, t)))


def diff_mask(A: np.ndarray, B: np.ndarray, thr: float = 12.0) -> np.ndarray:
    d = np.abs(A.astype(np.float32) - B.astype(np.float32)).mean(axis=2)
    m = (d > thr).astype(np.uint8)
    # fecha buracos pequenos
    from PIL import ImageFilter
    mi = Image.fromarray(m * 255).filter(ImageFilter.MaxFilter(5)).filter(
        ImageFilter.MinFilter(5))
    return np.asarray(mi) > 127


def components(mask: np.ndarray, min_area: int = 150, top: int = 3):
    """Componentes conexos (4-neighborhood) por área descrescente (BFS)."""
    H, W = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    comps = []
    for y0 in range(0, H, 4):
        for x0 in range(0, W, 4):
            if seen[y0, x0] or not mask[y0, x0]:
                continue
            q = deque([(y0, x0)])
            seen[y0, x0] = True
            pix = []
            while q:
                y, x = q.popleft()
                pix.append((y, x))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < H and 0 <= nx < W and not seen[ny, nx] and mask[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            if len(pix) >= min_area:
                ys = [p[0] for p in pix]; xs = [p[1] for p in pix]
                comps.append(dict(pixels=pix, area=len(pix),
                                  bbox=(max(0, min(xs)), max(0, min(ys)),
                                        min(W, max(xs) + 1), min(H, max(ys) + 1))))
    comps.sort(key=lambda c: -c["area"])
    return comps[:top]


def match_offset(A: np.ndarray, B: np.ndarray, bbox, radius: int = 70) -> tuple:
    """Deslocamento (dx, dy) do recorte A→B por correlação FFT normalizada."""
    x0, y0, x1, y1 = bbox
    T = A[y0:y1, x0:x1].mean(axis=2).astype(np.float32)
    T = T - T.mean()
    tnorm = np.sqrt((T * T).sum()) + 1e-6
    ex0, ey0 = max(0, x0 - radius), max(0, y0 - radius)
    ex1, ey1 = min(A.shape[1], x1 + radius), min(A.shape[0], y1 + radius)
    Wimg = B[ey0:ey1, ex0:ex1].mean(axis=2).astype(np.float32)
    fh = max(Wimg.shape[0] + T.shape[0], 32)
    fw = max(Wimg.shape[1] + T.shape[1], 32)
    FT = np.fft.rfft2(T, (fh, fw))
    FW = np.fft.rfft2(Wimg, (fh, fw))
    corr = np.fft.irfft2(FW * np.conj(FT), (fh, fw))
    # energia local de W para normalização
    ones = np.ones_like(T)
    energy = np.fft.irfft2(np.fft.rfft2(Wimg ** 2, (fh, fw)) *
                           np.fft.rfft2(ones, (fh, fw)).conj(), (fh, fw))
    corr = corr / (np.sqrt(np.maximum(energy, 1e-6)) * tnorm + 1e-6)
    cy, cx = T.shape[0] - 1, T.shape[1] - 1
    win = corr[cy:cy + Wimg.shape[0] - T.shape[0] + 1,
               cx:cx + Wimg.shape[1] - T.shape[1] + 1]
    iy, ix = np.unravel_index(np.argmax(win), win.shape)
    peak = float(win[iy, ix])
    dy = (ey0 + iy) - y0
    dx = (ex0 + ix) - x0
    return (int(dx), int(dy)), peak


def _soft_alpha(mask_patch: np.ndarray) -> np.ndarray:
    from PIL import ImageFilter
    a = Image.fromarray((mask_patch * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(2.0))
    return np.asarray(a, dtype=np.float32)[..., None] / 255


def _over(base: np.ndarray, patch_rgb: np.ndarray, patch_a: np.ndarray,
          pos, H, W) -> None:
    x, y = pos
    h, w = patch_rgb.shape[:2]
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(w, W - x), min(h, H - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    dx0, dy0 = max(0, x), max(0, y)
    a = patch_a[sy0:sy1, sx0:sx1]
    region = base[dy0:dy0 + (sy1 - sy0), dx0:dx0 + (sx1 - sx0)]
    base[dy0:dy0 + (sy1 - sy0), dx0:dx0 + (sx1 - sx0)] = (
        region * (1 - a) + patch_rgb[sy0:sy1, sx0:sx1] * a)


def tween(A: np.ndarray, B: np.ndarray, t: float, n_comp: int = 3,
          radius: int = 70, trail: float = 0.9) -> np.ndarray:
    """Desenho intermediário no instante t ∈ (0,1)."""
    e = _smoothstep(t)
    base = A.astype(np.float32) * (1 - e) + B.astype(np.float32) * e
    H, W = base.shape[:2]
    mask = diff_mask(A, B)
    for comp in components(mask, top=n_comp):
        x0, y0, x1, y1 = comp["bbox"]
        (dx, dy), score = match_offset(A, B, comp["bbox"], radius)
        if score < 0.70 or (abs(dx) + abs(dy)) < 3:
            continue  # mudança não-translacional → fica no crossfade
        pad = 3
        px0, py0 = max(0, x0 - pad), max(0, y0 - pad)
        px1, py1 = min(W, x1 + pad), min(H, y1 + pad)
        mloc = mask[py0:py1, px0:px1]
        aA = _soft_alpha(mloc) * (1 - e) * trail
        aB = _soft_alpha(mloc) * e * trail
        rgbA = A[py0:py1, px0:px1]
        rgbB = B[py0:py1, px0:px1]
        # elemento de A avança em direção à posição dele em B…
        _over(base, rgbA, aA, (px0 + int(round(dx * e)), py0 + int(round(dy * e))), H, W)
        # …e o de B recua pelo caminho que ainda falta (motion trail duplo)
        _over(base, rgbB, aB, (px0 - int(round(dx * (1 - e))), py0 - int(round(dy * (1 - e)))), H, W)
    return np.clip(base, 0, 255).astype(np.uint8)


def build_sequence(keys: dict, n_tweens: int = 4) -> list:
    """keys: {nome: np.ndarray}. Retorna lista de desenhos (np.ndarray) com
    tweens entre pares consecutivos (sem duplicar endpoints)."""
    names = sorted(keys)
    seq = [np.clip(keys[names[0]], 0, 255).astype(np.uint8)]
    for a, b in zip(names, names[1:]):
        for k in range(1, n_tweens + 1):
            seq.append(tween(keys[a], keys[b], k / (n_tweens + 1)))
        seq.append(np.clip(keys[b], 0, 255).astype(np.uint8))
    return seq

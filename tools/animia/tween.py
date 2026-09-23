#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/tween.py v3 — in-betweens suaves entre keyframes IA (v6.1).

Regras (auditadas após feedback do dono — "ponteiro bagunçado", "gotas acima"):
  * PAREAMENTO 1:1 — cada componente do lado A casa com no máximo um do lado B
    (template matching FFT). O elemento viaja UMA vez, do seu lugar em A até o
    lugar dele em B, num caminho único e desaparecendo (sem trilha dupla —
    era isso que duplicava gotas e criava cópias acima da pipeta).
  * Componente sem par (aparece/some) faz fade NO LUGAR (crossfade puro) —
    nunca "viaja" para longe.
  * Zonas de crossfade puro (tween.json → crossfade_rects): o ponteiro do
    medidor é ROTAÇÃO — traduzi-lo criava dois ponteiros fantasmas. Ali só
    crossfade (com keyframe intermediário IA, o arco fica contínuo).
  * Suavidade: easing smoothstep; delta entre desenhos consecutivos medido
    pelo lint Q8.
"""
from __future__ import annotations
import numpy as np
from collections import deque
from PIL import Image, ImageFilter

DEFAULTS = dict(thr=12.0, min_area=60, max_components=8, radius=70,
                match_min=0.72, min_travel=3, trail=0.85, crossfade_rects=[])


def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def diff_mask(A: np.ndarray, B: np.ndarray, thr: float = 12.0) -> np.ndarray:
    d = np.abs(A.astype(np.float32) - B.astype(np.float32)).mean(axis=2)
    m = (d > thr).astype(np.uint8)
    mi = Image.fromarray(m * 255).filter(ImageFilter.MaxFilter(5)).filter(
        ImageFilter.MinFilter(5))
    return np.asarray(mi) > 127


def components(mask: np.ndarray, min_area: int = 60, top: int = 8):
    H, W = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    comps = []
    for y0 in range(0, H, 3):
        for x0 in range(0, W, 3):
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
    tnorm = np.sqrt(max((T * T).sum(), 1e-6))
    ex0, ey0 = max(0, x0 - radius), max(0, y0 - radius)
    ex1, ey1 = min(A.shape[1], x1 + radius), min(A.shape[0], y1 + radius)
    Wimg = B[ey0:ey1, ex0:ex1].mean(axis=2).astype(np.float32)
    if Wimg.shape[0] < T.shape[0] or Wimg.shape[1] < T.shape[1]:
        return (0, 0), 0.0
    fh = max(Wimg.shape[0] + T.shape[0], 32)
    fw = max(Wimg.shape[1] + T.shape[1], 32)
    FT = np.fft.rfft2(T, (fh, fw))
    FW = np.fft.rfft2(Wimg, (fh, fw))
    corr = np.fft.irfft2(FW * np.conj(FT), (fh, fw))
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


def _in_rects(cx: float, cy: float, rects) -> bool:
    for (x0, y0, x1, y1) in rects:
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            return True
    return False


def _soft_alpha(mask_patch: np.ndarray, blur: float = 2.0) -> np.ndarray:
    a = Image.fromarray((mask_patch * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(blur))
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


def tween(A: np.ndarray, B: np.ndarray, t: float, cfg: dict | None = None) -> np.ndarray:
    """Desenho intermediário no instante t ∈ (0,1)."""
    c = dict(DEFAULTS)
    if cfg:
        c.update(cfg)
    e = _smoothstep(t)
    base = A.astype(np.float32) * (1 - e) + B.astype(np.float32) * e
    H, W = base.shape[:2]
    mask = diff_mask(A, B, c["thr"])
    for comp in components(mask, c["min_area"], c["max_components"]):
        x0, y0, x1, y1 = comp["bbox"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if _in_rects(cx, cy, c["crossfade_rects"]):
            continue  # rotação/luz → crossfade puro (sem fantasmas)
        (dx, dy), score = match_offset(A, B, comp["bbox"], c["radius"])
        if score < c["match_min"] or (abs(dx) + abs(dy)) < c["min_travel"]:
            continue  # aparece/some → fica no crossfade, no lugar certo
        pad = 3
        px0, py0 = max(0, x0 - pad), max(0, y0 - pad)
        px1, py1 = min(W, x1 + pad), min(H, y1 + pad)
        mloc = mask[py0:py1, px0:px1]
        rgbA = A[py0:py1, px0:px1]
        # caminho ÚNICO: o elemento de A viaja até sua posição em B e some
        aA = _soft_alpha(mloc) * (1 - e) * c["trail"]
        _over(base, rgbA, aA,
              (px0 + int(round(dx * e)), py0 + int(round(dy * e))), H, W)
    return np.clip(base, 0, 255).astype(np.uint8)


def build_sequence(keys: dict, n_tweens: int = 4, cfg: dict | None = None) -> list:
    """keys: {nome: np.ndarray} em ordem natural (k01, k02, k05b, …)."""
    names = sorted(keys)
    seq = [np.clip(keys[names[0]], 0, 255).astype(np.uint8)]
    for a, b in zip(names, names[1:]):
        for k in range(1, n_tweens + 1):
            seq.append(tween(keys[a], keys[b], k / (n_tweens + 1), cfg))
        seq.append(np.clip(keys[b], 0, 255).astype(np.uint8))
    return seq

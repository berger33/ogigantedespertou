#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/anim/rig.py — camadas, pivôs e transformações AFINS (spec v4, R1–R5).

Este módulo é a garantia anti-gelatina no nível de arquitetura:
  * R1: a placa (plate) NUNCA é deformada — ela entra na composição intocada;
  * R2: recortes só recebem transformação afim (translação / rotação / escala);
  * R3: squash & stretch limitado a SQUASH_MAX (8%) e só onde o board declarar;
  * R4: toda rotação/escala acontece em torno do PIVÔ declarado (anatômico);
  * R5: trajetórias em arco são obtidas compondo dx/dy com easings distintos.

Também fornece o cutter de camadas por DIFERENÇA (E2): dois estados pintados
pela IA (ex.: "feixe ligado" vs "feixe desligado") viram uma camada RGBA com
silhueta real, após alinhamento translacional automático (phase correlation).
"""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageFilter

SQUASH_MAX = 0.08          # R3 — máx. 8% de deformação não-uniforme
ALPHA_EDGE_MAX = 0.35      # fração máx. de pixels de borda "meio透明" (L2)


# --------------------------------------------------------------------------- #
# Camada
# --------------------------------------------------------------------------- #
@dataclass
class Layer:
    name: str
    file: str
    z: int = 10
    kind: str = "sprite"          # "sprite" (alpha over) | "patch" (substitui pixels)
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)   # x, y, w, h no quadro
    pivot: Tuple[float, float] = (0.5, 0.5)          # fração do bbox (R4)
    soft_squash: bool = False                        # R3: permite squash ≤ 8%
    group: Optional[str] = None                      # troca de pose dentro do grupo
    patch_over: Optional[str] = None                 # L7: o que este patch cobre
    img: Optional[Image.Image] = field(default=None, repr=False)

    def load(self, root: str) -> Image.Image:
        if self.img is None:
            p = os.path.join(root, self.file)
            self.img = Image.open(p).convert("RGBA")
            if self.bbox == (0, 0, 0, 0):
                self.bbox = (0, 0, self.img.width, self.img.height)
        return self.img

    def pivot_px(self) -> Tuple[float, float]:
        x, y, w, h = self.bbox
        return (x + w * self.pivot[0], y + h * self.pivot[1])


def clamp_squash(sx: float, sy: float, allow: bool) -> Tuple[float, float]:
    """R3: se a camada não é macia, escala deve ser uniforme; senão ≤ 8%."""
    if abs(sx - 1) < 1e-6 and abs(sy - 1) < 1e-6:
        return sx, sy
    if not allow:
        s = (sx + sy) / 2.0
        return s, s
    d = sy - sx
    if abs(d) > SQUASH_MAX:
        m = (sx + sy) / 2.0
        sx = m - (SQUASH_MAX / 2) * (1 if d < 0 else -1) * -1
        sy = m + (SQUASH_MAX / 2) * (1 if d < 0 else -1) * -1
        # recompute cleanly:
        sx = m - d / 2 * (SQUASH_MAX / abs(d))
        sy = m + d / 2 * (SQUASH_MAX / abs(d))
    return sx, sy


def affine_paste(canvas: Image.Image, layer_img: Image.Image,
                 bbox: Tuple[int, int, int, int],
                 pivot: Tuple[float, float],
                 dx: float, dy: float, rot: float,
                 sx: float, sy: float, alpha: float,
                 kind: str = "sprite",
                 soft_squash: bool = False) -> None:
    """Aplica UMA transformação afim em torno do pivô e compõe no canvas.

    Implementação: matriz 2x3 inversa para Image.transform (AFFINE), renderizada
    num RGBA do tamanho do quadro — sem warp, sem interpolação da placa.
    """
    if alpha <= 0.003:
        return
    sx, sy = clamp_squash(sx, sy, soft_squash)
    W, H = canvas.size
    x, y, w, h = bbox
    px, py = x + w * pivot[0], y + h * pivot[1]

    # matriz direta: T(pivô+delta) · R · S · T(-pivô)
    a = np.cos(np.radians(rot)) * sx
    b = -np.sin(np.radians(rot)) * sx
    c = np.sin(np.radians(rot)) * sy
    d = np.cos(np.radians(rot)) * sy
    tx = (px + dx) - (a * px + b * py)
    ty = (py + dy) - (c * px + d * py)

    src = layer_img
    if alpha < 0.997:
        r, g, bl, al = src.split()
        al = al.point(lambda v: int(v * alpha))
        src = Image.merge("RGBA", (r, g, bl, al))

    # inversa para PIL (mapeia destino -> origem)
    det = a * d - b * c
    if abs(det) < 1e-9:
        return
    ia, ib, ic, id_ = d / det, -b / det, -c / det, a / det
    itx = -(ia * tx + ib * ty)
    ity = -(ic * tx + id_ * ty)

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # coloca a imagem de origem na posição do bbox dentro de um pano maior
    pad = max(W, H)
    big = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    big.paste(src, (pad + x, pad + y), src)
    warped = big.transform((W, H), Image.AFFINE,
                           (ia, ib, itx + pad, ic, id_, ity + pad),
                           resample=Image.BICUBIC)
    if kind == "patch":
        # patch substitui: primeiro apaga o destino onde há alpha, depois cola
        mask = warped.split()[3]
        base = canvas.copy()
        base.paste(Image.new("RGBA", (W, H), (0, 0, 0, 0)), (0, 0), mask)
        canvas.paste(base, (0, 0))
        canvas.alpha_composite(warped)
    else:
        canvas.alpha_composite(warped)


# --------------------------------------------------------------------------- #
# Cutter por diferença (E2): estado A vs estado B -> camada RGBA
# --------------------------------------------------------------------------- #
def _align_translation(ref: np.ndarray, mov: np.ndarray) -> Tuple[int, int]:
    """Phase correlation (só translação) para alinhar dois estados pintados."""
    f_ref = np.fft.rfft2(ref)
    f_mov = np.fft.rfft2(mov)
    eps = 1e-9
    cross = f_ref * np.conj(f_mov)
    cross /= (np.abs(cross) + eps)
    corr = np.fft.irfft2(cross, s=ref.shape)
    idx = np.unravel_index(np.argmax(corr), corr.shape)
    dy = idx[0] if idx[0] < ref.shape[0] // 2 else idx[0] - ref.shape[0]
    dx = idx[1] if idx[1] < ref.shape[1] // 2 else idx[1] - ref.shape[1]
    return int(dx), int(dy)


def diff_extract(state_a: Image.Image, state_b: Image.Image,
                 thresh: float = 14.0,
                 feather: int = 1,
                 min_area: int = 240,
                 align: bool = True,
                 restrict: Optional[Tuple[int, int, int, int]] = None,
                 ) -> Tuple[Image.Image, Tuple[int, int, int, int], dict]:
    """Extrai o que MUDOU de A para B como camada RGBA recortada ao bbox.

    state_a = placa/estado base; state_b = estado com o elemento.
    Retorna (layer_rgba_cropada, bbox_no_quadro, info).
    """
    A = state_a.convert("RGB")
    B = state_b.convert("RGB")
    if A.size != B.size:
        B = B.resize(A.size, Image.LANCZOS)
    a = np.asarray(A, dtype=np.float32)
    b = np.asarray(B, dtype=np.float32)
    info: dict = {}
    if align:
        ga = a.mean(axis=2)
        gb = b.mean(axis=2)
        dx, dy = _align_translation(ga, gb)
        info["align_shift"] = [dx, dy]
        if abs(dx) > 24 or abs(dy) > 24:
            dx = dy = 0  # desalinho grande demais: confia no enquadramento
        if dx or dy:
            b = np.roll(np.roll(b, dy, axis=0), dx, axis=1)
    delta = np.sqrt(((a - b) ** 2).sum(axis=2))
    mask = delta > thresh
    if restrict is not None:
        rx, ry, rw, rh = restrict
        keep = np.zeros_like(mask)
        keep[ry:ry + rh, rx:rx + rw] = True
        mask &= keep
    # limpeza morfológica simples (abre + fecha) via PIL
    m = Image.fromarray((mask * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MinFilter(3))   # abre: mata sal e pico
    m = m.filter(ImageFilter.MaxFilter(5))   # fecha: preenche o interior
    mask = np.asarray(m) > 127
    # componentes conexos: mantém só os grandes (evita ruído de compressão)
    mask = _keep_big_components(mask, min_area)
    if not mask.any():
        raise RuntimeError("diff_extract: nenhuma diferença significativa")
    ys, xs = np.where(mask)
    x0, x1 = xs.min(), xs.max() + 1
    y0, y1 = ys.min(), ys.max() + 1
    alpha = (mask * 255).astype(np.uint8)
    if feather:
        alpha_img = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(feather * 0.6))
        alpha = np.asarray(alpha_img)
        alpha = np.where(mask, np.maximum(alpha, 200), alpha)  # interior cheio
    layer = np.dstack([b.astype(np.uint8), alpha])[y0:y1, x0:x1]
    info.update(bbox=[int(x0), int(y0), int(x1 - x0), int(y1 - y0)],
                area=int(mask.sum()),
                edge_frac=round(float(((alpha > 12) & (alpha < 243)).mean()), 4))
    return Image.fromarray(layer, "RGBA"), (int(x0), int(y0), int(x1 - x0), int(y1 - y0)), info


def _keep_big_components(mask: np.ndarray, min_area: int) -> np.ndarray:
    """Flood-fill iterativo simples (4-vizinhança) para filtrar componentes."""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    cur = 0
    sizes: Dict[int, int] = {}
    idxs = np.argwhere(mask)
    for (y, x) in idxs:
        if lab[y, x]:
            continue
        cur += 1
        stack = [(y, x)]
        lab[y, x] = cur
        n = 0
        while stack:
            cy, cx = stack.pop()
            n += 1
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur
                    stack.append((ny, nx))
        sizes[cur] = n
    keep = np.isin(lab, [k for k, v in sizes.items() if v >= min_area])
    return keep


def _components(mask: np.ndarray):
    """Componentes conexos (4-vizinhança) com área e bbox, sem scipy."""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    comps = []
    cur = 0
    ys, xs = np.where(mask)
    for y, x in zip(ys, xs):
        if lab[y, x]:
            continue
        cur += 1
        stack = [(y, x)]
        lab[y, x] = cur
        pix = [(y, x)]
        while stack:
            cy, cx = stack.pop()
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur
                    stack.append((ny, nx))
                    pix.append((ny, nx))
        pys = [p[0] for p in pix]; pxs = [p[1] for p in pix]
        comps.append(dict(id=cur, area=len(pix),
                          bbox=(min(pxs), min(pys), max(pxs) - min(pxs) + 1,
                                max(pys) - min(pys) + 1)))
    return lab, comps


def refine_layer(img: Image.Image, min_area: int = 0, max_w: int = 10 ** 9,
                 max_h: int = 10 ** 9, drop_cyan: bool = False,
                 drop_flat: bool = False,
                 zero_rects: Optional[List[Tuple[int, int, int, int]]] = None,
                 ) -> Tuple[Image.Image, Tuple[int, int, int, int], dict]:
    """Refino de camada pós-diff (E2): remove contaminação de repaint.

    * drop_cyan: zera pixels de feixe ciano saturado (B−R>55, G−R>35) que o
      diff trouxe junto nas poses de quem flutua;
    * min_area / max_w: descarta fragmentos de repaint e faixas largas
      (telhados redesenhados) mantendo só os componentes do elemento;
    * zero_rects: retângulos (x,y,w,h) de alpha zerado (ex.: mão fantasma).
    Retorna (layer recortada, bbox no quadro, info).
    """
    arr = np.asarray(img.convert("RGBA")).copy()
    a = arr[..., 3] > 8
    if drop_cyan:
        # família de cor do feixe medida no piloto (G−R>55, B−R>70); roupas ficam fora
        r = arr[..., 0].astype(int); g = arr[..., 1].astype(int); b = arr[..., 2].astype(int)
        a &= ~((g - r > 55) & (b - r > 70) & (b > 110) & (g > 80))
        m = Image.fromarray((a * 255).astype(np.uint8))
        m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
        a = np.asarray(m) > 127
    if zero_rects:
        for (x, y, w, h) in zero_rects:
            a[y:y + h, x:x + w] = False
    lab, comps = _components(a)
    def _ok(c):
        w, h = c["bbox"][2], c["bbox"][3]
        if c["area"] < min_area or w > max_w or h > max_h:
            return False
        if drop_flat and w > 1.6 * h and h < 60:   # telhados/faixas redesenhadas
            return False
        return True
    keep_ids = [c["id"] for c in comps if _ok(c)]
    keep = np.isin(lab, keep_ids) if keep_ids else np.zeros_like(a)
    arr[..., 3] = np.where(keep, arr[..., 3], 0)
    if not keep.any():
        raise RuntimeError("refine_layer: camada vazia após refino")
    ys, xs = np.where(keep)
    x0, x1 = xs.min(), xs.max() + 1
    y0, y1 = ys.min(), ys.max() + 1
    info = dict(area=int(keep.sum()), comps_kept=len(keep_ids),
                comps_total=len(comps))
    return Image.fromarray(arr[y0:y1, x0:x1], "RGBA"), \
        (int(x0), int(y0), int(x1 - x0), int(y1 - y0)), info


def save_layer(img: Image.Image, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG", optimize=True)


def load_meta(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    print("rig.py ok — SQUASH_MAX", SQUASH_MAX)

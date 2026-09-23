#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/anim/fx.py — FX procedurais do vocabulário WAI (spec v4 §6).

Tudo é deterministic (seed no meta.json) e ADITIVO (RGBA sobre a cena), com
follow-through e dissipação (R8) e defasagem do evento primário.

Catálogo implementado:
  beam_glow      bloom ciano sobre o feixe pintado (pulso/overdrive)
  flicker        tremulação em degraus (blink token)
  sparkles       sparkles dourados subindo (atlas IA) com twinkle
  halo_twinkle   auréolas pulsando em posições fixas (atlas IA)
  scan_sweep     linha de varredura vertical (materializar / overdrive)
  light_sweep    faixa de luz diagonal varrendo a cidade (impacto)
  dust_puff      poeira de impacto expandindo e dissipando (atlas IA)
  smear          risco de movimento de 1 quadro (troca de pose)
  window_flick   janelas da cidade piscando quente (secundário)
  console_glow   brilho radial no console no aperto (impacto)
  lightbits      confete de luz aditivo (atlas IA)
"""
from __future__ import annotations
import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _rng(seed: int) -> random.Random:
    return random.Random(seed)


def flicker_value(t_ms: float, seed: int = 7, hz: float = 18.0,
                  depth: float = 0.25) -> float:
    """Tremulação em degraus (não senoidal) — 'blink' da referência."""
    r = _rng(seed)
    step = int(t_ms * hz / 1000.0)
    r.jumpahead(step * 7919) if hasattr(r, "jumpahead") else None
    # determinístico por step:
    h = (step * 2654435761 + seed * 40503) & 0xFFFFFFFF
    u = ((h >> 8) & 0xFFFF) / 65535.0
    return 1.0 - depth * u


def atlas_sprites(atlas: Image.Image, grid: Tuple[int, int]) -> List[Image.Image]:
    """Recorta um atlas IA em sprites (grid cols x rows)."""
    w, h = atlas.size
    cols, rows = grid
    cw, ch = w // cols, h // rows
    out = []
    for ry in range(rows):
        for cx in range(cols):
            out.append(atlas.crop((cx * cw, ry * ch, (cx + 1) * cw, (ry + 1) * ch)))
    return out


def _additive(canvas: Image.Image, overlay: Image.Image) -> None:
    """Soma aditiva (screen-ish) preservando alpha do overlay."""
    base = np.asarray(canvas.convert("RGBA"), dtype=np.float32)
    ov = np.asarray(overlay.convert("RGBA"), dtype=np.float32)
    a = (ov[..., 3:4] / 255.0)
    rgb = base[..., :3] + ov[..., :3] * a
    canvas.paste(Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
                 .convert("RGBA"), (0, 0))


def _soft_ellipse(size: Tuple[int, int], color: Tuple[int, int, int],
                  alpha: float, blur: float) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, size[0] - 1, size[1] - 1], fill=color + (int(255 * alpha),))
    return img.filter(ImageFilter.GaussianBlur(blur))


# --------------------------------------------------------------------------- #
# FX
# --------------------------------------------------------------------------- #
def beam_glow(canvas: Image.Image, t_ms: float, p: dict) -> None:
    """Bloom aditivo ao longo do eixo do feixe (params: apex[x,y], top[x,y],
    width0, width1, color, intensity)."""
    inten = p.get("intensity", 1.0) * flicker_value(t_ms, p.get("seed", 3), 16, 0.18)
    if inten <= 0.01:
        return
    W, H = canvas.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ax, ay = p["apex"]; tx, ty = p.get("top", [ax, 0])
    w0, w1 = p.get("width0", 60), p.get("width1", 220)
    col = tuple(p.get("color", [120, 230, 255]))
    steps = 14
    for i in range(steps):
        u = i / (steps - 1)
        x = ax + (tx - ax) * u
        y = ay + (ty - ay) * u
        w = (w0 + (w1 - w0) * u) * (0.9 + 0.2 * math.sin(u * 9 + t_ms / 220))
        blob = _soft_ellipse((int(w), int(w * 0.42)), col,
                             0.10 * inten * (1 - 0.45 * u), w * 0.22)
        ov.alpha_composite(blob, (int(x - w / 2), int(y - w * 0.21)))
    _additive(canvas, ov)


def sparkles(canvas: Image.Image, t_ms: float, p: dict, atlas: Image.Image) -> None:
    """Partículas douradas subindo com twinkle (R8: dissipam)."""
    t0, t1 = p["t0"], p["t1"]
    if not (t0 <= t_ms <= t1 + p.get("life", 900)):
        return
    sprites = atlas_sprites(atlas, tuple(p.get("grid", (4, 3))))
    r = _rng(p.get("seed", 11))
    x0, y0, x1, y1 = p["region"]
    n = p.get("n", 10)
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    for i in range(n):
        birth = t0 + r.uniform(0, (t1 - t0) * 0.8)
        life = r.uniform(500, p.get("life", 900))
        u = (t_ms - birth) / life
        if u < 0 or u > 1:
            continue
        sx = r.uniform(x0, x1)
        sy = r.uniform(y0, y1)
        rise = p.get("rise", 90)
        x = sx + math.sin(u * 6 + i) * p.get("sway", 10)
        y = sy - rise * u
        spr = sprites[i % len(sprites)]
        s = p.get("size", 44) * r.uniform(0.5, 1.1) * (1 - 0.35 * u)
        spr = spr.resize((max(4, int(s)), max(4, int(s))), Image.LANCZOS)
        tw = 0.55 + 0.45 * math.sin(u * 22 + i * 2.1)
        a = (1 - u) ** 1.4 * tw
        if a <= 0.02:
            continue
        r_, g_, b_, al = spr.split()
        al = al.point(lambda v: int(v * a))
        ov.alpha_composite(Image.merge("RGBA", (r_, g_, b_, al)),
                           (int(x - s / 2), int(y - s / 2)))
    _additive(canvas, ov)


def halo_twinkle(canvas: Image.Image, t_ms: float, p: dict, atlas: Image.Image) -> None:
    sprites = atlas_sprites(atlas, tuple(p.get("grid", (2, 2))))
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    for i, (x, y, s) in enumerate(p["positions"]):
        ph = t_ms / 1000.0 * p.get("hz", 2.2) + i * 1.7
        a = p.get("alpha", 0.8) * (0.72 + 0.28 * math.sin(ph * 2 * math.pi))
        spr = sprites[i % len(sprites)].resize((int(s), int(s * 0.5)), Image.LANCZOS)
        r_, g_, b_, al = spr.split()
        al = al.point(lambda v: int(v * a))
        ov.alpha_composite(Image.merge("RGBA", (r_, g_, b_, al)),
                           (int(x - s / 2), int(y - s * 0.25)))
    _additive(canvas, ov)


def scan_sweep(canvas: Image.Image, t_ms: float, p: dict) -> None:
    """Linha de varredura vertical (materialização / overdrive)."""
    t0, t1 = p["t0"], p["t1"]
    if not (t0 <= t_ms <= t1):
        return
    u = (t_ms - t0) / max(1, (t1 - t0))
    y = int(p["y0"] + (p["y1"] - p["y0"]) * u)
    W, H = canvas.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    col = tuple(p.get("color", [160, 240, 255]))
    band = p.get("band", 26)
    for k in range(band):
        a = int(90 * (1 - abs(k - band / 2) / (band / 2)) ** 2 * p.get("alpha", 1))
        d.line([(0, y - band // 2 + k), (W, y - band // 2 + k)], fill=col + (a,))
    _additive(canvas, ov.filter(ImageFilter.GaussianBlur(2)))


def light_sweep(canvas: Image.Image, t_ms: float, p: dict) -> None:
    t0, t1 = p["t0"], p["t1"]
    if not (t0 <= t_ms <= t1):
        return
    u = (t_ms - t0) / max(1, (t1 - t0))
    W, H = canvas.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    x = int(-0.3 * W + 1.6 * W * u)
    wdt = p.get("width", 150)
    for k in range(wdt):
        a = int(52 * (1 - abs(k - wdt / 2) / (wdt / 2)) ** 2)
        d.line([(x - wdt // 2 + k - int(0.25 * H), 0),
                (x - wdt // 2 + k + int(0.25 * H), H)],
               fill=tuple(p.get("color", [255, 244, 200])) + (a,))
    _additive(canvas, ov.filter(ImageFilter.GaussianBlur(3)))


def dust_puff(canvas: Image.Image, t_ms: float, p: dict, atlas: Image.Image) -> None:
    t0 = p["t0"]
    life = p.get("life", 700)
    u = (t_ms - t0) / life
    if u < 0 or u > 1:
        return
    sprites = atlas_sprites(atlas, tuple(p.get("grid", (3, 1))))
    r = _rng(p.get("seed", 21))
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    for i, (x, y) in enumerate(p["origins"]):
        du = min(1, max(0, u - i * 0.06))
        s = p.get("size", 90) * (0.45 + 0.9 * du)
        a = (1 - du) ** 1.6 * p.get("alpha", 0.85)
        if a <= 0.02:
            continue
        spr = sprites[i % len(sprites)].resize((int(s), int(s * 0.8)), Image.LANCZOS)
        r_, g_, b_, al = spr.split()
        al = al.point(lambda v: int(v * a))
        ov.alpha_composite(Image.merge("RGBA", (r_, g_, b_, al)),
                           (int(x - s / 2), int(y - s * 0.4 - 18 * du)))
    canvas.alpha_composite(ov)


def smear(canvas: Image.Image, t_ms: float, p: dict) -> None:
    """Risco de movimento de 1 quadro na troca de pose (R6/leitura)."""
    t0, t1 = p["t0"], p["t1"]
    if not (t0 <= t_ms <= t1):
        return
    x0, y0, x1, y1 = p["bbox"]
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    a = p.get("alpha", 90)
    d.rounded_rectangle([x0, y0, x1, y1], radius=(x1 - x0) // 2,
                        fill=tuple(p.get("color", [190, 240, 255])) + (a,))
    _additive(canvas, ov.filter(ImageFilter.GaussianBlur(p.get("blur", 9))))


def window_flick(canvas: Image.Image, t_ms: float, p: dict) -> None:
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i, (x, y, s) in enumerate(p["points"]):
        h = ((int(t_ms / 140) + i * 37) * 2654435761) & 0xFF
        if h > p.get("on_above", 150):
            continue
        d.ellipse([x - s, y - s, x + s, y + s], fill=tuple(p.get("color", [255, 214, 120])) + (150,))
    _additive(canvas, ov.filter(ImageFilter.GaussianBlur(1.4)))


def console_glow(canvas: Image.Image, t_ms: float, p: dict) -> None:
    t0 = p["t0"]
    u = (t_ms - t0) / p.get("life", 420)
    if u < 0 or u > 1:
        return
    a = (1 - u) ** 1.7
    x, y = p["at"]
    s = p.get("size", 220) * (0.7 + 0.6 * u)
    blob = _soft_ellipse((int(s), int(s * 0.7)), tuple(p.get("color", [255, 120, 90])),
                         0.5 * a, s * 0.2)
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ov.alpha_composite(blob, (int(x - s / 2), int(y - s * 0.35)))
    _additive(canvas, ov)


def lightbits(canvas: Image.Image, t_ms: float, p: dict, atlas: Image.Image) -> None:
    t0, t1 = p["t0"], p["t1"]
    if not (t0 <= t_ms <= t1 + 600):
        return
    sprites = atlas_sprites(atlas, tuple(p.get("grid", (5, 2))))
    r = _rng(p.get("seed", 31))
    ov = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = p["region"]
    for i in range(p.get("n", 12)):
        birth = t0 + r.uniform(0, (t1 - t0) * 0.7)
        life = r.uniform(400, 700)
        u = (t_ms - birth) / life
        if u < 0 or u > 1:
            continue
        x = r.uniform(x0, x1) + r.uniform(-30, 30) * u
        y = r.uniform(y0, y1) - r.uniform(40, 140) * u
        spr = sprites[i % len(sprites)]
        s = r.uniform(10, 26) * (1 - 0.4 * u)
        spr = spr.resize((max(3, int(s)), max(3, int(s))), Image.LANCZOS)
        a = (1 - u) ** 1.3
        r_, g_, b_, al = spr.split()
        al = al.point(lambda v: int(v * a))
        ov.alpha_composite(Image.merge("RGBA", (r_, g_, b_, al)), (int(x), int(y)))
    _additive(canvas, ov)


KINDS = {
    "beam_glow": beam_glow, "scan_sweep": scan_sweep, "light_sweep": light_sweep,
    "smear": smear, "window_flick": window_flick, "console_glow": console_glow,
}
ATLAS_KINDS = {"sparkles": sparkles, "halo_twinkle": halo_twinkle,
               "dust_puff": dust_puff, "lightbits": lightbits}

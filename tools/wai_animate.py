#!/usr/bin/env python3
"""wai_animate.py — anima o quadro pintado no ritmo do gênero (We Are Illuminati).

Gramática medida no trailer de referência (não é cópia de arte):

  * o fundo NÃO anda. Câmera travada. O que se mexe é o ator e o efeito.
  * o ciclo é seno inteiro: o quadro 0 e o retorno do loop são o mesmo passo,
    sem o "pulo" dos 4 frames com zoom.
  * 12 quadros × 110 ms ≈ 1,3 s (16 na história do Blue Beam). Dá para ler a piada.
  * verbo único por cena (balanço, giro, gota, onda, varredura, faísca).

O mestre é o poster.webp (pintura limpa, sem o zoom quebrado das recipes
antigas). Saída: loop.webp + ff_XX.webp + contact.png. O poster não muda.

Uso:
  python3 tools/wai_animate.py p1_09 p5_06
  python3 tools/wai_animate.py --all
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ANIM = ROOT / "src" / "assets" / "anim"

N = 12                 # quadros por ciclo (mínimo para ler um gesto)
MS = 110               # ~1,32 s de loop
W, H = 640, 360

# ---------------------------------------------------------------- primitives

def _plate(mission_id: str) -> Image.Image:
    d = ANIM / mission_id
    src = d / "poster.webp"
    if not src.exists():
        raise SystemExit(f"sem poster: {src}")
    im = Image.open(src).convert("RGB")
    # poster já é 640x360 na prática; força o tamanho do card
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return im


def _mask_ellipse(cx, cy, rx, ry, inner=0.72, outer=1.05):
    ys, xs = np.mgrid[0:H, 0:W]
    nx = (xs - cx) / max(rx, 1)
    ny = (ys - cy) / max(ry, 1)
    r = np.sqrt(nx * nx + ny * ny)
    m = np.clip((outer - r) / (outer - inner), 0, 1)
    return m * m * (3 - 2 * m)


def _sample(arr, sx, sy):
    hh, ww = arr.shape[0], arr.shape[1]
    x0 = np.floor(sx).astype(np.int32)
    y0 = np.floor(sy).astype(np.int32)
    wx = (sx - x0)[..., None]
    wy = (sy - y0)[..., None]
    x1 = x0 + 1
    y1 = y0 + 1
    x0 = np.clip(x0, 0, ww - 1)
    x1 = np.clip(x1, 0, ww - 1)
    y0 = np.clip(y0, 0, hh - 1)
    y1 = np.clip(y1, 0, hh - 1)
    Ia = arr[y0, x0]
    Ib = arr[y0, x1]
    Ic = arr[y1, x0]
    Id = arr[y1, x1]
    return (Ia * (1 - wx) * (1 - wy) + Ib * wx * (1 - wy)
            + Ic * (1 - wx) * wy + Id * wx * wy)


def _warp(arr, sx, sy, mask):
    """Amostra (sx,sy) só onde a máscara manda; o resto fica parado."""
    sampled = _sample(arr, sx, sy)
    m = mask[..., None]
    return arr * (1 - m) + sampled * m


def op_bob(arr, t, cx, cy, rx, ry, amp):
    """Sobe e desce um pedaço (ator) sem mexer o resto da cena."""
    cx, cy, rx, ry = cx * W, cy * H, rx * W, ry * H
    mask = _mask_ellipse(cx, cy, rx, ry)
    dy = amp * np.sin(2 * np.pi * t)
    ys, xs = np.mgrid[0:H, 0:W]
    # inverso: o pixel de saída veio de y - dy*mask (o ator subiu, amostra abaixo)
    sy = ys - dy * mask
    return _warp(arr, xs.astype(np.float32), sy.astype(np.float32), mask)


def op_swing(arr, t, px, py, radius, deg):
    """Balança um membro em volta de um pivô. Ângulo volta a zero no loop."""
    px, py = px * W, py * H
    ang = np.deg2rad(deg) * np.sin(2 * np.pi * t)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = xs - px
    dy = ys - py
    dist = np.sqrt(dx * dx + dy * dy)
    fall = np.clip((radius - dist) / (radius * 0.38), 0, 1)
    fall = fall * fall * (3 - 2 * fall)
    a = -ang * fall
    ca = np.cos(a)
    sa = np.sin(a)
    sx = px + ca * dx - sa * dy
    sy = py + sa * dx + ca * dy
    return _warp(arr, sx, sy, fall)


def op_spin(arr, t, cx, cy, radius, turns=1):
    """Gira um disco redondo N voltas inteiras — rígido por dentro, pena na borda."""
    cx, cy = cx * W, cy * H
    ang = -2 * np.pi * turns * t
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = xs - cx
    dy = ys - cy
    dist = np.sqrt(dx * dx + dy * dy)
    ca = np.cos(ang)
    sa = np.sin(ang)
    sx = cx + ca * dx - sa * dy
    sy = cy + sa * dx + ca * dy
    # 1 no miolo, 0 fora — a borda de 6px esconde o corte
    fall = np.clip((radius - dist) / 6.0, 0, 1)
    return _warp(arr, sx, sy, fall)


def op_pulse(arr, t, x0, y0, x1, y1, amp=0.28, phase=0.0, thresh=168):
    """Luzes, telas e olhos já pintados piscam — sem desenhar por cima."""
    xa, ya = int(x0 * W), int(y0 * H)
    xb, yb = int(x1 * W), int(y1 * H)
    xa, ya = max(0, xa), max(0, ya)
    xb, yb = min(W, xb), min(H, yb)
    if xb <= xa or yb <= ya:
        return arr
    sl = arr[ya:yb, xa:xb]
    bright = sl.max(axis=2) >= thresh
    if not bright.any():
        return arr
    factor = 1.0 + amp * np.sin(2 * np.pi * (t + phase))
    out = arr.copy()
    block = sl.copy()
    block[bright] = np.clip(sl[bright] * factor, 0, 255)
    out[ya:yb, xa:xb] = block
    return out


def op_wave(arr, t, x0, y0, x1, y1, amp=0.62, thresh=120):
    """Onda de apagão: as luzes apagam da esquerda para a direita e voltam."""
    xa, ya = int(x0 * W), int(y0 * H)
    xb, yb = int(x1 * W), int(y1 * H)
    sl = arr[ya:yb, xa:xb]
    bright = sl.max(axis=2) >= thresh
    if not bright.any():
        return arr
    xs = np.linspace(0, 1, xb - xa, dtype=np.float32)[None, :]
    # desce até 12% — lê como apagão, não como um flicker tímido
    factor = 0.12 + 0.88 * (0.5 + 0.5 * np.sin(2 * np.pi * (t - xs)))
    factor = np.broadcast_to(factor, sl.shape[:2])
    out = arr.copy()
    block = sl.copy()
    block[bright] = np.clip(sl[bright] * factor[bright][..., None], 0, 255)
    out[ya:yb, xa:xb] = block
    return out


# ---------------------------------------------------------------- desenho FX
# Partículas com contorno grosso, no mesmo flat-toon. Nascem e morrem
# dentro do ciclo (fade nas pontas) para o loop não pular.

def _fade_loop(u, edge=0.14):
    u = u % 1.0
    return float(min(1.0, u / edge, (1.0 - u) / edge))


def _sprite_layer(base: Image.Image, draw_fn) -> Image.Image:
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(ov))
    return Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB")


def _coin(d, x, y, r, alpha):
    a = int(220 * alpha)
    if a < 8:
        return
    d.ellipse([x - r, y - r, x + r, y + r], fill=(232, 176, 42, a),
              outline=(30, 22, 10, a), width=2)
    d.ellipse([x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55],
              outline=(255, 226, 140, a), width=2)
    d.ellipse([x - r * 0.28, y - r * 0.42, x - r * 0.05, y - r * 0.16],
              fill=(255, 245, 200, int(a * 0.8)))


def _drop(d, x, y, r, color, alpha):
    a = int(230 * alpha)
    if a < 8:
        return
    c = (*color, a)
    d.polygon([(x, y - r), (x - r * 0.46, y), (x + r * 0.46, y)], fill=c)
    d.ellipse([x - r * 0.5, y - r * 0.2, x + r * 0.5, y + r * 0.72],
              fill=c, outline=(12, 20, 24, a), width=2)
    d.ellipse([x - r * 0.22, y + r * 0.05, x - r * 0.02, y + r * 0.28],
              fill=(255, 255, 255, int(a * 0.75)))


def _spark(d, x, y, r, color, alpha):
    a = int(230 * alpha)
    if a < 8:
        return
    c = (*color, a)
    ink = (20, 16, 10, a)
    d.polygon([(x, y - r), (x + 2, y - 2), (x + r, y), (x + 2, y + 2),
               (x, y + r), (x - 2, y + 2), (x - r, y), (x - 2, y - 2)],
              fill=c, outline=ink)


def _note(d, x, y, s, color, alpha):
    a = int(220 * alpha)
    if a < 8:
        return
    c = (*color, a)
    d.ellipse([x - s * 0.45, y, x + s * 0.15, y + s * 0.55], fill=c)
    d.line([(x + s * 0.1, y + s * 0.2), (x + s * 0.1, y - s * 0.7)],
           fill=c, width=max(2, int(s * 0.16)))
    d.line([(x + s * 0.1, y - s * 0.7), (x + s * 0.55, y - s * 0.45)],
           fill=c, width=max(2, int(s * 0.16)))


def _flyer(d, x, y, alpha, tilt):
    """Panfleto de cartum: papel, rabisco e uma tarja — não um retângulo branco."""
    a = int(220 * alpha)
    if a < 8:
        return
    w, h = 11, 15
    t = tilt * 0.6
    pts = [(x - w, y - h + t), (x + w, y - h - t),
           (x + w - 1, y + h - t * 0.3), (x - w + 1, y + h + t * 0.3)]
    ink = (28, 20, 14, a)
    d.polygon(pts, fill=(244, 232, 196, a), outline=ink)
    d.line([(x - w + 3, y - 4), (x + w - 4, y - 5)], fill=(70, 55, 40, a), width=1)
    d.line([(x - w + 3, y), (x + w - 5, y - 1)], fill=(70, 55, 40, a), width=1)
    d.line([(x - w + 3, y + 4), (x + 1, y + 3)], fill=(70, 55, 40, a), width=1)
    d.polygon([(x - w, y - h + t), (x - 2, y - h + t * 0.4),
               (x - 2, y - h + 6), (x - w, y - h + 6 + t)],
              fill=(196, 48, 42, a))


def op_travel(base, t, kind, p0, p1, n, color, size=7):
    """n partículas viajando de p0 a p1, defasadas, sumindo nas pontas."""
    x0, y0 = p0[0] * W, p0[1] * H
    x1, y1 = p1[0] * W, p1[1] * H

    def draw(d):
        for i in range(n):
            u = (t + i / n) % 1.0
            fade = _fade_loop(u)
            x = x0 + (x1 - x0) * u
            y = y0 + (y1 - y0) * u
            # um leve arco para não parecer um trilho
            y += np.sin(u * np.pi) * 10 * (1 if i % 2 == 0 else -1)
            if kind == "coin":
                _coin(d, x, y, size, fade)
            elif kind == "drop":
                _drop(d, x, y, size, color, fade)
            elif kind == "spark":
                _spark(d, x, y, size, color, fade)
            elif kind == "note":
                _note(d, x, y, size * 1.6, color, fade)
            elif kind == "flyer":
                _flyer(d, x, y, fade, int(8 * np.sin(u * 6)))
            else:
                _spark(d, x, y, size, color, fade)
    return _sprite_layer(base, draw)


def op_arcs(base, t, cx, cy, color, r0, r1):
    """Anéis de sinal: um nasce, cresce e some; o outro está no meio do ciclo."""
    cx, cy = cx * W, cy * H

    def draw(d):
        for phase in (0.0, 0.5):
            u = (t + phase) % 1.0
            fade = _fade_loop(u, 0.18)
            r = r0 + (r1 - r0) * u
            a = int(180 * fade)
            if a < 8:
                continue
            d.arc([cx - r, cy - r * 0.72, cx + r, cy + r * 0.72],
                  200, 340, fill=(*color, a), width=4)
    return _sprite_layer(base, draw)


def op_scan(base, t, x0, y0, x1, y1, color):
    """Faixa de varredura que atravessa um retângulo e some nas bordas."""
    xa, ya = int(x0 * W), int(y0 * H)
    xb, yb = int(x1 * W), int(y1 * H)

    def draw(d):
        for phase in (0.0, 0.5):
            u = (t + phase) % 1.0
            fade = _fade_loop(u, 0.16)
            x = xa + (xb - xa) * u
            a = int(90 * fade)
            if a < 6:
                continue
            d.rectangle([x - 3, ya, x + 3, yb], fill=(*color, a))
    return _sprite_layer(base, draw)


def op_sparks_burst(base, t, cx, cy, color, n=7, spread=26):
    """Faíscas em volta de um ponto, cada uma num raio que pulsa."""
    cx, cy = cx * W, cy * H

    def draw(d):
        for i in range(n):
            ang = (i / n) * 2 * np.pi + 0.4
            u = (t + i / n) % 1.0
            fade = np.sin(np.pi * u)  # nasce e morre, sem pulo
            r = 6 + spread * u
            x = cx + np.cos(ang) * r
            y = cy + np.sin(ang) * r * 0.8
            _spark(d, x, y, 5 + 3 * (1 - u), color, fade)
    return _sprite_layer(base, draw)


def op_steam(base, t, cx, cy, n=3):
    cx, cy = cx * W, cy * H

    def draw(d):
        for i in range(n):
            u = (t + i / n) % 1.0
            fade = _fade_loop(u, 0.2) * 0.7
            x = cx + np.sin(u * 6 + i) * 6
            y = cy - u * 36
            a = int(160 * fade)
            if a < 8:
                continue
            r = 4 + u * 7
            d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7],
                      outline=(230, 240, 245, a), width=2)
    return _sprite_layer(base, draw)


def op_scroll(arr, t, x0, y0, x1, y1, period_px, axis="x"):
    """Esteira: o retângulo anda um número inteiro de períodos e volta."""
    xa, ya = int(x0 * W), int(y0 * H)
    xb, yb = int(x1 * W), int(y1 * H)
    xa, ya = max(0, xa), max(0, ya)
    xb, yb = min(W, xb), min(H, yb)
    if xb - xa < 8 or yb - ya < 8:
        return arr
    sl = arr[ya:yb, xa:xb]
    out = arr.copy()
    if axis == "x":
        shift = (t * period_px) % sl.shape[1]
        xs = (np.arange(sl.shape[1], dtype=np.float32) - shift) % sl.shape[1]
        ys = np.arange(sl.shape[0], dtype=np.float32)
        gx, gy = np.meshgrid(xs, ys)
        sl2 = _sample(sl, gx, gy)
    else:
        shift = (t * period_px) % sl.shape[0]
        xs = np.arange(sl.shape[1], dtype=np.float32)
        ys = (np.arange(sl.shape[0], dtype=np.float32) - shift) % sl.shape[0]
        gx, gy = np.meshgrid(xs, ys)
        sl2 = _sample(sl, gx, gy)
    out[ya:yb, xa:xb] = sl2
    return out


def op_bubbles(base, t, cx, cy, rw, rh, n=6, color=(180, 255, 255)):
    cx, cy, rw, rh = cx * W, cy * H, rw * W, rh * H

    def draw(d):
        for i in range(n):
            u = (t + i / n) % 1.0
            fade = _fade_loop(u, 0.18)
            x = cx + math.sin(i * 2.4 + u * 4) * rw * 0.7
            y = cy + rh * 0.5 - u * rh
            a = int(200 * fade)
            if a < 8:
                continue
            r = 2.2 + (i % 3)
            d.ellipse([x - r, y - r, x + r, y + r],
                      outline=(*color, a), width=2)
    return _sprite_layer(base, draw)


def op_stream(base, t, x0, y0, x1, y1, color, width=6):
    """Jato de água/xarope que treme e pinga."""
    x0, y0, x1, y1 = x0 * W, y0 * H, x1 * W, y1 * H

    def draw(d):
        a = 210
        wob = math.sin(t * 2 * math.pi * 3) * 2.2
        pts = [(x0 - width / 2 + wob, y0), (x0 + width / 2 + wob, y0),
               (x1 + width / 2 - wob * 0.4, y1), (x1 - width / 2 - wob * 0.4, y1)]
        d.polygon(pts, fill=(*color, a))
        # splash
        for k in range(4):
            u = (t * 2 + k / 4) % 1.0
            fade = _fade_loop(u, 0.25)
            sx = x1 + math.cos(k * 1.7 + t * 8) * (4 + 10 * u)
            sy = y1 + 3 + u * 8
            _drop(d, sx, sy, 3.5, color, fade)
    return _sprite_layer(base, draw)


def op_orbit(base, t, cx, cy, radius, n, color, size=7):
    cx, cy, radius = cx * W, cy * H, radius * min(W, H)

    def draw(d):
        for i in range(n):
            ang = 2 * math.pi * (t + i / n)
            x = cx + math.cos(ang) * radius
            y = cy + math.sin(ang) * radius * 0.72
            _spark(d, x, y, size, color, 0.9)
    return _sprite_layer(base, draw)


def op_halo(base, t, cx, cy, r, color=(255, 214, 70)):
    cx, cy, r = cx * W, cy * H, r * min(W, H)
    pulse = 0.75 + 0.25 * math.sin(2 * math.pi * t)

    def draw(d):
        a = int(200 * pulse)
        rr = r * pulse
        d.ellipse([cx - rr, cy - rr * 0.45, cx + rr, cy + rr * 0.45],
                  outline=(*color, a), width=3)
    return _sprite_layer(base, draw)


def op_warm(arr, t, x0, y0, x1, y1, amp=0.22):
    """Velas/lamparinas: pixels quentes piscam em fases diferentes."""
    xa, ya = int(x0 * W), int(y0 * H)
    xb, yb = int(x1 * W), int(y1 * H)
    xa, ya = max(0, xa), max(0, ya)
    xb, yb = min(W, xb), min(H, yb)
    if xb <= xa or yb <= ya:
        return arr
    sl = arr[ya:yb, xa:xb]
    r, g, b = sl[:, :, 0], sl[:, :, 1], sl[:, :, 2]
    warm = (r > 170) & (g > 80) & (b < 140) & (r > b + 40)
    if not warm.any():
        return arr
    # fase espacial para não piscar tudo junto
    ys, xs = np.mgrid[0:sl.shape[0], 0:sl.shape[1]]
    phase = (xs * 0.17 + ys * 0.13) % 1.0
    factor = 1.0 + amp * np.sin(2 * np.pi * (t * 2 + phase))
    out = arr.copy()
    block = sl.copy()
    f = factor[warm][..., None]
    block[warm] = np.clip(sl[warm] * f, 0, 255)
    out[ya:yb, xa:xb] = block
    return out


def op_fill(base, t, x0, y0, x1, y1, color, level):
    """Nível de líquido (0..1) dentro de um retângulo — xarope no vidro."""
    xa, ya = int(x0 * W), int(y0 * H)
    xb, yb = int(x1 * W), int(y1 * H)
    fill_y = int(yb - (yb - ya) * max(0.0, min(1.0, level)))

    def draw(d):
        a = 200
        if fill_y >= yb:
            return
        d.rectangle([xa, fill_y, xb, yb], fill=(*color, a))
        # menisco
        d.ellipse([xa, fill_y - 3, xb, fill_y + 4], fill=(*color, a))
    return _sprite_layer(base, draw)


# ---------------------------------------------------------------- aplicar

def apply_op(im: Image.Image, op, t) -> Image.Image:
    kind = op[0]
    arr = None
    if kind in ("bob", "swing", "spin", "pulse", "wave", "scroll", "warm"):
        arr = np.asarray(im).astype(np.float32)

    if kind == "bob":
        _, cx, cy, rx, ry, amp = op
        arr = op_bob(arr, t, cx, cy, rx, ry, amp)
    elif kind == "swing":
        _, px, py, radius, deg = op
        arr = op_swing(arr, t, px, py, radius, deg)
    elif kind == "spin":
        _, cx, cy, radius, turns = op
        arr = op_spin(arr, t, cx, cy, radius, turns)
    elif kind == "pulse":
        _, x0, y0, x1, y1, amp = op
        arr = op_pulse(arr, t, x0, y0, x1, y1, amp)
    elif kind == "wave":
        _, x0, y0, x1, y1 = op
        arr = op_wave(arr, t, x0, y0, x1, y1)
    elif kind == "scroll":
        _, x0, y0, x1, y1, period, axis = op
        arr = op_scroll(arr, t, x0, y0, x1, y1, period, axis)
    elif kind == "warm":
        _, x0, y0, x1, y1, amp = op
        arr = op_warm(arr, t, x0, y0, x1, y1, amp)
    elif kind == "travel":
        _, pkind, p0, p1, n, color, size = op
        return op_travel(im, t, pkind, p0, p1, n, color, size)
    elif kind == "arcs":
        _, cx, cy, color, r0, r1 = op
        return op_arcs(im, t, cx, cy, color, r0, r1)
    elif kind == "scan":
        _, x0, y0, x1, y1, color = op
        return op_scan(im, t, x0, y0, x1, y1, color)
    elif kind == "sparks":
        _, cx, cy, color, n, spread = op
        return op_sparks_burst(im, t, cx, cy, color, n, spread)
    elif kind == "steam":
        _, cx, cy, n = op
        return op_steam(im, t, cx, cy, n)
    elif kind == "bubbles":
        _, cx, cy, rw, rh, n = op
        return op_bubbles(im, t, cx, cy, rw, rh, n)
    elif kind == "stream":
        _, x0, y0, x1, y1, color, width = op
        return op_stream(im, t, x0, y0, x1, y1, color, width)
    elif kind == "orbit":
        _, cx, cy, radius, n, color, size = op
        return op_orbit(im, t, cx, cy, radius, n, color, size)
    elif kind == "halo":
        _, cx, cy, r = op
        return op_halo(im, t, cx, cy, r)
    elif kind == "fill":
        _, x0, y0, x1, y1, color, level = op
        return op_fill(im, t, x0, y0, x1, y1, color, level)
    else:
        raise SystemExit(f"op desconhecida: {kind}")

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def render(mission_id: str, ops) -> list[Image.Image]:
    if mission_id in STORIES:
        return STORIES[mission_id]()
    plate = _plate(mission_id)
    frames = []
    for i in range(N):
        t = i / N
        im = plate
        for op in ops:
            im = apply_op(im, op, t)
        frames.append(im)
    return frames


def save(mission_id: str, frames: list[Image.Image]) -> None:
    d = ANIM / mission_id
    fdir = d / "frames"
    fdir.mkdir(parents=True, exist_ok=True)
    # limpa quadros velhos (4 frames com zoom) para não misturar
    for old in fdir.glob("ff_*.webp"):
        old.unlink()
    for i, im in enumerate(frames):
        im.save(fdir / f"ff_{i:02d}.webp", "WEBP", quality=76, method=4)

    loop = d / "loop.webp"
    frames[0].save(
        loop, "WEBP", save_all=True, append_images=frames[1:],
        duration=[MS] * len(frames), loop=0, quality=74, method=4,
    )
    # poster continua o mestre limpo (estado "não comprado")
    # folha de contato: 5 colunas, quadro 0 / meio / fim visíveis
    cols = 6
    tw, th = 256, 144
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (14, 18, 16))
    for i, im in enumerate(frames):
        sheet.paste(im.resize((tw, th), Image.LANCZOS),
                    ((i % cols) * tw, (i // cols) * th))
    sheet.save(d / "contact.png")
    kb = loop.stat().st_size // 1024
    print(f"  {mission_id}: {len(frames)}q × {MS}ms → loop {kb} KB")


# ---------------------------------------------------------------- performances
# Coordenadas normalizadas medidas no poster 640×360 (fundo travado).
# Cada cena tem UM verbo forte + um secundário. Nada de zoom de câmera.

C = {
    "gold": (255, 206, 70),
    "cyan": (90, 220, 255),
    "green": (70, 255, 150),
    "red": (255, 70, 60),
    "pink": (255, 120, 210),
    "orange": (255, 160, 50),
    "white": (255, 245, 220),
    "purple": (190, 120, 255),
    "syrup": (232, 168, 36),
    "water": (90, 210, 230),
}

# ---------------------------------------------------------------- histórias
# Cenas cujo loop NÃO é um seno em cima da pintura: tem começo, gag e volta.


def _ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def _gate(t, t0, t1, fade=0.12):
    if t1 <= t0:
        return 0.0
    if t < t0 or t > t1:
        return 0.0
    u = (t - t0) / (t1 - t0)
    return min(1.0, u / fade, (1.0 - u) / fade)


def _press_amt(t):
    """0 = dedo no ar, 1 = botão fundo. Segura enquanto o feixe está ligado."""
    if t < 0.10:
        return 0.0
    if t < 0.20:
        return _ease((t - 0.10) / 0.10)
    if t < 0.78:
        return 1.0
    if t < 0.90:
        return 1.0 - _ease((t - 0.78) / 0.12)
    return 0.0


def _beam_amt(t):
    if t < 0.18:
        return 0.0
    if t < 0.30:
        return _ease((t - 0.18) / 0.12)
    if t < 0.72:
        return 1.0
    if t < 0.88:
        return 1.0 - _ease((t - 0.72) / 0.16)
    return 0.0


def _draw_beam(d, x_top, x_bot, y0, y1, half_top, half_bot, alpha):
    if alpha < 0.04:
        return
    a = int(150 * alpha)
    core = int(210 * alpha)
    pts = [
        (x_top - half_top, y0), (x_top + half_top, y0),
        (x_bot + half_bot, y1), (x_bot - half_bot, y1),
    ]
    d.polygon(pts, fill=(120, 230, 255, a))
    # miolo mais claro
    cpts = [
        (x_top - half_top * 0.35, y0), (x_top + half_top * 0.35, y0),
        (x_bot + half_bot * 0.35, y1), (x_bot - half_bot * 0.35, y1),
    ]
    d.polygon(cpts, fill=(220, 250, 255, core))


def _draw_person(d, x, y, kind, scale, alpha, halo=False):
    """Civil de cartum (4 silhuetas) — sobe no feixe e some."""
    if alpha < 0.05:
        return
    a = int(255 * alpha)
    s = scale
    skin = (242, 196, 150, a)
    ink = (28, 22, 18, a)
    if kind == "woman":
        hair, shirt, pants = (90, 50, 40, a), (176, 70, 130, a), (90, 50, 110, a)
    elif kind == "man":
        hair, shirt, pants = (70, 90, 140, a), (70, 140, 190, a), (50, 70, 110, a)
    elif kind == "grandpa":
        hair, shirt, pants = (220, 220, 210, a), (90, 130, 90, a), (70, 70, 60, a)
    else:
        hair, shirt, pants = (60, 40, 30, a), (240, 190, 60, a), (50, 90, 160, a)

    d.rectangle([x - 5 * s, y + 6 * s, x - 1 * s, y + 16 * s], fill=pants, outline=ink)
    d.rectangle([x + 1 * s, y + 6 * s, x + 5 * s, y + 16 * s], fill=pants, outline=ink)
    d.rectangle([x - 7 * s, y - 4 * s, x + 7 * s, y + 8 * s], fill=shirt, outline=ink)
    d.ellipse([x - 6.5 * s, y - 17 * s, x + 6.5 * s, y - 3 * s], fill=skin, outline=ink, width=2)
    d.pieslice([x - 6.5 * s, y - 19 * s, x + 6.5 * s, y - 7 * s], 200, 340, fill=hair)
    d.ellipse([x - 3 * s, y - 12 * s, x - 1 * s, y - 9.5 * s], fill=ink)
    d.ellipse([x + 1 * s, y - 12 * s, x + 3 * s, y - 9.5 * s], fill=ink)
    if halo:
        d.ellipse([x - 9 * s, y - 24 * s, x + 9 * s, y - 18 * s],
                  outline=(255, 220, 70, a), width=2)


def render_p4_10() -> list[Image.Image]:
    """Arrebatamento holográfico: luz apagada → aperta o botão → feixe → sobem → some."""
    src = ANIM / "p4_10" / "plate_off.webp"
    if not src.exists():
        plate = _plate("p4_10")
    else:
        plate = Image.open(src).convert("RGB")
        if plate.size != (W, H):
            plate = plate.resize((W, H), Image.LANCZOS)

    n = 16
    people = [
        # kind, x_ground, y_ground, x_sky, y_sky
        ("woman", 0.56, 0.74, 0.54, 0.22),
        ("man", 0.63, 0.72, 0.61, 0.16),
        ("grandpa", 0.70, 0.74, 0.68, 0.24),
        ("boy", 0.76, 0.76, 0.74, 0.30),
    ]
    frames = []
    for i in range(n):
        t = i / n
        im = plate
        press = _press_amt(t)
        beam = _beam_amt(t)

        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)

        # feixes (dois cones)
        _draw_beam(d, 0.52 * W, 0.58 * W, 0, 0.80 * H, 10, 42, beam)
        _draw_beam(d, 0.66 * W, 0.72 * W, 0, 0.78 * H, 9, 38, beam)

        # botão acende quando apertado (sem distorcer o dedo)
        if press > 0.25:
            bx, by = 0.405 * W, 0.785 * H
            a = int(140 * press)
            d.ellipse([bx - 22, by - 10, bx + 22, by + 10],
                      outline=(255, 90, 70, a), width=3)
            d.ellipse([bx - 8, by - 4, bx + 8, by + 4],
                      fill=(255, 200, 180, int(90 * press)))

        # pessoas: no chão até o feixe ligar, depois sobem e somem
        rise_t0, rise_t1 = 0.28, 0.78
        for k, (kind, xg, yg, xs, ys) in enumerate(people):
            delay = k * 0.03
            if t < rise_t0 + delay:
                u, fade = 0.0, 1.0
            else:
                u = _ease((t - rise_t0 - delay) / (rise_t1 - rise_t0))
                fade = 1.0 if u < 0.72 else max(0.0, 1.0 - (u - 0.72) / 0.28)
            x = (xg + (xs - xg) * u) * W
            y = (yg + (ys - yg) * u) * H
            sc = 1.15 - 0.20 * u
            _draw_person(d, x, y, kind, sc, fade, halo=(u > 0.12 and fade > 0.15))

        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        if beam > 0.2:
            arr = np.asarray(im).astype(np.float32)
            arr = op_pulse(arr, t, 0.02, 0.45, 0.18, 0.85, 0.25 * beam)
            im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
        frames.append(im)
    return frames


def render_p4_08() -> list[Image.Image]:
    """Água da torneira: esteira anda, torneira enche, rótulo/auréola, inspetor anota."""
    plate = _plate("p4_08")
    n = 12
    frames = []
    for i in range(n):
        t = i / n
        im = plate
        arr = np.asarray(im).astype(np.float32)
        # só a fileira de garrafas (não o inspetor, não a mesa)
        arr = op_scroll(arr, t, 0.015, 0.525, 0.375, 0.655, 58, "x")
        arr = op_scroll(arr, t, 0.545, 0.505, 0.78, 0.640, 58, "x")
        arr = op_pulse(arr, t, 0.12, 0.08, 0.36, 0.42, 0.16)
        arr = op_pulse(arr, t, 0.62, 0.18, 0.98, 0.42, 0.14)
        # inspetor: vai e volta entre as garrafas e a prancheta (amplitude curta)
        arr = op_bob(arr, t, 0.88, 0.52, 0.06, 0.08, 3)
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

        im = op_bubbles(im, t, 0.22, 0.28, 0.05, 0.16, 5)
        im = op_bubbles(im, t, 0.30, 0.26, 0.04, 0.14, 4)
        im = op_bubbles(im, t, 0.72, 0.32, 0.06, 0.10, 4)
        im = op_bubbles(im, t, 0.92, 0.28, 0.05, 0.12, 4)
        im = op_steam(im, t, 0.22, 0.10, 3)
        im = op_steam(im, t, 0.70, 0.16, 3)
        im = op_stream(im, t, 0.545, 0.32, 0.545, 0.54, C["water"], 7)
        im = op_travel(im, t, "drop", (0.18, 0.48), (0.18, 0.72), 3, C["water"], 4)
        im = op_travel(im, t, "drop", (0.50, 0.62), (0.52, 0.78), 2, C["water"], 4)
        for hx in (0.60, 0.66, 0.72, 0.78):
            im = op_halo(im, t + hx, hx, 0.48, 0.028)
        # caneta na prancheta: risquinho que aparece quando ele "anota"
        if 0.48 < t < 0.92:
            def _pen(d, tt=t):
                a = int(200 * _gate(tt, 0.48, 0.92, 0.15))
                x0, y0 = 0.84 * W, 0.60 * H
                x1 = x0 + 14 * ((tt - 0.48) / 0.44)
                d.line([(x0, y0), (x1, y0 + 2)], fill=(40, 30, 20, a), width=2)
            im = _sprite_layer(im, _pen)
        frames.append(im)
    return frames


def render_p4_06() -> list[Image.Image]:
    """Quadro chora xarope, o copo enche, o espertinho recolhe, velas tremulam."""
    plate = _plate("p4_06")
    n = 12
    frames = []
    for i in range(n):
        t = i / n
        fill_u = 0.20 + 0.70 * t
        if t > 0.82:
            fill_u = 0.90 - 0.55 * _ease((t - 0.82) / 0.18)

        arr = np.asarray(plate).astype(np.float32)
        arr = op_warm(arr, t, 0.00, 0.00, 0.22, 0.55, 0.32)
        arr = op_warm(arr, t, 0.18, 0.00, 0.72, 0.12, 0.28)
        arr = op_warm(arr, t, 0.58, 0.00, 0.88, 0.30, 0.30)
        arr = op_warm(arr, t, 0.58, 0.38, 0.78, 0.58, 0.26)
        arr = op_pulse(arr, t, 0.38, 0.16, 0.56, 0.50, 0.16)
        arr = op_bob(arr, t, 0.30, 0.58, 0.08, 0.14, 2)
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

        im = op_travel(im, t, "drop", (0.44, 0.28), (0.40, 0.62), 4, C["syrup"], 6)
        im = op_travel(im, t, "drop", (0.50, 0.30), (0.42, 0.62), 4, (255, 190, 50), 5)
        im = op_travel(im, t, "drop", (0.46, 0.48), (0.46, 0.68), 2, C["syrup"], 5)
        im = op_fill(im, t, 0.398, 0.608, 0.422, 0.655, C["syrup"], fill_u)
        frames.append(im)
    return frames


STORIES = {
    "p4_10": render_p4_10,
    "p4_08": render_p4_08,
    "p4_06": render_p4_06,
}

P = {}

# --- mapa 1 Deep Web ---
P["p1_01"] = [  # mão no notebook: tela pulsa, moedas sobem
    ("pulse", 0.02, 0.28, 0.42, 0.78, 0.35),
    ("bob", 0.28, 0.48, 0.16, 0.28, 5),
    ("travel", "coin", (0.22, 0.55), (0.55, 0.18), 4, C["gold"], 7),
]
P["p1_02"] = [  # manchete se reescreve: varredura no jornal
    ("scan", 0.28, 0.12, 0.62, 0.62, C["white"]),
    ("bob", 0.42, 0.38, 0.16, 0.22, 4),
    ("travel", "flyer", (0.62, 0.30), (0.92, 0.08), 3, C["white"], 8),
]
P["p1_03"] = [  # lagarto toma café: balança, vapor
    ("bob", 0.62, 0.48, 0.14, 0.26, 6),
    ("steam", 0.48, 0.55, 3),
    ("pulse", 0.55, 0.28, 0.72, 0.46, 0.22),
]
P["p1_04"] = [  # pasta passando de mão: balanço da pasta
    ("swing", 0.48, 0.42, 90, 8),
    ("bob", 0.32, 0.48, 0.12, 0.24, 4),
    ("sparks", 0.55, 0.48, C["gold"], 5, 18),
]
P["p1_05"] = [  # quadro de barbante: alfinetes piscam
    ("pulse", 0.15, 0.12, 0.85, 0.78, 0.30),
    ("sparks", 0.40, 0.40, C["red"], 6, 22),
    ("travel", "spark", (0.20, 0.30), (0.75, 0.55), 4, C["gold"], 5),
]
P["p1_06"] = [  # diva: notas sobem, espiral pulsa
    ("pulse", 0.55, 0.15, 0.85, 0.55, 0.32),
    ("bob", 0.38, 0.48, 0.12, 0.26, 6),
    ("travel", "note", (0.40, 0.45), (0.70, 0.12), 4, C["pink"], 8),
]
P["p1_07"] = [  # mapa: alfinete cai, cifrões sobem
    ("travel", "spark", (0.55, 0.12), (0.55, 0.48), 3, C["red"], 6),
    ("travel", "coin", (0.30, 0.70), (0.70, 0.28), 4, C["gold"], 6),
    ("pulse", 0.20, 0.20, 0.80, 0.70, 0.16),
]
P["p1_08"] = [  # roteador: ondas saem, cientista balança
    ("arcs", 0.55, 0.42, C["cyan"], 18, 120),
    ("bob", 0.28, 0.55, 0.12, 0.24, 5),
    ("pulse", 0.45, 0.28, 0.68, 0.55, 0.28),
    ("orbit", 0.55, 0.42, 0.14, 4, C["cyan"], 5),
]
P["p1_09"] = [  # marionete balança no fio; diretor respira
    ("swing", 0.46, 0.24, 130, 7),
    ("bob", 0.43, 0.52, 0.08, 0.16, 9),
    ("pulse", 0.30, 0.08, 0.72, 0.28, 0.25),
]
P["p1_10"] = [  # o globo do tempo gira (não a cabeça); a manivela balança
    ("spin", 0.22, 0.43, 82, 1),
    ("swing", 0.70, 0.50, 48, 8),
    ("pulse", 0.78, 0.20, 0.90, 0.36, 0.40),
    ("sparks", 0.74, 0.58, C["orange"], 5, 16),
]

# --- mapa 2 Democracia ---
P["p2_01"] = [  # tio do churrasco: balança, santinhos voam
    ("bob", 0.32, 0.55, 0.12, 0.22, 5),
    ("travel", "flyer", (0.18, 0.16), (0.88, 0.05), 4, C["white"], 7),
    ("steam", 0.22, 0.62, 3),
]
P["p2_02"] = [  # gráfico 99%: o ponteiro e o verde pulsam
    ("pulse", 0.40, 0.18, 0.78, 0.62, 0.34),
    ("swing", 0.38, 0.40, 80, 8),
    ("travel", "spark", (0.48, 0.55), (0.70, 0.22), 3, C["green"], 5),
]
P["p2_03"] = [  # político em cima do muro
    ("bob", 0.50, 0.32, 0.10, 0.16, 7),
    ("swing", 0.50, 0.28, 60, 6),
    ("pulse", 0.35, 0.15, 0.65, 0.40, 0.18),
]
P["p2_04"] = [  # trator de ouro: balança, confete/moedas
    ("bob", 0.48, 0.48, 0.16, 0.20, 5),
    ("travel", "coin", (0.30, 0.65), (0.72, 0.22), 5, C["gold"], 6),
    ("pulse", 0.35, 0.30, 0.62, 0.55, 0.22),
]
P["p2_05"] = [  # robôs votando: botões piscam em onda
    ("wave", 0.15, 0.35, 0.85, 0.75),
    ("bob", 0.40, 0.48, 0.10, 0.18, 4),
    ("pulse", 0.20, 0.25, 0.80, 0.50, 0.26),
]
P["p2_06"] = [  # megafone: anéis de som, panfletos
    ("arcs", 0.58, 0.40, C["gold"], 16, 78),
    ("bob", 0.70, 0.55, 0.10, 0.22, 5),
    ("travel", "flyer", (0.62, 0.32), (0.92, 0.12), 4, C["white"], 7),
]
P["p2_07"] = [  # dupla sertaneja: balanço defasado, notas
    ("bob", 0.38, 0.48, 0.10, 0.22, 6),
    ("bob", 0.58, 0.50, 0.10, 0.22, -6),
    ("travel", "note", (0.48, 0.40), (0.70, 0.12), 4, C["gold"], 7),
]
P["p2_08"] = [  # pena escreve, pergaminho pulsa
    ("swing", 0.42, 0.40, 80, 10),
    ("pulse", 0.45, 0.25, 0.85, 0.70, 0.22),
    ("travel", "note", (0.55, 0.45), (0.85, 0.20), 3, C["green"], 6),
]
P["p2_09"] = [  # sósia suando atrás da cortina
    ("bob", 0.55, 0.48, 0.10, 0.24, 5),
    ("travel", "drop", (0.58, 0.32), (0.60, 0.55), 3, C["cyan"], 5),
    ("swing", 0.30, 0.40, 50, 5),
]
P["p2_10"] = [  # martelo bate
    ("swing", 0.48, 0.28, 70, 12),
    ("sparks", 0.52, 0.55, C["gold"], 5, 16),
    ("pulse", 0.35, 0.30, 0.70, 0.65, 0.18),
]

# --- mapa 3 Pindorama ---
P["p3_01"] = [  # broca vibra, terra sobe
    ("bob", 0.38, 0.42, 0.10, 0.28, 4),
    ("sparks", 0.40, 0.62, C["orange"], 6, 20),
    ("travel", "spark", (0.35, 0.70), (0.55, 0.30), 4, C["gold"], 5),
]
P["p3_02"] = [  # ET balança, vapor do café, olho pulsa
    ("bob", 0.32, 0.50, 0.10, 0.22, 6),
    ("steam", 0.42, 0.55, 3),
    ("pulse", 0.25, 0.32, 0.42, 0.50, 0.30),
]
P["p3_03"] = [  # flash do radar estoura e apaga
    ("sparks", 0.62, 0.48, C["white"], 6, 22),
    ("pulse", 0.50, 0.35, 0.75, 0.62, 0.45),
    ("bob", 0.28, 0.55, 0.08, 0.18, 3),
]
P["p3_04"] = [  # chupa-cabra e a cabra, defasados
    ("bob", 0.32, 0.48, 0.12, 0.20, 6),
    ("bob", 0.62, 0.55, 0.10, 0.16, -5),
    ("pulse", 0.20, 0.25, 0.50, 0.50, 0.20),
]
P["p3_05"] = [  # tomada faisca no carro
    ("sparks", 0.42, 0.48, C["cyan"], 7, 26),
    ("pulse", 0.35, 0.40, 0.70, 0.70, 0.30),
    ("bob", 0.28, 0.50, 0.08, 0.20, 3),
]
P["p3_06"] = [  # lanternas no túnel
    ("pulse", 0.20, 0.30, 0.70, 0.65, 0.35),
    ("bob", 0.35, 0.55, 0.08, 0.18, 4),
    ("bob", 0.58, 0.55, 0.08, 0.18, -4),
]
P["p3_07"] = [  # orelhão: anéis de GPS
    ("arcs", 0.55, 0.42, C["green"], 16, 100),
    ("bob", 0.40, 0.50, 0.08, 0.18, 4),
    ("pulse", 0.45, 0.25, 0.75, 0.55, 0.26),
]
P["p3_08"] = [  # lupa revela o circuito
    ("swing", 0.55, 0.40, 80, 6),
    ("pulse", 0.35, 0.35, 0.70, 0.70, 0.32),
    ("scan", 0.38, 0.40, 0.68, 0.72, C["green"]),
]
P["p3_09"] = [  # mão do fisco morde a moeda
    ("swing", 0.35, 0.30, 110, 6),
    ("travel", "coin", (0.70, 0.55), (0.40, 0.40), 3, C["gold"], 8),
    ("pulse", 0.45, 0.30, 0.75, 0.60, 0.22),
]
P["p3_10"] = [  # ímã puxa as moedas
    ("travel", "coin", (0.25, 0.70), (0.72, 0.28), 5, C["gold"], 6),
    ("pulse", 0.62, 0.12, 0.85, 0.40, 0.30),
    ("bob", 0.30, 0.60, 0.08, 0.16, 3),
]

# --- mapa 4 Religião ---
P["p4_01"] = [  # vinil ao contrário: o disco GIRA, velas tremulam, notas
    ("spin", 0.62, 0.70, 52, 1),
    ("travel", "note", (0.55, 0.55), (0.30, 0.15), 4, C["purple"], 8),
    ("warm", 0.08, 0.55, 0.28, 0.95, 0.30),
    ("pulse", 0.15, 0.20, 0.40, 0.55, 0.22),
    ("bob", 0.50, 0.48, 0.14, 0.22, 3),
    ("orbit", 0.22, 0.28, 0.10, 3, C["purple"], 6),
]
P["p4_02"] = [  # espiral da TV, diabinho levita, criança e gato
    ("pulse", 0.08, 0.25, 0.40, 0.70, 0.40),
    ("bob", 0.22, 0.48, 0.08, 0.12, 6),
    ("bob", 0.55, 0.55, 0.10, 0.18, 4),
    ("bob", 0.78, 0.68, 0.06, 0.10, -3),
    ("orbit", 0.22, 0.48, 0.08, 4, C["pink"], 5),
    ("travel", "note", (0.22, 0.40), (0.40, 0.18), 3, C["pink"], 6),
]
P["p4_03"] = [  # boneção levita, orbes orbitam, esteira dos bonecos
    ("bob", 0.48, 0.40, 0.12, 0.20, 10),
    ("orbit", 0.48, 0.40, 0.16, 5, C["purple"], 7),
    ("scroll", 0.02, 0.72, 0.52, 0.86, 40, "x"),
    ("sparks", 0.48, 0.38, C["purple"], 6, 28),
    ("pulse", 0.30, 0.20, 0.70, 0.55, 0.24),
    ("bob", 0.78, 0.55, 0.10, 0.20, 3),
]
P["p4_04"] = [  # geometria secreta pulsa, coruja cruza
    ("pulse", 0.15, 0.15, 0.85, 0.80, 0.34),
    ("arcs", 0.50, 0.48, C["green"], 20, 110),
    ("orbit", 0.50, 0.48, 0.22, 6, C["green"], 5),
    ("travel", "spark", (0.78, 0.18), (0.92, 0.08), 2, C["gold"], 6),
]
P["p4_05"] = [  # facho varre o palco, operador, confete
    ("scan", 0.25, 0.15, 0.75, 0.75, C["gold"]),
    ("bob", 0.18, 0.62, 0.10, 0.18, 4),
    ("pulse", 0.30, 0.10, 0.70, 0.35, 0.30),
    ("travel", "spark", (0.55, 0.22), (0.70, 0.70), 5, C["gold"], 5),
    ("swing", 0.18, 0.55, 50, 6),
]
P["p4_06"] = [  # fallback se a história falhar
    ("travel", "drop", (0.42, 0.28), (0.44, 0.62), 3, C["gold"], 6),
    ("warm", 0.00, 0.00, 1.0, 1.0, 0.28),
    ("pulse", 0.30, 0.15, 0.60, 0.45, 0.20),
]
P["p4_07"] = [  # fita gira, tábua flutua, arquivista cochicha
    ("spin", 0.14, 0.62, 28, 1),
    ("spin", 0.22, 0.62, 28, 1),
    ("bob", 0.55, 0.28, 0.08, 0.10, 6),
    ("arcs", 0.62, 0.45, C["cyan"], 14, 90),
    ("bob", 0.48, 0.58, 0.10, 0.18, 3),
    ("pulse", 0.45, 0.20, 0.80, 0.60, 0.28),
]
P["p4_08"] = [  # fallback
    ("scroll", 0.02, 0.52, 0.38, 0.68, 56, "x"),
    ("travel", "drop", (0.54, 0.32), (0.54, 0.55), 3, C["cyan"], 6),
    ("halo", 0.62, 0.48, 0.03),
]
P["p4_09"] = [  # empurra o bloco do apocalipse, alarme, suor
    ("bob", 0.55, 0.50, 0.12, 0.22, 5),
    ("swing", 0.58, 0.48, 80, 7),
    ("pulse", 0.08, 0.02, 0.18, 0.16, 0.55),
    ("travel", "drop", (0.52, 0.32), (0.54, 0.50), 3, C["cyan"], 4),
    ("sparks", 0.72, 0.42, C["red"], 4, 14),
]
P["p4_10"] = [  # fallback
    ("pulse", 0.40, 0.05, 0.70, 0.85, 0.40),
    ("scan", 0.45, 0.05, 0.62, 0.80, C["cyan"]),
    ("bob", 0.30, 0.62, 0.08, 0.14, 3),
]

# --- mapa 5 Singularidade ---
P["p5_01"] = [  # coluna verde da antena
    ("pulse", 0.55, 0.05, 0.75, 0.80, 0.40),
    ("travel", "spark", (0.62, 0.70), (0.66, 0.15), 4, C["green"], 5),
    ("bob", 0.32, 0.58, 0.10, 0.18, 4),
]
P["p5_02"] = [  # a dose pinga, o medidor pulsa no vermelho
    ("travel", "drop", (0.22, 0.22), (0.24, 0.55), 3, C["cyan"], 7),
    ("pulse", 0.58, 0.12, 0.82, 0.42, 0.40),
    ("bob", 0.30, 0.45, 0.10, 0.20, 3),
    ("steam", 0.40, 0.55, 3),
]
P["p5_03"] = [  # apagão em onda nas janelinhas
    ("wave", 0.02, 0.08, 0.55, 0.78),
    ("pulse", 0.28, 0.02, 0.42, 0.18, 0.55),
    ("bob", 0.70, 0.48, 0.08, 0.20, 3),
]
P["p5_04"] = [  # olho da Skynet pulsa
    ("pulse", 0.35, 0.20, 0.65, 0.60, 0.38),
    ("bob", 0.72, 0.62, 0.08, 0.16, 4),
    ("arcs", 0.50, 0.40, C["purple"], 18, 70),
]
P["p5_05"] = [  # aparelho suga a conversa, TV varre
    ("arcs", 0.16, 0.28, C["cyan"], 12, 55),
    ("scan", 0.62, 0.18, 0.96, 0.58, C["cyan"]),
    ("pulse", 0.28, 0.62, 0.48, 0.82, 0.30),
    ("bob", 0.28, 0.50, 0.10, 0.16, 3),
]
P["p5_06"] = [  # bateria entra, faísca, olhos acendem
    ("sparks", 0.56, 0.42, C["gold"], 7, 30),
    ("pulse", 0.26, 0.20, 0.46, 0.38, 0.35),
    ("bob", 0.32, 0.48, 0.12, 0.24, 4),
    ("bob", 0.70, 0.55, 0.10, 0.20, 3),
]
P["p5_07"] = [  # pombos-drone: cada um num tempo
    ("bob", 0.25, 0.35, 0.06, 0.08, 5),
    ("bob", 0.45, 0.32, 0.06, 0.08, -5),
    ("bob", 0.65, 0.36, 0.06, 0.08, 4),
    ("pulse", 0.20, 0.25, 0.80, 0.50, 0.22),
]
P["p5_08"] = [  # anéis da torre-palmeira, jardineiro rega
    ("arcs", 0.32, 0.38, C["orange"], 16, 100),
    ("bob", 0.62, 0.55, 0.08, 0.18, 4),
    ("travel", "drop", (0.55, 0.48), (0.48, 0.68), 3, C["cyan"], 5),
]
P["p5_09"] = [  # última gota no QR, celular varre
    ("travel", "drop", (0.56, 0.42), (0.50, 0.68), 2, C["green"], 6),
    ("scan", 0.30, 0.55, 0.62, 0.88, C["green"]),
    ("pulse", 0.16, 0.35, 0.34, 0.70, 0.35),
]
P["p5_10"] = [  # chip no prato do restaurante
    ("pulse", 0.35, 0.40, 0.60, 0.70, 0.32),
    ("bob", 0.72, 0.50, 0.08, 0.18, 4),
    ("sparks", 0.48, 0.55, C["purple"], 5, 18),
]


def main(argv: list[str]) -> None:
    if not argv or argv == ["--all"]:
        ids = sorted(P)
    else:
        ids = argv
    missing = [i for i in ids if i not in P]
    if missing:
        raise SystemExit(f"sem performance: {missing}")
    for mid in ids:
        frames = render(mid, P[mid])
        save(mid, frames)


if __name__ == "__main__":
    main(sys.argv[1:])

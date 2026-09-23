"""kit.py — motor de loops narrativos (animação v2) do O GIGANTE DESPERTOU.

Princípio do plano (`docs/ANIM_V2_PLANO_LOTES.md`): a **pintura aprovada é a
base**, nunca é redesenhada. A história é contada por camadas por cima dela:

  * **máscaras suaves** (elipse/retângulo/anel) para agir só na região certa;
  * **warps locais** (deslocamento/rotação com máscara) para articular o que já
    está pintado (mão, cabeça, boneca, engrenagem) sem abrir buraco — o entorno
    é esticado, não revelado;
  * **inpaint** (interpolação por linha + difusão) apenas onde a mecânica exige
    apagar algo pintado (feixe apagado, garrafa sob o bico, pessoas no céu);
  * **recortes** (sprites) para o que precisa viajar na cena (garrafa);
  * **FX desenhados** no traço flat-toon (gotas, auréola, chama, vapor, confete,
    lágrima, papéis, pessoas) — mesmos tons da pintura;
  * **timeline de keyframes** com fechamento de loop (o valor de saída de cada
    trilha volta ao valor de entrada, então o último quadro emenda no primeiro).

Uso típico:

    from . import kit as K
    base = K.plate('p4_06')
    a = K.warp_rotate(base, 292, 252, 20, tilt_deg)
    img = K.to_rgba(a)
    K.fx_drop(img, 278, 206, 3.0, (255, 214, 120), 0.9)
    frames.append(K.from_rgba(img))
    ...
    K.save_loop('p4_06', frames, durations)
"""
from __future__ import annotations

import math
import os
import re

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 640, 360
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANIM = os.path.join(ROOT, "src", "assets", "anim")

# grade de coordenadas reaproveitada por todos os warps (uma vez por processo)
_X, _Y = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))

_FONT_CACHE: dict = {}


# ---------------------------------------------------------------------------
# carga / conversão
# ---------------------------------------------------------------------------
def scene_dir(scene: str) -> str:
    return os.path.join(ANIM, scene)


def load_arr(path: str) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)


def plate(scene: str, name: str = "poster.webp") -> np.ndarray:
    """Pintura mestre da missão (nunca modificada no disco)."""
    return load_arr(os.path.join(scene_dir(scene), name))


def to_img(a: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def to_rgba(a: np.ndarray) -> Image.Image:
    return to_img(a).convert("RGBA")


def from_rgba(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGB"), dtype=np.float32)


def font(size: int):
    if size not in _FONT_CACHE:
        f = None
        for name in ("DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
            try:
                f = ImageFont.truetype(name, size)
                break
            except Exception:
                continue
        _FONT_CACHE[size] = f or ImageFont.load_default()
    return _FONT_CACHE[size]


# ---------------------------------------------------------------------------
# máscaras
# ---------------------------------------------------------------------------
def _mask(paint, feather: float) -> np.ndarray:
    im = Image.new("L", (W, H), 0)
    paint(ImageDraw.Draw(im))
    if feather and feather > 0:
        im = im.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(im, dtype=np.float32) / 255.0


def mellipse(cx, cy, rx, ry, feather: float = 2.0) -> np.ndarray:
    return _mask(lambda d: d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255), feather)


def mrect(x0, y0, x1, y1, feather: float = 2.0) -> np.ndarray:
    return _mask(lambda d: d.rectangle([x0, y0, x1, y1], fill=255), feather)


def mring(cx, cy, r0, r1, feather: float = 1.5) -> np.ndarray:
    def paint(d):
        d.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=255)
        d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=0)
    return _mask(paint, feather)


def blur_mask(m: np.ndarray, radius: float) -> np.ndarray:
    im = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), "L")
    im = im.filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im, dtype=np.float32) / 255.0


def grow(m: np.ndarray, radius: float = 1.0) -> np.ndarray:
    """Dilatação leve (usada para pegar a borda pintada de um feixe/traço)."""
    return (blur_mask(m, radius) > 0.25).astype(np.float32)


def color_key(a: np.ndarray, fn) -> np.ndarray:
    return np.where(fn(a), 1.0, 0.0).astype(np.float32)


def union(*masks) -> np.ndarray:
    out = np.zeros((H, W), np.float32)
    for m in masks:
        out = np.maximum(out, m)
    return out


# ---------------------------------------------------------------------------
# inpaint: interpolação por linha + difusão (só onde a mecânica exige apagar)
# ---------------------------------------------------------------------------
def inpaint(a: np.ndarray, mask: np.ndarray, iters: int = 60) -> np.ndarray:
    hard = mask > 0.35
    if not hard.any():
        return a.copy()
    ys, xs = np.where(hard)
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    out = a.copy()
    # 1) chute inicial: interpola linearmente entre os vizinhos limpos da linha
    for y in range(y0, y1):
        row = hard[y, x0:x1]
        if not row.any():
            continue
        idx = np.where(~row)[0]
        if idx.size == 0:
            continue
        xx = np.arange(x0, x1, dtype=np.float32)
        xn = (idx + x0).astype(np.float32)
        for c in range(3):
            out[y, x0:x1, c] = np.where(row, np.interp(xx, xn, a[y, idx + x0, c]),
                                        a[y, x0:x1, c])
    # 2) difusão: suaviza o chute até casar com o entorno
    p = np.pad(out, ((1, 1), (1, 1), (0, 0)), mode="edge")
    for _ in range(iters):
        avg = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4.0
        out[hard] = avg[hard]
        p[1:-1, 1:-1] = out
    return out


def fill_rows(a: np.ndarray, mask: np.ndarray, y_from: int, y_to: int,
              x_win, skip_rect=None, blur: float = 2.0) -> np.ndarray:
    """Preenche `mask` copiando, linha a linha, a mediana de uma janela limpa.

    É a técnica usada no p4_05 (feixe do holofote) e no p4_08 (estação do bico):
    o fundo dessas cenas é chapado, então a mediana local reconstitui a parede /
    a madeira sem as manchas de uma difusão ampla.
    """
    sel = mask < 0.4
    mf = blur_mask(mask, blur)
    fill = a.copy()
    for y in range(max(0, y_from), min(H, y_to)):
        s = sel[y].copy()
        s[:x_win[0]] = False
        s[x_win[1]:] = False
        if skip_rect is not None:
            sx0, sy0, sx1, sy1 = skip_rect
            if sy0 <= y < sy1:
                s[sx0:sx1] = False
        if s.sum() < 6:
            s = sel[y]
        fill[y] = np.median(a[y][s], axis=0)
    m3 = mf[..., None]
    return a * (1 - m3) + fill * m3


# ---------------------------------------------------------------------------
# warps locais
# ---------------------------------------------------------------------------
def _sample(a: np.ndarray, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    h, w = a.shape[:2]
    xs = np.clip(xs, 0, w - 1.001)
    ys = np.clip(ys, 0, h - 1.001)
    x0 = np.floor(xs).astype(np.int32)
    y0 = np.floor(ys).astype(np.int32)
    x1 = np.minimum(x0 + 1, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    fx = (xs - x0)[..., None]
    fy = (ys - y0)[..., None]
    top = a[y0, x0] * (1 - fx) + a[y0, x1] * fx
    bot = a[y1, x0] * (1 - fx) + a[y1, x1] * fx
    return top * (1 - fy) + bot * fy


def warp_shift(a: np.ndarray, m: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Move o conteúdo dentro da máscara (o resto fica parado)."""
    if abs(dx) < 1e-4 and abs(dy) < 1e-4:
        return a
    return _sample(a, _X - dx * m, _Y - dy * m)


def warp_rotate(a: np.ndarray, cx, cy, radius, deg: float, feather: float = 0.55) -> np.ndarray:
    """Gira o conteúdo dentro de um círculo suave em torno de (cx, cy)."""
    if abs(deg) < 1e-4:
        return a
    r = np.sqrt((_X - cx) ** 2 + (_Y - cy) ** 2)
    soft = max(1.0, radius * feather)
    m = np.clip((radius - r) / soft, 0, 1)
    m = m * m * (3 - 2 * m)
    th = math.radians(deg) * m
    dx, dy = _X - cx, _Y - cy
    ct, st = np.cos(th), np.sin(th)
    return _sample(a, cx + dx * ct + dy * st, cy - dx * st + dy * ct)


def roll_band(a: np.ndarray, x0, x1, y0, y1, dx: float) -> np.ndarray:
    """Rolagem cíclica de uma faixa (esteira/correia)."""
    n = int(round(dx))
    if n:
        a[y0:y1, x0:x1] = np.roll(a[y0:y1, x0:x1], n, axis=1)
    return a


# ---------------------------------------------------------------------------
# cor
# ---------------------------------------------------------------------------
def lerp_imgs(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    t = max(0.0, min(1.0, t))
    return a * (1 - t) + b * t


def tint(a: np.ndarray, m: np.ndarray, color, alpha: float) -> np.ndarray:
    m3 = (m * alpha)[..., None]
    return np.clip(a * (1 - m3) + np.asarray(color, np.float32) * m3, 0, 255)


def glow(a: np.ndarray, cx, cy, r, color, alpha: float) -> np.ndarray:
    if alpha <= 0.004:
        return a
    d = np.sqrt((_X - cx) ** 2 + (_Y - cy) ** 2)
    m = np.clip(1 - d / float(r), 0, 1)
    m = m * m * (3 - 2 * m)
    return np.clip(a + np.asarray(color, np.float32) * m[..., None] * alpha, 0, 255)


# ---------------------------------------------------------------------------
# recortes (sprites) e colagem
# ---------------------------------------------------------------------------
def _local_alpha(w: int, h: int, feather: float) -> np.ndarray:
    im = Image.new("L", (w, h), 0)
    f = max(1, int(round(feather)))
    ImageDraw.Draw(im).rectangle([f, f, w - 1 - f, h - 1 - f], fill=255)
    if feather:
        im = im.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(im, dtype=np.float32) / 255.0


def cut(a: np.ndarray, box, feather: float = 3.0) -> Image.Image:
    """Recorte retangular suave (usado quando o destino tem o mesmo fundo)."""
    x0, y0, x1, y1 = box
    img = to_rgba(a[y0:y1, x0:x1])
    al = _local_alpha(img.width, img.height, feather)
    img.putalpha(Image.fromarray((al * 255).astype(np.uint8), "L"))
    return img


def cut_silhouette(a: np.ndarray, box, tol: float = 95.0, ramp: float = 40.0,
                   feather: float = 1.4, min_filter: int = 0, grow_px: int = 2, bg=None,
                   keep=None) -> Image.Image:
    """Recorta um objeto claro apoiado num fundo chapado, matando o glow pintado.

    `bg` = cor do fundo (por padrão a mediana da borda da caixa). `min_filter`
    come 1-2 px do contorno, que é justamente onde mora o halo suave da pintura.
    """
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1].copy()
    if bg is None:
        border = np.concatenate([sub[0], sub[-1], sub[:, 0], sub[:, -1]]).reshape(-1, 3)
        bg = np.median(border, axis=0)
    d = np.sqrt(((sub - np.asarray(bg, np.float32)) ** 2).sum(-1))
    m = np.clip((d - tol) / ramp, 0, 1)
    if keep is not None:
        m = np.maximum(m, keep)
    im = Image.fromarray((m * 255).astype(np.uint8), "L")
    if min_filter:
        im = im.filter(ImageFilter.MinFilter(min_filter))
    if grow_px:
        # recupera o contorno escuro do objeto (ele fica perto do fundo em cor)
        im = im.filter(ImageFilter.MaxFilter(2 * grow_px + 1))
    if feather:
        im = im.filter(ImageFilter.GaussianBlur(feather))
    img = to_rgba(sub)
    img.putalpha(im)
    return img


def fill_bottle(sp: Image.Image, level: float, color=(96, 208, 236)) -> Image.Image:
    """Nível de líquido dentro de um sprite de garrafa (o vidro é o molde)."""
    out = sp.copy()
    if level <= 0.01:
        return out
    w, h = out.size
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    top = h - 6 - (h - 24) * max(0.0, min(1.0, level))
    d.rounded_rectangle([5, top, w - 6, h - 5], radius=3, fill=tuple(color) + (240,))
    d.line([6, top + 1, w - 7, top + 1], fill=(232, 250, 255, 240), width=1)
    out.alpha_composite(ov)
    out.putalpha(ImageChops.multiply(out.getchannel("A"), sp.getchannel("A")))
    return out


def paste(img: Image.Image, sp: Image.Image, x, y, alpha: float = 1.0,
          scale: float = 1.0, rot: float = 0.0) -> Image.Image:
    if scale != 1.0:
        w, h = sp.size
        sp = sp.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    if rot:
        sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        sp = sp.copy()
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * max(0.0, alpha))))
    img.alpha_composite(sp, (int(round(x)), int(round(y))))
    return img


# ---------------------------------------------------------------------------
# FX desenhados (flat-toon, mesmos tons da pintura)
# ---------------------------------------------------------------------------
def _a(alpha: float) -> int:
    return int(round(255 * max(0.0, min(1.0, alpha))))


def fx_drop(img, x, y, r, color=(255, 214, 120), alpha=1.0, outline=None):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    box = [x - r * 0.82, y - r, x + r * 0.82, y + r]
    d.ellipse(box, fill=tuple(color) + (_a(alpha),))
    if outline:
        d.ellipse(box, outline=tuple(outline) + (_a(alpha),), width=1)
    if r > 2.2:
        d.ellipse([x - r * 0.45, y - r * 0.55, x - r * 0.05, y - r * 0.15],
                  fill=(255, 255, 255, _a(alpha * 0.55)))


def fx_splash(img, x, y, r, color, alpha):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    for k in range(5):
        ang = -math.pi * 0.85 + k * (math.pi * 0.42)
        x2 = x + math.cos(ang) * r
        y2 = y - abs(math.sin(ang)) * r * 0.85
        d.line([x, y, x2, y2], fill=tuple(color) + (_a(alpha),), width=max(1, int(r * 0.16)))
    d.ellipse([x - r * 0.3, y - r * 0.3, x + r * 0.3, y + r * 0.3], fill=tuple(color) + (_a(alpha),))


def fx_spark(img, x, y, r, color=(255, 255, 226), alpha=1.0):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    a = _a(alpha)
    d.polygon([(x, y - r), (x + r * 0.22, y), (x, y + r), (x - r * 0.22, y)], fill=tuple(color) + (a,))
    d.polygon([(x - r, y), (x, y - r * 0.22), (x + r, y), (x, y + r * 0.22)], fill=tuple(color) + (a,))


def fx_halo(img, x, y, r, alpha, color=(255, 216, 120), width=1.8, squash=0.42):
    """Auréola: anel principal + brilho externo (o adesivo santo das garrafas)."""
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    w = max(1, int(round(width)))
    d.ellipse([x - r * 1.5, y - r * squash * 1.5, x + r * 1.5, y + r * squash * 1.5],
              outline=tuple(color) + (_a(alpha * 0.22),), width=max(1, int(round(width * 1.6))))
    d.ellipse([x - r, y - r * squash, x + r, y + r * squash],
              outline=tuple(color) + (_a(alpha),), width=w)


def fx_text(img, x, y, text, size, color, alpha, mirror=False, stroke=None):
    if alpha <= 0.02:
        return
    f = font(size)
    tmp = Image.new("RGBA", (len(text) * size + 24, size * 2 + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((6, 6), text, font=f, fill=tuple(color) + (_a(alpha),),
           stroke_width=2 if stroke else 0,
           stroke_fill=(tuple(stroke) + (_a(alpha * 0.9),)) if stroke else None)
    tmp = tmp.crop(tmp.getbbox() or (0, 0, 1, 1))
    if mirror:
        tmp = tmp.transpose(Image.FLIP_LEFT_RIGHT)
    img.alpha_composite(tmp, (int(x - tmp.width / 2), int(y - tmp.height / 2)))


def fx_note(img, x, y, size, alpha, color=(255, 232, 190), mirror=False):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    a = _a(alpha)
    r = size * 0.34
    d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=tuple(color) + (a,))
    sx = x + (r if mirror else -r)
    d.line([sx, y, sx, y - size], fill=tuple(color) + (a,), width=max(1, int(size * 0.16)))
    d.line([sx, y - size, sx + (-1 if mirror else 1) * size * 0.42, y - size + size * 0.16],
           fill=tuple(color) + (a,), width=max(1, int(size * 0.16)))


def fx_person(img, x, y, h, body, skin, alpha, arms_up=0.0, halo=0.0, outline=(28, 34, 44)):
    """Pessoazinha flat-toon (a rua do p4_10) — nasce em pé e sobe ao arrebatar."""
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    a = _a(alpha)
    ow = max(1, int(round(h * 0.055)))
    hr = h * 0.15
    hy = y - h + hr
    d.line([x, y - h * 0.66, x, y], fill=tuple(body) + (a,), width=max(2, int(h * 0.20)))
    d.line([x - h * 0.10, y, x + h * 0.10, y], fill=tuple(outline) + (a,), width=ow)
    # braços (sobem no arrebatamento)
    ax, ay = x, y - h * 0.62
    for sgn in (-1, 1):
        ex = x + sgn * (h * 0.20) * (1 - arms_up) + sgn * (h * 0.13) * arms_up
        ey = ay + h * 0.22 * (1 - arms_up) - h * 0.30 * arms_up
        d.line([ax, ay, ex, ey], fill=tuple(skin) + (a,), width=max(1, int(h * 0.09)))
    d.line([x, y - h * 0.66, x, y], fill=tuple(outline) + (a,), width=ow)
    d.ellipse([x - hr, hy - hr, x + hr, hy + hr], fill=tuple(skin) + (a,),
              outline=tuple(outline) + (a,), width=ow)
    if halo > 0.02:
        fx_halo(img, x, hy - hr - h * 0.14, h * 0.13, halo, (255, 226, 140), 1.6)


def fx_steam(img, x, y, r, alpha, t, color=(226, 244, 248)):
    if alpha <= 0.02:
        return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(3):
        tt = (t + k / 3.0) % 1.0
        rr = r * (0.45 + 0.35 * math.sin(math.pi * tt))
        px = x + math.sin(2 * math.pi * tt) * r * 0.35
        py = y - tt * r * 1.5
        d.ellipse([px - rr, py - rr * 0.7, px + rr, py + rr * 0.7],
                  fill=tuple(color) + (_a(alpha * math.sin(math.pi * tt)),))
    lay = lay.filter(ImageFilter.GaussianBlur(2.2))
    img.alpha_composite(lay)


def fx_bubbles(img, x, y, r, n, t, color=(198, 244, 255), alpha=0.85):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    for k in range(n):
        tt = (t + k / float(n)) % 1.0
        px = x + math.sin(2 * math.pi * (k * 0.37 + tt * 0.2)) * r * 0.45
        py = y + r * 0.6 - tt * r * 1.25
        rr = 1.4 + 1.7 * math.sin(math.pi * tt)
        d.ellipse([px - rr, py - rr, px + rr, py + rr],
                  outline=tuple(color) + (_a(alpha * math.sin(math.pi * tt)),), width=1)


def fx_dash(img, x, y, ln, deg, alpha, color, width=2):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    th = math.radians(deg)
    dx, dy = math.cos(th) * ln / 2.0, math.sin(th) * ln / 2.0
    d.line([x - dx, y - dy, x + dx, y + dy], fill=tuple(color) + (_a(alpha),),
           width=max(1, int(width)))


def fx_arc(img, x, y, r, a0, a1, alpha, color, width=2):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    d.arc([x - r, y - r, x + r, y + r], a0, a1, fill=tuple(color) + (_a(alpha),),
          width=max(1, int(width)))


def fx_ring(img, x, y, r, alpha, color, width=2, squash=0.55):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    d.ellipse([x - r, y - r * squash, x + r, y + r * squash],
              outline=tuple(color) + (_a(alpha),), width=max(1, int(width)))


def fx_wedge(img, x, y, r, deg, spread, alpha, color):
    if alpha <= 0.02:
        return
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(4):
        a = math.radians(deg + k * 22)
        d.polygon([(x, y),
                   (x + math.cos(a - math.radians(spread)) * r, y + math.sin(a - math.radians(spread)) * r),
                   (x + math.cos(a + math.radians(spread)) * r, y + math.sin(a + math.radians(spread)) * r)],
                  fill=tuple(color) + (_a(alpha * (1 - k * 0.22)),))
    lay = lay.filter(ImageFilter.GaussianBlur(1.6))
    img.alpha_composite(lay)


def fx_scribble(img, box, n, t, alpha, color=(44, 52, 70)):
    """Rabiscos que vão se formando na prancheta (inspetor do p4_08)."""
    if alpha <= 0.02 or n <= 0:
        return
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    for k in range(min(n, 12)):
        yy = y0 + (y1 - y0) * (k + 0.5) / 12.0
        amp = (y1 - y0) * 0.06
        pts = []
        for j in range(7):
            xx = x0 + (x1 - x0) * j / 6.0
            pts.append((xx, yy + amp * math.sin(j * 1.7 + k * 0.9 + t)))
        d.line(pts, fill=tuple(color) + (_a(alpha),), width=1)


def fx_papers(img, x, y, s, rot, alpha, color=(246, 244, 236)):
    if alpha <= 0.02:
        return
    lay = Image.new("RGBA", (s * 3, s * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon([(s, s * 0.5), (s * 2, s * 0.7), (s * 1.9, s * 2.2), (s * 0.9, s * 2.0)],
              fill=tuple(color) + (_a(alpha),), outline=(90, 96, 108, _a(alpha)))
    d.line([(s * 1.15, s * 1.15), (s * 1.75, s * 1.3)], fill=(120, 128, 140, _a(alpha)), width=1)
    d.line([(s * 1.15, s * 1.55), (s * 1.7, s * 1.7)], fill=(120, 128, 140, _a(alpha)), width=1)
    lay = lay.rotate(rot, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(lay, (int(x - s * 1.5), int(y - s * 1.5)))


def fx_xmark(img, x, y, s, alpha, color=(214, 66, 58), width=4):
    if alpha <= 0.02:
        return
    d = ImageDraw.Draw(img)
    for sgn in (-1, 1):
        d.line([x - s / 2, y - s * 0.42, x + s / 2, y + s * 0.42],
               fill=tuple(color) + (_a(alpha),), width=max(1, int(width)))
        d.line([x + s / 2, y - s * 0.42, x - s / 2, y + s * 0.42],
               fill=tuple(color) + (_a(alpha),), width=max(1, int(width)))


# ---------------------------------------------------------------------------
# timeline
# ---------------------------------------------------------------------------
def track(pairs, f: float) -> float:
    """Interpolação linear por keyframes: [(quadro, valor), ...]."""
    if f <= pairs[0][0]:
        return float(pairs[0][1])
    for (f0, v0), (f1, v1) in zip(pairs, pairs[1:]):
        if f <= f1:
            if f1 == f0:
                return float(v1)
            return float(v0 + (v1 - v0) * (f - f0) / (f1 - f0))
    return float(pairs[-1][1])


def smooth(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out_back(t: float, k: float = 1.7) -> float:
    t = max(0.0, min(1.0, t)) - 1.0
    return 1 + t * t * ((k + 1) * t + k)


def cyc(i, N, phase: float = 0.0) -> float:
    return math.sin(2 * math.pi * (i / float(N) + phase))


# ---------------------------------------------------------------------------
# empacotamento do loop
# ---------------------------------------------------------------------------
def save_loop(scene: str, frames, durations, quality: int = 84) -> float:
    """Grava ff_XX.webp + loop.webp + contact.png e devolve a consistência."""
    d = scene_dir(scene)
    fd = os.path.join(d, "frames")
    os.makedirs(fd, exist_ok=True)
    for f in os.listdir(fd):
        if re.match(r"ff_\d+\.webp$", f):
            os.remove(os.path.join(fd, f))
    imgs = [to_img(a) for a in frames]
    for i, im in enumerate(imgs):
        im.save(os.path.join(fd, f"ff_{i:02d}.webp"), quality=quality, method=4)
    imgs[0].save(os.path.join(d, "loop.webp"), save_all=True, append_images=imgs[1:],
                 duration=[int(x) for x in durations], loop=0, quality=quality, method=4)
    # folha de contato (4 colunas) para conferência rápida
    cols, tw, th = 4, 160, 90
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (10, 12, 16))
    for i, im in enumerate(imgs):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    sheet.save(os.path.join(d, "contact.png"))
    # métrica de consistência: o quanto a cena muda entre quadros vizinhos
    small = [np.asarray(im.resize((80, 45), Image.LANCZOS), dtype=np.float32) for im in imgs]
    diffs = [float(np.abs(small[i + 1] - small[i]).mean()) for i in range(len(small) - 1)]
    return sum(diffs) / max(1, len(diffs))

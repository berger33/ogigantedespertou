#!/usr/bin/env python3
"""build_motion_frames.py — sintetiza f01..f03 a partir do quadro-mestre pintado f00.

Pipeline híbrido (quota de geração de imagem do ambiente limitado): para as cenas
com mestre pintado, o movimento é composto PROGRAMATICAMENTE sobre a pintura:
  - transform global (zoom/pan/rotação em volta do pivô da ação)
  - FX desenhados por cena (glitch, vapor, brilhos, alfinete, carimbo, ondas, $, poeira)

Cada cena tem VERBO ÚNICO (RECIPE) — nunca a mesma animação genérica.
O f00 é reescrito já recortado 16:9 (mesma matemática do build_animation_loop.py)
para que os 4 quadros tenham tamanho idêntico; o build_animation_loop.py segue
fazendo loop.webp/poster.webp/contact.png normalmente.

Uso: python3 tools/build_motion_frames.py <id> [id ...]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_animation_loop import crop169  # noqa: E402

INK = (10, 18, 16, 255)
GREEN = (57, 255, 156, 255)
PURPLE = (181, 123, 255, 255)
GOLD = (212, 175, 55, 255)
RED = (227, 60, 46, 255)
WHITE = (255, 255, 255, 255)
PINK = (244, 130, 160, 255)
BLUE = (77, 195, 255, 255)
ORANGE = (255, 159, 69, 255)
CYAN = (140, 235, 255, 255)

_FONT_CACHE = {}


def bold_font(size):
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if Path(path).exists():
            f = ImageFont.truetype(path, size)
            _FONT_CACHE[size] = f
            return f
    _FONT_CACHE[size] = ImageFont.load_default()
    return _FONT_CACHE[size]


# ---------------------------------------------------------------- helpers ---

def zoom_pan(im, cx, cy, scale):
    """Amplia `scale` em volta do ponto normalizado (cx, cy) e recorta o original."""
    w, h = im.size
    big = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    x = int(cx * w * scale - w / 2)
    y = int(cy * h * scale - h / 2)
    x = max(0, min(x, big.width - w))
    y = max(0, min(y, big.height - h))
    return big.crop((x, y, x + w, y + h))


def rotate_around(im, cx, cy, deg):
    """Rotaciona `deg` graus em volta do ponto normalizado (cx, cy)."""
    w, h = im.size
    ang = math.radians(deg)
    c, s = math.cos(ang), math.sin(ang)
    pw, ph = w, h
    # canvas grande o suficiente
    W2 = int(w * abs(c) + h * abs(s)) + 8
    H2 = int(w * abs(s) + h * abs(c)) + 8
    big = Image.new("RGB", (W2, H2), (0, 0, 0))
    px, py = int(cx * w), int(cy * h)
    rot = im.rotate(deg, resample=Image.BICUBIC, expand=True)
    # centraliza o pivô
    ox = (W2 - rot.width) // 2
    oy = (H2 - rot.height) // 2
    big.paste(rot, (ox, oy))
    # o pivô no sistema rotacionado:
    dx, dy = px - w // 2, py - h // 2
    rx = W2 // 2 + int(dx * c - dy * s)
    ry = H2 // 2 + int(dx * s + dy * c)
    x = rx - w // 2
    y = ry - h // 2
    x = max(0, min(x, big.width - w))
    y = max(0, min(y, big.height - h))
    return big.crop((x, y, x + w, y + h))


def overlay(im):
    return Image.new("RGBA", im.size, (0, 0, 0, 0))


def composite(base, ov):
    out = base.convert("RGBA")
    out.alpha_composite(ov)
    return out.convert("RGB")


def _px(im, nx, ny):
    return int(nx * im.width), int(ny * im.height)


def ring(d, nx, ny, r, color, width=6, alpha=200):
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2], alpha)
    d.ellipse([x - r, y - r, x + r, y + r], outline=c, width=width)


def radial_glow(d, nx, ny, r, color, alpha=120):
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2])
    a = alpha
    while r > 4:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(c[0], c[1], c[2], a))
        r = int(r * 0.72)
        a = max(0, a - 34)


def sparkle(d, nx, ny, r, color, alpha=230):
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2], alpha)
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y),
               (x + r * 0.22, y + r * 0.22), (x, y + r), (x - r * 0.22, y + r * 0.22),
               (x - r, y), (x - r * 0.22, y - r * 0.22)], fill=c)
    d.ellipse([x - r * 0.18, y - r * 0.18, x + r * 0.18, y + r * 0.18], fill=(255, 255, 255, alpha))


def burst_lines(d, nx, ny, r0, r1, n=6, color=WHITE, alpha=210, width=5):
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2], alpha)
    for i in range(n):
        a = 2 * math.pi * i / n + 0.4
        d.line([(x + math.cos(a) * r0, y + math.sin(a) * r0),
                (x + math.cos(a) * r1, y + math.sin(a) * r1)], fill=c, width=width)


def line(d, n_a, n_b, color, width=5, alpha=200):
    c = (color[0], color[1], color[2], alpha)
    d.line([_px(d._image, *n_a), _px(d._image, *n_b)], fill=c, width=width)


def arc_line(d, nx, ny, r, a0, a1, color, width=6, alpha=200):
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2], alpha)
    d.arc([x - r, y - r, x + r, y + r], a0, a1, fill=c, width=int(width))


def arc_spiral(d, nx, ny, r, color, alpha=170, width=6, rot=0.0):
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2], alpha)
    for i in range(3):
        a0 = rot + i * 2.1
        d.arc([x - r, y - r, x + r, y + r], math.degrees(a0), math.degrees(a0 + 4.2),
              fill=c, width=width)


def note(d, nx, ny, r, color, alpha=230):
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2], alpha)
    d.ellipse([x - r * 0.55, y - r * 0.4, x + r * 0.55, y + r * 0.4], fill=c)
    d.line([(x + r * 0.45, y - r * 0.1), (x + r * 0.45, y - r * 1.5)], fill=c, width=max(3, int(r * 0.22)))
    d.line([(x + r * 0.45, y - r * 1.5), (x + r * 0.95, y - r * 1.15)], fill=c, width=max(3, int(r * 0.22)))


def steam_swirl(d, nx, ny, h, w, color, alpha=150, width=6):
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2], alpha)
    pts = []
    for i in range(24):
        t = i / 23.0
        pts.append((x + math.sin(t * math.pi * 2.2) * w * (0.4 + 0.6 * t), y - t * h))
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=c, width=width)


def dollar_puff(d, nx, ny, r, alpha=200):
    x, y = _px(d._image, nx, ny)
    d.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85], fill=(212, 175, 55, 60))
    f = bold_font(int(r * 1.1))
    d.text((x, y), "$", font=f, fill=GOLD, anchor="mm")


def confetti(d, nx, ny, r, n=14, seed=7, palette=None):
    rnd = random.Random(seed)
    x, y = _px(d._image, nx, ny)
    palette = palette or [GOLD, (255, 159, 69, 255), WHITE, (255, 93, 93, 255)]
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        dist = rnd.uniform(r * 0.25, r)
        cx = x + math.cos(a) * dist
        cy = y + math.sin(a) * dist * 0.8
        c = rnd.choice(palette)
        d.rectangle([cx - 5, cy - 8, cx + 5, cy + 8], fill=(c[0], c[1], c[2], 230))


def text(d, nx, ny, s, size, color, alpha=255):
    x, y = _px(d._image, nx, ny)
    d.text((x, y), s, font=bold_font(size), fill=(color[0], color[1], color[2], alpha), anchor="mm")


def glitch_band(im, y0, y1, n, max_shift, seed=3):
    """Desloca fatias horizontais da faixa (efeito de reescrita do texto)."""
    w, h = im.size
    box = (0, int(y0 * h), w, int(y1 * h))
    band = im.crop(box)
    rnd = random.Random(seed)
    n = max(4, n)
    bh = band.height // n
    edge = band.getpixel((2, 2))
    out = Image.new("RGB", band.size, edge)
    for i in range(n):
        sl = band.crop((0, i * bh, band.width, (i + 1) * bh))
        dx = rnd.choice([-1, 1]) * rnd.randint(max_shift // 3, max_shift)
        out.paste(sl, (dx, i * bh))
    # esconder as bordas expostas
    out = out.crop((max(0, -max_shift), 0, out.width - max(0, -max_shift), out.height))
    im.paste(out, (0, box[1]))
    return im


def region_jitter(im, x0, y0, x1, y1, amp, seed=5):
    rnd = random.Random(seed)
    box = (int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height))
    patch = im.crop(box)
    im.paste((0, 0, 0), box)
    im.paste(patch, (box[0] + rnd.randint(-amp, amp), box[1] + rnd.randint(-amp, amp)))
    return im


def dust(d, nx, ny, r, alpha=90):
    x, y = _px(d._image, nx, ny)
    for i in range(3):
        rr = r * (1 - i * 0.25)
        d.ellipse([x - rr + i * 6, y - rr * 0.8 + i * 4, x + rr + i * 6, y + rr * 0.8 + i * 4],
                  fill=(170, 180, 170, max(0, alpha - i * 26)))


# ------------------------------------------------------------- recipes -----

def rec_p1_02(m):
    """Fake news: a manchete SE REESCREVE (glitch) e fixa com brilho."""
    f1 = zoom_pan(m, 0.47, 0.45, 1.07)
    f1 = glitch_band(f1, 0.27, 0.66, 12, 16, seed=11)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    line(d, (0.60, 0.30), (0.60, 0.60), GREEN, 4, 90)
    composite(f1, ov)
    f2 = zoom_pan(m, 0.47, 0.45, 1.11)
    f2 = glitch_band(f2, 0.26, 0.68, 16, 30, seed=29)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    for x, a in ((0.55, 120), (0.63, 80), (0.35, 70)):
        line(d, (x, 0.24), (x, 0.70), GREEN, 3, a)
    composite(f2, ov)
    f3 = zoom_pan(m, 0.47, 0.45, 1.14)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.47, 0.45, int(f3.width * 0.20), GREEN, 60)
    sparkle(d, 0.60, 0.30, 16, GREEN)
    sparkle(d, 0.36, 0.56, 12, GREEN)
    return [m, f1, f2, f3]


def rec_p1_03(m):
    """Reptilianos: brinde (mugs se aproximam + vapor + flash no contato)."""
    f1 = zoom_pan(m, 0.49, 0.42, 1.07)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    steam_swirl(d, 0.455, 0.36, 90, 12, (210, 255, 225, 255), 130, 5)
    steam_swirl(d, 0.520, 0.35, 80, 11, (210, 255, 225, 255), 130, 5)
    sparkle(d, 0.487, 0.40, 10, GREEN, 190)
    f1 = composite(f1, ov)
    f2 = rotate_around(zoom_pan(m, 0.49, 0.42, 1.10), 0.49, 0.50, -1.7)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    steam_swirl(d, 0.452, 0.34, 120, 14, (210, 255, 225, 255), 150, 6)
    steam_swirl(d, 0.524, 0.33, 115, 13, (210, 255, 225, 255), 150, 6)
    burst_lines(d, 0.487, 0.395, 8, 30, 6, GREEN, 200, 5)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.49, 0.42, 1.05)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.487, 0.395, 70, (190, 255, 210, 255), 130)
    ring(d, 0.487, 0.395, 46, GREEN, 5, 150)
    steam_swirl(d, 0.452, 0.33, 140, 15, (210, 255, 225, 255), 160, 6)
    steam_swirl(d, 0.526, 0.32, 135, 14, (210, 255, 225, 255), 160, 6)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p1_04(m):
    """Informante: a pasta brilha (roxo) e recebe o carimbo na entrega."""
    f1 = zoom_pan(m, 0.50, 0.52, 1.08)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.50, 0.485, 60, PURPLE, 110)
    sparkle(d, 0.47, 0.45, 10, PURPLE, 190)
    sparkle(d, 0.53, 0.52, 8, PURPLE, 170)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.50, 0.52, 1.12)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.50, 0.485, 90, PURPLE, 140)
    line(d, (0.44, 0.44), (0.56, 0.55), WHITE, 10, 70)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.50, 0.52, 1.06)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    ring(d, 0.565, 0.565, 34, RED, 7, 210)
    line(d, (0.545, 0.552), (0.585, 0.552), RED, 5, 210)
    line(d, (0.547, 0.566), (0.583, 0.566), RED, 5, 210)
    ring(d, 0.565, 0.565, 52, WHITE, 4, 90)
    dust(d, 0.60, 0.62, 22, 80)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p1_05(m):
    """Teorias: o alfinete cai, a linha estica, o quadro vibra."""
    f1 = zoom_pan(m, 0.55, 0.42, 1.07)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    line(d, (0.555, 0.40), (0.66, 0.22), RED, 5, 170)
    d.ellipse([int(0.555 * f1.width) - 7, int(0.40 * f1.height) - 7,
               int(0.555 * f1.width) + 7, int(0.40 * f1.height) + 7], fill=GOLD)
    d.ellipse([int(0.552 * f1.width) - 4, int(0.345 * f1.height) - 4,
               int(0.552 * f1.width) + 4, int(0.345 * f1.height) + 4], fill=(212, 175, 55, 120))
    d.ellipse([int(0.549 * f1.width) - 3, int(0.295 * f1.height) - 3,
               int(0.549 * f1.width) + 3, int(0.295 * f1.height) + 3], fill=(212, 175, 55, 70))
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.55, 0.42, 1.10)
    f2 = region_jitter(f2, 0.60, 0.15, 0.71, 0.30, 4, seed=8)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    line(d, (0.555, 0.415), (0.66, 0.22), RED, 8, 200)
    d.ellipse([int(0.555 * f2.width) - 8, int(0.415 * f2.height) - 8,
               int(0.555 * f2.width) + 8, int(0.415 * f2.height) + 8], fill=GOLD)
    ring(d, 0.555, 0.415, 26, GOLD, 3, 120)
    ring(d, 0.555, 0.415, 38, GOLD, 3, 70)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.55, 0.42, 1.05)
    f3 = region_jitter(f3, 0.235, 0.295, 0.315, 0.395, 3, seed=14)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    line(d, (0.555, 0.415), (0.66, 0.22), RED, 6, 160)
    for t in (0.25, 0.55, 0.85):
        x = 0.555 + (0.66 - 0.555) * t
        y = 0.415 + (0.22 - 0.415) * t
        d.ellipse([int(x * f3.width) - 5, int(y * f3.height) - 5,
                   int(x * f3.width) + 5, int(y * f3.height) + 5], fill=GOLD)
    sparkle(d, 0.545, 0.39, 11, GOLD)
    sparkle(d, 0.585, 0.44, 8, GOLD)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def _zmap(px, py, cx, cy, s):
    """Mapeia um ponto do espaço master para o espaço zoom_pan(s, c)."""
    return cx + (px - cx) * s, cy + (py - cy) * s


def rec_p1_06(m):
    """Lavar cérebros pop: o dial gira, a espiral do olho pulsa, notas sobem."""
    E = (0.234, 0.410)   # olho-espiral (medido)
    D = (0.565, 0.520)   # dial
    C = (0.40, 0.44)     # centro do zoom

    f1 = zoom_pan(m, *C, 1.08)
    e1 = _zmap(*E, *C, 1.08)
    d1 = _zmap(*D, *C, 1.08)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    arc_spiral(d, e1[0], e1[1], 66, PURPLE, 150, 6, rot=0.4)
    line(d, d1, e1, PURPLE, 4, 90)
    note(d, 0.42, 0.30, 16, PURPLE)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, *C, 1.11)
    e2 = _zmap(*E, *C, 1.11)
    d2 = _zmap(*D, *C, 1.11)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    arc_spiral(d, e2[0], e2[1], 74, PURPLE, 190, 7, rot=1.6)
    ring(d, e2[0], e2[1], 46, PURPLE, 4, 110)
    radial_glow(d, d2[0], d2[1], 46, PURPLE, 110)
    note(d, 0.46, 0.24, 18, PURPLE)
    note(d, 0.35, 0.42, 14, PURPLE, 180)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, *C, 1.06)
    e3 = _zmap(*E, *C, 1.06)
    d3 = _zmap(*D, *C, 1.06)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    arc_spiral(d, e3[0], e3[1], 82, PURPLE, 210, 8, rot=2.8)
    ring(d, e3[0], e3[1], 52, PURPLE, 4, 130)
    ring(d, e3[0], e3[1], 30, (255, 255, 255, 255), 3, 90)
    for t in (0.35, 0.65, 0.92):
        x = d3[0] + (e3[0] - d3[0]) * t
        y = d3[1] + (e3[1] - d3[1]) * t - 0.03 * (1 - t)
        note(d, x, y, int(14 + 8 * t), PURPLE, int(170 + 60 * t))
    sparkle(d, e3[0], e3[1] - 0.06, 13, PURPLE)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p1_07(m):
    """Guerra por lucro: a mira bate no mapa e fumaça de cifrão sobe."""
    f1 = zoom_pan(m, 0.42, 0.68, 1.09)
    f1 = region_jitter(f1, 0.335, 0.42, 0.455, 0.72, 3, seed=4)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    ring(d, 0.395, 0.72, 36, RED, 5, 190)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.42, 0.68, 1.13)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    ring(d, 0.395, 0.72, 52, RED, 6, 210)
    ring(d, 0.395, 0.72, 66, WHITE, 4, 110)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.42, 0.68, 1.07)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    dollar_puff(d, 0.405, 0.60, 26, 200)
    dollar_puff(d, 0.445, 0.52, 22, 170)
    dollar_puff(d, 0.415, 0.44, 18, 140)
    ring(d, 0.395, 0.72, 40, RED, 5, 120)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p1_08(m):
    """Wi-Fi: o botão dispara as ondas e cérebros surfam nelas."""
    f1 = zoom_pan(m, 0.58, 0.45, 1.06)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    cx, cy = 0.63, 0.44
    for rr in (0.30, 0.37):
        d.arc([int((cx - rr) * f1.width), int((cy - rr * 0.72) * f1.height),
               int((cx + rr) * f1.width), int((cy + rr * 0.72) * f1.height)],
              200, 340, fill=(57, 255, 156, 110), width=7)
    d.ellipse([int(0.80 * f1.width) - 12, int(0.30 * f1.height) - 9,
               int(0.80 * f1.width) + 12, int(0.30 * f1.height) + 9], fill=PINK)
    d.ellipse([int(0.42 * f1.width) - 11, int(0.60 * f1.height) - 8,
               int(0.42 * f1.width) + 11, int(0.60 * f1.height) + 8], fill=PINK)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.58, 0.45, 1.09)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    cx, cy = 0.63, 0.44
    for rr in (0.30, 0.38, 0.46):
        d.arc([int((cx - rr) * f2.width), int((cy - rr * 0.72) * f2.height),
               int((cx + rr) * f2.width), int((cy + rr * 0.72) * f2.height)],
              200, 340, fill=(57, 255, 156, 130), width=7)
    radial_glow(d, 0.63, 0.44, 120, GREEN, 70)
    for (bx, by) in ((0.84, 0.26), (0.38, 0.55), (0.74, 0.66)):
        d.ellipse([int(bx * f2.width) - 13, int(by * f2.height) - 10,
                   int(bx * f2.width) + 13, int(by * f2.height) + 10], fill=PINK)
    ring(d, 0.10, 0.78, 34, GREEN, 5, 150)
    ring(d, 0.10, 0.78, 52, GREEN, 4, 90)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.58, 0.45, 1.04)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.63, 0.44, 170, GREEN, 90)
    ring(d, 0.10, 0.78, 44, (255, 93, 93, 255), 6, 190)
    sparkle(d, 0.10, 0.78, 12, WHITE, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_03(m):
    """Meio-termo: o muro BALANÇA de um lado e de outro; a rachadura pisca."""
    f1 = rotate_around(m, 0.50, 0.95, 1.9)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    dust(d, 0.68, 0.88, 26, 100)
    dust(d, 0.72, 0.83, 18, 70)
    f1 = composite(f1, ov)
    f2 = rotate_around(m, 0.50, 0.95, -1.9)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    dust(d, 0.32, 0.88, 26, 100)
    dust(d, 0.28, 0.83, 18, 70)
    f2 = composite(f2, ov)
    f3 = rotate_around(m, 0.50, 0.95, 0.9)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    pts = []
    for i in range(14):
        t = i / 13.0
        pts.append((0.512 - 0.012 * math.sin(t * 5.0), 0.44 + 0.34 * t))
    for i in range(len(pts) - 1):
        line(d, pts[i], pts[i + 1], GREEN, 6, 200)
    sparkle(d, 0.512, 0.42, 13, GREEN)
    sparkle(d, 0.498, 0.60, 9, GREEN, 170)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]



def _bezier(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def rec_p3_01(m):
    """Ratanabá: a broca vibra, a caverna de ouro pulsa, brilho sobe."""
    f1 = zoom_pan(m, 0.55, 0.60, 1.06)
    f1 = region_jitter(f1, 0.50, 0.25, 0.75, 0.65, 3, seed=3)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.65, 0.80, 110, (255, 170, 60, 255), 70)
    sparkle(d, 0.72, 0.82, 12, (255, 220, 120, 255))
    dust(d, 0.60, 0.60, 20, 90)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.55, 0.60, 1.09)
    f2 = region_jitter(f2, 0.50, 0.25, 0.75, 0.65, 4, seed=7)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.65, 0.80, 150, (255, 170, 60, 255), 95)
    sparkle(d, 0.68, 0.74, 14, (255, 220, 120, 255))
    sparkle(d, 0.76, 0.86, 10, (255, 220, 120, 255))
    dust(d, 0.62, 0.58, 24, 100)
    dust(d, 0.57, 0.66, 16, 70)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.55, 0.60, 1.04)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.65, 0.80, 180, (255, 190, 80, 255), 120)
    for (sx, sy) in ((0.66, 0.70), (0.74, 0.78), (0.70, 0.88)):
        sparkle(d, sx, sy, 11, (255, 230, 150, 255))
    ring(d, 0.65, 0.80, 120, (255, 170, 60, 255), 4, 60)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_02(m):
    """E.T. de Varginha: aperto de mão com faísca, raio do OVNI pulsa."""
    f1 = zoom_pan(m, 0.50, 0.55, 1.06)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.48, 90, BLUE, 70)
    line(d, (0.60, 0.13), (0.46, 0.40), (170, 230, 255, 255), 8, 90)
    sparkle(d, 0.54, 0.62, 10, (190, 240, 255, 255))
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.50, 0.55, 1.09)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.48, 120, BLUE, 95)
    line(d, (0.60, 0.12), (0.455, 0.40), (190, 240, 255, 255), 12, 130)
    burst_lines(d, 0.545, 0.615, 10, 30, 8, (200, 245, 255, 255), 200, 4)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.50, 0.55, 1.04)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.48, 100, BLUE, 80)
    ring(d, 0.545, 0.615, 26, (190, 240, 255, 255), 5, 140)
    sparkle(d, 0.50, 0.55, 11, (210, 245, 255, 255))
    sparkle(d, 0.58, 0.68, 8, (210, 245, 255, 255))
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_06(m):
    """Túnel São Tomé→Machu Picchu: o trem viaja, o ouro pulsa."""
    T0, T1, T2 = (0.17, 0.52), (0.45, 0.82), (0.85, 0.52)
    f1 = zoom_pan(m, 0.50, 0.62, 1.05)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    for t in (0.25, 0.55):
        x, y = _bezier(T0, T1, T2, t)
        d.ellipse([int(x * f1.width) - 6, int(y * f1.height) - 6,
                   int(x * f1.width) + 6, int(y * f1.height) + 6], fill=GOLD)
    radial_glow(d, 0.45, 0.72, 100, GOLD, 50)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.50, 0.62, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    for t in (0.35, 0.68):
        x, y = _bezier(T0, T1, T2, t)
        d.ellipse([int(x * f2.width) - 7, int(y * f2.height) - 7,
                   int(x * f2.width) + 7, int(y * f2.height) + 7], fill=GOLD)
    radial_glow(d, 0.50, 0.70, 130, GOLD, 70)
    dust(d, 0.62, 0.66, 18, 80)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.50, 0.62, 1.03)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    for t in (0.15, 0.45, 0.80):
        x, y = _bezier(T0, T1, T2, t)
        d.ellipse([int(x * f3.width) - 6, int(y * f3.height) - 6,
                   int(x * f3.width) + 6, int(y * f3.height) + 6], fill=GOLD)
    for (sx, sy) in ((0.30, 0.62), (0.62, 0.72), (0.80, 0.58)):
        sparkle(d, sx, sy, 10, (255, 220, 120, 255))
    radial_glow(d, 0.50, 0.70, 150, GOLD, 60)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_04(m):
    """Cidade ocultista: a geometria pulsa, o olho-ave vigia, a catedral brilha."""
    f1 = zoom_pan(m, 0.50, 0.50, 1.05)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.55, 0.42, 90, GREEN, 60)
    radial_glow(d, 0.78, 0.18, 60, (140, 255, 160, 255), 80)
    arc_line(d, 0.50, 0.55, 0.40 * f1.width, 200, 320, GREEN, 4, 90)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.50, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.55, 0.42, 120, GREEN, 85)
    radial_glow(d, 0.78, 0.18, 80, (140, 255, 160, 255), 110)
    ring(d, 0.78, 0.18, 44, (170, 255, 190, 255), 4, 130)
    arc_line(d, 0.42, 0.55, 0.34 * f2.width, 210, 330, GREEN, 4, 110)
    arc_line(d, 0.62, 0.52, 0.30 * f2.width, 190, 320, GREEN, 3, 80)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.50, 0.50, 1.03)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.55, 0.42, 150, GREEN, 100)
    sparkle(d, 0.78, 0.14, 12, (190, 255, 205, 255))
    sparkle(d, 0.30, 0.48, 9, (190, 255, 205, 255))
    sparkle(d, 0.70, 0.60, 8, (190, 255, 205, 255))
    ring(d, 0.55, 0.42, 110, GREEN, 4, 90)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_05(m):
    """Milagre na TV: o facho varre, o confete explode, o chão pisca."""
    f1 = zoom_pan(m, 0.55, 0.50, 1.05)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    line(d, (0.445, 0.14), (0.56, 0.86), (255, 226, 130, 255), 10, 70)
    radial_glow(d, 0.62, 0.83, 90, GOLD, 60)
    for (sx, sy) in ((0.52, 0.35), (0.58, 0.52), (0.66, 0.40)):
        sparkle(d, sx, sy, 8, (255, 236, 170, 255), 200)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.55, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    line(d, (0.445, 0.14), (0.68, 0.84), (255, 236, 160, 255), 12, 100)
    line(d, (0.445, 0.14), (0.50, 0.82), (255, 226, 130, 255), 8, 60)
    confetti(d, 0.60, 0.55, 120, 10, seed=4)
    radial_glow(d, 0.62, 0.83, 120, GOLD, 90)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.55, 0.50, 1.03)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    line(d, (0.445, 0.14), (0.60, 0.85), (255, 236, 160, 255), 12, 90)
    radial_glow(d, 0.62, 0.83, 150, GOLD, 110)
    sparkle(d, 0.55, 0.30, 12, (255, 240, 190, 255))
    sparkle(d, 0.68, 0.50, 9, (255, 240, 190, 255))
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_10(m):
    """Arrebatamento holográfico: a grade LED pisca, o raio pulsa, os halos sobem."""
    def led_grid(im, a):
        ov = overlay(im)
        d = ImageDraw.Draw(ov)
        for x in range(0, im.width, 26):
            d.line([(x, 0), (x, int(im.height * 0.62))], fill=(BLUE[0], BLUE[1], BLUE[2], a), width=2)
        for y in range(0, int(im.height * 0.62), 26):
            d.line([(0, y), (im.width, y)], fill=(BLUE[0], BLUE[1], BLUE[2], a), width=2)
        return composite(im, ov)
    f1 = led_grid(zoom_pan(m, 0.50, 0.50, 1.05), 14)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    line(d, (0.42, 0.78), (0.52, 0.02), (170, 230, 255, 255), 10, 100)
    line(d, (0.42, 0.78), (0.60, 0.02), (170, 230, 255, 255), 8, 80)
    ring(d, 0.63, 0.47, 20, (200, 240, 255, 255), 4, 140)
    ring(d, 0.70, 0.52, 20, (200, 240, 255, 255), 4, 110)
    f1 = composite(f1, ov)
    f2 = led_grid(zoom_pan(m, 0.50, 0.50, 1.08), 22)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    line(d, (0.42, 0.78), (0.50, 0.02), (200, 240, 255, 255), 14, 140)
    line(d, (0.42, 0.78), (0.62, 0.02), (200, 240, 255, 255), 10, 110)
    radial_glow(d, 0.56, 0.40, 120, BLUE, 70)
    ring(d, 0.63, 0.44, 24, (210, 245, 255, 255), 5, 170)
    ring(d, 0.70, 0.49, 24, (210, 245, 255, 255), 5, 140)
    ring(d, 0.73, 0.66, 20, (210, 245, 255, 255), 4, 110)
    f2 = composite(f2, ov)
    f3 = led_grid(zoom_pan(m, 0.50, 0.50, 1.03), 10)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    line(d, (0.42, 0.78), (0.54, 0.02), (190, 235, 255, 255), 12, 110)
    radial_glow(d, 0.58, 0.42, 150, BLUE, 80)
    sparkle(d, 0.63, 0.42, 10, (220, 248, 255, 255))
    sparkle(d, 0.71, 0.47, 8, (220, 248, 255, 255))
    ring(d, 0.40, 0.86, 26, (255, 120, 110, 255), 5, 150)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p5_04(m):
    """Skynet: o olho vermelho pulsa, as teclas digitam, os cabos brilham."""
    f1 = zoom_pan(m, 0.47, 0.45, 1.05)
    f1 = region_jitter(f1, 0.36, 0.46, 0.47, 0.56, 3, seed=5)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.47, 0.27, 80, (255, 60, 60, 255), 70)
    radial_glow(d, 0.30, 0.55, 60, PURPLE, 50)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.47, 0.45, 1.08)
    f2 = region_jitter(f2, 0.36, 0.46, 0.47, 0.56, 4, seed=9)
    f2 = region_jitter(f2, 0.48, 0.46, 0.60, 0.56, 3, seed=11)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.47, 0.27, 120, (255, 60, 60, 255), 100)
    ring(d, 0.47, 0.27, 70, (255, 90, 90, 255), 4, 90)
    radial_glow(d, 0.30, 0.55, 80, PURPLE, 70)
    radial_glow(d, 0.64, 0.48, 70, PURPLE, 60)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.47, 0.45, 1.03)
    f3 = region_jitter(f3, 0.36, 0.46, 0.60, 0.56, 3, seed=13)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.47, 0.27, 150, (255, 70, 70, 255), 120)
    sparkle(d, 0.47, 0.18, 12, (255, 150, 150, 255))
    radial_glow(d, 0.66, 0.72, 70, (240, 220, 150, 255), 50)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p5_07(m):
    """Pombos drones: o rotor gira, o olho de câmera pisca, o controle responde."""
    f1 = zoom_pan(m, 0.45, 0.45, 1.05)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.52, 0.19, 60, (255, 80, 80, 255), 70)
    arc_spiral(d, 0.52, 0.10, 26, GREEN, 140, 5, rot=0.2)
    line(d, (0.44, 0.16), (0.42, 0.14), (220, 230, 235, 255), 4, 110)
    line(d, (0.45, 0.22), (0.425, 0.23), (220, 230, 235, 255), 4, 90)
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.45, 0.45, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.52, 0.19, 80, (255, 80, 80, 255), 100)
    arc_spiral(d, 0.52, 0.10, 30, GREEN, 170, 6, rot=1.6)
    ring(d, 0.52, 0.19, 40, (255, 120, 120, 255), 3, 80)
    line(d, (0.45, 0.16), (0.415, 0.13), (230, 240, 245, 255), 5, 140)
    line(d, (0.46, 0.23), (0.42, 0.25), (230, 240, 245, 255), 5, 120)
    ring(d, 0.285, 0.72, 14, GREEN, 4, 150)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.45, 0.45, 1.03)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.52, 0.19, 60, (255, 80, 80, 255), 70)
    arc_spiral(d, 0.52, 0.10, 26, GREEN, 150, 5, rot=2.9)
    sparkle(d, 0.52, 0.13, 10, (190, 255, 205, 255))
    ring(d, 0.285, 0.72, 20, GREEN, 4, 110)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p5_10(m):
    """O chip: a igluarota do chip pulsa, faíscas sobem, o robô acompanha."""
    f1 = zoom_pan(m, 0.42, 0.45, 1.05)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.40, 0.30, 70, PURPLE, 80)
    sparkle(d, 0.40, 0.20, 12, (215, 180, 255, 255))
    f1 = composite(f1, ov)
    f2 = zoom_pan(m, 0.42, 0.45, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.40, 0.30, 100, PURPLE, 110)
    ring(d, 0.40, 0.30, 46, (215, 180, 255, 255), 4, 130)
    sparkle(d, 0.36, 0.22, 11, (225, 195, 255, 255))
    sparkle(d, 0.45, 0.16, 9, (225, 195, 255, 255))
    ring(d, 0.53, 0.47, 16, (190, 230, 255, 255), 4, 130)
    f2 = composite(f2, ov)
    f3 = zoom_pan(m, 0.42, 0.45, 1.03)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.40, 0.30, 130, PURPLE, 130)
    for (sx, sy) in ((0.37, 0.24), (0.44, 0.18), (0.40, 0.12)):
        sparkle(d, sx, sy, 10, (230, 205, 255, 255))
    line(d, (0.34, 0.36), (0.46, 0.33), (230, 210, 255, 255), 5, 120)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p1_09(m):
    """Manipular governantes fantoches: boneco sapateia no palco, holofote roxo pulsa, cordas vibram."""
    f1 = zoom_pan(m, 0.50, 0.50, 1.04)
    f1 = region_jitter(f1, 0.35, 0.38, 0.53, 0.78, 4, seed=5)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.40, 90, PURPLE, 80)
    sparkle(d, 0.62, 0.30, 10, WHITE, 220)
    line(d, (0.42, 0.28), (0.43, 0.42), (240, 230, 255, 255), 2, 160)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.50, 1.07)
    f2 = region_jitter(f2, 0.35, 0.38, 0.53, 0.78, 6, seed=8)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.40, 130, PURPLE, 110)
    radial_glow(d, 0.68, 0.20, 70, PURPLE, 60)
    sparkle(d, 0.62, 0.30, 14, WHITE, 255)
    sparkle(d, 0.46, 0.72, 8, (255, 220, 120, 255), 190)
    line(d, (0.41, 0.27), (0.44, 0.44), (240, 230, 255, 255), 3, 200)
    ring(d, 0.46, 0.76, 24, PURPLE, 3, 100)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.50, 1.02)
    f3 = region_jitter(f3, 0.35, 0.38, 0.53, 0.78, 2, seed=12)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.40, 100, PURPLE, 70)
    sparkle(d, 0.44, 0.48, 9, (220, 200, 255, 255), 180)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p1_10(m):
    """Controle do clima: radar do globo pisca ciano, raio estala, faíscas na alavanca."""
    f1 = zoom_pan(m, 0.50, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.28, 0.38, 90, BLUE, 90)
    ring(d, 0.28, 0.38, 60, BLUE, 4, 150)
    sparkle(d, 0.35, 0.35, 12, GOLD, 220)
    line(d, (0.78, 0.45), (0.75, 0.43), (255, 255, 200, 255), 3, 140)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.28, 0.38, 140, BLUE, 130)
    radial_glow(d, 0.21, 0.30, 60, GOLD, 110)
    ring(d, 0.28, 0.38, 100, BLUE, 5, 180)
    line(d, (0.34, 0.36), (0.35, 0.42), (255, 255, 100, 255), 4, 240)
    line(d, (0.35, 0.42), (0.33, 0.48), (255, 255, 100, 255), 3, 240)
    sparkle(d, 0.77, 0.52, 14, GOLD, 240)
    sparkle(d, 0.81, 0.50, 9, WHITE, 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.28, 0.38, 80, BLUE, 70)
    sparkle(d, 0.28, 0.38, 10, WHITE, 180)
    sparkle(d, 0.76, 0.54, 8, GOLD, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_01(m):
    """Comprar o voto do tio: sol brilha na varanda, fumacinha do churrasco sobe, santinho brilha."""
    f1 = zoom_pan(m, 0.50, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.62, 0.12, 60, GOLD, 80)
    radial_glow(d, 0.52, 0.55, 40, (230, 230, 220, 255), 40)
    sparkle(d, 0.64, 0.45, 11, GREEN, 200)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.50, 1.07)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.62, 0.12, 90, GOLD, 110)
    burst_lines(d, 0.62, 0.12, 40, 75, n=8, color=GOLD, alpha=160, width=4)
    radial_glow(d, 0.52, 0.52, 55, (230, 230, 220, 255), 55)
    sparkle(d, 0.64, 0.45, 14, GREEN, 240)
    sparkle(d, 0.34, 0.60, 9, (200, 240, 255, 255), 180)
    sparkle(d, 0.47, 0.45, 8, GOLD, 170)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.62, 0.12, 50, GOLD, 60)
    radial_glow(d, 0.52, 0.50, 45, (230, 230, 220, 255), 35)
    sparkle(d, 0.64, 0.45, 9, GREEN, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_02(m):
    """Pesquisa encomendada: vara aponta pro gráfico de pizza, fatia verde irradia, estagiários tremem."""
    f1 = zoom_pan(m, 0.55, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.68, 0.46, 70, GREEN, 90)
    sparkle(d, 0.66, 0.42, 12, GREEN, 220)
    sparkle(d, 0.38, 0.35, 8, WHITE, 180)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.55, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.68, 0.46, 120, GREEN, 130)
    ring(d, 0.68, 0.46, 65, GREEN, 4, 160)
    sparkle(d, 0.66, 0.42, 16, GREEN, 255)
    sparkle(d, 0.72, 0.50, 10, GOLD, 200)
    sparkle(d, 0.38, 0.35, 12, WHITE, 230)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.55, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.68, 0.46, 80, GREEN, 70)
    sparkle(d, 0.66, 0.42, 9, GREEN, 170)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_04(m):
    """Emenda do trator de ouro: trator reluz, fumaça sai do escapamento, prefeito acena com auréola dourada."""
    f1 = zoom_pan(m, 0.50, 0.45, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.48, 0.60, 80, GOLD, 80)
    radial_glow(d, 0.39, 0.20, 35, (220, 220, 210, 255), 50)
    sparkle(d, 0.40, 0.62, 11, GOLD, 210)
    sparkle(d, 0.56, 0.64, 10, GOLD, 200)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.45, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.48, 0.60, 130, GOLD, 120)
    radial_glow(d, 0.53, 0.30, 90, GOLD, 100)
    burst_lines(d, 0.53, 0.30, 50, 95, n=8, color=GOLD, alpha=180, width=4)
    radial_glow(d, 0.39, 0.16, 50, (220, 220, 210, 255), 65)
    sparkle(d, 0.40, 0.62, 15, WHITE, 240)
    sparkle(d, 0.56, 0.64, 14, WHITE, 240)
    sparkle(d, 0.48, 0.48, 12, GOLD, 220)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.45, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.48, 0.60, 90, GOLD, 70)
    radial_glow(d, 0.39, 0.22, 40, (220, 220, 210, 255), 40)
    sparkle(d, 0.48, 0.55, 9, GOLD, 170)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_05(m):
    """Plenário de robôs: botões verdes são apertados em sequência, antenas emitem arcos de sinal."""
    f1 = zoom_pan(m, 0.50, 0.55, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.28, 0.68, 60, GREEN, 100)
    ring(d, 0.28, 0.68, 30, GREEN, 4, 180)
    sparkle(d, 0.23, 0.30, 10, GREEN, 210)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.55, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.28, 0.68, 80, GREEN, 90)
    radial_glow(d, 0.51, 0.68, 80, GREEN, 120)
    radial_glow(d, 0.70, 0.68, 80, GREEN, 110)
    ring(d, 0.51, 0.68, 32, GREEN, 5, 200)
    ring(d, 0.70, 0.68, 32, GREEN, 5, 200)
    arc_line(d, 0.51, 0.28, 25, 200, 340, GREEN, 4, 180)
    arc_line(d, 0.79, 0.21, 25, 200, 340, GREEN, 4, 180)
    sparkle(d, 0.51, 0.28, 12, WHITE, 240)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.55, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.51, 0.68, 50, GREEN, 60)
    arc_line(d, 0.51, 0.28, 35, 210, 330, GREEN, 3, 120)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_06(m):
    """Cabo eleitoral com megafone: ondas sonoras estouram do megafone, panfletos giram pelo ar."""
    f1 = zoom_pan(m, 0.50, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.35, 0.44, 70, (255, 180, 50, 255), 90)
    arc_line(d, 0.35, 0.44, 60, 110, 250, (255, 210, 80, 255), 5, 180)
    sparkle(d, 0.51, 0.65, 10, PURPLE, 200)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.35, 0.44, 120, (255, 160, 40, 255), 130)
    arc_line(d, 0.35, 0.44, 75, 100, 260, (255, 220, 80, 255), 6, 220)
    arc_line(d, 0.35, 0.44, 110, 100, 260, (255, 240, 120, 255), 5, 170)
    sparkle(d, 0.51, 0.65, 14, PURPLE, 240)
    sparkle(d, 0.72, 0.25, 10, GOLD, 200)
    sparkle(d, 0.78, 0.35, 8, GREEN, 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.35, 0.44, 80, (255, 180, 50, 255), 70)
    arc_line(d, 0.35, 0.44, 140, 105, 255, (255, 230, 90, 255), 4, 120)
    sparkle(d, 0.51, 0.65, 9, PURPLE, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_07(m):
    """Comício em dupla: canhões de luz cruzam o palco, confetes chovem, violas brilham."""
    f1 = zoom_pan(m, 0.50, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.28, 0.15, 80, GOLD, 80)
    radial_glow(d, 0.72, 0.15, 80, (240, 80, 180, 255), 80)
    sparkle(d, 0.38, 0.58, 11, GOLD, 200)
    sparkle(d, 0.62, 0.58, 11, GOLD, 200)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.28, 0.15, 120, GOLD, 110)
    radial_glow(d, 0.72, 0.15, 120, (240, 80, 180, 255), 110)
    radial_glow(d, 0.50, 0.48, 60, WHITE, 90)
    burst_lines(d, 0.28, 0.15, 30, 90, n=6, color=GOLD, alpha=150, width=4)
    burst_lines(d, 0.72, 0.15, 30, 90, n=6, color=(240, 80, 180, 255), alpha=150, width=4)
    sparkle(d, 0.38, 0.58, 15, WHITE, 240)
    sparkle(d, 0.62, 0.58, 15, WHITE, 240)
    sparkle(d, 0.50, 0.48, 12, (200, 240, 255, 255), 220)
    for cx, cy in [(0.20, 0.35), (0.35, 0.25), (0.50, 0.18), (0.65, 0.28), (0.80, 0.38)]:
        sparkle(d, cx, cy, 7, GOLD, 190)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.28, 0.15, 70, GOLD, 60)
    radial_glow(d, 0.72, 0.15, 70, (240, 80, 180, 255), 60)
    sparkle(d, 0.38, 0.58, 8, GOLD, 160)
    sparkle(d, 0.62, 0.58, 8, GOLD, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_08(m):
    """Constituição do Zap: pena verde escreve furiosamente, tiques verdes brilham no pergaminho, óculos reluzem."""
    f1 = zoom_pan(m, 0.50, 0.45, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.35, 70, GREEN, 90)
    sparkle(d, 0.45, 0.35, 12, GREEN, 220)
    sparkle(d, 0.20, 0.75, 10, GREEN, 180)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.45, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.35, 120, GREEN, 130)
    burst_lines(d, 0.45, 0.35, 30, 80, n=6, color=GREEN, alpha=160, width=4)
    sparkle(d, 0.45, 0.35, 16, WHITE, 240)
    sparkle(d, 0.60, 0.27, 9, WHITE, 210)
    sparkle(d, 0.15, 0.85, 12, GREEN, 220)
    sparkle(d, 0.30, 0.65, 11, GREEN, 200)
    sparkle(d, 0.68, 0.58, 10, GREEN, 190)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.45, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.45, 0.35, 80, GREEN, 70)
    sparkle(d, 0.45, 0.35, 9, GREEN, 170)
    sparkle(d, 0.40, 0.55, 9, GREEN, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_09(m):
    """Sósia na urna: sósia sai na ponta dos pés, suor escorre, luz amarela da cabine pulsa, crachá brilha."""
    f1 = zoom_pan(m, 0.55, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.72, 0.20, 80, GOLD, 90)
    sparkle(d, 0.55, 0.60, 10, WHITE, 200)
    sparkle(d, 0.57, 0.28, 7, (180, 230, 255, 255), 180)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.55, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.72, 0.20, 120, GOLD, 120)
    radial_glow(d, 0.62, 0.45, 70, PURPLE, 80)
    sparkle(d, 0.55, 0.60, 14, GOLD, 240)
    sparkle(d, 0.57, 0.28, 9, (180, 230, 255, 255), 230)
    ring(d, 0.75, 0.52, 35, GOLD, 4, 150)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.55, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.72, 0.20, 70, GOLD, 60)
    sparkle(d, 0.55, 0.60, 8, WHITE, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p2_10(m):
    """Democracia Relativa™: martelo desce com trovão cômico, balança oscila 50/50, confetes de festa chovem."""
    f1 = zoom_pan(m, 0.50, 0.45, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.44, 0.22, 90, GOLD, 90)
    sparkle(d, 0.44, 0.22, 12, GOLD, 220)
    sparkle(d, 0.60, 0.55, 10, GOLD, 200)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.45, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.44, 0.22, 140, GOLD, 130)
    burst_lines(d, 0.44, 0.22, 40, 100, n=8, color=GOLD, alpha=180, width=5)
    sparkle(d, 0.44, 0.22, 18, WHITE, 255)
    sparkle(d, 0.60, 0.55, 14, WHITE, 230)
    radial_glow(d, 0.50, 0.08, 60, BLUE, 80)
    for cx, cy in [(0.25, 0.20), (0.35, 0.35), (0.65, 0.25), (0.75, 0.40), (0.50, 0.60)]:
        sparkle(d, cx, cy, 7, GOLD, 190)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.45, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.44, 0.22, 80, GOLD, 70)
    sparkle(d, 0.44, 0.22, 9, GOLD, 170)
    sparkle(d, 0.60, 0.55, 8, GOLD, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_03(m):
    """Indústria da Multa: flash estourado do radar cega a pista, folhagem treme, velocímetro estoura."""
    f1 = zoom_pan(m, 0.50, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.55, 0.49, 80, GOLD, 110)
    sparkle(d, 0.55, 0.49, 14, WHITE, 240)
    line(d, (0.58, 0.49), (0.80, 0.53), (255, 250, 200, 255), 4, 160)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.55, 0.49, 150, GOLD, 150)
    burst_lines(d, 0.55, 0.49, 30, 110, n=10, color=WHITE, alpha=230, width=5)
    sparkle(d, 0.55, 0.49, 20, WHITE, 255)
    line(d, (0.56, 0.49), (0.88, 0.54), (255, 255, 220, 255), 8, 220)
    sparkle(d, 0.90, 0.55, 12, (255, 80, 80, 255), 220)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.55, 0.49, 90, GOLD, 80)
    sparkle(d, 0.55, 0.49, 10, WHITE, 180)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_04(m):
    """O Chupa-Cabra: criatura toma suco pelo canudo, olhos vermelhos brilham, lanterna do fazendeiro treme."""
    f1 = zoom_pan(m, 0.45, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.38, 0.33, 40, (255, 50, 50, 255), 90)
    sparkle(d, 0.35, 0.33, 8, (255, 100, 100, 255), 200)
    radial_glow(d, 0.70, 0.56, 50, (230, 255, 150, 255), 60)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.45, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.38, 0.33, 70, (255, 40, 40, 255), 130)
    sparkle(d, 0.35, 0.33, 12, (255, 150, 150, 255), 240)
    sparkle(d, 0.41, 0.33, 12, (255, 150, 150, 255), 240)
    radial_glow(d, 0.72, 0.56, 80, (230, 255, 150, 255), 90)
    sparkle(d, 0.35, 0.52, 9, GREEN, 200)
    sparkle(d, 0.58, 0.51, 9, WHITE, 180)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.45, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.38, 0.33, 45, (255, 50, 50, 255), 70)
    sparkle(d, 0.38, 0.33, 7, (255, 120, 120, 255), 160)
    radial_glow(d, 0.69, 0.56, 40, (230, 255, 150, 255), 50)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_05(m):
    """Carro Elétrico Nacional: faísca monumental na tomada, carro acende luzes e ferve de energia."""
    f1 = zoom_pan(m, 0.50, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.12, 0.42, 90, (100, 220, 255, 255), 110)
    sparkle(d, 0.12, 0.42, 14, WHITE, 240)
    sparkle(d, 0.70, 0.62, 10, GREEN, 190)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.12, 0.42, 160, (100, 220, 255, 255), 150)
    burst_lines(d, 0.12, 0.42, 35, 120, n=12, color=WHITE, alpha=240, width=5)
    sparkle(d, 0.12, 0.42, 22, WHITE, 255)
    line(d, (0.75, 0.55), (0.78, 0.51), (120, 255, 180, 255), 4, 220)
    line(d, (0.78, 0.51), (0.83, 0.56), (120, 255, 180, 255), 4, 220)
    radial_glow(d, 0.70, 0.65, 70, (100, 255, 150, 255), 120)
    sparkle(d, 0.39, 0.22, 11, WHITE, 210)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.12, 0.42, 80, (100, 220, 255, 255), 80)
    sparkle(d, 0.12, 0.42, 10, WHITE, 180)
    sparkle(d, 0.70, 0.62, 8, GREEN, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_07(m):
    """GPS de todo mundo: o orelhão ESCUTA — anéis de sonar saem da orelha,
    radar pisca nos painéis holográficos, a trilha de pegadas acende."""
    f1 = zoom_pan(m, 0.60, 0.42, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    ring(d, 0.71, 0.33, 20, GREEN, 4, 150)
    ring(d, 0.455, 0.19, 15, GREEN, 4, 140)
    radial_glow(d, 0.583, 0.415, 46, GREEN, 70)
    sparkle(d, 0.583, 0.415, 9, (190, 255, 210, 255))
    sparkle(d, 0.485, 0.47, 8, GREEN, 190)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.60, 0.42, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    ring(d, 0.71, 0.33, 32, GREEN, 5, 200)
    ring(d, 0.71, 0.33, 46, (150, 255, 190, 255), 4, 110)
    ring(d, 0.785, 0.25, 18, GREEN, 4, 160)
    ring(d, 0.505, 0.36, 18, GREEN, 4, 150)
    radial_glow(d, 0.583, 0.415, 66, GREEN, 110)
    sparkle(d, 0.61, 0.345, 8, WHITE, 220)
    for (sx, sy) in ((0.472, 0.455), (0.50, 0.50), (0.532, 0.545)):
        sparkle(d, sx, sy, 7, GREEN, 210)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.60, 0.42, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    ring(d, 0.71, 0.33, 40, GREEN, 4, 90)
    radial_glow(d, 0.615, 0.32, 84, GREEN, 60)
    sparkle(d, 0.583, 0.415, 7, (190, 255, 210, 255), 170)
    sparkle(d, 0.755, 0.53, 7, GREEN, 170)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_08(m):
    """Chip no papel timbre: a lupa revela — anéis sob a lente, o circuito do
    documento pulsa verde, a anteninha pisca e a luminária dá um flash."""
    f1 = zoom_pan(m, 0.52, 0.50, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    ring(d, 0.468, 0.415, 26, GREEN, 4, 140)
    radial_glow(d, 0.575, 0.615, 60, GREEN, 70)
    sparkle(d, 0.494, 0.525, 9, (190, 255, 210, 255), 220)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.52, 0.50, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    ring(d, 0.468, 0.415, 38, GREEN, 5, 190)
    ring(d, 0.468, 0.415, 52, (150, 255, 190, 255), 4, 100)
    radial_glow(d, 0.575, 0.615, 90, GREEN, 120)
    radial_glow(d, 0.742, 0.45, 70, (190, 255, 170, 255), 70)
    sparkle(d, 0.494, 0.525, 13, WHITE, 240)
    sparkle(d, 0.55, 0.59, 8, GREEN, 210)
    sparkle(d, 0.61, 0.64, 8, GREEN, 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.52, 0.50, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.575, 0.615, 110, GREEN, 90)
    ring(d, 0.575, 0.615, 40, GREEN, 4, 110)
    sparkle(d, 0.494, 0.525, 8, (190, 255, 210, 255), 180)
    sparkle(d, 0.44, 0.39, 9, WHITE, 180)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_09(m):
    """Taxa na transferência: a mão do fisco MORDE a moeda — explosão dourada
    na mordida, farelos de moeda caindo e o feixe do celular pulsando."""
    f1 = zoom_pan(m, 0.42, 0.36, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.358, 0.295, 58, (255, 220, 120, 255), 60)
    sparkle(d, 0.475, 0.215, 10, (255, 230, 140, 255), 220)
    line(d, (0.677, 0.405), (0.55, 0.34), (255, 240, 160, 255), 6, 110)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.42, 0.36, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.358, 0.295, 84, (255, 220, 120, 255), 85)
    burst_lines(d, 0.475, 0.215, 14, 44, n=8, color=GOLD, alpha=210, width=4)
    ring(d, 0.358, 0.295, 44, (255, 226, 140, 255), 5, 150)
    sparkle(d, 0.475, 0.215, 15, WHITE, 250)
    sparkle(d, 0.725, 0.355, 9, (255, 230, 140, 255), 220)
    sparkle(d, 0.785, 0.335, 9, (255, 230, 140, 255), 210)
    line(d, (0.677, 0.405), (0.55, 0.34), (255, 250, 190, 255), 9, 170)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.42, 0.36, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.358, 0.295, 80, GOLD, 80)
    sparkle(d, 0.475, 0.215, 8, (255, 230, 140, 255), 180)
    sparkle(d, 0.205, 0.365, 9, WHITE, 210)
    for (cx, cy) in ((0.44, 0.36), (0.46, 0.42), (0.43, 0.48)):
        d.ellipse([int(cx * f3.width) - 4, int(cy * f3.height) - 4,
                   int(cx * f3.width) + 4, int(cy * f3.height) + 4], fill=(212, 175, 55, 150))
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p3_10(m):
    """Moeda magnética: o superímã PUXA — ondas de campo estouram dos polos,
    cédulas e moedas voam na espiral e o cofre reluz satisfeito."""
    f1 = zoom_pan(m, 0.55, 0.38, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    arc_line(d, 0.545, 0.185, 60, 120, 240, (255, 120, 110, 255), 5, 150)
    sparkle(d, 0.505, 0.155, 10, (255, 140, 130, 255), 220)
    sparkle(d, 0.575, 0.21, 10, (255, 140, 130, 255), 220)
    sparkle(d, 0.42, 0.40, 8, GOLD, 200)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.55, 0.38, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    arc_line(d, 0.545, 0.185, 80, 110, 250, (255, 120, 110, 255), 6, 200)
    arc_line(d, 0.545, 0.185, 105, 115, 245, (255, 160, 150, 255), 5, 130)
    sparkle(d, 0.505, 0.155, 14, WHITE, 250)
    sparkle(d, 0.575, 0.21, 14, WHITE, 250)
    for (sx, sy) in ((0.36, 0.50), (0.42, 0.36), (0.47, 0.28), (0.50, 0.22)):
        sparkle(d, sx, sy, 8, GOLD, 220)
    sparkle(d, 0.695, 0.475, 11, (220, 240, 255, 255), 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.55, 0.38, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    arc_line(d, 0.545, 0.185, 95, 120, 240, (255, 120, 110, 255), 4, 100)
    radial_glow(d, 0.545, 0.185, 90, (255, 90, 80, 255), 50)
    sparkle(d, 0.505, 0.155, 8, (255, 140, 130, 255), 180)
    sparkle(d, 0.44, 0.33, 7, GOLD, 180)
    sparkle(d, 0.695, 0.475, 8, (220, 240, 255, 255), 170)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_01(m):
    """Mensagem invertida no vinil: os grooves brilham, ondas sonoras incham
    nos alto-falantes, chamas das velas tremem e o dedo do DJ raspa faísca."""
    f1 = zoom_pan(m, 0.56, 0.50, 1.04)
    f1 = region_jitter(f1, 0.07, 0.12, 0.10, 0.21, 2, seed=4)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    ring(d, 0.628, 0.555, 30, GOLD, 4, 150)
    arc_line(d, 0.115, 0.44, 70, 80, 200, (180, 120, 255, 255), 5, 130)
    sparkle(d, 0.615, 0.55, 9, (255, 230, 140, 255), 210)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.56, 0.50, 1.08)
    f2 = region_jitter(f2, 0.07, 0.12, 0.10, 0.21, 3, seed=8)
    f2 = region_jitter(f2, 0.775, 0.55, 0.80, 0.63, 2, seed=10)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    ring(d, 0.628, 0.555, 40, GOLD, 5, 200)
    ring(d, 0.628, 0.555, 55, (200, 150, 255, 255), 4, 110)
    arc_line(d, 0.115, 0.44, 95, 70, 210, (180, 120, 255, 255), 6, 190)
    arc_line(d, 0.735, 0.42, 95, -20, 110, (180, 120, 255, 255), 6, 190)
    radial_glow(d, 0.357, 0.175, 50, (255, 180, 90, 255), 70)
    sparkle(d, 0.615, 0.55, 13, WHITE, 240)
    note(d, 0.74, 0.30, 12, (200, 150, 255, 255), 220)
    note(d, 0.175, 0.32, 11, (200, 150, 255, 255), 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.56, 0.50, 1.02)
    f3 = region_jitter(f3, 0.07, 0.12, 0.10, 0.21, 2, seed=12)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    ring(d, 0.628, 0.555, 48, GOLD, 4, 110)
    arc_line(d, 0.115, 0.44, 120, 75, 205, (180, 120, 255, 255), 4, 100)
    arc_line(d, 0.735, 0.42, 120, -25, 105, (180, 120, 255, 255), 4, 100)
    sparkle(d, 0.628, 0.555, 8, (255, 230, 140, 255), 180)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_02(m):
    """Desenho da indução: os anéis da TV PULSAM ciano, as espirais giram nos
    olhinhos da criança e do gato, e o brilho da tela varre o tapete."""
    EYEL, EYER = (0.607, 0.388), (0.668, 0.388)
    CATL, CATR = (0.766, 0.535), (0.797, 0.527)
    f1 = zoom_pan(m, 0.50, 0.45, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    ring(d, 0.283, 0.345, 40, (140, 230, 255, 255), 5, 160)
    arc_spiral(d, *EYEL, 14, (220, 200, 255, 255), 190, 4, rot=0.4)
    arc_spiral(d, *EYER, 14, (220, 200, 255, 255), 190, 4, rot=0.4)
    radial_glow(d, 0.50, 0.66, 110, (80, 200, 235, 255), 40)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.50, 0.45, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.283, 0.345, 110, (80, 200, 235, 255), 70)
    ring(d, 0.283, 0.345, 52, (140, 230, 255, 255), 6, 200)
    ring(d, 0.283, 0.345, 66, (190, 240, 255, 255), 4, 120)
    arc_spiral(d, *EYEL, 16, (230, 210, 255, 255), 220, 5, rot=1.6)
    arc_spiral(d, *EYER, 16, (230, 210, 255, 255), 220, 5, rot=1.6)
    arc_spiral(d, *CATL, 10, (230, 210, 255, 255), 200, 4, rot=1.6)
    arc_spiral(d, *CATR, 10, (230, 210, 255, 255), 200, 4, rot=1.6)
    sparkle(d, 0.28, 0.10, 9, (190, 240, 255, 255), 220)
    sparkle(d, 0.628, 0.525, 8, (255, 230, 150, 255), 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.50, 0.45, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    ring(d, 0.283, 0.345, 60, (140, 230, 255, 255), 4, 110)
    radial_glow(d, 0.283, 0.345, 80, (80, 200, 235, 255), 50)
    arc_spiral(d, *EYEL, 14, (220, 200, 255, 255), 170, 4, rot=2.8)
    arc_spiral(d, *EYER, 14, (220, 200, 255, 255), 170, 4, rot=2.8)
    sparkle(d, 0.283, 0.345, 8, WHITE, 190)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_03(m):
    """Fábrica do boneco possuído: os orbes roxos pulsam, os botões flutuam
    girando, a chavinha gira fagulhando e a cola do artesão pinga."""
    f1 = zoom_pan(m, 0.45, 0.38, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    ring(d, 0.165, 0.335, 20, PURPLE, 4, 140)
    sparkle(d, 0.212, 0.225, 9, (255, 230, 140, 255), 220)
    sparkle(d, 0.43, 0.22, 7, (200, 170, 255, 255), 190)
    d.ellipse([int(0.788 * f1.width) - 4, int(0.365 * f1.height) - 4,
               int(0.788 * f1.width) + 4, int(0.365 * f1.height) + 4], fill=(220, 230, 235, 170))
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.45, 0.38, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.32, 0.30, 100, PURPLE, 70)
    ring(d, 0.165, 0.335, 30, PURPLE, 5, 190)
    ring(d, 0.397, 0.06, 24, PURPLE, 5, 170)
    sparkle(d, 0.212, 0.225, 13, WHITE, 250)
    sparkle(d, 0.505, 0.43, 8, (200, 170, 255, 255), 210)
    sparkle(d, 0.185, 0.145, 7, (200, 170, 255, 255), 200)
    sparkle(d, 0.595, 0.215, 7, (200, 170, 255, 255), 200)
    d.ellipse([int(0.792 * f2.width) - 5, int(0.385 * f2.height) - 5,
               int(0.792 * f2.width) + 5, int(0.385 * f2.height) + 5], fill=(230, 240, 245, 200))
    sparkle(d, 0.788, 0.365, 6, WHITE, 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.45, 0.38, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.32, 0.30, 80, PURPLE, 50)
    ring(d, 0.165, 0.335, 26, PURPLE, 4, 100)
    sparkle(d, 0.212, 0.225, 7, (255, 230, 140, 255), 180)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_06(m):
    """Imagem que chora xarope: as lágrimas douradas escorrem brilhando,
    a pinga cai certinho no pote do espertinho e as velas do altar tremem."""
    f1 = zoom_pan(m, 0.48, 0.40, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    sparkle(d, 0.473, 0.26, 7, (255, 230, 140, 255), 210)
    sparkle(d, 0.527, 0.27, 7, (255, 230, 140, 255), 210)
    radial_glow(d, 0.50, 0.415, 46, GOLD, 50)
    sparkle(d, 0.585, 0.49, 8, WHITE, 200)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.48, 0.40, 1.08)
    f2 = region_jitter(f2, 0.675, 0.33, 0.70, 0.38, 2, seed=6)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    sparkle(d, 0.473, 0.31, 8, (255, 236, 160, 255), 230)
    sparkle(d, 0.527, 0.33, 8, (255, 236, 160, 255), 230)
    radial_glow(d, 0.50, 0.415, 70, GOLD, 80)
    for (cx, cy) in ((0.455, 0.455), (0.555, 0.465), (0.53, 0.49)):
        d.ellipse([int(cx * f2.width) - 4, int(cy * f2.height) - 4,
                   int(cx * f2.width) + 4, int(cy * f2.height) + 4], fill=(255, 200, 90, 190))
    ring(d, 0.585, 0.49, 16, GOLD, 4, 160)
    line(d, (0.56, 0.44), (0.585, 0.475), (255, 220, 130, 255), 4, 160)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.48, 0.40, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    sparkle(d, 0.473, 0.37, 6, (255, 230, 140, 255), 180)
    sparkle(d, 0.527, 0.39, 6, (255, 230, 140, 255), 180)
    d.ellipse([int(0.528 * f3.width) - 5, int(0.505 * f3.height) - 5,
               int(0.528 * f3.width) + 5, int(0.505 * f3.height) + 5], fill=(255, 210, 110, 200))
    sparkle(d, 0.583, 0.46, 7, GOLD, 190)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_07(m):
    """13º mandamento no áudio: a tábua de som pulsa, faíscas viajam pela
    fita-waveform do microfone e o rolo de fita reluz girando."""
    f1 = zoom_pan(m, 0.52, 0.36, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    ring(d, 0.512, 0.125, 38, (140, 230, 255, 255), 5, 150)
    sparkle(d, 0.40, 0.35, 8, (170, 235, 255, 255), 210)
    sparkle(d, 0.155, 0.405, 8, (220, 245, 255, 255), 190)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.52, 0.36, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.512, 0.125, 90, (80, 200, 235, 255), 80)
    ring(d, 0.512, 0.125, 52, (180, 240, 255, 255), 6, 190)
    sparkle(d, 0.49, 0.20, 9, (190, 245, 255, 255), 230)
    sparkle(d, 0.83, 0.245, 9, (190, 245, 255, 255), 220)
    sparkle(d, 0.625, 0.40, 8, WHITE, 210)
    d.ellipse([int(0.213 * f2.width) - 3, int(0.503 * f2.height) - 3,
               int(0.213 * f2.width) + 3, int(0.503 * f2.height) + 3], fill=(120, 255, 170, 220))
    d.ellipse([int(0.233 * f2.width) - 3, int(0.503 * f2.height) - 3,
               int(0.233 * f2.width) + 3, int(0.503 * f2.height) + 3], fill=(255, 220, 90, 220))
    arc_line(d, 0.155, 0.405, 34, 200, 320, (200, 240, 255, 255), 4, 150)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.52, 0.36, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    ring(d, 0.512, 0.125, 60, (140, 230, 255, 255), 4, 100)
    radial_glow(d, 0.512, 0.125, 70, (80, 200, 235, 255), 50)
    sparkle(d, 0.42, 0.29, 7, (170, 235, 255, 255), 180)
    sparkle(d, 0.235, 0.385, 7, (220, 245, 255, 255), 170)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_08(m):
    """Água da torneira bendita: o jato cintila, auréolas douradas selam as
    garrafas e bolhas sobem na garrafa da vez sob a torneira."""
    f1 = zoom_pan(m, 0.58, 0.45, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    sparkle(d, 0.555, 0.40, 8, (190, 245, 255, 255), 220)
    ring(d, 0.845, 0.375, 15, GOLD, 4, 150)
    sparkle(d, 0.50, 0.175, 7, (220, 245, 255, 255), 190)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.58, 0.45, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    line(d, (0.555, 0.28), (0.555, 0.44), (210, 250, 255, 255), 8, 130)
    sparkle(d, 0.548, 0.42, 9, (220, 250, 255, 255), 240)
    sparkle(d, 0.563, 0.41, 9, (220, 250, 255, 255), 230)
    ring(d, 0.71, 0.375, 17, GOLD, 5, 190)
    ring(d, 0.845, 0.375, 17, GOLD, 5, 190)
    ring(d, 0.895, 0.265, 22, (255, 230, 140, 255), 5, 170)
    for (bx, by) in ((0.553, 0.455), (0.557, 0.475), (0.552, 0.495)):
        d.ellipse([int(bx * f2.width) - 3, int(by * f2.height) - 3,
                   int(bx * f2.width) + 3, int(by * f2.height) + 3], fill=(220, 250, 255, 210))
    sparkle(d, 0.98, 0.575, 7, (190, 245, 255, 255), 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.58, 0.45, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    sparkle(d, 0.555, 0.40, 7, (190, 245, 255, 255), 180)
    ring(d, 0.845, 0.375, 19, GOLD, 4, 110)
    radial_glow(d, 0.68, 0.76, 40, (120, 220, 255, 255), 50)
    sparkle(d, 0.68, 0.74, 6, (220, 250, 255, 255), 180)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p4_09(m):
    """Apocalipse adiado (de novo): o bloco vermelho é EMPURRADO — linhas de
    esforço à esquerda do bloco, suor voa e o cometinha esperto aguarda."""
    f1 = zoom_pan(m, 0.60, 0.40, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    for i, yy in enumerate((0.28, 0.33, 0.38)):
        line(d, (0.655, yy), (0.675, yy), (255, 240, 200, 255), 4, 140)
    d.ellipse([int(0.468 * f1.width) - 3, int(0.34 * f1.height) - 3,
               int(0.468 * f1.width) + 3, int(0.34 * f1.height) + 3], fill=(200, 235, 255, 190))
    sparkle(d, 0.865, 0.395, 8, (200, 220, 235, 255), 200)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.60, 0.40, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.725, 0.36, 110, (255, 80, 70, 255), 60)
    for i, yy in enumerate((0.27, 0.325, 0.38, 0.435)):
        line(d, (0.645, yy), (0.672, yy), (255, 240, 200, 255), 5, 190)
    ring(d, 0.865, 0.395, 24, (200, 220, 235, 255), 4, 150)
    sparkle(d, 0.865, 0.395, 11, WHITE, 230)
    for (sx, sy) in ((0.462, 0.33), (0.475, 0.38), (0.468, 0.43)):
        d.ellipse([int(sx * f2.width) - 4, int(sy * f2.height) - 4,
                   int(sx * f2.width) + 4, int(sy * f2.height) + 4], fill=(210, 240, 255, 200))
    sparkle(d, 0.775, 0.46, 8, (255, 180, 170, 255), 200)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.60, 0.40, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.725, 0.36, 80, (255, 80, 70, 255), 40)
    line(d, (0.65, 0.33), (0.67, 0.33), (255, 240, 200, 255), 4, 120)
    sparkle(d, 0.865, 0.395, 7, (200, 220, 235, 255), 170)
    sparkle(d, 0.117, 0.135, 8, (255, 120, 110, 255), 200)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p5_01(m):
    """Feixe sobre o cerrado: a coluna verde ENGROSSA e solta anéis subindo,
    os pratos laterais respondem e os vaga-lumes testemunham piscando."""
    f1 = zoom_pan(m, 0.62, 0.40, 1.04)
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.705, 0.42, 80, GREEN, 80)
    ring(d, 0.705, 0.42, 40, (170, 255, 200, 255), 5, 150)
    sparkle(d, 0.55, 0.485, 7, (255, 255, 170, 255), 200)
    sparkle(d, 0.965, 0.655, 7, (255, 255, 170, 255), 190)
    f1 = composite(f1, ov)

    f2 = zoom_pan(m, 0.62, 0.40, 1.08)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.705, 0.42, 120, GREEN, 110)
    line(d, (0.672, 0.02), (0.672, 0.40), (190, 255, 210, 255), 6, 110)
    line(d, (0.738, 0.02), (0.738, 0.40), (190, 255, 210, 255), 6, 110)
    ring(d, 0.705, 0.42, 55, (190, 255, 215, 255), 6, 190)
    ring(d, 0.705, 0.20, 40, (170, 255, 200, 255), 4, 120)
    ring(d, 0.598, 0.40, 22, (170, 255, 200, 255), 4, 150)
    ring(d, 0.815, 0.39, 22, (170, 255, 200, 255), 4, 150)
    sparkle(d, 0.615, 0.50, 8, (255, 255, 170, 255), 220)
    sparkle(d, 0.88, 0.54, 7, (255, 255, 170, 255), 200)
    sparkle(d, 0.40, 0.585, 9, (255, 230, 140, 255), 220)
    f2 = composite(f2, ov)

    f3 = zoom_pan(m, 0.62, 0.40, 1.02)
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    radial_glow(d, 0.705, 0.42, 90, GREEN, 70)
    ring(d, 0.705, 0.42, 48, (170, 255, 200, 255), 4, 100)
    sparkle(d, 0.25, 0.545, 6, (255, 255, 170, 255), 180)
    sparkle(d, 0.52, 0.50, 6, (255, 255, 170, 255), 170)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def soft_glow(im, nx, ny, r, color, alpha=90, blur=10):
    """Brilho embaçado — não desenha disco de borda dura sobre a pintura."""
    ov = overlay(im)
    d = ImageDraw.Draw(ov)
    x, y = _px(im, nx, ny)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(color[0], color[1], color[2], alpha))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    return composite(im, ov)


def teardrop(d, nx, ny, r, color, alpha=210):
    """Gota pequena (ponta pra cima) — usada só onde já existe uma gota pintada."""
    x, y = _px(d._image, nx, ny)
    c = (color[0], color[1], color[2], alpha)
    rr = max(4, int(r))
    d.polygon([(x, y - rr), (x - int(rr * 0.42), y), (x + int(rr * 0.42), y)], fill=c)
    d.ellipse([x - int(rr * 0.48), y - int(rr * 0.15), x + int(rr * 0.48), y + int(rr * 0.7)], fill=c)
    d.ellipse([x - int(rr * 0.16), y + int(rr * 0.05), x - 1, y + int(rr * 0.28)],
              fill=(255, 255, 255, min(255, alpha)))


def _drop_big_blobs(mask, max_px=2200):
    """Zera componentes claros grandes demais para serem uma janelinha."""
    w, h = mask.size
    px = mask.load()
    seen = bytearray(w * h)
    for y in range(h):
        row = y * w
        for x in range(w):
            i = row + x
            if seen[i] or px[x, y] < 128:
                continue
            stack = [(x, y)]
            seen[i] = 1
            comp = [(x, y)]
            while stack:
                cx, cy = stack.pop()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny * w + nx
                        if not seen[j] and px[nx, ny] >= 128:
                            seen[j] = 1
                            stack.append((nx, ny))
                            comp.append((nx, ny))
            if len(comp) > max_px:
                for cx, cy in comp:
                    px[cx, cy] = 0
    return mask


def extinguish_windows(im, box, frac, seed=3, cell=34):
    """Apaga uma fração das janelinhas claras, pixel a pixel — sem retângulo duro."""
    w, h = im.size
    x0, y0 = int(box[0] * w), int(box[1] * h)
    x1, y1 = int(box[2] * w), int(box[3] * h)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x1 <= x0 or y1 <= y0:
        return im
    crop = im.crop((x0, y0, x1, y1))
    px = crop.load()
    mask = Image.new("L", crop.size, 0)
    mp = mask.load()
    cw, ch = crop.size
    for yy in range(ch):
        for xx in range(cw):
            r, g, b = px[xx, yy]
            if r > 185 and g > 150 and b < 150 and r > b + 35:
                mp[xx, yy] = 255
    mask = mask.filter(ImageFilter.MaxFilter(5))
    rng = random.Random(seed)
    mp = mask.load()
    for cy in range(0, ch, cell):
        for cx in range(0, cw, cell):
            if rng.random() > frac:
                for yy in range(cy, min(ch, cy + cell)):
                    for xx in range(cx, min(cw, cx + cell)):
                        mp[xx, yy] = 0
    dark = ImageEnhance.Brightness(crop).enhance(0.18)
    # puxa o que apagou para o teal da sala, não para preto chapado
    teal = Image.new("RGB", crop.size, (14, 32, 38))
    dark = Image.blend(dark, teal, 0.45)
    out = Image.composite(dark, crop, mask)
    im = im.copy()
    im.paste(out, (x0, y0))
    return im


# -------------------------------- lote H — Singularidade fecha 50/50 --------
def rec_p5_02(m):
    """Fórmula da água: uma segunda dose desce do conta-gotas até a água
    e o arco vermelho do manômetro pulsa. Sem zoom (coordenadas medidas)."""
    GAUGE = (0.748, 0.335)  # arco vermelho, medido

    f1 = m.copy()
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    teardrop(d, 0.500, 0.575, 16, CYAN, 230)
    sparkle(d, 0.512, 0.640, 10, (230, 255, 255, 255), 180)
    f1 = composite(f1, ov)

    f2 = m.copy()
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    teardrop(d, 0.508, 0.630, 18, CYAN, 235)
    sparkle(d, 0.490, 0.710, 10, (220, 250, 255, 255), 210)
    sparkle(d, 0.535, 0.718, 9, (220, 250, 255, 255), 190)
    radial_glow(d, *GAUGE, 36, RED, 100)
    f2 = composite(f2, ov)

    f3 = m.copy()
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    teardrop(d, 0.512, 0.690, 8, CYAN, 200)
    sparkle(d, 0.480, 0.720, 7, (230, 255, 255, 255), 210)
    sparkle(d, 0.545, 0.725, 6, (230, 255, 255, 255), 190)
    radial_glow(d, *GAUGE, 30, RED, 110)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p5_03(m):
    """Ensaio do apagão: as janelinhas do painel apagam em onda e só o
    alarme vermelho continua. Máscara nas luzes, nunca um retângulo."""
    ALARM = (0.345, 0.100)
    PANEL = (0.012, 0.145, 0.635, 0.930)
    CITY = (0.865, 0.220, 0.990, 0.480)

    f1 = m.copy()
    f1 = extinguish_windows(f1, PANEL, 0.28, seed=11)
    f1 = soft_glow(f1, *ALARM, 36, RED, 80, 12)

    f2 = zoom_pan(m, 0.42, 0.42, 1.06)
    f2 = extinguish_windows(f2, PANEL, 0.62, seed=11)
    f2 = extinguish_windows(f2, CITY, 0.45, seed=19, cell=22)
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    radial_glow(d, *ALARM, 32, RED, 100)
    sparkle(d, 0.345, 0.075, 6, (255, 220, 200, 255), 180)
    f2 = composite(f2, ov)

    f3 = m.copy()
    f3 = extinguish_windows(f3, PANEL, 0.90, seed=11)
    f3 = extinguish_windows(f3, CITY, 0.75, seed=19, cell=22)
    f3 = soft_glow(f3, *ALARM, 42, RED, 120, 14)
    return [m, f1, f2, f3]


def rec_p5_05(m):
    """A conversa é ouvida: as ondas saem do aparelho e a varredura da TV
    fica DENTRO da tela (x 0.84–0.97, y 0.32–0.66)."""
    SPEAK = (0.230, 0.380)
    # tela interna medida: x 0.83–0.98, y 0.31–0.66 — a faixa não sai daí
    SX0, SX1, SY0, SY1 = 0.840, 0.970, 0.330, 0.640

    def scan(im, x):
        ov = overlay(im)
        d = ImageDraw.Draw(ov)
        x = min(SX1 - 0.01, max(SX0 + 0.01, x))
        # barra escura (a tela é clara) + filete branco, ambos dentro do vidro
        line(d, (x, SY0), (x, SY1), (12, 28, 34, 255), 22, 170)
        line(d, (x + 0.012, SY0), (x + 0.012, SY1), (255, 255, 255, 255), 4, 200)
        return composite(im, ov)

    f1 = m.copy()
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    arc_line(d, *SPEAK, 78, 290, 350, CYAN, 5, 140)
    sparkle(d, 0.320, 0.300, 6, CYAN, 180)
    f1 = composite(f1, ov)
    f1 = soft_glow(f1, 0.720, 0.685, 16, CYAN, 70, 6)

    f2 = m.copy()
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    arc_line(d, *SPEAK, 100, 285, 350, CYAN, 5, 170)
    arc_line(d, *SPEAK, 136, 300, 345, CYAN, 4, 110)
    f2 = composite(f2, ov)
    f2 = scan(f2, 0.885)
    f2 = soft_glow(f2, 0.720, 0.685, 20, CYAN, 100, 6)

    f3 = m.copy()
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    arc_line(d, *SPEAK, 64, 295, 345, CYAN, 4, 90)
    f3 = composite(f3, ov)
    f3 = scan(f3, 0.945)
    return [m, f1, f2, f3]


def rec_p5_06(m):
    """Presidente 2.0: a faísca estoura no compartimento e os olhos ganham
    um pontinho de brilho — nunca um borrão sobre o rosto."""
    SPARK = (0.500, 0.430)

    f1 = m.copy()
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    burst_lines(d, *SPARK, 6, 22, 6, (255, 220, 120, 255), 160, 3)
    f1 = composite(f1, ov)

    f2 = m.copy()
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    burst_lines(d, *SPARK, 14, 52, 9, (255, 230, 150, 255), 220, 4)
    sparkle(d, 0.485, 0.400, 7, (255, 245, 190, 255), 200)
    sparkle(d, 0.530, 0.460, 6, (255, 200, 80, 255), 180)
    f2 = composite(f2, ov)

    f3 = m.copy()
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    burst_lines(d, *SPARK, 8, 28, 6, (255, 220, 130, 255), 150, 3)
    sparkle(d, 0.300, 0.500, 6, GOLD, 160)
    f3 = composite(f3, ov)
    return [m, f1, f2, f3]


def rec_p5_08(m):
    """Malha de torres: o jardineiro rega a torre caída e os anéis de
    sinal pulsam a partir da luz laranja — arcos curtos, não uma grade."""
    LAMP = (0.330, 0.370)
    WAVES = (0.405, 0.335)

    f1 = m.copy()
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    arc_line(d, *WAVES, 62, 250, 340, ORANGE, 4, 140)
    f1 = composite(f1, ov)
    f1 = soft_glow(f1, *LAMP, 14, ORANGE, 150, 4)

    f2 = m.copy()
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    arc_line(d, *WAVES, 88, 245, 345, ORANGE, 5, 170)
    arc_line(d, *WAVES, 118, 255, 335, ORANGE, 3, 110)
    f2 = composite(f2, ov)

    f3 = m.copy()
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    arc_line(d, *WAVES, 52, 255, 340, ORANGE, 4, 100)
    sparkle(d, 0.430, 0.320, 6, (255, 210, 140, 255), 170)
    f3 = composite(f3, ov)
    f3 = soft_glow(f3, *LAMP, 16, ORANGE, 130, 5)
    return [m, f1, f2, f3]


def rec_p5_09(m):
    """QR no prato: a última gota de molho cai e o feixe do celular
    varre o código. Sem anel gigante sobre o arroz."""
    PHONE = (0.700, 0.455)

    f1 = m.copy()
    ov = overlay(f1)
    d = ImageDraw.Draw(ov)
    teardrop(d, 0.445, 0.575, 8, (120, 42, 32, 255), 210)
    sparkle(d, 0.640, 0.540, 7, GREEN, 190)
    f1 = composite(f1, ov)
    f1 = soft_glow(f1, *PHONE, 14, GREEN, 80, 5)

    f2 = m.copy()
    ov = overlay(f2)
    d = ImageDraw.Draw(ov)
    teardrop(d, 0.446, 0.615, 9, (110, 36, 28, 255), 220)
    sparkle(d, 0.580, 0.630, 8, GREEN, 210)
    f2 = composite(f2, ov)
    f2 = soft_glow(f2, *PHONE, 18, GREEN, 110, 5)

    f3 = m.copy()
    ov = overlay(f3)
    d = ImageDraw.Draw(ov)
    sparkle(d, 0.520, 0.740, 14, GREEN, 220)
    sparkle(d, 0.590, 0.760, 12, (190, 255, 200, 255), 200)
    sparkle(d, 0.500, 0.800, 10, GREEN, 170)
    radial_glow(d, 0.560, 0.760, 48, GREEN, 50)
    f3 = composite(f3, ov)
    f3 = soft_glow(f3, *PHONE, 16, GREEN, 90, 5)
    return [m, f1, f2, f3]


RECIPES = {
    "p1_02": rec_p1_02,
    "p1_03": rec_p1_03,
    "p1_04": rec_p1_04,
    "p1_05": rec_p1_05,
    "p1_06": rec_p1_06,
    "p1_07": rec_p1_07,
    "p1_08": rec_p1_08,
    "p1_09": rec_p1_09,
    "p1_10": rec_p1_10,
    "p2_01": rec_p2_01,
    "p2_02": rec_p2_02,
    "p2_03": rec_p2_03,
    "p2_04": rec_p2_04,
    "p2_05": rec_p2_05,
    "p2_06": rec_p2_06,
    "p2_07": rec_p2_07,
    "p2_08": rec_p2_08,
    "p2_09": rec_p2_09,
    "p2_10": rec_p2_10,
    "p3_01": rec_p3_01,
    "p3_02": rec_p3_02,
    "p3_03": rec_p3_03,
    "p3_04": rec_p3_04,
    "p3_05": rec_p3_05,
    "p3_06": rec_p3_06,
    "p3_07": rec_p3_07,
    "p3_08": rec_p3_08,
    "p3_09": rec_p3_09,
    "p3_10": rec_p3_10,
    "p4_01": rec_p4_01,
    "p4_02": rec_p4_02,
    "p4_03": rec_p4_03,
    "p4_06": rec_p4_06,
    "p4_07": rec_p4_07,
    "p4_08": rec_p4_08,
    "p4_09": rec_p4_09,
    "p5_01": rec_p5_01,
    "p4_04": rec_p4_04,
    "p4_05": rec_p4_05,
    "p4_10": rec_p4_10,
    "p5_04": rec_p5_04,
    "p5_07": rec_p5_07,
    "p5_10": rec_p5_10,
    "p5_02": rec_p5_02,
    "p5_03": rec_p5_03,
    "p5_05": rec_p5_05,
    "p5_06": rec_p5_06,
    "p5_08": rec_p5_08,
    "p5_09": rec_p5_09,
}


def main():
    ids = sys.argv[1:] or list(RECIPES)
    for mid in ids:
        d = Path(ROOT) / "src" / "assets" / "anim" / mid / "frames"
        m = Image.open(d / "f00.png").convert("RGB")
        m = crop169(m)
        fn = RECIPES.get(mid)
        if fn is None:
            sys.exit(f"sem recipe para {mid}")
        frames = fn(m)
        for i, im in enumerate(frames):
            im.save(d / f"f{i:02d}.png")
        print(f"[{mid}] 4 quadros sintéticos prontos ({m.size[0]}x{m.size[1]})")


if __name__ == "__main__":
    main()

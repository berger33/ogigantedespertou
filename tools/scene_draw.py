#!/usr/bin/env python3
"""scene_draw.py — desenha (em código) as 11 cenas sem mestre pintado, 4 keyframes cada.

Por que existe: a quota de geração de imagem do ambiente (10/sessão) esgotou no
meio dos lotes C/D. Estas cenas mantêm o MESMO padrão visual do lote pintado:
flat-toon, outline preto grosso, cores chapadas, dark teal + 1 acento por missão,
e cada uma com elenco e verbo próprios (nunca animação genérica).

Cada função `scene_<id>()` devolve [img0..img3] em 1280x720 (16:9), prontas para
tools/build_animation_loop.py. Os quadros brutos ficam em frames/f00..f03.png
(ignorados no Git; só o .webp otimizado vai pro repo).

Uso: python3 tools/scene_draw.py [id ...]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent

W, H = 1280, 720
INK = (12, 20, 18)
WALL = (16, 49, 43)
WALL_D = (11, 38, 33)
FLOOR = (8, 26, 23)
BASE = (24, 68, 59)
SKIN = (242, 201, 160)
SKIN_D = (214, 165, 126)
SKIN_B = (196, 138, 98)
HAIR_W = (245, 242, 234)
COAT = (201, 180, 137)
COAT_D = (160, 141, 102)
SHIRT = (237, 230, 214)
TIE = (179, 38, 30)
GOLD = (212, 175, 55)
GOLD_D = (168, 138, 42)
GREEN = (57, 255, 156)
GREEN_D = (38, 190, 118)
BLUE = (77, 195, 255)
BLUE_D = (44, 140, 200)
PURPLE = (181, 123, 255)
PURPLE_D = (130, 84, 200)
RED = (227, 60, 46)
RED_D = (160, 38, 30)
ORANGE = (255, 159, 69)
PAPER = (232, 220, 192)
PAPER_D = (198, 183, 150)
SILVER = (186, 197, 199)
SILVER_D = (138, 152, 155)
DARK = (26, 42, 39)
CURL = (90, 108, 104)

_FONT_CACHE = {}


def font(size):
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if Path(path).exists():
            _FONT_CACHE[size] = ImageFont.truetype(path, size)
            return _FONT_CACHE[size]
    _FONT_CACHE[size] = ImageFont.load_default()
    return _FONT_CACHE[size]


# ---------------------------------------------------------------- basics ---

def new_frame():
    return Image.new("RGB", (W, H), WALL)


def bg(d, floor_y=560):
    d.rectangle([0, 0, W, floor_y], fill=WALL)
    for x in range(110, W, 220):
        d.rectangle([x, 0, x + 7, floor_y], fill=WALL_D)
    d.rectangle([0, floor_y - 16, W, floor_y], fill=BASE)
    d.rectangle([0, floor_y, W, H], fill=FLOOR)
    for x in range(60, W, 170):
        d.line([(x, floor_y), (x - 46, H)], fill=WALL_D, width=4)


def orect(d, x0, y0, x1, y1, r, fill, outline=INK, lw=6):
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=lw)


def oell(d, cx, cy, rx, ry, fill, outline=INK, lw=6):
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill, outline=outline, width=lw)


def oline(d, a, b, fill, lw=6):
    d.line([a, b], fill=fill, width=int(lw))


def capsule(d, a, b, w, fill, outline=INK, lw=5):
    w = int(w)
    d.line([a, b], fill=outline, width=w + 2 * lw)
    for p in (a, b):
        r = w / 2 + lw
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=outline)
    d.line([a, b], fill=fill, width=w)
    for p in (a, b):
        r = w / 2
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def hand(d, x, y, r=13, fill=SKIN):
    oell(d, x, y, r, r * 0.9, fill, lw=5)


def glow(ov, cx, cy, r, color, a=90):
    d = ImageDraw.Draw(ov)
    for i in range(6):
        rr = max(4, int(r * (1 - i / 6)))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(*color, max(0, a - i * 18)))


def sparkle(d, x, y, r, color, a=230):
    d.polygon([(x, y - r), (x + r * 0.22, y - r * 0.22), (x + r, y), (x + r * 0.22, y + r * 0.22),
               (x, y + r), (x - r * 0.22, y + r * 0.22), (x - r, y), (x - r * 0.22, y - r * 0.22)],
              fill=(*color, a))
    d.ellipse([x - r * 0.16, y - r * 0.16, x + r * 0.16, y + r * 0.16], fill=(255, 255, 255, a))


def ring(d, cx, cy, r, color, width=6, a=200):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(*color, a), width=width)


def txt(d, x, y, s, size, color, anchor="mm"):
    d.text((x, y), s, font=font(size), fill=color, anchor=anchor)


def arc_line(d, cx, cy, r, a0, a1, color, width=6, a=200):
    d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=(*color, a), width=width)


# ------------------------------------------------------------- pessoas -----

def face(d, cx, cy, r, skin=SKIN, hair_fn=None, look=(0, 0), grin=True, brow=0.0):
    oell(d, cx, cy, r, r * 0.94, skin, lw=6)
    # orelhas
    oell(d, cx - r * 0.96, cy + 4, r * 0.16, r * 0.24, skin, lw=5)
    oell(d, cx + r * 0.96, cy + 4, r * 0.16, r * 0.24, skin, lw=5)
    # olhos
    ex, ey = r * 0.36, -r * 0.14
    for sgn in (-1, 1):
        ox = cx + sgn * ex
        oy = cy + ey
        oell(d, ox, oy, r * 0.19, r * 0.24, (250, 250, 246), lw=4)
        d.ellipse([ox + look[0] * 6 - r * 0.07, oy + look[1] * 6 - r * 0.09,
                   ox + look[0] * 6 + r * 0.07, oy + look[1] * 6 + r * 0.09], fill=INK)
        if brow < 0:  # sobrancelha irritada
            oline(d, (ox - r * 0.2, oy - r * 0.34 - brow * 4), (ox + r * 0.2, oy - r * 0.24 - brow * 4), INK, 5)
    # nariz (grande, 3/4)
    oell(d, cx + r * 0.10, cy + r * 0.22, r * 0.14, r * 0.20, skin, lw=5)
    # boca
    if grin:
        d.chord([cx - r * 0.42, cy + r * 0.28, cx + r * 0.42, cy + r * 0.72], 15, 165, fill=(120, 44, 36), outline=INK, width=5)
        d.chord([cx - r * 0.30, cy + r * 0.40, cx + r * 0.30, cy + r * 0.62], 10, 170, fill=(245, 240, 235), outline=None)
    else:
        oline(d, (cx - r * 0.22, cy + r * 0.5), (cx + r * 0.22, cy + r * 0.5), INK, 6)
    if hair_fn:
        hair_fn(d, cx, cy, r)


def hair_grifter(d, cx, cy, r):
    pts = []
    for i, (dx, dy) in enumerate([(-0.95, -0.55), (-0.7, -0.95), (-0.35, -0.75), (0.0, -1.05),
                                  (0.35, -0.8), (0.7, -1.0), (0.95, -0.6), (1.0, -0.15),
                                  (-1.0, -0.15)]):
        pts.append((cx + dx * r, cy + dy * r))
    d.polygon(pts, fill=HAIR_W, outline=INK)
    d.line(pts, fill=INK, width=6)


def hair_bun(d, cx, cy, r):
    d.pieslice([cx - r * 1.02, cy - r * 1.05, cx + r * 1.02, cy + r * 0.25], 180, 360, fill=(96, 66, 48), outline=INK, width=6)
    oell(d, cx + r * 0.1, cy - r * 1.12, r * 0.3, r * 0.28, (96, 66, 48), lw=5)


def hair_unkempt(d, cx, cy, r):
    d.pieslice([cx - r * 1.0, cy - r * 1.02, cx + r * 1.0, cy + r * 0.2], 180, 360, fill=(70, 58, 52), outline=INK, width=6)


def cap(d, cx, cy, r, color):
    d.pieslice([cx - r * 1.08, cy - r * 1.15, cx + r * 1.08, cy + r * 0.1], 180, 360, fill=color, outline=INK, width=6)
    orect(d, cx - r * 1.25, cy - r * 0.28, cx + r * 1.25, cy - r * 0.02, 8, color, lw=5)


def grifter(d, x, y, s=1.0, arm_l=200, arm_r=340, look=(0, 0), grin=True):
    """Grifter inteiro. (x, y) = centro do quadril. braços em graus (0=baixo, 180=cima)."""
    hipx, hipy = x, y
    # pernas
    capsule(d, (hipx - 22 * s, hipy + 6 * s), (hipx - 26 * s, hipy + 120 * s), 34 * s, (58, 52, 48))
    capsule(d, (hipx + 22 * s, hipy + 6 * s), (hipx + 26 * s, hipy + 120 * s), 34 * s, (58, 52, 48))
    for sgn in (-1, 1):
        orect(d, hipx + sgn * 26 * s - 26 * s, hipy + 118 * s, hipx + sgn * 26 * s + 14 * s, hipy + 142 * s,
              10, (40, 34, 30), lw=5)
    # casaco
    d.polygon([(hipx - 58 * s, hipy - 150 * s), (hipx + 58 * s, hipy - 150 * s),
               (hipx + 74 * s, hipy + 30 * s), (hipx - 74 * s, hipy + 30 * s)], fill=COAT, outline=INK)
    d.line([(hipx - 58 * s, hipy - 150 * s), (hipx + 58 * s, hipy - 150 * s)], fill=INK, width=7)
    d.line([(hipx - 74 * s, hipy + 30 * s), (hipx + 74 * s, hipy + 30 * s)], fill=INK, width=7)
    # gola + camisa + gravata
    d.polygon([(hipx - 26 * s, hipy - 150 * s), (hipx + 26 * s, hipy - 150 * s), (hipx, hipy - 96 * s)], fill=SHIRT, outline=INK, width=5)
    d.polygon([(hipx - 7 * s, hipy - 142 * s), (hipx + 7 * s, hipy - 142 * s), (hipx + 3 * s, hipy - 60 * s),
               (hipx - 3 * s, hipy - 60 * s)], fill=TIE, outline=INK, width=4)
    # pin
    oell(d, hipx - 40 * s, hipy - 118 * s, 9 * s, 9 * s, GOLD, lw=4)
    # braços (angulo: 0=para baixo, 90=para a direita, 180=para cima)
    shx, shy = hipx, hipy - 138 * s
    for sgn, ang in ((-1, arm_l), (1, arm_r)):
        a = math.radians(ang)
        dx = math.sin(math.radians(ang)) * sgn * 92 * s
        dy = -math.cos(math.radians(ang)) * 92 * s
        ex, ey = shx + dx, shy + dy
        capsule(d, (shx + sgn * 12 * s, shy), (ex, ey), 26 * s, COAT_D)
        hand(d, ex, ey, 13 * s)
    # cabeça
    hx, hy = hipx + 6 * s, hipy - 196 * s
    face(d, hx, hy, 52 * s, skin=SKIN, hair_fn=hair_grifter, look=look, grin=grin)


def grifter_arm(d, x, y, s=1.0, ang=300, hold=None):
    """Só o braço+punho do Grifter (entra da borda). hold = (dx,dy,fn) desenha objeto na mão."""
    shx, shy = x, y
    dx = math.sin(math.radians(ang)) * 100 * s
    dy = -math.cos(math.radians(ang)) * 100 * s
    ex, ey = shx + dx, shy + dy
    capsule(d, (shx, shy), (ex, ey), 26 * s, COAT_D)
    hand(d, ex, ey, 14 * s)
    return ex, ey


def uncle(d, x, y, s=1.0, arm_r=340, look=(0, 0)):
    hipx, hipy = x, y
    # pernas sentadas: só sapatos aparecem
    for sgn in (-1, 1):
        orect(d, hipx + sgn * 30 * s - 20 * s, hipy + 118 * s, hipx + sgn * 30 * s + 22 * s, hipy + 144 * s, 10, (46, 38, 34), lw=5)
    # colete
    d.polygon([(hipx - 52 * s, hipy - 140 * s), (hipx + 52 * s, hipy - 140 * s),
               (hipx + 62 * s, hipy + 40 * s), (hipx - 62 * s, hipy + 40 * s)], fill=(122, 106, 92), outline=INK)
    d.line([(hipx - 52 * s, hipy - 140 * s), (hipx + 52 * s, hipy - 140 * s)], fill=INK, width=7)
    # camisa dentro
    d.polygon([(hipx - 22 * s, hipy - 140 * s), (hipx + 22 * s, hipy - 140 * s), (hipx, hipy - 60 * s)], fill=SHIRT, outline=INK, width=5)
    # braço esquerdo apoiado
    capsule(d, (hipx - 44 * s, hipy - 120 * s), (hipx - 84 * s, hipy - 30 * s), 26 * s, (122, 106, 92))
    hand(d, hipx - 84 * s, hipy - 30 * s, 13 * s)
    # braço direito (ângulo)
    shx, shy = hipx + 44 * s, hipy - 120 * s
    a = math.radians(arm_r)
    dx = math.sin(a) * 86 * s
    dy = -math.cos(a) * 86 * s
    ex, ey = shx + dx, shy + dy
    capsule(d, (shx, shy), (ex, ey), 26 * s, (122, 106, 92))
    hand(d, ex, ey, 13 * s)
    # cabeça
    hx, hy = hipx, hipy - 188 * s
    face(d, hx, hy, 48 * s, skin=SKIN, hair_fn=None, look=look, grin=True)
    d.pieslice([hx - 48 * s, hy + 18 * s, hx + 48 * s, hy + 66 * s], 20, 160, fill=HAIR_W, outline=INK, width=5)  # barba
    cap(d, hx, hy, 48 * s, (232, 228, 218))
    return ex, ey


def researcher(d, x, y, s=1.0, arm_l=210, arm_r=330, look=(0, 0)):
    hipx, hipy = x, y
    capsule(d, (hipx - 20 * s, hipy + 6 * s), (hipx - 24 * s, hipy + 118 * s), 32 * s, (92, 84, 78))
    capsule(d, (hipx + 20 * s, hipy + 6 * s), (hipx + 24 * s, hipy + 118 * s), 32 * s, (92, 84, 78))
    for sgn in (-1, 1):
        orect(d, hipx + sgn * 24 * s - 24 * s, hipy + 116 * s, hipx + sgn * 24 * s + 12 * s, hipy + 140 * s, 10, (52, 46, 42), lw=5)
    # jaleco
    d.polygon([(hipx - 54 * s, hipy - 146 * s), (hipx + 54 * s, hipy - 146 * s),
               (hipx + 66 * s, hipy + 34 * s), (hipx - 66 * s, hipy + 34 * s)], fill=(226, 222, 210), outline=INK)
    d.line([(hipx - 54 * s, hipy - 146 * s), (hipx + 54 * s, hipy - 146 * s)], fill=INK, width=7)
    d.line([(hipx - 66 * s, hipy + 34 * s), (hipx + 66 * s, hipy + 34 * s)], fill=INK, width=7)
    d.line([(hipx, hipy - 146 * s), (hipx, hipy + 34 * s)], fill=INK, width=5)
    d.polygon([(hipx - 20 * s, hipy - 146 * s), (hipx + 20 * s, hipy - 146 * s), (hipx, hipy - 100 * s)], fill=(64, 120, 150), outline=INK, width=4)
    for sgn, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = hipx + sgn * 46 * s, hipy - 128 * s
        dx = math.sin(math.radians(ang)) * sgn * 88 * s
        dy = -math.cos(math.radians(ang)) * 88 * s
        ex, ey = shx + dx, shy + dy
        capsule(d, (shx, shy), (ex, ey), 24 * s, (226, 222, 210))
        hand(d, ex, ey, 12 * s)
    hx, hy = hipx + 4 * s, hipy - 192 * s
    face(d, hx, hy, 46 * s, skin=SKIN, hair_fn=hair_bun, look=look, grin=True)
    # óculos enormes
    for sgn in (-1, 1):
        oell(d, hx + sgn * 46 * s * 0.36, hy - 46 * s * 0.14, 46 * s * 0.30, 46 * s * 0.34, None, outline=INK, lw=6)
    oline(d, (hx - 46 * s * 0.06, hy - 46 * s * 0.14), (hx + 46 * s * 0.06, hy - 46 * s * 0.14), INK, 6)


def citizen(d, x, y, s=1.0, arm_r=340, look=(0, 0), cap_color=RED, shirt=(226, 210, 170)):
    hipx, hipy = x, y
    capsule(d, (hipx - 20 * s, hipy + 6 * s), (hipx - 24 * s, hipy + 118 * s), 32 * s, (70, 74, 90))
    capsule(d, (hipx + 20 * s, hipy + 6 * s), (hipx + 24 * s, hipy + 118 * s), 32 * s, (70, 74, 90))
    for sgn in (-1, 1):
        orect(d, hipx + sgn * 24 * s - 24 * s, hipy + 116 * s, hipx + sgn * 24 * s + 12 * s, hipy + 140 * s, 10, (40, 38, 44), lw=5)
    d.polygon([(hipx - 50 * s, hipy - 142 * s), (hipx + 50 * s, hipy - 142 * s),
               (hipx + 60 * s, hipy + 30 * s), (hipx - 60 * s, hipy + 30 * s)], fill=shirt, outline=INK)
    d.line([(hipx - 50 * s, hipy - 142 * s), (hipx + 50 * s, hipy - 142 * s)], fill=INK, width=7)
    d.line([(hipx - 60 * s, hipy + 30 * s), (hipx + 60 * s, hipy + 30 * s)], fill=INK, width=7)
    capsule(d, (hipx - 42 * s, hipy - 124 * s), (hipx - 78 * s, hipy - 20 * s), 24 * s, shirt)
    hand(d, hipx - 78 * s, hipy - 20 * s, 12 * s)
    shx, shy = hipx + 42 * s, hipy - 124 * s
    a = math.radians(arm_r)
    dx = math.sin(a) * 84 * s
    dy = -math.cos(a) * 84 * s
    ex, ey = shx + dx, shy + dy
    capsule(d, (shx, shy), (ex, ey), 24 * s, shirt)
    hx, hy = hipx + 4 * s, hipy - 186 * s
    face(d, hx, hy, 44 * s, skin=SKIN_B, hair_fn=hair_unkempt, look=look, grin=True)
    cap(d, hx, hy, 44 * s, cap_color)
    return ex, ey


def double(d, x, y, s=1.0, arm_r=350, look=(0, 0)):
    hipx, hipy = x, y
    capsule(d, (hipx - 20 * s, hipy + 6 * s), (hipx - 24 * s, hipy + 118 * s), 32 * s, (74, 82, 88))
    capsule(d, (hipx + 20 * s, hipy + 6 * s), (hipx + 24 * s, hipy + 118 * s), 32 * s, (74, 82, 88))
    for sgn in (-1, 1):
        orect(d, hipx + sgn * 24 * s - 24 * s, hipy + 116 * s, hipx + sgn * 24 * s + 12 * s, hipy + 140 * s, 10, (42, 44, 48), lw=5)
    d.polygon([(hipx - 50 * s, hipy - 142 * s), (hipx + 50 * s, hipy - 142 * s),
               (hipx + 60 * s, hipy + 30 * s), (hipx - 60 * s, hipy + 30 * s)], fill=(112, 120, 126), outline=INK)
    d.line([(hipx - 50 * s, hipy - 142 * s), (hipx + 50 * s, hipy - 142 * s)], fill=INK, width=7)
    d.line([(hipx - 60 * s, hipy + 30 * s), (hipx + 60 * s, hipy + 30 * s)], fill=INK, width=7)
    d.polygon([(hipx - 18 * s, hipy - 142 * s), (hipx + 18 * s, hipy - 142 * s), (hipx, hipy - 96 * s)], fill=SHIRT, outline=INK, width=4)
    capsule(d, (hipx - 42 * s, hipy - 124 * s), (hipx - 76 * s, hipy - 24 * s), 24 * s, (112, 120, 126))
    hand(d, hipx - 76 * s, hipy - 24 * s, 12 * s)
    shx, shy = hipx + 42 * s, hipy - 124 * s
    a = math.radians(arm_r)
    dx = math.sin(a) * 84 * s
    dy = -math.cos(a) * 84 * s
    ex, ey = shx + dx, shy + dy
    capsule(d, (shx, shy), (ex, ey), 24 * s, (112, 120, 126))
    hand(d, ex, ey, 12 * s)
    hx, hy = hipx + 4 * s, hipy - 186 * s
    face(d, hx, hy, 44 * s, skin=SKIN, hair_fn=None, look=look, grin=False)
    d.pieslice([hx - 44 * s, hy - 44 * s, hx + 44 * s, hy + 20 * s], 180, 360, fill=(150, 148, 144), outline=INK, width=6)  # cabelo grisalho
    for sgn in (-1, 1):  # óculos redondos
        oell(d, hx + sgn * 44 * s * 0.38, hy - 44 * s * 0.1, 44 * s * 0.26, 44 * s * 0.26, None, outline=INK, lw=6)
    oline(d, (hx - 4, hy - 4), (hx + 4, hy - 4), INK, 6)
    return ex, ey


def robot(d, x, y, s=1.0, arm_l=250, arm_r=290, glow_eye=True):
    hipx, hipy = x, y
    # pés
    for sgn in (-1, 1):
        orect(d, hipx + sgn * 30 * s - 26 * s, hipy + 116 * s, hipx + sgn * 30 * s + 26 * s, hipy + 142 * s, 10, SILVER_D, lw=5)
    # pernas
    capsule(d, (hipx - 30 * s, hipy + 4 * s), (hipx - 30 * s, hipy + 112 * s), 30 * s, SILVER_D)
    capsule(d, (hipx + 30 * s, hipy + 4 * s), (hipx + 30 * s, hipy + 112 * s), 30 * s, SILVER_D)
    # corpo
    orect(d, hipx - 62 * s, hipy - 150 * s, hipx + 62 * s, hipy + 10 * s, 18, SILVER, lw=7)
    # peito: luz
    oell(d, hipx, hipy - 70 * s, 20 * s, 20 * s, BLUE if glow_eye else SILVER_D, lw=5)
    d.line([(hipx - 40 * s, hipy - 30 * s), (hipx + 40 * s, hipy - 30 * s)], fill=SILVER_D, width=5)
    d.line([(hipx - 40 * s, hipy - 12 * s), (hipx + 40 * s, hipy - 12 * s)], fill=SILVER_D, width=5)
    # braços
    for sgn, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = hipx + sgn * 60 * s, hipy - 128 * s
        dx = math.sin(math.radians(ang)) * sgn * 78 * s
        dy = -math.cos(math.radians(ang)) * 78 * s
        ex, ey = shx + dx, shy + dy
        capsule(d, (shx, shy), (ex, ey), 24 * s, SILVER_D)
        orect(d, ex - 14 * s, ey - 14 * s, ex + 14 * s, ey + 14 * s, 8, SILVER, lw=5)
    # cabeça
    hx, hy = hipx, hipy - 208 * s
    oell(d, hx, hy, 52 * s, 46 * s, (198, 208, 210), lw=7)
    oell(d, hx, hy + 4 * s, 30 * s, 24 * s, (38, 52, 54), lw=5)
    d.ellipse([hx - 9 * s, hy - 4 * s, hx + 9 * s, hy + 12 * s], fill=BLUE)
    # antena
    oline(d, (hx, hy - 44 * s), (hx, hy - 76 * s), INK, 6)
    oell(d, hx, hy - 84 * s, 10 * s, 10 * s, ORANGE, lw=5)


def crowd_head(d, x, y, r, skin, up=0, arm_up=False):
    y -= up
    d.pieslice([x - r * 1.5, y + r * 0.5, x + r * 1.5, y + r * 3.2], 180, 360, fill=(52, 66, 64), outline=INK, width=5)  # ombros
    oell(d, x, y, r, r * 0.95, skin, lw=5)
    d.pieslice([x - r, y - r, x + r, y + r * 0.4], 180, 360, fill=CURL, outline=INK, width=5)
    if arm_up:
        capsule(d, (x + r * 1.2, y + r * 1.2), (x + r * 1.7, y - r * 0.4), 14, (52, 66, 64))


# ------------------------------------------------------------ cenarios -----

def lamp(d, x, y, s=1.0, color=GREEN):
    oline(d, (x, y - 90 * s), (x, y), INK, 7)
    d.pieslice([x - 46 * s, y - 60 * s, x + 46 * s, y + 40 * s], 180, 360, fill=(58, 128, 84), outline=INK, width=6)
    oell(d, x, y + 18 * s, 30 * s, 12 * s, color, lw=4)


def window_pane(d, x, y, w, h):
    orect(d, x, y, x + w, y + h, 14, (10, 34, 38), outline=INK, lw=8)
    orect(d, x + 12, y + 12, x + w - 12, y + h - 12, 10, (16, 52, 58), lw=5)


def banner(d, x, y, w, h, color, glyph="★"):
    d.polygon([(x, y), (x + w, y), (x + w, y + h - 18), (x + w / 2, y + h), (x, y + h - 18)], fill=color, outline=INK)
    d.line([(x, y), (x + w, y), (x + w, y + h - 18), (x + w / 2, y + h), (x, y + h - 18), (x, y)], fill=INK, width=6)
    txt(d, x + w / 2, y + h * 0.42, glyph, int(h * 0.4), (240, 236, 224))


def ballot_box(d, x, y, s=1.0):
    orect(d, x - 70 * s, y - 90 * s, x + 70 * s, y + 40 * s, 12, (190, 178, 150), lw=7)
    orect(d, x - 78 * s, y - 108 * s, x + 78 * s, y - 78 * s, 8, (205, 192, 160), lw=6)
    orect(d, x - 40 * s, y - 100 * s, x + 40 * s, y - 88 * s, 5, INK, lw=4)
    oell(d, x, y - 30 * s, 22 * s, 18 * s, (216, 208, 186), lw=5)  # olho do gigante (marca)
    oline(d, (x - 14 * s, y - 30 * s), (x + 14 * s, y - 30 * s), INK, 4)


def flyer(d, x, y, ang=0, s=1.0):
    box = [(x - 26 * s, y - 34 * s), (x + 26 * s, y - 34 * s), (x + 26 * s, y + 34 * s), (x - 26 * s, y + 34 * s)]
    if ang:
        c, ss = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        box = [(x + bx * c - by * ss, y + bx * ss + by * c) for (bx, by) in ((bx - x, by - y) for (bx, by) in box)]
    d.polygon(box, fill=PAPER, outline=INK)
    d.line(box + [box[0]], fill=INK, width=6)
    d.ellipse([x - 14 * s, y - 22 * s, x + 14 * s, y + 4 * s], fill=GOLD, outline=INK, width=4)
    d.rectangle([x - 18 * s, y + 10 * s, x + 18 * s, y + 16 * s], fill=(120, 110, 96))
    d.rectangle([x - 18 * s, y + 20 * s, x + 12 * s, y + 26 * s], fill=(120, 110, 96))


def coin(d, x, y, r=12):
    oell(d, x, y, r, r, GOLD, lw=4)
    txt(d, x, y + 1, "$", int(r * 1.1), GOLD_D)


def kiosk(d, x, y, s=1.0, screen_state=0, button_dy=0):
    # urna eletrônica
    orect(d, x - 90 * s, y - 210 * s, x + 90 * s, y + 60 * s, 16, (120, 132, 138), lw=8)
    orect(d, x - 70 * s, y - 190 * s, x + 70 * s, y - 96 * s, 10, (30, 44, 48), lw=6)
    cols = [(48, 66, 74), (70, 90, 104), (240, 240, 250)]
    d.rectangle([x - 58 * s, y - 178 * s, x + 58 * s, y - 108 * s], fill=cols[screen_state])
    if screen_state:
        # cédula + check
        d.rectangle([x - 30 * s, y - 170 * s, x + 30 * s, y - 130 * s], fill=(232, 220, 192), outline=INK, width=4)
        d.line([(x - 18 * s, y - 158 * s), (x - 4 * s, y - 144 * s), (x + 18 * s, y - 168 * s)], fill=(38, 150, 90), width=7)
    # teclado
    for i in range(3):
        for j in range(4):
            orect(d, x - 58 * s + j * 30 * s, y - 84 * s + i * 24 * s, x - 46 * s + j * 30 * s, y - 72 * s + i * 24 * s, 4, SILVER_D, lw=3)
    # botão grande
    oell(d, x + 58 * s, y - 40 * s + button_dy, 16 * s, 12 * s, RED if button_dy else (150, 50, 42), lw=5)
    # perna
    orect(d, x - 16 * s, y + 60 * s, x + 16 * s, y + 120 * s, 6, SILVER_D, lw=5)


def gavel(d, x, y, ang=90, s=1.0):
    """x,y = punho. ang=90 => cabo para cima."""
    a = math.radians(ang)
    dx, dy = math.sin(a) * 120 * s, -math.cos(a) * 120 * s
    ex, ey = x + dx, y + dy
    capsule(d, (x, y), (ex, ey), 20 * s, (168, 132, 84), lw=6)
    # cabeça do martelo perpendicular
    px, py = -dy, dx
    orect(d, ex - 34 * s, ey - 30 * s, ex + 34 * s, ey + 30 * s, 12, (150, 112, 66), lw=7)
    orect(d, ex - 44 * s, ey - 40 * s, ex - 30 * s, ey + 40 * s, 8, (120, 88, 50), lw=5)
    orect(d, ex + 30 * s, ey - 40 * s, ex + 44 * s, ey + 40 * s, 8, (120, 88, 50), lw=5)


def cloud(d, x, y, s=1.0, fill=(238, 240, 240)):
    for cx, cy, r in [(-60, 10, 34), (0, -14, 44), (58, 8, 36)]:
        d.ellipse([x + cx * s - r * s, y + cy * s - r * s, x + cx * s + r * s, y + cy * s + r * s], fill=fill, outline=INK, width=6)
    d.chord([x - 90 * s, y, x + 90 * s, y + 52 * s], 0, 180, fill=fill, outline=INK, width=6)


def sun(d, x, y, r=46, smile=True):
    for i in range(8):
        a = math.radians(i * 45)
        oline(d, (x + math.cos(a) * (r + 8), y + math.sin(a) * (r + 8)),
              (x + math.cos(a) * (r + 26), y + math.sin(a) * (r + 26)), GOLD, 8)
    oell(d, x, y, r, r, (250, 208, 82), lw=6)
    if smile:
        d.arc([x - r * 0.5, y - r * 0.2, x + r * 0.5, y + r * 0.5], 20, 160, fill=INK, width=6)
        d.ellipse([x - r * 0.34 - 5, y - r * 0.3 - 5, x - r * 0.34 + 5, y - r * 0.3 + 5], fill=INK)
        d.ellipse([x + r * 0.34 - 5, y - r * 0.3 - 5, x + r * 0.34 + 5, y - r * 0.3 + 5], fill=INK)


def confetti(d, n, y0, y1, seed, cx=640, spread=560, palette=None):
    rnd = random.Random(seed)
    palette = palette or [GOLD, ORANGE, (255, 255, 255, 255), RED, BLUE]
    for i in range(n):
        x = cx + rnd.randint(-spread, spread)
        y = rnd.randint(y0, y1)
        c = rnd.choice(palette)
        d.rectangle([x - 6, y - 9, x + 6, y + 9], fill=c[:3], outline=INK, width=2)


# -------------------------------------------------------------- cenas ------

def scene_p1_09():
    """Fantoches: o Grifter puxa as cordas; o boneco sobe e desce. (roxo)"""
    frames = []
    for i, (bar_y, pup_y, pup_tilt, arm_r, crown_dy, sp) in enumerate([
        (330, 300, 7, 20, 0, False),
        (290, 250, -4, 40, -10, False),
        (260, 205, -9, 55, -22, True),
        (300, 260, 4, 30, -6, False),
    ]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        # palcos/plateia
        orect(d, 60, 470, 1220, 560, 10, (52, 42, 40), lw=6)
        d.line([(60, 470), (1220, 470)], fill=INK, width=8)
        # cortina
        d.rectangle([60, 60, 1220, 210], fill=(120, 30, 30), outline=INK, width=7)
        for x in range(100, 1200, 120):
            d.pieslice([x - 40, 150, x + 40, 260], 0, 180, fill=(96, 24, 24), outline=INK, width=5)
        d.line([(60, 210), (1220, 210)], fill=INK, width=8)
        # Grifter
        grifter(d, 330, 420, s=0.92, arm_r=95 + (i % 2) * 6, look=(1, 0))
        # barra de marionete
        bx0, bx1 = 430, 640
        oline(d, (bx0, bar_y), (bx1, bar_y), (150, 112, 66), 16)
        oline(d, (bx0 - 8, bar_y), (bx0 + 8, bar_y), INK, 20)
        oline(d, (bx1 - 8, bar_y), (bx1 + 8, bar_y), INK, 20)
        # cordas + boneco
        px, py = 880, pup_y
        for sx in (bx1 - 40, bx1 + 40):
            oline(d, (sx, bar_y), (px - 20 + (10 if sx < bx1 else 30), py - 120), (230, 228, 220), 4)
        # boneco
        c, ss = math.cos(math.radians(pup_tilt)), math.sin(math.radians(pup_tilt))
        def R(bx, by):
            dx, dy = bx - px, by - py
            return px + dx * c - dy * ss, py + dx * ss + dy * c
        body = [R(px - 34, py - 110), R(px + 34, py - 110), R(px + 44, py + 10), R(px - 44, py + 10)]
        d.polygon(body, fill=(60, 66, 92), outline=INK)
        d.line(body + [body[0]], fill=INK, width=6)
        for sgn in (-1, 1):
            a0 = R(px + sgn * 34, py - 96)
            a1 = R(px + sgn * 74, py - 60 + (14 if sgn > 0 else 30))
            capsule(d, a0, a1, 18, (60, 66, 92))
        for sgn in (-1, 1):
            l0 = R(px + sgn * 20, py + 10)
            l1 = R(px + sgn * 24, py + 90)
            capsule(d, l0, l1, 20, (60, 66, 92))
        hx, hy = R(px, py - 158)
        oell(d, hx, hy, 30, 32, SKIN, lw=6)
        d.pieslice([hx - 30, hy - 32, hx + 30, hy + 8], 180, 360, fill=(120, 116, 110), outline=INK, width=5)
        d.ellipse([hx - 16, hy - 6, hx - 6, hy + 4], fill=INK)
        d.ellipse([hx + 6, hy - 6, hx + 16, hy + 4], fill=INK)
        d.arc([hx - 14, hy + 6, hx + 14, hy + 26], 20, 160, fill=INK, width=5)
        # coroa flutuando
        cxx, cyy = px + 30, py - 218 + crown_dy
        d.polygon([(cxx - 22, cyy + 14), (cxx - 22, cyy - 10), (cxx - 8, cyy + 2), (cxx, cyy - 18),
                   (cxx + 8, cyy + 2), (cxx + 22, cyy - 10), (cxx + 22, cyy + 14)], fill=GOLD, outline=INK, width=5)
        if sp:
            sparkle(d, cxx + 34, cyy - 12, 12, PURPLE)
            sparkle(d, cxx - 30, cyy + 16, 9, PURPLE)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 880, 430, 150, PURPLE, 18)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p1_10():
    """Clima: o SOL/CHUVA alterna — alavanca, sol, nuvem e chuva cômica. (verde)"""
    frames = []
    states = [
        dict(lever=-38, sun_y=150, cloud_y=300, rain=0, peek=0),
        dict(lever=0, sun_y=150, cloud_y=250, rain=0, peek=0),
        dict(lever=38, sun_y=210, cloud_y=150, rain=3, peek=1),
        dict(lever=-38, sun_y=150, cloud_y=300, rain=1, peek=0),
    ]
    for st in states:
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        # janela redonda com céu
        oell(d, 330, 250, 210, 210, (70, 110, 130), outline=INK, lw=10)
        d.ellipse([330 - 196, 250 - 196, 330 + 196, 250 + 196], fill=(120, 160, 180), outline=INK, width=8)
        cx, cy = 330, 250
        if st["peek"]:
            sun(d, cx - 120, cy + 120, r=40, smile=False)
        else:
            sun(d, cx - 90, st["sun_y"], r=52)
        cloud(d, cx + 40, st["cloud_y"], s=1.5)
        if st["rain"]:
            for i in range(st["rain"]):
                rx = cx - 40 + i * 44
                ry = st["cloud_y"] + 90 + (i * 26) % 60
                d.polygon([(rx, ry - 18), (rx - 10, ry + 10), (rx + 10, ry + 10)], fill=(90, 170, 230), outline=INK, width=4)
        d.ellipse([330 - 196, 250 - 196, 330 + 196, 250 + 196], outline=INK, width=8)
        # painel
        orect(d, 660, 300, 1180, 600, 18, (54, 70, 68), lw=8)
        orect(d, 690, 330, 1150, 430, 12, (30, 44, 42), lw=6)
        # ícones no painel (sol / nuvem)
        sun(d, 780, 380, r=26, smile=False)
        cloud(d, 1050, 380, s=0.8)
        # alavanca
        ax, ay = 930, 520
        oell(d, ax, ay, 46, 40, (40, 54, 52), lw=6)
        a = math.radians(90 + st["lever"])
        ex, ey = ax + math.sin(a) * 110, ay - math.cos(a) * 110
        capsule(d, (ax, ay), (ex, ey), 18, SILVER, lw=6)
        oell(d, ex, ey, 22, 22, RED, lw=6)
        # luzes do painel
        for i in range(5):
            on = i < (2 if st["lever"] >= 0 else 3)
            oell(d, 720 + i * 46, 470, 12, 12, GREEN if on else (46, 60, 58), lw=4)
        # Grifter ao lado
        grifter(d, 1150, 470, s=0.8, arm_r=245, look=(-1, 0))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 330, 250, 140, GREEN, 16)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_01():
    """Voto do tio: santinho + moedas no sofá; o voto cai na urna. (dourado)"""
    frames = []
    states = [
        dict(fx=150, fy=300, uncle_arm=240, coins=[(200, 380)], box=None, flyer_who="hand", eyes=(-0.6, 0.5)),
        dict(fx=300, fy=280, uncle_arm=270, coins=[(240, 420), (300, 470)], box=None, flyer_who="hand", eyes=(-0.3, 0.3)),
        dict(fx=430, fy=330, uncle_arm=290, coins=[(330, 500), (400, 540), (300, 560)], box=None, flyer_who="uncle", eyes=(0, 0)),
        dict(fx=None, fy=None, uncle_arm=60, coins=[], box=880, flyer_who="box", eyes=(0.6, 0.2)),
    ]
    for st in states:
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        # TV estática
        orect(d, 80, 150, 300, 330, 14, (60, 74, 78), lw=8)
        d.rectangle([100, 170, 280, 310], fill=(150, 160, 160))
        rnd = random.Random(9)
        for _ in range(120):
            x, y = rnd.randint(100, 276), rnd.randint(170, 306)
            c = rnd.choice([(210, 214, 214), (110, 118, 118), (70, 78, 78)])
            d.rectangle([x, y, x + 8, y + 6], fill=c)
        oline(d, (140, 150), (120, 110), (60, 74, 78), 8)
        oline(d, (240, 150), (260, 110), (60, 74, 78), 8)
        # sofá
        orect(d, 380, 330, 900, 560, 26, (122, 84, 60), lw=8)
        orect(d, 360, 300, 440, 560, 20, (108, 72, 52), lw=7)
        orect(d, 820, 300, 900, 560, 20, (108, 72, 52), lw=7)
        orect(d, 400, 340, 820, 470, 20, (134, 94, 66), lw=6)
        # tio
        handpos = uncle(d, 640, 470, s=1.0, arm_r=st["uncle_arm"], look=st["eyes"])
        # cédula na mão do tio (quando ele segura)
        if st["flyer_who"] in ("uncle", "box"):
            flyer(d, handpos[0], handpos[1], ang=12)
        if st["flyer_who"] == "box":
            ballot_box(d, st["box"], 560, s=1.0)
            # cédula indo pra boca
            d.polygon([(handpos[0] - 14, handpos[1] - 18), (handpos[0] + 14, handpos[1] - 18),
                       (handpos[0] + 10, handpos[1] + 16), (handpos[0] - 10, handpos[1] + 16)], fill=PAPER, outline=INK, width=4)
        # braço do Grifter da borda esquerda
        if st["flyer_who"] == "hand":
            ex, ey = grifter_arm(d, -20, 320, s=1.0, ang=80)
            dx, dy = ex - st["fx"], ey - st["fy"]
            flyer(d, st["fx"], st["fy"], ang=8)
            coin(d, st["fx"] - 18, st["fy"] + 44)
            coin(d, st["fx"] + 16, st["fy"] + 56)
        for (cx, cy) in st["coins"]:
            coin(d, cx, cy, 13)
        lamp(d, 1150, 330, s=1.0, color=(240, 220, 150))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 260, 330, 110, GOLD, 18)
        if st["flyer_who"] == "box":
            sparkle(d, st["box"], 470, 14, GOLD)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_02():
    """Pesquisa 99%: o pesquisador gira o dial e a barra sobe até 99%. (azul)"""
    frames = []
    states = [
        dict(bar=0.42, needle=-80, arm=210, pct=None),
        dict(bar=0.72, needle=10, arm=220, pct=None),
        dict(bar=0.99, needle=80, arm=180, pct="99%"),
        dict(bar=0.99, needle=80, arm=165, pct="99%"),
    ]
    for i, st in enumerate(states):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        # gráfico de parede
        orect(d, 480, 90, 1210, 420, 16, (14, 40, 36), lw=8)
        d.line([(510, 390), (1180, 390)], fill=(90, 120, 112), width=5)
        bars = [(600, 0.30), (845, st["bar"]), (1090, 0.22)]
        jx = 0
        if i == 3:
            jx = 4
        for (bx, bh) in bars:
            top = 390 - bh * 280
            col = BLUE if bx == 845 else (60, 90, 100)
            orect(d, bx - 60, top + (jx if bx == 845 else 0), bx + 60, 390, 10, col, lw=7)
        # topo brilhante da barra grande
        if i >= 1:
            top = 390 - st["bar"] * 280 + (jx if i == 3 else 0)
            d.rectangle([845 - 60, top, 845 + 60, top + 16], fill=(210, 240, 255), outline=INK, width=5)
        if st["pct"]:
            txt(d, 845, 130, st["pct"], 74, BLUE)
        # console + dial
        orect(d, 90, 330, 380, 560, 14, (54, 70, 68), lw=8)
        orect(d, 120, 360, 350, 430, 10, (30, 44, 42), lw=6)
        dxc, dyv = 235, 490
        oell(d, dxc, dyv, 62, 62, (38, 52, 52), lw=7)
        for a in range(0, 361, 30):
            oline(d, (dxc + math.cos(math.radians(a - 90)) * 46, dyv + math.sin(math.radians(a - 90)) * 46),
                  (dxc + math.cos(math.radians(a - 90)) * 56, dyv + math.sin(math.radians(a - 90)) * 56), (120, 150, 144), 4)
        na = math.radians(st["needle"])
        oline(d, (dxc, dyv), (dxc + math.sin(na) * 44, dyv - math.cos(na) * 44), RED, 9)
        oell(d, dxc, dyv, 10, 10, RED, lw=4)
        # pesquisadora
        researcher(d, 640, 470, s=1.0, arm_r=st["arm"], look=(1, -0.3))
        # prancheta
        orect(d, 760, 400, 830, 480, 8, PAPER, lw=5)
        d.rectangle([770, 415, 820, 470], fill=(200, 190, 170), outline=INK, width=3)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if i >= 1:
            top = 390 - st["bar"] * 280
            glow(ov, 845, top, 90, BLUE, 60)
        if i == 3:
            glow(ov, 845, 130, 110, BLUE, 70)
            sparkle(d, 940, 170, 13, BLUE)
            sparkle(d, 760, 150, 10, BLUE)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_04():
    """Emenda pública: a caneta assina e as letras saem voando. (dourado)"""
    frames = []
    states = [
        dict(pen_dy=-18, ink=0, flies=[], seal=False),
        dict(pen_dy=0, ink=0.35, flies=[], seal=False),
        dict(pen_dy=4, ink=0.75, flies=[(-0.10, -0.25), (-0.22, -0.42)], seal=False),
        dict(pen_dy=0, ink=1.0, flies=[(-0.16, -0.30), (-0.30, -0.52), (-0.05, -0.14)], seal=True),
    ]
    for st in states:
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        # mesa
        orect(d, 120, 430, 1160, 500, 12, (96, 72, 50), lw=8)
        d.line([(120, 430), (1160, 430)], fill=INK, width=9)
        # suporte + pergaminho
        orect(d, 420, 500, 470, 560, 8, (80, 60, 44), lw=6)
        orect(d, 830, 500, 880, 560, 8, (80, 60, 44), lw=6)
        orect(d, 380, 130, 920, 470, 14, PAPER, lw=8)
        # linhas do documento
        for i in range(5):
            d.rectangle([430, 190 + i * 40, 870 - (80 if i else 0), 202 + i * 40], fill=(170, 158, 132))
        # linha de assinatura
        d.line([(450, 410), (850, 410)], fill=(120, 108, 88), width=4)
        # rabiola da assinatura
        if st["ink"]:
            t = st["ink"]
            pts = []
            for i in range(int(40 * t) + 1):
                u = i / 40.0
                px = 470 + u * 300
                py = 400 + math.sin(u * 9) * 14 * (1 - u * 0.4) - (u * 6)
                pts.append((px, py))
            if len(pts) > 1:
                d.line(pts, fill=INK, width=7)
                if t > 0.9:
                    d.line([(470, 428), (790, 428)], fill=INK, width=6)
        # letras voando (bloquinhos abstratos)
        for (fx, fy) in st["flies"]:
            lx, ly = 840 + fx * 500, 380 + fy * 500
            orect(d, lx - 14, ly - 9, lx + 14, ly + 9, 4, (90, 82, 70), lw=3)
            orect(d, lx + 20, ly - 5, lx + 34, ly + 5, 3, (120, 110, 96), lw=3)
        # lacre dourado
        if st["seal"]:
            oell(d, 850, 440, 26, 22, GOLD, lw=6)
            d.arc([838, 430, 862, 452], 40, 300, fill=GOLD_D, width=4)
        # mão + caneta da borda direita
        mx, my = 1150, 360
        orect(d, 1150, 330, 1290, 400, 14, COAT_D, lw=7)  # manga
        hx, hy = 1090, 380 + st["pen_dy"]
        capsule(d, (1160, 366), (hx, hy), 30, COAT_D)
        hand(d, hx, hy, 15)
        # caneta ornada
        capsule(d, (hx - 8, hy - 6), (hx - 74, hy - 44 + st["pen_dy"]), 12, GOLD, lw=5)
        d.polygon([(hx - 74, hy - 50 + st["pen_dy"]), (hx - 96, hy - 30 + st["pen_dy"]), (hx - 62, hy - 34 + st["pen_dy"])],
                  fill=(240, 236, 226), outline=INK, width=4)
        lamp(d, 220, 300, s=1.2, color=(240, 220, 150))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 620, 400, 150, GOLD, 34)
        if st["seal"]:
            glow(ov, 850, 440, 80, GOLD, 90)
            sparkle(d, 900, 410, 13, GOLD)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_05():
    """Plenária de robôs: o robô digita e as luzes acendem fila a fila. (azul)"""
    frames = []

    def rows(d, lit):
        for row in range(3):
            ry = 400 + row * 70
            rw = 340 + row * 220
            n = 5 + row * 2
            for i in range(n):
                rx = 640 - rw / 2 + (rw / n) * (i + 0.5)
                orect(d, rx - 46, ry, rx + 46, ry + 34, 8, (58, 76, 74), lw=5)
                on = row >= (2 - lit)
                oell(d, rx, ry + 10, 9, 9, BLUE if on else (36, 48, 48), lw=4)
                if on:
                    d.ellipse([rx - 14, ry + 2, rx + 14, ry + 18], outline=(*BLUE, 90), width=3)

    for i, (typing, lit, thumb) in enumerate([(0, 0, False), (1, 1, False), (2, 2, False), (0, 3, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 380)
        rows(d, lit)
        # púlpito central
        orect(d, 480, 300, 800, 400, 12, (54, 70, 68), lw=8)
        # robô
        robot(d, 640, 300, s=1.05, arm_l=250 if typing else 220, arm_r=290 if typing else 340,
              glow_eye=True)
        # linhas de digitação
        if typing:
            for k in range(typing + 1):
                oline(d, (540 - k * 14, 330 + k * 8), (560 - k * 14, 322 + k * 8), (200, 220, 224), 5)
        if thumb:
            sparkle(d, 760, 150, 14, BLUE)
            sparkle(d, 540, 120, 10, BLUE)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if i == 3:
            glow(ov, 640, 240, 120, BLUE, 28)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_06():
    """Cabo com megafone: o grito faz ondas e a plateia rebola. (vermelho)"""
    frames = []
    skins = [SKIN, SKIN_B, (170, 120, 86), (226, 186, 148), (150, 104, 74)]
    for i, (arcs, bounces, arm_up) in enumerate([(0, [], -1), (1, [2], -1), (3, [0, 3], -1), (2, [1, 4], 2)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 520)
        # multidão (direita)
        for k in range(5):
            x = 780 + k * 95
            up = 16 if k in bounces else 0
            crowd_head(d, x, 470 - up, 44, skins[k], up=0, arm_up=(k == arm_up))
        # cidadão com megafone
        hx, hy = citizen(d, 330, 420, s=1.1, arm_r=8 if i else 30, look=(1, 0), cap_color=RED)
        # megafone na mão (ângulo 8 = quase horizontal p/ direita)
        if i:
            mx, my = hx + 26, hy - 6
            d.polygon([(mx - 18, my - 16), (mx + 26, my - 34), (mx + 26, my + 34), (mx - 18, my + 16)], fill=ORANGE, outline=INK)
            d.line([(mx - 18, my - 16), (mx + 26, my - 34), (mx + 26, my + 34), (mx - 18, my + 16), (mx - 18, my - 16)], fill=INK, width=6)
            oell(d, mx + 26, my, 34, 34, (230, 170, 80), lw=6)
            for a in range(arcs):
                rr = 66 + a * 30
                arc_line(d, mx + 40, my, rr, -52, 52, (255, 120, 100), width=7, a=200)
            if i == 2:
                sparkle(d, mx + 70, my - 50, 12, RED)
                sparkle(d, mx + 60, my + 44, 9, RED)
        else:
            d.polygon([(hx - 6, hy + 8), (hx + 30, hy - 8), (hx + 30, hy + 44), (hx - 6, hy + 58)], fill=ORANGE, outline=INK, width=6)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 330, 380, 130, RED, 14)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_07():
    """Comício em dupla: os dois prometem com a mão no peito + confete. (laranja)"""
    frames = []
    for i, (conf, guitar_up, strum) in enumerate([(0, 0, 0), (0, 0, 1), (14, 0, 2), (20, 1, 2)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 520)
        # palco
        orect(d, 180, 400, 1100, 520, 10, (84, 66, 54), lw=8)
        d.line([(180, 400), (1100, 400)], fill=INK, width=9)
        # backdrop com estrelas abstratas
        orect(d, 300, 90, 980, 330, 14, (30, 52, 50), lw=8)
        for (sx, sy, sr) in [(420, 160, 16), (640, 130, 20), (860, 170, 14), (520, 260, 12), (760, 260, 15)]:
            sparkle(d, sx, sy, sr, (120, 150, 148), 255)
        banner(d, 380, 40, 220, 64, (150, 60, 50), "♥")
        banner(d, 700, 40, 220, 64, (60, 90, 120), "★")
        # dupla sertaneja
        for k, (sx, beard, hat_tilt) in enumerate([(520, True, 6), (760, False, -6)]):
            # guitarra
            if guitar_up and k == 0:
                ga = -30
            else:
                ga = 30
                # corpo
            d.polygon([(sx - 46, 270 - 142), (sx + 46, 270 - 142), (sx + 56, 270 + 30), (sx - 56, 270 + 30)], fill=(238, 234, 224), outline=INK)
            d.line([(sx - 46, 270 - 142), (sx + 46, 270 - 142)], fill=INK, width=7)
            d.line([(sx - 56, 270 + 30), (sx + 56, 270 + 30)], fill=INK, width=7)
            # pernas
            for sgn in (-1, 1):
                capsule(d, (sx + sgn * 20, 270 + 30), (sx + sgn * 24, 270 + 140), 30, (90, 80, 70))
                orect(d, sx + sgn * 24 - 22, 270 + 138, sx + sgn * 24 + 16, 270 + 162, 10, (48, 42, 38), lw=5)
            # guitarra (braço da banda)
            nx, ny = sx + 66, 320 - 40 * guitar_up * (1 if k == 0 else 0)
            oline(d, (nx, ny), (nx + 90, ny - 70 - 40 * guitar_up * (1 if k == 0 else 0)), (120, 84, 52), 12)
            oell(d, nx, ny, 34, 30, (170, 120, 66), lw=6)
            oell(d, nx, ny, 10, 9, (60, 44, 34), lw=4)
            # braço p/ o peito (ou strum)
            shx, shy = sx - 40, 270 - 128
            if strum and k == 1:
                exx, eyy = nx - 26, ny + 6
            else:
                exx, eyy = sx - 6, 270 - 78
            capsule(d, (shx, shy), (exx, eyy), 22, (238, 234, 224))
            hand(d, exx, eyy, 12)
            if strum and k == 1:
                arc_line(d, nx, ny, 44, 200, 320, (200, 220, 224), 5, 180)
            # braço oposto na cintura
            capsule(d, (sx + 40, 270 - 128), (sx + 62, 270 - 60), 22, (238, 234, 224))
            hand(d, sx + 62, 270 - 60, 12)
            # cabeça
            hx, hy = sx, 270 - 186
            face(d, hx, hy, 42, skin=SKIN, hair_fn=None, look=(0, 0), grin=True)
            if beard:
                d.pieslice([hx - 40, hy + 16, hx + 40, hy + 62], 20, 160, fill=(90, 76, 66), outline=INK, width=5)
            # chapéu
            d.pieslice([hx - 48, hy - 62, hx + 48, hy + 6], 180, 360, fill=(60, 50, 44), outline=INK, width=6)
            d.ellipse([hx - 62, hy - 20, hx + 62, hy + 4], fill=(60, 50, 44), outline=INK, width=6)
        if conf:
            confetti(d, conf, 60, 260 + i * 60, seed=11 + i)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 640, 210, 200, ORANGE, 14)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_08():
    """Constituição do Zap: mensagens viram artigos no pergaminho. (verde)"""
    frames = []
    states = [
        dict(t=0.35, lines=1, chev=0),
        dict(t=1.0, lines=2, chev=0, poof=True),
        dict(t=0.35, lines=2, chev=3),
        dict(t=0.72, lines=3, chev=3, sp=True),
    ]
    for st in states:
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        # mesa
        orect(d, 80, 470, 1200, 540, 12, (96, 72, 50), lw=8)
        # pergaminho em suporte
        orect(d, 240, 540, 290, 600, 8, (80, 60, 44), lw=6)
        orect(d, 640, 540, 690, 600, 8, (80, 60, 44), lw=6)
        orect(d, 200, 130, 780, 520, 14, PAPER, lw=8)
        # artigos (linhas com número)
        for i in range(3):
            if i < st["lines"]:
                y = 220 + i * 90
                oell(d, 260, y, 16, 16, GREEN_D, lw=4)
                d.rectangle([300, y - 8, 720 - (60 * (i % 2)), y + 8], fill=(150, 138, 112))
                d.rectangle([300, y + 18, 640, y + 30], fill=(180, 168, 140))
        # balão de chat (verde, canto sup. dir.)
        orect(d, 860, 100, 1200, 330, 26, (38, 178, 110), lw=8)
        d.polygon([(920, 330), (880, 400), (980, 330)], fill=(38, 178, 110), outline=INK, width=6)
        for i, full in enumerate([(True), (True), (False)]):
            y = 150 + i * 64
            if full:
                orect(d, 890, y, 1130 - (90 * (i % 2)), y + 44, 20, (222, 246, 230), lw=5)
                d.rectangle([906, y + 12, 1100 - (90 * (i % 2)), y + 30], fill=(120, 160, 140))
            else:
                orect(d, 890, y, 1080, y + 44, 20, (38, 178, 110), outline=(210, 250, 226), lw=4)
        # mensagem em voo: trajetória de (940, 300) até (660, 340)
        fx = 940 + (660 - 940) * st["t"]
        fy = 300 + (340 - 300) * st["t"] - math.sin(st["t"] * math.pi) * 60
        orect(d, fx - 34, fy - 20, fx + 34, fy + 20, 16, (222, 246, 230), lw=5)
        d.rectangle([fx - 22, fy - 8, fx + 22, fy + 6], fill=(120, 160, 140))
        if st.get("poof"):
            ring(d, 660, 340, 34, GREEN, 6, 160)
        # chevrons "encaminhando"
        for c in range(st["chev"]):
            cx = 1160 - c * 34
            d.polygon([(cx, 356), (cx + 16, 372), (cx, 388), (cx - 8, 388), (cx + 8, 372), (cx - 8, 356)], fill=GREEN, outline=INK, width=3)
        lamp(d, 140, 330, s=1.2, color=(240, 220, 150))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 1030, 215, 140, GREEN, 22)
        if st.get("sp"):
            sparkle(d, 1150, 120, 13, GREEN)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_09():
    """Sósia por procuração: o botão fecha, a urna brilha, o carimbo cai. (roxo)"""
    frames = []
    states = [
        dict(b=0, scr=0, ring=False, stamp=False, look=(1, 0)),
        dict(b=6, scr=1, ring=True, stamp=False, look=(1, 0.2)),
        dict(b=6, scr=2, ring=False, stamp=False, look=(1, 0.4)),
        dict(b=0, scr=1, ring=False, stamp=True, look=(0, -0.2)),
    ]
    for st in states:
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        # tapume/fundo de votação
        for x in range(0, W, 160):
            d.polygon([(x, 90), (x + 160, 90), (x + 140, 420), (x + 20, 420)], fill=(120, 128, 132), outline=INK, width=5)
        kiosk(d, 780, 560, s=1.1, screen_state=st["scr"], button_dy=st["b"])
        # sósia
        arm = 90 if st["scr"] < 3 else 8
        hx, hy = double(d, 360, 440, s=1.05, arm_r=arm, look=st["look"])
        if st["stamp"]:
            orect(d, hx - 14, hy + 4, hx + 14, hy + 26, 8, SKIN, lw=5)  # polegar em cima
            # carimbo gigante roxo
            sx, sy = 980, 220
            ring(d, sx, sy, 84, PURPLE, 14, 230)
            for i in range(3):
                d.rectangle([sx - 46, sy - 34 + i * 28, sx + 46, sy - 16 + i * 28], fill=PURPLE)
            sparkle(d, sx + 100, sy - 60, 14, PURPLE)
            sparkle(d, sx - 96, sy + 56, 10, PURPLE)
        if st["ring"]:
            ring(d, 830, 514, 40, PURPLE, 6, 150)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if st["scr"]:
            glow(ov, 780, 420, 100, PURPLE, 32)
        if st["stamp"]:
            glow(ov, 980, 220, 120, PURPLE, 44)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p2_10():
    """Proclamar a Democracia Relativa™: o martelo bate e o 50% aparece. (dourado)"""
    frames = []
    states = [
        dict(gav=95, impact=False, banner=False, conf=0, crowd_up=0),
        dict(gav=178, impact=False, banner=False, conf=0, crowd_up=10),
        dict(gav=135, impact=True, banner=False, conf=0, crowd_up=4),
        dict(gav=95, impact=False, banner=True, conf=18, crowd_up=14),
    ]
    for st in states:
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 540)
        # multidão
        skins = [SKIN, SKIN_B, (170, 120, 86), (226, 186, 148), (150, 104, 74), (210, 170, 130), (186, 138, 100)]
        for k in range(7):
            x = 120 + k * 170 + (40 if k % 2 else 0)
            crowd_head(d, x, 520, 46, skins[k], up=st["crowd_up"], arm_up=(k in (1, 5)))
        # púlpito
        orect(d, 520, 430, 760, 560, 10, (96, 72, 50), lw=8)
        d.line([(520, 430), (760, 430)], fill=INK, width=9)
        orect(d, 545, 400, 735, 430, 8, (120, 90, 62), lw=6)
        # Grifter no púlpito
        grifter(d, 640, 380, s=0.95, arm_r=st["gav"] - 90 + 90, look=(0, -0.3))
        # martelo (na mão direita)
        shx, shy = 640 + 46 * 0.95, 380 - 138 * 0.95
        a = math.radians(st["gav"])
        dx = math.sin(a) * 110 * 0.95
        dy = -math.cos(a) * 110 * 0.95
        gavel(d, shx + dx, shy + dy, ang=st["gav"] + 100, s=1.0)
        if st["impact"]:
            sparkle(d, 800, 405, 26, (255, 240, 200))
            d.polygon([(768, 402), (776, 380), (790, 400), (806, 384), (812, 408)], fill=(255, 240, 200), outline=INK, width=4)
        if st["banner"]:
            # bandeirão 50%
            orect(d, 340, 90, 940, 250, 18, GOLD, lw=10)
            d.polygon([(340, 250), (940, 250), (900, 300), (380, 300)], fill=GOLD_D, outline=INK, width=8)
            txt(d, 640, 172, "50%", 110, INK)
            oline(d, (340, 90), (320, 60), (120, 90, 62), 10)
            oline(d, (940, 90), (960, 60), (120, 90, 62), 10)
        if st["conf"]:
            confetti(d, st["conf"], 40, 300, seed=21)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 640, 300, 160, GOLD, 16)
        if st["banner"]:
            glow(ov, 640, 170, 170, GOLD, 40)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


SCENES = {
    "p1_09": scene_p1_09,
    "p1_10": scene_p1_10,
    "p2_01": scene_p2_01,
    "p2_02": scene_p2_02,
    "p2_04": scene_p2_04,
    "p2_05": scene_p2_05,
    "p2_06": scene_p2_06,
    "p2_07": scene_p2_07,
    "p2_08": scene_p2_08,
    "p2_09": scene_p2_09,
    "p2_10": scene_p2_10,
}


def main():
    ids = sys.argv[1:] if len(sys.argv) > 1 else list(SCENES)
    for sid in ids:
        fn = SCENES.get(sid)
        if fn is None:
            sys.exit(f"cena desconhecida: {sid}")
        frames = fn()
        d = ROOT / "src" / "assets" / "anim" / sid / "frames"
        d.mkdir(parents=True, exist_ok=True)
        for i, im in enumerate(frames):
            im.save(d / f"f{i:02d}.png")
        print(f"[{sid}] 4 keyframes desenhados ({W}x{H})")


if __name__ == "__main__":
    main()

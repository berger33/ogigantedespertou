#!/usr/bin/env python3
"""scene_draw2.py — keyframes desenhados (código) para as 21 cenas dos lotes E/F/G
que a quota de geração de imagem não cobriu. Mesmo padrão flat-toon do
scene_draw.py: outline grosso, cores chapadas, dark teal + 1 acento por missão,
elenco e verbo únicos por cena. Quadros: frames/f00..f03.png (fora do Git).

Uso: python3 tools/scene_draw2.py [id ...]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scene_draw as sd
from scene_draw import (
    INK, SKIN, SKIN_B, COAT_D, SHIRT, TIE, GOLD, GREEN, BLUE, PURPLE, RED,
    ORANGE, PAPER, SILVER, CURL,
    orect, oell, oline, capsule, hand, glow, sparkle, ring, txt, arc_line,
    font, new_frame, bg, grifter, lamp, cloud, sun, coin, cap,
)


ROOT = sd.ROOT
W, H = sd.W, sd.H


# -------------------------------------------------- helpers novos -----------

def spiral(d, cx, cy, r, color, width=4, a=190):
    """Espiral simples (substituto de arc_spiral, que só existe no build_motion)."""
    for k in range(3):
        rr = max(3, r * (1 - k * 0.3))
        arc_line(d, cx, cy, rr, -90 + k * 70, 140 + k * 70, color, width, a)


def car(d, x, y, s=1.0, color=(150, 70, 60)):
    orect(d, x - 62 * s, y - 26 * s, x + 62 * s, y + 14 * s, 12, color, lw=6)
    orect(d, x - 34 * s, y - 48 * s, x + 30 * s, y - 22 * s, 10, (60, 74, 80), lw=5)
    d.rectangle([x - 26 * s, y - 42 * s, x - 4 * s, y - 26 * s], fill=(140, 190, 210))
    d.rectangle([x + 4 * s, y - 42 * s, x + 24 * s, y - 26 * s], fill=(140, 190, 210))
    for wx in (-38, 34):
        oell(d, x + wx * s, y + 16 * s, 16 * s, 16 * s, (30, 34, 38), lw=5)
        oell(d, x + wx * s, y + 16 * s, 7 * s, 7 * s, SILVER, lw=3)


def gantry(d, x, y, active=False):
    oline(d, (x, y), (x, y - 150), (120, 130, 134), 18)
    oline(d, (x + 150, y), (x + 150, y - 150), (120, 130, 134), 18)
    oline(d, (x - 10, y - 150), (x + 160, y - 150), (120, 130, 134), 14)
    orect(d, x + 55, y - 138, x + 95, y - 112, 6, (60, 70, 74), lw=5)
    oell(d, x + 75, y - 125, 8, 8, RED if active else (90, 96, 100), lw=4)
    if active:
        d.polygon([(x + 62, y - 112), (x + 88, y - 112), (x + 104, y - 60), (x + 46, y - 60)],
                  fill=(196, 74, 60), outline=None)


def chupa(d, x, y, s=1.0, eyes=True):
    d.ellipse([x - 56 * s, y - 40 * s, x + 60 * s, y + 52 * s], fill=(110, 128, 96), outline=INK, width=6)
    for i, dx in enumerate(range(-40, 56, 24)):
        h = (30 if i % 2 else 22) * s
        d.polygon([(x + (dx - 8) * s, y - 26 * s), (x + dx * s, y - 26 * s - h), (x + (dx + 8) * s, y - 26 * s)],
                  fill=(88, 104, 78), outline=INK, width=4)
    oell(d, x - 66 * s, y - 8 * s, 30 * s, 26 * s, (120, 138, 104), lw=6)
    orect(d, x - 96 * s, y - 2 * s, x - 70 * s, y + 14 * s, 4, (150, 164, 130), lw=4)
    if eyes:
        for sx in (-76, -60):
            d.ellipse([x + sx * s - 5, y - 14 * s - 4, x + sx * s + 5, y - 14 * s + 6], fill=(255, 90, 70))
    for fx in (-30, 18):
        capsule(d, (x + fx * s, y + 44 * s), (x + (fx - 4) * s, y + 74 * s), 14 * s, (96, 112, 84))


def cage(d, x, y, s=1.0):
    for i in range(7):
        oline(d, (x - 70 * s, y - 80 * s), (x - 70 * s + i * 22 * s, y + 40 * s), (150, 160, 164), 6)
    for j in range(4):
        oline(d, (x - 74 * s, y - 74 * s + j * 36 * s), (x + 74 * s, y - 74 * s + j * 36 * s), (150, 160, 164), 6)


def gauge(d, cx, cy, r, ang):
    oell(d, cx, cy, r, r, (34, 48, 46), lw=6)
    oline(d, (cx - r * 0.55, cy + r * 0.2), (cx + r * 0.55, cy - r * 0.2), (120, 150, 144), 5)
    a = math.radians(ang)
    oline(d, (cx, cy), (cx + math.sin(a) * r * 0.7, cy - math.cos(a) * r * 0.7), RED if ang > 200 else GREEN, 6)
    oell(d, cx, cy, 7, 7, (230, 234, 232), lw=4)


def ev_car(d, x, y, s=1.0, light=False, wheels=False):
    orect(d, x - 74 * s, y - 22 * s, x + 74 * s, y + 16 * s, 16, (60, 150, 110), lw=7)
    orect(d, x - 44 * s, y - 52 * s, x + 40 * s, y - 18 * s, 12, (44, 120, 92), lw=6)
    d.rectangle([x - 36 * s, y - 46 * s, x - 8 * s, y - 24 * s], fill=(150, 210, 220))
    d.rectangle([x + 2 * s, y - 46 * s, x + 30 * s, y - 24 * s], fill=(150, 210, 220))
    oell(d, x + 58 * s, y - 4 * s, 8 * s, 8 * s, GOLD, lw=4)
    for wx in (-44, 42):
        oell(d, x + wx * s, y + 18 * s, 17 * s, 17 * s, (28, 32, 36), lw=5)
        oell(d, x + wx * s, y + 18 * s, 8 * s, 8 * s, SILVER, lw=3)
        if wheels:
            arc_line(d, x + wx * s, y + 18 * s, 24, 20, 160, (200, 220, 224), 4, 150)
    if light:
        d.polygon([(x + 74 * s, y - 14 * s), (x + 150 * s, y - 26 * s), (x + 150 * s, y + 4 * s), (x + 74 * s, y - 2 * s)],
                  fill=(150, 200, 160), outline=None)


def brazil(d, x, y, s=1.0):
    pts = [(-0.42, -0.5), (-0.1, -0.62), (0.2, -0.5), (0.4, -0.34), (0.46, -0.1),
           (0.3, 0.16), (0.16, 0.42), (-0.02, 0.56), (-0.2, 0.4), (-0.36, 0.16),
           (-0.5, -0.05), (-0.46, -0.3)]
    poly = [(x + a * s, y + b * s) for a, b in pts]
    d.polygon(poly, fill=(24, 62, 54), outline=(90, 200, 170), width=5)
    d.line(poly + [poly[0]], fill=(90, 200, 170), width=5)


def phone_big(d, x, y, s=1.0, screen=(70, 110, 130)):
    orect(d, x - 40 * s, y - 76 * s, x + 40 * s, y + 76 * s, 14, (40, 46, 52), lw=6)
    d.rectangle([x - 30 * s, y - 62 * s, x + 30 * s, y + 58 * s], fill=screen)
    oell(d, x, y + 66 * s, 8 * s, 5 * s, (90, 100, 106), lw=3)


def wallet(d, x, y, s=1.0, open_=False):
    orect(d, x - 46 * s, y - 30 * s, x + 46 * s, y + 30 * s, 10, (122, 92, 60), lw=6)
    if open_:
        orect(d, x - 50 * s, y - 44 * s, x + 50 * s, y - 26 * s, 8, (140, 106, 70), lw=5)


def atm(d, x, y, s=1.0):
    orect(d, x - 80 * s, y - 190 * s, x + 80 * s, y + 40 * s, 14, (96, 108, 116), lw=8)
    d.rectangle([x - 56 * s, y - 160 * s, x + 56 * s, y - 96 * s], fill=(60, 90, 100), outline=INK, width=5)
    orect(d, x - 56 * s, y - 84 * s, x + 56 * s, y - 40 * s, 8, (52, 60, 66), lw=6)
    orect(d, x - 60 * s, y - 30 * s, x + 60 * s, y - 8 * s, 4, INK, lw=5)
    for i in range(3):
        for j in range(4):
            orect(d, x - 40 * s + j * 22 * s, y + 4 * s + i * 14 * s, x - 26 * s + j * 22 * s, y + 14 * s + i * 14 * s, 3, (140, 150, 156), lw=3)


def banknote(d, x, y, ang=0, s=1.0):
    c, ss = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    box = [(-34, -16), (34, -16), (34, 16), (-34, 16)]
    poly = [(x + bx * c * s - by * ss * s, y + bx * ss * s + by * c * s) for bx, by in box]
    d.polygon(poly, fill=(214, 196, 140), outline=INK, width=5)
    d.line(poly + [poly[0]], fill=INK, width=5)
    oell(d, x, y, 12 * s, 9 * s, (170, 150, 100), lw=4)


def magnet(d, x, y, s=1.0, ang=0):
    c, ss = math.cos(math.radians(ang)), math.sin(math.radians(ang))

    def R(bx, by):
        return x + bx * c * s - by * ss * s, y + bx * ss * s + by * c * s

    pts = [R(-30, -34), R(-30, 34), R(-12, 34), R(-12, -16), R(12, -16), R(12, 34), R(30, 34), R(30, -34)]
    d.polygon(pts, fill=RED, outline=INK, width=6)
    d.line(pts + [pts[0]], fill=INK, width=6)
    d.line([R(-30, -34), R(-12, -34)], fill=(230, 234, 236), width=8)
    d.line([R(12, -34), R(30, -34)], fill=(230, 234, 236), width=8)


def vinyl(d, cx, cy, r, ang, star=False):
    oell(d, cx, cy, r, r, (20, 24, 26), lw=6)
    for i in range(3):
        rr = r - 14 - i * 16
        arc_line(d, cx, cy, rr, ang + i * 90, ang + i * 90 + 200, (70, 78, 82), 3, 160)
    oell(d, cx, cy, 22, 22, (150, 60, 60), lw=5)
    if star:
        sparkle(d, cx, cy - 40, 12, (255, 220, 130))


def tv_cartoon(d, x, y, w, h, f):
    orect(d, x, y, x + w, y + h, 12, (52, 60, 66), lw=8)
    d.rectangle([x + 12, y + 12, x + w - 12, y + h - 12], fill=(120, 190, 210))
    cx, cy = x + w / 2, y + h / 2 - 8
    for i in range(8):
        a = math.radians(i * 45 + f * 22)
        oline(d, (cx + math.cos(a) * 44, cy + math.sin(a) * 44), (cx + math.cos(a) * 56, cy + math.sin(a) * 56), GOLD, 6)
    oell(d, cx, cy, 34, 34, (250, 210, 90), lw=6)
    if f >= 2:
        spiral(d, cx - 12, cy - 4, 12, (140, 90, 200), width=4)
        d.ellipse([cx + 8, cy - 10, cx + 18, cy], fill=INK)
    else:
        d.ellipse([cx - 18, cy - 10, cx - 8, cy], fill=INK)
        d.ellipse([cx + 8, cy - 10, cx + 18, cy], fill=INK)
        d.arc([cx - 14, cy + 2, cx + 14, cy + 20], 20, 160, fill=INK, width=5)
    if f == 1:
        d.polygon([(x + w - 44, y + 34), (x + w - 24, y + 62), (x + w - 64, y + 62)], fill=None, outline=(140, 90, 160), width=4)
        d.ellipse([x + w - 40, y + 42, x + w - 30, y + 52], fill=(140, 90, 160))
    rnd = random.Random(3 + f)
    for _ in range(50 + f * 25):
        px, py = rnd.randint(x + 12, x + w - 18), rnd.randint(y + 12, y + h - 16)
        d.rectangle([px, py, px + 6, py + 4], fill=rnd.choice([(240, 244, 244), (90, 110, 116)]))
    oline(d, (x + w * 0.3, y + h), (x + w * 0.2, y + h + 26), (52, 60, 66), 10)
    oline(d, (x + w * 0.7, y + h), (x + w * 0.8, y + h + 26), (52, 60, 66), 10)


def doll(d, x, y, s=1.0, red=False):
    orect(d, x - 24 * s, y - 10 * s, x + 24 * s, y + 44 * s, 10, (200, 120, 130), lw=5)
    for sgn in (-1, 1):
        capsule(d, (x + sgn * 22 * s, y + 4 * s), (x + sgn * 34 * s, y + 26 * s), 10 * s, (200, 120, 130))
        capsule(d, (x + sgn * 12 * s, y + 44 * s), (x + sgn * 14 * s, y + 64 * s), 10 * s, (200, 120, 130))
    oell(d, x, y - 30 * s, 24 * s, 24 * s, (236, 214, 200), lw=5)
    d.pieslice([x - 24 * s, y - 54 * s, x + 24 * s, y - 22 * s], 180, 360, fill=(160, 120, 96), outline=INK, width=4)
    ec = (255, 60, 50) if red else (40, 44, 48)
    for sgn in (-1, 1):
        d.ellipse([x + sgn * 10 * s - 5, y - 32 * s - 4, x + sgn * 10 * s + 5, y - 32 * s + 6], fill=ec)
    d.arc([x - 8 * s, y - 26 * s, x + 8 * s, y - 16 * s], 20, 160, fill=INK, width=4)
    if red:
        d.polygon([(x - 16 * s, y - 58 * s), (x - 10 * s, y - 72 * s), (x - 4 * s, y - 58 * s)], fill=(150, 90, 200), outline=None)
        d.polygon([(x + 4 * s, y - 60 * s), (x + 10 * s, y - 76 * s), (x + 16 * s, y - 60 * s)], fill=(150, 90, 200), outline=None)


def conveyor(d, y):
    orect(d, 80, y, W - 80, y + 26, 10, (90, 100, 104), lw=6)
    for x in range(110, W - 100, 90):
        oell(d, x, y + 13, 10, 10, (60, 68, 72), lw=4)
    for x in (200, 640, 1080):
        orect(d, x - 14, y + 26, x + 14, y + 60, 6, (70, 78, 82), lw=5)


def holy_image(d, x, y, s=1.0, tears=0):
    orect(d, x - 70 * s, y - 90 * s, x + 70 * s, y + 60 * s, 8, GOLD, lw=8)
    d.rectangle([x - 58 * s, y - 78 * s, x + 58 * s, y + 48 * s], fill=(52, 66, 74))
    ring(d, x, y - 62 * s, 16 * s, (250, 220, 130), 5, 200)
    oell(d, x, y - 20 * s, 26 * s, 30 * s, (226, 200, 170), lw=5)
    d.arc([x - 16 * s, y - 26 * s, x - 6 * s, y - 18 * s], 0, 180, fill=INK, width=4)
    d.arc([x + 6 * s, y - 26 * s, x + 16 * s, y - 18 * s], 0, 180, fill=INK, width=4)
    d.arc([x - 8 * s, y - 2 * s, x + 8 * s, y + 8 * s], 20, 160, fill=INK, width=4)
    for i in range(tears):
        gx = x - 20 * s + i * 20 * s
        gy = y - 30 * s + i * 26 * s
        d.line([(gx, gy - 12 * s), (gx, gy)], fill=(240, 200, 90), width=5)
        d.polygon([(gx, gy), (gx - 6 * s, gy + 16 * s), (gx + 6 * s, gy + 16 * s)], fill=(240, 200, 90), outline=None)


def tap_bottle(d, x, y, fill=0.0, halo=True, drop=False):
    orect(d, x - 50, y - 70, x + 50, y - 30, 8, (120, 130, 136), lw=6)
    oline(d, (x, y - 30), (x, y), (120, 130, 136), 26)
    orect(d, x - 20, y - 4, x + 40, y + 14, 5, (140, 150, 156), lw=5)
    if drop:
        d.polygon([(x, y + 16), (x - 7, y + 42), (x + 7, y + 42)], fill=(110, 190, 235), outline=INK, width=4)
    if halo:
        ring(d, x, y - 88, 16, (180, 230, 255), 4, 190)
    bx, by = x, y + 150
    orect(d, bx - 26, by - 60, bx + 26, by + 40, 12, (150, 200, 230), lw=6)
    orect(d, bx - 10, by - 78, bx + 10, by - 56, 5, (150, 200, 230), lw=5)
    if fill > 0:
        d.rectangle([bx - 20, by + 34 - 70 * fill, bx + 20, by + 34], fill=(110, 190, 235))


def qr_code(d, x, y, s=1.0, scan=0.0):
    orect(d, x - 34 * s, y - 34 * s, x + 34 * s, y + 34 * s, 4, (238, 240, 238), lw=5)
    rnd = random.Random(11)
    for i in range(6):
        for j in range(6):
            if rnd.random() > 0.45:
                d.rectangle([x - 28 * s + i * 9 * s, y - 28 * s + j * 9 * s, x - 20 * s + i * 9 * s, y - 20 * s + j * 9 * s], fill=INK)
    for (cx, cy) in ((x - 24 * s, y - 24 * s), (x + 24 * s, y - 24 * s), (x - 24 * s, y + 24 * s)):
        d.rectangle([cx - 8 * s, cy - 8 * s, cx + 8 * s, cy + 8 * s], fill=INK)
        d.rectangle([cx - 4 * s, cy - 4 * s, cx + 4 * s, cy + 4 * s], fill=(238, 240, 238))
    if 0 < scan < 1:
        sy = y - 34 * s + scan * 68 * s
        d.line([(x - 34 * s, sy), (x + 34 * s, sy)], fill=(60, 230, 140), width=5)


def burger(d, x, y, s=1.0):
    d.arc([x - 40 * s, y - 26 * s, x + 40 * s, y + 26 * s], 180, 360, fill=INK, width=12)
    d.arc([x - 40 * s, y - 26 * s, x + 40 * s, y + 26 * s], 180, 360, fill=(214, 158, 84), width=6)
    orect(d, x - 42 * s, y - 2 * s, x + 42 * s, y + 12 * s, 4, (120, 78, 44), lw=5)
    d.rectangle([x - 44 * s, y + 12 * s, x + 44 * s, y + 20 * s], fill=(150, 190, 90), outline=INK, width=4)
    d.arc([x - 40 * s, y - 8 * s, x + 40 * s, y + 44 * s], 0, 180, fill=INK, width=12)
    d.arc([x - 40 * s, y - 8 * s, x + 40 * s, y + 44 * s], 0, 180, fill=(214, 158, 84), width=6)
    for i in range(5):
        d.ellipse([x - 30 * s + i * 15 * s, y - 24 * s - 4, x - 24 * s + i * 15 * s, y - 18 * s - 4], fill=(240, 220, 180))


def comet(d, x, y, ang=0, s=1.0):
    c, ss = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    if ang:
        d.polygon([(x - 60, y - 8 * s), (x - 100 * s, y - 14 * s), (x - 90 * s, y + 2 * s), (x - 100 * s, y + 16 * s), (x - 60, y + 8 * s)],
                  fill=(222, 190, 128), outline=None)
    else:
        d.polygon([(x - 26 * s, y - 8 * s), (x - 76 * s, y - 16 * s), (x - 66 * s, y + 2 * s), (x - 76 * s, y + 18 * s), (x - 26 * s, y + 8 * s)],
                  fill=(222, 190, 128), outline=None)
    d.ellipse([x - 18 * s, y - 14 * s, x + 18 * s, y + 14 * s], fill=(240, 200, 130), outline=INK, width=5)


def dish_array(d, x, y, s=1.0, beam=False):
    for dx in (-90, 0, 90):
        bx, by = x + dx * s, y
        oline(d, (bx, by), (bx, by - 60 * s), (120, 130, 134), 12)
        d.ellipse([bx - 46 * s, by - 120 * s, bx + 46 * s, by - 56 * s], fill=(90, 110, 116), outline=INK, width=6)
        d.ellipse([bx - 34 * s, by - 108 * s, bx + 34 * s, by - 66 * s], fill=(60, 76, 82), outline=INK, width=4)
    if beam:
        d.polygon([(x - 20, y - 100), (x + 20, y - 100), (x + 90, y - 420), (x - 90, y - 420)],
                  fill=(70, 180, 120), outline=None)


def city_grid(d, x, y, cols, rows, lit, scale=26):
    for i in range(cols):
        for j in range(rows):
            bx, by = x + i * scale, y + j * scale
            on = lit.get((i, j), 0)
            if on == 1:
                d.rectangle([bx, by, bx + scale - 8, by + scale - 8], fill=(250, 210, 110), outline=(20, 30, 28), width=3)
            elif on == 2:
                d.rectangle([bx, by, bx + scale - 8, by + scale - 8], fill=(255, 120, 100), outline=INK, width=3)
            else:
                d.rectangle([bx, by, bx + scale - 8, by + scale - 8], fill=(34, 48, 48), outline=(20, 30, 28), width=3)


def president(d, x, y, s=1.0, seam=0, arm=0):
    capsule(d, (x - 18 * s, y + 6 * s), (x - 22 * s, y + 116 * s), 30 * s, (60, 64, 78))
    capsule(d, (x + 18 * s, y + 6 * s), (x + 22 * s, y + 116 * s), 30 * s, (60, 64, 78))
    for sgn in (-1, 1):
        orect(d, x + sgn * 22 * s - 22 * s, y + 114 * s, x + sgn * 22 * s + 14 * s, y + 138 * s, 10, (36, 38, 46), lw=5)
    d.polygon([(x - 48 * s, y - 138 * s), (x + 48 * s, y - 138 * s), (x + 58 * s, y + 28 * s), (x - 58 * s, y + 28 * s)],
              fill=(84, 92, 116), outline=INK)
    d.line([(x - 48 * s, y - 138 * s), (x + 48 * s, y - 138 * s)], fill=INK, width=7)
    d.line([(x - 58 * s, y + 28 * s), (x + 58 * s, y + 28 * s)], fill=INK, width=7)
    d.polygon([(x - 18 * s, y - 138 * s), (x + 18 * s, y - 138 * s), (x, y - 96 * s)], fill=SHIRT, outline=INK, width=4)
    d.polygon([(x - 6 * s, y - 132 * s), (x + 6 * s, y - 132 * s), (x + 2 * s, y - 60 * s), (x - 2 * s, y - 60 * s)], fill=(150, 50, 44), outline=INK, width=4)
    if arm:
        capsule(d, (x + 42 * s, y - 120 * s), (x + 92 * s, y - 190 * s), 24 * s, (84, 92, 116))
        hand(d, x + 96 * s, y - 196 * s, 12 * s)
    else:
        capsule(d, (x + 42 * s, y - 120 * s), (x + 66 * s, y - 30 * s), 24 * s, (84, 92, 116))
        hand(d, x + 68 * s, y - 24 * s, 12 * s)
    capsule(d, (x - 42 * s, y - 120 * s), (x - 64 * s, y - 34 * s), 24 * s, (84, 92, 116))
    hand(d, x - 66 * s, y - 28 * s, 12 * s)
    hx, hy = x + 2 * s, y - 184 * s
    oell(d, hx, hy, 42 * s, 44 * s, SKIN, lw=6)
    d.pieslice([hx - 42 * s, hy - 44 * s, hx + 42 * s, hy - 10 * s], 180, 360, fill=(110, 108, 104), outline=INK, width=6)
    d.pieslice([hx, hy - 44 * s, hx + 42 * s, hy + 44 * s], 270, 90, fill=(150, 158, 164), outline=INK, width=6)
    d.ellipse([hx + 12 * s, hy - 10 * s, hx + 28 * s, hy + 4 * s], fill=RED)
    d.ellipse([hx - 20 * s, hy - 10 * s, hx - 8 * s, hy], fill=INK)
    d.arc([hx - 22 * s, hy + 12 * s, hx + 10 * s, hy + 26 * s], 20, 160, fill=INK, width=5)
    oell(d, hx + 20 * s, hy + 40 * s, 8 * s, 8 * s, SILVER, lw=4)
    oline(d, (hx + 20 * s, hy + 35 * s), (hx + 20 * s, hy + 45 * s), INK, 3)
    if seam:
        oline(d, (hx + 42 * s, hy - 20 * s), (hx + 30 * s, hy + 44 * s), (255, 90, 80), 5)
        d.polygon([(hx + 40 * s, hy + 46 * s), (hx + 46 * s, hy + 60 * s), (hx + 34 * s, hy + 58 * s)], fill=(255, 200, 90), outline=None)


def tower(d, x, y, s=1.0, waves=0):
    oline(d, (x, y), (x, y - 260 * s), (130, 140, 146), 16)
    oline(d, (x - 34 * s, y), (x, y - 90 * s), (130, 140, 146), 10)
    oline(d, (x + 34 * s, y), (x, y - 90 * s), (130, 140, 146), 10)
    for i in range(3):
        oline(d, (x - 20 * s + i * 20 * s, y - 250 * s), (x - 20 * s + i * 20 * s, y - 210 * s), (130, 140, 146), 8)
    oell(d, x, y - 272 * s, 10, 10, RED, lw=4)
    for i in range(waves):
        rr = 120 + i * 70
        arc_line(d, x, y - 240 * s, rr, -50, 50, (255, 170, 90), 6, 200)


# -------------------------------------------------------------- cenas ------

def scene_p3_03():
    """Indústria da multa: o radar torto pega o carro e a multa sai voando."""
    frames = []
    for i, (car_x, active, slip, coins) in enumerate([
        (None, False, None, []),
        (300, True, None, []),
        (560, True, (430, 220), [(470, 260)]),
        (860, True, (620, 300), [(520, 240), (560, 320)]),
    ]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 0, 560, W, 700, 0, (40, 46, 52), lw=0)
        for x in range(40, W, 140):
            d.line([(x, 640), (x + 70, 640)], fill=(220, 220, 200), width=8)
        gantry(d, 240, 560, active)
        if car_x:
            car(d, car_x, 620, s=1.0)
        if slip:
            orect(d, slip[0] - 16, slip[1] - 22, slip[0] + 16, slip[1] + 22, 3, PAPER, lw=4)
            d.rectangle([slip[0] - 8, slip[1] - 12, slip[0] + 8, slip[1] - 4], fill=RED)
            d.rectangle([slip[0] - 8, slip[1] + 2, slip[0] + 8, slip[1] + 8], fill=(140, 130, 110))
        for (cx, cy) in coins:
            coin(d, cx, cy, 11)
        grifter(d, 1150, 470, s=0.85, arm_r=200, look=(-1, 0))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if active:
            glow(ov, 315, 440, 120, RED, 40)
        if coins:
            glow(ov, 540, 280, 90, GOLD, 50)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p3_04():
    """Chupa-cabra: avistado (olhos), encurralado, enjaulado, encomenda entregue."""
    frames = []
    for i, (stage, eyes) in enumerate([(0, True), (1, True), (2, True), (3, False)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        for x in (120, 980):
            d.line([(x, 560), (x, 420)], fill=(70, 56, 44), width=16)
            d.pieslice([x - 90, 330, x + 90, 470], 180, 360, fill=(52, 66, 52), outline=INK, width=6)
        d.polygon([(60, 560), (200, 560), (420, 120), (300, 120)], fill=(170, 168, 130), outline=None)
        if stage == 0:
            d.pieslice([480, 520, 660, 620], 180, 360, fill=(52, 66, 52), outline=INK, width=6)
            d.ellipse([540, 540, 556, 556], fill=(255, 90, 70))
            d.ellipse([580, 540, 596, 556], fill=(255, 90, 70))
        elif stage == 1:
            chupa(d, 560, 470, s=1.1, eyes=eyes)
            for x in range(480, 680, 40):
                d.line([(x, 120), (x + 20, 420)], fill=(220, 224, 220), width=4)
            d.line([(470, 200), (690, 200)], fill=(220, 224, 220), width=4)
        else:
            chupa(d, 560, 470, s=0.85, eyes=eyes)
            cage(d, 560, 480, s=1.3)
            grifter(d, 220, 470, s=0.9, arm_r=120, look=(1, -0.2))
            orect(d, 330, 300, 400, 380, 6, PAPER, lw=5)
            for k in range(4):
                d.rectangle([342, 314 + k * 16, 390, 320 + k * 16], fill=(150, 140, 116))
            if stage == 3:
                ring(d, 365, 340, 24, RED, 6, 200)
                sparkle(d, 365, 340, 10, (255, 200, 190))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 560, 460, 160, RED, 24)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p3_05():
    """Carro elétrico nacional: carga, farol, alcance no fim, puf final."""
    frames = []
    for i, (gauge_ang, light, wheels, puff, plug) in enumerate([
        (60, False, False, False, True),
        (120, True, False, False, True),
        (220, True, True, False, True),
        (260, False, False, True, False),
    ]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 300, 520, 900, 560, 8, (90, 100, 104), lw=6)
        ev_car(d, 600, 500, s=1.3, light=light, wheels=wheels)
        d.line([(600, 80), (600, 160)], fill=INK, width=8)
        d.arc([560, 160, 640, 240], 90, 270, fill=(60, 200, 130), width=10)
        if plug:
            d.line([(600, 240), (600, 440)], fill=(60, 200, 130), width=10)
            orect(d, 588, 436, 612, 470, 6, (120, 130, 134), lw=5)
        else:
            d.line([(600, 240), (588, 330)], fill=(60, 200, 130), width=10)
            orect(d, 560, 326, 604, 360, 6, (120, 130, 134), lw=5)
        orect(d, 950, 180, 1180, 400, 12, (54, 70, 68), lw=8)
        gauge(d, 1065, 290, 70, gauge_ang)
        if puff:
            for (cx, cy) in ((760, 520), (800, 540), (740, 545)):
                d.ellipse([cx - 18, cy - 12, cx + 18, cy + 12], fill=(190, 200, 198))
        grifter(d, 150, 480, s=0.95, arm_r=160, look=(1, -0.3))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if light:
            glow(ov, 800, 480, 120, GREEN, 40)
        if gauge_ang > 200:
            glow(ov, 1065, 290, 90, RED, 70)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p3_07():
    """GPS de todo mundo: o mapa do Brasil com pins e o blip que viaja."""
    frames = []
    T0, T1, T2 = (0.30, 0.52), (0.46, 0.62), (0.62, 0.40)

    def bez(t):
        u = 1 - t
        x = u * u * T0[0] + 2 * u * t * T1[0] + t * t * T2[0]
        y = u * u * T0[1] + 2 * u * t * T1[1] + t * t * T2[1]
        return x * W, y * H

    for i, (t, n_pins, mag) in enumerate([(0.25, 1, False), (0.5, 2, True), (0.78, 3, False), (0.95, 3, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 180, 100, 1120, 560, 16, (14, 40, 36), lw=8)
        brazil(d, 620, 320, s=300)
        pts = [bez(tt / 12) for tt in range(13)]
        for a, b in zip(pts, pts[1:]):
            d.line([a, b], fill=(120, 220, 255), width=4)
        pins = [(0.40, 0.50), (0.52, 0.44), (0.60, 0.56)]
        for k in range(n_pins):
            px, py = pins[k][0] * W, pins[k][1] * H
            d.polygon([(px, py + 16), (px - 9, py - 8), (px + 9, py - 8)], fill=RED, outline=INK, width=3)
            d.ellipse([px - 6, py - 16, px + 6, py - 4], fill=RED, outline=INK, width=3)
        bx, by = bez(t)
        d.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=(140, 230, 255), outline=INK, width=4)
        ring(d, bx, by, 22, (140, 230, 255), 4, 150)
        if mag:
            ring(d, 700, 340, 60, (200, 240, 255), 6, 200)
            d.line([(748, 388), (790, 430)], fill=(200, 240, 255), width=8)
        phone_big(d, 1080, 430, s=1.1, screen=(60, 120, 150))
        arc_line(d, 1080, 355, 30, 200, 340, GREEN, 4, 160)
        d.line([(1080, 350), (1000, 300)], fill=(100, 180, 210), width=4)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 620, 320, 260, BLUE, 24)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p3_08():
    """Chips nos documentos: a folha revela o chip, os dados vazam, o carimbo fecha."""
    frames = []
    for i, (reveal, waves, stamp) in enumerate([(0, 0, False), (1, 1, False), (2, 2, False), (1, 2, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 100, 470, 1180, 540, 12, (96, 72, 50), lw=8)
        for k in range(3):
            orect(d, 180 + k * 8, 452 - k * 10, 420 + k * 8, 470 - k * 10, 4, (210, 198, 170), lw=4)
        orect(d, 480, 130, 1000, 500, 10, PAPER, lw=8)
        for k in range(5):
            d.rectangle([520, 180 + k * 44, 960 - 60 * (k % 2), 192 + k * 44], fill=(170, 158, 132))
        if reveal:
            cx, cy = 740, 360
            ring(d, cx, cy, 84, (200, 235, 255), 5, 170)
            d.line([(808, 428), (860, 480)], fill=(200, 235, 255), width=8)
            orect(d, cx - 26, cy - 26, cx + 26, cy + 26, 6, (120, 90, 190), lw=6)
            for k in range(4):
                d.rectangle([cx - 20 + k * 10, cy - 34, cx - 12 + k * 10, cy - 26], fill=SILVER)
                d.rectangle([cx - 20 + k * 10, cy + 26, cx - 12 + k * 10, cy + 34], fill=SILVER)
            if waves:
                for rr in (44, 60 + 8 * waves):
                    ring(d, cx, cy, rr, PURPLE, 4, 140)
        if stamp:
            ring(d, 880, 200, 44, RED, 8, 210)
            d.rectangle([852, 188, 908, 200], fill=RED)
        grifter(d, 150, 470, s=0.9, arm_r=100, look=(1, -0.2))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if reveal:
            glow(ov, 740, 360, 110 + 30 * waves, PURPLE, 50 + 20 * waves)
        if stamp:
            glow(ov, 880, 200, 80, RED, 60)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p3_09():
    """Dinheiro instantâneo: a cédula voa... e a mão grande SEGURA no meio do caminho."""
    frames = []
    T0 = (0.22, 0.62)
    T1 = (0.5, 0.40)
    T2 = (0.78, 0.62)
    for i, (t, held, done) in enumerate([(0.15, False, False), (0.5, False, False), (0.5, True, False), (1.0, False, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        phone_big(d, 640, 320, s=3.2, screen=(44, 84, 96))
        for sgn in (1, -1):
            d.polygon([(640 + sgn * 60, 250), (640 + sgn * 130, 250), (640 + sgn * 130, 220),
                       (640 + sgn * 170, 265), (640 + sgn * 130, 310), (640 + sgn * 130, 280),
                       (640 + sgn * 60, 280)], fill=(90, 220, 160), outline=INK, width=4)
        wallet(d, 200, 500, s=1.2, open_=True)
        wallet(d, 1080, 500, s=1.2, open_=True)
        coin(d, 200, 470, 12)
        if done:
            for k in range(3):
                coin(d, 1060 + k * 24, 470 - k * 8, 12)
        if not done:
            u = 1 - t
            x = u * u * T0[0] + 2 * u * t * T1[0] + t * t * T2[0]
            y = u * u * T0[1] + 2 * u * t * T1[1] + t * t * T2[1]
            if held:
                x, y = 0.5, 0.40
                d.polygon([(610, 322), (670, 322), (658, 250), (622, 250)], fill=COAT_D, outline=INK, width=6)
                oell(d, 640, 240, 26, 22, SKIN, lw=6)
                orect(d, 600, 322, 680, 356, 6, PAPER, lw=5)
                oell(d, 700, 210, 20, 20, (240, 238, 228), lw=5)
                d.line([(700, 210), (700, 198)], fill=INK, width=4)
                d.line([(700, 210), (710, 214)], fill=INK, width=4)
            else:
                orect(d, x * W - 30, y * H - 14, x * W + 30, y * H + 14, 4, PAPER, lw=5)
                d.line([(x * W - 40, y * H), (x * W - 60, y * H)], fill=(140, 200, 160), width=6)
                d.line([(x * W - 55, y * H - 10), (x * W - 75, y * H - 14)], fill=(110, 160, 130), width=5)
        grifter(d, 150, 470, s=0.9, arm_r=120 if held else 200, look=(1, -0.2))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if held:
            glow(ov, 640, 280, 130, RED, 60)
        if done:
            glow(ov, 1080, 470, 100, GOLD, 70)
            sparkle(d, 1080, 420, 12, (255, 220, 120))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p3_10():
    """Moeda magnética: a cédula sai do caixa, é puxada pelo ímã... e volta pra caixa."""
    frames = []
    T0, T2 = (0.28, 0.72), (0.66, 0.52)
    T1 = ((T0[0] + T2[0]) / 2, min(T0[1], T2[1]) - 0.12)

    def pos(t):
        u = 1 - t
        x = u * u * T0[0] + 2 * u * t * T1[0] + t * t * T2[0]
        y = u * u * T0[1] + 2 * u * t * T1[1] + t * t * T2[1]
        return x, y

    for i, (t, back) in enumerate([(0.35, False), (0.7, False), (1.0, False), (0.15, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        atm(d, 340, 560, s=1.2)
        x, y = pos(t)
        ang = 40 if back else -20 + t * 60
        banknote(d, x * W, y * H, ang=ang, s=1.4)
        for k in range(3):
            tt = (t + k * 0.18) % 1
            xx, yy = pos(tt)
            d.ellipse([xx * W - 5, yy * H - 5, xx * W + 5, yy * H + 5], fill=(255, 120, 100))
        grifter(d, 900, 470, s=1.0, arm_r=130, look=(-1, -0.2))
        magnet(d, 920, 360, s=1.3, ang=20)
        if back:
            sparkle(d, 340, 500, 14, (255, 200, 120))
            d.line([(360, 500), (390, 480)], fill=(255, 200, 120), width=5)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 920, 360, 130, (255, 110, 90), 50)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p4_01():
    """Vinil invertido: o disco gira (120° por quadro), o som sai ao contrário."""
    frames = []
    for i, (ang, waves, star) in enumerate([(0, 1, False), (120, 2, True), (240, 3, True), (300, 1, False)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 160, 380, 760, 560, 14, (96, 72, 50), lw=8)
        vinyl(d, 420, 450, 120, ang, star=star)
        d.line([(640, 400), (500, 440)], fill=SILVER, width=10)
        orect(d, 488, 432, 520, 456, 4, (60, 66, 70), lw=5)
        oell(d, 640, 400, 18, 18, SILVER, lw=5)
        orect(d, 820, 340, 1100, 520, 12, (70, 78, 84), lw=8)
        oell(d, 960, 430, 60, 60, (40, 46, 50), lw=6)
        oell(d, 960, 430, 24, 24, (120, 130, 136), lw=4)
        for k in range(waves):
            arc_line(d, 960, 430, 90 + k * 40, 130, 230, (200, 170, 255), 6, 180)
        grifter(d, 1180, 480, s=0.9, arm_r=200, look=(-1, -0.3))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 420, 450, 170, PURPLE, 30)
        if star:
            glow(ov, 420, 410, 70, (255, 220, 130), 60)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p4_02():
    """Desenho da indução: o solzinho, o símbolo escondido, a estática final."""
    frames = []
    for i in range(4):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        tv_cartoon(d, 240, 120, 560, 380, i)
        d.pieslice([980, 480, 1120, 620], 180, 360, fill=(60, 74, 72), outline=INK, width=6)
        oell(d, 1050, 500, 44, 46, (86, 100, 96), lw=6)
        d.pieslice([1010, 460, 1090, 540], 180, 360, fill=(70, 84, 80), outline=INK, width=5)
        if i >= 2:
            d.ellipse([1032, 500, 1046, 514], fill=(240, 244, 244))
            d.ellipse([1058, 500, 1072, 514], fill=(240, 244, 244))
        if i == 3:
            for k in range(5):
                a = math.radians(30 + k * 20)
                oline(d, (1050 + math.cos(a) * 60, 490 + math.sin(a) * 60),
                      (1050 + math.cos(a) * 80, 490 + math.sin(a) * 80), (220, 230, 228), 5)
        oell(d, 1160, 590, 30, 18, (214, 158, 84), lw=5)
        lamp(d, 120, 300, s=1.1, color=(240, 220, 150))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 520, 300, 240, BLUE, 30)
        if i == 3:
            glow(ov, 1050, 500, 100, (200, 220, 255), 50)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p4_03():
    """Brinquedos possuídos: a linha de produção enfileira, o névoa faz o olho acender."""
    frames = []
    xs = [240, 520, 800, 1040]
    for i, (off, mist, reds) in enumerate([(0, False, 0), (60, True, 1), (120, True, 2), (40, False, 4)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        conveyor(d, 480)
        for bx in (560, 880):
            d.line([(bx, 120), (bx, 200)], fill=(138, 152, 155), width=12)
            d.line([(bx, 200), (bx + 40, 330)], fill=(138, 152, 155), width=10)
            orect(d, bx + 24, 330, bx + 76, 356, 6, (138, 152, 155), lw=5)
        if mist:
            for k in range(6):
                cx = 480 + k * 110
                d.ellipse([cx - 46, 300, cx + 46, 380], fill=(110, 84, 150))
        for k, x in enumerate(xs):
            doll(d, (x + off) % (W - 160) + 80, 430, s=1.0, red=(k < reds))
        orect(d, 1080, 560, 1240, 660, 8, (150, 110, 70), lw=6)
        d.line([(1080, 600), (1240, 600)], fill=INK, width=5)
        oell(d, 1160, 590, 22, 16, (216, 208, 186), lw=5)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if mist:
            glow(ov, 700, 340, 260, (150, 100, 200), 40)
        if reds == 4:
            glow(ov, 640, 440, 300, (255, 70, 60), 40)
            sparkle(d, 300 + off, 380, 10, (255, 120, 110))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p4_06():
    """A imagem que chora: o xarope pinga, a tigela enche, a moeda cai."""
    frames = []
    for i, (tears, bowl, bottle, coin_drop) in enumerate([(0, 0.0, 0, False), (1, 0.3, 1, False), (2, 0.6, 1, False), (3, 0.9, 1, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 60, 120, 200, 560, 10, (70, 92, 86), lw=7)
        if bottle:
            orect(d, 236, 180, 288, 260, 10, (240, 200, 90), lw=6)
            orect(d, 248, 160, 276, 184, 5, (200, 160, 70), lw=5)
            oline(d, (288, 190), (330, 214), (240, 200, 90), 14)
        holy_image(d, 700, 300, s=1.5, tears=tears)
        d.pieslice([560, 560, 840, 700], 0, 180, fill=(150, 160, 164), outline=INK, width=7)
        if bowl:
            d.pieslice([580, 560 + (1 - bowl) * 40, 820, 700], 0, 180, fill=(240, 200, 90), outline=None)
        if coin_drop:
            coin(d, 700, 500, 14)
            sparkle(d, 740, 460, 10, (255, 220, 120))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 700, 300, 220, GOLD, 26)
        if bottle:
            glow(ov, 300, 220, 70, (255, 220, 130), 50)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p4_07():
    """O 13º mandamento: a fita roda, o 13 surge no meio da onda, o pico queima."""
    frames = []
    rnd = random.Random(5)
    waves = []
    for f in range(4):
        rows = []
        for _ in range(12):
            rows.append(rnd.randint(10, 90) if f in (1, 2) else rnd.randint(8, 40))
        waves.append(rows)
    for i in range(4):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 220, 260, 1060, 560, 16, (54, 70, 68), lw=8)
        orect(d, 260, 300, 1020, 520, 12, (30, 44, 42), lw=6)
        for bx in (360, 940):
            oell(d, bx, 400, 54, 54, (90, 100, 104), lw=7)
            oell(d, bx, 400, 18, 18, (50, 58, 62), lw=5)
            for k in range(4):
                a = math.radians(i * 90 + k * 90)
                d.ellipse([bx + math.cos(a) * 32 - 10, 400 + math.sin(a) * 32 - 10,
                           bx + math.cos(a) * 32 + 10, 400 + math.sin(a) * 32 + 10], fill=(140, 150, 154), outline=INK, width=3)
        for k, hgt in enumerate(waves[i]):
            x = 510 + k * 28
            d.rectangle([x, 400 - hgt // 2, x + 12, 400 + hgt // 2], fill=(90, 220, 160))
        if i >= 1:
            d.text((665, 400), "13", font=font(64), fill=(220, 190, 255), anchor="mm")
            ring(d, 665, 400, 52, PURPLE, 5, 170 if i == 1 else 210)
        if i == 2:
            orect(d, 1100, 380, 1230, 470, 8, (70, 78, 84), lw=6)
            for k in range(3):
                arc_line(d, 1165, 425, 30 + k * 24, -60, 60, (150, 220, 255), 5, 170)
        if i == 3:
            sparkle(d, 665, 350, 12, (230, 205, 255))
            sparkle(d, 720, 440, 9, (230, 205, 255))
        oell(d, 150, 470, 34, 34, (60, 68, 72), lw=6)
        oell(d, 250, 470, 34, 34, (60, 68, 72), lw=6)
        arc_line(d, 200, 470, 52, 180, 360, (120, 130, 134), 10, 255)
        grifter(d, 1190, 500, s=0.8, arm_r=220, look=(-1, -0.2))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 665, 400, 200, PURPLE, 24 + 14 * i)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p4_08():
    """Água abençoada: a torneira da capela enche a garrafa milagrosa."""
    frames = []
    for i, (drop, fill, glow_) in enumerate([(False, 0.0, False), (True, 0.45, False), (True, 0.85, True), (False, 1.0, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        d.rectangle([0, 0, W, 544], fill=(34, 58, 54))
        ring(d, 640, 170, 90, (140, 190, 220), 8, 120)
        d.line([(640, 80), (640, 260)], fill=(140, 190, 220), width=6)
        d.line([(550, 170), (730, 170)], fill=(140, 190, 220), width=6)
        tap_bottle(d, 640, 330, fill=fill, halo=True, drop=drop)
        if glow_:
            for (sx, sy) in ((600, 420), (684, 470)):
                sparkle(d, sx, sy, 10, (190, 235, 255))
        if i == 3:
            orect(d, 628, 246, 652, 264, 4, (150, 110, 70), lw=4)
            coin(d, 760, 590, 14)
            ring(d, 760, 590, 22, (255, 220, 120), 4, 150)
        grifter(d, 150, 480, s=0.9, arm_r=140, look=(1, -0.2))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if drop:
            glow(ov, 640, 400, 120, BLUE, 50)
        if glow_:
            glow(ov, 640, 480, 150, BLUE, 70)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p4_09():
    """Apocalipse adiado: o X na data, a cometa de volta, o relógio zerado."""
    frames = []
    for i, (comet_x, strike, circled, reset) in enumerate([
        (300, 0, 1, False), (520, 2, 2, False), (740, 2, 3, False), (980, 0, 3, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        comet(d, comet_x, 140, ang=0 if comet_x < 700 else 180, s=1.1)
        orect(d, 200, 200, 780, 600, 12, PAPER, lw=8)
        orect(d, 200, 200, 780, 260, 12, (150, 60, 50), lw=0)
        d.line([(200, 260), (780, 260)], fill=INK, width=8)
        for r in range(4):
            for c in range(6):
                bx, by = 240 + c * 90, 300 + r * 70
                d.rectangle([bx, by, bx + 70, by + 52], outline=(170, 160, 140), width=4)
                d.text((bx + 35, by + 26), str(r * 6 + c + 1), font=font(26), fill=(110, 100, 86), anchor="mm")
        ring(d, 425, 326, 44, RED, 7, 220)
        if strike:
            oline(d, (390, 300), (460, 352), RED, 12)
            if strike > 1:
                oline(d, (460, 300), (390, 352), RED, 12)
        if circled > 2:
            ring(d, 515, 396, 44, RED, 7, 220)
        oell(d, 1050, 300, 90, 90, (232, 220, 192), lw=8)
        for k in range(12):
            a = math.radians(k * 30)
            oline(d, (1050 + math.sin(a) * 74, 300 - math.cos(a) * 74), (1050 + math.sin(a) * 84, 300 - math.cos(a) * 84), INK, 5)
        ha = 0 if reset else math.radians(120 + i * 30)
        oline(d, (1050, 300), (1050 + math.sin(ha) * 50, 300 - math.cos(ha) * 50), RED, 9)
        oline(d, (1050, 300), (1080, 260), INK, 6)
        if reset:
            ring(d, 1050, 300, 104, (255, 200, 120), 6, 150)
            sparkle(d, 1100, 240, 12, (255, 220, 130))
        grifter(d, 1130, 520, s=0.85, arm_r=230, look=(-1, -0.3))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 640, 400, 260, ORANGE, 22)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p5_01():
    """Feixe do cerrado: as antenas disparam, a chuva vai pro lado A, o sol pro B."""
    frames = []
    for i, (beam, rain, sun_) in enumerate([(0, 0, 0), (1, 3, 0), (2, 6, 1), (1, 1, 1)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        d.rectangle([0, 0, 560, 470], fill=(24, 44, 54))
        d.rectangle([560, 0, W, 470], fill=(30, 52, 48))
        cloud(d, 300 - i * 40, 160, s=1.3)
        cloud(d, 880 + i * 30, 130, s=1.2)
        if sun_:
            sun(d, 1080, 140, r=52, smile=True)
        for k in range(rain):
            x = 160 + k * 70
            y = 260 + (k * 53) % 140
            d.polygon([(x, y - 16), (x - 9, y + 10), (x + 9, y + 10)], fill=(110, 180, 235), outline=INK, width=4)
        d.line([(700, 560), (700, 470)], fill=(70, 56, 44), width=18)
        d.pieslice([600, 380, 800, 500], 180, 360, fill=(52, 66, 52), outline=INK, width=6)
        d.rectangle([0, 470, W, 560], fill=(54, 60, 44))
        dish_array(d, 640, 470, s=1.1, beam=beam > 0)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if beam:
            glow(ov, 640, 120, 180, GREEN, 60)
            glow(ov, 640, 380, 160, GREEN, 30)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p5_02():
    """A fórmula da água: o dial sobe, a gota muda, o medidor estoura."""
    frames = []
    for i, (dial, swirl, gauge_, glass) in enumerate([(0, False, 60, False), (60, True, 150, False), (150, True, 230, True), (120, True, 180, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 140, 180, 700, 560, 14, (96, 108, 116), lw=8)
        d.rectangle([180, 220, 420, 480], fill=(52, 66, 74), outline=INK, width=6)
        d.rectangle([188, 300, 412, 472], fill=(70, 130, 170))
        d.line([(188, 300), (412, 300)], fill=(140, 200, 235), width=5)
        d.line([(420, 380), (560, 380)], fill=(140, 150, 156), width=22)
        d.line([(560, 380), (560, 470)], fill=(140, 150, 156), width=22)
        d.polygon([(560, 480), (536, 520), (584, 520)], fill=(110, 190, 235), outline=INK, width=5)
        oell(d, 560, 330, 70, 70, (30, 44, 48), lw=7)
        d.polygon([(560, 292), (536, 330), (584, 330)], fill=(110, 190, 235), outline=INK, width=5)
        if swirl:
            spiral(d, 560, 322, 26, (190, 235, 255), width=5)
        orect(d, 780, 240, 1160, 560, 14, (54, 70, 68), lw=8)
        oell(d, 970, 350, 80, 80, (38, 52, 52), lw=7)
        a = math.radians(dial - 90)
        oline(d, (970, 350), (970 + math.cos(a) * 60, 350 + math.sin(a) * 60), RED, 9)
        oell(d, 970, 350, 10, 10, RED, lw=4)
        gauge(d, 1060, 470, 54, gauge_)
        if glass:
            orect(d, 240, 590, 320, 700, 10, (150, 200, 230), lw=6)
            d.rectangle([248, 640, 312, 692], fill=(110, 190, 235))
            sparkle(d, 300, 620, 9, (200, 240, 255))
        grifter(d, 1240, 500, s=0.85, arm_r=240, look=(-1, -0.2))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 560, 330, 110, BLUE, 30 + 20 * i)
        if gauge_ > 200:
            glow(ov, 1060, 470, 80, RED, 80)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p5_03():
    """Apagão cibernético: a grade da cidade acesa, o flicker, o escuro, o 'acidente'."""
    frames = []
    rnd = random.Random(21)
    keys = [(i, j) for i in range(10) for j in range(4)]
    grid_full = {k: 1 for k in keys}
    grid_half = {k: (1 if rnd.random() > 0.45 else 0) for k in keys}
    grid_dark = {k: 0 for k in keys}
    grid_one = dict(grid_dark)
    grid_one[(2, 1)] = 1
    for i, (grid, alarm, grifter_arm) in enumerate([
        (grid_full, False, 200), (grid_half, False, 190), (grid_dark, True, 90), (grid_one, False, 40)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 140, 120, 900, 560, 16, (14, 34, 32), lw=8)
        city_grid(d, 180, 160, 10, 4, grid, scale=72)
        orect(d, 980, 260, 1160, 470, 12, (54, 70, 68), lw=8)
        orect(d, 1040, 290, 1100, 440, 8, (30, 44, 42), lw=6)
        posv = [0, 40, 120, 0][i]
        orect(d, 1048, 300 + posv, 1092, 348 + posv, 8, (230, 90, 80) if i == 2 else (230, 200, 120), lw=5)
        if alarm:
            d.polygon([(980, 120), (1160, 120), (1220, 0), (920, 0)], fill=(190, 70, 60))
            oell(d, 1070, 240, 14, 14, RED, lw=5)
        if i == 3:
            ring(d, 1070, 340, 30, (250, 220, 130), 5, 140)
        grifter(d, 700, 500, s=1.0, arm_r=grifter_arm, look=(1, -0.2))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if i == 0:
            glow(ov, 520, 340, 300, (250, 210, 110), 40)
        if alarm:
            glow(ov, 1070, 300, 200, RED, 80)
        if i == 3:
            glow(ov, 356, 264, 90, (250, 210, 110), 100)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p5_05():
    """Aparelhos espionando: a conversa vira onda, o celular pega, a TV anuncia o pneu."""
    frames = []
    for i, (wave, phone_glow, ad) in enumerate([(0, False, False), (2, True, False), (3, True, True), (1, False, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        d.rectangle([0, 0, W, 544], fill=(28, 48, 46))
        orect(d, 0, 544, W, 560, 0, (22, 38, 36), lw=0)
        orect(d, 120, 420, 560, 560, 22, (122, 84, 60), lw=8)
        for k, (hx, look) in enumerate([(280, (1, 0)), (420, (-1, 0))]):
            oell(d, hx, 380, 40, 42, SKIN if k == 0 else SKIN_B, lw=6)
            d.pieslice([hx - 40, 340, hx + 40, 400], 180, 360, fill=CURL if k == 0 else (90, 70, 60), outline=INK, width=5)
            d.arc([hx - 16 + (8 if k == 0 else -8), 402, hx + 8 + (8 if k == 0 else -8), 416], 20, 160, fill=INK, width=5)
        orect(d, 240, 220, 480, 320, 18, (238, 240, 238), lw=6)
        d.polygon([(320, 320), (300, 360), (360, 320)], fill=(238, 240, 238), outline=INK, width=5)
        oell(d, 360, 270, 34, 34, (40, 44, 48), lw=6)
        oell(d, 360, 270, 14, 14, (120, 130, 136), lw=4)
        for k in range(wave):
            arc_line(d, 620, 300, 60 + k * 36, -50, 50, (120, 220, 255), 6, 190)
        phone_big(d, 680, 480, s=0.9, screen=(70, 130, 160) if phone_glow else (50, 70, 80))
        orect(d, 860, 200, 1180, 460, 12, (52, 60, 66), lw=8)
        d.rectangle([876, 216, 1164, 444], fill=(90, 120, 130))
        if ad:
            oell(d, 1020, 330, 64, 64, (40, 44, 48), lw=7)
            oell(d, 1020, 330, 26, 26, (120, 130, 136), lw=5)
            for a in range(12):
                an = math.radians(a * 30)
                oline(d, (1020 + math.cos(an) * 50, 330 + math.sin(an) * 50),
                       (1020 + math.cos(an) * 62, 330 + math.sin(an) * 62), (240, 230, 200), 5)
            if i == 3:
                sparkle(d, 1120, 260, 12, (255, 230, 150))
                coin(d, 940, 400, 12)
        if wave:
            d.line([(700, 430), (760, 320), (900, 260)], fill=(90, 170, 200), width=4)
            d.ellipse([880, 240, 950, 280], fill=(140, 190, 210), outline=(120, 220, 255), width=3)
        lamp(d, 110, 250, s=1.1, color=(240, 220, 150))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if phone_glow:
            glow(ov, 680, 480, 100, BLUE, 60)
        if ad:
            glow(ov, 1020, 330, 150, (255, 220, 130), 50)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p5_06():
    """Presidente 2.0: o técnico ajusta, a emenda brilha, o aceno da bateria, o discurso sai da fenda."""
    frames = []
    for i, (seam, arm, bolt, scroll) in enumerate([(0, 0, False, False), (1, 0, True, False), (0, 1, False, False), (1, 0, False, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 480, 440, 760, 620, 10, (96, 72, 50), lw=8)
        d.line([(480, 440), (760, 440)], fill=INK, width=9)
        d.line([(620, 440), (620, 380)], fill=INK, width=8)
        oell(d, 620, 368, 16, 20, (60, 66, 70), lw=5)
        president(d, 620, 340, s=1.0, seam=seam, arm=arm)
        orect(d, 720, 250, 780, 300, 6, (60, 70, 74), lw=5)
        d.rectangle([728, 258, 772, 292], fill=GREEN if i >= 1 else (80, 90, 94))
        grifter(d, 220, 500, s=0.95, arm_r=130 if bolt else 200, look=(1, -0.3))
        if bolt:
            oline(d, (292, 424), (630, 196), SILVER, 8)
            bx, by = 642, 196
            for a in range(4):
                an = math.radians(i * 90 + a * 90)
                oline(d, (bx + math.cos(an) * 12, by + math.sin(an) * 12), (bx - math.cos(an) * 12, by - math.sin(an) * 12), SILVER, 5)
        if scroll:
            orect(d, 690, 470, 750, 540, 6, PAPER, lw=5)
            d.line([(690, 470), (750, 470)], fill=INK, width=6)
            for k in range(3):
                d.rectangle([700, 484 + k * 14, 740, 489 + k * 14], fill=(150, 140, 116))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        if seam:
            glow(ov, 660, 190, 90, RED, 70)
        if i == 2:
            glow(ov, 750, 275, 70, GREEN, 80)
            sparkle(d, 790, 240, 10, (170, 255, 190))
        if scroll:
            sparkle(d, 720, 450, 9, (255, 230, 170))
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p5_08():
    """Torres de 5G: as ondas chegam, a casa formigueira, o dosímetro estoura."""
    frames = []
    for i, (waves, tingles, meter) in enumerate([(1, 0, 80), (3, 2, 170), (5, 4, 250), (4, 4, 210)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        tower(d, 300, 560, s=1.2, waves=waves)
        orect(d, 760, 340, 1120, 560, 8, (122, 92, 66), lw=8)
        d.polygon([(740, 340), (1140, 340), (940, 220)], fill=(96, 60, 50), outline=INK, width=8)
        d.line([(940, 220), (940, 180)], fill=INK, width=8)
        d.polygon([(940, 180), (990, 196), (940, 212)], fill=RED, outline=INK, width=4)
        oell(d, 940, 480, 36, 38, SKIN, lw=6)
        d.pieslice([904, 444, 976, 500], 180, 360, fill=CURL, outline=INK, width=5)
        d.ellipse([924, 474, 936, 484], fill=INK)
        d.ellipse([948, 474, 960, 484], fill=INK)
        d.arc([928, 492, 952, 504], 20, 160, fill=INK, width=5)
        for k in range(tingles):
            a = math.radians(40 + k * 50)
            x0 = 940 + math.cos(a) * 52
            y0 = 478 + math.sin(a) * 52
            d.polygon([(x0, y0 - 12), (x0 + 6, y0 - 2), (x0 + 12, y0 - 12), (x0 + 16, y0), (x0 + 22, y0 - 12),
                       (x0 + 22, y0 + 6), (x0 + 8, y0 + 4)], fill=(255, 200, 90), outline=None)
        orect(d, 1180, 330, 1280, 510, 10, (54, 70, 68), lw=7)
        gauge(d, 1230, 420, 60, meter)
        if meter > 200:
            oell(d, 1230, 350, 10, 10, RED, lw=4)
        grifter(d, 150, 500, s=0.9, arm_r=150, look=(1, -0.2))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 300, 240, 200, ORANGE, 30 + 14 * waves)
        if meter > 200:
            glow(ov, 1230, 420, 90, RED, 90)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


def scene_p5_09():
    """QR no prato: o celular escaneia, o check fecha, o dado vai pra nuvem, o selo sela."""
    frames = []
    for i, (scan, check, cloud_, seal) in enumerate([(0.0, False, False, False), (0.5, False, True, False), (1.0, True, True, True), (0.0, True, True, True)]):
        im = new_frame()
        d = ImageDraw.Draw(im)
        bg(d, 560)
        orect(d, 0, 500, W, 560, 0, (122, 92, 66), lw=0)
        d.line([(0, 500), (W, 500)], fill=INK, width=9)
        oell(d, 640, 470, 130, 34, (238, 240, 238), lw=6)
        burger(d, 640, 420, s=1.3)
        qr_code(d, 820, 440, s=1.2, scan=scan)
        phone_big(d, 950, 330, s=1.1, screen=(60, 120, 150))
        if scan > 0:
            d.line([(950, 330), (860, 420)], fill=(60, 230, 140), width=5)
        if check:
            d.line([(920, 330), (940, 352)], fill=(80, 240, 150), width=10)
            d.line([(940, 352), (975, 305)], fill=(80, 240, 150), width=10)
        if cloud_:
            d.ellipse([1060, 90, 1160, 150], fill=(140, 190, 210), outline=INK, width=4)
            d.ellipse([1120, 70, 1230, 150], fill=(140, 190, 210), outline=INK, width=4)
            d.ellipse([1000, 100, 1090, 150], fill=(140, 190, 210), outline=INK, width=4)
            d.line([(990, 300), (1080, 150)], fill=(60, 230, 140), width=4)
            for k in range(3):
                x = 1080 + k * 26
                d.polygon([(x, 170 + k * 10), (x + 12, 170 + k * 10), (x + 6, 184 + k * 10)], fill=(60, 230, 140))
        if seal:
            ring(d, 640, 420, 66, GREEN, 6, 180)
            sparkle(d, 700, 370, 10, (150, 255, 190))
        grifter(d, 220, 500, s=0.95, arm_r=110, look=(1, -0.3))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        glow(ov, 820, 440, 110, GREEN, 40)
        if cloud_:
            glow(ov, 1115, 110, 110, (140, 220, 200), 60)
        im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        frames.append(im)
    return frames


SCENES = {
    "p3_03": scene_p3_03,
    "p3_04": scene_p3_04,
    "p3_05": scene_p3_05,
    "p3_07": scene_p3_07,
    "p3_08": scene_p3_08,
    "p3_09": scene_p3_09,
    "p3_10": scene_p3_10,
    "p4_01": scene_p4_01,
    "p4_02": scene_p4_02,
    "p4_03": scene_p4_03,
    "p4_06": scene_p4_06,
    "p4_07": scene_p4_07,
    "p4_08": scene_p4_08,
    "p4_09": scene_p4_09,
    "p5_01": scene_p5_01,
    "p5_02": scene_p5_02,
    "p5_03": scene_p5_03,
    "p5_05": scene_p5_05,
    "p5_06": scene_p5_06,
    "p5_08": scene_p5_08,
    "p5_09": scene_p5_09,
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

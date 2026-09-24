#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/rig_v7.py — RIG ESTRUTURAL v7: 30 desenhos @ 5 fps, 6 s, loop perfeito.

Consistência ESTRUTURAL (o fundo NUNCA é re-desenhado; v6 derivava porque cada
quadro era uma imagem nova):

  * BASE imutável: poster-âncora (veneno verde via recolor_v7.py) com furos
    inpaintados por interpolação horizontal (gota, torneira, pipeta+mãos).
  * PIPETA+MÃOS: sprite recortado do poster (polígono featherizado) que
    INCLINA ±4° (o homem despeja) e volta — o objeto inclina, a gota cai,
    o objeto retorna: loop perfeito.
  * GOTA: recortada por flood-fill bloqueado no outline; o outline do sprite é
    o ANEL da própria máscara (NUNCA pixels de borda do tanque viajando).
  * Gotinha da torneira: cai e SE INCORPORA à água do copinho (squash+fade+glint).
  * Mostrador/relógio: NÃO mexe (fica o do poster).
  * Todo movimento é periódico (período 30) → frame(30) == frame(0).

Uso: python3 tools/animia/rig_v7.py --mission p5_02
"""
from __future__ import annotations
import argparse, json, math, os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TAU = 2 * math.pi
N = 30
FPS = 5
DUR_MS = 6000
STEP_MS = DUR_MS // N

DROP_C = (329, 241)
TIP0 = (325, 190)          # bico da pipeta em repouso
PIVOT = (235, 168)         # pivô do tilt (punho inferior)
PEAK_DEG = 2.5

# polígono pipeta+bulbo+mãos+cotos de manga (coords do poster, sentido horário)
PIP_POLY = [(141, 52), (152, 42), (168, 38), (196, 52), (206, 58), (238, 72),
            (246, 92), (247, 110), (240, 124), (262, 132), (300, 158),
            (327, 178), (334, 192), (330, 202), (318, 199), (285, 178),
            (262, 166), (258, 172), (252, 182), (249, 203), (224, 203),
            (219, 182), (213, 158), (206, 132), (200, 120), (190, 122),
            (181, 108), (188, 96), (170, 88), (152, 70)]


def lerp(a, b, t): return a + (b - a) * t

def smooth(t): return t * t * (3 - 2 * t)

def bump(k, c, w): return math.exp(-((k - c) ** 2) / (2 * w * w))

def ease_in(t, p=1.8): return t ** p


def inpaint_hole(im, x0, y0, x1, y1, m=5, feather=2):
    out = im.copy()
    h, w, _ = im.shape
    for y in range(y0, y1 + 1):
        L = im[y, max(0, x0 - m):x0].astype(float).mean(axis=0)
        R = im[y, x1 + 1:min(w, x1 + 1 + m)].astype(float).mean(axis=0)
        t = np.linspace(0, 1, x1 - x0 + 1)[:, None]
        out[y, x0:x1 + 1] = np.round(L[None, :] * (1 - t) + R[None, :] * t
                                     ).astype(np.uint8)
    xs = np.arange(w)
    sel = ((xs >= x0) & (xs <= x1))[:, None]
    for f in range(feather):
        t = (f + 1) / (feather + 1)
        for y in (y0 + f, y1 - f):
            blended = (im[y].astype(float) * (1 - t) + out[y].astype(float) * t)
            out[y] = np.where(sel, np.round(blended), out[y]).astype(np.uint8)
    return out


def inpaint_region(im, mask, m=4):
    """Inpainta uma região irregular: por linha, cada trecho contíguo é
    preenchido interpolando as cores imediatamente fora do trecho."""
    out = im.copy()
    H, W = im.shape[:2]
    for y in range(H):
        xs = np.nonzero(mask[y])[0]
        if len(xs) == 0:
            continue
        runs, start, prev = [], xs[0], xs[0]
        for x in xs[1:]:
            if x != prev + 1:
                runs.append((start, prev)); start = x
            prev = x
        runs.append((start, prev))
        for a, b in runs:
            la = im[y, max(0, a - m):a].astype(float)
            L = la.mean(axis=0) if len(la) else out[y, 0].astype(float)
            rb = im[y, b + 1:min(W, b + 1 + m)].astype(float)
            R = rb.mean(axis=0) if len(rb) else out[y, -1].astype(float)
            t = np.linspace(0, 1, b - a + 1)[:, None]
            out[y, a:b + 1] = np.round(L[None, :] * (1 - t) + R[None, :] * t
                                       ).astype(np.uint8)
    return out


def region_grow(seed_xy, bound, iters=300):
    cur = np.zeros_like(bound)
    cur[seed_xy] = True
    for _ in range(iters):
        nxt = cur.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt |= np.roll(np.roll(cur, dy, 0), dx, 1)
        nxt &= bound
        if (nxt == cur).all():
            break
        cur = nxt
    return cur


def drop_silhouette(h, w, cx=DROP_C[0], cy=DROP_C[1], r=34, tip_y=202, pad=4):
    yy, xx = np.mgrid[0:h, 0:w]
    circ = (xx - cx) ** 2 + (yy - cy) ** 2 <= (r + pad) ** 2
    cone = (np.abs(xx - cx) <= np.maximum(.5, (yy - tip_y) * .62) + pad) & \
           (yy >= tip_y) & (yy <= cy + 2)
    return circ | cone


def ring_of(mask, n=2):
    out = mask.copy()
    for _ in range(n):
        g = out.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            g |= np.roll(np.roll(out, dy, 0), dx, 1)
        out = g
    return out


def drop_interior(im, bbox, seed, sil=None, barrier=None):
    """Interior da gota: flood a partir do seed, propagação estrita (verde ou
    ciano vivo) e barreira no outline ESCURO NÍTIDO (o do poster original) —
    não vaza p/ água do tanque nem por outline desfocado."""
    R, G, B = (im[..., i].astype(int) for i in range(3))
    prop = (G > 170) & ((G - R) > 60) & ((B > 150) | ((G - B) > 30))
    core = (R > 180) & (G > 220) & ((B > 200) | ((G - B) > 20))
    x0, y0, x1, y1 = bbox
    bb = np.zeros(im.shape[:2], bool)
    bb[y0:y1 + 1, x0:x1 + 1] = True
    bound = (prop | core) & bb
    if sil is not None:
        bound &= sil
    if barrier is not None:
        bound &= ~barrier
    return region_grow(seed, bound)


def clean_drop_sprite(im, bbox, seed, sil=None, barrier=None):
    """Sprite limpo: interior + anel-outline com cor constante do outline —
    nenhum pixel de borda do tanque/água viaja com a gota."""
    R, G, B = (im[..., i].astype(int) for i in range(3))
    interior = drop_interior(im, bbox, seed, sil, barrier)
    ring = ring_of(interior) & ~interior
    dark = (R < 95) & (G < 95) & (B < 95)
    near = ring_of(interior, 3)
    ol_col = im[dark & near]
    ol = ol_col.mean(axis=0) if len(ol_col) else np.array([22, 26, 25])
    ys, xs = np.nonzero(interior | ring)
    Y0, Y1, X0, X1 = ys.min(), ys.max(), xs.min(), xs.max()
    rgb = im[Y0:Y1 + 1, X0:X1 + 1].astype(float)
    rr = ring[Y0:Y1 + 1, X0:X1 + 1]
    rgb[rr] = ol
    mask = (interior | ring)[Y0:Y1 + 1, X0:X1 + 1]
    am = Image.fromarray((mask * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(.5))
    return np.dstack([np.round(rgb), np.asarray(am)]).astype(np.uint8), (X0, Y0)


class Rig:
    def __init__(self, mission_dir):
        poster = np.asarray(
            Image.open(os.path.join(mission_dir, 'poster.webp')).convert('RGB')
        ).astype(np.uint8)
        self.poster = poster
        self.H, self.W, _ = poster.shape

        # ---- máscaras/sprites
        pm = Image.new('L', (self.W, self.H), 0)
        ImageDraw.Draw(pm).polygon(PIP_POLY, fill=255)
        self.pip_mask = np.asarray(pm) > 0
        self.pip_soft = np.asarray(Image.fromarray(
            (self.pip_mask * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(1.2))).astype(float) / 255.

        barrier = None
        oref = os.path.join(mission_dir, 'v7', 'outline_ref.png')
        if os.path.exists(oref):
            b0 = np.asarray(Image.open(oref).convert('L')) > 128
            barrier = ring_of(b0, 1)   # outline original nítido, dilatado 1
        self.drop, (dx0, dy0) = clean_drop_sprite(
            poster, (296, 200, 362, 270), (232, 329),
            sil=drop_silhouette(self.H, self.W), barrier=barrier)
        self.dt0 = dy0
        self.fdrop, (fx0, fy0) = clean_drop_sprite(
            poster, (520, 238, 546, 268), (250, 532))
        self.ft0 = fy0

        # ---- base: poster sem gota, sem gotinha, sem pipeta+mãos
        base = inpaint_region(poster, self.pip_mask, m=14)
        # 2ª passada: limpa o halo de glow que ficou em volta do polígono
        halo = self.pip_mask.copy()
        for _ in range(12):
            g = halo.copy()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                g |= np.roll(np.roll(halo, dy, 0), dx, 1)
            halo = g
        R, G, B = (base[..., i].astype(int) for i in range(3))
        bright = (G - R > 35) & (G > 110)
        halo = halo & ~self.pip_mask & bright
        base = inpaint_region(base, halo, m=6)
        base = inpaint_hole(base, 296, 200, 362, 270)
        base = inpaint_hole(base, 521, 239, 544, 267)
        self.base = base

        ys, xs = np.nonzero(self.pip_mask)
        self.pip_box = (xs.min(), ys.min(), xs.max(), ys.max())
        x0, y0, x1, y1 = self.pip_box
        self.pip_sprite = np.dstack([
            poster[y0:y1 + 1, x0:x1 + 1],
            (self.pip_soft[y0:y1 + 1, x0:x1 + 1] * 255).astype(np.uint8)])

        self.impact = (329, 250)
        self.glass_water = 293

    # ------------------------------------------------------------- overlays
    def paste(self, out, sprite, cx, top, scale=1.0, alpha=1.0, stretch=1.0):
        if alpha <= 0.01 or scale <= 0.02:
            return
        h, w = sprite.shape[:2]
        nw = max(2, int(round(w * scale)))
        nh = max(2, int(round(h * scale * stretch)))
        sp = np.asarray(Image.fromarray(sprite).resize((nw, nh), Image.LANCZOS))
        a = (sp[..., 3:4] / 255.0) * alpha
        x0 = int(round(cx - nw / 2)); y0 = int(round(top))
        X0, Y0 = max(0, x0), max(0, y0)
        X1, Y1 = min(self.W, x0 + nw), min(self.H, y0 + nh)
        if X1 <= X0 or Y1 <= Y0:
            return
        sx, sy = X0 - x0, Y0 - y0
        reg = out[Y0:Y1, X0:X1].astype(float)
        spr = sp[sy:sy + (Y1 - Y0), sx:sx + (X1 - X0), :3].astype(float)
        aa = a[sy:sy + (Y1 - Y0), sx:sx + (X1 - X0)]
        out[Y0:Y1, X0:X1] = (spr * aa + reg * (1 - aa)).astype(np.uint8)

    def paste_rot(self, out, sprite, box, pivot, deg, extra=1.0):
        if abs(deg) < .01 and extra >= 1:
            a0 = sprite[..., 3:4] / 255.
        x0, y0 = box
        im = Image.fromarray(sprite)
        if abs(deg) > .01:
            pc = (pivot[0] - x0, pivot[1] - y0)
            im = im.rotate(-deg, center=pc, resample=Image.BICUBIC)
        sp = np.asarray(im)
        a = (sp[..., 3:4] / 255.) * extra
        X0, Y0 = max(0, x0), max(0, y0)
        X1, Y1 = min(self.W, x0 + sp.shape[1]), min(self.H, y0 + sp.shape[0])
        sx, sy = X0 - x0, Y0 - y0
        reg = out[Y0:Y1, X0:X1].astype(float)
        spr = sp[sy:sy + (Y1 - Y0), sx:sx + (X1 - X0), :3].astype(float)
        aa = a[sy:sy + (Y1 - Y0), sx:sx + (X1 - X0)]
        out[Y0:Y1, X0:X1] = (spr * aa + reg * (1 - aa)).astype(np.uint8)

    def glow(self, out, cx, cy, rx, ry, color, alpha):
        if alpha <= 0.004:
            return
        X0, Y0 = max(0, int(cx - rx * 2)), max(0, int(cy - ry * 2))
        X1, Y1 = min(self.W, int(cx + rx * 2)), min(self.H, int(cy + ry * 2))
        if X1 <= X0 or Y1 <= Y0:
            return
        yy, xx = np.mgrid[Y0:Y1, X0:X1]
        g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
        reg = out[Y0:Y1, X0:X1].astype(float)
        col = np.array(color, float)
        out[Y0:Y1, X0:X1] = np.clip(
            reg * (1 - g[..., None] * alpha) + col[None, None, :] * (g[..., None] * alpha),
            0, 255).astype(np.uint8)

    def ring(self, d, cx, cy, r, ry_frac, color, alpha, width=2):
        if alpha <= 0.01 or r <= 1:
            return
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        e = ((xx - cx) / r) ** 2 + ((yy - cy) / (r * ry_frac)) ** 2
        band = np.exp(-((np.sqrt(e) - 1) * r / width) ** 2)
        a = (band * alpha)[..., None]
        col = np.array(color, float)
        d[:] = np.clip(d * (1 - a) + col * a, 0, 255)

    def star(self, out, x, y, s, alpha):
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        d1 = np.minimum(np.abs(xx - x), np.abs(yy - y))
        cross = (np.abs(xx - x) + np.abs(yy - y)) <= s
        m = (cross & (d1 <= 0.8)).astype(float)
        m *= np.clip(1 - (np.abs(xx - x) + np.abs(yy - y)) / (s + 1), 0, 1)
        a = (m * alpha)[..., None]
        col = np.array((234, 255, 251), float)
        out[:] = np.clip(out * (1 - a) + col * a, 0, 255)

    # ------------------------------------------------------------- o ciclo
    def tilt_deg(self, k):
        """0 → 4° (despeja) → 0. Periódico."""
        if 1 <= k <= 4:
            return PEAK_DEG * smooth((k - 0.5) / 4)
        if 5 <= k <= 9:
            return PEAK_DEG
        if 10 <= k <= 15:
            return PEAK_DEG * (1 - smooth((k - 9.5) / 6))
        return 0.0

    def rot_tip(self, deg):
        th = math.radians(deg)
        dx, dy = TIP0[0] - PIVOT[0], TIP0[1] - PIVOT[1]
        return (PIVOT[0] + dx * math.cos(th) - dy * math.sin(th),
                PIVOT[1] + dx * math.sin(th) + dy * math.cos(th))

    def params(self, k):
        k = k % N
        p = {'tilt': self.tilt_deg(k)}
        # gota principal: solta no pico do tilt, cai, afunda e se mistura
        if 5 <= k <= 8:
            t = (k - 5) / 4
            tip = self.rot_tip(PEAK_DEG)
            p['drop'] = dict(top=lerp(tip[1] + 4, 246, ease_in(t)),
                             alpha=min(1, (k - 4) / 1.0), scale=1.0,
                             stretch=1 + .12 * math.sin(math.pi * t), sink=0)
        elif 9 <= k <= 10:
            t = (k - 8) / 2
            p['drop'] = dict(top=246 + 6 * t, alpha=1 - smooth(t),
                             scale=lerp(1, .8, t), stretch=lerp(1, .55, t), sink=1)
        else:
            p['drop'] = dict(top=246, alpha=0, scale=1, stretch=1, sink=0)
        p['rings'] = []
        for off in (0, 2):
            kk = k - (9 + off)
            if 0 <= kk <= 10:
                p['rings'].append((6 + kk * 3.4, .45 * (1 - kk / 11)))
        p['liq'] = .045 + .10 * bump(k, 12, 3.0) + .03 * math.sin(TAU * k / N)
        # gotinha da torneira: forma, cai e SE INCORPORA à água do copinho
        if 20 <= k <= 27:
            q = smooth((k - 20) / 7)
            p['fdrop'] = dict(scale=lerp(.6, 1, q),
                              top=lerp(self.ft0 - 6 * q, self.ft0, q),
                              alpha=min(1, (k - 19) / 3), sink=0)
        elif k in (28, 29, 0, 1, 2):
            idx = (k - 28) % 30
            t = idx / 5
            p['fdrop'] = dict(scale=1.0,
                              top=lerp(self.ft0, self.glass_water - 14,
                                       ease_in(t, 1.6)),
                              alpha=1.0, sink=0)
        elif 3 <= k <= 4:
            t = (k - 2) / 2
            p['fdrop'] = dict(scale=lerp(1, .8, t),
                              top=self.glass_water - 14 + 4 * t,
                              alpha=1 - smooth(t), sink=1)
        else:
            p['fdrop'] = dict(scale=1, top=self.ft0, alpha=0, sink=0)
        p['frings'] = []
        for off in (0, 1):
            kk = k - (3 + off)
            if 0 <= kk <= 5:
                p['frings'].append((3 + kk * 1.8, .4 * (1 - kk / 6)))
        p['fglint'] = .5 * max(0, 1 - abs(k - 5) / 3) if 2 <= k <= 8 else 0
        p['spk'] = [(352, 150, 1, 0.0, 4), (298, 252, 1, 2.1, 5),
                    (532, 292, 2, 1.0, 3), (210, 242, 2, 4.0, 4)]
        return p

    def frame(self, k):
        out = self.base.copy().astype(float)
        p = self.params(k)
        self.glow(out, 321, 252, 120, 20, (140, 232, 170), p['liq'])
        for r, a in p['rings']:
            self.ring(out, self.impact[0], self.impact[1] + 2, r, .26,
                      (214, 255, 224), a)
        # pipeta+mãos inclinam e voltam (relógio intocado)
        self.paste_rot(out, self.pip_sprite, (self.pip_box[0], self.pip_box[1]),
                       PIVOT, p['tilt'])
        # gota de veneno
        if p['drop']['alpha'] > 0:
            sc = p['drop']['scale']
            self.glow(out, 329, p['drop']['top'] + 34 * sc, 40 * sc, 44 * sc,
                      (120, 240, 140), .22 * p['drop']['alpha'])
            self.paste(out, self.drop, 329, p['drop']['top'], sc,
                       p['drop']['alpha'], p['drop']['stretch'])
        # gotinha da torneira + incorporação no copinho
        if p['fdrop']['alpha'] > 0:
            sc = p['fdrop']['scale']
            self.glow(out, 532, p['fdrop']['top'] + 12 * sc, 14 * sc, 16 * sc,
                      (127, 232, 228), .20 * p['fdrop']['alpha'])
            self.paste(out, self.fdrop, 532, p['fdrop']['top'], sc,
                       p['fdrop']['alpha'])
        for r, a in p['frings']:
            self.ring(out, 531, self.glass_water, r, .3, (214, 255, 250), a)
        if p['fglint'] > 0:
            self.glow(out, 531, 292, 10, 4, (240, 255, 252), p['fglint'])
        for (x, y, f, ph, s) in p['spk']:
            a = max(0.0, math.sin(TAU * f * k / N + ph)) ** 3 * .85
            if a > .02:
                self.star(out, x, y, s, a)
        return np.clip(out, 0, 255).astype(np.uint8)

    def render_all(self, out_dir):
        os.makedirs(os.path.join(out_dir, 'frames'), exist_ok=True)
        frames = []
        for k in range(N):
            fr = self.frame(k)
            frames.append(fr)
            Image.fromarray(fr).save(
                os.path.join(out_dir, 'frames', f'f{k:02d}.webp'),
                quality=82, method=5)
        return frames, self.frame(N)


def contact_sheet(frames, path, cols=6):
    rows = math.ceil(len(frames) / cols)
    fw, fh = 213, 120
    sheet = Image.new('RGB', (cols * fw, rows * (fh + 14)), (10, 12, 16))
    dr = ImageDraw.Draw(sheet)
    for i, fr in enumerate(frames):
        x, y = (i % cols) * fw, (i // cols) * (fh + 14)
        sheet.paste(Image.fromarray(fr).resize((fw, fh)), (x, y))
        dr.text((x + 3, y + fh + 1), f'#{i:02d}', fill=(154, 161, 178))
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mission', default='p5_02')
    ap.add_argument('--root', default='src/assets/anim')
    args = ap.parse_args()
    mdir = os.path.join(args.root, args.mission)
    out = os.path.join(mdir, 'v7')
    rig = Rig(mdir)
    frames, closure = rig.render_all(out)
    diff0 = np.abs(frames[0].astype(int) - closure.astype(int)).mean()
    loop = [Image.fromarray(f) for f in frames]
    loop[0].save(os.path.join(out, 'loop.webp'), format='WEBP', save_all=True,
                 append_images=loop[1:], duration=STEP_MS, loop=0,
                 quality=80, method=5)
    contact_sheet(frames, os.path.join(out, 'contact.png'))
    meta = dict(id=args.mission, version='7', method='rig-estrutural',
                fps=FPS, duration_ms=DUR_MS, frames=N, step_ms=STEP_MS,
                size=[rig.W, rig.H],
                loop=f'perfect (frame30 == frame0, meanabsdiff={diff0:.4f})',
                anchor='poster.webp (veneno verde; relógio intocado)',
                ai_assets=[],
                beats=[
                 'k00–04 · homem inclina a pipeta (0→4°)',
                 'k05–08 · no pico do tilt a gota de veneno cai no tanque',
                 'k09–10 · gota afunda e se mistura (squash+fade) + anéis',
                 'k10–15 · pipeta volta à posição original (loop fecha)',
                 'k20–29 · torneira: gotinha forma; k28–02 cai no copinho;',
                 'k03–04 · gotinha SE INCORPORA à água do copo (squash+fade+anéis)',
                ])
    json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'frames={N} fps={FPS} dur={DUR_MS}ms closure_diff={diff0:.4f}')
    print('loop.webp bytes:', os.path.getsize(os.path.join(out, 'loop.webp')))


if __name__ == '__main__':
    main()

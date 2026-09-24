#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/rig_v7.py — RIG ESTRUTURAL v7: 30 desenhos @ 5 fps, 6 s, loop perfeito.

Consistência ESTRUTURAL (não estatística como no v6, que re-desenhava quadros):

  * BASE imutável: o poster-âncora (recolorido p/ veneno verde por
    recolor_v7.py) com dois furos inpaintados por interpolação procedural.
  * A GOTA é recortada dos PRÓPRIOS pixels do poster (máscara colorida limitada
    à silhueta de gota — NUNCA carrega a beirada do tanque; o brilho é overlay
    procedural, então não há "cópia da beirada" viajando com a gota).
  * Sem sprite de coroa: a gota cai, afunda e se mistura (squash + fade + anéis).
  * Todo movimento = função PERIÓDICA de k (período 30): frame(30) == frame(0).

Saída: frames/f00..f29.webp, loop.webp (5 fps, 200 ms, loop=0), contact.png,
meta.json. Uso: python3 tools/animia/rig_v7.py --mission p5_02
"""
from __future__ import annotations
import argparse, json, math, os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TAU = 2 * math.pi
N = 30                      # quadros do ciclo
FPS = 5                     # 5 fps
DUR_MS = 6000               # 6 s
STEP_MS = DUR_MS // N       # 200 ms

DROP_C = (329, 241)         # centro do bojo da gota no poster


# ---------------------------------------------------------------- utilidades
def lerp(a, b, t): return a + (b - a) * t

def smooth(t): return t * t * (3 - 2 * t)

def bump(k, c, w):
    return math.exp(-((k - c) ** 2) / (2 * w * w))

def ease_in(t, p=1.8): return t ** p


def inpaint_hole(im, x0, y0, x1, y1, m=5, feather=2):
    """Preenche o retângulo interpolando horizontalmente as faixas vizinhas."""
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


def drop_silhouette(h, w, cx=DROP_C[0], cy=DROP_C[1], r=30, tip_y=204, pad=2):
    """Silhueta paramétrica de lágrima (bojo + cone do bico), com pad."""
    yy, xx = np.mgrid[0:h, 0:w]
    circ = (xx - cx) ** 2 + (yy - cy) ** 2 <= (r + pad) ** 2
    cone = (np.abs(xx - cx) <= np.maximum(.5, (yy - tip_y) * .62) + pad) & \
           (yy >= tip_y) & (yy <= cy + 2)
    return circ | cone


def region_grow(seed_xy, bound, iters=200):
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


def tight_drop_mask(im, x0, y0, x1, y1, sil=None, seed=(232, 329)):
    """Interior da gota = flood-fill a partir do núcleo, BLOQUEADO pelo outline
    escuro (a água do tanque tem a mesma cor, mas está fora do outline).
    + outline escuro colado ao interior (±2 px)."""
    R, G, B = im[..., 0].astype(int), im[..., 1].astype(int), im[..., 2].astype(int)
    # interior verde (veneno) OU ciano (água): o flood bloqueia no outline,
    # então a água do tanque — mesma família de cor — não vaza p/ a máscara
    cyan = (G > 140) & ((G - R) > 40) & ((B > 140) | ((G - B) > 25))
    core = (R > 180) & (G > 220) & ((B > 200) | ((G - B) > 20))
    bbox = np.zeros(im.shape[:2], bool)
    bbox[y0:y1 + 1, x0:x1 + 1] = True
    if sil is None:
        sil = bbox
    interior = region_grow(seed, (cyan | core) & bbox & sil)
    out = interior.copy()
    for _ in range(2):
        g = out.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            g |= np.roll(np.roll(out, dy, 0), dx, 1)
        out = g
    dark = (R < 95) & (G < 95) & (B < 95)
    return (out & (interior | (dark & bbox & sil))) | interior


def crop_sprite(im, mask):
    ys, xs = np.nonzero(mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    m = mask[y0:y1 + 1, x0:x1 + 1]
    am = Image.fromarray((m * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(.5))
    rgb = im[y0:y1 + 1, x0:x1 + 1]
    return np.dstack([rgb, np.asarray(am)]).astype(np.uint8), (x0, y0)


class Rig:
    def __init__(self, mission_dir):
        self.dir = mission_dir
        poster = np.asarray(
            Image.open(os.path.join(mission_dir, 'poster.webp')).convert('RGB')
        ).astype(np.uint8)
        self.poster = poster
        self.H, self.W, _ = poster.shape

        # ---- base: poster + 2 furos inpaintados (fundo NUNCA muda depois)
        base = inpaint_hole(poster, 296, 200, 362, 270)   # furo da gota central
        base = inpaint_hole(base, 521, 239, 544, 267)     # furo da gota da torneira
        self.base = base

        # ---- sprites recortados do poster (silhueta limita => sem beirada)
        sil = drop_silhouette(self.H, self.W)
        dm = tight_drop_mask(poster, 296, 200, 362, 270, sil)
        self.drop, (dx0, dy0) = crop_sprite(poster, dm)
        self.dt0 = dy0
        fm = tight_drop_mask(poster, 520, 238, 546, 268, seed=(250, 532))
        self.fdrop, (fx0, fy0) = crop_sprite(poster, fm)
        self.ft0 = fy0

        # ---- geometria medida no poster (set/2026)
        self.tip = (322, 196)          # bico da pipeta
        self.impact = (329, 250)       # ponto de impacto na superfície
        self.dial = (471.0, 142.5, 33.0)
        self.needle_a0 = -50.0
        dialcol = poster[120:165, 448:495]
        wht = dialcol[(dialcol[..., 0] > 205) & (dialcol[..., 1] > 215)]
        self.dial_face = wht.mean(axis=0).astype(np.uint8) if len(wht) else \
            np.array([222, 239, 234], np.uint8)
        self.glass_top = 283

    # ------------------------------------------------------------- overlays
    def paste(self, out, sprite, cx, top, scale=1.0, alpha=1.0, stretch=1.0):
        if alpha <= 0.01 or scale <= 0.02: return
        h, w = sprite.shape[:2]
        nw, nh = max(2, int(round(w * scale))), max(2, int(round(h * scale * stretch)))
        sp = np.asarray(Image.fromarray(sprite).resize((nw, nh), Image.LANCZOS))
        a = (sp[..., 3:4] / 255.0) * alpha
        x0 = int(round(cx - nw / 2)); y0 = int(round(top))
        x1, y1 = x0 + nw, y0 + nh
        X0, Y0 = max(0, x0), max(0, y0)
        X1, Y1 = min(self.W, x1), min(self.H, y1)
        if X1 <= X0 or Y1 <= Y0: return
        sx0, sy0 = X0 - x0, Y0 - y0
        reg = out[Y0:Y1, X0:X1].astype(float)
        spr = sp[sy0:sy0 + (Y1 - Y0), sx0:sx0 + (X1 - X0), :3].astype(float)
        aa = a[sy0:sy0 + (Y1 - Y0), sx0:sx0 + (X1 - X0)]
        out[Y0:Y1, X0:X1] = (spr * aa + reg * (1 - aa)).astype(np.uint8)

    def glow(self, out, cx, cy, rx, ry, color, alpha):
        if alpha <= 0.004: return
        x0, x1 = int(cx - rx * 2), int(cx + rx * 2)
        y0, y1 = int(cy - ry * 2), int(cy + ry * 2)
        X0, Y0 = max(0, x0), max(0, y0)
        X1, Y1 = min(self.W, x1), min(self.H, y1)
        if X1 <= X0 or Y1 <= Y0: return
        yy, xx = np.mgrid[Y0:Y1, X0:X1]
        g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
        reg = out[Y0:Y1, X0:X1].astype(float)
        col = np.array(color, float)
        out[Y0:Y1, X0:X1] = np.clip(
            reg * (1 - g[..., None] * alpha) + col[None, None, :] * (g[..., None] * alpha),
            0, 255).astype(np.uint8)

    def ring(self, d, cx, cy, r, ry_frac, color, alpha, width=2):
        if alpha <= 0.01 or r <= 1: return
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        e = ((xx - cx) / r) ** 2 + ((yy - cy) / (r * ry_frac)) ** 2
        band = np.exp(-((np.sqrt(e) - 1) * r / width) ** 2)
        a = (band * alpha)[..., None]
        col = np.array(color, float)
        d[:] = np.clip(d * (1 - a) + col * a, 0, 255)

    # ------------------------------------------------------------- o ciclo
    def params(self, k):
        """Todas as funções de movimento: periódicas em 30 (k % N)."""
        k = k % N
        p = {}
        oo = 6  # offset outline→topo do sprite (medido)
        # gota principal: forma no bico → desce → afunda e se mistura
        if 20 <= k <= 29:                      # forma no bico e desce
            q = smooth((k - 20) / 9)
            sc = lerp(.22, 1.0, q)
            p['drop'] = dict(scale=sc,
                             top=lerp(198 - oo * sc, self.dt0, q),
                             alpha=min(1, (k - 19) / 2), stretch=1.0, sink=0)
        elif k <= 2:                           # cai até o ponto do poster
            t = (k + 1) / 3
            p['drop'] = dict(scale=1.0, top=lerp(self.dt0, self.dt0 + 8,
                             ease_in(t)), alpha=1.0,
                             stretch=1 + .12 * math.sin(math.pi * t), sink=0)
        elif k <= 4:                           # afunda e se mistura (squash+fade)
            t = (k - 2) / 2
            p['drop'] = dict(scale=lerp(1.0, .8, t), top=self.dt0 + 8 + 6 * t,
                             alpha=1 - smooth(t), stretch=lerp(1.0, .55, t),
                             sink=1)
        else:
            p['drop'] = dict(scale=1, top=self.dt0, alpha=0, stretch=1, sink=0)
        # anéis de ondulação (veneno se espalhando)
        p['rings'] = []
        for off in (0, 2):
            kk = k - (3 + off)
            if 0 <= kk <= 10:
                p['rings'].append((6 + kk * 3.4, .45 * (1 - kk / 11)))
        # brilho da superfície (reage à mistura)
        p['liq'] = .045 + .10 * bump(k, 8, 3.0) + .03 * math.sin(TAU * k / N)
        # ponteiro: balança + coice no impacto
        p['needle'] = self.needle_a0 + 3 * math.sin(TAU * k / N) + 13 * bump(k, 8, 2.6)
        # gotinha da torneira (água do tanque: ciano, sprite próprio do poster)
        if 20 <= k <= 27:
            q = smooth((k - 20) / 7)
            sc = lerp(.6, 1.0, q)
            p['fdrop'] = dict(scale=sc,
                              top=lerp(self.ft0 - 6 * sc, self.ft0, q),
                              alpha=min(1, (k - 19) / 3))
        elif k in (28, 29, 0, 1, 2):
            idx = (k - 28) % 30
            t = idx / 5
            p['fdrop'] = dict(scale=1.0,
                              top=lerp(self.ft0, self.ft0 + 30, ease_in(t, 1.6)),
                              alpha=1.0)
        else:
            p['fdrop'] = dict(scale=1.0, top=self.ft0, alpha=0)
        p['fglint'] = .55 * max(0, 1 - abs(k - 4) / 3) if 1 <= k <= 7 else 0
        # brilho da pipeta (veneno) + sparkles (freqs inteiras => periódico)
        p['pip'] = .05 + .04 * math.sin(TAU * k / N)
        p['spk'] = [(352, 150, 1, 0.0, 4), (298, 252, 1, 2.1, 5),
                    (532, 292, 2, 1.0, 3), (210, 242, 2, 4.0, 4)]
        return p

    def frame(self, k):
        out = self.base.copy().astype(float)
        p = self.params(k)
        # brilhos: superfície e pipeta (veneno verde)
        self.glow(out, 321, 252, 120, 20, (140, 232, 170), p['liq'])
        self.glow(out, 300, 165, 62, 40, (140, 232, 170), p['pip'])
        # anéis de ondulação verde-claro
        for r, a in p['rings']:
            self.ring(out, self.impact[0], self.impact[1] + 2, r, .26,
                      (214, 255, 224), a)
        # gota principal + glow procedural que viaja com ela (sem beirada!)
        if p['drop']['alpha'] > 0:
            sc = p['drop']['scale']
            cy = p['drop']['top'] + 34 * sc
            self.glow(out, 329, cy, 40 * sc, 44 * sc, (120, 240, 140),
                      .22 * p['drop']['alpha'])
            self.paste(out, self.drop, 329, p['drop']['top'],
                       sc, p['drop']['alpha'], p['drop']['stretch'])
        # gotinha da torneira (ciano) + glow pequeno
        if p['fdrop']['alpha'] > 0:
            sc = p['fdrop']['scale']
            self.glow(out, 532, p['fdrop']['top'] + 12 * sc, 14 * sc, 16 * sc,
                      (127, 232, 228), .20 * p['fdrop']['alpha'])
            self.paste(out, self.fdrop, 532, p['fdrop']['top'],
                       sc, p['fdrop']['alpha'])
        if p['fglint'] > 0:
            self.glow(out, 531, 292, 10, 4, (240, 255, 252), p['fglint'])
        # sparkles
        for (x, y, f, ph, s) in p['spk']:
            a = max(0.0, math.sin(TAU * f * k / N + ph)) ** 3 * .85
            if a > .02:
                self.star(out, x, y, s, a)
        # ponteiro do manômetro
        self.needle(out, p['needle'])
        return np.clip(out, 0, 255).astype(np.uint8)

    def star(self, out, x, y, s, alpha):
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        d1 = np.minimum(np.abs(xx - x), np.abs(yy - y))
        cross = (np.abs(xx - x) + np.abs(yy - y)) <= s
        thin = d1 <= 0.8
        m = (cross & thin).astype(float)
        m *= np.clip(1 - (np.abs(xx - x) + np.abs(yy - y)) / (s + 1), 0, 1)
        a = (m * alpha)[..., None]
        col = np.array((234, 255, 251), float)
        out[:] = np.clip(out * (1 - a) + col * a, 0, 255)

    def needle(self, out, ang_deg):
        cx, cy, r = self.dial
        d = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        dr = ImageDraw.Draw(d)
        cvr = r * 0.66
        dr.ellipse([cx - cvr, cy - cvr, cx + cvr, cy + cvr],
                   fill=tuple(int(c) for c in self.dial_face))
        a = math.radians(ang_deg)
        tx, ty = cx + math.cos(a) * r * .60, cy + math.sin(a) * r * .60
        bx, by = cx - math.cos(a) * r * .26, cy - math.sin(a) * r * .26
        dr.line([bx, by, tx, ty], fill=(20, 19, 18), width=7)
        dr.line([bx, by, tx, ty], fill=(62, 107, 102), width=4)
        dr.ellipse([cx - 5, cy - 5, cx + 5, cy + 5],
                   fill=(62, 107, 102), outline=(20, 19, 18), width=3)
        out[:] = np.asarray(d).astype(float)

    # ------------------------------------------------------------- entrega
    def render_all(self, out_dir):
        os.makedirs(os.path.join(out_dir, 'frames'), exist_ok=True)
        frames = []
        for k in range(N):
            fr = self.frame(k)
            frames.append(fr)
            Image.fromarray(fr).save(
                os.path.join(out_dir, 'frames', f'f{k:02d}.webp'),
                quality=82, method=5)
        closure = self.frame(N)
        return frames, closure


def contact_sheet(frames, path, cols=6):
    n = len(frames)
    rows = math.ceil(n / cols)
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
                size=[rig.W, rig.H], loop='perfect (frame30 == frame0, '
                                          f'meanabsdiff={diff0:.4f})',
                anchor='poster.webp (fundo imutável, veneno verde)',
                ai_assets=[],
                drop_sprite='recortada dos pixels do poster (máscara colorida '
                            'limitada à silhueta — sem beirada do tanque)',
                beats=[
                 'k00–02 · gota de veneno no ponto do poster, cai no líquido',
                 'k03–04 · gota afunda e se mistura (squash + fade) + anéis',
                 'k05–19 · brilho da superfície reage; ponteiro coiceia e volta',
                 'k20–29 · gota se forma no bico da pipeta e desce até o poster',
                 'torneira: gotinha de água cai no copinho 1× por ciclo + glint',
                ])
    json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'frames={N} fps={FPS} dur={DUR_MS}ms closure_diff={diff0:.4f}')
    print('loop.webp bytes:', os.path.getsize(os.path.join(out, 'loop.webp')))


if __name__ == '__main__':
    main()

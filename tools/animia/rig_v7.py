#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/rig_v7.py — RIG ESTRUTURAL v7: 30 desenhos @ 5 fps, 6 s, loop perfeito.

A consistência aqui não é estatística (v6 re-desenhava quadros → deriva).
Ela é ESTRUTURAL, por construção:

  * BASE imutável: o poster aprovado, com dois furos tampados por inpainting
    procedural (interpolação das faixas vizinhas) — o fundo NUNCA é re-gerado.
  * A GOTA é recortada dos PRÓPRIOS pixels do poster (máscara = diff poster×base)
    — o sprite tem estilo/contorno/cor idênticos porque É o poster.
  * O SPLASH é o único asset de IA (sprite isolado em fundo magenta, chroma-key).
  * Todo movimento = função PERIÓDICA de k (período 30 quadros): somas de
    sin(2π·n·k/30) e bumps gaussianos com suporte dentro do ciclo.
    => frame(30) == frame(0) EXATO (verificado pelo qa_v7).

Saída: frames/f00..f29.webp, loop.webp (5 fps, 200 ms/quadro, loop=0),
contact.png, meta.json. Uso:

  python3 tools/animia/rig_v7.py --mission p5_02
"""
from __future__ import annotations
import argparse, json, math, os

import numpy as np
from PIL import Image, ImageDraw

TAU = 2 * math.pi
N = 30                      # quadros do ciclo
FPS = 5                     # 5 fps
DUR_MS = 6000               # 6 s
STEP_MS = DUR_MS // N       # 200 ms


# ---------------------------------------------------------------- utilidades
def lerp(a, b, t): return a + (b - a) * t

def smooth(t): return t * t * (3 - 2 * t)

def bump(k, c, w):
    """Gaussiana periódica-safe: suporte efetivo dentro de 0..30."""
    return math.exp(-((k - c) ** 2) / (2 * w * w))

def ease_in(t, p=1.8): return t ** p


def inpaint_hole(im, x0, y0, x1, y1, m=5, feather=2):
    """Preenche o retângulo interpolando horizontalmente as faixas vizinhas
    (cada linha usa a própria cor das bordas => gradientes verticais e linhas
    horizontais — borda do tanque, outlines — são reconstruídos)."""
    out = im.copy()
    h, w, _ = im.shape
    for y in range(y0, y1 + 1):
        L = im[y, max(0, x0 - m):x0].astype(float).mean(axis=0)
        R = im[y, x1 + 1:min(w, x1 + 1 + m)].astype(float).mean(axis=0)
        t = np.linspace(0, 1, x1 - x0 + 1)[:, None]
        out[y, x0:x1 + 1] = np.round(L[None, :] * (1 - t) + R[None, :] * t
                                     ).astype(np.uint8)
    # feather vertical (curvatura mínima da borda do tanque)
    xs = np.arange(w)
    sel = ((xs >= x0) & (xs <= x1))[:, None]
    for f in range(feather):
        t = (f + 1) / (feather + 1)
        for y in (y0 + f, y1 - f):
            blended = (im[y].astype(float) * (1 - t) + out[y].astype(float) * t)
            out[y] = np.where(sel, np.round(blended), out[y]).astype(np.uint8)
    return out


def region_grow(mask, seed_xy, bound, iters=60):
    """Componente conexa que contém a semente, crescendo só dentro de `bound`."""
    cur = np.zeros_like(mask)
    sy, sx = seed_xy
    cur[sy, sx] = True
    for _ in range(iters):
        nxt = cur.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt |= np.roll(np.roll(cur, dy, 0), dx, 1)
        nxt &= bound
        if (nxt == cur).all(): break
        cur = nxt
    return cur


def chroma_key_splash(path):
    """Recorta o sprite IA removendo o fundo magenta (alpha por distância)."""
    im = np.asarray(Image.open(path).convert('RGB')).astype(float)
    d = np.sqrt((im[..., 0] - 255) ** 2 + im[..., 1] ** 2 + (im[..., 2] - 255) ** 2)
    a = np.clip((d - 90) / 110, 0, 1)
    ys, xs = np.nonzero(a > 0.5)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    rgb = im[y0:y1 + 1, x0:x1 + 1]
    al = a[y0:y1 + 1, x0:x1 + 1]
    out = np.dstack([rgb, al * 255]).astype(np.uint8)
    return out


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

        # ---- sprite da gota = pixels do próprio poster, máscara pelo diff
        diff = np.abs(poster.astype(int) - base.astype(int)).sum(axis=2)
        bound = np.zeros_like(diff, bool)
        bound[200:271, 296:363] = True
        mask = region_grow(diff > 26, (235, 329), bound & (diff > 12))
        # dilata 1 px p/ pegar o anti-aliasing do outline
        dil = mask.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            dil |= np.roll(np.roll(mask, dy, 0), dx, 1)
        dil &= bound
        # silhueta paramétrica de gota (círculo + cone do bico) p/ o alpha NÃO
        # arrastar a faixa de borda reconstruída — só a gota+glow viajam.
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        circ = (xx - 329) ** 2 + (yy - 241) ** 2 <= 31 ** 2
        cone = (np.abs(xx - 329) <= np.maximum(.5, (yy - 204) * .62)) & \
               (yy >= 204) & (yy <= 243)
        sil = circ | cone
        for _ in range(5):
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                sil |= np.roll(np.roll(sil, dy, 0), dx, 1)
        alpha = np.clip(diff * 3, 0, 255) * (dil & sil)
        ys, xs = np.nonzero(alpha > 8)
        y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
        self.drop = np.dstack([poster[y0:y1 + 1, x0:x1 + 1],
                               alpha[y0:y1 + 1, x0:x1 + 1].astype(np.uint8)])
        self.drop_box = (x0, y0, x1, y1)
        self.dt0 = y0                 # topo natural do sprite (= posição poster)
        self.OUT_OFF = 206 - y0       # offset do outline da gota dentro do sprite

        # ---- sprite IA do splash (chroma-key)
        self.splash = chroma_key_splash(
            os.path.join(mission_dir, 'v7', 'ai', 'splash.png'))

        # ---- geometria medida no poster (set/2026)
        self.tip = (322, 196)          # bico da pipeta
        self.drop_top_poster = 208     # topo da gota no poster (frame 0)
        self.impact = (329, 250)       # ponto de impacto na superfície
        self.dial = (471.0, 142.5, 33.0)
        self.needle_a0 = -50.0
        dialcol = poster[120:165, 448:495]
        wht = dialcol[(dialcol[..., 0] > 205) & (dialcol[..., 1] > 215)]
        self.dial_face = wht.mean(axis=0).astype(np.uint8) if len(wht) else \
            np.array([222, 239, 234], np.uint8)
        self.faucet = (532, 240)       # topo da gotinha da torneira
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
        oo = self.OUT_OFF
        # gota principal — `top` = topo do SPRITE; outline fica em top+oo*scale
        if 20 <= k <= 29:                      # forma no bico e desce
            q = smooth((k - 20) / 9)
            sc = lerp(.22, 1.0, q)
            p['drop'] = dict(scale=sc,
                             top=lerp(198 - oo * sc, self.dt0, q),
                             alpha=min(1, (k - 19) / 2), stretch=1.0)
        elif k <= 2:                           # assenta no ponto do poster
            t = (k + 1) / 3
            p['drop'] = dict(scale=1.0, top=lerp(self.dt0, self.dt0 + 8,
                             ease_in(t)), alpha=1.0,
                             stretch=1 + .12 * math.sin(math.pi * t))
        else:
            p['drop'] = dict(scale=1, top=self.dt0, alpha=0, stretch=1)
        # splash (IA) + anéis
        if 3 <= k <= 8:
            t = (k - 3) / 5
            p['splash'] = dict(scale=lerp(.07, .14, smooth(t)),
                               alpha=min(1, (k - 2) / 1.2) * max(0, 1 - max(0, (k - 6)) / 2.6))
        else:
            p['splash'] = dict(scale=.07, alpha=0)
        p['rings'] = []
        for off in (0, 2):
            kk = k - (3 + off)
            if 0 <= kk <= 10:
                p['rings'].append((6 + kk * 3.4, .45 * (1 - kk / 11)))
        # brilho da superfície (reage ao splash)
        p['liq'] = .045 + .10 * bump(k, 8, 3.0) + .03 * math.sin(TAU * k / N)
        # ponteiro: balança + coice no splash
        p['needle'] = self.needle_a0 + 3 * math.sin(TAU * k / N) + 13 * bump(k, 8, 2.6)
        # gotinha da torneira (mesmo sprite do poster, escala .38)
        if 20 <= k <= 27:
            q = smooth((k - 20) / 7)
            sc = lerp(.15, .38, q)
            p['fdrop'] = dict(scale=sc,
                              top=lerp(232 - oo * sc, 242 - oo * .38, q),
                              alpha=min(1, (k - 19) / 3))
        elif k in (28, 29, 0, 1, 2):
            idx = (k - 28) % 30
            t = idx / 5
            p['fdrop'] = dict(scale=.38,
                              top=lerp(242 - oo * .38, 272, ease_in(t, 1.6)),
                              alpha=1.0)
        else:
            p['fdrop'] = dict(scale=.38, top=242 - oo * .38, alpha=0)
        p['fglint'] = .55 * max(0, 1 - abs(k - 4) / 3) if 1 <= k <= 7 else 0
        # brilho da pipeta + sparkles (freqs inteiras => periódico)
        p['pip'] = .05 + .04 * math.sin(TAU * k / N)
        p['spk'] = [(352, 150, 1, 0.0, 4), (298, 252, 1, 2.1, 5),
                    (532, 292, 2, 1.0, 3), (210, 242, 2, 4.0, 4)]
        return p

    def frame(self, k):
        out = self.base.copy().astype(float)
        p = self.params(k)
        # brilho da superfície e da pipeta (aditivos, sutis)
        self.glow(out, 321, 252, 120, 20, (127, 232, 228), p['liq'])
        self.glow(out, 300, 165, 62, 40, (127, 232, 228), p['pip'])
        # anéis de ondulação
        for r, a in p['rings']:
            self.ring(out, self.impact[0], self.impact[1] + 2, r, .26,
                      (207, 252, 247), a)
        # splash IA
        if p['splash']['alpha'] > 0:
            h = self.splash.shape[0]
            sc = p['splash']['scale']
            self.paste(out, self.splash, self.impact[0],
                       self.impact[1] - h * sc * .92, sc, p['splash']['alpha'])
        # gota principal / torneira (pixels do poster)
        if p['drop']['alpha'] > 0:
            self.paste(out, self.drop, 329, p['drop']['top'],
                       p['drop']['scale'], p['drop']['alpha'], p['drop']['stretch'])
        if p['fdrop']['alpha'] > 0:
            self.paste(out, self.drop, self.faucet[0], p['fdrop']['top'],
                       p['fdrop']['scale'], p['fdrop']['alpha'])
        if p['fglint'] > 0:
            self.glow(out, 531, 292, 10, 4, (240, 255, 252), p['fglint'])
        # sparkles
        for (x, y, f, ph, s) in p['spk']:
            a = max(0.0, math.sin(TAU * f * k / N + ph)) ** 3 * .85
            if a > .02:
                self.star(out, x, y, s, a)
        # ponteiro do manômetro (tampa o original e redesenha girando)
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
        # prova do loop: quadro 30 deve ser idêntico ao quadro 0
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
                anchor='poster.webp (fundo imutável)',
                ai_assets=['ai/splash.png (chroma-key)'],
                drop_sprite='recortada dos pixels do poster (diff vs base)',
                beats=[
                 'k00–02 · gota no ponto do poster, assenta no líquido',
                 'k03–08 · SPLASH (sprite IA) + anéis de ondulação',
                 'k09–19 · brilho da superfície reage; ponteiro coiceia e volta',
                 'k20–29 · gota se forma no bico da pipeta e desce até o ponto do poster',
                 'torneira: gotinha cai no copinho 1× por ciclo (k28–02) + glint',
                ])
    json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'),
              ensure_ascii=False, indent=1)
    print(f'frames={N} fps={FPS} dur={DUR_MS}ms closure_diff={diff0:.4f}')
    print('loop.webp bytes:', os.path.getsize(os.path.join(out, 'loop.webp')))


if __name__ == '__main__':
    main()

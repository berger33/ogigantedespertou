#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tools/animia/riglib.py — helpers do RIG ESTRUTURAL v7 (compartilhados entre
missões). Consistência estrutural: base imutável + overlays periódicos
(período N=30 => frame(30)==frame(0)). Ver docs/ANIM_V7_RIG.md."""
from __future__ import annotations
import json, math, os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TAU = 2 * math.pi
N = 30
FPS = 5
DUR_MS = 6000
STEP_MS = DUR_MS // N


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


def region_grow(seed_xy, bound, iters=400):
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


def ring_of(mask, n=2):
    out = mask.copy()
    for _ in range(n):
        g = out.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            g |= np.roll(np.roll(out, dy, 0), dx, 1)
        out = g
    return out


class BaseRig:
    def __init__(self, poster):
        self.poster = poster
        self.H, self.W, _ = poster.shape

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

    def star(self, out, x, y, s, alpha, color=(234, 255, 251)):
        yy, xx = np.mgrid[0:self.H, 0:self.W]
        d1 = np.minimum(np.abs(xx - x), np.abs(yy - y))
        cross = (np.abs(xx - x) + np.abs(yy - y)) <= s
        m = (cross & (d1 <= 0.8)).astype(float)
        m *= np.clip(1 - (np.abs(xx - x) + np.abs(yy - y)) / (s + 1), 0, 1)
        a = (m * alpha)[..., None]
        col = np.array(color, float)
        out[:] = np.clip(out * (1 - a) + col * a, 0, 255)


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


def finalize(rig, out_dir, meta_extra=None):
    """Renderiza 30 quadros + closure, grava frames/loop.webp/loop.gif/
    contact.png/meta.json e roda o QA. Retorna (frames, closure, qa)."""
    os.makedirs(os.path.join(out_dir, 'frames'), exist_ok=True)
    frames = [rig.frame(k) for k in range(N)]
    closure = rig.frame(N)
    for k, fr in enumerate(frames):
        Image.fromarray(fr).save(
            os.path.join(out_dir, 'frames', f'f{k:02d}.webp'),
            quality=82, method=5)
    loop = [Image.fromarray(f) for f in frames]
    loop[0].save(os.path.join(out_dir, 'loop.webp'), format='WEBP',
                 save_all=True, append_images=loop[1:], duration=STEP_MS,
                 loop=0, quality=80, method=5)
    gifs = [f.convert('P', palette=Image.ADAPTIVE, colors=128) for f in loop]
    gifs[0].save(os.path.join(out_dir, 'loop.gif'), save_all=True,
                 append_images=gifs[1:], duration=STEP_MS, loop=0,
                 optimize=True)
    contact_sheet(frames, os.path.join(out_dir, 'contact.png'))
    qa = run_qa(frames, closure, rig.base, out_dir)
    meta = dict(version='7', method='rig-estrutural', fps=FPS,
                duration_ms=DUR_MS, frames=N, step_ms=STEP_MS,
                size=[rig.W, rig.H],
                loop=f'perfect (frame30 == frame0, '
                     f'meanabsdiff={qa["Q1_loop_closure"]["meanabsdiff"]})',
                **(meta_extra or {}))
    json.dump(meta, open(os.path.join(out_dir, 'meta.json'), 'w'),
              ensure_ascii=False, indent=1)
    return frames, closure, qa


def run_qa(frames, closure, base, out_dir):
    qa = {}
    d = float(np.abs(frames[0].astype(int) - closure.astype(int)).mean())
    qa['Q1_loop_closure'] = dict(ok=d == 0.0, meanabsdiff=round(d, 4))
    b = base.astype(int)
    union = np.zeros(frames[0].shape[:2], bool)
    for fr in frames:
        union |= np.abs(fr.astype(int) - b).sum(axis=2) > 2
    qa['Q3_fundo_cobertura'] = dict(ok=bool(union.mean() <= .45),
                                    cobertura=round(float(union.mean()) * 100, 2))
    worst = max(int(np.abs(fr.astype(int) - b).sum(axis=2)[~union].max())
                for fr in frames)
    qa['Q2_fundo_intacto'] = dict(ok=worst <= 2, max_diff_fora_uniao=worst)
    lum = [float(np.asarray(Image.fromarray(f).convert('L')).mean())
           for f in frames]
    qa['Q4_flicker'] = dict(ok=bool(np.std(lum) <= 6),
                            std=round(float(np.std(lum)), 2))
    deltas = [round(float(np.abs(frames[i].astype(int) -
                                 frames[(i + 1) % N].astype(int)).mean()), 2)
              for i in range(N)]
    qa['Q5_step_delta'] = dict(ok=max(deltas) <= 20, max=max(deltas),
                               mean=round(float(np.mean(deltas)), 2))
    lp = os.path.join(out_dir, 'loop.webp')
    data = open(lp, 'rb').read()
    i, nf, durs = 12, 0, []
    while i + 8 <= len(data):
        fourcc = data[i:i + 4]
        size = int.from_bytes(data[i + 4:i + 8], 'little')
        if fourcc == b'ANMF':
            nf += 1
            durs.append(int.from_bytes(data[i + 20:i + 23], 'little'))
        i += 8 + size + (size & 1)
    sz = os.path.getsize(lp)
    qa['Q6_entrega'] = dict(ok=(nf == 30 and all(x == 200 for x in durs)
                                and sz <= 900_000 and data[:4] == b'RIFF'),
                            n_frames=nf, step_ms=200, bytes=sz)
    qa['all_ok'] = all(v['ok'] for k, v in qa.items() if k.startswith('Q'))
    json.dump(qa, open(os.path.join(out_dir, 'qa.json'), 'w'), indent=1,
              default=lambda o: bool(o) if isinstance(o, np.bool_) else
              (float(o) if isinstance(o, np.floating) else int(o)))
    for k, v in qa.items():
        if k.startswith('Q'):
            print(('PASS' if v['ok'] else 'FAIL'), k,
                  {a: c for a, c in v.items() if a != 'ok'})
    print('ALL OK' if qa['all_ok'] else 'REPROVADO')
    return qa

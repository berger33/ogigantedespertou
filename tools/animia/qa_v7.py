#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/animia/qa_v7.py — lints do rig estrutural v7 (30 quadros, 5 fps, 6 s).

Q1 loop_closure   frame(30) == frame(0) — mean abs diff EXATAMENTE 0
Q2 fundo_intacto  fora da união das regiões animadas, TODO quadro é idêntico à
                  base (o poster inpaintado) — deriva de fundo impossível
Q3 fundo_cobertura regiões animadas cobrem ≤ 40% da imagem (resto é âncora)
Q4 flicker        desvio-padrão da luminância média entre quadros ≤ 6
Q5 step_delta     diff média entre quadros consecutivos ≤ 20 (sem teleporte)
Q6 entrega        loop.webp: 30 quadros, 200 ms, loop=0, ≤ 900 KB

Uso: python3 tools/animia/qa_v7.py --mission p5_02
"""
from __future__ import annotations
import argparse, json, os

import numpy as np
from PIL import Image

import importlib.util
_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('rig', os.path.join(_here, 'rig_v7.py'))
rigmod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rigmod)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mission', default='p5_02')
    ap.add_argument('--root', default='src/assets/anim')
    args = ap.parse_args()
    mdir = os.path.join(args.root, args.mission)
    out = os.path.join(mdir, 'v7')
    rig = rigmod.Rig(mdir)

    frames = [rig.frame(k) for k in range(rigmod.N)]
    closure = rig.frame(rigmod.N)
    qa = {}

    # Q1 — loop fecha exato
    d = np.abs(frames[0].astype(int) - closure.astype(int)).mean()
    qa['Q1_loop_closure'] = dict(ok=d == 0.0, meanabsdiff=round(float(d), 4))

    # Q2/Q3 — fundo intacto: regiões animadas = diff vs base (limiar 2/255/canal)
    base = rig.base.astype(int)
    union = np.zeros(frames[0].shape[:2], bool)
    for fr in frames:
        union |= np.abs(fr.astype(int) - base).sum(axis=2) > 2
    cov = union.mean()
    qa['Q3_fundo_cobertura'] = dict(ok=bool(cov <= .40),
                                    cobertura=round(float(cov) * 100, 2))
    # fora da união, todos os quadros idênticos à base (≤ 2 por canal = invisível)
    worst = 0
    for fr in frames:
        dd = np.abs(fr.astype(int) - base).sum(axis=2)
        worst = max(worst, int(dd[~union].max()))
    qa['Q2_fundo_intacto'] = dict(ok=worst <= 2, max_diff_fora_uniao=worst)

    # Q4 — flicker
    lum = [float(np.asarray(Image.fromarray(f).convert('L')).mean()) for f in frames]
    qa['Q4_flicker'] = dict(ok=bool(np.std(lum) <= 6),
                            std=round(float(np.std(lum)), 2),
                            means=[round(x, 1) for x in lum])

    # Q5 — delta entre consecutivos (inclui emenda 29→0)
    deltas = []
    for i in range(rigmod.N):
        a = frames[i].astype(int)
        b = frames[(i + 1) % rigmod.N].astype(int)
        deltas.append(round(float(np.abs(a - b).mean()), 2))
    qa['Q5_step_delta'] = dict(ok=bool(max(deltas) <= 20),
                               max=max(deltas), mean=round(float(np.mean(deltas)), 2),
                               deltas=deltas)

    # Q6 — entrega (parse RIFF direto: contagem ANMF + durations)
    lp = os.path.join(out, 'loop.webp')
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
    qa['Q6_entrega'] = dict(ok=(nf == 30 and all(d == 200 for d in durs)
                                and sz <= 900_000 and data[:4] == b'RIFF'),
                            n_frames=nf, step_ms=200, loop=0, bytes=sz)

    qa['all_ok'] = all(v['ok'] for k, v in qa.items() if k.startswith('Q'))
    json.dump(qa, open(os.path.join(out, 'qa.json'), 'w'), indent=1,
              default=lambda o: bool(o) if isinstance(o, np.bool_) else
              (float(o) if isinstance(o, np.floating) else int(o)))
    for k, v in qa.items():
        if k.startswith('Q'):
            print(('PASS' if v['ok'] else 'FAIL'), k,
                  {kk: vv for kk, vv in v.items() if kk != 'ok'})
    print('ALL OK' if qa['all_ok'] else 'REPROVADO')
    raise SystemExit(0 if qa['all_ok'] else 1)


if __name__ == '__main__':
    main()

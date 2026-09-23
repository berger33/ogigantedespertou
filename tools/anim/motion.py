#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/anim/motion.py — curvas, tokens de timing e agenda de quadros (spec v4).

Regras que este módulo garante (docs/ANIM_V4_PLANO_REMAKE.md §2, §4, §6):
  * 5,00 s ± 0,05 por clip;
  * segmento A: 3,0–4,0 s a 10 fps (setup + ação);
  * segmento B: 1,0–2,0 s a 12–18 fps (rajada / finalização);
  * total de quadros 52–66;
  * tokens de timing: anticipate / act / impact / follow / settle / hold / blink;
  * easings com antecipação, overshoot e settle (nada de seno contínuo = "gelatina").

Uso típico:
    sched = build_schedule("P2")                 # [(t_ms, dur_ms, fps), ...] 60 quadros
    tr = Track().key(0, 0, "hold").key(300, 0, "hold").key(600, -40, "back_out")
    y = tr.at(t_ms)
"""
from __future__ import annotations
import math
from typing import Callable, Dict, List, Sequence, Tuple

# --------------------------------------------------------------------------- #
# Easings (o vocabulário de curvas da v4)
# --------------------------------------------------------------------------- #
def _lin(u: float) -> float: return u
def _quad_in(u: float) -> float: return u * u
def _quad_out(u: float) -> float: return 1 - (1 - u) ** 2
def _cubic_in(u: float) -> float: return u ** 3
def _cubic_out(u: float) -> float: return 1 - (1 - u) ** 3
def _cubic_inout(u: float) -> float:
    return 4 * u ** 3 if u < .5 else 1 - (-2 * u + 2) ** 3 / 2
def _back_out(u: float, s: float = 1.70158) -> float:
    """overshoot clássico: passa do alvo e volta (R6)."""
    c = s + 1
    return 1 + c * (u - 1) ** 3 + s * (u - 1) ** 2
def _back_in(u: float, s: float = 1.70158) -> float:
    """antecipação clássica: recua antes de partir (R6)."""
    c = s + 1
    return c * u ** 3 - s * u ** 2
def _back_inout(u: float) -> float:
    if u < .5:
        return _back_in(u * 2) / 2
    return .5 + _back_out(u * 2 - 1) / 2
def _settle(u: float) -> float:
    """overshoot amortecido: 1 pico pequeno e assenta (follow-through + settle)."""
    if u >= 1: return 1.0
    return 1 - math.exp(-6.0 * u) * math.cos(9.0 * u) * (1 - u) ** 0.7
def _hold(u: float) -> float: return 0.0
def _step(u: float) -> float: return 0.0 if u < 1 else 1.0

EASINGS: Dict[str, Callable[[float], float]] = {
    "lin": _lin,
    "quad_in": _quad_in, "quad_out": _quad_out,
    "cubic_in": _cubic_in, "cubic_out": _cubic_out, "cubic_inout": _cubic_inout,
    "back_in": _back_in, "back_out": _back_out, "back_inout": _back_inout,
    "settle": _settle, "hold": _hold, "step": _step,
}

# --------------------------------------------------------------------------- #
# Tokens de timing (§6) — duração em ms e easing default
# --------------------------------------------------------------------------- #
TOKENS: Dict[str, Tuple[int, str]] = {
    "anticipate": (300, "back_in"),     # 3 f @10fps  — recuo antes da ação
    "act":        (300, "cubic_in"),    # 2–4 f @10fps
    "impact":     (180, "step"),        # 2–4 f @16fps — colisão / carimbo
    "follow":     (360, "settle"),      # 4–6 f @14fps — follow-through
    "settle":     (800, "settle"),      # 6–10 f @10fps
    "hold":       (300, "hold"),        # 3 f @10fps (1 quadro encodado)
    "blink":      (167, "step"),        # 2 f @12fps
}

# --------------------------------------------------------------------------- #
# Agenda de quadros (fps variável de verdade)
# --------------------------------------------------------------------------- #
PROFILES: Dict[str, List[Tuple[float, float, int]]] = {
    # perfil: [(inicio_s, fim_s, fps), ...]  → A = 10fps, B = 12–18fps
    "P1": [(0.0, 3.0, 10), (3.0, 5.0, 15)],   # 30 + 30 = 60 f  (ação pesada)
    "P2": [(0.0, 3.4, 10), (3.4, 5.0, 16)],   # 34 + 26 = 60 f  (clímax no meio)
    "P3": [(0.0, 4.0, 10), (4.0, 5.0, 14)],   # 40 + 14 = 54 f  (ritual / solene)
}

def build_schedule(profile: str = "P2") -> List[Tuple[int, int, int]]:
    """Retorna [(t_inicio_ms, duracao_ms, fps)] com duração por quadro.

    O último quadro de cada segmento carrega o resto do tempo do segmento,
    de modo que a soma feche exatamente 5000 ms (loop sem deriva).
    """
    segs = PROFILES[profile]
    sched: List[Tuple[int, int, int]] = []
    for (a, b, fps) in segs:
        step = 1000.0 / fps
        n = int(round((b - a) * fps))
        t0 = a * 1000.0
        seg_end = b * 1000.0
        for i in range(n):
            t = t0 + i * step
            tend = t0 + (i + 1) * step if i < n - 1 else seg_end
            sched.append((int(round(t)), int(round(tend - t)), fps))
    return sched


def schedule_stats(sched: Sequence[Tuple[int, int, int]]) -> dict:
    total = sum(d for _, d, _ in sched)
    seg_a = [(t, d, f) for (t, d, f) in sched if f == 10]
    seg_b = [(t, d, f) for (t, d, f) in sched if f != 10]
    return {
        "frames": len(sched),
        "duration_ms": total,
        "segA_s": round(sum(d for _, d, _ in seg_a) / 1000.0, 3),
        "segB_s": round(sum(d for _, d, _ in seg_b) / 1000.0, 3),
        "segB_fps": sorted({f for _, _, f in seg_b}),
    }


# --------------------------------------------------------------------------- #
# Track: chaves por tempo (ms) com easing entre chaves
# --------------------------------------------------------------------------- #
class Track:
    """Sequência de chaves (t_ms, valor, easing_ate_a_proxima_chave)."""

    def __init__(self, default: float = 0.0):
        self.keys: List[Tuple[float, float, str]] = []
        self.default = default

    def key(self, t_ms: float, value: float, ease: str = "lin") -> "Track":
        self.keys.append((float(t_ms), float(value), ease))
        return self

    def at(self, t_ms: float) -> float:
        if not self.keys:
            return self.default
        ks = self.keys
        if t_ms <= ks[0][0]:
            return ks[0][1]
        for i in range(len(ks) - 1):
            t0, v0, ease = ks[i]
            t1, v1, _ = ks[i + 1]
            if t0 <= t_ms <= t1:
                if t1 <= t0:
                    return v1
                u = (t_ms - t0) / (t1 - t0)
                f = EASINGS.get(ease, _lin)
                return v0 + (v1 - v0) * f(min(max(u, 0.0), 1.0))
        return ks[-1][1]

    # atalhos de direção de arte ------------------------------------------- #
    def hold(self, t0: float, t1: float, value: float) -> "Track":
        return self.key(t0, value, "hold").key(t1, value, "hold")


def track_from_keys(keys: Sequence[Sequence]) -> Track:
    tr = Track()
    for k in keys:
        tr.key(k[0], k[1], k[2] if len(k) > 2 else "lin")
    return tr


if __name__ == "__main__":
    for p in ("P1", "P2", "P3"):
        s = build_schedule(p)
        print(p, schedule_stats(s))

#!/usr/bin/env python3
"""
gen_animations.py — gera o conteúdo de ANIMAÇÃO das missões (docs/ANIMATION_PLAN.md).

Espelho data-driven da gramática estudada no vídeo de referência (sem copiar arte):
cada missão vira uma "cena emoldurada" em camadas  bg (estático) → ator (loop)
→ fx (partículas), com 2 estados: idle (sutil) e running (ação, ativado pelo
Coordenador). A arte é SVG ORIGINAL na paleta do ART_BIBLE.md.

Saídas:
  - src/content/animations.json   (spec que o renderizador lê)
  - src/assets/anim/<id>/scene.svg (camadas com [data-layer])

Uso: python3 tools/gen_animations.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"
ASSETS = ROOT / "src" / "assets" / "anim"

# Paleta oficial (ART_BIBLE.md §2)
P = {
    "bg_top": "#123A24", "bg_bot": "#0B1F15", "deep": "#072718",
    "building": "#0A1B12", "ink": "#16130F", "paper": "#F2E9D0",
    "green": "#39FF9C", "green_mid": "#24B26B", "gold": "#D4AF37",
    "violet": "#B57BFF", "stamp": "#B3261E", "muted": "#9AAEA2",
}

STAGE = {"width": 320, "height": 88}


def _skyline():
    """Linha do horizonte (HQ/ladrões de cueca) — estático. Retorna SVG."""
    rects = [
        (0, 62, 26, 26), (30, 54, 22, 34), (56, 66, 30, 22), (90, 57, 20, 31),
        (114, 48, 24, 40), (142, 64, 22, 24), (168, 54, 18, 34), (190, 60, 24, 28),
        (218, 50, 20, 38), (242, 63, 24, 25), (270, 56, 22, 32), (296, 60, 24, 28),
    ]
    out = [f'<rect width="320" height="88" fill="url(#sky)"/>']
    out.append('<g id="bg">')
    for x, y, w, h in rects:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{P["building"]}"/>')
    # janelas acesas (detalhe)
    for ex, ey in [(4, 68), (36, 60), (120, 54), (148, 70), (224, 56), (274, 62)]:
        out.append(f'<rect x="{ex}" y="{ey}" width="3" height="4" fill="{P["green_mid"]}" opacity=".55"/>')
    # linha do chão
    out.append(f'<rect x="0" y="85" width="320" height="3" fill="{P["ink"]}" opacity=".8"/>')
    out.append('</g>')
    return "\n  ".join(out)


def scene_p1_01():
    """Comprar as maiores empresas com cripto: pregão + gráfico subindo + clique."""
    chart = "M32,58 L48,50 L64,52 L80,42 L96,34 L114,26"
    svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 88" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Comprar as maiores empresas com cripto">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{P['bg_top']}"/>
      <stop offset="1" stop-color="{P['bg_bot']}"/>
    </linearGradient>
    <linearGradient id="scr" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0E3A22"/>
      <stop offset="1" stop-color="{P['deep']}"/>
    </linearGradient>
  </defs>
  {_skyline()}

  <!-- monitor do pregão (ator) -->
  <g id="monitor">
    <rect x="122" y="70" width="6" height="10" fill="{P['ink']}"/>
    <rect x="120" y="80" width="10" height="2" fill="{P['ink']}"/>
    <rect x="20" y="16" width="122" height="58" rx="6" fill="{P['ink']}" stroke="{P['gold']}" stroke-width="1.5"/>
    <rect x="26" y="22" width="110" height="46" rx="3" fill="url(#scr)"/>
    <g opacity=".22">
      <path d="M26 44 L136 44 M26 54 L136 54 M63 22 L63 68 M100 22 L100 68" stroke="{P['green']}" stroke-width="1"/>
    </g>
    <path d="{chart}" fill="none" stroke="{P['green']}" stroke-width="2" stroke-linecap="round"/>
    <circle cx="32" cy="58" r="2" fill="{P['gold']}"/>
    <circle cx="114" cy="26" r="2.6" fill="{P['gold']}"/>
    <rect x="50" y="40" width="40" height="15" rx="4" fill="{P['gold']}"/>
    <path d="M70 44 L63 50 L77 50 Z" fill="{P['ink']}"/>
  </g>

  <!-- cursor clicando no COMPRAR (ator) -->
  <g id="hand">
    <g transform="translate(98 52)">
      <path d="M0 0 L0 13 L4 9.5 L7 15 L10.5 13.5 L7.5 8 L12 8 Z" fill="{P['paper']}" stroke="{P['ink']}" stroke-width="1"/>
    </g>
  </g>

  <!-- lamp piscando (fx) -->
  <circle id="lamp" cx="150" cy="40" r="3" fill="{P['green']}"/>

  <!-- ticker de pregão (fx) -->
  <g id="ticker">
    <g>
      <text x="0" y="10" font-family="monospace" font-size="7.5" fill="{P['green']}" opacity=".9">▲ C+MENTES +2,7%   ▲ ZAP-INDEX +3,1%   ▲ BOATO 500 +5,4%   </text>
      <text x="196" y="10" font-family="monospace" font-size="7.5" fill="{P['green']}" opacity=".9">▲ C+MENTES +2,7%   ▲ ZAP-INDEX +3,1%   ▲ BOATO 500 +5,4%   </text>
    </g>
  </g>

  <!-- gráfico de barras (ator) -->
  <g id="bars">
    <rect x="176" y="60" width="13" height="20" fill="{P['green_mid']}"/>
    <rect x="194" y="48" width="13" height="32" fill="{P['green']}"/>
    <rect x="212" y="36" width="13" height="44" fill="{P['green']}"/>
    <rect x="230" y="22" width="13" height="58" fill="{P['gold']}"/>
    <rect x="248" y="30" width="13" height="50" fill="{P['violet']}" opacity=".85"/>
    <path d="M170 60 L258 26" stroke="{P['green']}" stroke-width="1.4" stroke-dasharray="3 3" opacity=".6"/>
  </g>

  <!-- moedas de cripto subindo (fx) -->
  <g id="coins">
    <g class="coin"><circle cx="272" cy="52" r="5" fill="{P['deep']}" stroke="{P['gold']}" stroke-width="1.6"/><circle cx="272" cy="52" r="2" fill="{P['green']}"/></g>
    <g class="coin"><circle cx="286" cy="60" r="4" fill="{P['deep']}" stroke="{P['gold']}" stroke-width="1.6"/><circle cx="286" cy="60" r="1.6" fill="{P['green']}"/></g>
    <g class="coin"><circle cx="300" cy="48" r="4.4" fill="{P['deep']}" stroke="{P['gold']}" stroke-width="1.6"/><circle cx="300" cy="48" r="1.8" fill="{P['violet']}"/></g>
    <g class="coin"><circle cx="280" cy="66" r="3.6" fill="{P['deep']}" stroke="{P['green_mid']}" stroke-width="1.6"/><circle cx="280" cy="66" r="1.4" fill="{P['gold']}"/></g>
    <g class="coin"><circle cx="294" cy="72" r="4.6" fill="{P['deep']}" stroke="{P['gold']}" stroke-width="1.6"/><circle cx="294" cy="72" r="1.8" fill="{P['green']}"/></g>
    <g class="coin"><circle cx="266" cy="70" r="3.4" fill="{P['deep']}" stroke="{P['violet']}" stroke-width="1.6"/><circle cx="266" cy="70" r="1.4" fill="{P['gold']}"/></g>
  </g>
</svg>
'''
    return "\n".join(line for line in svg.splitlines() if line.strip() != "")


# ---------------- catálogo de cenas (Lote 0 = p1_01; demais plugáveis) ----------------
SCENES = {
    "p1_01": {
        "label": "Comprar as maiores empresas com cripto",
        "accent": P["violet"],
        "svg": scene_p1_01(),
        "layers": [
            {"id": "bars",   "loop": "pump",   "dur": 1.8, "child": True,  "delay": 0.12},
            {"id": "hand",   "loop": "press",  "dur": 1.2},
            {"id": "lamp",   "loop": "blink",  "dur": 1.1, "fx": True},
            {"id": "ticker", "loop": "scroll", "dur": 6.0, "fx": True},
            {"id": "coins",  "loop": "rise",   "dur": 1.5, "child": True, "delay": 0.18, "fx": True},
        ],
    },
}


def build_spec():
    scenes = {}
    for sid, sc in SCENES.items():
        rel = f"assets/anim/{sid}/scene.svg"
        scenes[sid] = {
            "label": sc["label"],
            "accent": sc["accent"],
            "src": rel,
            "layers": sc["layers"],
        }
    return {
        "_comment": (
            "Especificação de animação das missões (docs/ANIMATION_PLAN.md). "
            "Renderizador: app.js (AnimStage). Cena = camadas bg/ator/fx; estados "
            "off/idle/running. Lote 0 = cena completa p1_01; demais plugáveis."
        ),
        "version": 1,
        "stage": STAGE,
        "scenes": scenes,
    }


def main():
    spec = build_spec()
    (CONTENT / "animations.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for sid, sc in SCENES.items():
        d = ASSETS / sid
        d.mkdir(parents=True, exist_ok=True)
        (d / "scene.svg").write_text(sc["svg"], encoding="utf-8")
        print(f"  wrote {d / 'scene.svg'} ({len(sc['svg'])} bytes)")
    print(f"wrote {CONTENT / 'animations.json'} com {len(spec['scenes'])} cena(s)")


if __name__ == "__main__":
    main()

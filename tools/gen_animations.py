#!/usr/bin/env python3
"""
gen_animations.py — gera o conteúdo de ANIMAÇÃO das missões (docs/ANIMATION_PLAN.md).

Segunda geração: cada missão vira uma "cena de dossiê conspiratório"
(em vez de planilha abstrata):
  - sala secreta (parede/holofote/olho na janela/quadro de cordas/mesa)
  - o personagem "O Grifter" numa POSE temática
  - um OBJETO de cena sob holofote (o alvo da missão)
  - uma PLAQUETA com o título + piada curta (o humor)
  - partículas/efeitos (prop) com loop tipado

Arte 100% procedural/original (tools/art_kit.py) na paleta do ART_BIBLE.md.

Saídas:
  - src/content/animations.json   (spec que o renderizador lê)
  - src/assets/anim/<id>/scene.svg

Cada missão tem 3 estados: off (sem posse), idle (produção manual) e running
(automatizado pelo Coordenador). Loops mantidos no apêndice `src/theme/app.css`.

Uso: python3 tools/gen_animations.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_kit as ak

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"
ASSETS = ROOT / "src" / "assets" / "anim"

# --------------------------------------------------------------------------
# Cenas da Deep Web (p1_01..p1_10): pose, spot, prop, jogada, placa
# --------------------------------------------------------------------------
DEEP_WEB = [
    {
        "id": "p1_01",
        "pose": "typing", "flip": False,
        "spot": "monitors", "prop": "brains",
        "accent": "#B57BFF",
        "line1": "COMPRAR COM CRIPTO",
        "line2": "carteira_real_v2_FINAL.docx",
        "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"],
    },
    {
        "id": "p1_02",
        "pose": "poster", "flip": False,
        "spot": "telegraph", "prop": "sheets",
        "accent": "#39FF9C",
        "line1": "PLANTAR FAKE NEWS",
        "line2": "a manchete sai antes do fato",
        "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"],
    },
    {
        "id": "p1_03",
        "pose": "pet", "flip": True,
        "spot": "iguana", "prop": "eyeicons",
        "accent": "#39FF9C",
        "line1": "AMIGOS REPTILIANOS",
        "line2": "café com um escamoso",
        "loops": ["marcha", "bracos", "cabeca", "sway", "rise", "blink", "flicker"],
    },
    {
        "id": "p1_04",
        "pose": "handoff", "flip": False,
        "spot": "envelope", "prop": "shades",
        "accent": "#B57BFF",
        "line1": "INFORMANTE NO GOVERNO",
        "line2": "título: 'conselheiro'",
        "loops": ["marcha", "bracos", "cabeca", "levitate", "rise", "blink", "flicker"],
    },
    {
        "id": "p1_05",
        "pose": "point", "flip": False,
        "spot": "pinboard", "prop": "pins",
        "accent": "#D4AF37",
        "line1": "TEORIAS DA CONSPIRAÇÃO",
        "line2": "cada boato, uma semente",
        "loops": ["marcha", "bracos", "cabeca", "throb", "drop", "blink", "flicker"],
    },
    {
        "id": "p1_06",
        "pose": "dj", "flip": True,
        "spot": "spiral", "prop": "notes",
        "accent": "#B57BFF",
        "line1": "LAVAR CÉREBROS POP",
        "line2": "o hit vem com a mensagem",
        "loops": ["marcha", "bracos", "cabeca", "spin", "rise", "blink", "flicker"],
    },
    {
        "id": "p1_07",
        "pose": "peace", "flip": False,
        "spot": "warchart", "prop": "gears",
        "accent": "#B3261E",
        "line1": "GUERRA POR LUCRO",
        "line2": "paz é quando ninguém lucra",
        "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"],
    },
    {
        "id": "p1_08",
        "pose": "phone", "flip": True,
        "spot": "routerbox", "prop": "brainbits",
        "accent": "#39FF9C",
        "line1": "CONTROLAR PELO WI-FI",
        "line2": "sinal forte, convicção + forte",
        "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"],
    },
    {
        "id": "p1_09",
        "pose": "point", "flip": False,
        "spot": "puppet", "prop": "crowns",
        "accent": "#B57BFF",
        "line1": "GOVERNANTES FANTOCHES",
        "line2": "trocamos o roteiro, não o elenco",
        "loops": ["marcha", "bracos", "cabeca", "sway", "rise", "blink", "flicker"],
    },
    {
        "id": "p1_10",
        "pose": "armsup", "flip": False,
        "spot": "weather", "prop": "rain",
        "accent": "#39FF9C",
        "line1": "CONTROLAR O CLIMA",
        "line2": "chuva no bloco A, sol no B",
        "loops": ["marcha", "bracos", "cabeca", "throb", "rain", "blink", "flicker"],
    },
]

SPOT_FN = {
    "monitors": ak.spot_monitors,
    "telegraph": ak.spot_telegraph,
    "iguana": ak.spot_iguana,
    "envelope": ak.spot_envelope,
    "pinboard": ak.spot_pinboard,
    "spiral": ak.spot_spiral,
    "warchart": ak.spot_warchart,
    "routerbox": ak.spot_routerbox,
    "puppet": ak.spot_puppet,
    "weather": ak.spot_weather,
}
PROP_FN = {
    "brains": ak.prop_brains,
    "sheets": ak.prop_sheets,
    "eyeicons": ak.prop_eyeicons,
    "shades": ak.prop_shades,
    "pins": ak.prop_pins,
    "notes": ak.prop_notes,
    "gears": ak.prop_gears,
    "brainbits": ak.prop_brainbits,
    "crowns": ak.prop_crowns,
    "rain": ak.prop_rain,
}


def scene_svg(sc):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 88" preserveAspectRatio="xMidYMid slice" role="img" aria-label="%s">' % sc["line1"],
        '<defs>',
        '<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0" stop-color="#17422E"/>',
        '<stop offset="1" stop-color="#0B1F15"/>',
        '</linearGradient>',
        '</defs>',
        ak.stage(),
        ak.char(sc["pose"], flip=sc["flip"]),
        SPOT_FN[sc["spot"]](),
        PROP_FN[sc["prop"]](),
        ak.tag(sc["line1"], sc["line2"], sc["accent"]),
        '</svg>',
    ]
    return "\n".join(parts)


def build_spec():
    scenes = {}
    for sc in DEEP_WEB:
        pid = sc["id"]
        # cenas com desenho 2D real (loop.webp já montado) usam animação bitmap;
        # as demais permanecem na camada SVG procedural até o lote de arte chegar.
        animated = (Path(ASSETS / pid / "loop.webp").exists())
        scenes[pid] = {
            "label": sc["line1"],
            "accent": sc["accent"],
            "src": "assets/anim/%s/loop.webp" % pid if animated else "assets/anim/%s/scene.svg" % pid,
            "poster": "assets/anim/%s/poster.webp" % pid if animated else None,
            "animated": animated,
            "loops": sc["loops"],
        }
    return {
        "_comment": (
            "Especificação de animação das missões (docs/ANIMATION_PLAN.md). "
            "Renderizador: app.js (AnimStage). Cenas `animated:true` são desenhos 2D "
            "reais (loop.webp em estilo desenho animado); as demais mantêm o SVG "
            "procedural em camadas. Estados: off/idle/running."
        ),
        "version": 3,
        "stage": {"width": 320, "height": 88},
        "scenes": scenes,
    }


def main():
    spec = build_spec()
    (CONTENT / "animations.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for sc in DEEP_WEB:
        d = ASSETS / sc["id"]
        d.mkdir(parents=True, exist_ok=True)
        path = d / "scene.svg"
        path.write_text(scene_svg(sc), encoding="utf-8")
        print("  wrote %s (%d bytes)" % (path.relative_to(ROOT), path.stat().st_size))
    print("wrote %s com %d cenas" % (CONTENT / "animations.json", len(spec["scenes"])))


if __name__ == "__main__":
    main()

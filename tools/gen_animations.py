#!/usr/bin/env python3
"""
gen_animations.py — gera o conteúdo de ANIMAÇÃO das 40 missões (docs/ANIMATION_PLAN.md).

Spec v4 (4 mapas × 10 missões): cada missão tem cena, acento e loops declarados.
Arte em 3 regimes (o spec aponta o que existe em disco):
  - `animated:true`  → desenho 2D real (loop.webp + poster.webp), o renderizador
                       exibe o loop em idle/running e o poster em off;
  - `animated:false` → camada SVG procedural (dossiê conspiratório, art_kit) até o
                       lote de arte pintada chegar.

Cenas com 3 estados: off (sem posse), idle (produção manual) e running
(automatizado pelo Coordenador). Loops mantêm o vocabulário do apêndice em
`src/theme/app.css`: marcha, bracos, cabeca, throb, sway, levitate, spin, drop,
rise, rain, blink, flicker.

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
# Mapa 1 — Deep Web (p1_01..p1_10)
# --------------------------------------------------------------------------
DEEP_WEB = [
    {"id": "p1_01", "pose": "typing", "flip": False, "spot": "monitors", "prop": "brains",
     "accent": "#B57BFF", "line1": "COMPRAR COM CRIPTO", "line2": "carteira_real_v2_FINAL.docx",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p1_02", "pose": "poster", "flip": False, "spot": "telegraph", "prop": "sheets",
     "accent": "#39FF9C", "line1": "PLANTAR FAKE NEWS", "line2": "a manchete sai antes do fato",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p1_03", "pose": "pet", "flip": True, "spot": "iguana", "prop": "eyeicons",
     "accent": "#39FF9C", "line1": "AMIGOS REPTILIANOS", "line2": "café com um escamoso",
     "loops": ["marcha", "bracos", "cabeca", "sway", "rise", "blink", "flicker"]},
    {"id": "p1_04", "pose": "handoff", "flip": False, "spot": "envelope", "prop": "shades",
     "accent": "#B57BFF", "line1": "INFORMANTE NO GOVERNO", "line2": "título: 'conselheiro'",
     "loops": ["marcha", "bracos", "cabeca", "levitate", "rise", "blink", "flicker"]},
    {"id": "p1_05", "pose": "point", "flip": False, "spot": "pinboard", "prop": "pins",
     "accent": "#D4AF37", "line1": "TEORIAS DA CONSPIRAÇÃO", "line2": "cada boato, uma semente",
     "loops": ["marcha", "bracos", "cabeca", "throb", "drop", "blink", "flicker"]},
    {"id": "p1_06", "pose": "dj", "flip": True, "spot": "spiral", "prop": "notes",
     "accent": "#B57BFF", "line1": "LAVAR CÉREBROS POP", "line2": "o hit vem com a mensagem",
     "loops": ["marcha", "bracos", "cabeca", "spin", "rise", "blink", "flicker"]},
    {"id": "p1_07", "pose": "peace", "flip": False, "spot": "warchart", "prop": "gears",
     "accent": "#B3261E", "line1": "GUERRA POR LUCRO", "line2": "paz é quando ninguém lucra",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p1_08", "pose": "phone", "flip": True, "spot": "routerbox", "prop": "brainbits",
     "accent": "#39FF9C", "line1": "CONTROLAR PELO WI-FI", "line2": "sinal forte, convicção + forte",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p1_09", "pose": "point", "flip": False, "spot": "puppet", "prop": "crowns",
     "accent": "#B57BFF", "line1": "GOVERNANTES FANTOCHES", "line2": "trocamos o roteiro, não o elenco",
     "loops": ["marcha", "bracos", "cabeca", "sway", "rise", "blink", "flicker"]},
    {"id": "p1_10", "pose": "armsup", "flip": False, "spot": "weather", "prop": "rain",
     "accent": "#39FF9C", "line1": "CONTROLAR O CLIMA", "line2": "chuva no bloco A, sol no B",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rain", "blink", "flicker"]},
]

# --------------------------------------------------------------------------
# Mapa 2 — Democracia Relativa (p2_01..p2_10)
# --------------------------------------------------------------------------
DEMOCRACIA = [
    {"id": "p2_01", "pose": "handoff", "flip": False, "spot": "envelope", "prop": "pins",
     "accent": "#D4AF37", "line1": "COMPRAR VOTO DO TIO", "line2": "santinho vale mais que discurso",
     "loops": ["marcha", "bracos", "cabeca", "drop", "rise", "blink", "flicker"]},
    {"id": "p2_02", "pose": "phone", "flip": True, "spot": "monitors", "prop": "sheets",
     "accent": "#4DC3FF", "line1": "PESQUISA QUE PROVA", "line2": "99% de aprovação (margem: a nossa)",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p2_03", "pose": "armsup", "flip": False, "spot": "telegraph", "prop": "sheets",
     "accent": "#39FF9C", "line1": "PARTIDO DO MEIO-TERMO", "line2": "em cima do muro, no meio do caminho",
     "loops": ["marcha", "bracos", "cabeca", "sway", "rise", "blink", "flicker"]},
    {"id": "p2_04", "pose": "typing", "flip": False, "spot": "telegraph", "prop": "sheets",
     "accent": "#D4AF37", "line1": "EMENDA TOTALMENTE PÚBLICA", "line2": "publicidade: 1 linha, miudinha",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p2_05", "pose": "typing", "flip": False, "spot": "monitors", "prop": "gears",
     "accent": "#4DC3FF", "line1": "PLENÁRIA COM ROBÔS", "line2": "votação unânime (0% de oposição)",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p2_06", "pose": "dj", "flip": True, "spot": "spiral", "prop": "notes",
     "accent": "#B3261E", "line1": "CABO COM MEGAFONE", "line2": "a verdade sai em volume alto",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p2_07", "pose": "dj", "flip": False, "spot": "weather", "prop": "rain",
     "accent": "#FF9F45", "line1": "COMÍCIO EM DUPLA", "line2": "um promete, o outro confirma",
     "loops": ["marcha", "bracos", "cabeca", "spin", "rise", "blink", "flicker"]},
    {"id": "p2_08", "pose": "phone", "flip": True, "spot": "routerbox", "prop": "brainbits",
     "accent": "#39FF9C", "line1": "CONSTITUIÇÃO DO ZAP", "line2": "artigo 1º: encaminhando…",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p2_09", "pose": "handoff", "flip": False, "spot": "envelope", "prop": "shades",
     "accent": "#B57BFF", "line1": "SÓSIA POR PROCURAÇÃO", "line2": "ele votou. (o outro 'ele')",
     "loops": ["marcha", "bracos", "cabeca", "levitate", "rise", "blink", "flicker"]},
    {"id": "p2_10", "pose": "armsup", "flip": False, "spot": "pinboard", "prop": "crowns",
     "accent": "#D4AF37", "line1": "PROCLAMAR DEMOCRACIA™", "line2": "50% + 1 ideia",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
]

# --------------------------------------------------------------------------
# Mapa 3 — Pindorama (p3_01..p3_10) — conspiração 100% brasileira
# --------------------------------------------------------------------------
RATANABA = [
    {"id": "p3_01", "pose": "typing", "flip": False, "spot": "warchart", "prop": "gears",
     "accent": "#FF9F45", "line1": "ESCAVAR A CIDADE SECRETA", "line2": "a broca parou onde o GPS também",
     "loops": ["marcha", "bracos", "cabeca", "throb", "drop", "blink", "flicker"]},
    {"id": "p3_02", "pose": "pet", "flip": True, "spot": "iguana", "prop": "eyeicons",
     "accent": "#4DC3FF", "line1": "O E.T. DE VARGINHA", "line2": "a permuta é justa. (ele paga em mistério)",
     "loops": ["marcha", "bracos", "cabeca", "levitate", "rise", "blink", "flicker"]},
    {"id": "p3_03", "pose": "typing", "flip": False, "spot": "telegraph", "prop": "sheets",
     "accent": "#D4AF37", "line1": "INDÚSTRIA DA MULTA", "line2": "o radar torto é o caixa",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p3_04", "pose": "point", "flip": False, "spot": "iguana", "prop": "eyeicons",
     "accent": "#B3261E", "line1": "O CHUPA-CABRA", "line2": "capturado por encomenda",
     "loops": ["marcha", "bracos", "cabeca", "sway", "drop", "blink", "flicker"]},
    {"id": "p3_05", "pose": "typing", "flip": False, "spot": "monitors", "prop": "brains",
     "accent": "#39FF9C", "line1": "CARRO ELÉTRICO NACIONAL", "line2": "alcance: até a esquina",
     "loops": ["marcha", "bracos", "cabeca", "spin", "rise", "blink", "flicker"]},
    {"id": "p3_06", "pose": "point", "flip": False, "spot": "warchart", "prop": "pins",
     "accent": "#D4AF37", "line1": "O TÚNEL SUBTERRÂNEO", "line2": "7 mil km, prazo: 3 mil anos",
     "loops": ["marcha", "bracos", "cabeca", "throb", "drop", "blink", "flicker"]},
    {"id": "p3_07", "pose": "phone", "flip": True, "spot": "routerbox", "prop": "brainbits",
     "accent": "#4DC3FF", "line1": "CELULARES MONITORES", "line2": "cada passo, um dado",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p3_08", "pose": "handoff", "flip": False, "spot": "envelope", "prop": "shades",
     "accent": "#B57BFF", "line1": "CHIPS NOS DOCUMENTOS", "line2": "a folha lembra tudo",
     "loops": ["marcha", "bracos", "cabeca", "levitate", "rise", "blink", "flicker"]},
    {"id": "p3_09", "pose": "typing", "flip": False, "spot": "monitors", "prop": "sheets",
     "accent": "#39FF9C", "line1": "DINHEIRO INSTANTÂNEO", "line2": "chega na hora certa (a nossa)",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p3_10", "pose": "armsup", "flip": False, "spot": "monitors", "prop": "brains",
     "accent": "#D4AF37", "line1": "MOEDA MAGNÉTICA", "line2": "saiu da máquina, já voltou",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
]

# --------------------------------------------------------------------------
# Mapa 4 — Religião (p4_01..p4_10) — a engenharia da fé
# --------------------------------------------------------------------------
RELIGIAO = [
    {"id": "p4_01", "pose": "dj", "flip": True, "spot": "spiral", "prop": "notes",
     "accent": "#B57BFF", "line1": "VINIL INVERTIDO", "line2": "no replay, a música manda votar",
     "loops": ["marcha", "bracos", "cabeca", "spin", "rise", "blink", "flicker"]},
    {"id": "p4_02", "pose": "typing", "flip": False, "spot": "monitors", "prop": "notes",
     "accent": "#4DC3FF", "line1": "DESENHO DA INDUÇÃO", "line2": "a cada 4 episódios, um símbolo",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p4_03", "pose": "pet", "flip": False, "spot": "iguana", "prop": "brainbits",
     "accent": "#B3261E", "line1": "BRINQUEDOS POSSUÍDOS", "line2": "o mal, em linha de produção",
     "loops": ["marcha", "bracos", "cabeca", "sway", "rise", "blink", "flicker"]},
    {"id": "p4_04", "pose": "point", "flip": False, "spot": "warchart", "prop": "pins",
     "accent": "#39FF9C", "line1": "CIDADE OCULTISTA", "line2": "de cima, um avião; de dentro, fé",
     "loops": ["marcha", "bracos", "cabeca", "sway", "rise", "blink", "flicker"]},
    {"id": "p4_05", "pose": "dj", "flip": False, "spot": "telegraph", "prop": "notes",
     "accent": "#D4AF37", "line1": "MILAGRE NA TV", "line2": "luz certa, lágrima certa",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p4_06", "pose": "pet", "flip": True, "spot": "iguana", "prop": "brainbits",
     "accent": "#D4AF37", "line1": "A IMAGEM QUE CHORA", "line2": "choro de 5 em 5",
     "loops": ["marcha", "bracos", "cabeca", "sway", "drop", "blink", "flicker"]},
    {"id": "p4_07", "pose": "phone", "flip": True, "spot": "monitors", "prop": "brainbits",
     "accent": "#B57BFF", "line1": "O 13º MANDAMENTO", "line2": "estava no áudio de 11 minutos",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p4_08", "pose": "phone", "flip": True, "spot": "weather", "prop": "rain",
     "accent": "#4DC3FF", "line1": "ÁGUA ABENÇOADA", "line2": "saída da torneira: 2014",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rain", "blink", "flicker"]},
    {"id": "p4_09", "pose": "point", "flip": False, "spot": "pinboard", "prop": "pins",
     "accent": "#FF9F45", "line1": "APOCALIPSE ADIADO", "line2": "nova data: em breve",
     "loops": ["marcha", "bracos", "cabeca", "sway", "drop", "blink", "flicker"]},
    {"id": "p4_10", "pose": "armsup", "flip": False, "spot": "weather", "prop": "rain",
     "accent": "#4DC3FF", "line1": "ARREBATAMENTO HOLOGRÁFICO", "line2": "céu de LED, nuvem de verdade",
     "loops": ["marcha", "bracos", "cabeca", "levitate", "rise", "blink", "flicker"]},
]

# --------------------------------------------------------------------------
# Mapa 5 — Singularidade (p5_01..p5_10) — conspirações de tecnologia
# --------------------------------------------------------------------------
SINGULARIDADE = [
    {"id": "p5_01", "pose": "phone", "flip": True, "spot": "routerbox", "prop": "brainbits",
     "accent": "#39FF9C", "line1": "O FEIXE DO CERRADO", "line2": "o céu faz o clima",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p5_02", "pose": "phone", "flip": True, "spot": "weather", "prop": "rain",
     "accent": "#4DC3FF", "line1": "A FÓRMULA DA ÁGUA", "line2": "cada gota, uma dose",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rain", "blink", "flicker"]},
    {"id": "p5_03", "pose": "typing", "flip": False, "spot": "monitors", "prop": "gears",
     "accent": "#B3261E", "line1": "O APAGÃO CIBERNÉTICO", "line2": "ensaio geral às 22h",
     "loops": ["marcha", "bracos", "cabeca", "throb", "flicker", "blink", "drop"]},
    {"id": "p5_04", "pose": "typing", "flip": False, "spot": "monitors", "prop": "gears",
     "accent": "#B57BFF", "line1": "SKYNET", "line2": "ela decide, a gente confirma",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p5_05", "pose": "phone", "flip": True, "spot": "routerbox", "prop": "brainbits",
     "accent": "#4DC3FF", "line1": "APARELHOS ESPIONANDO", "line2": "o anúncio chegou antes do café",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p5_06", "pose": "handoff", "flip": False, "spot": "puppet", "prop": "crowns",
     "accent": "#B3261E", "line1": "PRESIDENTE 2.0", "line2": "mesmo sorriso, melhor bateria",
     "loops": ["marcha", "bracos", "cabeca", "levitate", "rise", "blink", "flicker"]},
    {"id": "p5_07", "pose": "point", "flip": False, "spot": "weather", "prop": "eyeicons",
     "accent": "#39FF9C", "line1": "POMBOS DRONES", "line2": "nove em linha? coincidência",
     "loops": ["marcha", "bracos", "cabeca", "sway", "rise", "blink", "flicker"]},
    {"id": "p5_08", "pose": "phone", "flip": True, "spot": "routerbox", "prop": "brainbits",
     "accent": "#FF9F45", "line1": "TORRES DE 5G", "line2": "a torrinha explica tudo",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p5_09", "pose": "typing", "flip": False, "spot": "telegraph", "prop": "sheets",
     "accent": "#39FF9C", "line1": "QR NO PRATO", "line2": "escaneie, coma, pense",
     "loops": ["marcha", "bracos", "cabeca", "throb", "rise", "blink", "flicker"]},
    {"id": "p5_10", "pose": "handoff", "flip": False, "spot": "envelope", "prop": "brains",
     "accent": "#B57BFF", "line1": "O CHIP", "line2": "um ponto na nuca e a sincronia",
     "loops": ["marcha", "bracos", "cabeca", "levitate", "rise", "blink", "flicker"]},
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

MAPS = [DEEP_WEB, DEMOCRACIA, RATANABA, RELIGIAO, SINGULARIDADE]


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
    for table in MAPS:
        for sc in table:
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
            "Especificação de animação das 40 missões (docs/ANIMATION_PLAN.md, spec v4). "
            "Renderizador: app.js (AnimStage). Cenas `animated:true` são desenhos 2D reais "
            "(loop.webp em estilo flat-toon; 8 com mestre pintado + motion composto e "
            "11 com keyframes desenhados em código — tools/scene_draw.py); as demais mantêm "
            "o SVG procedural em camadas. Estados: off/idle/running."
        ),
        "version": 4,
        "stage": {"width": 320, "height": 88},
        "scenes": scenes,
    }


def main():
    spec = build_spec()
    (CONTENT / "animations.json").write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for table in MAPS:
        for sc in table:
            d = ASSETS / sc["id"]
            d.mkdir(parents=True, exist_ok=True)
            path = d / "scene.svg"
            path.write_text(scene_svg(sc), encoding="utf-8")
            print("  wrote %s (%d bytes)" % (path.relative_to(ROOT), path.stat().st_size))
    n_anim = sum(1 for s in spec["scenes"].values() if s["animated"])
    print("wrote %s com %d cenas (%d animadas em 2D)" % (
        CONTENT / "animations.json", len(spec["scenes"]), n_anim))


if __name__ == "__main__":
    main()

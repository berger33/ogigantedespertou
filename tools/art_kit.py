#!/usr/bin/env python3
"""
art_kit.py — kit procedural de ARTE ORIGINAL (sem assets externos).

Paleta e formas seguem o ART_BIBLE.md. Gera fragmentos SVG reutilizaveis:
  - cenario da "sala secreta" (holofote, janela com olho, quadro de cordas)
  - o personagem "O Grifter" em varias poses (chapeu de aluminio)
  - objetos de cena (spot) por missao
  - particulas/efeitos (prop) por missao
  - plaqueta com texto (a piada da missao)

Cada elemento usa CLASSES (nao ids) para o renderizador animar por estado
(`off/idle/running`) sem colisao entre cards.
"""
from textwrap import dedent

# --------------------------------------------------------------------------
# Paleta oficial — ART_BIBLE.md §2
# --------------------------------------------------------------------------
P = {
    "deep": "#0B1F15", "deep2": "#072718", "wall": "#12301F",
    "ink": "#16130F", "paper": "#F2E9D0", "paper2": "#EFE3C3",
    "skin": "#E9C9A0",
    "green": "#39FF9C", "green_mid": "#24B26B", "green_dk": "#145132",
    "gold": "#D4AF37", "violet": "#B57BFF", "stamp": "#B3261E",
    "muted": "#9AAEA2", "alu": "#CDD6D3",
    "hood": "#1E3A2A", "hood_dk": "#14301F",
    "glass": "#0E3A22",
}

STAGE = {"w": 320, "h": 88}
GROUND = 78


def _sc(x):
    return "%g" % x


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def sparks(n=10, seed=7):
    out = ['<g class="dust" fill="%s">' % P["green"]]
    a = 1103515245 + seed
    for i in range(n):
        a = (a * 6364136223846793005 + 1442695040888963407) % (2 ** 64)
        r1 = ((a >> 33) % 1000) / 1000.0
        a = (a * 6364136223846793005 + 1442695040888963407) % (2 ** 64)
        r2 = ((a >> 33) % 1000) / 1000.0
        x = 4 + r1 * 312
        y = 6 + r2 * 70
        r = 0.7 + ((a >> 20) % 10) / 10.0
        out.append('<circle cx="%s" cy="%s" r="%s" opacity=".55"/>' % (_sc(x), _sc(y), _sc(r)))
    out.append('</g>')
    return "\n".join(out)


def beam():
    return ('<g class="beam" opacity=".14">'
            '<polygon points="14,10 8,44 96,44" fill="%s"/>'
            '</g>' % P["green"])


def window_eye():
    return dedent('''\
    <g class="eye">
      <rect x="256" y="8" width="52" height="32" rx="4" fill="{deep2}" stroke="{ink}" stroke-width="2"/>
      <path d="M258 10 h48 M258 38 h48" stroke="{ink}" stroke-width="1.4" opacity=".7"/>
      <ellipse cx="282" cy="24" rx="13" ry="6" fill="{paper}"/>
      <circle cx="282" cy="24" r="4.2" fill="{green}"/>
      <circle cx="282" cy="24" r="1.7" fill="{ink}"/>
      <path d="M270 21 q12 -4 24 0" fill="none" stroke="{ink}" stroke-width="1.5"/>
    </g>''').format(**P)


def strings_board():
    return dedent('''\
    <g class="board" opacity=".5">
      <path d="M30 20 L96 26 M30 20 L118 40 M96 26 L118 40 M52 8 L30 20" stroke="{paper}" stroke-width=".8" opacity=".5"/>
      <rect x="92" y="22" width="12" height="10" fill="{paper}" transform="rotate(6 98 27)"/>
      <rect x="114" y="36" width="12" height="10" fill="{paper}" transform="rotate(-8 120 41)"/>
      <rect x="26" y="16" width="12" height="10" fill="{paper}" transform="rotate(4 32 21)"/>
      <circle cx="30" cy="20" r="1.6" fill="{stamp}"/>
      <circle cx="96" cy="26" r="1.6" fill="{stamp}"/>
      <circle cx="118" cy="40" r="1.6" fill="{stamp}"/>
    </g>''').format(**P)


def desk():
    return dedent('''\
    <g class="desk">
      <rect x="150" y="32" width="4" height="46" fill="{ink}"/>
      <rect x="290" y="32" width="4" height="46" fill="{ink}"/>
      <rect x="146" y="52" width="152" height="6" rx="2" fill="{hood}"/>
      <rect x="146" y="58" width="152" height="4" fill="{hood_dk}"/>
    </g>''').format(**P)


def stage():
    return dedent('''\
    <rect width="{w}" height="{h}" fill="url(#wall)"/>
    <rect y="0" width="320" height="44" fill="{wall}" opacity=".35"/>
    <path d="M0 78 L40 56 L80 78 Z" fill="{deep}"/>
    <rect y="78" width="320" height="10" fill="{deep}"/>
    {board}
    {eye}
    {beam}
    <g class="spotlight" opacity=".10">
      <polygon points="250,4 182,66 272,66" fill="{green}"/>
    </g>
    <g class="lamp">
      <path d="M12 12 l8 16 h-6 z" fill="{gold}" opacity=".85"/>
      <rect x="11.4" y="10.5" width="8" height="2.4" fill="{ink}"/>
      <ellipse cx="14" cy="31" rx="4" ry="2.6" fill="{green}" opacity=".8"/>
    </g>
    {dust}''').format(w=STAGE["w"], h=STAGE["h"], wall=P["wall"], deep=P["deep"],
                      gold=P["gold"], ink=P["ink"], green=P["green"],
                      board=strings_board(), eye=window_eye(), beam=beam(),
                      dust=sparks())


# --------------------------------------------------------------------------
# PERSONAGEM — O Grifter (chapeu de aluminio) em poses
# --------------------------------------------------------------------------

def _hat(cx, cy):
    return dedent('''\
      <polygon points="{a},{b} {c},{d} {e},{f}" fill="{alu}" stroke="{ink}" stroke-width="1.4"/>
      <ellipse cx="{cx}" cy="{g}" rx="8.4" ry="3" fill="{alu}" stroke="{ink}" stroke-width="1.4"/>''').format(
        a=cx - 7, b=cy - 3, c=cx, d=cy - 13, e=cx + 7, f=cy - 3, g=cy - 3,
        alu=P["alu"], ink=P["ink"], cx=cx)


def _head(cx, cy, look="r"):
    ex = cx + 2.6 if look == "r" else cx - 2.6
    eyes = ('<circle cx="%s" cy="%s" r="1.15" fill="{ink}"/>'
            '<circle cx="%s" cy="%s" r=".4" fill="{paper}"/>') % (_sc(ex), _sc(cy), _sc(ex), _sc(cy))
    return dedent('''\
      <path d="M{a} {b} q0 -16 8 -16 l8 0 q8 0 8 16 z" fill="{hood}"/>
      <rect x="{c}" y="{d}" width="18" height="7" fill="{skin}"/>
      {eyes}
      <rect x="{c}" y="{e}" width="18" height="4" fill="{hood}"/>
      {hat}''').format(a=cx - 8, b=cy + 2, c=cx - 9, d=cy - 1, e=cy + 6,
                       hood=P["hood"], skin=P["skin"], eyes=eyes, hat=_hat(cx, cy - 5))


def _torso_svg(x, y, w=16, h=20):
    return ('<rect x="%s" y="%s" width="%s" height="%s" rx="5" fill="%s" stroke="%s" stroke-width="1.6"/>'
            '<path d="M%s %s l%s 0 M%s %s l%s 0 M%s %s l%s 0" stroke="%s" stroke-width=".7" opacity=".35"/>') % (
        _sc(x), _sc(y), w, h, P["paper2"], P["ink"],
        _sc(x + 3), _sc(y + 2), w - 6, _sc(x + 3), _sc(y + 7), w - 6, _sc(x + 3), _sc(y + 12), w - 6, P["ink"])


def _legs(x, y):
    return ('<rect x="%s" y="%s" width="5.4" height="13" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>'
            '<rect x="%s" y="%s" width="5.4" height="13" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>') % (
        _sc(x + 1.5), _sc(y), P["hood_dk"], P["ink"], _sc(x + 9), _sc(y), P["hood_dk"], P["ink"])


def _arm(x1, y1, x2, y2):
    return ('<path d="M%s %s Q%s %s %s %s" fill="none" stroke="%s" stroke-width="4" stroke-linecap="round"/>') % (
        _sc(x1), _sc(y1), _sc((x1 + x2) / 2), _sc(min(y1, y2) - 2), _sc(x2), _sc(y2), P["paper2"])


def char(pose, x=44, y=GROUND, flip=False):
    """Personagem completo. Base no ponto (x, y) [pes]. Altura ~48px."""
    hx = x + 8
    hy = y - 34
    ty = y - 24
    torso = _torso_svg(x + 0.5, ty, 16, 20)

    if pose == "typing":
        arms = (_arm(x + 2, ty + 5, x + 26, ty + 8)
                + '<rect x="%s" y="%s" width="22" height="6" rx="1.5" fill="%s" stroke="%s" stroke-width="1.1"/>' % (_sc(x + 26), _sc(ty + 5), P["hood"], P["ink"]))
    elif pose == "poster":
        arms = (_arm(x + 2, ty + 6, x + 30, ty - 4)
                + '<rect x="%s" y="%s" width="14" height="14" fill="%s" stroke="%s" stroke-width="1.2" transform="rotate(-6 %s %s)"/>' % (_sc(x + 24), _sc(ty - 16), P["paper"], P["ink"], _sc(x + 31), _sc(ty - 9)))
    elif pose == "pet":
        arms = (_arm(x + 2, ty + 7, x + 22, ty + 16) + _arm(x + 14, ty + 7, x + 28, ty + 13))
    elif pose == "handoff":
        arms = (_arm(x + 2, ty + 7, x + 30, ty + 3)
                + '<rect x="%s" y="%s" width="13" height="9" rx="1.5" fill="%s" stroke="%s" stroke-width="1.1"/>' % (_sc(x + 30), _sc(ty - 3), P["gold"], P["ink"]))
    elif pose == "point":
        arms = (_arm(x + 2, ty + 9, x + 6, ty + 16) + _arm(x + 14, ty + 5, x + 30, ty - 10))
    elif pose == "dj":
        arms = (_arm(x + 2, ty + 8, x - 6, ty + 18) + _arm(x + 14, ty + 8, x + 32, ty + 14)
                + '<path d="M%s %s q8 -8 16 0" fill="none" stroke="%s" stroke-width="2"/>' % (_sc(hx - 8), _sc(hy - 8), P["ink"]))
    elif pose == "phone":
        arms = (_arm(x + 2, ty + 9, x + 4, ty + 17) + _arm(x + 14, ty + 4, x + 20, ty - 8)
                + '<rect x="%s" y="%s" width="7" height="12" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>' % (_sc(x + 20), _sc(ty - 14), P["alu"], P["ink"]))
    elif pose == "router":
        arms = (_arm(x + 2, ty + 7, x + 26, ty + 13) + _arm(x + 14, ty + 7, x + 34, ty + 14))
    elif pose == "peace":
        arms = (_arm(x + 2, ty + 10, x + 12, ty + 17) + _arm(x + 14, ty + 4, x + 28, ty - 12)
                + '<path d="M%s %s V%s M%s %s V%s" stroke="%s" stroke-width="2" stroke-linecap="round"/>' % (_sc(x + 28), _sc(ty - 12), _sc(ty - 20), _sc(x + 32), _sc(ty - 12), _sc(ty - 20), P["ink"]))
    else:  # armsup
        arms = '<path d="M%s %s V%s M%s %s V%s" stroke="%s" stroke-width="4" stroke-linecap="round"/>' % (
            _sc(x + 2), _sc(ty + 9), _sc(ty - 8), _sc(x + 14), _sc(ty + 9), _sc(ty - 12), P["skin"])

    if flip:
        return '<g class="char" transform="translate(%s 0) scale(-1 1)">%s%s%s%s</g>' % (
            _sc(2 * x + 16), _legs(x, y - 13), torso, arms, _head(hx, hy))
    return '<g class="char">%s%s%s%s</g>' % (_legs(x, y - 13), torso, arms, _head(hx, hy))


# --------------------------------------------------------------------------
# OBJETOS DE CENA (spot) — um por missao, sob o holofote
# --------------------------------------------------------------------------

def spot(loop, inner):
    return ('<g class="spot spot-%s" transform="translate(20 16)">'
            '<ellipse cx="198" cy="52" rx="46" ry="3.6" fill="%s" opacity=".5"/>'
            '%s</g>' % (loop, P["deep"], inner))


def spot_monitors():
    return spot("throb", dedent('''\
      <rect x="176" y="38" width="40" height="14" fill="{ink}" stroke="{green}" stroke-width="1.2"/>
      <rect x="180" y="40" width="32" height="10" fill="{glass}"/>
      <path d="M182 47 l5 -4 6 4 6 -5 7 3 5 -3" fill="none" stroke="{green}" stroke-width="1.6"/>
      <rect x="168" y="52" width="56" height="4" fill="{ink}"/>''').format(**P))


def spot_telegraph():
    return spot("throb", dedent('''\
      <rect x="172" y="34" width="52" height="14" rx="3" fill="{ink}"/>
      <rect x="176" y="38" width="20" height="6" fill="{gold}" opacity=".85"/>
      <circle cx="184" cy="41" r="1.6" fill="{stamp}"/>
      <circle cx="204" cy="45" r="1.4" fill="{green}"/>
      <circle cx="192" cy="45" r="1.4" fill="{green}"/>
      <path d="M206 44 l10 0" stroke="{green}" stroke-width="1.6"/>
      <rect x="168" y="48" width="60" height="5" fill="{ink}"/>''').format(**P))


def spot_iguana():
    body = dedent('''\
      <ellipse cx="200" cy="44" rx="20" ry="6.5" fill="{green_dk}"/>
      <circle cx="222" cy="42" r="6" fill="{green_mid}"/>
      <rect x="222" y="36" width="8" height="3" rx="1.5" fill="{green_dk}"/>
      <circle cx="226" cy="40" r="1.4" fill="{gold}"/>
      <path d="M196 38 l-6 -3 M196 44 l-7 2 M197 49 l-5 4" stroke="{green_dk}" stroke-width="2" stroke-linecap="round"/>
      <path d="M186 30 q4 -8 10 -8 q8 0 6 8" fill="{green_mid}"/>
      <path d="M186 30 q4 -8 10 -8 q8 0 6 8 M188 28 q2 -4 6 -4 M194 27 l3 -2" stroke="{ink}" stroke-width="1.2" fill="none"/>''').format(**P)
    return spot("sway", body)


def spot_envelope():
    return spot("levitate", dedent('''\
      <rect x="186" y="30" width="30" height="20" rx="2" fill="{paper}" stroke="{ink}" stroke-width="1.6"/>
      <path d="M187 31 l14 12 l14 -12 M187 48 l11 -8 M216 48 l-11 -8" fill="none" stroke="{ink}" stroke-width="1.2"/>
      <circle cx="201" cy="45" r="3.4" fill="{stamp}"/>''').format(**P))


def spot_pinboard():
    return spot("throb", dedent('''\
      <rect x="166" y="16" width="64" height="40" rx="2" fill="{hood}" stroke="{ink}" stroke-width="1.6"/>
      <path d="M174 44 L190 30 M182 48 L196 32 M196 48 L206 26" stroke="{paper}" stroke-width=".9" opacity=".8"/>
      <rect x="174" y="26" width="14" height="11" fill="{paper}" transform="rotate(-5 181 31)"/>
      <rect x="196" y="28" width="14" height="11" fill="{paper2}" transform="rotate(6 203 33)"/>
      <circle cx="180" cy="44" r="1.7" fill="{stamp}"/>
      <circle cx="190" cy="30" r="1.7" fill="{stamp}"/>
      <circle cx="210" cy="22" r="1.7" fill="{stamp}"/>''').format(**P))


def spot_spiral():
    return spot("spin", dedent('''\
      <rect x="172" y="28" width="48" height="24" rx="3" fill="{ink}" stroke="{gold}" stroke-width="1.4"/>
      <rect x="176" y="32" width="40" height="16" fill="{glass}"/>
      <g stroke="{violet}" stroke-width="1.6" fill="none">
        <path d="M196 40 m0 -6 a6 6 0 1 1 -6 6"/>
        <path d="M196 40 m0 -3 a3 3 0 1 1 -3 3"/>
        <path d="M196 40 l2 -2"/>
      </g>''').format(**P))


def spot_warchart():
    return spot("throb", dedent('''\
      <rect x="170" y="26" width="60" height="26" rx="2" fill="{ink}" stroke="{green}" stroke-width="1.3"/>
      <path d="M176 46 L196 40 l12 4 l12 -8 l8 6" fill="none" stroke="{green}" stroke-width="1.8"/>
      <circle cx="196" cy="40" r="2.2" fill="{gold}"/>
      <rect x="176" y="30" width="9" height="6" rx="1.2" fill="{stamp}" opacity=".85"/>
      <circle cx="224" cy="38" r="3" fill="{gold}" opacity=".9"/>''').format(**P))


def spot_routerbox():
    return spot("throb", dedent('''\
      <rect x="178" y="36" width="36" height="14" rx="4" fill="{hood}" stroke="{ink}" stroke-width="1.6"/>
      <rect x="188" y="24" width="4" height="12" fill="{ink}"/>
      <rect x="200" y="22" width="4" height="14" fill="{ink}"/>
      <circle cx="186" cy="43" r="1.6" fill="{green}"/>
      <circle cx="196" cy="43" r="1.6" fill="{gold}"/>
      <circle cx="206" cy="43" r="1.6" fill="{stamp}"/>
      <path d="M176 40 q-6 0 -6 -5 M216 40 q6 0 6 -5" stroke="{green}" stroke-width="1.4" fill="none" opacity=".8"/>''').format(**P))


def spot_puppet():
    return spot("sway", dedent('''\
      <path d="M200 18 l0 10" stroke="{paper}" stroke-width="1.2"/>
      <path d="M196 20 l8 0" stroke="{ink}" stroke-width="2"/>
      <circle cx="200" cy="30" r="5" fill="{skin}"/>
      <path d="M200 48 v-13 l6 -0 8 13 z" fill="{paper2}" stroke="{ink}" stroke-width="1.4"/>
      <path d="M196 38 l2 0 1 8 M204 38 l-1 0 M202 46 l5 1" stroke="{skin}" stroke-width="3" stroke-linecap="round" fill="none"/>
      <rect x="193" y="26" width="14" height="3.4" fill="{ink}" opacity=".85"/>''').format(**P))


def spot_weather():
    return spot("throb", dedent('''\
      <rect x="168" y="34" width="60" height="18" rx="3" fill="{ink}" stroke="{gold}" stroke-width="1.3"/>
      <rect x="172" y="38" width="18" height="5" rx="1.5" fill="{green_mid}" opacity=".8"/>
      <rect x="206" y="38" width="18" height="5" rx="1.5" fill="{violet}" opacity=".8"/>
      <circle cx="181" cy="46" r="3" fill="{gold}"/>
      <rect x="214" y="30" width="3" height="5" fill="{ink}"/>
      <path d="M214 30 q3 -3 6 -1 M214 30 q-2 -3 -5 -2" stroke="{green}" stroke-width="1.3" fill="none"/>''').format(**P))


# --------------------------------------------------------------------------
# PARTICULAS (prop) — efeitos flutuantes por missao
# --------------------------------------------------------------------------

def prop(loop, inner):
    return '<g class="prop prop-%s">%s</g>' % (loop, inner)


def prop_brains():
    return prop("rise", dedent('''\
      <g fill="{deep}" stroke="{green}" stroke-width="1.2">
        <path d="M236 24 q-2 -4 -8 -3 q-3 1 -2 4 q3 1 6 2 q2 2 4 -3 z"/><circle cx="233" cy="21" r="1" fill="{green}"/>
        <path d="M262 33 q-2 -4 -7 -3 q-3 2 -2 5 q3 0 5 1 q2 2 4 -2 z"/><circle cx="259" cy="30" r="1" fill="{green}"/>
        <path d="M248 14 q-1 -4 -7 -3 q-3 1 -1 4 q3 1 5 1 q2 2 3 -2 z"/><circle cx="245" cy="12" r="1" fill="{gold}"/>
      </g>''').format(**P))


def prop_sheets():
    return prop("rise", dedent('''\
      <g fill="{paper}" stroke="{ink}" stroke-width="1">
        <rect x="236" y="30" width="11" height="14" transform="rotate(-8 241 37)"/>
        <rect x="256" y="20" width="11" height="14" transform="rotate(10 261 27)"/>
        <rect x="248" y="40" width="9" height="12" transform="rotate(-14 252 46)"/>
      </g>''').format(**P))


def prop_eyeicons():
    return prop("rise", dedent('''\
      <g>
        <circle cx="240" cy="30" r="3.4" fill="{paper}"/><circle cx="240" cy="30" r="1.4" fill="{green}"/>
        <circle cx="258" cy="22" r="2.8" fill="{paper}"/><circle cx="258" cy="22" r="1.1" fill="{green}"/>
        <circle cx="252" cy="42" r="3" fill="{paper}"/><circle cx="252" cy="42" r="1.2" fill="{violet}"/>
      </g>''').format(**P))


def prop_shades():
    return prop("rise", dedent('''\
      <g fill="{alu}" stroke="{ink}" stroke-width="1.2">
        <rect x="238" y="26" width="13" height="8" rx="2"/>
        <rect x="238" y="26" width="13" height="3.4" fill="{ink}" stroke="none"/>
        <rect x="258" y="16" width="11" height="7" rx="2"/>
        <rect x="258" y="16" width="11" height="3" fill="{ink}" stroke="none"/>
      </g>''').format(**P))


def prop_pins():
    return prop("drop", dedent('''\
      <g>
        <circle cx="236" cy="20" r="3" fill="{stamp}"/><path d="M236 23 v7" stroke="{ink}" stroke-width="1.2"/>
        <circle cx="252" cy="28" r="3" fill="{stamp}"/><path d="M252 31 v7" stroke="{ink}" stroke-width="1.2"/>
        <circle cx="244" cy="12" r="2.6" fill="{gold}"/><path d="M244 15 v6" stroke="{ink}" stroke-width="1.2"/>
      </g>''').format(**P))


def prop_notes():
    return prop("rise", dedent('''\
      <g fill="none" stroke="{violet}" stroke-width="1.4">
        <path d="M240 32 q0 -9 9 -9 q9 0 9 9 l0 8 l-9 0 z"/><path d="M249 24 v16"/>
        <path d="M258 20 q0 -7 7 -7 q7 0 7 7 l0 6 l-7 0 z"/><path d="M265 14 v13"/>
      </g>''').format(**P))


def prop_gears():
    return prop("rise", dedent('''\
      <g stroke="{gold}" stroke-width="1.6" fill="none">
        <circle cx="238" cy="30" r="5.5"/><path d="M238 22 v-3 M244 25 l2 -2.4 M245 31 l3.4 0 M244 37 l2 2.4 M238 39 v3 M232 37 l-2 2.4 M231 30 l-3.4 0"/>
        <circle cx="258" cy="20" r="4"/><path d="M258 13.6 v-2 M262 16.8 l1.6 -1.8 M262.6 21 l2.6 0"/>
      </g>''').format(**P))


def prop_brainbits():
    return prop("rise", dedent('''\
      <g fill="{deep}" stroke="{violet}" stroke-width="1.1">
        <path d="M240 36 q-1 -4 -7 -3 q-3 1 -1 4 q3 0 5 1 q2 2 3 -2 z"/><circle cx="237" cy="33" r="1" fill="{violet}"/>
        <path d="M258 24 q-1 -3 -6 -2 q-3 1 -1 4 q3 0 4 1 q2 1 3 -3 z"/><circle cx="255" cy="22" r="1" fill="{gold}"/>
      </g>''').format(**P))


def prop_crowns():
    return prop("rise", dedent('''\
      <g fill="{gold}" stroke="{ink}" stroke-width="1">
        <path d="M238 30 l-4 -9 l7 5 l4 -7 l4 7 l7 -5 l-4 9 z"/>
        <path d="M256 22 l-3 -7 l5 3 l3 -5 l3 5 l5 -3 l-3 7 z"/>
      </g>''').format(**P))


def prop_rain():
    return prop("rain", dedent('''\
      <g stroke="{alu}" stroke-width="1.3" stroke-linecap="round">
        <path d="M236 24 l-2 5"/><path d="M244 18 l-2 5"/><path d="M252 24 l-2 5"/><path d="M260 18 l-2 5"/>
      </g>''').format(**P))


# --------------------------------------------------------------------------
# PLAQUETA (a piada da missao)
# --------------------------------------------------------------------------

def tag(top, sub, accent):
    return dedent('''\
    <g class="tag">
      <rect x="100" y="4" width="170" height="22" rx="3" fill="{deep2}" stroke="{accent}" stroke-width="1.1" opacity=".92"/>
      <path d="M102 6 h166" stroke="{accent}" stroke-width=".7" opacity=".4"/>
      <rect x="96" y="7" width="5" height="12" fill="{gold}" opacity=".65"/>
      <text x="108" y="13.5" font-family="monospace" font-size="8" font-weight="700" fill="{green}">{top}</text>
      <text x="108" y="22.5" font-family="monospace" font-size="6.8" fill="{paper}" opacity=".85">{sub}</text>
    </g>''').format(deep2=P["deep2"], accent=accent, gold=P["gold"],
                    green=P["green"], paper=P["paper"], top=top, sub=sub)

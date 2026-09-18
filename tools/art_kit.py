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
    eyes = ('<circle cx="%s" cy="%s" r="1.15" fill="%s"/>'
            '<circle cx="%s" cy="%s" r=".4" fill="%s"/>') % (_sc(ex), _sc(cy), P["ink"], _sc(ex), _sc(cy), P["paper"])
    # pivô no pescoço (cx, cy+2), inline em px do viewBox (CSS anima a rotação)
    return dedent('''\
      <g class="head" style="transform-origin:{hx}px {hy}px">
        <path d="M{a} {b} q0 -16 8 -16 l8 0 q8 0 8 16 z" fill="{hood}"/>
        <rect x="{c}" y="{d}" width="18" height="7" fill="{skin}"/>
        {eyes}
        <rect x="{c}" y="{e}" width="18" height="4" fill="{hood}"/>
        {hat}
      </g>''').format(a=cx - 8, b=cy + 2, c=cx - 9, d=cy - 1, e=cy + 6, cx=cx, hx=_sc(cx), hy=_sc(cy + 2),
                       hood=P["hood"], skin=P["skin"], eyes=eyes, hat=_hat(cx, cy - 5))


def _torso_svg(x, y, w=16, h=20):
    return ('<rect x="%s" y="%s" width="%s" height="%s" rx="5" fill="%s" stroke="%s" stroke-width="1.6"/>'
            '<path d="M%s %s l%s 0 M%s %s l%s 0 M%s %s l%s 0" stroke="%s" stroke-width=".7" opacity=".35"/>') % (
        _sc(x), _sc(y), w, h, P["paper2"], P["ink"],
        _sc(x + 3), _sc(y + 2), w - 6, _sc(x + 3), _sc(y + 7), w - 6, _sc(x + 3), _sc(y + 12), w - 6, P["ink"])


def _legs(x, y):
    """Pernas desenhadas em coords de cena, pivô no quadril (topo da perna) via style."""
    lx, rx, hy = x + 1.5, x + 9, y
    leg = ('<g class="leg %s" style="transform-origin:%spx %spx">'
           '<rect x="%s" y="%s" width="5.4" height="13" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>'
           '<rect class="foot" x="%s" y="%s" width="6.4" height="3" rx="1.5" fill="%s" stroke="%s" stroke-width="1.1"/>'
           '</g>')
    return (leg % ("leg-l", _sc(lx + 2.7), _sc(hy), _sc(lx), _sc(hy), P["hood_dk"], P["ink"],
                   _sc(lx - 0.5), _sc(hy + 10.6), P["ink"], P["ink"])
            + leg % ("leg-r", _sc(rx + 2.7), _sc(hy), _sc(rx), _sc(hy), P["hood_dk"], P["ink"],
                     _sc(rx - 0.5), _sc(hy + 10.6), P["ink"], P["ink"]))


def _limb(side, sx, sy, hx1, hy1, painter="paper2", extra=""):
    """Braço articulado em coords de cena, pivô no ombro (sx,sy) via transform-origin px.

    `extra` permite pendurar um objeto segurado (pôster, envelope, telefone, dedos)
    DENTRO do grupo do braço, para que balance junto com a mão quando o CSS gira o braço.
    """
    band = ('<path d="M%s %s Q%s %s %s %s" fill="none" stroke="%s" stroke-width="4" '
            'stroke-linecap="round"/>') % (_sc(sx), _sc(sy),
            _sc((sx + hx1) / 2), _sc(min(sy, hy1) - 2), _sc(hx1), _sc(hy1), P[painter])
    hand = '<circle cx="%s" cy="%s" r="2.7" fill="%s" stroke="%s" stroke-width="1.1"/>' % (
        _sc(hx1), _sc(hy1), P[painter], P["ink"])
    return ('<g class="arm arm-%s" style="transform-origin:%spx %spx">%s%s%s</g>'
            % (side, _sc(sx), _sc(sy), band, hand, extra))


def _fingers(hx1, hy1):
    """Dedos para poses de teclado/saudação (animam balanço com pivô no pulso)."""
    return ('<g class="fingers" style="transform-origin:%spx %spx">'
            '<path d="M%s %s v-6 M%s %s v-5 M%s %s v-6" stroke="%s" stroke-width="2" stroke-linecap="round"/></g>') % (
        _sc(hx1), _sc(hy1),
        _sc(hx1 - 5), _sc(hy1), _sc(hx1), _sc(hy1), _sc(hx1 + 5), _sc(hy1), P["skin"])


def char(pose, x=44, y=GROUND, flip=False, gait=False):
    """Personagem articulado (puppet): tronco/braços/pernas/cabeça com pivôs próprios.

    Pivôs em coords de viewBox (o CSS roda `transform` com `transform-origin` igual):
      - cabeça .....(hx, ty-8)   [pescoço]
      - tronco .....(hx, ty+20)  [base / quadril]
      - pernas .....(topo de cada perna, no quadril)
      - braços .....(ombro esq./dir.)
    Objetos segurados entram DENTRO do grupo do braço (extra) → balançam com a mão.
    """
    hx = x + 8
    ty = y - 24
    torso = ('<g class="root" style="transform-origin:%spx %spx">%s</g>'
             % (_sc(hx), _sc(ty + 20), _torso_svg(x + 0.5, ty, 16, 20)))
    sx_l, sy = x + 2, ty + 9
    sx_r = x + 14
    hand_l = _limb("l", sx_l, sy, x + 2, ty + 18)

    if pose == "typing":
        gadget = ('<g class="gadget">'
                  '<rect x="%s" y="%s" width="24" height="6" rx="1.5" fill="%s" stroke="%s" stroke-width="1.1"/>'
                  '<rect x="%s" y="%s" width="28" height="2.4" rx="1" fill="%s"/>'
                  '<g class="tap">'
                  '<path d="M%s %s v3 M%s %s v4 M%s %s v3" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>'
                  '</g></g>'
                  % (_sc(x + 25), _sc(ty + 5), P["hood"], P["ink"],
                     _sc(x + 23), _sc(ty + 11), P["hood_dk"],
                     _sc(x + 28), _sc(ty + 4), _sc(x + 31), _sc(ty + 4), _sc(x + 34), _sc(ty + 4), P["skin"]))
        arms = (_limb("r", sx_r, sy, x + 31, ty + 9, extra=gadget)
                + _limb("l", sx_l, sy, x + 23, ty + 9))
        headwear = ''
    elif pose == "poster":
        poster = ('<g class="gadget"><rect x="%s" y="%s" width="15" height="15" fill="%s" stroke="%s" stroke-width="1.2"/>'
                  '<path d="M%s %s h9 M%s %s h6 M%s %s h4" stroke="%s" stroke-width="1"/>'
                  '</g>'
                  % (_sc(x + 27), _sc(ty - 23), P["paper"], P["ink"],
                     _sc(x + 29), _sc(ty - 19), _sc(x + 29), _sc(ty - 15), _sc(x + 29), _sc(ty - 11), P["stamp"]))
        arms = _limb("r", sx_r, sy, x + 32, ty - 11, extra=poster) + hand_l
        headwear = ''
    elif pose == "pet":
        arms = (_limb("r", sx_r, sy, x + 40, ty + 8) + _limb("l", sx_l, sy, x + 30, ty + 12))
        headwear = ''
    elif pose == "handoff":
        envelope = ('<g class="gadget"><rect x="%s" y="%s" width="13" height="9" rx="1.5" fill="%s" stroke="%s" stroke-width="1.1"/>'
                    '<path d="M%s %s l11 7 M%s %s l-11 7" stroke="%s" stroke-width=".9"/></g>'
                    % (_sc(x + 34), _sc(ty - 5), P["gold"], P["ink"],
                       _sc(x + 35), _sc(ty - 4), _sc(x + 46), _sc(ty - 4), P["ink"]))
        arms = _limb("r", sx_r, sy, x + 40, ty - 1, extra=envelope) + hand_l
        headwear = ''
    elif pose == "point":
        arms = _limb("r", sx_r, sy, x + 36, ty - 8) + hand_l
        headwear = ''
    elif pose == "dj":
        arms = (_limb("r", sx_r, sy, x + 36, ty + 12) + _limb("l", sx_l, sy, x + 28, ty + 15))
        headwear = ('<g class="headgear" style="transform-origin:%spx %spx">'
                    '<path d="M%s %s q8 -8 16 0" fill="none" stroke="%s" stroke-width="2"/>'
                    '<rect x="%s" y="%s" width="4" height="6" rx="2" fill="%s"/></g>'
                    % (_sc(hx), _sc(ty - 10), _sc(hx - 8), _sc(ty - 10), P["ink"],
                       _sc(hx - 10), _sc(ty - 9), P["gold"]))
    elif pose == "phone":
        phone = ('<g class="gadget"><rect x="%s" y="%s" width="7" height="12" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>'
                 '<circle cx="%s" cy="%s" r="1.6" fill="%s"/></g>'
                 % (_sc(x + 19), _sc(ty - 18), P["alu"], P["ink"], _sc(x + 22.5), _sc(ty - 17), P["green"]))
        arms = _limb("r", sx_r, sy, x + 21, ty - 11, extra=phone) + hand_l
        headwear = ''
    elif pose == "router":
        arms = (_limb("r", sx_r, sy, x + 34, ty + 14) + _limb("l", sx_l, sy, x + 29, ty + 16))
        headwear = ''
    elif pose == "peace":
        arms = (_limb("r", sx_r, sy, x + 29, ty - 14, extra=_fingers(x + 29, ty - 14))
                + _limb("l", sx_l, sy, x + 25, ty - 17, extra=_fingers(x + 25, ty - 17)))
        headwear = ''
    else:  # armsup (clima)
        arms = (_limb("r", sx_r, sy, x + 32, ty - 15) + _limb("l", sx_l, sy, x + 27, ty - 17))
        headwear = ''

    head = _head(hx, ty - 10)
    legs = _legs(x, y - 13)
    return '<g class="char">%s%s%s%s%s</g>' % (legs, torso, arms, headwear, head)


# --------------------------------------------------------------------------
# OBJETOS DE CENA (spot) — um por missao, sob o holofote
# --------------------------------------------------------------------------

def spot(loop, inner):
    """Objeto de cena sob o holofote. Wrapper estático (translate) + grupo animado.

    A classe `spot-<loop>` é que recebe o `transform` do CSS; o `translate` fica num
    wrapper <g> separado para o CSS não sobrescrever o posicionamento.
    """
    return ('<g transform="translate(20 16)">'
            '<ellipse cx="198" cy="52" rx="46" ry="3.6" fill="%s" opacity=".5"/>'
            '<g class="spot spot-%s">'
            '%s</g></g>' % (P["deep"], loop, inner))


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

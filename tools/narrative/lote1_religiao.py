"""lote1_religiao.py — Lote 1 do plano de animação v2: mapa 4 (Religião).

Cada missão virou um **loop narrativo** (setup → ação → resolução → reset) sobre
a pintura aprovada, usando o kit de composição: warps locais no que já está
pintado, inpaint só onde a mecânica exige apagar (feixe apagado, garrafa sob o
bico, pessoas no céu), recorte para o que viaja (a garrafa) e FX desenhados no
mesmo traço flat-toon (gotas, auréola, lágrima, confete, chamas, vapor).

As três referências do dono — que definem o padrão de complexidade do lote:
  * p4_10 · projetar o arrebatamento holográfico (luz apaga, botão livre,
    aperta, feixe acende, pessoas sobem aureoladas e somem, luz apaga, loop);
  * p4_08 · bendizer a água da torneira (esteiras andam, torneira enche a
    garrafa vazia, a cheia segue e ganha adesivo de auréola, vapor/bolhas/
    goteira/engrenagens animados, inspetor olha e anota na prancheta);
  * p4_06 · mandar a imagem chorar xarope (o quadro chora, gotas caem e enchem
    o copo, o comerciante serve o vidro, as velas tremulam o tempo todo).
"""
from __future__ import annotations

import math

import numpy as np
from PIL import ImageDraw

from . import kit as K

# ---------------------------------------------------------------------------
# histórias (vão para a spec — legível para o dono e para a QA)
# ---------------------------------------------------------------------------
STORIES = {
    "p4_01": "O disco gira, a agulha vibra e as caixas soltam notas espelhadas; o letreiro "
             "pisca e revela a mensagem invertida — e tudo volta ao normal.",
    "p4_02": "A TV pulsa a espiral hipnótica, o diabinho balança e os olhos do menino e do "
             "gato giram; pipocas saltam da tigela — e o desenho volta ao neutro.",
    "p4_03": "A esteira anda com as bonecas; a possuída flutua com olhos acesos, chave "
             "girando e aura roxa; o pincel pinga tinta — e o ciclo recomeça.",
    "p4_04": "O mapa limpa: o sigilo geométrico se desenha do centro para fora sobre a "
             "capital, o olho alado circula e o alfinete crava — o traço brilha e apaga.",
    "p4_05": "Palco escuro: o holofote acende no arco, a lágrima gigante cai, o confete de "
             "luz desce e a plateia entra em êxtase — e a luz apaga.",
    "p4_06": "O quadro chora xarope: as gotas formam no fio, caem e enchem o copo; o "
             "comerciante mergulha a colher, serve o vidro no pote e as velas tremulam.",
    "p4_07": "Os dois rolos giram, a onda de áudio corre pela fita e o '13' pisca na tábua "
             "enquanto as agulhas do painel tremem — e a onda volta ao mínimo.",
    "p4_08": "As esteiras andam: a torneira enche a garrafa vazia, a cheia segue para o "
             "outro lado e ganha o adesivo de auréola; o inspetor olha, anota, e o vapor, "
             "as bolhas, a goteira e as engrenagens não param.",
    "p4_09": "Ele empurra o bloco do X no calendário (de novo): a sirene gira, papéis voam, "
             "o carimbo marca mais um dia — e o calendário zera no reset.",
    "p4_10": "Luz azul desligada e botão sem mão: o personagem aperta o botão, o feixe "
             "acende, as pessoas sobem aureoladas e somem — a luz apaga e o loop recomeça.",
}

# ritmo por missão (ms/quadro): setup lento → ação rápida → hold → reset suave
DUR = {
    "p4_01": [140, 120, 120, 120, 140, 140, 140, 140, 120, 120, 120, 140],
    "p4_02": [140, 120, 120, 120, 140, 140, 140, 140, 120, 120, 120, 140],
    "p4_03": [160, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 140, 140, 160, 160],
    "p4_04": [150, 130, 130, 130, 130, 130, 130, 130, 140, 140, 150, 160],
    "p4_05": [200, 140, 140, 140, 140, 160, 140, 140, 140, 140, 140, 140, 160, 180, 180, 200],
    "p4_06": [200, 140, 140, 140, 140, 160, 140, 140, 140, 140, 140, 140, 160, 180, 180, 200],
    "p4_07": [140, 120, 120, 120, 140, 140, 140, 140, 120, 120, 120, 140],
    "p4_08": [150, 130, 130, 130, 130, 140, 140, 140, 140, 140, 150, 150, 150, 150, 160, 160],
    "p4_09": [160, 130, 130, 130, 130, 130, 130, 130, 140, 140, 150, 160],
    "p4_10": [260, 160, 160, 140, 140, 160, 140, 140, 140, 140, 140, 140, 160, 180, 220, 240],
}

# pré-cálculos caros (inpaint, recorte, reconstrução de fundo) ficam em cache
_CACHE: dict = {}


def _prep(scene: str) -> dict:
    if scene not in _CACHE:
        _CACHE[scene] = _PREP[scene]()
    return _CACHE[scene]


def _out(img) -> np.ndarray:
    return K.from_rgba(img)


# ===========================================================================
# p4_01 · Gravar a mensagem invertida no vinil
# ===========================================================================
_FLAMES_01 = [(55, 88), (205, 262), (240, 318), (393, 120), (405, 120), (500, 283)]


def scene_p4_01():
    N = 12
    base = K.plate("p4_01")
    frames = []
    for i in range(N):
        a = base.copy()
        a = K.warp_rotate(a, 373, 273, 31, 360.0 * i / N)            # prato girando
        a = K.warp_rotate(a, 418, 258, 20, 3.0 * K.cyc(i, N, 0.25))  # agulha vibrando
        a = K.warp_rotate(a, 75, 75, 85, 8.0 * K.cyc(i, N))          # espirais das caixas
        a = K.warp_rotate(a, 545, 85, 95, -8.0 * K.cyc(i, N, 0.25))
        for k, (cx, cy) in enumerate(_FLAMES_01):                    # velas
            a = K.warp_shift(a, K.mellipse(cx, cy, 5, 7, 1.5), 0, 0.9 * K.cyc(i, N, 0.17 * k))
            a = K.glow(a, cx, cy, 13, (255, 196, 96), 0.30 + 0.16 * K.cyc(i, N, 0.11 * k))
        a = K.glow(a, 226, 45, 46, (120, 240, 255), 0.14 + 0.10 * K.cyc(i, N))  # letreiro
        img = K.to_rgba(a)
        inv = K.track([(4, 0), (5, 1), (8, 1), (9, 0)], i)           # mensagem invertida
        if inv > 0.01:
            K.fx_text(img, 226, 45, "LIVE", 15, (170, 255, 246), inv,
                      mirror=True, stroke=(12, 44, 66))
        for k in range(3):                                           # notas espelhadas
            t = (i / N + k / 3.0) % 1.0
            al = math.sin(math.pi * t) * 0.92
            K.fx_note(img, 120 - 58 * t + 8 * math.sin(math.pi * t), 150 - 88 * t,
                      10, al, (255, 232, 190), mirror=True)
            K.fx_note(img, 490 + 56 * t, 160 - 80 * t, 10, al, (255, 232, 190), mirror=True)
        # o vinil é um círculo perfeito: sem um brilho que orbita o giro não se lê
        ang = 2 * math.pi * i / N + 0.4
        d = ImageDraw.Draw(img)
        gx, gy = 373 + 21 * math.cos(ang), 273 + 9 * math.sin(ang)
        d.ellipse([gx - 3, gy - 2, gx + 3, gy + 2], fill=(255, 255, 255, 120))
        gx2, gy2 = 373 + 21 * math.cos(ang + math.pi), 273 + 9 * math.sin(ang + math.pi)
        d.ellipse([gx2 - 2, gy2 - 1, gx2 + 2, gy2 + 1], fill=(255, 255, 255, 70))
        frames.append(_out(img))
    return N, DUR["p4_01"], STORIES["p4_01"], frames


# ===========================================================================
# p4_02 · Exibir o desenho da indução espiritual
# ===========================================================================
def scene_p4_02():
    N = 12
    base = K.plate("p4_02")
    eyes = [(384, 174, 10, 1.0), (406, 174, 10, 1.0), (508, 246, 8, -1.0), (528, 246, 8, -1.0)]
    frames = []
    for i in range(N):
        a = base.copy()
        a = K.tint(a, K.mellipse(175, 155, 58, 52, 16), (92, 220, 236), 0.10 + 0.06 * K.cyc(i, N))
        a = K.warp_rotate(a, 175, 168, 20, 6.0 * K.cyc(i, N))         # diabinho balança
        a = K.warp_shift(a, K.mellipse(175, 150, 22, 26, 4), 0, 2.0 * K.cyc(i, N, 0.25))
        for (ex, ey, er, sgn) in eyes:                                # olhos girando
            a = K.warp_rotate(a, ex, ey, er, sgn * 360.0 * i / N)
        a = K.warp_shift(a, K.mellipse(395, 200, 60, 90, 9), 0, 1.5 * K.cyc(i, N, 0.5))
        a = K.warp_rotate(a, 545, 318, 26, 10.0 * K.cyc(i, N, 0.75))  # rabo do gato
        a = K.glow(a, 175, 155, 74, (120, 255, 240), 0.13 + 0.06 * K.cyc(i, N))
        img = K.to_rgba(a)
        for k in range(3):                                            # pipocas saltando
            t = (i / N + k / 3.0) % 1.0
            al = math.sin(math.pi * t)
            K.fx_drop(img, 385 + 9 * math.sin(math.pi * t * 2),
                      250 - 26 * math.sin(math.pi * t), 3.4, (255, 240, 186), al)
        frames.append(_out(img))
    return N, DUR["p4_02"], STORIES["p4_02"], frames


# ===========================================================================
# p4_03 · Fábrica do boneco possuído
# ===========================================================================
def scene_p4_03():
    N = 16
    base = K.plate("p4_03")
    frames = []
    for i in range(N):
        a = base.copy()
        # engrenagens da esteira: o passo medido (57 px) fecha o loop sem salto
        a = K.roll_band(a, 0, 400, 286, 318, -57.0 * i / N)
        for cx in (25, 75, 275, 345):                                 # bonecas marchando
            a = K.warp_shift(a, K.mellipse(cx, 225, 26, 40, 6),
                             0, 1.2 * math.sin(2 * math.pi * (2 * i / N) + cx * 0.13))
        a = K.warp_shift(a, K.mellipse(195, 140, 55, 60, 9), 0, 5.0 * K.cyc(i, N))  # possuída
        a = K.warp_rotate(a, 150, 105, 16, 360.0 * i / N)             # chave de corda
        a = K.warp_rotate(a, 400, 185, 26, 8.0 * K.cyc(i, N))         # mão do pincel
        a = K.glow(a, 195, 140, 72, (200, 120, 255), 0.30 + 0.12 * K.cyc(i, N))
        a = K.tint(a, K.mellipse(187, 120, 5, 5, 1.5), (255, 70, 70), 0.55 + 0.40 * K.cyc(i, N, 0.25))
        a = K.tint(a, K.mellipse(210, 120, 5, 5, 1.5), (255, 70, 70), 0.55 + 0.40 * K.cyc(i, N, 0.25))
        for k, (lx, ly) in enumerate([(75, 45), (315, 45), (545, 45)]):
            a = K.glow(a, lx, ly, 60, (255, 190, 90), 0.10 + 0.05 * K.cyc(i, N, k / 3.0))
        img = K.to_rgba(a)
        for k in range(2):                                            # tinta pingando
            t = ((i / (N / 2.0)) + k / 2.0) % 1.0
            if t > 0.97:
                continue
            K.fx_drop(img, 388, 180 + t * 56, 2.4, (236, 240, 246),
                      min(1.0, t * 6) * (1 - t) ** 0.35)
        frames.append(_out(img))
    return N, DUR["p4_03"], STORIES["p4_03"], frames


# ===========================================================================
# p4_04 · Traçar a capital em sigilo geométrico
# ===========================================================================
def _prep_p4_04():
    base = K.plate("p4_04")
    # o "traço" do sigilo é verde-ciano por cima de um mapa que também tem grade
    # esverdeada: o limiar médio separa os dois (o alto deixava fantasma do traço,
    # o baixo lavava a cidade)
    lines = K.color_key(base, lambda a: (a[..., 1] > 115) & (a[..., 1] - a[..., 0] > 26)
                        & (a[..., 1] - a[..., 2] > 12))
    lines_d = K.grow(lines, 2.0)
    nl = K.inpaint(base, lines_d, iters=45)                            # mapa limpo
    eye_box = (478, 50, 516, 84)
    nl = K.inpaint(nl, K.mrect(*eye_box, feather=1.5), iters=35)
    return {"nl": nl, "diff": (base - nl) * lines_d[..., None],
            "eye": K.cut(base, eye_box, 3)}


def scene_p4_04():
    N = 12
    C = _prep("p4_04")
    dist = np.sqrt((K._X - 345) ** 2 + (K._Y - 165) ** 2)
    frames = []
    for i in range(N):
        rev = K.smooth(K.track([(0, 0), (1, 0), (8, 1), (9, 1)], i))   # o traço se desenha
        fade = K.track([(9, 1), (11, 0)], i)                           # e apaga no reset
        pulse = 1.0 + 0.35 * math.sin(math.pi * min(1.0, max(0.0, (i - 8) / 2.0)))
        step = np.clip((rev * 340 - 40 + 26 - dist) / 26.0, 0, 1)
        alpha = step * fade * pulse
        a = C["nl"] + C["diff"] * alpha[..., None]
        a = K.glow(a, 345, 165, 130, (90, 255, 170), 0.06 * fade)
        img = K.to_rgba(a)
        ang = 2 * math.pi * i / N - 0.6 * math.pi                      # olho alado circula
        K.paste(img, C["eye"], 345 + 200 * math.cos(ang) - C["eye"].width / 2,
                165 + 108 * math.sin(ang) - C["eye"].height / 2,
                rot=14 * math.sin(2 * math.pi * i / N))
        pin_a = K.track([(5, 0), (6, 1), (9, 1), (10, 0)], i)          # alfinete crava
        if pin_a > 0.01:
            py = 62 + 88 * K.smooth(K.track([(5, 0), (9, 1)], i))
            d = ImageDraw.Draw(img)
            d.ellipse([345 - 3, py - 7, 345 + 3, py], fill=(214, 66, 58, 255))
            d.line([345, py, 345, py + 9], fill=(214, 214, 226, 255), width=1)
        K.fx_spark(img, 345, 151, 10, (255, 255, 226),
                   K.track([(8, 0), (9, 1), (11, 0)], i))
        frames.append(_out(img))
    return N, DUR["p4_04"], STORIES["p4_04"], frames


# ===========================================================================
# p4_05 · Encenar o milagre ao vivo
# ===========================================================================
def _prep_p4_05():
    on = K.plate("p4_05")
    beam = K.color_key(on, lambda a: (a[..., 0] - a[..., 2] > 60) & (a[..., 0] > 140)
                       & (K._X > 240))
    arch = K.mrect(395, 12, 548, 268, 3)
    outside = 1.0 - (arch > 0.4).astype(np.float32)
    shaft = K.grow(K.grow((beam * outside * (K._Y < 272)).astype(np.float32), 1.0), 1.0)
    floor = K.grow(K.grow((beam * outside * (K._Y >= 272)).astype(np.float32), 1.0), 1.0)
    ring = np.clip(K.mellipse(398, 304, 124, 27, 1.0) - K.mellipse(398, 304, 106, 19, 1.0), 0, 1)
    floor = np.maximum(floor, (ring > 0.35).astype(np.float32))
    off = K.fill_rows(on, shaft, 0, K.H, (240, 560), skip_rect=(395, 0, 560, 272))
    off = K.fill_rows(off, floor, 0, K.H, (240, 560))
    arch_m = K.mrect(395, 12, 550, 272, 3)[..., None]                  # holofote apagado
    cool = np.array([26, 44, 56], np.float32)
    off = off * (1 - arch_m) + (off * 0.30 + cool * 0.42) * arch_m
    return {"on": on, "off": off}


def scene_p4_05():
    N = 16
    C = _prep("p4_05")
    frames = []
    for i in range(N):
        beam = K.smooth(K.track([(0, 0), (3, 0), (5, 1), (11, 1), (13, 0), (15, 0)], i))
        a = K.lerp_imgs(C["off"], C["on"], beam)
        a = K.warp_shift(a, K.mellipse(95, 252, 46, 62, 9), 0, 1.5 * K.cyc(i, N))
        img = K.to_rgba(a)
        for k in range(7):                                             # confete de luz
            t = (i / N + k / 7.0) % 1.0
            K.fx_dash(img, 300 + ((k * 53) % 180) + 9 * math.sin(2 * math.pi * t * 2),
                      88 + t * 205, 6, 20 * k, math.sin(math.pi * t) * beam,
                      [(255, 236, 150), (255, 255, 240), (250, 210, 160)][k % 3], 2)
        tf = K.track([(6, 0), (10, 1)], i)                             # lágrima gigante
        ta = K.track([(6, 0), (6.6, 1), (9.4, 1), (10, 0)], i)
        if ta > 0.01:
            K.fx_drop(img, 462, 58 + tf * 138, 6 + 2 * min(1.0, tf * 4), (208, 244, 255), ta)
        K.fx_splash(img, 462, 198, 12, (208, 244, 255), K.track([(9, 0), (10, 1), (11, 0)], i))
        for k in range(9):                                             # plateia em êxtase
            K.fx_dash(img, 18 + k * 33, 233 + (k % 3) * 8, 9,
                      -70 + 20 * math.sin(2 * math.pi * (i / N + k / 9.0)),
                      beam * (0.30 + 0.30 * K.cyc(i, N, k / 9.0)), (255, 240, 190), 2)
        for k in range(2):                                             # megafone do diretor
            tt = (i / 6.0 + k / 2.0) % 1.0
            K.fx_arc(img, 128, 214, 6 + tt * 17, -55, 5, (1 - tt) * 0.45, (255, 235, 200), 2)
        frames.append(_out(img))
    return N, DUR["p4_05"], STORIES["p4_05"], frames


# ===========================================================================
# p4_06 · Mandar a imagem chorar xarope  (referência do dono)
# ===========================================================================
def _prep_p4_06():
    base = K.plate("p4_06")
    wall = np.median(base[236:240, 300:330].reshape(-1, 3), axis=0)    # parede atrás do copo
    glass = np.array([150, 178, 176], np.float32)
    interior = np.clip(wall * 0.35 + glass * 0.65, 0, 255).astype(np.uint8)
    out = base.copy()
    m = K.mrect(265, 240, 284, 258, 1.0)[..., None]
    flat = np.zeros_like(base) + interior.reshape(1, 1, 3)
    return {"base": out * (1 - m) + flat * m}


def scene_p4_06():
    N = 16
    C = _prep("p4_06")
    flames = [(410, 72), (575, 72), (452, 150), (490, 150), (523, 150)]
    lights = [(20, 26), (58, 20), (98, 18), (138, 26), (178, 36)]
    frames = []
    for i in range(N):
        a = C["base"].copy()
        tilt = K.track([(12, 0), (13, 22), (14, 22), (15, 5)], i)      # serve o copo
        a = K.warp_rotate(a, 292, 252, 20, tilt)
        a = K.warp_rotate(a, 245, 218, 28,
                          12.0 * K.track([(5, 0), (7, 1), (9, 1), (11, 0)], i))  # colher
        a = K.warp_shift(a, K.mellipse(165, 170, 42, 46, 6), 0, 1.0 * K.cyc(i, N))
        for k, (cx, cy) in enumerate(flames):                          # chamas tremulando
            a = K.warp_shift(a, K.mellipse(cx, cy, 5, 7, 1.5), 0, 0.9 * K.cyc(i, N, 0.13 * k))
            a = K.glow(a, cx, cy, 13, (255, 196, 96), 0.30 + 0.16 * K.cyc(i, N, 0.11 * k))
        for k, (lx, ly) in enumerate(lights):                          # lâmpadas do varal
            a = K.glow(a, lx, ly, 9, (255, 226, 170),
                       0.30 * max(0.0, math.sin(2 * math.pi * (2 * i / N + k / 5.0))))
        img = K.to_rgba(a)
        d = ImageDraw.Draw(img)
        for (fx_, y0, y1) in [(277, 178, 212), (292, 178, 206), (360, 178, 232)]:
            for k in range(2):                                         # brilho no fio de xarope
                t = (i / N + k / 2.0) % 1.0
                yy = y0 + t * (y1 - y0)
                d.rounded_rectangle([fx_ - 2, yy - 4, fx_ + 2, yy + 4], radius=2,
                                    fill=(255, 236, 178, K._a(math.sin(math.pi * t) * 0.8)))

        def drip(phase, x, y0, y1, color=(255, 214, 120)):             # gotas que caem
            tt = ((i + phase) % 8) / 8.0
            if tt < 0.32:                                              # formando no fio
                K.fx_drop(img, x, y0, 1.0 + 3.2 * (tt / 0.32), color, 0.65 + 0.30 * (tt / 0.32))
            else:                                                      # caindo
                t = (tt - 0.32) / 0.68
                K.fx_drop(img, x, y0 + t * (y1 - y0), 2.6 * (0.75 + 0.35 * t), color, 0.95)
                if t > 0.88:
                    K.fx_splash(img, x, y1, 7, (255, 226, 170), (t - 0.88) / 0.12 * 0.75)

        drip(0, 278, 206, 240)                                         # enche o copo
        drip(8, 278, 206, 240)
        drip(4, 360, 226, 262)                                         # respinga no balcão
        drip(12, 360, 226, 262)
        level = K.track([(0, 0.0), (5, 0.42), (9, 0.50), (12, 0.95), (13, 0.90), (15, 0.0)], i)
        if level > 0.02 and tilt < 5:
            ytop = 257 - 16 * level
            d.rectangle([266, ytop, 283, 257], fill=(232, 178, 66, 240))
            d.line([266, ytop, 283, ytop], fill=(255, 226, 150, 240), width=1)
        pa = K.track([(13, 0), (14, 0.95), (15, 0.6)], i)              # serve no pote
        if pa > 0.01:
            for k in range(3):
                t = 0.12 + k / 3.0
                K.fx_drop(img, 288 + 110 * t, 242 + 6 * math.sin(math.pi * t), 2.6,
                          (240, 190, 90), pa)
            K.fx_spark(img, 400, 240, 7, (255, 246, 210), pa * 0.8)
        frames.append(_out(img))
    return N, DUR["p4_06"], STORIES["p4_06"], frames


# ===========================================================================
# p4_07 · Gravar o 13º mandamento só no áudio
# ===========================================================================
def _prep_p4_07():
    base = K.plate("p4_07")
    ribbon = K.color_key(base, lambda a: (a[..., 2] > 150) & (a[..., 1] > 120) & (a[..., 0] < 130))
    return {"base": base, "ribbon": ribbon}


def scene_p4_07():
    N = 12
    C = _prep("p4_07")
    frames = []
    for i in range(N):
        a = C["base"].copy()
        a = K.warp_rotate(a, 90, 185, 26, 360.0 * i / N)               # rolos girando
        a = K.warp_rotate(a, 145, 185, 26, 360.0 * i / N)
        wave = 0.85 + 0.35 * np.sin(2 * np.pi * (K._X / 140.0 - i / N))
        a = a + C["ribbon"][..., None] * wave[..., None] * np.array([26, 60, 74], np.float32)
        a = K.warp_rotate(a, 548, 214, 10, 14 * math.sin(2 * math.pi * 3 * i / N))
        a = K.warp_rotate(a, 586, 214, 10, 14 * math.sin(2 * math.pi * 3 * i / N + 1.0))
        a = K.warp_shift(a, K.mellipse(350, 205, 42, 60, 6), 0,
                         1.0 * math.sin(2 * math.pi * 4 * i / N))
        a = K.glow(a, 352, 54, 46, (120, 240, 255), 0.10 + 0.06 * math.sin(2 * math.pi * 2 * i / N))
        img = K.to_rgba(a)
        al13 = K.track([(3, 0), (4, 1), (8, 1), (9, 0)], i) * (1.0 if i % 2 == 0 else 0.55)
        K.fx_text(img, 352, 54, "13", 30, (200, 255, 255), al13, stroke=(20, 60, 80))
        for k in range(2):                                             # ondas do microfone
            tt = (i / 6.0 + k / 2.0) % 1.0
            K.fx_arc(img, 282, 182, 8 + tt * 18, -60, 10, (1 - tt) * 0.45, (150, 245, 255), 2)
        frames.append(_out(img))
    return N, DUR["p4_07"], STORIES["p4_07"], frames


# ===========================================================================
# p4_08 · Bendizer a água da torneira  (referência do dono)
# ===========================================================================
def _prep_p4_08():
    base = K.plate("p4_08")
    # 1) "estação" sob o bico: o bico precisa de um trecho limpo de esteira para
    #    receber a garrafa vazia, então reconstruímos a faixa amostrando a própria
    #    pintura (parede à direita do vão, madeira à esquerda do cano).
    clean = base.copy()
    m = np.zeros((K.H, K.W), np.float32)
    m[168:248, 342:379] = 1.0
    m = K.blur_mask(m, 3.0)
    fill = base.copy()
    for y in range(168, 248):
        # a faixa x 296..312 tem a mesma estrutura vertical do vão: parede em cima,
        # madeira da esteira embaixo — então a mediana por linha reconstitui tudo
        fill[y] = np.median(base[y, 296:313], axis=0)
    rng = np.random.default_rng(7)
    fill[168:248, 342:379] += rng.normal(0, 1.6, size=(248 - 168, 37, 3)).astype(np.float32)
    clean = clean * (1 - m[..., None]) + fill * m[..., None]
    # 2) garrafa vazia da esteira esquerda (fundo chapado conhecido da pintura)
    empty = K.cut_silhouette(base, (272, 184, 298, 240), tol=95, ramp=30, feather=0.9,
                             grow_px=2, bg=np.array([51, 148, 150], np.float32))
    # 3) passo real das garrafas em cada fileira (autocorrelação): rolar por um
    #    passo inteiro faz o loop fechar com uma única passada da esteira extra
    def pitch(x0, x1, y0, y1):
        band = base[y0:y1, x0:x1].mean(-1)
        return min(range(18, 46), key=lambda s: float(np.abs(band[:, :-s] - band[:, s:]).mean()))
    return {"b": clean, "empty": empty,
            "pitch_esq": float(pitch(20, 290, 190, 255)),
            "pitch_dir": float(pitch(390, 630, 185, 255))}


def scene_p4_08():
    N = 16
    C = _prep("p4_08")
    frames = []
    for i in range(N):
        a = C["b"].copy()
        rolled = a.copy()
        K.roll_band(rolled, 0, 300, 188, 272, C["pitch_esq"] * i / N)  # esteira esquerda
        xs = np.arange(378, 640)[None, :, None]                        # esmaece a borda da faixa
        t = np.clip((xs - 378) / 14.0, 0, 1)
        a[:, 378:640] = rolled[:, 378:640] * t + a[:, 378:640] * (1 - t)
        for k, gx in enumerate((58, 148, 238, 428, 508, 596)):         # engrenagens
            a = K.warp_rotate(a, gx, 292, 13, (360.0 * i / N) * (-1 if k % 2 else 1), 0.8)
        a = K.warp_rotate(a, 555, 222, 34, 7.0 * math.sin(2 * math.pi * 2 * i / N), 0.7)
        a = K.warp_shift(a, K.mellipse(560, 250, 16, 16, 5),           # mão anotando
                         2.5 * math.sin(2 * math.pi * 6 * i / N),
                         2.0 * math.cos(2 * math.pi * 6 * i / N))
        a = K.warp_rotate(a, 572, 124, 26, 8.0 * K.cyc(i, N, 0.5), 0.7)  # auréola do inspetor
        a = K.tint(a, K.mellipse(232, 332, 26, 8, 3), (200, 240, 250), 0.10 + 0.06 * K.cyc(i, N))
        a = K.tint(a, K.mellipse(420, 342, 26, 8, 3), (200, 240, 250),
                   0.10 + 0.06 * K.cyc(i, N, 0.5))
        img = K.to_rgba(a)
        d = ImageDraw.Draw(img)
        # 3) a garrafa-protagonista: entra da esteira, para sob o bico, enche,
        #    recebe a auréola e segue para o outro lado (vira a fileira abençoada)
        x = K.track([(0, 344), (2, 361), (8, 361), (12, 396), (15, 396)], i)
        sp_a = K.track([(0, 0), (1, 1), (12, 1), (15, 0)], i)
        level = K.track([(3, 0), (4, 0.08), (8, 1.0), (12, 1.0)], i)
        bot = K.fill_bottle(C["empty"], level) if level < 0.99 else K.fill_bottle(C["empty"], 1.0)
        K.paste(img, bot, x - bot.width / 2, 182, sp_a)
        sa = K.track([(2, 0), (3, 1), (8, 1), (9, 0)], i)              # a torneira abre
        if sa > 0.01:
            for yy in range(160, 190, 5):
                wob = math.sin(yy / 12.0 + i * 1.3) * 1.1
                d.line([361 + wob, yy, 361 + wob, yy + 4],
                       fill=(190, 240, 255, int(228 * sa)), width=2)
            K.fx_splash(img, 361, 190, 6, (210, 245, 255), sa * 0.8)
        st_t = K.smooth(K.track([(10, 0), (11, 1)], i))                # adesivo de auréola
        halo_a = K.track([(10, 0), (11, 1), (15, 1)], i) * sp_a
        if halo_a > 0.01:
            K.fx_halo(img, x, 176, 10 + 5 * (1 - st_t), halo_a, (255, 216, 120), 1.5)
        K.fx_steam(img, 140, 40, 26, 0.30, i / N)                      # vapor
        K.fx_steam(img, 430, 32, 24, 0.26, (i / N + 0.4) % 1.0)
        K.fx_steam(img, 608, 44, 22, 0.22, (i / N + 0.7) % 1.0)
        K.fx_bubbles(img, 118, 96, 30, 5, i / N, (190, 245, 255), 0.8)  # dornas borbulhando
        K.fx_bubbles(img, 200, 88, 34, 5, (i / N + 0.5) % 1.0, (190, 245, 255), 0.8)
        tt = ((i + 2) % 8) / 8.0                                       # goteira do barril
        if tt < 0.3:
            K.fx_drop(img, 150, 166, 1 + 2.4 * (tt / 0.3), (200, 240, 250), 0.75)
        else:
            K.fx_drop(img, 150, 166 + ((tt - 0.3) / 0.7) * 62, 2.6, (200, 240, 250), 0.9)
        sc_a = K.track([(0, 1), (11, 1), (13, 0), (15, 0)], i)         # anota e vira a página
        if sc_a > 0.01:
            K.fx_scribble(img, (508, 236, 546, 268), min(10, int(i * 1.35)), i * 0.4, sc_a * 0.85)
        if i == 6:                                                     # piscada
            d.ellipse([524, 182, 540, 191], fill=(236, 190, 156, 255))
        frames.append(_out(img))
    return N, DUR["p4_08"], STORIES["p4_08"], frames


# ===========================================================================
# p4_09 · Empurrar o apocalipse (de novo)
# ===========================================================================
def scene_p4_09():
    N = 12
    base = K.plate("p4_09")
    frames = []
    for i in range(N):
        lean = K.smooth(K.track([(0, 0), (3, 1), (6, 1), (9, 0), (11, 0)], i))
        a = base.copy()
        a = K.warp_rotate(a, 350, 335, 95, 6.0 * lean, 0.6)            # ele empurra
        a = K.warp_shift(a, K.mrect(405, 100, 538, 238, 6),
                         10.0 * lean + 1.4 * math.sin(2 * math.pi * 6 * i / N) * lean, 0)
        a = K.glow(a, 70, 42, 30, (255, 70, 55), 0.30 + 0.30 * math.sin(2 * math.pi * 2 * i / N))
        a = K.glow(a, 95, 142, 58, (255, 195, 110), 0.10 + 0.05 * K.cyc(i, N, 0.3))
        img = K.to_rgba(a)
        K.fx_wedge(img, 70, 42, 30, (i / N) * 360.0, 44, 0.28, (255, 90, 70))  # sirene girando
        for k in range(3):                                             # papéis voando
            t = (i / N + k / 3.0) % 1.0
            K.fx_papers(img, [448, 560, 604][k] + 12 * math.sin(2 * math.pi * t),
                        [40, 86, 18][k] + t * 250, 12, 40 * t, math.sin(math.pi * t) * 0.95)
        xa = K.track([(4, 0), (5, 1), (8, 1), (10, 0)], i)             # carimba mais um dia
        if xa > 0.01:
            K.fx_xmark(img, 562, 64, 30, xa, (214, 66, 58), 4)
        K.fx_ring(img, 562, 64, 10 + max(0, i - 5) * 9,
                  K.track([(5, 0), (6, 1), (8, 0)], i) * 0.6, (255, 120, 90), 2)
        for k in range(2):                                             # gotas de suor
            t = (i / N * 2 + k / 2.0) % 1.0
            K.fx_drop(img, 305 - 16 * t, 112 + 26 * t + 8 * t * t, 2.4, (200, 240, 255),
                      math.sin(math.pi * t))
        if lean > 0.05:                                                # poeira do empurrão
            K.fx_steam(img, 470, 236, 22, 0.22 * lean, (i / N) % 1.0, (226, 214, 190))
        frames.append(_out(img))
    return N, DUR["p4_09"], STORIES["p4_09"], frames


# ===========================================================================
# p4_10 · Projetar o arrebatamento holográfico  (referência nº1 do dono)
# ===========================================================================
PEOPLE_10 = [(375, 292, (232, 110, 160)), (410, 288, (84, 142, 220)),
             (440, 292, (152, 112, 78)), (475, 296, (242, 202, 84))]


# pessoas pintadas flutuando no céu do pôster (medidas no original) — a versão
# "acesso ligado" da cena é o pôster sem elas; a versão "desligado" é o
# plate_off.webp, que a arte já previu sem feixe e sem gente no céu.
_PAINTED_10 = [
    (357, 205, 25, 35), (425, 150, 25, 33), (498, 175, 28, 35), (500, 292, 21, 29),
]
_PAINTED_HALOS_10 = [(358, 150), (425, 104), (505, 128), (523, 252)]


def _prep_p4_10():
    on = K.plate("p4_10")
    off = K.plate("p4_10", "plate_off.webp")
    m = np.zeros((K.H, K.W), np.float32)
    for (cx, cy, rx, ry) in _PAINTED_10:
        m = np.maximum(m, K.mellipse(cx, cy, rx, ry, 5))
    for (cx, cy) in _PAINTED_HALOS_10:
        m = np.maximum(m, K.mellipse(cx, cy, 18, 10, 4))
    # dentro do feixe só dá para reconstruir por difusão: a névoa residual lê
    # como brilho do próprio holograma (é o mesmo caminho da luz)
    return {"on": K.inpaint(on, m, iters=160), "off": off}


def scene_p4_10():
    N = 16
    C = _prep("p4_10")
    frames = []
    for i in range(N):
        beam = K.smooth(K.track([(4, 0), (6, 1), (11, 1), (13, 0), (15, 0)], i))
        a = K.lerp_imgs(C["off"], C["on"], beam)                       # a luz acende e apaga
        hover = K.track([(0, 1), (2, 1), (4, 0), (14, 0), (15, 1)], i)  # botão sem mão
        a = K.warp_shift(a, K.mellipse(247, 297, 26, 22, 4), 0, -7.0 * hover)
        press = K.track([(3, 0), (4, 1), (6, 1), (7, 0)], i)
        if press > 0.01:
            a = K.tint(a, K.mellipse(255, 314, 19, 8, 2), (150, 40, 40), 0.5 * press)
        a = K.glow(a, 272, 252, 26, (180, 240, 255), 0.55 * beam)      # cúpula acesa
        a = K.tint(a, K.mrect(242, 268, 308, 298, 3), (150, 240, 255), 0.26 * beam)
        img = K.to_rgba(a)
        if press > 0.4:
            K.fx_spark(img, 255, 318, 7, (255, 250, 220),
                       K.track([(4, 0), (4.5, 1), (6, 0)], i))
        for k, (px, py, col) in enumerate(PEOPLE_10):                  # arrebatamento
            t = K.track([(6 + k * 0.6, 0), (11.4 + k * 0.6, 1),
                         (12.4 + k * 0.6, 1), (13.4, 0), (15, 0)], i)
            al = 1.0 - K.smooth(max(0.0, (t - 0.74) / 0.26))
            halo = K.smooth(K.track([(5.8 + k * 0.6, 0), (6.4 + k * 0.6, 1),
                                     (11.2 + k * 0.6, 1), (11.8 + k * 0.6, 0)], i))
            K.fx_person(img, px, py - 132 * K.smooth(t), 34, col, (244, 206, 168), al,
                        arms_up=K.smooth(t) * 0.9, halo=halo)
        frames.append(_out(img))
    return N, DUR["p4_10"], STORIES["p4_10"], frames


# ---------------------------------------------------------------------------
_PREP = {
    "p4_04": _prep_p4_04,
    "p4_05": _prep_p4_05,
    "p4_06": _prep_p4_06,
    "p4_07": _prep_p4_07,
    "p4_08": _prep_p4_08,
    "p4_10": _prep_p4_10,
}

SCENES = {
    "p4_01": scene_p4_01,
    "p4_02": scene_p4_02,
    "p4_03": scene_p4_03,
    "p4_04": scene_p4_04,
    "p4_05": scene_p4_05,
    "p4_06": scene_p4_06,
    "p4_07": scene_p4_07,
    "p4_08": scene_p4_08,
    "p4_09": scene_p4_09,
    "p4_10": scene_p4_10,
}

LOTE = sorted(SCENES)

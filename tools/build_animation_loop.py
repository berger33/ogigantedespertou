#!/usr/bin/env python3
"""build_animation_loop.py — monta o LOOP animado de uma missão a partir dos quadros.

Fluxo (desenho 2D real, estilo desenho animado):
  1. `tools/art_kit` gerava cenas geométricas; agora cada missão tem quadros
     PINTADOS (frames/f00.png ... fNN.png) em 2D cartoon.
  2. Este script: recorta 16:9 (cabeça/torso do personagem), redimensiona para
     mobile-friendly, exporta WebP (estático + loop animado) e uma folha de contato.

Saídas por missão (ex.: p1_01):
  - src/assets/anim/<id>/frames/ff_i.webp   (quadros isolados, otimizados)
  - src/assets/anim/<id>/loop.webp          (animação em loop — o que o card exibe)
  - src/assets/anim/<id>/contact.png        (folha de contato para revisão de arte)

Uso: python3 tools/build_animation_loop.py p1_01
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def load_frames(mission_id):
    d = Path(ROOT) / "src" / "assets" / "anim" / mission_id / "frames"
    names = sorted(p.name for p in d.glob("f*.png"))
    if not names:
        sys.exit(f"nenhum quadro PNG em {d}")
    return [Image.open(d / n).convert("RGB") for n in names], names


def crop169(im):
    w, h = im.size
    ratio = 16 / 9
    tw = w
    th = round(tw / ratio)
    if th > h:  # proteção p/ imagens mais baixas que 16:9
        th = h
        tw = round(th * ratio)
    top = (h - th) // 2
    left = (w - tw) // 2
    return im.crop((left, top, left + tw, top + th))


def consistency_score(imgs):
    """Média das diferenças entre quadros adjacentes (0..255). Baixa = mesmo
    cenário/personagem (bom); alta = o modelo redesenhou a cena (alerta)."""
    import statistics
    diffs = []
    small_a = imgs[0].resize((64, 64))
    for nxt in imgs[1:]:
        small_b = nxt.resize((64, 64))
        a = list(small_a.getdata())
        b = list(small_b.getdata())
        d = sum(abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])
                for x, y in zip(a, b)) / (3 * len(a))
        diffs.append(round(d, 2))
        small_a = small_b
    return diffs


def contact_sheet(imgs, cols=4, thumb_w=360):
    ratio = imgs[0].size[0] / imgs[0].size[1]
    thumb_h = round(thumb_w / ratio)
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (18, 24, 20))
    for i, im in enumerate(imgs):
        t = im.resize((thumb_w, thumb_h), Image.LANCZOS)
        x = (i % cols) * thumb_w
        y = (i // cols) * thumb_h
        sheet.paste(t, (x, y))
    return sheet


def main():
    mission_id = sys.argv[1] if len(sys.argv) > 1 else "p1_01"
    durations = [260, 180, 220, 420]  # ~1.08s: digita, pesa, digita, vitória
    d = Path(ROOT) / "src" / "assets" / "anim" / mission_id
    imgs, names = load_frames(mission_id)

    print(f"[{mission_id}] {len(imgs)} quadros → consistência adjacente:", consistency_score(imgs))

    W = 640
    frames = []
    for im in imgs:
        im2 = crop169(im).resize((W, round(W * 9 / 16)), Image.LANCZOS)
        frames.append(im2)

    # quadros isolados otimizados
    fdir = d / "frames"
    for i, (name, im) in enumerate(zip(names, frames)):
        im.save(fdir / f"ff_{i:02d}.webp", "WEBP", quality=82, method=6)

    # loop animado (o card exibe este)
    loop = d / "loop.webp"
    frames[0].save(loop, "WEBP", save_all=True, append_images=frames[1:],
                   duration=durations[: len(frames)], loop=0, quality=82, method=6)

    # poster estático (primeiro quadro) p/ estado "off" (não comprado)
    poster = d / "poster.webp"
    frames[0].save(poster, "WEBP", quality=85, method=6)

    # folha de contato p/ revisão de arte
    sheet = contact_sheet(frames)
    sheet.save(d / "contact.png")

    print(f"  loop → {loop.relative_to(ROOT)} ({loop.stat().st_size // 1024} KB)")
    print(f"  poster → {poster.name} ({poster.stat().st_size // 1024} KB)")
    print(f"  contact → {d.name}/contact.png")


if __name__ == "__main__":
    main()

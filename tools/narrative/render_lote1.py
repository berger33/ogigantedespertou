"""render_lote1.py — renderiza o Lote 1 (Religião) e publica os artefatos.

    python3 -m tools.narrative.render_lote1                 # as 10 missões
    python3 -m tools.narrative.render_lote1 p4_10 p4_08     # só algumas
    python3 -m tools.narrative.render_lote1 --no-spec       # não mexe na spec

Para cada missão grava:
  * src/assets/anim/<id>/frames/ff_XX.webp  (≥12 quadros, emenda fechada)
  * src/assets/anim/<id>/loop.webp          (loop.webp animado, duração por quadro)
  * src/assets/anim/<id>/contact.png        (folha de contato para conferência)

E no fim:
  * src/content/animations.json  → campos v2/frames/story/duration_ms (aditivos)
  * src/review/lote1.html        → página de revisão do lote (para o dono validar)
"""
from __future__ import annotations

import argparse
import json
import os

from . import kit as K
from . import lote1_religiao as L

SPEC = os.path.join(K.ROOT, "src", "content", "animations.json")
REVIEW = os.path.join(K.ROOT, "src", "review", "lote1.html")
LABELS = {
    "p4_01": "Gravar a mensagem invertida no vinil",
    "p4_02": "Exibir o desenho da indução espiritual",
    "p4_03": "Fábrica do boneco possuído",
    "p4_04": "Traçar a capital em sigilo geométrico",
    "p4_05": "Encenar o milagre ao vivo",
    "p4_06": "Mandar a imagem chorar xarope",
    "p4_07": "Gravar o 13º mandamento só no áudio",
    "p4_08": "Bendizer a água da torneira",
    "p4_09": "Empurrar o apocalipse (de novo)",
    "p4_10": "Projetar o arrebatamento holográfico",
}


def patch_spec(meta: dict) -> None:
    with open(SPEC, encoding="utf-8") as fh:
        data = json.load(fh)
    scenes = data["scenes"]
    for sid, info in meta.items():
        sc = scenes.get(sid)
        if sc is None:
            continue
        sc["v2"] = True                     # loops narrativos (multi-beat)
        sc["frames"] = info["frames"]       # ≥12, contado pelo teste de QA
        sc["story"] = info["story"]         # história legível para o dono/QA
        sc["duration_ms"] = info["ms"]
    with open(SPEC, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def write_review(meta: dict) -> None:
    os.makedirs(os.path.dirname(REVIEW), exist_ok=True)
    cards = []
    for sid in sorted(meta):
        info = meta[sid]
        cards.append(f"""    <figure class="card">
      <img src="../assets/anim/{sid}/loop.webp" alt="{sid} loop" loading="lazy">
      <figcaption>
        <b>{sid.upper()} · {LABELS.get(sid, '')}</b>
        <span>{info['frames']} quadros · {info['ms']} ms · consistência {info['cons']:.2f}</span>
        <p>{info['story']}</p>
        <a href="../assets/anim/{sid}/contact.png" target="_blank">folha de contato (quadro a quadro)</a>
      </figcaption>
    </figure>""")
    html = f"""<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<title>Lote 1 · Religião — loops narrativos</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root {{ color-scheme: dark }}
  body {{ margin:0; background:#0b0d12; color:#e8ecf4; font:15px/1.5 system-ui,sans-serif }}
  header {{ padding:24px 28px 8px }}
  h1 {{ margin:0 0 6px; font-size:22px }}
  header p {{ margin:0; color:#9fb0c8; max-width:820px }}
  main {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:18px; padding:20px 28px 40px }}
  .card {{ margin:0; background:#141824; border:1px solid #222c3d; border-radius:12px; overflow:hidden }}
  .card img {{ width:100%; display:block; background:#0b0d12 }}
  figcaption {{ padding:12px 14px 16px }}
  figcaption b {{ display:block; font-size:14px }}
  figcaption span {{ display:block; color:#8fa3bd; font-size:12px; margin:4px 0 8px }}
  figcaption p {{ margin:0 0 8px; color:#c8d4e6; font-size:13px }}
  figcaption a {{ color:#6fd0ff; font-size:12px; text-decoration:none }}
  .note {{ padding:0 28px 28px; color:#8fa3bd; font-size:13px }}
</style>
<header>
  <h1>Lote 1 · Religião — loops narrativos (animação v2)</h1>
  <p>As 10 missões do mapa Religião com loop de história fechado: setup → ação →
  resolução → reset. A pintura aprovada continua sendo a base; por cima dela
  entram só recortes, camadas animadas e FX no mesmo traço. As três referências
  do dono estão aqui: <b>p4_10</b> (arrebatamento), <b>p4_08</b> (água da torneira)
  e <b>p4_06</b> (chorar xarope).</p>
</header>
<main>
{chr(10).join(cards)}
</main>
<p class="note">Renderizado por <code>python3 -m tools.narrative.render_lote1</code>.
Compare cada loop com o quadro original em <code>poster.webp</code>: nada do desenho
aprovado foi redesenhado — só o que a mecânica exige foi adaptado localmente
(estação do bico no p4_08, interior do copo no p4_06, céu no p4_10).</p>
</html>
"""
    with open(REVIEW, "w", encoding="utf-8") as fh:
        fh.write(html)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="missões específicas (padrão: todo o lote)")
    ap.add_argument("--no-spec", action="store_true")
    ap.add_argument("--no-review", action="store_true")
    args = ap.parse_args()

    ids = args.ids or L.LOTE
    meta = {}
    for sid in ids:
        n, dur, story, frames = L.SCENES[sid]()
        cons = K.save_loop(sid, frames, dur)
        meta[sid] = {"frames": n, "ms": int(sum(dur)), "story": story, "cons": cons}
        print(f"{sid}: {n:2d} quadros · {sum(dur):4d} ms · consistência {cons:5.2f}")

    if not args.no_spec:
        patch_spec(meta)
        print(f"spec atualizada: {SPEC}")
    if not args.no_review and len(ids) >= 10:
        write_review(meta)
        print(f"página de revisão: {REVIEW}")


if __name__ == "__main__":
    main()

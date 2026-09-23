#!/usr/bin/env python3
"""
gen_upgrades.py — regenera `src/content/upgrades.json` (per-mission) e
`src/content/achievements.json` de forma data-driven, coerentes com
`src/content/producers.json` (ver tools/gen_campaign.py).

Melhoria por missão (§71):
  - 5 níveis ×3 cada; 1º nível ≈ ×4 o custo base da missão (âncora proporcional).
  - níveis internos na escada ×2000→×5000 da referência (estrelas).

Uso: python3 tools/gen_upgrades.py
"""
import json
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"
MAP_IDS = ["phase1", "phase2", "phase3", "phase4"]


def sig(x, n=4):
    """Arredonda para n dígitos significativos, limpo (Decimal), devolvendo int/float."""
    if x == 0:
        return 0
    with localcontext() as ctx:
        ctx.prec = 200
        d = Decimal(str(x))
        q = Decimal(1).scaleb(d.adjusted() - (n - 1))  # 10^(exp - (n-1))
        v = d.quantize(q, rounding=ROUND_HALF_UP)
    if v == v.to_integral_value():
        return int(v)
    return float(v)


def main():
    producers = json.load(open(CONTENT / "producers.json", encoding="utf-8"))
    upgrades = json.load(open(CONTENT / "upgrades.json", encoding="utf-8"))

    per = []
    for mid in MAP_IDS:
        for p in producers[mid]:
            base = float(p["baseCost"])
            l1 = sig(base * 4)
            per.append({
                "producer": p["id"], "name": p["name"],
                "costs": [sig(l1), sig(l1 * 2000), sig(l1 * 1e7),
                          sig(l1 * 5e10), sig(l1 * 2.5e14)],
                "mult": 3, "label": p["icon"],
            })
    upgrades["perProducer"] = per
    upgrades["_comment"] = (
        "Loja de Melhorias (spec §71). Uma melhoria ×3 POR MISSÃO (4 mapas × 10 = 40). "
        "1º nível ≈ ×4 o custo da missão (progressão fluida entre mapas); níveis internos "
        "seguem a escada ×2000→×5000 da referência (estrelas)."
    )
    # globais reescalonados para o teto da campanha (p4_10 ≈ 6.1e42)
    upgrades["global"][0]["cost"] = "1e22"
    upgrades["global"][1]["cost"] = "1e27"
    upgrades["global"][2]["cost"] = "1e32"
    upgrades["global"][1]["icon"] = "🧠"
    upgrades["global"][2]["icon"] = "🧠"
    for g in upgrades["global"]:
        g["label"] = g["label"].replace("toda a Deep Web", "todas as mentes")
    (CONTENT / "upgrades.json").write_text(
        json.dumps(upgrades, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ach = json.load(open(CONTENT / "achievements.json", encoding="utf-8"))
    for a in ach["list"]:
        a["desc"] = a.get("desc", "").replace("Crédulos", "mentes")
        if a["id"] == "ACH_million":
            a["icon"] = "🧠"
            a["desc"] = "Convença 1 milhão de mentes na vida."
    (CONTENT / "achievements.json").write_text(
        json.dumps(ach, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("upgrades per-missão:", len(per))
    print("  p1_01:", per[0]["costs"])
    print("  p4_10:", per[-1]["costs"])


if __name__ == "__main__":
    main()

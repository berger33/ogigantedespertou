#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/anim/promote.py — promove uma cena v4 aprovada ao jogo (pós Gate 2).

  * loop.webp v4  -> src/assets/anim/<id>/loop.webp
  * poster.webp   -> frame 0 do clip v4 em 640x360 (arte oficial do card)
  * frames/       -> substituídos pelos 8 quadros-chave v4
  * contact.png   -> contact sheet v4
  * animations.json -> entry com schema v4 (v4:true, duration_ms, fps_segments,
    frames, assets{ai,proc}, story, label no título WAI)
  * producers.json  -> name/flavor no tom WAI (§7 do plano)

Uso: python3 tools/anim/promote.py --meta src/assets/anim/p4_10/v4/meta.json
"""
from __future__ import annotations
import argparse
import json
import os
import shutil

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", ".."))


def promote(meta_path: str) -> dict:
    meta = json.load(open(meta_path))
    v4 = os.path.dirname(os.path.abspath(meta_path))
    scene = os.path.dirname(v4)
    sid = meta["id"]

    shutil.copy(os.path.join(v4, "loop.webp"), os.path.join(scene, "loop.webp"))
    shutil.copy(os.path.join(v4, "contact.png"), os.path.join(scene, "contact.png"))
    fdir = os.path.join(scene, "frames")
    if os.path.isdir(fdir):
        for f in os.listdir(fdir):
            if f.endswith((".webp", ".png")):
                os.remove(os.path.join(fdir, f))
    else:
        os.makedirs(fdir)
    for f in sorted(os.listdir(os.path.join(v4, "frames"))):
        shutil.copy(os.path.join(v4, "frames", f), os.path.join(fdir, f))

    # poster oficial = frame 0 do clip, 640x360 (card 320x88 @DPR2)
    plate = Image.open(os.path.join(v4, meta["plate"])).convert("RGB")
    plate.resize((640, 360), Image.LANCZOS).save(os.path.join(scene, "poster.webp"),
                                                 quality=88)

    # animations.json — schema v4
    apath = os.path.join(ROOT, "src", "content", "animations.json")
    aj = json.load(open(apath))
    e = aj["scenes"][sid]
    nai = sum(1 for a in meta.get("assets", []) if a["prov"] == "ai")
    npr = sum(1 for a in meta.get("assets", []) if a["prov"] == "proc")
    e.pop("v2", None)
    e.update(label=meta["title"].upper(), animated=True, v4=True,
             duration_ms=meta["duration_ms"],
             frames=meta.get("frames_planned", 60),
             fps_segments=meta["fps_segments"],
             assets={"ai": nai, "proc": npr},
             story=meta.get("story", e.get("story", "")),
             loops=sorted({t for b in meta.get("beats", [])
                           for t in b.get("tokens", [])}))
    json.dump(aj, open(apath, "w"), indent=1, ensure_ascii=False)

    # producers.json — título e fala no tom WAI
    ppath = os.path.join(ROOT, "src", "content", "producers.json")
    pj = json.load(open(ppath))
    hit = None
    for phase in pj.values():
        for item in phase:
            if item.get("id") == sid:
                hit = item
    if hit is not None:
        hit["name"] = meta["title"]
        hit["flavor"] = meta["flavor"]
    json.dump(pj, open(ppath, "w"), indent=1, ensure_ascii=False)

    return dict(scene=scene, loop_kb=round(os.path.getsize(
        os.path.join(scene, "loop.webp")) / 1024, 1), producer=hit is not None)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    a = ap.parse_args()
    print(json.dumps(promote(a.meta), ensure_ascii=False))

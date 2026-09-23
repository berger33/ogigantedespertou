import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';

// RESET v6 (pedido do dono): nenhuma missão animada — apenas o frame original
// (poster.webp) permanece em disco. O remake passa a ser por IA, missão a
// missão (docs/ANIM_V6_METODO_IA.md): missões com `v6:true` têm loop IA.

const ALL_IDS = [];
for (let m = 1; m <= 5; m++) for (let i = 1; i <= 10; i++) ALL_IDS.push(`p${m}_${String(i).padStart(2, '0')}`);

test('reset v6: spec na versão 6 cobre as 50 missões e resolve por id', () => {
  const cfg = loadConfig({});
  assert.equal(cfg.animations.version, 6);
  const s = new GameState(cfg);
  for (const id of ALL_IDS) {
    const sc = s.animationFor(id);
    assert.ok(sc, `${id} deve ter cena`);
    assert.match(sc.accent, /^#[0-9A-Fa-f]{6}$/, 'accent em hex');
    assert.equal(sc.animated, false, `${id}: reset — nenhuma animada fora do piloto IA`);
    assert.equal(s.animationFor('p9_99'), null);
  }
});

test('reset v6: as 50 missões têm o frame original (poster.webp RIFF válido) e nada de loop antigo', () => {
  for (const id of ALL_IDS) {
    const poster = new URL(`../src/assets/anim/${id}/poster.webp`, import.meta.url);
    assert.ok(fs.existsSync(poster), `${id}: poster.webp ausente`);
    const magic = fs.readFileSync(poster).subarray(0, 4);
    assert.ok(magic[0] === 0x52 && magic[1] === 0x49 && magic[2] === 0x46 && magic[3] === 0x46,
      `${id}: poster.webp não é RIFF/WebP`);
    assert.ok(!fs.existsSync(new URL(`../src/assets/anim/${id}/loop.webp`, import.meta.url)),
      `${id}: loop.webp antigo deveria ter sido removido no reset`);
  }
});

test('reset v6: nenhuma pasta de remake procedural sobrevive', () => {
  assert.ok(!fs.existsSync(new URL('../src/assets/anim/p4_10/v4/', import.meta.url)), 'v4 removida');
  assert.ok(!fs.existsSync(new URL('../src/assets/anim/p4_10/v5/', import.meta.url)), 'v5 removida');
  assert.ok(!fs.existsSync(new URL('../tools/anim/', import.meta.url)), 'tools/anim v4 removida');
});

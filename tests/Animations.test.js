import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';

// Spec v7 (docs/ANIM_V7_RIG.md): piloto p5_02 animado pelo RIG ESTRUTURAL
// (30 quadros @ 5 fps, 6 s, loop perfeito; fundo = poster imutável).
// As demais 49 missões permanecem só com o frame original (poster.webp).

const ALL_IDS = [];
for (let m = 1; m <= 5; m++) for (let i = 1; i <= 10; i++) ALL_IDS.push(`p${m}_${String(i).padStart(2, '0')}`);

test('spec v7: cobre as 50 missões; só o piloto p5_02 animado', () => {
  const cfg = loadConfig({});
  assert.equal(cfg.animations.version, 7);
  const s = new GameState(cfg);
  for (const id of ALL_IDS) {
    const sc = s.animationFor(id);
    assert.ok(sc, `${id} deve ter cena`);
    assert.match(sc.accent, /^#[0-9A-Fa-f]{6}$/, 'accent em hex');
    if (id === 'p5_02') {
      assert.equal(sc.animated, true, 'p5_02 é o piloto animado');
      assert.equal(sc.fps, 5);
      assert.equal(sc.frames, 30);
      assert.equal(sc.duration_ms, 6000);
      assert.equal(sc.loop_perfect, true);
      assert.match(sc.src, /v7\/loop\.webp$/);
    } else {
      assert.equal(sc.animated, false, `${id}: ainda sem animação`);
    }
  }
  assert.equal(s.animationFor('p9_99'), null);
});

test('spec v7: as 50 missões têm o frame original (poster.webp RIFF válido)', () => {
  for (const id of ALL_IDS) {
    const poster = new URL(`../src/assets/anim/${id}/poster.webp`, import.meta.url);
    assert.ok(fs.existsSync(poster), `${id}: poster.webp ausente`);
    const magic = fs.readFileSync(poster).subarray(0, 4);
    assert.ok(magic[0] === 0x52 && magic[1] === 0x49 && magic[2] === 0x46 && magic[3] === 0x46,
      `${id}: poster.webp não é RIFF/WebP`);
  }
});

test('spec v7: loop do piloto é WebP animado com 30 quadros @ 200 ms (RIFF/ANMF)', () => {
  const loop = new URL('../src/assets/anim/p5_02/v7/loop.webp', import.meta.url);
  const data = fs.readFileSync(loop);
  assert.equal(data.subarray(0, 4).toString('ascii'), 'RIFF');
  let i = 12, anmf = 0, durs = [];
  while (i + 8 <= data.length) {
    const fourcc = data.subarray(i, i + 4).toString('ascii');
    const size = data.readUInt32LE(i + 4);
    if (fourcc === 'ANMF') { anmf++; durs.push(data.readUIntLE(i + 8 + 12, 3)); }
    i += 8 + size + (size & 1);
  }
  assert.equal(anmf, 30, '30 quadros');
  assert.ok(durs.every((d) => d === 200), '200 ms por quadro (5 fps)');
});

test('spec v7: nenhum resquício do método v6 (re-desenho por IA) sobrevive', () => {
  assert.ok(!fs.existsSync(new URL('../src/assets/anim/p5_02/v6/', import.meta.url)), 'v6 removida');
  assert.ok(!fs.existsSync(new URL('../src/assets/anim/p4_10/v4/', import.meta.url)), 'v4 removida');
  assert.ok(!fs.existsSync(new URL('../src/assets/anim/p4_10/v5/', import.meta.url)), 'v5 removida');
  assert.ok(!fs.existsSync(new URL('../tools/anim/', import.meta.url)), 'tools/anim v4 removida');
  assert.ok(!fs.existsSync(new URL('../tools/animia/tween.py', import.meta.url)), 'tween v6 removido');
});

import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';

// Pipeline de animação (docs/ANIMATION_PLAN.md, spec v4): 50 missões em 5 mapas.
// Cenas `animated:true` = desenho 2D real (loop.webp flat-toon). Todas as 50
// cenas estão animadas (50/50 mestres pintados, Lote H fecha Singularidade).

const ALL_IDS = [];
for (let m = 1; m <= 5; m++) for (let i = 1; i <= 10; i++) ALL_IDS.push(`p${m}_${String(i).padStart(2, '0')}`);

test('animação: spec v4 cobre as 50 missões dos 5 mapas e resolve por id', () => {
  const cfg = loadConfig({});
  assert.equal(cfg.animations.version, 4);
  const s = new GameState(cfg);
  for (const id of ALL_IDS) {
    const sc = s.animationFor(id);
    assert.ok(sc, `${id} deve ter cena`);
    assert.match(sc.accent, /^#[0-9A-Fa-f]{6}$/, 'accent em hex');
    assert.ok(Array.isArray(sc.loops) && sc.loops.length > 0, 'loops declarados');
    assert.ok(sc.src, 'src declarado');
  }
  // id inexistente → null (fallback de ícone, nunca exceção)
  assert.equal(s.animationFor('p9_99'), null);
});

test('animação: os 5 mapas (50 cenas) 100% animadas em 2D', () => {
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  for (const id of ALL_IDS) {
    const sc = s.animationFor(id);
    assert.equal(sc.animated, true, `${id} deve estar no modo desenho 2D real`);
    assert.match(sc.src, /loop\.webp$/, `${id}: src deve apontar o loop`);
    assert.ok(sc.poster, `${id}: poster para estado off`);
  }
});

test('animação: loop.webp e poster.webp válidos em amostra de todos os 5 mapas', () => {
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  for (const id of ['p1_01', 'p1_02', 'p2_03', 'p3_06', 'p4_10', 'p5_04', 'p5_10']) {
    const sc = s.animationFor(id);
    assert.equal(sc.animated, true, `${id} deve estar no modo desenho 2D real`);
    const loop = new URL(`../src/${sc.src.replace(/^\//, '')}`, import.meta.url);
    const poster = new URL(`../src/${sc.poster.replace(/^\//, '')}`, import.meta.url);
    assert.ok(fs.existsSync(loop), `${id}: loop.webp deve existir`);
    assert.ok(fs.existsSync(poster), `${id}: poster.webp deve existir`);
    const magic = fs.readFileSync(loop).subarray(0, 4);
    assert.ok(magic[0] === 0x52 && magic[1] === 0x49 && magic[2] === 0x46 && magic[3] === 0x46,
      `${id}: loop.webp deve ser RIFF/WebP`);
  }
});

test('animação: todas as 50 cenas têm loop.webp + poster.webp no disco (RIFF/WebP)', () => {
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  for (const id of ALL_IDS) {
    const sc = s.animationFor(id);
    const loop = new URL(`../src/${sc.src.replace(/^\//, '')}`, import.meta.url);
    const poster = new URL(`../src/${sc.poster.replace(/^\//, '')}`, import.meta.url);
    assert.ok(fs.existsSync(loop), `${id}: loop.webp ausente`);
    assert.ok(fs.existsSync(poster), `${id}: poster.webp ausente`);
    const magic = fs.readFileSync(loop).subarray(0, 4);
    assert.ok(magic[0] === 0x52 && magic[1] === 0x49 && magic[2] === 0x46 && magic[3] === 0x46,
      `${id}: loop.webp não é RIFF/WebP`);
  }
});

test('animação: cada loop tem pelo menos 12 quadros (histórias podem ter mais)', () => {
  for (const id of ALL_IDS) {
    const dir = new URL(`../src/assets/anim/${id}/frames/`, import.meta.url);
    const files = fs.readdirSync(dir).filter((f) => /^ff_\d+\.webp$/.test(f));
    assert.ok(files.length >= 12, `${id}: esperava ≥12 quadros, veio ${files.length}`);
  }
});

test('animação: SVG de dossiê é rig articulada (partes com pivôs próprios), não uma caixa única', () => {
  // Regressão contra o bug do "uma imagem só balançando": o char precisa expor
  // tronco, braços esq/dir, pernas esq/dir e cabeça como grupos separados,
  // cada um com transform-origin inline (pivô de articulação em px do viewBox).
  // O gerador continua emitindo o dossiê SVG por cena (scene.svg) como arte
  // de referência/fallback — validamos direto no arquivo.
  for (const id of ALL_IDS) {
    const txt = fs.readFileSync(
      new URL(`../src/assets/anim/${id}/scene.svg`, import.meta.url), 'utf-8');
    for (const cls of ['class="root"', 'class="arm arm-l"', 'class="arm arm-r"',
                       'class="leg leg-l"', 'class="leg leg-r"', 'class="head"']) {
      assert.match(txt, new RegExp(cls.replace(/"/g, '\\"')), `${id}: falta ${cls}`);
    }
    assert.ok((txt.match(/transform-origin/g) || []).length >= 5,
      `${id}: esperava transform-origin nas articulações`);
  }
});

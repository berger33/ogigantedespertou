import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';

// Pipeline de animação (docs/ANIMATION_PLAN.md, Lote 0): cena invocável por missão
// com camadas bg/ator/fx dirigidas pelo spec `animations.json`.

test('animação: spec das cenas é data-driven e a cena p1_01 resolve', () => {
  const cfg = loadConfig({});
  assert.ok(cfg.animations, 'config deve carregar animations');
  assert.equal(cfg.animations.version, 1);
  assert.ok(Array.isArray(Object.keys(cfg.animations.scenes)));

  const s = new GameState(cfg);
  const scene = s.animationFor('p1_01');
  assert.ok(scene, 'p1_01 deve ter cena');
  assert.equal(scene.label, 'Comprar as maiores empresas com cripto');
  for (const layer of scene.layers) {
    assert.ok(layer.id, 'camada precisa de id');
    assert.ok(['pump', 'press', 'blink', 'scroll', 'rise'].includes(layer.loop), `loop válido (${layer.loop})`);
  }
  // missão sem cena ainda → null (fallback de ícone na UI, nunca exceção)
  assert.equal(s.animationFor('p2_05'), null);
});

test('animação: arquivo SVG referenciado existe e é autônomo', () => {
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  const scene = s.animationFor('p1_01');
  const rel = scene.src.replace(/^\//, '');
  const path = new URL(`../src/${rel}`, import.meta.url);
  assert.ok(fs.existsSync(path), `SVG deve existir: ${rel}`);
  const txt = fs.readFileSync(path, 'utf-8');
  assert.match(txt, /^\s*<svg/, 'deve ser SVG');
  for (const layer of scene.layers) {
    assert.ok(
      txt.includes(layer.id),
      `SVG deve conter a camada "${layer.id}"`
    );
  }
});

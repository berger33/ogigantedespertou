import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';

// Pipeline de animação (docs/ANIMATION_PLAN.md, v2): cada missão vira um
// "dossiê conspiratório" ilustrado — sala secreta + Grifter + objeto sob
// holofote + plaqueta (piada) + efeitos. Spec data-driven `animations.json`.

test('animação: spec v2 cobre as 10 missões da Deep Web e resolve por id', () => {
  const cfg = loadConfig({});
  assert.equal(cfg.animations.version, 2);
  const ids = ['p1_01', 'p1_02', 'p1_03', 'p1_04', 'p1_05', 'p1_06', 'p1_07', 'p1_08', 'p1_09', 'p1_10'];
  const s = new GameState(cfg);
  for (const id of ids) {
    const sc = s.animationFor(id);
    assert.ok(sc, `${id} deve ter cena`);
    assert.match(sc.accent, /^#[0-9A-Fa-f]{6}$/, 'accent em hex');
    assert.ok(Array.isArray(sc.loops) && sc.loops.length > 0, 'loops declarados');
  }
  // missão de outro mapa ainda sem cena → null (fallback de ícone, nunca exceção)
  assert.equal(s.animationFor('p2_05'), null);
});

test('animação: SVG referenciado existe, é bem-formado e contém a cena conspiratória', () => {
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  for (const id of ['p1_01', 'p1_05', 'p1_10']) {
    const sc = s.animationFor(id);
    const rel = sc.src.replace(/^\//, '');
    const p = new URL(`../src/${rel}`, import.meta.url);
    assert.ok(fs.existsSync(p), `SVG deve existir: ${rel}`);
    const txt = fs.readFileSync(p, 'utf-8');
    assert.match(txt, /^\s*<svg/, 'deve ser SVG');
    // elementos-chave do "dossiê": personagem, objeto, plaqueta e atmosfera
    assert.match(txt, /class="char"/, 'personagem O Grifter');
    assert.match(txt, /class="spot spot-/, 'objeto de cena sob holofote');
    assert.match(txt, /class="tag"/, 'plaqueta com a piada');
    assert.match(txt, /class="eye"/, 'olho vigiando (atmosfera)');
  }
});

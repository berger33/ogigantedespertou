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

test('animação: personagem é rig articulada (partes com pivôs próprios), não uma caixa única', () => {
  // Regressão contra o bug do "uma imagem só balançando": o char precisa expor
  // tronco, braços esq/dir, pernas esq/dir e cabeça como grupos separados,
  // cada um com transform-origin inline (pivô de articulação em px do viewBox).
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  for (const id of ['p1_01', 'p1_08', 'p1_09']) {
    const sc = s.animationFor(id);
    const rel = sc.src.replace(/^\//, '');
    const txt = fs.readFileSync(new URL(`../src/${rel}`, import.meta.url), 'utf-8');
    for (const cls of ['class="root"', 'class="arm arm-l"', 'class="arm arm-r"',
                       'class="leg leg-l"', 'class="leg leg-r"', 'class="head"']) {
      assert.match(txt, new RegExp(cls.replace(/"/g, '\\"')), `${id}: falta ${cls}`);
    }
    // pivôs de articulação presentes (transform-origin px em ombros/quadril/pescoço)
    assert.ok((txt.match(/transform-origin/g) || []).length >= 5,
      `${id}: esperava transform-origin nas articulações`);
  }
});

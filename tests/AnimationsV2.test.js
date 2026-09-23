import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';

// Animação v2 — loops narrativos (docs/ANIM_V2_PLANO_LOTES.md).
// Parte 1 = mapa Religião: as 10 missões saem do "movimento sutil" e passam a
// contar uma história com setup → ação → resolução → reset, em ≥12 quadros.

const LOTE1 = ['p4_01', 'p4_02', 'p4_03', 'p4_04', 'p4_05',
               'p4_06', 'p4_07', 'p4_08', 'p4_09', 'p4_10'];

test('animação v2: as 10 missões de Religião declaram história, quadros e duração', () => {
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  for (const id of LOTE1) {
    const sc = s.animationFor(id);
    assert.equal(sc.v2, true, `${id}: deve estar no pipeline de loops narrativos`);
    assert.ok(Number.isInteger(sc.frames) && sc.frames >= 12, `${id}: frames >= 12`);
    assert.ok(typeof sc.story === 'string' && sc.story.length > 40, `${id}: história legível na spec`);
    assert.ok(sc.duration_ms >= 1200 && sc.duration_ms <= 4000, `${id}: duração plausível`);
  }
});

test('animação v2: quadros no disco casam com a spec e a numeração é contínua', () => {
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  for (const id of LOTE1) {
    const sc = s.animationFor(id);
    const dir = new URL(`../src/assets/anim/${id}/frames/`, import.meta.url);
    const files = fs.readdirSync(dir).filter((f) => /^ff_\d+\.webp$/.test(f)).sort();
    assert.equal(files.length, sc.frames, `${id}: disco=${files.length} vs spec=${sc.frames}`);
    files.forEach((f, k) => {
      assert.equal(f, `ff_${String(k).padStart(2, '0')}.webp`, `${id}: numeração contínua a partir de zero`);
    });
    assert.ok(fs.existsSync(new URL(`../src/assets/anim/${id}/contact.png`, import.meta.url)),
      `${id}: folha de contato do lote`);
  }
});

test('animação v2: as três referências do dono contam o beat que ele pediu', () => {
  const cfg = loadConfig({});
  const s = new GameState(cfg);
  assert.match(s.animationFor('p4_10').story, /feixe/i);        // arrebatamento: luz acende
  assert.match(s.animationFor('p4_10').story, /botão/i);        // botão sem mão no quadro 1
  assert.match(s.animationFor('p4_08').story, /garrafa/i);      // torneira enche a garrafa
  assert.match(s.animationFor('p4_08').story, /auréola/i);      // adesivo santo
  assert.match(s.animationFor('p4_06').story, /xarope/i);       // o quadro chora xarope
  assert.match(s.animationFor('p4_06').story, /copo/i);         // gotas enchem o copo
});

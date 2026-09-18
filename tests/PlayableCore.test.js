import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';
import BigNumber from '../src/core/BigNumber.js';
import { serialize, deserialize } from '../src/core/Save.js';
import { prestige, convictosFrom } from '../src/core/Prestige.js';

// Fluxo horizontal do vertical slice: FTCZ (click → coletar → coordenador → sósia → zap → save/reload).

test('fluxo M1: clique → coleta manual → coordenador → sósia grátis → zap → save/reload', () => {
  const config = loadConfig({ maxProducers: 12 });
  let s = new GameState(config);

  // 100 toques
  let t = 0;
  for (let i = 0; i < 100; i++) { s.click(t); t += 100; }
  assert.equal(s.totalClicks, 100);

  // compra 1º produtor (custo 12)
  s.credits = BigNumber.fromString('1e3');
  assert.equal(s.buyProducer('p1_01', 1).ok, true);

  // coleta manual (cycleSeconds=1)
  s.tick(1000);
  const got = s.collect('p1_01');
  assert.ok(got.gt(BigNumber.zero()));

  // coordenador MGR_01
  s.credits = BigNumber.fromString('5000');
  assert.equal(s.buyManager('MGR_01').ok, true);
  assert.ok(s.productionPerSecond().gt(BigNumber.zero()));

  // sósia grátis
  const clone = s.openClone();
  assert.equal(clone.ok, true);
  assert.equal(clone.free, true);
  assert.equal(Object.keys(s.clones).length, 1);

  // zap — acertar um pró
  s.chumbo = 10;
  const pro = s.zapMessages().find((m) => m.pro === true);
  const zr = s.zapDecision(pro.id, true);
  assert.equal(zr.correct, true);

  // save/reload integridade
  const s2 = new GameState(config, deserialize(serialize(s)).data);
  assert.equal(s2.totalClicks, 100);
  assert.equal(s2.managers['MGR_01'], 1);
  assert.equal(Object.keys(s2.clones).length, 1);
  assert.equal(s2.zapStreak, 1);
  assert.equal(s2.credits.eq(s.credits), true);
});

test('conquistas declarativas avaliam sobre o estado', () => {
  const config = loadConfig({ maxProducers: 12 });
  const s = new GameState(config);
  s.buyProducer('p1_02', 1); // precisa de saldo? não — setamos direto
  s.producers['p1_02'] = 10;
  const achs = Object.fromEntries(s.evaluateAchievements().map((a) => [a.id, a.done]));
  assert.equal(achs.ACH_prod10, true);
  assert.equal(achs.ACH_first, false);
});

test('campanha por mapas: última missão destrava o próximo mapa', () => {
  const config = loadConfig({ maxProducers: 12 });
  const s = new GameState(config);
  assert.equal(s.activeMapId(), 'phase1');
  assert.equal(s.currentPhase().id, 'phase1');
  // compra a missão FINAL do Deep Web (p1_12) → avança para O País que Não Existe
  s.credits = BigNumber.fromString('1e13');
  const res = s.buyProducer('p1_12', 1);
  assert.equal(res.ok, true);
  assert.equal(res.advanced.moved, true);
  assert.equal(s.activeMapId(), 'phase2');
  assert.equal(s.currentPhase().name, 'O País que Não Existe');
  // mapas: P1 concluído, P2 liberado, P3 bloqueado até concluir P2
  assert.ok(s.completedMaps().includes('phase1'));
  assert.equal(s.isMapUnlocked('phase2'), true);
  assert.equal(s.isMapUnlocked('phase3'), false);
});

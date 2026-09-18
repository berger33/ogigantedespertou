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
  assert.equal(s.buyProducer('PRD_phase1_01', 1).ok, true);

  // coleta manual (cycleSeconds=1)
  s.tick(1000);
  const got = s.collect('PRD_phase1_01');
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
  s.buyProducer('PRD_phase1_02', 1); // precisa de saldo? não — setamos direto
  s.producers['PRD_phase1_02'] = 10;
  const achs = Object.fromEntries(s.evaluateAchievements().map((a) => [a.id, a.done]));
  assert.equal(achs.ACH_prod10, true);
  assert.equal(achs.ACH_first, false);
});

test('fases mapeiam lifetimeCredits', () => {
  const config = loadConfig({ maxProducers: 12 });
  const s = new GameState(config);
  assert.equal(s.currentPhase().id, 'P1');
  s.lifetimeCredits = BigNumber.fromString('1e21');
  assert.equal(s.currentPhase().id, 'P2');
});

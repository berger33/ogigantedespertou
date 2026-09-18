import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadConfig } from '../src/core/content.js';
import { GameState } from '../src/core/GameState.js';
import BigNumber from '../src/core/BigNumber.js';
import { serialize, deserialize } from '../src/core/Save.js';
import { convictosFrom } from '../src/core/Prestige.js';

// Fluxo de integração §202: tutorial → produtor → save/reload → prestige preview.
test('sessão FTUE: clicar → comprar produtor → produção → save/reload → preview de prestige', () => {
  const cfg = loadConfig({ maxProducers: 4 });
  let s = new GameState(cfg);

  // 60 toques (1 min de FTUE)
  let t = 0;
  for (let i = 0; i < 60; i++) { s.click(t); t += 100; }
  assert.equal(s.totalClicks, 60);

  // compra o 1º produtor (custo 15)
  assert.equal(s.buyProducer('PRD_phase1_01', 1).ok, true);
  assert.equal(s.producers['PRD_phase1_01'], 1);
  assert.ok(s.productionPerSecond().gt(BigNumber.zero()));

  // produção idle
  s.tick(60000);
  assert.ok(s.lifetimeCredits.gt(BigNumber.zero()));

  // save → reload (integridade)
  const str = serialize(s);
  const res = deserialize(str);
  assert.equal(res.ok, true);
  const s2 = new GameState(cfg, res.data);
  assert.equal(s2.credits.eq(s.credits), true);
  assert.equal(s2.producers['PRD_phase1_01'], 1);
  assert.equal(s2.totalClicks, 60);

  // prestige ainda abaixo do limiar (1e6) — retorna 0 sem reset
  assert.equal(convictosFrom(s2.lifetimeCredits, s2.prestigeParams(), s2.convictos), 0);
});

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';
import BigNumber from '../src/core/BigNumber.js';
import { serialize, deserialize } from '../src/core/Save.js';
import { convictosFrom } from '../src/core/Prestige.js';

// Fluxo de integração §202: tutorial → produtor → save/reload → preview de prestige.
test('sessão FTUE: clicar → comprar produtor → coleta manual → save/reload → preview de prestige', () => {
  const cfg = loadConfig({ maxProducers: 4 });
  let s = new GameState(cfg);

  // 60 toques (1 min de FTUE)
  let t = 0;
  for (let i = 0; i < 60; i++) { s.click(t); t += 100; }
  assert.equal(s.totalClicks, 60);

  // compra o 1º produtor (custo 12)
  assert.equal(s.buyProducer('p1_01', 1).ok, true);
  assert.equal(s.producers['p1_01'], 1);

  // ciclo acumula e é coletado manualmente (§41)
  s.tick(1100);
  const got = s.collect('p1_01');
  assert.ok(got.gt(BigNumber.zero()));
  assert.ok(s.lifetimeCredits.gt(BigNumber.zero()));

  // save → reload (integridade)
  const str = serialize(s);
  const res = deserialize(str);
  assert.equal(res.ok, true);
  const s2 = new GameState(cfg, res.data);
  assert.equal(s2.credits.eq(s.credits), true);
  assert.equal(s2.producers['p1_01'], 1);
  assert.equal(s2.totalClicks, 60);

  // prestige ainda abaixo do limiar (1e6) — retorna 0 sem reset
  assert.equal(convictosFrom(s2.lifetimeCredits, s2.prestigeParams(), s2.convictos), 0);
});

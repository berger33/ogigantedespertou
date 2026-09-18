import { test } from 'node:test';
import assert from 'node:assert/strict';
import { convictosFrom, globalBonus, prestige } from '../src/core/Prestige.js';
import BigNumber from '../src/core/BigNumber.js';
import { loadConfig } from '../src/core/content.js';
import { GameState } from '../src/core/GameState.js';

const P = { threshold: '1e6', exponent: 0.5, convictBonus: 0.03 };

test('convictosFrom: abaixo do limiar = 0', () => {
  assert.equal(convictosFrom(BigNumber.fromString('999999'), P), 0);
  assert.equal(convictosFrom(BigNumber.zero(), P), 0);
});

test('convictosFrom: no limiar = 1', () => {
  assert.equal(convictosFrom(BigNumber.fromString('1e6'), P), 1);
});

test('convictosFrom: segue floor((lifetime/limiar)^exp)', () => {
  // 1e8 / 1e6 = 100; 100^0.5 = 10
  assert.equal(convictosFrom(BigNumber.fromString('1e8'), P), 10);
  // 4e6 / 1e6 = 4; 4^0.5 = 2
  assert.equal(convictosFrom(BigNumber.fromString('4e6'), P), 2);
});

test('globalBonus: (1+taxa)^n', () => {
  const b = globalBonus(10, P);
  assert.ok(Math.abs(b.toNumber() - Math.pow(1.03, 10)) < 1e-9);
  assert.equal(globalBonus(0, P).toNumber(), 1);
});

test('prestige: reseta run e preserva total de Convictos', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  s.lifetimeCredits = BigNumber.fromString('1e8');
  s.producers['PRD_phase1_01'] = 20;
  s.clickLevel = 3;

  const res = prestige(s, P);
  assert.equal(res.ok, true);
  assert.equal(res.gained, 10);

  const snap = res.snapshot;
  assert.equal(snap.producers['PRD_phase1_01'] === undefined || snap.producers['PRD_phase1_01'] === 0, true);
  assert.equal(snap.clickLevel, 1);
  assert.equal(snap.convictos, 10);
  assert.equal(BigNumber.fromJSON(snap.credits).isZero(), true);
  assert.equal(BigNumber.fromJSON(snap.lifetimeCredits).isZero(), true);
});

test('prestige: não reseta abaixo do limiar', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  s.lifetimeCredits = BigNumber.fromString('1e3');
  const res = prestige(s, P);
  assert.equal(res.ok, false);
});

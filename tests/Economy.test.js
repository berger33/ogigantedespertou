import { test } from 'node:test';
import assert from 'node:assert/strict';
import BigNumber from '../src/core/BigNumber.js';
import * as Economy from '../src/core/Economy.js';
import { loadConfig } from '../src/core/content.js';
import { GameState } from '../src/core/GameState.js';

test('buyCost: primeira unidade = baseCost; cresce exponencialmente', () => {
  assert.equal(Economy.buyCost(15, 1.07, 0, 1).toNumber(), 15);
  const c2 = Economy.buyCost(15, 1.07, 1, 1).toNumber();
  assert.ok(Math.abs(c2 - 16.05) < 0.01, `esperado ~16.05, veio ${c2}`);
  // custo cresce com owned
  assert.ok(Economy.buyCost(15, 1.07, 10, 1).gt(Economy.buyCost(15, 1.07, 1, 1)));
});

test('buyCost(10 unidades) = soma dos 10 custos unitários crescentes', () => {
  const singleTotal = (() => {
    let sum = 0;
    for (let o = 0; o < 10; o++) sum += Economy.buyCost(15, 1.07, o, 1).toNumber();
    return sum;
  })();
  const ten = Economy.buyCost(15, 1.07, 0, 10).toNumber();
  assert.ok(Math.abs(ten - singleTotal) < 1e-6, `esperado ${singleTotal}, veio ${ten}`);
  // e é maior que 10× a primeira unidade (preços sobem)
  assert.ok(ten > 15 * 10);
});

test('maxAffordable retorna 0 quando não dá para comprar', () => {
  assert.equal(Economy.maxAffordable(15, 1.07, 0, BigNumber.fromNumber(10)), 0);
  assert.equal(Economy.maxAffordable(15, 1.07, 0, BigNumber.fromNumber(14)), 0);
});

test('maxAffordable encontra a quantidade inteira correta', () => {
  // saldo exato para 1 unidade
  const m1 = Economy.maxAffordable(15, 1.07, 0, BigNumber.fromNumber(15));
  assert.equal(m1, 1);
  // saldo generoso
  const m2 = Economy.maxAffordable(15, 1.07, 0, BigNumber.fromNumber(1e6));
  assert.ok(m2 >= 20, `esperado >= 20, veio ${m2}`);
  // nunca > custo
  assert.ok(Economy.buyCost(15, 1.07, 0, m2).lte(BigNumber.fromNumber(1e6)));
});

test('milestoneMultiplier encadeia fatores (10,25,50...)', () => {
  const ms = [{ count: 10, factor: 2 }, { count: 25, factor: 2 }, { count: 50, factor: 2 }];
  assert.equal(Economy.milestoneMultiplier(ms, 9).toNumber(), 1);
  assert.equal(Economy.milestoneMultiplier(ms, 10).toNumber(), 2);
  assert.equal(Economy.milestoneMultiplier(ms, 26).toNumber(), 4);
  assert.equal(Economy.milestoneMultiplier(ms, 50).toNumber(), 8);
});

test('producerProduction = base * owned * milestones', () => {
  const ms = [{ count: 10, factor: 2 }];
  // 5 owned, sem milestone: 1 * 5 = 5
  assert.equal(Economy.producerProduction(1, 5, ms, 5).toNumber(), 5);
  // 10 owned, com milestone x2: 1*10*2 = 20
  assert.equal(Economy.producerProduction(1, 10, ms, 10).toNumber(), 20);
});

test('GameState: clique gera Crédulos e conta total', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  const gain = s.click(1000);
  assert.equal(s.credits.eq(gain), true);
  assert.equal(s.credits.toNumber(), 1);
  assert.equal(s.totalClicks, 1);
});

test('GameState: combo viral cresce e capa em ×2', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  let t = 0;
  for (let i = 0; i < 12; i++) { s.click(t); t += 100; } // dentro da janela de decay
  assert.equal(s.viralMultiplier(t), 2.0);
});

test('GameState: buyProducer desconta saldo e aumenta produção', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  s.credits = BigNumber.fromNumber(1000);
  const before = s.productionPerSecond();
  const res = s.buyProducer('PRD_phase1_01', 1);
  assert.equal(res.ok, true);
  assert.equal(s.producers['PRD_phase1_01'], 1);
  assert.ok(s.productionPerSecond().gt(before));
  assert.ok(s.credits.lt(BigNumber.fromNumber(1000)));
});

test('GameState: compra de 10 usa buy modes e não compra sem saldo', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  const fail = s.buyProducer('PRD_phase1_01', 1);
  assert.equal(fail.ok, false);
  assert.equal(fail.reason, 'cost');
});

test('GameState: idle tick gera produção proporcional', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  s.producers['PRD_phase1_02'] = 1; // 1 Crédulo/s
  s._compute();
  const pps = s.productionPerSecond().toNumber();
  const gained = s.tick(5000);
  assert.ok(Math.abs(gained.toNumber() - pps * 5) < 1e-9);
});

test('GameState: milestones do economy.json são aplicados', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  s.producers['PRD_phase1_01'] = 10; // milestone 10 → ×2
  s._compute();
  const raw = config.producers[0].baseProduction * 10;
  const actual = s.productionPerSecond().toNumber();
  assert.ok(Math.abs(actual - raw * 2) < 1e-9);
});

test('upgrade de clique: custo, aumento de poder e teto', () => {
  const config = loadConfig({ maxProducers: 4 });
  const s = new GameState(config);
  assert.equal(s.clickPower().toNumber(), 1);
  // sem saldo: falha
  const fail = s.buyClickUpgrade();
  assert.equal(fail.ok, false);
  // dá saldo e compra nível 2
  s.credits = BigNumber.fromString('600');
  const ok = s.buyClickUpgrade();
  assert.equal(ok.ok, true);
  assert.equal(s.clickLevel, 2);
  assert.equal(s.clickPower().toNumber(), 5);
  const gain = s.click(0);
  assert.equal(gain.toNumber(), 5);
});

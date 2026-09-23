import { test } from 'node:test';
import assert from 'node:assert/strict';
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';
import BigNumber from '../src/core/BigNumber.js';
import { prestige, globalBonus } from '../src/core/Prestige.js';

const cfg = () => loadConfig({ maxProducers: 12 });

// ---------------- Coordenadores (automação, §38–§42) ----------------
test('Coordenador: automatiza e desbloqueia produção contínua', () => {
  const s = new GameState(cfg());
  s.credits = BigNumber.fromString('5000');
  assert.equal(s.buyProducer('p1_01', 1).ok, true);
  assert.equal(s.productionPerSecond().toNumber(), 0); // sem manager
  assert.equal(s.buyManager('MGR_01').ok, true);
  assert.ok(s.productionPerSecond().toNumber() > 0);
});

// ---------------- Upgrades por produtor e global ----------------
test('Upgrades: por produtor (×3) multiplicam produção', () => {
  const s = new GameState(cfg());
  s.credits = BigNumber.fromString('1e6');
  assert.equal(s.buyProducer('p1_01', 1).ok, true);
  s.managers['MGR_01'] = 1;
  s._compute();
  const base = s.productionPerSecond().toNumber();
  // upgrade por produtor slot 1 (custo 25000)
  assert.equal(s.buyProducerUpgrade(1).ok, true);
  assert.ok(Math.abs(s.productionPerSecond().toNumber() - base * 3) < 1e-6);
});

// ---------------- Sósias (clones, §43–§49) ----------------
test('Sósias: primeiro gratuito, duplicata vira Puxa-Saco', () => {
  const s = new GameState(cfg());
  s.credits = BigNumber.fromString('1e6');
  s.buyProducer('p1_01', 1);
  s.managers['MGR_01'] = 1;
  s._compute();
  // primeiro clone grátis
  const r1 = s.openClone();
  assert.equal(r1.ok, true);
  // compra chumbo e abre vários até duplicata → puxasacos
  s.chumbo = 100;
  let dupOrNew = 0;
  for (let i = 0; i < 80; i++) {
    const r = s.openClone();
    if (r.ok && r.duplicate) { dupOrNew += 1; break; }
  }
  assert.ok(dupOrNew >= 1, 'esperado pelo menos uma duplicata em 80 aberturas');
  assert.ok(s.puxasacos >= 1);
});

// ---------------- Zap Vazado (§50–§56) ----------------
test('Zap: acerto recompensa e erra zera streak', () => {
  const s = new GameState(cfg());
  const pro = s.zapMessages().find((m) => m.pro === true);
  const anti = s.zapMessages().find((m) => m.pro === false);
  const good = s.zapDecision(pro.id, true);
  assert.equal(good.ok, true);
  assert.equal(good.correct, true);
  assert.equal(s.zapStreak, 1);
  const bad = s.zapDecision(anti.id, true); // aprovar uma anti = errado
  assert.equal(bad.correct, false);
  assert.equal(s.zapStreak, 0);
  assert.ok(s.desconfianca > 0);
});

test('Zap: recompensa em Mentes soma ao saldo', () => {
  const s = new GameState(cfg());
  const before = s.credits;
  const pro = s.zapMessages().find((m) => m.pro === true);
  const res = s.zapDecision(pro.id, true);
  assert.equal(res.correct, true);
  assert.ok(s.credits.gt(before));
});

// ---------------- Prestígio preserva permanentes ----------------
test('Prestige: reseta run, preserva Chumbo, Sósias e Convictos', () => {
  const s = new GameState(cfg());
  s.lifetimeCredits = BigNumber.fromString('1e8');
  s.chumbo = 55;
  s.clones['p1_01'] = { rarity: 'common', name: 'Tio do Zap', mult: 5 };
  s.puxasacos = 7;
  const res = prestige(s, s.prestigeParams());
  assert.equal(res.ok, true);
  assert.equal(res.gained, 10);
  const snap = res.snapshot;
  assert.equal(snap.chumbo, 55);
  assert.equal(snap.puxasacos, 7);
  assert.equal(snap.clones['p1_01'].mult, 5);
  assert.equal(snap.convictos, 10);
  assert.equal(BigNumber.fromJSON(snap.credits).isZero(), true);
});

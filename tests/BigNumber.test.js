import { test } from 'node:test';
import assert from 'node:assert/strict';
import { BigNumber, MAX_EXP } from '../src/core/BigNumber.js';

test('construção e normalização', () => {
  assert.equal(new BigNumber(1500).m, 1.5);
  assert.equal(new BigNumber(1500).e, 3);
  assert.equal(new BigNumber(0.0005).e, -4);
  assert.equal(BigNumber.zero().format(), '0');
  assert.equal(BigNumber.fromNumber(0).isZero(), true);
});

test('ops básicas: add/mul/div/pow', () => {
  const a = BigNumber.fromNumber(2);
  const b = BigNumber.fromNumber(3);
  assert.equal(a.add(b).toNumber(), 5);
  assert.equal(BigNumber.fromNumber(1.5e6).add(BigNumber.fromNumber(1e6)).toNumber(), 2.5e6);

  const big = new BigNumber(1, 40);
  const small = new BigNumber(1, 10);
  assert.equal(big.add(small), big); // desprezível
  assert.equal(big.mul(small).e, 50);
  assert.equal(big.div(small).e, 30);
  assert.equal(BigNumber.fromNumber(2).pow(10).eq(BigNumber.fromNumber(1024)), true);
  assert.equal(BigNumber.fromNumber(3).pow(0).toNumber(), 1);
});

test('cmp / igualdade / sinal', () => {
  assert.equal(BigNumber.fromNumber(1.5e6).cmp(BigNumber.fromNumber(2e6)), -1);
  assert.equal(BigNumber.fromNumber(2e6).cmp(BigNumber.fromNumber(1.5e6)), 1);
  assert.equal(new BigNumber(3).cmp(new BigNumber(3)), 0);
  assert.equal(new BigNumber(-5).cmp(new BigNumber(1)), -1);
  assert.equal(new BigNumber(-5).cmp(new BigNumber(-2)), -1);
  assert.equal(new BigNumber(-2).cmp(new BigNumber(-5)), 1);
});

test('overflow silencioso é proibido', () => {
  assert.throws(() => new BigNumber(1, MAX_EXP + 1));
  assert.throws(() => new BigNumber(1).div(BigNumber.zero()));
  assert.throws(() => new BigNumber(2).pow(-1));
  assert.throws(() => BigNumber.fromNumber(NaN));
  assert.throws(() => BigNumber.fromString('abc'));
});

test('fromString aceita padrões BR', () => {
  assert.equal(BigNumber.fromString('1500').toNumber(), 1500);
  assert.equal(BigNumber.fromString('1,5').toNumber(), 1.5);
  assert.equal(BigNumber.fromString('1.5').toNumber(), 1.5);
  assert.equal(BigNumber.fromString('1.500').toNumber(), 1500);
  assert.equal(BigNumber.fromString('1,5e6').toNumber(), 1.5e6);
  assert.equal(BigNumber.fromString('0').isZero(), true);
});

test('formatação: full / short / scientific', () => {
  const n = (v) => new BigNumber(v, 0);
  assert.equal(n(1500).format('full'), '1,5 mil');
  assert.equal(n(1e6).format('full'), '1 milhão');
  assert.equal(n(2e6).format('full'), '2 milhões');
  assert.equal(n(2.5e9).format('full'), '2,5 bilhões');
  assert.equal(n(1e12).format('full'), '1 trilhão');
  assert.equal(n(4200).format('short'), '4,2 mil');
  assert.equal(n(1e6).format('short'), '1 M');
  assert.equal(n(2.5e9).format('short'), '2,5 B');
  assert.equal(n(1e12).format('short'), '1 T');
  assert.equal(new BigNumber(3.7, 15).format('short'), '3,7 Qa');
  assert.equal(n(4200).format('scientific'), '4,2e3');
  assert.equal(n(999).format(), '999');
  assert.equal(n(12345).format(), '12,35 mil');
});

test('números gigantes não estouram e formatam cientificamente', () => {
  // 10^120 (muito acima da faixa nomeada)
  const huge = new BigNumber(1, 120);
  assert.equal(huge.format('scientific'), '1e120');
  assert.equal(huge.log10(), 120);
  const product = new BigNumber(2, 60).mul(new BigNumber(3, 60));
  assert.equal(product.e, 120);
  assert.ok(product.e < MAX_EXP);
});

test('toJSON round-trip', () => {
  const a = new BigNumber(3.14159, 33);
  const b = BigNumber.fromJSON(JSON.parse(JSON.stringify(a)));
  assert.equal(a.eq(b), true);
  assert.equal(a.format(), b.format());
});

test('floor/ceil', () => {
  const v = new BigNumber(1.7, 3); // 1700
  assert.equal(v.floor().toNumber(), 1700);
  assert.equal(v.ceil().toNumber(), 1700);
  const f = new BigNumber(1.234, 1); // 12.34
  assert.equal(f.floor().toNumber(), 12);
  assert.equal(f.ceil().toNumber(), 13);
  assert.equal(BigNumber.zero().floor().isZero(), true);
});

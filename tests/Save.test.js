import { test } from 'node:test';
import assert from 'node:assert/strict';
import { serialize, deserialize, recover, hydrate, hash32, SAVE_VERSION } from '../src/core/Save.js';
import { GameState } from '../src/core/GameState.js';
import { loadConfig } from '../src/core/content.node.js';
import BigNumber from '../src/core/BigNumber.js';

function makeState() {
  const s = new GameState(loadConfig({ maxProducers: 4 }));
  s.credits = BigNumber.fromString('1.5e9');
  s.producers['PRD_phase1_02'] = 7;
  s.clickLevel = 3;
  s.totalClicks = 42;
  return s;
}

test('serialize/deserialize: round-trip completo', () => {
  const s = makeState();
  const str = serialize(s);
  const res = deserialize(str);
  assert.equal(res.ok, true);
  const s2 = hydrate(res.data, loadConfig({ maxProducers: 4 }));
  assert.equal(s2.credits.eq(s.credits), true);
  assert.equal(s2.producers['PRD_phase1_02'], 7);
  assert.equal(s2.clickLevel, 3);
  assert.equal(s2.totalClicks, 42);
});

test('detecta corrupção via hash (§172)', () => {
  const str = serialize(makeState());
  const tampered = str.replace('PRD_phase1_02', 'PRD_phaseX_99') + 'x';
  const res = deserialize(tampered);
  assert.equal(res.ok, false);
});

test('recover: usa backup se o primário estiver corrompido', () => {
  const good = serialize(makeState());
  const bad = '###corrompido###';
  const res = recover(bad, [bad.slice(0, 20), good]);
  assert.equal(res.ok, true);
  assert.equal(res.source, 'backup2');
});

test('recover: todos inválidos → erro explícito', () => {
  const res = recover('', ['', '']);
  assert.equal(res.ok, false);
  assert.equal(res.error, 'no-valid-save');
});

test('save tem versão e hash', () => {
  const str = serialize(makeState());
  assert.ok(str.includes(`"version":${SAVE_VERSION}`));
  assert.ok(/\n#[0-9a-f]{8}$/.test(str));
});

test('hash32 é determinístico', () => {
  assert.equal(hash32('abc'), hash32('abc'));
  assert.notEqual(hash32('abc'), hash32('abd'));
});

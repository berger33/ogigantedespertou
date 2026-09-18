/**
 * Save — serialização, versionamento/migração e proteção contra corrupção
 * (spec §170–§174, §301–§302). Engine-agnóstico.
 *
 * - `serialize(state)`   → string JSON { schema, version, data, hash }
 * - `deserialize(str)`   → { ok, data } | { ok:false, error }
 * - `recover(primary, backups)` → melhor snapshot válido (rollback §172)
 */
import GameState from './GameState.js';

export const SAVE_VERSION = 1;

/** Hash FNV-1a 32 bits — checagem de integridade (não é criptografia). */
export function hash32(str) {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(16).padStart(8, '0');
}

/** Migrações de schemas antigos. vN -> vN+1. (spec §174) */
const migrations = {
  // 0 -> 1 (exemplo; versão 0 era pré-versionamento, sem hash)
  0: (data) => ({ ...data, version: 1 }),
};

export function migrate(data) {
  let d = data;
  let v = d.version ?? 0;
  while (v < SAVE_VERSION) {
    const step = migrations[v];
    if (!step) throw new Error(`Save: sem migração de v${v} para v${v + 1}`);
    d = step(d);
    v = d.version;
  }
  return d;
}

export function serialize(state) {
  const data = state.toSnapshot();
  const body = JSON.stringify({ schema: 'ogigante', version: SAVE_VERSION, data });
  return body + '\n#' + hash32(body);
}

export function deserialize(str) {
  try {
    const raw = String(str);
    const idx = raw.lastIndexOf('\n#');
    const body = idx >= 0 ? raw.slice(0, idx) : raw;
    const expectedHash = idx >= 0 ? raw.slice(idx + 2).trim() : null;
    if (expectedHash && hash32(body) !== expectedHash) {
      return { ok: false, error: 'corrupt' };
    }
    const parsed = JSON.parse(body);
    if (parsed.schema !== 'ogigante') return { ok: false, error: 'schema' };
    const data = migrate(parsed.data);
    return { ok: true, data };
  } catch (e) {
    return { ok: false, error: e.message || 'parse' };
  }
}

/** Retorna o primeiro snapshot válido, tentando primário e backups (§172). */
export function recover(primary, backups = []) {
  for (const [label, str] of [['primary', primary], ...backups.map((b, i) => [`backup${i + 1}`, b])]) {
    if (!str) continue;
    const res = deserialize(str);
    if (res.ok) return { ...res, source: label };
  }
  return { ok: false, error: 'no-valid-save' };
}

/** Reconstrói um GameState a partir de snapshot validado. */
export function hydrate(snapshot, config) {
  return new GameState(config, snapshot);
}

export default { SAVE_VERSION, hash32, serialize, deserialize, migrate, recover, hydrate };

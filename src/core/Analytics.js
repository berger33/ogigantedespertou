/**
 * Analytics — taxonomia de eventos (spec §175–§177).
 * Camada engine-agnóstica: no núcleo web é um stub console; na produção, a
 * mesma API é implementada por Firebase Analytics. Nunca envia PII (§178).
 */
const SESSION_ID = 'local-' + Math.random().toString(36).slice(2, 10);
const queue = [];

export const Analytics = {
  /** @param {string} event @param {object} [params] */
  track(event, params = {}) {
    const entry = { ts: Date.now(), session: SESSION_ID, event, params };
    if (typeof console !== 'undefined') console.debug('[analytics]', event, params);
    // buffer curto para inspeção/depuração (sem PII)
    queue.push(entry);
    if (queue.length > 500) queue.shift();
  },

  /** Snapshot do buffer (suporte/diagnóstico interno, §286). */
  dump() {
    return queue.slice();
  },
};

export default Analytics;

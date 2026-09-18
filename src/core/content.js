/**
 * content — loader data-driven (spec §14).
 * - `makeConfig(...)`: agrega JSONs crus → config do GameState (puro, roda em qualquer ambiente).
 * - `loadConfigWeb(opts)`: usado no NAVEGADOR (fetch) — não depende de import attributes.
 *
 * O loader com `import ... with { type: 'json' }` (Node/tests) vive em
 * `content.node.js` — sintaxe não suportada universalmente em browsers.
 */
export function makeConfig({ economy, producers, clicks, phase = 1, maxProducers = null } = {}) {
  const all = (producers && producers.phase1) || [];
  const list = maxProducers != null ? all.slice(0, maxProducers) : all;
  return {
    economy: {
      ...economy,
      producerList: list,
    },
    producers: list,
    clicks: clicks || { levels: [] },
    phase,
  };
}

/** Navegador: busca os JSONs (funciona em qualquer servidor estático). */
export async function loadConfigWeb(opts = {}) {
  const [economy, producers, clicks] = await Promise.all([
    fetch('content/economy.json').then((r) => {
      if (!r.ok) throw new Error(`economy.json HTTP ${r.status}`);
      return r.json();
    }),
    fetch('content/producers.json').then((r) => {
      if (!r.ok) throw new Error(`producers.json HTTP ${r.status}`);
      return r.json();
    }),
    fetch('content/clicks.json').then((r) => {
      if (!r.ok) throw new Error(`clicks.json HTTP ${r.status}`);
      return r.json();
    }),
  ]);
  return makeConfig({ economy, producers, clicks, ...opts });
}

export default { makeConfig, loadConfigWeb };

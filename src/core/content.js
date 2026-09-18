/**
 * content — loader data-driven (spec §14).
 * - `makeConfig(...)`: agrega JSONs crus → config do GameState (puro, testável).
 * - `loadNode()`: para Node/testes (import assertions).
 * - `loadWeb()`: para o navegador (fetch), sem dependência de import attributes.
 */
import economyJson from '../content/economy.json' with { type: 'json' };
import producersJson from '../content/producers.json' with { type: 'json' };
import clicksJson from '../content/clicks.json' with { type: 'json' };

export function makeConfig({ economy, producers, clicks, phase = 1, maxProducers = null } = {}) {
  const all = (producers && producers.phase1) || [];
  const list = maxProducers != null ? all.slice(0, maxProducers) : all;
  return {
    economy: {
      ...economy,
      producerList: list,
    },
    producers: list,
    clicks,
    phase,
  };
}

/** Node/tests: dados embutidos via import attributes. */
export function loadConfig(opts = {}) {
  return makeConfig({ economy: economyJson, producers: producersJson, clicks: clicksJson, ...opts });
}

/** Navegador: busca os JSONs (funciona em qualquer servidor estático). */
export async function loadConfigWeb(opts = {}) {
  const [economy, producers, clicks] = await Promise.all([
    fetch('content/economy.json').then((r) => r.json()),
    fetch('content/producers.json').then((r) => r.json()),
    fetch('content/clicks.json').then((r) => r.json()),
  ]);
  return makeConfig({ economy, producers, clicks, ...opts });
}

export default { makeConfig, loadConfig, loadConfigWeb };

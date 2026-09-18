/**
 * content — loader data-driven (spec §14).
 * - `makeConfig(...)`: agrega JSONs crus → config do GameState (puro).
 * - `loadConfigWeb(opts)`: NAVEGADOR (fetch) — sem import attributes.
 *
 * Loader Node (import attributes) vive em `content.node.js`.
 */
export function makeConfig({ economy, producers, clicks, managers, upgrades, clones, zaps, achievements, phases, phase = 1, maxProducers = null } = {}) {
  const all = (producers && producers.phase1) || [];
  const list = maxProducers != null ? all.slice(0, maxProducers) : all;
  return {
    economy: { ...economy, producerList: list },
    producers: list,
    clicks: clicks || { levels: [] },
    managers: managers || { managers: [], buyAllManager: {} },
    upgrades: upgrades || { perProducer: [], global: [] },
    clones: clones || { cost: 15, rarities: [], catalog: [] },
    zaps: zaps || { rewards: {}, messages: [] },
    achievements: achievements || { list: [] },
    phases: phases || { phases: [] },
    phase,
  };
}

/** Navegador: busca os JSONs (qualquer servidor estático). */
export async function loadConfigWeb(opts = {}) {
  const names = ['economy', 'producers', 'clicks', 'managers', 'upgrades', 'clones', 'zaps', 'achievements', 'phases'];
  const data = {};
  await Promise.all(names.map(async (n) => {
    const r = await fetch(`content/${n}.json`);
    if (!r.ok) throw new Error(`${n}.json HTTP ${r.status}`);
    data[n] = await r.json();
  }));
  return makeConfig({
    economy: data.economy,
    producers: data.producers,
    clicks: data.clicks,
    managers: data.managers,
    upgrades: data.upgrades,
    clones: data.clones,
    zaps: data.zaps,
    achievements: data.achievements,
    phases: data.phases,
    ...opts,
  });
}

export default { makeConfig, loadConfigWeb };

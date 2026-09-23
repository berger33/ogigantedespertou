/**
 * content — loader data-driven (spec §14).
 * - `makeConfig(...)`: agrega JSONs crus → config do GameState (puro).
 * - `loadConfigWeb(opts)`: NAVEGADOR (fetch) — sem import attributes.
 *
 * Campanha por mapas: producers/{manager,clones}.json contêm N mapas
 * (p.ex. phase1, phase2...). makeConfig recebe `mapId` e o limite de
 * missões por mapa (`maxProducers`).
 *
 * Loader Node (import attributes) vive em `content.node.js`.
 */
export function makeConfig({
  economy, producers, clicks, managers, upgrades, clones, zaps, achievements, maps,
  animations = null,
  mapId = 'phase1', maxProducers = null,
} = {}) {
  // pool: todos os mapas num array plano; producerList = mapa ativo
  const byMap = {};
  if (producers) {
    for (const key of Object.keys(producers)) {
      if (Array.isArray(producers[key])) byMap[key] = producers[key];
    }
  }
  const allMaps = Object.keys(byMap);
  const active = byMap[mapId] || [];
  const list = maxProducers ? active.slice(0, maxProducers) : active; // 0/null = todas
  return {
    economy: { ...economy, producerList: list },
    producers: list,                    // mapa ativo
    producerMaps: byMap,                // { mapId: [produtores] }
    producerMapIds: allMaps,
    mapId,
    clicks: clicks || { levels: [] },
    managers: managers || { managers: [], buyAllManager: {} },
    upgrades: upgrades || { perProducer: [], global: [] },
    clones: clones || { cost: 15, rarities: [], catalog: [] },
    zaps: zaps || { rewards: {}, messages: [] },
    achievements: achievements || { list: [] },
    maps: maps || { maps: [] },
    animations: animations || { scenes: {} },
  };
}

/** Navegador: busca os JSONs (qualquer servidor estático). */
export async function loadConfigWeb(opts = {}) {
  const names = ['economy', 'producers', 'clicks', 'managers', 'upgrades', 'clones', 'zaps', 'achievements', 'maps', 'animations'];
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
    maps: data.maps,
    animations: data.animations,
    ...opts,
  });
}

export default { makeConfig, loadConfigWeb };

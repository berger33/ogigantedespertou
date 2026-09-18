/**
 * content — loader data-driven (spec §14).
 * Agrega os JSONs de conteúdo + envia apenas os 4 primeiros produtores
 * no PLAYABLE CORE (§246–§247); o vertical slice usa os 12 (§31).
 */
import economyJson from '../content/economy.json' with { type: 'json' };
import producersJson from '../content/producers.json' with { type: 'json' };
import clicksJson from '../content/clicks.json' with { type: 'json' };

export function loadConfig({ phase = 1, maxProducers = null } = {}) {
  const all = producersJson.phase1 || [];
  const producers = maxProducers != null ? all.slice(0, maxProducers) : all;
  return {
    economy: {
      ...economyJson,
      producerList: producers,
    },
    producers,
    clicks: clicksJson,
    phase,
  };
}

export default { loadConfig };

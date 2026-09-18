/**
 * content.node — loader para Node/testes via import attributes.
 * NÃO use no navegador (use loadConfigWeb de ./content.js).
 */
import economyJson from '../content/economy.json' with { type: 'json' };
import producersJson from '../content/producers.json' with { type: 'json' };
import clicksJson from '../content/clicks.json' with { type: 'json' };
import managersJson from '../content/managers.json' with { type: 'json' };
import upgradesJson from '../content/upgrades.json' with { type: 'json' };
import clonesJson from '../content/clones.json' with { type: 'json' };
import zapsJson from '../content/zaps.json' with { type: 'json' };
import achievementsJson from '../content/achievements.json' with { type: 'json' };
import phasesJson from '../content/phases.json' with { type: 'json' };
import { makeConfig } from './content.js';

export function loadConfig(opts = {}) {
  return makeConfig({
    economy: economyJson,
    producers: producersJson,
    clicks: clicksJson,
    managers: managersJson,
    upgrades: upgradesJson,
    clones: clonesJson,
    zaps: zapsJson,
    achievements: achievementsJson,
    phases: phasesJson,
    ...opts,
  });
}

export default { loadConfig };

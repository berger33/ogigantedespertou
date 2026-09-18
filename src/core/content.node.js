/**
 * content.node — loader para Node/testes via import attributes
 * (`with { type: 'json' }`). NÃO use no navegador: use `loadConfigWeb`
 * de `./content.js`.
 */
import economyJson from '../content/economy.json' with { type: 'json' };
import producersJson from '../content/producers.json' with { type: 'json' };
import clicksJson from '../content/clicks.json' with { type: 'json' };
import { makeConfig } from './content.js';

export function loadConfig(opts = {}) {
  return makeConfig({ economy: economyJson, producers: producersJson, clicks: clicksJson, ...opts });
}

export default { loadConfig };

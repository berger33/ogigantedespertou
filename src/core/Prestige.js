/**
 * Prestige — "Despertar o Gigante" (spec §57–§63).
 * Engine-agnóstico. Fórmula e bônus por Convicto.
 */
import BigNumber from './BigNumber.js';

/**
 * Convictos ganhos no reset (§59).
 *   Convictos = floor((LifetimeCrédulos / Limiar)^Expoente)
 */
export function convictosFrom(lifetime, p) {
  const threshold = BigNumber.fromString(String(p.threshold));
  const exponent = Number(p.exponent ?? 0.5);
  if (lifetime.lt(threshold)) return 0;
  const ratio = lifetime.div(threshold);
  // ratio^exponent com expoente real: m^e * 10^(exp*e)
  const me = Math.pow(ratio.m, exponent);
  const ee = Math.round(ratio.e * exponent);
  return Math.max(0, Math.floor(new BigNumber(me, ee).toNumberSafe() ?? 0));
}

/** Bônus global multiplicativo por Convicto (§60): (1+taxa)^n. */
export function globalBonus(convictos, p) {
  const taxa = Number(p.convictBonus ?? 0.03);
  return new BigNumber(Math.pow(1 + taxa, convictos), 0);
}

/**
 * Aplica o reset em um snapshot de estado (não muta o original).
 * Retorna { snapshot, convictosGained }.
 */
export function prestige(state, p) {
  const gained = convictosFrom(state.lifetimeCredits, p);
  if (gained <= 0) return { ok: false, reason: 'below-threshold', gained: 0 };
  const snap = state.toSnapshot();
  // reset de run (§57): zera créditos correntes e produtores; volta à fase 1
  snap.credits = BigNumber.zero().toJSON();
  snap.producers = {};
  snap.clickLevel = 1;
  snap.timestamp = Date.now();
  // lifetime é preservado? Não: recomeça a contagem DESTA run.
  // O total histórico para a próxima rodada parte do zero (padrão do gênero).
  snap.lifetimeCredits = BigNumber.zero().toJSON();
  snap.convictos = (snap.convictos || 0) + gained;
  return { ok: true, snapshot: snap, gained };
}

export default { convictosFrom, globalBonus, prestige };

/**
 * Prestige — "Despertar o Gigante" (spec §57–§63).
 * Engine-agnóstico. Fórmula e bônus por Convicto.
 *
 * MODELO (validado pelo simulador, §60):
 *  - Convictos = floor((LifetimeMentes / Limiar)^Expoente), expoente < 1.
 *  - Bônus global LINEAR ADITIVO: 1 + taxa(3%) × Convictos.
 *    (A leitura fiel de §60 é "+3% POR Convicto" = soma 3% por ponto.)
 *  - Um bônus EXPONENCIAL (1+taxa)^Convictos gera crescimento iterado
 *    super-exponencial (runaway) — detectado e rejeitado pelo simulador (§60:
 *    não permitir runaway impossível de balancear).
 */
import BigNumber from './BigNumber.js';

/**
 * Convictos ganhos no reset (§59).
 *   Convictos = floor((Lifetime / Limiar)^Expoente)
 */
export function convictosFrom(lifetime, p, currentConvictos = 0) {
  void currentConvictos;
  const base = BigNumber.fromString(String(p.threshold));
  const exponent = Number(p.exponent ?? 0.5);
  if (lifetime.lt(base)) return 0;
  const ratio = lifetime.div(base);
  // Convictos = floor(ratio^exponent), em espaço logarítmico estável
  const logResult = ratio.log10() * exponent; // log10(ratio^e)
  const value = Math.pow(10, logResult);
  if (!Number.isFinite(value)) {
    // valor gigante: compõe por mantissa/expoente
    const e = Math.floor(logResult);
    const m = Math.pow(10, logResult - e);
    return Math.floor(m) * Math.pow(10, e);
  }
  return Math.floor(value);
}

/** Bônus global por Convicto (§60): 1 + taxa × Convictos (linear aditivo). */
export function globalBonus(convictos, p) {
  const taxa = Number(p.convictBonus ?? 0.03);
  if (!Number.isFinite(taxa) || taxa < 0) throw new Error('Prestige: convictBonus inválido');
  return BigNumber.one().add(BigNumber.fromNumber(taxa * Math.max(0, Math.floor(convictos))));
}

/**
 * Aplica o reset em um snapshot de estado (não muta o original).
 * Retorna { ok, snapshot, gained }.
 */
export function prestige(state, p) {
  const gained = convictosFrom(state.lifetimeCredits, p, state.convictos || 0);
  if (gained <= 0) return { ok: false, reason: 'below-threshold', gained: 0 };
  const snap = state.toSnapshot();
  // reset de run (§57): zera a run; preserva o que é permanente (§58/§47/§60)
  snap.credits = BigNumber.zero().toJSON();
  snap.producers = {};
  snap.collectables = {};
  snap.cycleAccum = {};
  snap.managers = {};
  snap.upgrades = {};
  snap.clickLevel = 1;
  snap.timestamp = Date.now();
  snap.lifetimeCredits = BigNumber.zero().toJSON(); // recomeça DESTA run
  snap.convictos = (snap.convictos || 0) + gained;
  // preserva: chumbo, clones(Sósias), puxasacos, zapStreak? (streak zera)
  snap.zapStreak = 0;
  return { ok: true, snapshot: snap, gained };
}

export default { convictosFrom, globalBonus, prestige };

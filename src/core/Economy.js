/**
 * Economy — custos, produção, buy modes e milestones (spec §27–§30, §76–§77).
 * Engine-agnóstico. API pública espelhada em `unity/Economy.cs`.
 */
import BigNumber from './BigNumber.js';

export const BUY_MODES = [1, 10, 25, 100, -1]; // -1 = MAX

/** Custo de comprar `qty` unidades do produtor, já possuindo `owned`. */
export function buyCost(baseCost, growthRate, owned, qty) {
  const base = BigNumber.fromNumber(baseCost);
  const g = BigNumber.fromNumber(growthRate);
  // soma geométrica fechada: baseCost * r^owned * (r^qty - 1)/(r - 1)
  const rPowOwned = g.pow(owned);
  const rPowQty = g.pow(qty);
  const numerator = rPowQty.sub(BigNumber.one());
  const denominator = BigNumber.fromNumber(growthRate - 1);
  return base.mul(rPowOwned).mul(numerator).div(denominator);
}

/** Maior quantidade comprável com `balance` (MAX) — fechado com progressão geométrica. */
export function maxAffordable(baseCost, growthRate, owned, balance) {
  const base = BigNumber.fromNumber(baseCost);
  const g = BigNumber.fromNumber(growthRate);
  const denom = BigNumber.fromNumber(growthRate - 1);
  // balance * (r-1) / (base * r^owned) + 1 >= r^n  =>  n <= log_r( ... )
  const budget = balance.mul(denom).div(base.mul(g.pow(owned))).add(BigNumber.one());
  if (budget.lte(BigNumber.one())) return 0;
  const n = Math.floor(budget.log10() / Math.log10(growthRate));
  // ajuste fino por iteração limitada (robustez numérica)
  let best = 0;
  for (let cand = Math.max(0, n - 1); cand <= n + 1; cand++) {
    const cost = buyCost(baseCost, growthRate, owned, cand);
    if (cost.lte(balance)) best = cand;
    else break;
  }
  return best;
}

/** Multiplicador acumulado de milestones para `owned` unidades (§30). */
export function milestoneMultiplier(milestones, owned) {
  let mult = BigNumber.one();
  for (const m of milestones) {
    if (owned >= m.count) mult = mult.scale(m.factor);
  }
  return mult;
}

/** Produção por segundo de um produtor. */
export function producerProduction(baseProduction, owned, milestones, ownedCount) {
  const base = BigNumber.fromNumber(baseProduction);
  const mmult = milestoneMultiplier(milestones, ownedCount);
  return base.scale(owned).mul(mmult);
}

export default { BUY_MODES, buyCost, maxAffordable, milestoneMultiplier, producerProduction };

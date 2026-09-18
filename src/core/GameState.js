/**
 * GameState — estado agregado do jogo + comandos de gameplay (spec §13, §15).
 * Engine-agnóstico (espelho C# planejado). A UI só dispara comandos e renderiza.
 *
 * Multiplicadores (derivados e explícitos):
 *  - globalMultiplier: bônus permanente de Convictos (§19/§60), aplicado à produção.
 *  - boost: bônus genérico/explícito (shop, ads, eventos, payer) — aplica a
 *    produção E ao clique. Persistido em save.
 */
import BigNumber from './BigNumber.js';
import * as Economy from './Economy.js';
import { globalBonus } from './Prestige.js';

// parse determinístico de custos de conteúdo ("1.5e6", "500", "0") → BigNumber
function bn(str) {
  if (str instanceof BigNumber) return str;
  return BigNumber.fromString(String(str));
}

export class GameState {
  /**
   * @param {object} config conteúdo data-driven agregado
   *   { economy: {...}, producers: [...], clicks: { levels: [...] } }
   * @param {object} [snapshot] save carregado (opcional)
   */
  constructor(config, snapshot = null) {
    this.config = config;
    this.eco = config.economy || {};
    this.milestones = (this.eco.milestones || []).map((m) => ({ count: m.count, factor: m.factor }));

    // ---- estado mutável ----
    this.version = 1;
    this.credits = BigNumber.zero();
    this.lifetimeCredits = BigNumber.zero(); // base do prestígio desta run (§59)
    this.comboSteps = 0;                      // Engajamento Viral (§24)
    this.lastClickAt = 0;
    this.clickLevel = 1;                      // upgrade de clique atual (§26)
    this.producers = {};                      // id -> owned (int)
    this.totalClicks = 0;
    this.convictos = 0;                       // §19: permanece após reset
    this.boost = BigNumber.one();             // bônus genérico (shop/ads/evento)
    this.timestamp = Date.now();

    if (snapshot) this._loadSnapshot(snapshot);

    this._recomputeGlobal();
    this._compute();
  }

  // ---------- conteúdo ----------

  producerList() {
    return this.config.producers || [];
  }

  producerDef(id) {
    return this.producerList().find((p) => p.id === id);
  }

  clickLevels() {
    return this.config.clicks?.levels || [];
  }

  /** Próximo upgrade de clique (nível seguinte ao atual). */
  nextClickLevel() {
    const levels = this.clickLevels();
    return levels.find((l) => l.level === this.clickLevel + 1) || null;
  }

  clickPower() {
    const lvl = this.clickLevels().find((l) => l.level === this.clickLevel);
    return BigNumber.fromNumber(lvl ? lvl.power : 1);
  }

  prestigeParams() {
    return this.eco.prestige || { threshold: '1e6', exponent: 0.5, convictBonus: 0.03 };
  }

  // ---------- combo viral (§24) ----------

  /** Multiplicador atual do Engajamento Viral (x1 → x1.1 → … → x2). */
  viralMultiplier(now = Date.now()) {
    const step = this.eco.viralCombo?.step ?? 0.1;
    const max = this.eco.viralCombo?.max ?? 2.0;
    const decay = this.eco.viralCombo?.decayMs ?? 2500;
    if (this.lastClickAt && now - this.lastClickAt > decay) this.comboSteps = 0;
    const cap = Math.floor((max - 1) / step);
    return 1 + Math.min(this.comboSteps, cap) * step;
  }

  // ---------- comandos ----------

  /** Toque no Compartilhar no Zap (§22–§24). Retorna o ganho. */
  click(now = Date.now()) {
    // §24: primeiro clique = x1; consecutivos sobem até x2
    const gain = this.clickPower().scale(this.viralMultiplier(now)).mul(this.boost);
    this.comboSteps += 1;
    this.lastClickAt = now;
    this.totalClicks += 1;
    this.credits = this.credits.add(gain);
    this.lifetimeCredits = this.lifetimeCredits.add(gain);
    return gain;
  }

  /** Compra `qty` de um produtor (§29). */
  buyProducer(id, qty) {
    const def = this.producerDef(id);
    if (!def) return { ok: false, reason: 'unknown' };
    if (qty <= 0) return { ok: false, reason: 'qty' };
    const owned = this.producers[id] || 0;
    const cost = Economy.buyCost(def.baseCost, this.eco.producerGrowthRate, owned, qty);
    if (cost.gt(this.credits)) return { ok: false, reason: 'cost', cost };
    this.credits = this.credits.sub(cost);
    this.producers[id] = owned + qty;
    this._compute();
    return { ok: true, cost, owned: this.producers[id] };
  }

  /** Máxima quantidade comprável (MAX) (§29). */
  maxBuy(id) {
    const def = this.producerDef(id);
    if (!def) return 0;
    const owned = this.producers[id] || 0;
    return Economy.maxAffordable(def.baseCost, this.eco.producerGrowthRate, owned, this.credits);
  }

  /** Compra o próximo upgrade de clique (§26). */
  buyClickUpgrade() {
    const next = this.nextClickLevel();
    if (!next) return { ok: false, reason: 'max' };
    const cost = bn(next.cost);
    if (cost.gt(this.credits)) return { ok: false, reason: 'cost', cost };
    this.credits = this.credits.sub(cost);
    this.clickLevel = next.level;
    return { ok: true, level: this.clickLevel };
  }

  // ---------- economia derivada ----------

  /** Produção total por segundo (milestones + global + boost). */
  productionPerSecond() { return this._pps; }

  _recomputeGlobal() {
    this.globalMultiplier = globalBonus(this.convictos, this.prestigeParams());
  }

  _compute() {
    let total = BigNumber.zero();
    for (const def of this.producerList()) {
      const owned = this.producers[def.id] || 0;
      if (owned <= 0) continue;
      total = total.add(Economy.producerProduction(def.baseProduction, owned, this.milestones, owned));
    }
    this._pps = total.mul(this.globalMultiplier).mul(this.boost);
  }

  /** Milestones já atingidos por produtor. */
  milestonesFor(id) {
    const owned = this.producers[id] || 0;
    return this.milestones
      .filter((m) => owned >= m.count)
      .map((m) => ({ count: m.count, factor: m.factor }));
  }

  // ---------- tempo / offline ----------

  /** Ganho por tempo decorrido (idle). Usa produção/seg atual. */
  tick(elapsedMs) {
    if (elapsedMs <= 0) return BigNumber.zero();
    const gained = this._pps.scale(elapsedMs / 1000);
    this.credits = this.credits.add(gained);
    this.lifetimeCredits = this.lifetimeCredits.add(gained);
    return gained;
  }

  /** Ganho offline (§86–§88). */
  applyOffline(now = Date.now()) {
    const elapsedMs = now - this.timestamp;
    const minMs = (this.eco.offline?.minEligibleSeconds ?? 30) * 1000;
    if (elapsedMs <= minMs) {
      this.timestamp = now;
      return { seconds: 0, gained: BigNumber.zero() };
    }
    const capMs = (this.eco.offline?.capHours ?? 4) * 3600 * 1000;
    const usedMs = Math.min(elapsedMs, capMs);
    const gained = this.tick(usedMs);
    this.timestamp = now;
    return { seconds: Math.floor(usedMs / 1000), gained };
  }

  // ---------- serialização (save v1) ----------

  toSnapshot() {
    return {
      version: this.version,
      credits: this.credits.toJSON(),
      lifetimeCredits: this.lifetimeCredits.toJSON(),
      clickLevel: this.clickLevel,
      totalClicks: this.totalClicks,
      convictos: this.convictos,
      boost: this.boost.toJSON(),
      producers: { ...this.producers },
      timestamp: this.timestamp,
    };
  }

  _loadSnapshot(s) {
    this.version = s.version ?? 1;
    this.credits = BigNumber.fromJSON(s.credits);
    this.lifetimeCredits = BigNumber.fromJSON(s.lifetimeCredits);
    this.clickLevel = s.clickLevel ?? 1;
    this.totalClicks = s.totalClicks ?? 0;
    this.convictos = s.convictos ?? 0;
    this.boost = BigNumber.fromJSON(s.boost);
    this.producers = { ...(s.producers || {}) };
    this.timestamp = s.timestamp ?? Date.now();
  }
}

export default GameState;

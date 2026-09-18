/**
 * GameState — estado agregado + comandos de gameplay.
 * Engine-agnóstico (espelho C# planejado). A UI só dispara comandos e renderiza.
 *
 * Sistemas (spec §13+):
 *  - Clique + Engajamento Viral (§22–§26)
 *  - Produtores com CICLO + coleta manual (§27–§30, §41)
 *  - Coordenadores = automação (§38–§42)
 *  - Upgrades por produtor/globais (§71) — paridade com upgrades do gênero
 *  - Sósias (clones) por produtor (§43–§49)
 *  - Zap Vazado + medidor de desconfiança + streak (§50–§56)
 *  - Prestígio "Despertar o Gigante" (§57–§63)
 *  - Offline (§86–§88)
 */
import BigNumber from './BigNumber.js';
import * as Economy from './Economy.js';
import { globalBonus, convictosFrom } from './Prestige.js';

function bn(str) {
  if (str instanceof BigNumber) return str;
  return BigNumber.fromString(String(str));
}

export class GameState {
  constructor(config, snapshot = null) {
    this.config = config;
    this.eco = config.economy || {};
    this.milestones = (this.eco.milestones || []).map((m) => ({ count: m.count, factor: m.factor }));

    // ---- estado base ----    this.version = 2;
    this.credits = BigNumber.zero();
    this.lifetimeCredits = BigNumber.zero();
    this.comboSteps = 0;
    this.lastClickAt = 0;
    this.clickLevel = 1;
    this.totalClicks = 0;
    this.totalCollected = 0;
    this.convictos = 0;               // §19
    this.puxasacos = 0;               // ¶47: duplicatas de Sósias
    this.chumbo = 0;                  // §18: moeda premium
    this.boost = BigNumber.one();     // shop/ads/evento
    this.timestamp = Date.now();
    this.lastZapAt = 0;

    // ---- coleções de estado ----
    this.producers = {};        // id -> owned
    this.collectables = {};     // id -> acumulado PRONTO para coleta (ciclos)
    this.cycleAccum = {};       // id -> progresso (ms) do ciclo atual (uso do app)
    this.managers = {};         // id -> level (0/1+)
    this.upgrades = {};         // upgradeId -> nível comprado
    this.clones = {};           // id -> raridade
    this.zapStreak = 0;
    this.zapApproved = 0;
    this.zapDenied = 0;
    this.desconfianca = 0;      // 0..100 medidor de desconfiança (§53)
    this._firstFreeGiven = false;
    this._sinceRare = 0;        // aberturas de sósia desde o último Raro (pity)

    // ---- campanha (fases/mapas) ----
    // Fases na ordem canônica (phase1 = P1, phase2 = P2...), mapa ativo = índice.
    this.faseIndice = 0;
    this.mapProgress = {};      // mapId -> época (ordem) da conclusão (undefined = em aberto)
    this.nextOrders = {};       // mapId -> { order (índice em mapProgress), gate }
    this.mapUnlocked = {};      // mapId -> 1 (re-entrante explícito)

    if (snapshot) this._loadSnapshot(snapshot);
    this._recomputeGlobal();
    this._compute();
  }

  // ---------------- conteúdo ----------------
  /** TODAS as missões de TODOS os mapas, na ordem da campanha. Os 4 mapas
   *  operam em paralelo: produção, ciclos e melhorias enxergam o conjunto todo,
   *  não apenas o mapa ativo (spec: 4 mapas rodando ao mesmo tempo). */
  allProducerList() {
    const byMap = this.config.producerMaps || {};
    return this.listMaps().flatMap((id) => byMap[id] || []);
  }
  /** Missões do mapa ATIVO (o que a Sede exibe na faixa). */
  producerList() {
    // reflete o mapa ativo; fallback para o pool fixo do config (retrocompat.)
    const mapId = this.activeMapId();
    const byMap = this.config.producerMaps || {};
    if (byMap[mapId] && byMap[mapId].length) return byMap[mapId];
    return this.config.producers || [];
  }
  producerDef(id) { return this.allProducerList().find((p) => p.id === id); }
  managerList() { return this.config.managers?.managers || []; }
  managerDef(id) { return this.managerList().find((m) => m.id === id); }
  clickLevels() { return this.config.clicks?.levels || []; }
  cloneCatalog() { return this.config.clones?.catalog || []; }
  cloneRarities() { return this.config.clones?.rarities || []; }
  cloneCost() { return this.config.clones?.cost ?? 15; }
  clonePity() { return this.config.clones?.pity ?? 25; }
  zapMessages() { return this.config.zaps?.messages || []; }
  achievementList() { return this.config.achievements?.list || []; }
  mapList() { return this.config.maps?.maps || []; }
  buyAllManagerDef() { return this.config.managers?.buyAllManager || null; }
  prestigeParams() { return this.eco.prestige || { threshold: '1e6', exponent: 0.5, convictBonus: 0.03 }; }

  nextClickLevel() { return this.clickLevels().find((l) => l.level === this.clickLevel + 1) || null; }

  /** Milestones já atingidos para um produtor (parity: ★ ×2 em 10/25/50/...). */
  milestonesFor(id) {
    const owned = this.producers[id] || 0;
    return this.milestones.filter((m) => owned >= m.count);
  }

  /** Fase atual a partir do lifetimeCredits (§81–§84) — retrocompatível com a antiga fase por limite. */
  /** Fase/mapa ativo (progresso de campanha, não limiar de lifetime). */
  currentPhase() {
    return this.activeMap() || { id: 'P1', name: 'Deep Web', icon: '🕳️' };
  }

  /** Quantidade de unidades comprada de um produtor. */
  ownedOf(id) { return this.producers[id] || 0; }

  /** Sósia revelado para um produtor (ou null). */
  cloneOf(id) { return this.clones[id] || null; }

  // ---------------- campanha (mapas/fases) ----------------
  /** Mapas na ordem canônica. */
  phases() { return this.mapList(); }

  /** Índice canônico de um mapa. */
  mapOrder(mapId) {
    const ids = this.config.producerMapIds || [];
    const i = ids.indexOf(mapId);
    return i < 0 ? 0 : i;
  }

  /** Id do mapa ativo. */
  activeMapId() { return this.listMaps()[this.faseIndice] || 'phase1'; }

  /** Índice do mapa ativo (0..3). */
  activePhaseIndex() { return this.faseIndice; }

  /** Metadados do mapa ativo. */
  activeMap() { return this.mapList()[this.faseIndice] || null; }

  /** Última missão (gate) de um mapa — abre o próximo mapa (§82). null se concluída. */
  pendingGate(mapId) {
    const list = (this.config.producerMaps || {})[mapId] || [];
    if (!list.length) return null;
    const last = list[list.length - 1];
    if ((this.producers[last.id] || 0) >= 1) return null; // concluída
    return { producerId: last.id, name: last.name, icon: last.icon, required: 1 };
  }

  /** A missão é o gate (última) do mapa? */
  isGateProducer(mapId, producerId) {
    const list = (this.config.producerMaps || {})[mapId] || [];
    if (!list.length) return false;
    return list[list.length - 1].id === producerId;
  }

  /** Gate do mapa concluído? */
  gateDone(mapId) { return this.pendingGate(mapId) === null; }

  /** Mapas com a última missão concluída. */
  completedMaps() {
    return (this.config.producerMapIds || []).filter((id) => this.gateDone(id));
  }

  /** Um mapa está liberado (linear: abre ao concluir o gate do anterior; pode revisitar concluídos). */
  isMapUnlocked(mapId) {
    if (this.mapUnlocked[mapId]) return true;
    const order = this.mapOrder(mapId);
    if (order <= 0) return true;
    if (this.completedMaps().includes(mapId)) return true; // revisita
    const prevId = this.listMaps()[order - 1];
    if (!prevId) return true;
    return this.gateDone(prevId);
  }

  /** Avança o mapa ativo para o próximo, se o gate atual estiver concluído (§82). */
  advanceMapIfPossible() {
    if (this.faseIndice + 1 < this.mapList().length && this.gateDone(this.activeMapId())) {
      this.faseIndice += 1;
      return { moved: true, to: this.activeMapId() };
    }
    return { moved: false };
  }

  /** Lista ordenada de mapIds (phase1, phase2...). */
  listMaps() { return this.config.producerMapIds || []; }

  /** Muda o mapa ativo (manual) — só se liberado. */
  setActivePhase(index) {
    const maps = this.listMaps();
    const i = Math.max(0, Math.min(index, maps.length - 1));
    if (!this.isMapUnlocked(maps[i])) return false;
    this.faseIndice = i;
    return true;
  }

  /** Metadados do próximo mapa, ou null. */
  nextPhase() { return this.mapList()[this.faseIndice + 1] || null; }

  /** Visão enriquecida dos mapas para a UI (faixa + Mapa da Dominação). */
  phaseInfo() {
    const idx = Math.max(0, Math.min(this.faseIndice, this.mapList().length - 1));
    return this.mapList().map((m, i) => ({
      ...m,
      index: i,
      active: i === idx,
      unlocked: this.isMapUnlocked(m.id),
      completed: this.completedMaps().includes(m.id),
      gate: this.pendingGate(m.id),
    }));
  }

  /** Contadores agregados para o Arquivo Secreto (conquistas declarativas). */
  achievementValue(field) {
    switch (field) {
      case 'totalClicks': return this.totalClicks;
      case 'producersMax': return Math.max(0, ...Object.values(this.producers));
      case 'managersOwned': return Object.keys(this.managers).length;
      case 'clonesOwned': return Object.keys(this.clones).length;
      case 'zapStreak': return this.zapStreak;
      case 'convictos': return this.convictos;
      case 'lifeCredits': return this.lifetimeCredits;
      default: return 0;
    }
  }

  /** Lista de conquistas com { id, name, desc, icon, done } (avaliado agora). */
  evaluateAchievements() {
    return this.achievementList().map((a) => {
      const v = this.achievementValue(a.cond.field);
      let done = false;
      if (a.cond.op === 'gte') {
        done = (typeof v === 'number') ? v >= Number(a.cond.value) : bn(v).gte(bn(a.cond.value));
      }
      return { ...a, value: v, done };
    });
  }

  nextClickLevel() { return this.clickLevels().find((l) => l.level === this.clickLevel + 1) || null; }

  clickPower() {
    const lvl = this.clickLevels().find((l) => l.level === this.clickLevel);
    return BigNumber.fromNumber(lvl ? lvl.power : 1);
  }

  // ---------------- combo viral (§24) ----------------
  viralMultiplier(now = Date.now()) {
    const step = this.eco.viralCombo?.step ?? 0.1;
    const max = this.eco.viralCombo?.max ?? 2.0;
    const decay = this.eco.viralCombo?.decayMs ?? 2500;
    if (this.lastClickAt && now - this.lastClickAt > decay) this.comboSteps = 0;
    const cap = Math.floor((max - 1) / step);
    return 1 + Math.min(this.comboSteps, cap) * step;
  }

  // ---------------- clique ----------------
  click(now = Date.now()) {
    const gain = this.clickPower().scale(this.viralMultiplier(now)).mul(this.boost);
    this.comboSteps += 1;
    this.lastClickAt = now;
    this.totalClicks += 1;
    this.credits = this.credits.add(gain);
    this.lifetimeCredits = this.lifetimeCredits.add(gain);
    return gain;
  }

  // ---------------- produtores (ciclo, §41) ----------------
  hasManager(id) { return (this.managers[id] || 0) >= 1; }

  /** Um produtor está automatizado se o Coordenador vinculado (campo `producer`) foi contratado. */
  isAutomated(producerId) {
    for (const m of this.managerList()) {
      if (m.producer === producerId && (this.managers[m.id] || 0) >= 1) return true;
    }
    return false;
  }

  /** Multiplicador de produção de UM produtor (milestones + upgrades + clones). */
  producerMult(id) {
    const def = this.producerDef(id);
    if (!def) return BigNumber.one();
    const owned = this.producers[id] || 0;
    let m = Economy.milestoneMultiplier(this.milestones, owned);
    const upgMult = this._upgradeMultFor(def.id);
    m = m.mul(upgMult);
    const clone = this.clones[id];
    if (clone) m = m.scale(clone.mult);
    return m;
  }

  _upgradeMultFor(slotOrId) {
    const def = this._producerUpgradeDef(slotOrId);
    // melhorias indexadas por missão (p1_01) ou por slot (retrocompat.)
    const storageKey = this._producerUpgradeKey(slotOrId);
    const lvl = this.upgrades[`pp_${storageKey}`] || 0;
    const costs = def && def.costs ? def.costs : [5, 5, 5, 5, 5];
    let m = BigNumber.one();
    for (let i = 0; i < costs.length; i++) {
      if (lvl > i) m = m.scale(def ? def.mult : 3);
    }
    return m;
  }

  /** Produção BRUTA por segundo de um produtor (sem managers). */
  producerPps(id) {
    const def = this.producerDef(id);
    if (!def) return BigNumber.zero();
    const owned = this.producers[id] || 0;
    if (owned <= 0) return BigNumber.zero();
    return BigNumber.fromNumber(def.valuePerCycle).scale(owned)
      .div(BigNumber.fromNumber(def.cycleSeconds))
      .mul(this.producerMult(id));
  }

  /** Produção total por segundo (só produtores com Coordenador contam para idle). */
  productionPerSecond() { return this._pps; }

  _compute() {
    let total = BigNumber.zero();
    // TODOS os mapas produzem em paralelo (não só o ativo).
    for (const def of this.allProducerList()) {
      if (!this.isAutomated(def.id)) continue; // sem automação, não gera sozinho
      total = total.add(this.producerPps(def.id));
    }
    const p = this.config.upgrades?.global || [];
    let g = BigNumber.one();
    for (let i = 0; i < p.length; i++) {
      if ((this.upgrades[p[i].id] || 0) > 0) g = g.scale(p[i].mult);
    }
    // Puxa-Sacos: +1% produção global por unidade (¶47)
    const ps = BigNumber.one().add(BigNumber.fromNumber(0.01 * this.puxasacos));
    this._pps = total.mul(g).mul(this.globalMultiplier).mul(this.boost).mul(ps);
  }

  _recomputeGlobal() {
    this.globalMultiplier = globalBonus(this.convictos, this.prestigeParams());
  }

  /**
   * Avança os ciclos dos produtores SEM coordenador: acumula valor "pronto"
   * para coleta manual (§41). Pode ir para coleta imediata quando atrelada.
   * Retorna o ganho coletado automaticamente (com managers).
   */
  tick(elapsedMs) {
    if (elapsedMs <= 0) return BigNumber.zero();
    let auto = BigNumber.zero();
    // ciclos manuais de TODOS os mapas (os 4 operam em paralelo).
    for (const def of this.allProducerList()) {
      const id = def.id;
      const owned = this.producers[id] || 0;
      if (owned <= 0) continue;
      if (this.isAutomated(id)) {
        // automação: gera produção contínua já tratada em _pps (aplicada abaixo)
        continue;
      }
      // sem manager: acumula ciclo (limitado a 1 "colheita" pendente para instigar o toque)
      this.cycleAccum[id] = (this.cycleAccum[id] || 0) + elapsedMs;
      const cycMs = def.cycleSeconds * 1000;
      if (this.cycleAccum[id] >= cycMs) {
        const cycles = Math.floor(this.cycleAccum[id] / cycMs);
        this.cycleAccum[id] = this.cycleAccum[id] % cycMs;
        const gain = BigNumber.fromNumber(def.valuePerCycle).scale(owned).scale(cycles)
          .mul(this.producerMult(id)).mul(this.globalMultiplier).mul(this.boost);
        this.collectables[id] = this.collectables[id] || BigNumber.zero();
        this.collectables[id] = this.collectables[id].add(gain);
      }
    }
    auto = this._pps.scale(elapsedMs / 1000);
    this.credits = this.credits.add(auto);
    this.lifetimeCredits = this.lifetimeCredits.add(auto);
    return auto;
  }

  /** Coleta manual do produtor (sem manager): paga o acumulado pronto (§41). */
  collect(id) {
    const acc = this.collectables[id];
    if (!acc || acc.isZero()) return BigNumber.zero();
    this.collectables[id] = BigNumber.zero();
    this.credits = this.credits.add(acc);
    this.lifetimeCredits = this.lifetimeCredits.add(acc);
    this.totalCollected += 1;
    return acc;
  }

  // ---------------- compras ----------------
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
    // missão-fim → muda o mapa ativo (paridade: última missão do mapa abre o próximo §82)
    return { ok: true, cost, owned: this.producers[id], advanced: this.advanceMapIfPossible() };
  }

  maxBuy(id) {
    const def = this.producerDef(id);
    if (!def) return 0;
    return Economy.maxAffordable(def.baseCost, this.eco.producerGrowthRate, this.producers[id] || 0, this.credits);
  }

  buyClickUpgrade() {
    const next = this.nextClickLevel();
    if (!next) return { ok: false, reason: 'max' };
    const cost = bn(next.cost);
    if (cost.gt(this.credits)) return { ok: false, reason: 'cost', cost };
    this.credits = this.credits.sub(cost);
    this.clickLevel = next.level;
    return { ok: true, level: this.clickLevel };
  }

  /** Coordenador (automação): custo em Mentes (§41). */
  buyManager(id) {
    const m = this.managerList().find((x) => x.id === id);
    if (!m) return { ok: false, reason: 'unknown' };
    if (this.hasManager(id)) return { ok: false, reason: 'owned' };
    const cost = BigNumber.fromNumber(m.cost);
    if (cost.gt(this.credits)) return { ok: false, reason: 'cost', cost };
    this.credits = this.credits.sub(cost);
    this.managers[id] = 1;
    // o que estava "pronto" para coleta vira automático de imediato
    this._compute();
    return { ok: true, cost };
  }

  /**
   * Upgrade por produtor (§71): nível 1..n.
   * `key` = id da missão (ex.: 'p1_01') na campanha por mapas, ou slot (retrocompat.: 1, 2...).
   * A chave interna é `pp_<key>`, migrando saves antigos (`pp_<slot>` → `pp_<id>`).
   */
  /**
   * Chave canônica de melhoria por produtor = id da missão (p.ex. 'p1_01').
   * Aceita: id da missão, ou slot numérico (resolve para a missão do mapa ativo;
   * retrocompat. com a UI antiga que passava slot).
   */
  _producerUpgradeKey(key) {
    // id de missão direto? (qualquer mapa)
    if (typeof key === 'string' && this.producerDef(key)) return key;
    // slot numérico → missão do MAPA ATIVO (retrocompat. com a UI antiga)
    const def = this.producerList().find((p) => p.slot === key);
    if (def) return def.id;
    return String(key); // fallback (chave arcaica 'pp_<slot>')
  }

  /** Definição de custos de uma missão (por id), herdando a curva do slot se não houver. */
  _producerUpgradeDef(producerId) {
    const def = this.producerDef(producerId);
    if (!def) return null;
    const upgs = this.config.upgrades?.perProducer || [];
    const found = upgs.find((u) => u.id === producerId || u.producer === producerId)
      || upgs.find((u) => u.slot === def.slot);
    if (found) return found;
    // fallback: custos derivados do baseCost da missão (5 níveis ×3 cada).
    const base = BigNumber.fromNumber(def.baseCost).toNumber();
    return { slot: def.slot, mult: 3, costs: [5, 4, 3, 2, 1].map((k) => base * 10 ** k) };
  }

  /**
   * Upgrade por produtor (§71): nível 1..n.
   * `key` = id da missão (ex.: 'p1_01') ou slot (retrocompat.). Nível em `pp_<missão>`.
   */
  buyProducerUpgrade(key) {
    const storageKey = this._producerUpgradeKey(key);
    const def = this._producerUpgradeDef(storageKey);
    if (!def) return { ok: false, reason: 'unknown' };
    // migração de save antigo: pp_<slot> → pp_<missão>
    const producer = this.producerDef(storageKey);
    let lvl = this.upgrades[`pp_${storageKey}`] || 0;
    if (lvl === 0 && producer && (this.upgrades[`pp_${producer.slot}`] || 0) > 0) {
      lvl = this.upgrades[`pp_${producer.slot}`] || 0;
    }
    if (lvl >= def.costs.length) return { ok: false, reason: 'max' };
    const cost = BigNumber.fromNumber(def.costs[lvl]);
    if (cost.gt(this.credits)) return { ok: false, reason: 'cost', cost };
    this.credits = this.credits.sub(cost);
    this.upgrades[`pp_${storageKey}`] = lvl + 1;
    if (producer) delete this.upgrades[`pp_${producer.slot}`]; // limpa chave antiga
    this._compute();
    return { ok: true, level: lvl + 1, key: storageKey };
  }

  /** Nível de melhoria de uma missão (chave da Loja de Melhorias). */
  upgradeLevelOf(key) {
    const storageKey = this._producerUpgradeKey(key);
    return this.upgrades[`pp_${storageKey}`] || 0;
  }

  /** Desbloqueio re-entrante de mapa: libera explicitamente (testes/cheats/flags). */
  toggleMapUnlock(mapId, unlocked = true) {
    if (unlocked) this.mapUnlocked[mapId] = 1;
    else delete this.mapUnlocked[mapId];
  }

  /** Upgrade global de fase. */
  buyGlobalUpgrade(id) {
    const def = (this.config.upgrades?.global || []).find((u) => u.id === id);
    if (!def) return { ok: false, reason: 'unknown' };
    if ((this.upgrades[id] || 0) > 0) return { ok: false, reason: 'owned' };
    const cost = bn(def.cost);
    if (cost.gt(this.credits)) return { ok: false, reason: 'cost', cost };
    this.credits = this.credits.sub(cost);
    this.upgrades[id] = 1;
    this._compute();
    return { ok: true };
  }

  // ---------------- classificação de produtor (estrelas §30/paridade) ----------------
  /** Nível de upgrade por produtor (base das estrelas bronze/prata/ouro). */
  starLevelOf(id) {
    const def = this.producerDef(id);
    if (!def) return 0;
    return this.upgradeLevelOf(def.id);
  }

  // ---------------- boost por anúncio (simulado em dev §88/§92) ----------------
  /** Ativa um boost multiplicativo (×mult) por `seconds`. Multiplica sobre o atual. */
  applyBoost(mult, seconds) {
    const now = Date.now();
    this.expireBoost(now);
    this.boost = this.boost.scale(mult);
    this.boostUntil = Math.max(this.boostUntil || 0, now) + seconds * 1000;
    this._compute();
    return { boost: this.boost, until: this.boostUntil };
  }

  /** Estende a duração do boost atual sem alterar o multiplicador (empilhável). */
  extendBoost(seconds, now = Date.now()) {
    this.expireBoost(now);
    if (this.boost.eq(BigNumber.one())) return this.boost;
    this.boostUntil = Math.max(this.boostUntil || now, now) + seconds * 1000;
    return this.boost;
  }

  /** Expira o boost quando o prazo passa. */
  expireBoost(now = Date.now()) {
    if (this.boostUntil && now >= this.boostUntil) {
      this.boost = BigNumber.one();
      this.boostUntil = 0;
      this._compute();
    }
    return this.boost;
  }

  /** Segundos restantes de boost por anúncio (0 = inativo). */
  boostRemaining(now = Date.now()) {
    if (!this.boostUntil) return 0;
    return Math.max(0, Math.ceil((this.boostUntil - now) / 1000));
  }

  // ---------------- desbloqueios (§31/§38/§44/§57) ----------------
  hasAnyProducer() { return Object.values(this.producers).some((v) => v > 0); }
  hasAnyManager() { return Object.values(this.managers).some((v) => (v || 0) >= 1); }

  /** Coordenadores desbloqueiam com o 1º produtor (fluxo de referência). */
  managersUnlocked() { return this.hasAnyProducer(); }
  /** Laboratório desbloqueia com o 1º Coordenador. */
  clonesUnlocked() { return this.hasAnyManager(); }
  /** Círculo Interno (prestígio) desbloqueia com o 1º Coordenador. */
  prestigeUnlocked() { return this.hasAnyManager(); }

  /**
   * "Comprar Lealdade" (§58, paridade): ganha os Convictos SEM reset,
   * pagando 10 Chumbo (moeda premium). Preserva todo o progresso da run.
   */
  buyLoyalty() {
    const gained = convictosFrom(this.lifetimeCredits, this.prestigeParams(), this.convictos);
    if (gained <= 0) return { ok: false, reason: 'below-threshold', gained: 0 };
    if (this.chumbo < 10) return { ok: false, reason: 'cost', gained };
    this.chumbo -= 10;
    this.convictos += gained;
    this._recomputeGlobal();
    this._compute();
    return { ok: true, gained };
  }

  // ---------------- tempo/offline ----------------
  buyAll() {
    let bought = 0;
    for (const def of this.producerList()) {
      const m = this.maxBuy(def.id);
      if (m >= 1) { if (this.buyProducer(def.id, m).ok) bought += 1; }
    }
    return bought;
  }

  /** Zé do Chapéu de Alumínio: comprar-tudo com um toque (§40/§63). Custo em Convictos (permanente). */
  buyBuyAllManager() {
    const def = this.buyAllManagerDef();
    if (!def) return { ok: false, reason: 'unknown' };
    if (this.hasBuyAllManager()) return { ok: false, reason: 'owned' };
    const cost = Number(def.cost);
    if (this.convictos < cost) return { ok: false, reason: 'cost', cost };
    this.convictos -= cost;
    this.managers['__buyall'] = 1;
    return { ok: true };
  }

  hasBuyAllManager() { return (this.managers['__buyall'] || 0) >= 1; }

  // ---------------- Sósias (clones) ----------------
  /** Abrir um tanque (gacha) — custo em Chumbo, revela raridade §45. Pity: Raro garantido a cada `pity` aberturas sem Raro. */
  openClone() {
    const cost = this.cloneCost();
    if (!this._firstFreeGiven) {
      // primeiro clone sempre grátis (gancho de tutoria, §44)
      return this._revealClone(true);
    }
    if (this.chumbo < cost) return { ok: false, reason: 'cost' };
    this.chumbo -= cost;
    return this._revealClone(false);
  }

  _revealClone(free) {
    let rarity = this._rollClone();
    this._sinceRare = (this._sinceRare || 0) + 1;
    // Pity: garante Raro quando o jogador chega ao limite sem um (§48, transparência)
    if (this._sinceRare >= this.clonePity()) {
      rarity = (this.cloneRarities().find((r) => r.id === 'rare') || rarity);
      this._sinceRare = 0;
    } else if (rarity.id === 'rare' || rarity.id === 'epic') {
      this._sinceRare = 0;
    }
    const pool = this.cloneCatalog().filter((c) => c.rarity === rarity.id);
    // restringe ao mapa ativo (o sósia boosta uma missão visível da campanha atual)
    const mapProducers = (this.config.producerMaps || {})[this.activeMapId()] || this.producerList();
    const mapIds = new Set(mapProducers.map((p) => p.id));
    const localPool = pool.filter((c) => mapIds.has(c.producer));
    const pick = (localPool.length ? localPool : pool)[Math.floor(Math.random() * (localPool.length || pool.length))];
    const pid = pick.producer;
    const existing = this.clones[pid];
    if (existing) {
      // duplicata → Puxa-Saco (¶47)
      this.puxasacos += 1;
    } else {
      this.clones[pid] = { rarity: rarity.id, name: pick.name, mult: rarity.mult };
    }
    if (free) this._firstFreeGiven = true;
    return { ok: true, free, clone: pick, rarity, duplicate: !!existing, sinceRare: this._sinceRare };
  }

  _rollClone() {
    const rarities = this.config.clones?.rarities || [];
    const total = rarities.reduce((a, r) => a + r.weight, 0);
    let roll = Math.random() * total;
    for (const r of rarities) {
      roll -= r.weight;
      if (roll <= 0) return r;
    }
    return rarities[0];
  }

  // ---------------- Zap Vazado ----------------
  /** Decide um zap: aprovar (true) ou negar (false). */
  zapDecision(zapId, approve) {
    const msg = this.zapMessages().find((m) => m.id === zapId);
    if (!msg) return { ok: false, reason: 'unknown' };
    const correct = msg.pro === approve;
    if (correct) {
      this.zapStreak += 1;
      if (approve) this.zapApproved += 1; else this.zapDenied += 1;
      this.desconfianca = Math.max(0, this.desconfianca - 10);
    } else {
      this.zapStreak = 0;
      this.desconfianca = Math.min(100, this.desconfianca + 15);
    }
    this.lastZapAt = Date.now();
    const reward = this._zapReward();
    if (reward.credits) { this.credits = this.credits.add(reward.credits); this.lifetimeCredits = this.lifetimeCredits.add(reward.credits); }
    if (reward.chumbo) this.chumbo += reward.chumbo;
    return { ok: true, correct, reward, streak: this.zapStreak, desconfianca: this.desconfianca };
  }

  _zapReward() {
    if (this.zapStreak <= 0) return {};
    const cfg = this.config.zaps?.rewards || {};
    const streakMult = Math.min(1 + (this.zapStreak - 1) * 0.25, 4);
    const credits = (() => {
      const lo = Number(cfg.credits?.min ?? 50), hi = Number(cfg.credits?.max ?? 2000);
      return BigNumber.fromNumber(Math.round((lo + Math.random() * (hi - lo)) * streakMult));
    })();
    const chumbo = Math.round(((cfg.chumbo?.min ?? 1) + Math.random() * ((cfg.chumbo?.max ?? 3) - 1)) * (this.zapStreak >= 3 ? 1 : 0.3));
    return { credits, chumbo: Math.max(0, Math.floor(chumbo)) };
  }

  // ---------------- tempo/offline ----------------
  applyOffline(now = Date.now()) {
    const elapsedMs = now - this.timestamp;
    const minMs = (this.eco.offline?.minEligibleSeconds ?? 30) * 1000;
    if (elapsedMs <= minMs) { this.timestamp = now; return { seconds: 0, gained: BigNumber.zero() }; }
    const capMs = (this.eco.offline?.capHours ?? 4) * 3600 * 1000;
    const usedMs = Math.min(elapsedMs, capMs);
    const gained = this.tick(usedMs);
    this.timestamp = now;
    return { seconds: Math.floor(usedMs / 1000), gained };
  }

  // ---------------- serialização ----------------
  _num(x) { return x ? x.toJSON() : { m: 0, e: 0 }; }

  toSnapshot() {
    const collectors = {};
    for (const k of Object.keys(this.collectables)) collectors[k] = this.collectables[k].toJSON();
    const acc = {};
    for (const k of Object.keys(this.cycleAccum)) acc[k] = this.cycleAccum[k];
    return {
      version: this.version,
      credits: this.credits.toJSON(),
      lifetimeCredits: this.lifetimeCredits.toJSON(),
      clickLevel: this.clickLevel,
      totalClicks: this.totalClicks,
      totalCollected: this.totalCollected,
      convictos: this.convictos,
      puxasacos: this.puxasacos,
      chumbo: this.chumbo,
      boost: this.boost.toJSON(),
      producers: { ...this.producers },
      collectables: collectors,
      cycleAccum: acc,
      managers: { ...this.managers },
      upgrades: { ...this.upgrades },
      clones: { ...this.clones },
      zapStreak: this.zapStreak,
      zapApproved: this.zapApproved,
      zapDenied: this.zapDenied,
      desconfianca: this.desconfianca,
      firstFreeGiven: this._firstFreeGiven,
      sinceRare: this._sinceRare || 0,
      boostUntil: this.boostUntil || 0,
      faseIndice: this.faseIndice,
      mapProgress: { ...this.mapProgress },
      mapUnlocked: { ...this.mapUnlocked },
      timestamp: this.timestamp,
    };
  }

  /**
   * Migração de save (retrocompat. §174): chaves antigas `PRD_phase1_XX`
   * → `p1_XX`. A campanha por mapas renomeou os ids das missões; saves
   * anteriores continuam válidos.
   */
  _migrateKey(k) {
    if (typeof k !== 'string') return k;
    return k.replace(/^PRD_phase(\d+)_(\d+)$/, (_m, p, idx) => `p${p}_${String(idx).padStart(2, '0')}`)
      .replace(/^PRD_(\d+)$/, (_m, idx) => `p1_${String(idx).padStart(2, '0')}`);
  }
  _migrateKeys(map) {
    const out = {};
    for (const k of Object.keys(map || {})) out[this._migrateKey(k)] = map[k];
    return out;
  }

  /** Migra upgrades `pp_<slot>` antigos para `pp_<missão>` do mapa correspondente. */
  _migrateUpgradeKeys(upgrades) {
    const out = { ...upgrades };
    for (const k of Object.keys(upgrades || {})) {
      if (!k.startsWith('pp_')) continue;
      const raw = k.slice(3);
      if (/^\d+$/.test(raw)) {
        // pp_<slot> → missão do mapa ativo com aquele slot
        const def = this.producerList().find((p) => p.slot === Number(raw));
        if (def) {
          out[`pp_${def.id}`] = upgrades[k];
          delete out[k];
        }
      }
    }
    return out;
  }

  _loadSnapshot(s) {
    this.version = s.version ?? 2;
    this.credits = BigNumber.fromJSON(s.credits);
    this.lifetimeCredits = BigNumber.fromJSON(s.lifetimeCredits);
    this.clickLevel = s.clickLevel ?? 1;
    this.totalClicks = s.totalClicks ?? 0;
    this.totalCollected = s.totalCollected ?? 0;
    this.convictos = s.convictos ?? 0;
    this.puxasacos = s.puxasacos ?? 0;
    this.chumbo = s.chumbo ?? 0;
    this.boost = BigNumber.fromJSON(s.boost);
    this.producers = this._migrateKeys(s.producers || {});
    this.collectables = {}; for (const k of Object.keys(s.collectables || {})) this.collectables[this._migrateKey(k)] = BigNumber.fromJSON(s.collectables[k]);
    this.cycleAccum = {}; for (const k of Object.keys(s.cycleAccum || {})) this.cycleAccum[this._migrateKey(k)] = s.cycleAccum[k];
    this.managers = { ...(s.managers || {}) };
    this.upgrades = this._migrateUpgradeKeys(s.upgrades || {});
    this.clones = {}; for (const k of Object.keys(s.clones || {})) this.clones[this._migrateKey(k)] = s.clones[k];
    this.zapStreak = s.zapStreak ?? 0;
    this.zapApproved = s.zapApproved ?? 0;
    this.zapDenied = s.zapDenied ?? 0;
    this.desconfianca = s.desconfianca ?? 0;
    this._firstFreeGiven = s.firstFreeGiven ?? false;
    this._sinceRare = s.sinceRare || 0;
    this.boostUntil = s.boostUntil || 0;
    if (this.boostUntil && this.boostUntil <= Date.now()) { this.boostUntil = 0; this.boost = BigNumber.one(); }
    this.faseIndice = s.faseIndice ?? 0;
    this.mapProgress = { ...(s.mapProgress || {}) };
    this.mapUnlocked = { ...(s.mapUnlocked || {}) };
    this.timestamp = s.timestamp ?? Date.now();
  }
}

export default GameState;

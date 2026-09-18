/**
 * O GIGANTE DESPERTOU — M1 vertical slice (9 telas, spec §74).
 * Camada de apresentação (descartável na porta Unity). Só dispara comandos no
 * GameState e renderiza; jamais calcula economia por conta própria.
 */
import { loadConfigWeb } from './core/content.js';
import { GameState } from './core/GameState.js';
import BigNumber from './core/BigNumber.js';
import * as Economy from './core/Economy.js';
import * as Prestige from './core/Prestige.js';
import { serialize, deserialize, recover } from './core/Save.js';
import { Analytics } from './core/Analytics.js';
import { SFX } from './core/SFX.js';
import { spawnFloater, spawnPhone } from './core/VFX.js';

// ---------- boot ----------
const SAVE_KEY = 'ogigante.save.v1';
const SAVE_BACKUP_KEY = 'ogigante.save.v1.bak';
const MAX_PRODUCERS = 12; // vertical slice: Fase 1 completa
const UI_BUY_MODES = [1, 10, -1]; // parity de referência: x1 / x10 / MAX

let config = null;
let state = null;
let numberFormat = 'short'; // 'full' | 'short' | 'scientific' (§21)
let lastFrame = performance.now();
let saveTimer = 0;
let offlinePending = null;
let currentScreen = 'screen-sede';
let lastSedeUpdate = 0;
let shopTarget = null;      // slot selecionado na Loja de Melhorias
let lastZap = null;         // zap em análise
let resetArmed = false;

const ui = {};

function $(id) { return document.getElementById(id); }
function el(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}
function fmt(bn) { return bn.format(numberFormat); }
function isBig(v) { return v instanceof BigNumber; }

// ---------- boot ----------
async function boot() {
  try {
    config = await loadConfigWeb({ maxProducers: MAX_PRODUCERS });
  } catch (err) {
    document.body.innerHTML = `<div style="padding:24px;color:#39FF9C;font-family:monospace">Falha ao carregar conteúdo: ${err.message}<br>Rode <b>python3 -m http.server 8000 --directory src</b> e abra http://localhost:8000</div>`;
    return;
  }
  state = hydrateState();
  bindUI();
  applyOfflineOnStart();
  Analytics.track('first_open', { version: 2, screens: 9 });
  buildProducerRows();
  renderAll();
  requestAnimationFrame(loop);
}

function hydrateState() {
  const primary = localStorage.getItem(SAVE_KEY);
  const backup = localStorage.getItem(SAVE_BACKUP_KEY);
  const rec = recover(primary, [backup]);
  if (rec.ok) {
    const s = new GameState(config, rec.data);
    Analytics.track('session_resume', { source: rec.source });
    return s;
  }
  Analytics.track('new_game');
  return new GameState(config);
}

// ---------- offline (§86–§88) ----------
function applyOfflineOnStart() {
  const res = state.applyOffline(Date.now());
  if (res.seconds > 0) {
    offlinePending = res;
    showOfflineReport(res);
  }
}

function showOfflineReport(res) {
  $('offline-report').classList.remove('hidden');
  const secs = res.seconds;
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const quando = h > 0 ? `${h}h ${m}min` : `${m}min`;
  $('offline-text').textContent = `Enquanto você sumiu (${quando}), a operação convenceu ${res.gained.format(numberFormat)} pessoas.`;
  $('offline-double').onclick = () => {
    state.credits = state.credits.add(res.gained);
    Analytics.track('rewarded_complete', { placement: 'offline_2x' });
    toast('Relatório duplicado! 📄');
    $('offline-report').classList.add('hidden');
    renderAll();
  };
  $('offline-close').onclick = () => $('offline-report').classList.add('hidden');
}

// ---------- UI bindings ----------
function bindUI() {
  // click principal
  const clickZone = $('click-zone');
  clickZone.addEventListener('pointerdown', (e) => {
    const r = clickZone.getBoundingClientRect();
    doClick(e.clientX - r.left, e.clientY - r.top);
  });

  // comprar tudo (Zé)
  $('buy-all-btn').onclick = buyAll;
  window.__buyZe = buyZe;

  // sósias
  $('clone-open').onclick = openClone;
  window.__closeClone = () => $('clone-modal').classList.add('hidden');

  // zap
  $('zap-approve').onclick = () => decideZap(true);
  $('zap-deny').onclick = () => decideZap(false);

  // prestige
  $('prestige-btn').onclick = doPrestige;
  window.__confirmPrestige = confirmPrestige;
  window.__closePrestige = closePrestige;

  // som / formato / reset
  $('sound-toggle').onclick = toggleSound;
  $('format-btn').onclick = cycleFormat;
  $('reset-btn').onclick = resetSave;

  // navegação dock + sheet
  document.querySelectorAll('.dock-btn').forEach((b) => {
    b.onclick = () => {
      if (b.classList.contains('more')) { toggleMenu(); return; }
      go(b.dataset.screen);
    };
  });
  document.querySelectorAll('.sheet-btn[data-screen]').forEach((b) => {
    b.onclick = () => { closeMenu(); if (b.dataset.screen) go(b.dataset.screen); };
  });
  $('menu-close').onclick = closeMenu;

  renderRates();
  renderMap();
  renderLeadPacks();
  renderArchive();
}

let menuOpen = false;
function toggleMenu() { menuOpen ? closeMenu() : openMenu(); }
function openMenu() { $('menu-sheet').classList.remove('hidden'); menuOpen = true; }
function closeMenu() { $('menu-sheet').classList.add('hidden'); menuOpen = false; }

function go(screenId) {
  currentScreen = screenId;
  document.querySelectorAll('.screen').forEach((s) => s.classList.toggle('active', s.id === screenId));
  document.querySelectorAll('.dock-btn').forEach((b) => b.classList.toggle('active', b.dataset.screen === screenId));
  renderScreen(screenId);
}

function renderScreen(id) {
  if (id === 'screen-sede') { buildProducerRows(); renderClickUpgrade(); updateProducerRows(); }
  if (id === 'screen-managers') renderManagers();
  if (id === 'screen-clones') renderClones();
  if (id === 'screen-zap') renderZap();
  if (id === 'screen-lodge') { renderLodgeStats(); renderGlobalUpgrades(); }
  if (id === 'screen-shop') renderShop();
  if (id === 'screen-map') renderMap();
  if (id === 'screen-lead') renderLeadPacks();
  if (id === 'screen-archive') renderArchive();
}

function renderAll() {
  renderHUD();
  renderScreen(currentScreen);
}

// ---------- clique principal ----------
function doClick(x, y) {
  const gain = state.click(performance.now());
  SFX.click();
  Analytics.track('click_main', { combo: state.comboSteps, credits: gain.log10() });
  spawnFloater(ui.clickPanel, `+${fmt(gain)} 👁`, { x, y, cls: 'credit' });
  spawnPhone(ui.clickPanel, { x: x + 8, y: y - 14 });
  renderHUD();
}

// ---------- produtores ----------
function buildProducerRows() {
  const wrap = ui.producers;
  wrap.innerHTML = '';
  for (const def of state.producerList()) wrap.appendChild(buildProducerRow(def));
}

function buildProducerRow(def) {
  const id = def.id;
  const owned = state.ownedOf(id);
  const perCycle = BigNumber.fromNumber(def.valuePerCycle).scale(Math.max(owned, 0))
    .mul(state.producerMult(id));
  const ms = state.milestonesFor(id);
  const msMult = ms.reduce((a, b) => a * b.factor, 1);
  const automated = state.isAutomated(id);
  const manager = state.managerList().find((m) => m.producer === id);

  const row = el('div', 'producer');
  row.dataset.id = id;

  const top = el('div', 'prod-top');
  top.appendChild(el('span', 'prod-icon', def.icon || '🏢'));
  const meta = el('div', 'prod-meta');
  meta.appendChild(el('div', 'producer-name',
    `${def.name}${msMult > 1 ? ` <span class="milestone" title="milestones">★×${msMult}</span>` : ''}`));
  meta.appendChild(el('div', 'producer-owned', `possuídos: <b>${owned}</b> · renda ${fmt(perCycle)} 👁 / ${def.cycleSeconds}s`));
  if (def.flavor) meta.appendChild(el('div', 'producer-flavor', def.flavor));
  meta.appendChild(el('div', 'producer-state', automated ? `<span style="color:var(--green-neon)">🤖 automático — ${fmt(state.producerPps(id))} 👁/s</span>` : `<span style="color:var(--alert)">✋ coleta manual</span>`));
  top.appendChild(meta);
  const improve = el('button', 'mini-btn improve', '🛠');
  improve.title = 'Melhorar este produtor (Loja)';
  improve.onclick = () => { shopTarget = def.slot; closeMenu(); go('screen-shop'); };
  top.appendChild(improve);
  row.appendChild(top);

  // botões x1 / x10 / MAX
  const actions = el('div', 'prod-actions');
  for (const mode of UI_BUY_MODES) {
    const qty = mode === -1 ? state.maxBuy(id) : mode;
    const cost = Economy.buyCost(def.baseCost, state.eco.producerGrowthRate, owned, qty);
    const b = el('button', 'buy-btn', `${mode === -1 ? 'MAX' : 'x' + mode}<span>${fmt(cost)}</span>`);
    b.dataset.mode = mode;
    b.disabled = qty <= 0 || state.credits.lt(cost);
    b.onclick = () => buyProducer(id, mode);
    actions.appendChild(b);
  }
  row.appendChild(actions);

  // coletar (manual)
  const colBtn = el('button', 'collect-btn', `COLETAR <b>+0</b> 👁`);
  colBtn.classList.add('hidden');
  colBtn.onclick = () => collectProducer(id);
  row.appendChild(colBtn);

  // coordenador inline
  const mgrRow = el('div', 'prod-manager');
  if (manager) {
    if (automated) {
      mgrRow.appendChild(el('span', '', `🧑‍💼 ${manager.icon || ''} ${manager.name} já cuida disso.`));
    } else {
      const cost = BigNumber.fromNumber(manager.cost);
      mgrRow.appendChild(el('span', '', `🧑‍💼 ${manager.icon || ''} Contratar <b>${manager.name}</b> — ${fmt(cost)} 👁 (automatiza)`));
      const hire = el('button', 'mini-btn hire', 'CONTRATAR');
      hire.disabled = state.credits.lt(cost);
      hire.onclick = () => hireManager(manager.id, id);
      mgrRow.appendChild(hire);
    }
  }
  row.appendChild(mgrRow);
  return row;
}

function updateProducerRows() {
  for (const def of state.producerList()) {
    const row = document.querySelector(`.producer[data-id="${def.id}"]`);
    if (!row) continue;
    const owned = state.ownedOf(def.id);
    row.querySelector('.producer-owned').innerHTML =
      `possuídos: <b>${owned}</b> · renda ${fmt(BigNumber.fromNumber(def.valuePerCycle).scale(Math.max(owned, 0)).mul(state.producerMult(def.id)))} 👁 / ${def.cycleSeconds}s`;
    for (const b of row.querySelectorAll('.buy-btn')) {
      const mode = Number(b.dataset.mode);
      const qty = mode === -1 ? state.maxBuy(def.id) : mode;
      const cost = Economy.buyCost(def.baseCost, state.eco.producerGrowthRate, owned, qty);
      b.querySelector('span').textContent = fmt(cost);
      b.disabled = qty <= 0 || state.credits.lt(cost);
    }
    const automated = state.isAutomated(def.id);
    row.querySelector('.producer-state').innerHTML = automated ?
      `<span style="color:var(--green-neon)">🤖 automático — ${fmt(state.producerPps(def.id))} 👁/s</span>` :
      `<span style="color:var(--alert)">✋ coleta manual</span>`;
    // coletar
    const acc = state.collectables[def.id];
    const colBtn = row.querySelector('.collect-btn');
    if (!automated && acc && !acc.isZero()) {
      colBtn.innerHTML = `COLETAR <b>+${fmt(acc)}</b> 👁`;
      colBtn.classList.remove('hidden');
    } else {
      colBtn.classList.add('hidden');
    }
    // botão contratar
    const hire = row.querySelector('.mini-btn.hire');
    if (hire) {
      const manager = state.managerList().find((m) => m.producer === def.id);
      hire.disabled = state.credits.lt(BigNumber.fromNumber(manager.cost));
    }
  }
  // Zé / comprar tudo
  const ba = $('buy-all-btn');
  const hasZe = state.hasBuyAllManager();
  ba.innerHTML = hasZe ? '👔 COMPRAR TUDO' : '👔🔒 comprar tudo';
  ba.title = hasZe ? 'Zé do Chapéu de Alumínio: compra o máximo com um toque' : 'Contrate o Zé do Chapéu de Alumínio (10 Convictos)';
}

function buyProducer(id, mode) {
  const qty = mode === -1 ? state.maxBuy(id) : mode;
  if (qty <= 0) return;
  const res = state.buyProducer(id, qty);
  if (res.ok) {
    SFX.buy();
    Analytics.track('producer_buy', { producer_id: id, qty });
    updateProducerRows();
    renderHUD();
  }
}

function collectProducer(id) {
  const got = state.collect(id);
  if (!got.isZero()) {
    SFX.buy();
    Analytics.track('collect', { producer_id: id, credits: got.log10() });
    updateProducerRows();
    renderHUD();
  }
}

function hireManager(mgrId, producerId) {
  const res = state.buyManager(mgrId);
  if (res.ok) {
    SFX.message();
    Analytics.track('manager_buy', { manager_id: mgrId, producer_id: producerId });
    toast('Coordenador contratado! 🤖');
    buildProducerRows();
    updateProducerRows();
    renderHUD();
  } else if (res.reason === 'cost') {
    toast('Faltam Crédulos para esse Coordenador. 👁');
  }
}

function buyAll() {
  if (!state.hasBuyAllManager()) { go('screen-managers'); toast('Contrate o Zé do Chapéu de Alumínio (10 Convictos).'); return; }
  const n = state.buyAll();
  if (n > 0) { SFX.stamp(); Analytics.track('buy_all', { lots: n }); updateProducerRows(); renderHUD(); }
  else toast('Nada comprável agora.');
}

function buyZe() {
  const res = state.buyBuyAllManager();
  if (res.ok) { SFX.giant(); Analytics.track('buy_all_manager'); toast('Zé contratado! Comprar tudo liberado. 🥫👔'); renderHUD(); renderManagers(); }
  else if (res.reason === 'cost') toast('O Zé custa 10 Convictos. Acorde o Gigante primeiro! 🌋');
  else if (res.reason === 'owned') toast('O Zé já é funcionário fixo.');
}

// ---------- coordenadores ----------
function renderManagers() {
  const wrap = $('managers-list');
  wrap.innerHTML = '';
  for (const m of state.managerList()) {
    const def = state.producerDef(m.producer);
    const owned = state.hasManager(m.id);
    const cost = BigNumber.fromNumber(m.cost);
    const row = el('div', 'mgr-row' + (owned ? ' owned' : ''));
    row.appendChild(el('div', 'mgr-icon', m.icon || '🧑‍💼'));
    const info = el('div', 'mgr-info');
    info.appendChild(el('div', 'mgr-name', m.name));
    info.appendChild(el('div', 'mgr-target', `automatiza: ${def ? def.icon + ' ' + def.name : m.producer}`));
    if (m.hire) info.appendChild(el('div', 'mgr-quote', `“${m.hire}”`));
    row.appendChild(info);
    if (!owned) {
      const hire = el('button', 'mini-btn hire', `CONTRATAR ${fmt(cost)}`);
      hire.disabled = state.credits.lt(cost);
      hire.onclick = () => { hireManager(m.id, m.producer); renderManagers(); };
      row.appendChild(hire);
    } else {
      row.appendChild(el('span', 'mgr-owned', '✓ contratado'));
    }
    wrap.appendChild(row);
  }
  // Zé
  const ze = state.buyAllManagerDef();
  const hasZe = state.hasBuyAllManager();
  const zeBtn = $('buy-zé');
  if (zeBtn) {
    zeBtn.disabled = hasZe;
    zeBtn.textContent = hasZe ? `👔 ${ze.name} — contratado (comprar tudo liberado)` : `👔 ${ze.name} — comprar tudo (${ze.cost} Convictos)`;
  }
}

// ---------- sósias ----------
function renderRates() {
  const wrap = $('clone-rates');
  wrap.innerHTML = '';
  const total = state.cloneRarities().reduce((a, r) => a + r.weight, 0);
  for (const r of state.cloneRarities()) {
    const pct = Math.round((r.weight / total) * 100);
    wrap.appendChild(el('div', 'rate-chip',
      `<b>${r.name}</b> ×${r.mult} <span>${pct}%</span>`));
  }
  $('clone-cost').textContent = state.cloneCost();
}

function renderClones() {
  const wrap = $('clones-list');
  wrap.innerHTML = '';
  const btn = $('clone-open');
  const freeReady = !state._firstFreeGiven;
  btn.innerHTML = freeReady ? '🧬 ABRIR 1º TANQUE — <b>GRÁTIS</b>' : `🧬 ABRIR TANQUE — <span id="clone-cost">${state.cloneCost()}</span> 🥫`;
  $('clone-pity').textContent =
    `Chumbo: ${state.chumbo} 🥫 · Puxa-Sacos: ${state.puxasacos} (+${state.puxasacos}% global) · Raro garantido a cada ${state.clonePity()} aberturas (${Math.min(state._sinceRare || 0, state.clonePity())}/${state.clonePity()})`;

  const ownedIds = Object.keys(state.clones);
  if (ownedIds.length === 0) {
    wrap.appendChild(el('div', 'empty-note', 'Nenhum sósia revelado ainda. Abra o primeiro tanque (grátis)!'));
    return;
  }
  for (const pid of ownedIds) {
    const c = state.clones[pid];
    const def = state.producerDef(pid);
    const rarity = state.cloneRarities().find((r) => r.id === c.rarity);
    const card = el('div', 'clone-card ' + (c.rarity || 'common'));
    card.appendChild(el('div', 'clone-prod-icon', (def ? def.icon : '🕵️')));
    card.appendChild(el('div', 'clone-name', c.name));
    card.appendChild(el('div', 'clone-rarity', `${rarity ? rarity.name : c.rarity} · ×${c.mult}`));
    card.appendChild(el('div', 'clone-target', def ? def.name : pid));
    wrap.appendChild(card);
  }
}

function openClone() {
  const res = state.openClone();
  if (!res.ok) {
    if (res.reason === 'cost') { toast('Falta Chumbo. Veja a Loja de Chumbo. 🥫'); }
    return;
  }
  SFX.giant();
  Analytics.track('clone_open', { rarity: res.rarity.id, duplicate: res.duplicate, free: res.free });
  const def = state.producerDef(res.clone.producer);
  $('clone-reveal-rarity').textContent = res.rarity.name.toUpperCase();
  $('clone-reveal-rarity').className = 'reveal-rarity ' + res.rarity.id;
  $('clone-reveal-icon').textContent = def ? def.icon : '🕵️';
  $('clone-reveal-name').textContent = res.clone.name;
  $('clone-reveal-line').textContent = res.clone.line || '';
  if (res.duplicate) {
    $('clone-reveal-eff').textContent = 'Duplicata! Vira Puxa-Saco: +1% de produção global. 🙇';
  } else {
    $('clone-reveal-eff').textContent = `×${res.rarity.mult} em “${def ? def.name : res.clone.producer}”`;
  }
  $('clone-modal').classList.remove('hidden');
  renderClones();
  renderHUD();
}

// ---------- zap vazado ----------
function renderZap() {
  if (!lastZap) nextZap(false);
  const m = lastZap;
  $('zap-sender').textContent = m ? `📲 ${m.sender}` : '';
  $('zap-text').textContent = m ? m.text : '';
  $('zap-buttons').classList.remove('hidden');
  renderZapMeter();
}

function nextZap(awardToasts) {
  const pool = state.zapMessages();
  const idx = Math.floor(Math.random() * pool.length);
  lastZap = pool[idx];
  const m = lastZap;
  $('zap-sender').textContent = `📲 ${m.sender}`;
  $('zap-text').textContent = m.text;
}

function renderZapMeter() {
  const d = state.desconfianca;
  const bar = $('zap-desconfianca');
  bar.style.width = Math.max(0, Math.min(100, d)) + '%';
  bar.style.background = d > 60 ? 'var(--stamp)' : 'var(--green-neon)';
}

function decideZap(approve) {
  if (!lastZap) { nextZap(); return; }
  const res = state.zapDecision(lastZap.id, approve);
  SFX.message();
  Analytics.track('zap_decision', { approve, correct: res.correct, streak: state.zapStreak });
  const r = res.reward || {};
  const bits = [];
  if (res.correct) bits.push(`✅ Certeiro! Streak ×${state.zapStreak}`);
  else bits.push('⛔ Você avaliou errado. Streak zerado.');
  if (r.credits && !r.credits.isZero()) bits.push(`+${fmt(r.credits)} 👁`);
  if (r.chumbo) bits.push(`+${r.chumbo} 🥫`);
  toast(bits.join(' · '));
  nextZap();
  renderZapMeter();
  renderHUD();
}

// ---------- maçonaria / prestige / upgrades globais ----------
function renderLodgeStats() {
  $('stat-life').textContent = fmt(state.lifetimeCredits);
  $('stat-credits').textContent = fmt(state.credits);
  $('stat-pps').textContent = fmt(state.productionPerSecond());
  $('stat-convictos').textContent = String(state.convictos);
  $('stat-power').textContent = fmt(state.clickPower());
  $('stat-puxasacos').textContent = String(state.puxasacos);
}

function renderGlobalUpgrades() {
  const wrap = $('global-upgrades');
  wrap.innerHTML = '';
  const list = config.upgrades?.global || [];
  for (const u of list) {
    const owned = (state.upgrades[u.id] || 0) > 0;
    const cost = BigNumber.fromString(u.cost);
    const row = el('div', 'mgr-row' + (owned ? ' owned' : ''));
    row.appendChild(el('div', 'mgr-icon', u.icon || '✨'));
    const info = el('div', 'mgr-info');
    info.appendChild(el('div', 'mgr-name', u.name));
    info.appendChild(el('div', 'mgr-target', `${u.desc || ''} · ×${u.mult} produção`));
    row.appendChild(info);
    if (!owned) {
      const b = el('button', 'mini-btn hire', `COMPRAR ${fmt(cost)}`);
      b.disabled = state.credits.lt(cost);
      b.onclick = () => {
        const r = state.buyGlobalUpgrade(u.id);
        if (r.ok) { SFX.stamp(); Analytics.track('upgrade_buy', { type: 'global', id: u.id }); renderGlobalUpgrades(); renderHUD(); }
      };
      row.appendChild(b);
    } else {
      row.appendChild(el('span', 'mgr-owned', '✓ ativo'));
    }
    wrap.appendChild(row);
  }
}

// ---------- loja de melhorias ----------
function renderShop() {
  const charge = $('shop-charge');
  const wrap = $('shop-list');
  wrap.innerHTML = '';

  if (shopTarget != null) {
    const targetDef = state.producerList().find((p) => p.slot === shopTarget);
    charge.classList.remove('hidden');
    $('shop-target').textContent = targetDef ? `${targetDef.icon} ${targetDef.name}` : `slot ${shopTarget}`;
  } else {
    charge.classList.add('hidden');
  }

  const list = config.upgrades?.perProducer || [];
  for (const u of list) {
    const def = state.producerList().find((p) => p.slot === u.slot);
    if (!def) continue;
    const lvl = state.upgrades[`pp_${u.slot}`] || 0;
    const maxed = lvl >= u.costs.length;
    const row = el('div', 'mgr-row' + (maxed ? ' owned' : '') + (shopTarget === u.slot ? ' highlight' : ''));
    row.appendChild(el('div', 'mgr-icon', def.icon || '🛠'));
    const info = el('div', 'mgr-info');
    info.appendChild(el('div', 'mgr-name', `${u.label || 'Melhoria'} — ${def.name}`));
    info.appendChild(el('div', 'mgr-target', maxed ? 'nível máximo' : `nível ${lvl}/${u.costs.length} · próximo: ×${u.mult} por ${fmt(BigNumber.fromNumber(u.costs[lvl]))} 👁`));
    row.appendChild(info);
    if (!maxed) {
      const b = el('button', 'mini-btn hire', 'MELHORAR');
      const cost = BigNumber.fromNumber(u.costs[lvl]);
      b.disabled = state.credits.lt(cost);
      b.onclick = () => {
        const r = state.buyProducerUpgrade(u.slot);
        if (r.ok) { SFX.stamp(); Analytics.track('upgrade_buy', { type: 'producer', slot: u.slot }); renderShop(); renderSedeIfNeeded(); renderHUD(); }
      };
      row.appendChild(b);
    } else {
      row.appendChild(el('span', 'mgr-owned', '✓ max'));
    }
    wrap.appendChild(row);
  }
  renderShopClicks();
}

function renderSedeIfNeeded() { if (currentScreen === 'screen-sede') { buildProducerRows(); updateProducerRows(); } }

function renderShopClicks() {
  const wrap = $('shop-clicks');
  wrap.innerHTML = '';
  const current = state.clickLevels().find((l) => l.level === state.clickLevel);
  const next = state.nextClickLevel();
  if (current) {
    const row = el('div', 'mgr-row');
    row.appendChild(el('div', 'mgr-icon', '👆'));
    const info = el('div', 'mgr-info');
    info.appendChild(el('div', 'mgr-name', `Toque: ${current.name}`));
    info.appendChild(el('div', 'mgr-target', `poder ${fmt(state.clickPower())} 👁/toque`));
    row.appendChild(info);
    if (next) {
      const cost = BigNumber.fromString(next.cost);
      const b = el('button', 'mini-btn hire', `UPGRADE`);
      b.disabled = state.credits.lt(cost);
      b.onclick = () => {
        const r = state.buyClickUpgrade();
        if (r.ok) { SFX.stamp(); Analytics.track('upgrade_buy', { type: 'click', level: r.level }); renderShopClicks(); renderClickUpgrade(); renderHUD(); }
      };
      row.appendChild(b);
      info.appendChild(el('div', 'mgr-target', `próximo: “${next.name}” por ${fmt(cost)} 👁`));
    }
    wrap.appendChild(row);
  }
}

// ---------- mapa ----------
function renderMap() {
  const wrap = $('map-list');
  wrap.innerHTML = '';
  const cur = state.currentPhase();
  for (const p of state.phaseList()) {
    const locked = state.lifetimeCredits.lt(BigNumber.fromString(p.threshold));
    const isCur = cur && cur.id === p.id;
    const card = el('div', 'map-card' + (isCur ? ' current' : '') + (locked ? ' locked' : ''));
    card.style.setProperty('--pc', p.color || '#D4AF37');
    card.appendChild(el('div', 'map-icon', p.icon || '🗺️'));
    card.appendChild(el('div', 'map-name', p.name));
    card.appendChild(el('div', 'map-flavor', p.flavor || ''));
    card.appendChild(el('div', 'map-threshold', locked ? `🔒 requer ${fmt(BigNumber.fromString(p.threshold))}` : (isCur ? '📍 você está aqui' : '✓ dominada')));
    wrap.appendChild(card);
  }
}

// ---------- loja de chumbo (IAP simulado) ----------
const LEAD_PACKS = [
  { id: 'LP_01', name: 'Punhado de Chumbo', chumbo: 100, price: 'R$ 9,90' },
  { id: 'LP_02', name: 'Balde de Chumbo', chumbo: 575, price: 'R$ 37,90', tag: 'MAIS VALOR' },
  { id: 'LP_03', name: 'Caçamba de Chumbo', chumbo: 2000, price: 'R$ 99,90', tag: 'MELHOR OFERTA' },
  { id: 'LP_04', name: 'Caminhão-pipa de Chumbo', chumbo: 6000, price: 'R$ 249,90' },
];

function renderLeadPacks() {
  const wrap = $('lead-packs');
  wrap.innerHTML = '';
  for (const p of LEAD_PACKS) {
    const row = el('div', 'mgr-row');
    row.appendChild(el('div', 'mgr-icon', '🥫'));
    const info = el('div', 'mgr-info');
    info.appendChild(el('div', 'mgr-name', `${p.name}${p.tag ? ` <span class="tag">${p.tag}</span>` : ''}`));
    info.appendChild(el('div', 'mgr-target', `+${p.chumbo} 🥫 · ${p.price} (simulado)`));
    row.appendChild(info);
    const b = el('button', 'mini-btn hire', 'COMPRAR');
    b.onclick = () => {
      state.chumbo += p.chumbo;
      SFX.buy();
      Analytics.track('iap_dev', { pack: p.id, chumbo: p.chumbo });
      toast(`+${p.chumbo} 🥫 (IAP simulado para dev — sem cobrança real)`);
      renderHUD();
    };
    row.appendChild(b);
    wrap.appendChild(row);
  }
}

// ---------- arquivo secreto ----------
function renderArchive() {
  const wrap = $('archive-list');
  wrap.innerHTML = '';
  for (const a of state.evaluateAchievements()) {
    const row = el('div', 'mgr-row' + (a.done ? ' owned' : ' locked'));
    row.appendChild(el('div', 'mgr-icon', a.icon || '🏅'));
    const info = el('div', 'mgr-info');
    info.appendChild(el('div', 'mgr-name', a.name));
    info.appendChild(el('div', 'mgr-target', a.desc));
    row.appendChild(info);
    row.appendChild(el('span', 'mgr-owned', a.done ? '✓ concluída' : '🔒'));
    wrap.appendChild(row);
  }
}

// ---------- prestige ----------
function doPrestige() {
  const gained = Prestige.convictosFrom(state.lifetimeCredits, state.prestigeParams(), state.convictos);
  $('prestige-gain').textContent = `+${gained} Convictos 👁‍🗨`;
  $('prestige-confirm').disabled = gained <= 0;
  $('prestige-modal').classList.remove('hidden');
}

function confirmPrestige() {
  const res = Prestige.prestige(state, state.prestigeParams());
  if (res.ok) {
    state = new GameState(config, res.snapshot);
    SFX.giant();
    Analytics.track('prestige_complete', { prestige_number: state.convictos });
    toast(`O Gigante despertou! +${res.gained} Convictos 👁‍🗨`);
    closePrestige();
    shopTarget = null;
    buildProducerRows();
    renderAll();
    persist();
  }
}

function closePrestige() { $('prestige-modal').classList.add('hidden'); }

// ---------- som / formato / reset ----------
function toggleSound() {
  SFX.toggleMuted();
  $('sound-ico').textContent = SFX.muted ? '🔇' : '🔊';
}

function cycleFormat() {
  const order = ['short', 'full', 'scientific'];
  const idx = order.indexOf(numberFormat);
  numberFormat = order[(idx + 1) % order.length];
  $('format-label').textContent = { short: 'abrev.', full: 'completo', scientific: 'cient.' }[numberFormat];
  renderAll();
}

function resetSave() {
  if (!resetArmed) {
    resetArmed = true;
    $('reset-btn').innerHTML = '<span>⚠️</span>Confirmar?';
    setTimeout(() => { resetArmed = false; $('reset-btn').innerHTML = '<span>🗑️</span>Resetar'; }, 3000);
    return;
  }
  localStorage.removeItem(SAVE_KEY);
  localStorage.removeItem(SAVE_BACKUP_KEY);
  state = new GameState(config);
  buildProducerRows();
  renderAll();
  persist();
  toast('Progresso apagado. Recomeçando do zero. 🫡');
}

// ---------- click upgrade (sede) ----------
function renderClickUpgrade() {
  const box = $('click-upgrade');
  const current = state.clickLevels().find((l) => l.level === state.clickLevel);
  const next = state.nextClickLevel();
  if (current) {
    $('click-lvl-name').textContent = current.name;
    $('click-lvl-power').textContent = `poder: ${fmt(state.clickPower())} 👁`;
  }
  if (next) {
    const cost = BigNumber.fromString(next.cost);
    $('click-next-name').textContent = `→ ${next.name}`;
    $('click-next-cost').textContent = fmt(cost);
    $('click-buy').disabled = state.credits.lt(cost);
    $('click-buy').onclick = () => {
      const res = state.buyClickUpgrade();
      if (res.ok) { SFX.stamp(); Analytics.track('upgrade_buy', { type: 'click', level: res.level }); renderClickUpgrade(); renderHUD(); }
    };
    box.classList.remove('hidden');
  } else {
    box.classList.add('hidden');
  }
}

// ---------- HUD ----------
function renderHUD() {
  $('credits').textContent = fmt(state.credits);
  $('chumbo').textContent = String(state.chumbo);
  $('convictos').textContent = String(state.convictos);
  $('pps').textContent = `${fmt(state.productionPerSecond())} 👁/s`;
  $('combo').textContent = `viral ×${state.viralMultiplier(performance.now()).toFixed(1)}`;
}

// ---------- loop ----------
function loop(now) {
  const delta = now - lastFrame;
  lastFrame = now;
  if (delta > 0) {
    state.tick(delta);
    saveTimer += delta;
    if (saveTimer >= (config.economy.autoSave?.intervalMs ?? 30000)) {
      saveTimer = 0;
      persist();
    }
  }
  renderHUD();
  if (currentScreen === 'screen-sede') {
    if (now - lastSedeUpdate > 250) { updateProducerRows(); renderClickUpgrade(); lastSedeUpdate = now; }
  }
  requestAnimationFrame(loop);
}

// ---------- persistência (§170–§171) ----------
function persist() {
  const str = serialize(state);
  const prev = localStorage.getItem(SAVE_KEY);
  if (prev) localStorage.setItem(SAVE_BACKUP_KEY, prev);
  localStorage.setItem(SAVE_KEY, str);
  showSaveFlash();
}

let flashTimer = null;
function showSaveFlash() {
  const elx = ui.saveFlash;
  elx.classList.add('show');
  clearTimeout(flashTimer);
  flashTimer = setTimeout(() => elx.classList.remove('show'), 700);
}

// ---------- util ----------
function toast(msg) {
  const elx = ui.toast;
  elx.textContent = msg;
  elx.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => elx.classList.remove('show'), 2600);
}

window.addEventListener('beforeunload', persist);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    state.applyOffline(Date.now());
    persist();
  }
});

// cache DOM principal
for (const id of ['credits', 'chumbo', 'convictos', 'pps', 'combo', 'click-panel', 'producers', 'click-upgrade', 'toast', 'save-flash']) {
  ui[id] = $(id);
}
ui.clickPanel = ui['click-panel'];

boot();

/**
 * O GIGANTE DESPERTOU — M1 (paridade de interface com a referência de gênero).
 * Camada de apresentação (descartável na porta Unity). Só dispara comandos no
 * GameState e renderiza; jamais calcula economia própria.
 *
 * Espelha a ESTRUTURA da referência (posições de botões, telas, bônus, animações);
 * nomes/textos/lore/ícones são 100% originais (ver docs/INTERFACE_STUDY.md).
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
const MAX_PRODUCERS = 0; // 0 = todas as missões do mapa (retrocompat.: pool único)
const UI_BUY_MODES = [1, 10, -1]; // x1 / x10 / MAX (paridade)
const WARP2_SECONDS = 2 * 3600;
const WARP4_SECONDS = 4 * 3600;

let config = null;
let state = null;
let numberFormat = 'short';
let lastFrame = performance.now();
let saveTimer = 0;
let offlinePending = null;
let currentScreen = 'screen-sede';
let lastSedeUpdate = 0;
let shopTarget = null;
let lastZap = null;
let resetArmed = false;
let notifEnabled = true;
let adOffer = null;          // bônus ativo no fone
let phoneShakeTimer = null;
let loyaltyBump = 0;         // bônus % acumulado para o próximo Despertar (anúncio)

const ui = {};

function $(id) { return document.getElementById(id); }
function el(tag, cls, html) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
}
function fmt(bn) { return bn.format(numberFormat); }
function big(s) { return BigNumber.fromString(String(s)); }

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
  Analytics.track('first_open', { version: 3 });
  // faixa de mapas: remove o hidden (sem JS o topo já vinha num estado inofensivo)
  const strip = $('map-strip');
  if (strip) strip.classList.remove('hidden');
  const mapHeader = $('map-header');
  if (mapHeader) mapHeader.classList.remove('hidden');
  buildProducerRows();
  renderMapStrip();
  renderAll();
  installBonusSoon();
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

// ---------- offline ----------
function applyOfflineOnStart() {
  const res = state.applyOffline(Date.now());
  if (res.seconds > 0) showOfflineReport(res);
}

function showOfflineReport(res) {
  const secs = res.seconds;
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const quando = h > 0 ? `${h}h ${m}min` : `${m}min`;
  $('offline-text').textContent = `Enquanto você sumiu (${quando}), a operação convenceu ${res.gained.format(numberFormat)} mentes.`;
  $('offline-double').onclick = () => {
    state.credits = state.credits.add(res.gained);
    Analytics.track('rewarded_complete', { placement: 'offline_2x' });
    toast('Relatório duplicado! 📄');
    $('offline-report').classList.add('hidden');
    renderAll();
  };
  $('offline-close').onclick = () => $('offline-report').classList.add('hidden');
  $('offline-report').classList.remove('hidden');
}

// ---------- UI bindings ----------
function bindUI() {
  // clique central (área)
  $('click-zone').addEventListener('pointerdown', (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    doClick(e.clientX - r.left, e.clientY - r.top);
  });
  // clique no botão redondo inferior
  $('click-phone').addEventListener('pointerdown', (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    doClick(e.clientX - r.left, e.clientY - r.top, true);
  });

  // HUD
  $('settings-btn').onclick = () => toggleSheet('settings-sheet');
  $('settings-close').onclick = () => hideSheet('settings-sheet');
  $('phone-btn').onclick = () => { toggleSheet('phone-sheet'); renderPhoneSheet(); };
  $('phone-close').onclick = () => hideSheet('phone-sheet');
  $('stopwatch-btn').onclick = doBoost;

  // faixa de mapas (setas nas pontas ciclam os 4 mapas; centro abre a visão geral)
  $('map-prev').onclick = cycleMap.bind(null, -1);
  $('map-next').onclick = cycleMap.bind(null, 1);
  $('map-strip-main').onclick = () => go('screen-map');

  // comprar tudo
  $('buy-all-btn').onclick = buyAll;

  // sósias
  $('clone-open').onclick = openClone;
  window.__closeClone = () => $('clone-modal').classList.add('hidden');

  // zap
  $('zap-approve').onclick = () => decideZap(true);
  $('zap-deny').onclick = () => decideZap(false);

  // prestígio / lealdade
  $('giant-bomb').onclick = openGiantBomb;
  $('giant-loyalty').onclick = openGiantLoyalty;
  window.__confirmPrestige = confirmPrestige;
  window.__closePrestige = closePrestige;
  window.__confirmLoyalty = confirmLoyalty;
  window.__closeLoyalty = closeLoyalty;

  // anúncios
  $('comm-close').onclick = closeCommercial;

  // config
  $('format-btn').onclick = cycleFormat;
  $('sound-toggle').onclick = toggleSound;
  $('notif-toggle').onclick = toggleNotif;
  $('reset-btn').onclick = resetSave;

  // navegação inferior
  document.querySelectorAll('.nav-btn[data-screen]').forEach((b) => {
    b.onclick = () => {
      if (b.classList.contains('locked')) {
        toast('🔒 Desbloqueie avançando na operação.');
        return;
      }
      hideSheets(); go(b.dataset.screen);
    };
  });

  // Zé do Chapéu (em Coordenadores)
  $('buy-zé').onclick = buyZe;

  renderRates();
  renderMap();
  renderLeadPacks();
  renderArchive();
  renderCommercial();
}

// ---------- sheets (config / phone / commercial) ----------
function toggleSheet(id) {
  const s = $(id);
  const showing = !s.classList.contains('hidden');
  hideSheets();
  if (!showing) s.classList.remove('hidden');
}
function hideSheet(id) { $(id).classList.add('hidden'); }
function hideSheets() {
  ['settings-sheet', 'phone-sheet'].forEach((id) => {
    const s = $(id);
    if (s) s.classList.add('hidden');
  });
}
function openCommercial() { $('screen-commercial').classList.remove('hidden'); }
function closeCommercial() { $('screen-commercial').classList.add('hidden'); }

// ---------- navegação ----------
function go(screenId) {
  if (screenId === 'screen-commercial') { openCommercial(); return; }
  currentScreen = screenId;
  document.querySelectorAll('.screen').forEach((s) => s.classList.toggle('active', s.id === screenId));
  document.querySelectorAll('.nav-btn').forEach((b) => b.classList.toggle('active', b.dataset.screen === screenId));
  renderScreen(screenId);
}

function renderScreen(id) {
  if (id === 'screen-sede') { renderMapHeader(); buildProducerRows(); renderClickUpgrade(); updateProducerRows(); }
  if (id === 'screen-managers') renderManagers();
  if (id === 'screen-clones') renderClones();
  if (id === 'screen-zap') renderZap();
  if (id === 'screen-lodge') { renderLodge(); renderGlobalUpgrades(); }
  if (id === 'screen-shop') renderShop();
  if (id === 'screen-map') renderMap();
  if (id === 'screen-lead') renderLeadPacks();
  if (id === 'screen-archive') renderArchive();
}

function renderAll() {
  renderHUD();
  renderScreen(currentScreen);
}

/** Desbloqueio progressivo dos botões inferiores (paridade de referência). */
function updateNav() {
  const locks = {
    'screen-managers': () => !state.managersUnlocked(),
    'screen-clones': () => !state.clonesUnlocked(),
    'screen-lodge': () => !state.prestigeUnlocked(),
  };
  document.querySelectorAll('.nav-btn').forEach((b) => {
    const guard = locks[b.dataset.screen];
    b.classList.toggle('locked', guard ? guard() : false);
  });
}

// ---------- clique principal ----------
function doClick(x, y, fromRound = false) {
  const gain = state.click(performance.now());
  SFX.click();
  Analytics.track('click_main', { combo: state.comboSteps, source: fromRound ? 'round' : 'panel' });
  const anchor = $('click-panel');
  spawnFloater(anchor, `+${fmt(gain)} 🧠`, { x: Math.max(20, x), y: Math.max(10, y), cls: 'credit' });
  spawnPhone(anchor, { x: Math.max(24, x), y: Math.max(10, y) });
  renderHUD();
}

// ---------- produtores ----------
// Cabeçalho do mapa ativo (nome, fase "missão X de Y", missão final em destaque)
function renderMapHeader() {
  const map = state.activeMap();
  const name = $('map-header-name');
  const progress = $('map-header-progress');
  const gate = $('map-header-gate');
  if (name && map) name.textContent = `${map.icon || ''} ${map.name}`;
  if (progress) {
    const done = state.producerList().filter((p) => (state.producers[p.id] || 0) > 0).length;
    progress.textContent = `missão ${Math.min(done + 1, state.producerList().length)} de ${state.producerList().length}`;
  }
  if (gate) {
    const g = state.pendingGate(state.activeMapId());
    if (g) gate.innerHTML = `<span class="gate-ico">🚩</span> Missão final: <b>${g.icon || ''} ${g.name}</b> — ao concluir, libera o próximo mapa.`;
    else gate.innerHTML = '<span class="gate-ico">✅</span> Mapa concluído! O próximo mapa foi liberado.';
  }
  renderMapStrip();
}

// ---------- faixa de mapas ----------
// Faixa horizontal no topo: nome do mapa ativo no centro, setas nas pontas ciclam
// os 4 mapas (Deep Web ↔ Democracia Relativa ↔ Ratanabá ↔ Religião). Revisitável.
function renderMapStrip() {
  const pop = $('map-strip');
  if (!pop) return;
  const info = state.phaseInfo();
  const active = info[state.activePhaseIndex()] || info[0] || null;
  if (!active) return;
  $('map-strip-ico').textContent = active.icon || '🗺️';
  $('map-strip-name').textContent = active.name;
  const done = state.producerList().filter((p) => (state.producers[p.id] || 0) > 0).length;
  $('map-strip-sub').textContent = `missão ${Math.min(done + 1, state.producerList().length)} de ${state.producerList().length}`;
  pop.style.setProperty('--pc', active.color || '#D4AF37');
  // setas: estado de liberado/travado
  const prev = info[(state.activePhaseIndex() - 1 + info.length) % info.length];
  const next = info[(state.activePhaseIndex() + 1) % info.length];
  const nb = $('map-next');
  const pb = $('map-prev');
  if (nb) { nb.classList.toggle('locked', !next || !next.unlocked); }
  if (pb) { pb.classList.toggle('locked', !prev || !prev.unlocked); }
}

function cycleMap(dir) {
  const info = state.phaseInfo();
  const idx = (state.activePhaseIndex() + dir + info.length) % info.length;
  const target = info[idx];
  if (!target || !target.unlocked) {
    toast(`🔒 ${target ? target.name : 'Mapa'} bloqueado. Conclua a missão final do mapa anterior.`);
    return;
  }
  if (state.setActivePhase(idx)) {
    SFX.stamp();
    Analytics.track('map_cycle', { to: target.id, dir });
    buildProducerRows();
    renderMapHeader();
    updateProducerRows();
    renderHUD();
  }
}

function buildProducerRows() {
  const wrap = $('producers');
  wrap.innerHTML = '';
  for (const def of state.producerList()) wrap.appendChild(buildProducerRow(def));
}

function buildProducerRow(def) {
  const id = def.id;
  const owned = state.ownedOf(id);
  const starLvl = state.starLevelOf(id);
  const automated = state.isAutomated(id);
  const manager = state.managerList().find((m) => m.producer === id);
  const clone = state.cloneOf(id);

  const isGate = state.isGateProducer(state.activeMapId(), id);
  const row = el('div', 'producer' + (isGate && owned <= 0 ? ' gate' : ''));
  row.dataset.id = id;

  // moldura + animação (emoji como placeholder de arte original)
  const frame = el('div', 'prod-frame');
  const anim = el('div', 'prod-anim' + (automated ? ' automated' : ''), def.icon || '🏢');
  anim.style.animationDelay = `-${(def.slot * 0.7).toFixed(2)}s`;
  frame.appendChild(anim);
  row.appendChild(frame);

  const body = el('div', 'prod-body');
  // nome + estrelas (canto sup. direito)
  const top = el('div', 'prod-line1');
  if (isGate) {
    const nameWrap = el('div', 'producer-name');
    nameWrap.innerHTML = `${def.name} <span class="gate-tag">🚩 FINAL</span>`;
    top.appendChild(nameWrap);
  } else {
    top.appendChild(el('div', 'producer-name', def.name));
  }
  top.appendChild(starBadge(starLvl));
  body.appendChild(top);
  // dono / renda
  body.appendChild(el('div', 'producer-owned',
    `possuídos: <b>${owned}</b> · +${fmt(BigNumber.fromNumber(def.valuePerCycle).scale(Math.max(owned, 0)).mul(state.producerMult(id)))} 🧠/${def.cycleSeconds}s`));
  if (def.flavor) body.appendChild(el('div', 'producer-flavor', def.flavor));

  // linha inferior: timer (esq) + upgrade/tanque (dir)
  const bottom = el('div', 'prod-line2');
  const timer = el('div', 'prod-timer', automated ? '⏱ 0s' : `⏱ ${def.cycleSeconds}s`);
  bottom.appendChild(timer);
  const right = el('div', 'prod-right');
  const upg = el('button', 'mini-icon', '🛠');
  upg.title = 'Melhorar (Loja de Melhorias)';
  upg.onclick = () => { shopTarget = def.id; go('screen-shop'); };
  right.appendChild(upg);
  const tank = el('button', 'mini-icon tank' + (clone ? ' filled' : ''), clone ? '🧫' : '🧪');
  tank.title = clone ? `Sósia: ${clone.name} (×${clone.mult})` : 'Tanque de sósia vazio';
  tank.onclick = () => go('screen-clones');
  right.appendChild(tank);
  bottom.appendChild(right);
  body.appendChild(bottom);
  row.appendChild(body);

  // buy modes sempre presentes (linha cheia)
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
  body.appendChild(actions);

  // coletar (manual) — aparece quando há lucro pronto
  const colBtn = el('button', 'collect-btn hidden', `COLETAR <b>+0</b> 🧠`);
  colBtn.onclick = () => collectProducer(id);
  body.appendChild(colBtn);

  // coordenador inline
  const mgrRow = el('div', 'prod-manager');
  if (manager) {
    if (automated) {
      mgrRow.appendChild(el('span', '', `🕴️ ${manager.icon || ''} ${manager.name} automatiza.`));
    } else {
      const cost = big(manager.cost);
      mgrRow.appendChild(el('span', '', `🕴️ ${manager.icon || ''} <b>${manager.name}</b> — ${fmt(cost)} 🧠`));
      const hire = el('button', 'mini-btn hire', 'CONTRATAR');
      hire.disabled = state.credits.lt(cost);
      hire.onclick = () => hireManager(manager.id, id);
      mgrRow.appendChild(hire);
    }
  }
  body.appendChild(mgrRow);
  return row;
}

function starBadge(level) {
  // paridade: 5 ★ bronze = 1 ★ prata; 5 pratas = 1 ouro (§30 da referência)
  const badge = el('span', 'stars');
  if (level <= 0) { badge.textContent = '☆'; return badge; }
  let lvl = level;
  let gold = 0, silver = 0, bronze = 0;
  while (lvl >= 25) { gold += 1; lvl -= 25; }
  while (lvl >= 5) { silver += 1; lvl -= 5; }
  bronze = lvl;
  const parts = [];
  parts.push(`<span class="s-gold">${'★'.repeat(gold)}</span>`);
  parts.push(`<span class="s-silver">${'★'.repeat(silver)}</span>`);
  parts.push(`<span class="s-bronze">${'★'.repeat(Math.max(bronze, (gold + silver === 0 && level > 0 ? 1 : 0)))}</span>`);
  badge.innerHTML = parts.join('') || '☆';
  return badge;
}

function updateProducerRows() {
  for (const def of state.producerList()) {
    const row = document.querySelector(`.producer[data-id="${def.id}"]`);
    if (!row) continue;
    const owned = state.ownedOf(def.id);
    const automated = state.isAutomated(def.id);
    const starLvl = state.starLevelOf(def.id);
    row.querySelector('.producer-owned').innerHTML =
      `possuídos: <b>${owned}</b> · +${fmt(BigNumber.fromNumber(def.valuePerCycle).scale(Math.max(owned, 0)).mul(state.producerMult(def.id)))} 🧠/${def.cycleSeconds}s`;
    // estrelas
    const badgeEl = row.querySelector('.stars');
    if (badgeEl) badgeEl.replaceWith(starBadge(starLvl));
    // timer de ciclo
    row.querySelector('.prod-timer').textContent = automated ? '⏱ 0s' : `⏱ ${def.cycleSeconds}s`;
    // anim automático
    const anim = row.querySelector('.prod-anim');
    if (anim) anim.classList.toggle('automated', automated);
    // buy buttons
    for (const b of row.querySelectorAll('.buy-btn')) {
      const mode = Number(b.dataset.mode);
      const qty = mode === -1 ? state.maxBuy(def.id) : mode;
      const cost = Economy.buyCost(def.baseCost, state.eco.producerGrowthRate, owned, qty);
      b.querySelector('span').textContent = fmt(cost);
      b.disabled = qty <= 0 || state.credits.lt(cost);
    }
    // coletar
    const acc = state.collectables[def.id];
    const colBtn = row.querySelector('.collect-btn');
    if (!automated && acc && !acc.isZero()) {
      colBtn.innerHTML = `COLETAR <b>+${fmt(acc)}</b> 🧠`;
      colBtn.classList.remove('hidden');
    } else {
      colBtn.classList.add('hidden');
    }
    // contratar
    const hire = row.querySelector('.mini-btn.hire');
    if (hire) {
      const manager = state.managerList().find((m) => m.producer === def.id);
      hire.disabled = state.credits.lt(big(manager.cost));
    }
    // tanque
    const clone = state.cloneOf(def.id);
    const tank = row.querySelector('.mini-icon.tank');
    if (tank) {
      tank.classList.toggle('filled', !!clone);
      tank.textContent = clone ? '🧫' : '🧪';
      tank.title = clone ? `Sósia: ${clone.name} (×${clone.mult})` : 'Tanque de sósia vazio';
    }
  }
  // comprar tudo (Zé)
  const hasZe = state.hasBuyAllManager();
  const ba = $('buy-all-btn');
  ba.classList.toggle('hidden', !hasZe);
  ba.innerHTML = '👔 comprar tudo';
  const holder = $('buy-all-holder');
  if (holder && !hasZe) holder.title = 'Contrate o Zé do Chapéu de Alumínio (10 Convictos) para liberar';
}

function buyProducer(id, mode) {
  const qty = mode === -1 ? state.maxBuy(id) : mode;
  if (qty <= 0) return;
  const res = state.buyProducer(id, qty);
  if (res.ok) {
    SFX.buy();
    Analytics.track('producer_buy', { producer_id: id, qty });
    if (res.advanced && res.advanced.moved) {
      // concluiu a missão final do mapa → novo mapa (spec §82)
      const map = state.activeMap();
      SFX.giant();
      toast(`🚩 DESBLOQUEADO: ${map ? map.icon + ' ' + map.name : 'novo mapa'}!`);
      persist();
      buildProducerRows();
      renderMapHeader();
    }
    updateProducerRows();
    renderMapStrip();
    renderHUD();
  } else if (res.reason === 'cost') {
    toast('Faltam Mentes. 🧠');
  }
}

function collectProducer(id) {
  const got = state.collect(id);
  if (!got.isZero()) {
    SFX.buy();
    Analytics.track('collect', { producer_id: id });
    updateProducerRows();
    renderHUD();
  }
}

function hireManager(mgrId, producerId) {
  const res = state.buyManager(mgrId);
  if (res.ok) {
    SFX.message();
    Analytics.track('manager_buy', { manager_id: mgrId });
    toast('Coordenador contratado! 🕴️');
    buildProducerRows();
    updateNav();
    renderHUD();
  } else if (res.reason === 'cost') {
    toast('Faltam Mentes. 🧠');
  }
}

function buyAll() {
  if (!state.hasBuyAllManager()) { go('screen-managers'); toast('Contrate o Zé do Chapéu de Alumínio (10 Convictos).'); return; }
  const n = state.buyAll();
  if (n > 0) { SFX.stamp(); Analytics.track('buy_all', { lots: n }); updateProducerRows(); renderHUD(); }
  else toast('Nada comprável agora.');
}

// ---------- coordenadores ----------
function renderManagers() {
  const wrap = $('managers-list');
  wrap.innerHTML = '';
  // apenas Coordenadores das missões do mapa ativo
  const activeProducers = new Set(state.producerList().map((p) => p.id));
  for (const m of state.managerList()) {
    if (!activeProducers.has(m.producer)) continue;
    const def = state.producerDef(m.producer);
    const owned = state.hasManager(m.id);
    const cost = big(m.cost);
    const row = el('div', 'mgr-row' + (owned ? ' owned' : ''));
    row.appendChild(el('div', 'mgr-icon', m.icon || '🕴️'));
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
  const ze = state.buyAllManagerDef();
  const hasZe = state.hasBuyAllManager();
  const zeBtn = $('buy-zé');
  if (zeBtn) {
    zeBtn.disabled = hasZe;
    zeBtn.textContent = hasZe ? `👔 ${ze.name} — contratado (comprar tudo liberado)` : `👔 ${ze.name} — comprar tudo (${ze.cost} Convictos)`;
  }
}

function buyZe() {
  const res = state.buyBuyAllManager();
  if (res.ok) { SFX.stamp(); Analytics.track('buy_all_manager'); toast('Zé contratado! Comprar tudo liberado. 🥫👔'); renderHUD(); renderManagers(); updateProducerRows(); }
  else if (res.reason === 'cost') toast('O Zé custa 10 Convictos. Acorde o Gigante primeiro! 🌋');
  else if (res.reason === 'owned') toast('O Zé já é da casa.');
}

// ---------- sósias ----------
function renderRates() {
  const wrap = $('clone-rates');
  wrap.innerHTML = '';
  const total = state.cloneRarities().reduce((a, r) => a + r.weight, 0);
  for (const r of state.cloneRarities()) {
    const pct = Math.round((r.weight / total) * 100);
    wrap.appendChild(el('div', 'rate-chip', `<b>${r.name}</b> ×${r.mult} <span>${pct}%</span>`));
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
  const activeProducers = new Set(state.producerList().map((p) => p.id));
  const ownedIds = Object.keys(state.clones).filter((pid) => activeProducers.has(pid));
  if (ownedIds.length === 0) {
    wrap.appendChild(el('div', 'empty-note', 'Nenhum sósia neste mapa ainda. Abra o primeiro tanque (grátis)!'));
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
  if (!res.ok) { if (res.reason === 'cost') toast('Falta Chumbo. Veja a Loja de Chumbo. 🥫'); return; }
  SFX.giant();
  Analytics.track('clone_open', { rarity: res.rarity.id, duplicate: res.duplicate, free: res.free });
  const def = state.producerDef(res.clone.producer);
  $('clone-reveal-rarity').textContent = res.rarity.name.toUpperCase();
  $('clone-reveal-rarity').className = 'reveal-rarity ' + res.rarity.id;
  $('clone-reveal-icon').textContent = def ? def.icon : '🕵️';
  $('clone-reveal-name').textContent = res.clone.name;
  $('clone-reveal-line').textContent = res.clone.line || '';
  $('clone-reveal-eff').textContent = res.duplicate
    ? 'Duplicata! Vira Puxa-Saco: +1% de produção global. 🙇'
    : `×${res.rarity.mult} em “${def ? def.name : res.clone.producer}”`;
  $('clone-modal').classList.remove('hidden');
  renderClones();
  renderHUD();
}

// ---------- zap vazado (fone / tela) ----------
function renderZap() {
  if (!lastZap) nextZap();
  $('zap-sender').textContent = `📲 ${lastZap.sender}`;
  $('zap-text').textContent = lastZap.text;
  $('zap-buttons').classList.remove('hidden');
  renderZapMeter();
}

function nextZap() {
  const pool = state.zapMessages();
  lastZap = pool[Math.floor(Math.random() * pool.length)];
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
  bits.push(res.correct ? `✅ Certeiro! Streak ×${state.zapStreak}` : '⛔ Errou. Streak zerado.');
  if (r.credits && !r.credits.isZero()) bits.push(`+${fmt(r.credits)} 🧠`);
  if (r.chumbo) bits.push(`+${r.chumbo} 🥫`);
  toast(bits.join(' · '));
  nextZap();
  renderZapMeter();
  renderPhoneSheet();
  renderHUD();
}

// ---------- círculo interno (prestígio) ----------
function renderLodge() {
  $('stat-credits').textContent = fmt(state.credits);
  $('stat-convictos').textContent = String(state.convictos);
  $('stat-pps').textContent = fmt(state.productionPerSecond());
  $('stat-puxasacos').textContent = String(state.puxasacos);
  const gained = Prestige.convictosFrom(state.lifetimeCredits, state.prestigeParams(), state.convictos);
  $('lodge-gain').textContent = `+${gained}` + (loyaltyBump > 0 ? ` <span class="tag">+${loyaltyBump}% anúncio</span>` : '');
}

function openGiantBomb() {
  const gained = Prestige.convictosFrom(state.lifetimeCredits, state.prestigeParams(), state.convictos);
  $('prestige-gain').textContent = `+${gained} Convictos 🙇`;
  $('prestige-confirm').disabled = gained <= 0;
  $('prestige-modal').classList.remove('hidden');
}

function confirmPrestige() {
  const res = Prestige.prestige(state, state.prestigeParams());
  if (res.ok) {
    state = new GameState(config, res.snapshot);
    if (loyaltyBump > 0) {
      const extra = Math.max(1, Math.floor(res.gained * loyaltyBump / 100));
      state.convictos += extra;
      toast(`+${extra} Convictos de anúncio! 📺`);
    }
    loyaltyBump = 0;
    SFX.giant();
    Analytics.track('prestige_complete', { prestige_number: state.convictos });
    closePrestige();
    showWake();
    shopTarget = null;
    buildProducerRows();
    renderAll();
    persist();
  }
}

function openGiantLoyalty() {
  const gained = Prestige.convictosFrom(state.lifetimeCredits, state.prestigeParams(), state.convictos);
  $('loyalty-gain').textContent = `+${gained} Convictos`;
  $('loyalty-confirm').disabled = gained <= 0 || state.chumbo < 10;
  $('loyalty-modal').classList.remove('hidden');
}

function confirmLoyalty() {
  const res = state.buyLoyalty();
  if (res.ok) {
    SFX.giant();
    Analytics.track('prestige_loyalty', { gained: res.gained });
    toast(`Lealdade comprada! +${res.gained} Convictos, sem perder nada. 💎`);
    closeLoyalty();
    renderAll();
    persist();
  } else if (res.reason === 'cost') {
    toast('Faltam 10 🥫 (Chumbo).');
    closeLoyalty();
  }
}

function closePrestige() { $('prestige-modal').classList.add('hidden'); }
function closeLoyalty() { $('loyalty-modal').classList.add('hidden'); }

function showWake() {
  const w = $('giant-wake');
  w.classList.remove('hidden');
  w.classList.remove('run');
  void w.offsetWidth;
  w.classList.add('run');
  setTimeout(() => w.classList.add('hidden'), 2200);
}

// ---------- melhorias globais ----------
function renderGlobalUpgrades() {
  const wrap = $('global-upgrades');
  wrap.innerHTML = '';
  const list = config.upgrades?.global || [];
  for (const u of list) {
    const owned = (state.upgrades[u.id] || 0) > 0;
    const cost = big(u.cost);
    const row = el('div', 'mgr-row' + (owned ? ' owned' : ''));
    row.appendChild(el('div', 'mgr-icon', u.icon || '✨'));
    const info = el('div', 'mgr-info');
    info.appendChild(el('div', 'mgr-name', u.name));
    info.appendChild(el('div', 'mgr-target', `${u.desc || u.label || ''} · ×${u.mult} produção`));
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
    const tDef = state.producerList().find((p) => p.slot === shopTarget || p.id === shopTarget);
    charge.classList.remove('hidden');
    $('shop-target').textContent = tDef ? `${tDef.icon} ${tDef.name}` : String(shopTarget);
  } else {
    charge.classList.add('hidden');
  }
  // melhorias das MISSÕES DO MAPA ATIVO (paridade: cada missão tem sua melhoria ×3)
  for (const def of state.producerList()) {
    const lvl = state.upgradeLevelOf(def.id);
    const cfg = state._producerUpgradeDef(def.id) || null;
    const costs = cfg ? cfg.costs : [25000, 5e7, 2.5e11, 1.25e15, 6.25e18];
    const mult = cfg ? cfg.mult : 3;
    const maxed = lvl >= costs.length;
    const row = el('div', 'mgr-row' + (maxed ? ' owned' : '') + (shopTarget === def.slot || shopTarget === def.id ? ' highlight' : ''));
    row.appendChild(el('div', 'mgr-icon', def.icon || '🛠'));
    const info = el('div', 'mgr-info');
    info.appendChild(el('div', 'mgr-name', `${def.name}`));
    info.appendChild(el('div', 'mgr-target', maxed ? 'nível máximo' : `nível ${lvl}/${costs.length} · próximo: ×${mult} por ${fmt(big(costs[lvl]))} 🧠`));
    row.appendChild(info);
    if (!maxed) {
      const b = el('button', 'mini-btn hire', 'MELHORAR');
      b.disabled = state.credits.lt(big(costs[lvl]));
      b.onclick = () => {
        const r = state.buyProducerUpgrade(def.id);
        if (r.ok) { SFX.stamp(); Analytics.track('upgrade_buy', { type: 'producer', id: def.id }); renderShop(); renderHUD(); }
      };
      row.appendChild(b);
    } else {
      row.appendChild(el('span', 'mgr-owned', '✓ max'));
    }
    wrap.appendChild(row);
  }
  renderShopClicks();
}

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
    info.appendChild(el('div', 'mgr-target', `poder ${fmt(state.clickPower())} 🧠/toque`));
    row.appendChild(info);
    if (next) {
      const cost = big(next.cost);
      info.appendChild(el('div', 'mgr-target', `próximo: “${next.name}” por ${fmt(cost)} 🧠`));
      const b = el('button', 'mini-btn hire', 'UPGRADE');
      b.disabled = state.credits.lt(cost);
      b.onclick = () => {
        const r = state.buyClickUpgrade();
        if (r.ok) { SFX.stamp(); Analytics.track('upgrade_buy', { type: 'click', level: r.level }); renderShopClicks(); renderClickUpgrade(); renderHUD(); }
      };
      row.appendChild(b);
    }
    wrap.appendChild(row);
  }
}

function renderClickUpgrade() {
  const box = $('click-upgrade');
  const current = state.clickLevels().find((l) => l.level === state.clickLevel);
  const next = state.nextClickLevel();
  if (current) {
    $('click-lvl-name').textContent = current.name;
    $('click-lvl-power').textContent = `poder: ${fmt(state.clickPower())} 🧠`;
  }
  if (next) {
    const cost = big(next.cost);
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

// ---------- mapa ----------
function renderMap() {
  const wrap = $('map-list');
  wrap.innerHTML = '';
  const info = state.phaseInfo();
  for (const p of info) {
    const locked = !p.unlocked;
    const card = el('div', 'map-card' + (p.active ? ' current' : '') + (locked ? ' locked' : '') + (p.completed ? ' done' : ''));
    card.style.setProperty('--pc', p.color || '#D4AF37');
    card.appendChild(el('div', 'map-icon', p.icon || '🗺️'));
    card.appendChild(el('div', 'map-name', p.name));
    card.appendChild(el('div', 'map-flavor', p.flavor || ''));
    let status;
    if (p.active && p.gate) status = `🎯 missão final: ${p.gate.name}`;
    else if (p.active) status = '📍 você está aqui';
    else if (p.completed) status = '✓ dominado (pode revisitar)';
    else if (locked) status = `🔒 conclua o mapa anterior`;
    else status = '✔ liberado';
    card.appendChild(el('div', 'map-threshold', status));
    if (p.active && p.gate) {
      const b = el('button', 'mini-btn hire', `IR PARA A MISSÃO: ${p.gate.icon || ''} ${p.gate.name}`);
      b.onclick = () => { go('screen-sede'); };
      card.appendChild(b);
    }
    wrap.appendChild(card);
  }
}

// ---------- loja de chumbo ----------
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
      Analytics.track('iap_dev', { pack: p.id });
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

// ---------- anúncios simulados (§92, dev: nunca anúncios reais) ----------
const BONUS_DEFS = {
  warp2: { icon: '⏩', title: 'Buraco de Minhoca', desc: 'Ganhe +2h de produção instantânea.' },
  warp4: { icon: '🌀', title: 'Buraco de Minhoca XL', desc: 'Ganhe +4h de produção instantânea.' },
  x5: { icon: '⚡', title: 'Viral de 5×', desc: 'Produção ×5 por 260 segundos.' },
  double: { icon: '👥', title: 'Convittes Dobrados', desc: '+50% de Convictos no próximo Despertar.' },
};

function renderCommercial() {
  $('ad-warp2').onclick = () => watchAd('warp2');
  $('ad-warp4').onclick = () => watchAd('warp4');
  $('ad-x5').onclick = () => watchAd('x5');
  $('ad-double').onclick = () => watchAd('double');
}

function watchAd(kind) {
  SFX.stamp();
  Analytics.track('rewarded_complete', { placement: kind, simulated: true });
  switch (kind) {
    case 'warp2': { const g = state.productionPerSecond().scale(WARP2_SECONDS); state.credits = state.credits.add(g); state.lifetimeCredits = state.lifetimeCredits.add(g); toast(`Buraco de Minhoca: +${fmt(g)} 🧠`); break; }
    case 'warp4': { const g = state.productionPerSecond().scale(WARP4_SECONDS); state.credits = state.credits.add(g); state.lifetimeCredits = state.lifetimeCredits.add(g); toast(`Buraco XL: +${fmt(g)} 🧠`); break; }
    case 'x5': state.applyBoost(5, 260); toast('Viral de 5× ativo por 260s! ⚡'); break;
    case 'double': loyaltyBump = 50; toast('+50% de Convictos no próximo Despertar! 👥'); break;
  }
  closeCommercial();
  schedulePhoneShakeIfNeeded();
  renderHUD();
}

// cronômetro permanente (paridade: boost ×2 empilhável — cada uso SOMA tempo)
function doBoost() {
  if (state.chumbo < 1) { toast('Custa 1 🥫 (Chumbo). Veja a Loja de Chumbo.'); return; }
  state.chumbo -= 1;
  if (state.boostRemaining() > 0) state.extendBoost(250); // paridade: empilha duração
  else state.applyBoost(2, 250);
  SFX.buy();
  Analytics.track('boost_watch', { simulated: true });
  toast('Boost ×2 ativo (empilha)! ⏱️');
  renderHUD();
}

/** Bônus aleatório aparece no fone após um tempo (paridade: fone notifica). */
function installBonusSoon() {
  if (!notifEnabled) return;
  setTimeout(() => {
    if (document.hidden) return;
    const keys = Object.keys(BONUS_DEFS);
    const kind = keys[Math.floor(Math.random() * keys.length)];
    adOffer = BONUS_DEFS[kind];
    showBonus(adOffer, kind);
    schedulePhoneShake(4000);
  }, 20000);
}

function showBonus(def, kind) {
  $('bonus-icon').textContent = def.icon;
  $('bonus-title').textContent = def.title;
  $('bonus-desc').textContent = def.desc;
  $('bonus-sub').textContent = 'Assistir um anúncio (simulado) para resgatar.';
  $('bonus-accept').onclick = () => { $('bonus-modal').classList.add('hidden'); watchAd(kind); };
  $('bonus-decline').onclick = () => { $('bonus-modal').classList.add('hidden'); adOffer = null; };
  $('bonus-modal').classList.remove('hidden');
}

function renderPhoneSheet() {
  const body = $('phone-sheet-body');
  body.innerHTML = '';
  if (adOffer) {
    const row = el('button', 'comm-row mini');
    row.innerHTML = `<span>${adOffer.icon}</span><div><b>${adOffer.title}</b><small>${adOffer.desc}</small></div>`;
    const keys = Object.keys(BONUS_DEFS);
    const kind = keys.find((k) => BONUS_DEFS[k] === adOffer) || 'x5';
    row.onclick = () => { hideSheet('phone-sheet'); showBonus(adOffer, kind); };
    body.appendChild(row);
  }
  // zap vazado inline (wiretap)
  if (!lastZap) nextZap();
  const zapRow = el('div', 'comm-zap');
  zapRow.innerHTML = `<div class="zap-sender">📲 ${lastZap.sender}</div><p>${lastZap.text}</p>`;
  const acts = el('div', 'zap-actions');
  const ap = el('button', 'btn-approve', '✅');
  ap.onclick = () => decideZap(true);
  const dn = el('button', 'btn-deny', '⛔');
  dn.onclick = () => decideZap(false);
  acts.appendChild(ap); acts.appendChild(dn);
  zapRow.appendChild(acts);
  body.appendChild(zapRow);
}

// ---------- fone tremendo (§88) ----------
function schedulePhoneShakeIfNeeded() { if (notifEnabled) schedulePhoneShake(3000); }
function schedulePhoneShake(ms) {
  clearTimeout(phoneShakeTimer);
  const btn = $('phone-btn');
  btn.classList.add('ringing');
  $('phone-badge').classList.remove('hidden');
  phoneShakeTimer = setTimeout(() => btn.classList.remove('ringing'), ms);
}

// ---------- config ----------
function cycleFormat() {
  const order = ['short', 'full', 'scientific'];
  numberFormat = order[(order.indexOf(numberFormat) + 1) % order.length];
  $('format-label').textContent = { short: 'abrev.', full: 'completo', scientific: 'cient.' }[numberFormat];
  renderAll();
}

function toggleSound() {
  SFX.toggleMuted();
  $('sound-ico').textContent = SFX.muted ? '🔇' : '🔊';
}

function toggleNotif() {
  notifEnabled = !notifEnabled;
  $('notif-ico').textContent = notifEnabled ? '🔔' : '🔕';
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
  loyaltyBump = 0;
  buildProducerRows();
  renderAll();
  persist();
  toast('Progresso apagado. Recomeçando do zero. 🫡');
}

// ---------- HUD ----------
function renderHUD() {
  state.expireBoost();
  $('credits').textContent = fmt(state.credits);
  $('chumbo').textContent = String(state.chumbo);
  $('convictos').textContent = String(state.convictos);
  $('pps').textContent = `${fmt(state.productionPerSecond())} 🧠/s`;
  $('combo').textContent = `viral ×${state.viralMultiplier(performance.now()).toFixed(1)}`;
  // cronômetro de boost
  const rem = state.boostRemaining();
  const sw = $('stopwatch-btn');
  sw.classList.toggle('active', rem > 0);
  $('stopwatch-timer').textContent = rem > 0 ? fmtBoost(rem) : '×2';
  updateNav();
}

function fmtBoost(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h${m}m`;
  if (m > 0) return `${m}m`;
  return `${s}s`;
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

// ---------- persistência ----------
function persist() {
  const str = serialize(state);
  const prev = localStorage.getItem(SAVE_KEY);
  if (prev) localStorage.setItem(SAVE_BACKUP_KEY, prev);
  localStorage.setItem(SAVE_KEY, str);
  showSaveFlash();
}

let flashTimer = null;
function showSaveFlash() {
  const elx = $('save-flash');
  elx.classList.add('show');
  clearTimeout(flashTimer);
  flashTimer = setTimeout(() => elx.classList.remove('show'), 700);
}

function toast(msg) {
  const elx = $('toast');
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

boot();

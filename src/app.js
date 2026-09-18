/**
 * O GIGANTE DESPERTOU — PLAYABLE CORE (M0, spec §325).
 * Camada de apresentação (descartável na porta Unity). Só dispara comandos no
 * GameState e renderiza; nunca calcula economia.
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
const MAX_PRODUCERS = 4; // PLAYABLE CORE (§246–§247)

let config, state;
let numberFormat = 'short'; // 'full' | 'short' | 'scientific' (§21)
let lastFrame = performance.now();
let saveTimer = 0;
let offlinePending = null;

const ui = {}; // referências DOM

function $(id) { return document.getElementById(id); }

async function boot() {
  config = await loadConfigWeb({ maxProducers: MAX_PRODUCERS });
  state = hydrateState();
  bindUI();
  applyOfflineOnStart();
  Analytics.track('first_open', { version: 1 });
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
  const cuando = h > 0 ? `${h}h ${m}min` : `${m}min`;
  $('offline-text').textContent = `Enquanto você sumiu (${cuando}), a operação convenceu ${res.gained.format(numberFormat)} pessoas.`;
  $('offline-double').onclick = () => {
    // DUPLICAR RELATÓRIO — rewarded (stub no core; produção: anúncio)
    state.credits = state.credits.add(res.gained);
    Analytics.track('rewarded_complete', { placement: 'offline_2x' });
    toast('Relatório duplicado! 📄');
    $('offline-report').classList.add('hidden');
    render();
  };
  $('offline-close').onclick = () => $('offline-report').classList.add('hidden');
}

// ---------- UI bindings ----------
function bindUI() {
  // mantém referências
  for (const id of ['credits', 'chumbo', 'pps', 'combo', 'click-panel', 'producers', 'click-upgrade', 'satire-note', 'toast', 'save-flash']) {
    ui[id] = $(id);
  }

  // botão central: Compartilhar no Zap
  const clickZone = $('click-zone');
  clickZone.addEventListener('pointerdown', (e) => {
    const r = clickZone.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    doClick(x, y);
  });

  // produtores (render dinâmico)
  renderProducers();

  // botões de formatação / settings rápidas
  bindSettings();
}

function doClick(x, y) {
  const gain = state.click(performance.now());
  SFX.click();
  Analytics.track('click_main', { combo: state.comboSteps });
  spawnFloater(ui['click-panel'], `+${gain.format(numberFormat)} 👁`, { x, y, cls: 'credit' });
  spawnPhone(ui['click-panel'], { x: x + 8, y: y - 14 });
  render();
}

function renderProducers() {
  const wrap = ui.producers;
  wrap.innerHTML = '';
  for (const def of state.producerList()) {
    wrap.appendChild(buildProducerRow(def));
  }
}

function buildProducerRow(def) {
  const row = document.createElement('div');
  row.className = 'producer';
  row.dataset.id = def.id;

  const info = document.createElement('div');
  info.className = 'producer-info';
  info.innerHTML = `
    <div class="producer-name">${def.name}</div>
    <div class="producer-owned">possuídos: <b>${state.producers[def.id] || 0}</b> ${milestoneLabel(def.id)}</div>
    <div class="producer-flavor">${def.flavor || ''}</div>
  `;
  row.appendChild(info);

  const actions = document.createElement('div');
  actions.className = 'producer-actions';
  const buyModes = [1, 10, 25, 100, -1];
  for (const mode of buyModes) {
    const btn = document.createElement('button');
    btn.className = 'buy-btn';
    btn.dataset.mode = mode;
    const qty = mode === -1 ? state.maxBuy(def.id) : mode;
    const cost = costFor(def.id, qty);
    const label = mode === -1 ? 'MAX' : `x${mode}`;
    btn.innerHTML = `${label}<span>${cost}</span>`;
    btn.disabled = qty <= 0 || state.credits.lt(costFor(def.id, qty));
    btn.onclick = () => buyProducer(def.id, mode);
    actions.appendChild(btn);
  }
  row.appendChild(actions);
  return row;
}

function costFor(id, qty) {
  const def = state.producerDef(id);
  const owned = state.producers[id] || 0;
  return Economy.buyCost(def.baseCost, state.eco.producerGrowthRate, owned, qty).format(numberFormat);
}

function milestoneLabel(id) {
  const ms = state.milestonesFor(id);
  return ms.length ? `<span class="milestone" title="milestones">★×${ms.reduce((a, b) => a * b.factor, 1)}</span>` : '';
}

function buyProducer(id, mode) {
  const def = state.producerDef(id);
  const owned = state.producers[id] || 0;
  const qty = mode === -1 ? state.maxBuy(id) : mode;
  if (qty <= 0) return;
  const cost = Economy.buyCost(def.baseCost, state.eco.producerGrowthRate, owned, qty);
  if (cost.gt(state.credits)) return;
  const res = state.buyProducer(id, qty);
  if (res.ok) {
    SFX.buy();
    Analytics.track('producer_buy', { producer_id: id, qty });
    renderProducers();
    renderHUD();
  }
}

function bindSettings() {
  $('format-full').onclick = () => setFormat('full');
  $('format-short').onclick = () => setFormat('short');
  $('format-sci').onclick = () => setFormat('scientific');
  $('sound-toggle').onclick = (e) => {
    const off = e.currentTarget.classList.toggle('off');
    SFX.setMuted(off);
  };
  $('prestige-btn').onclick = doPrestige;
  renderClickUpgrade();
}

function setFormat(m) {
  numberFormat = m;
  $('format-full').classList.toggle('active', m === 'full');
  $('format-short').classList.toggle('active', m === 'short');
  $('format-sci').classList.toggle('active', m === 'scientific');
  render();
}

function renderClickUpgrade() {
  const box = ui['click-upgrade'];
  const next = state.nextClickLevel();
  const current = state.clickLevels().find((l) => l.level === state.clickLevel);
  if (current) {
    $('click-lvl-name').textContent = current.name;
    $('click-lvl-power').textContent = `poder do toque: ${state.clickPower().format(numberFormat)} 👁`;
  }
  if (next) {
    $('click-next-name').textContent = `→ ${next.name}`;
    const cost = BigNumber.fromString(next.cost);
    $('click-next-cost').textContent = cost.format(numberFormat);
    $('click-buy').disabled = state.credits.lt(cost);
    $('click-buy').onclick = () => {
      const res = state.buyClickUpgrade();
      if (res.ok) {
        SFX.stamp();
        Analytics.track('upgrade_buy', { type: 'click', level: res.level });
        renderClickUpgrade();
        renderHUD();
      }
    };
    box.classList.remove('hidden');
  } else {
    box.classList.add('hidden');
  }
}

function doPrestige() {
  const gained = Prestige.convictosFrom(state.lifetimeCredits, state.prestigeParams(), state.convictos);
  $('prestige-gain').textContent = `+${gained} Convictos 👁‍🗨`;
  $('prestige-confirm').disabled = gained <= 0;
  $('prestige-modal').classList.remove('hidden');
}

// prestige confirmado
function confirmPrestige() {
  const res = Prestige.prestige(state, state.prestigeParams());
  if (res.ok) {
    const snap = res.snapshot;
    state = new GameState(config, snap);
    SFX.giant();
    Analytics.track('prestige_complete', { prestige_number: state.convictos });
    toast(`O Gigante despertou! +${res.gained} Convictos 👁‍🗨`);
    closePrestige();
    renderProducers();
    render();
    persist();
  }
}

function closePrestige() {
  $('prestige-modal').classList.add('hidden');
}

// ---------- loop / render ----------
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
  updateBuyButtons();
  requestAnimationFrame(loop);
}

function renderHUD() {
  $('credits').textContent = state.credits.format(numberFormat);
  $('chumbo').textContent = state.convictos; // exibe Convictos enquanto Chumbo não entra no core
  $('pps').textContent = `${state.productionPerSecond().format(numberFormat)} 👁/s`;
  $('combo').textContent = `viral ×${state.viralMultiplier(performance.now()).toFixed(1)}`;
  renderClickUpgrade();
}

function updateBuyButtons() {
  for (const def of state.producerList()) {
    const row = document.querySelector(`.producer[data-id="${def.id}"]`);
    if (!row) continue;
    const owned = state.producers[def.id] || 0;
    for (const btn of row.querySelectorAll('.buy-btn')) {
      const mode = Number(btn.dataset.mode);
      const qty = mode === -1 ? state.maxBuy(def.id) : mode;
      const cost = Economy.buyCost(def.baseCost, state.eco.producerGrowthRate, owned, qty);
      btn.querySelector('span').textContent = cost.format(numberFormat);
      btn.disabled = qty <= 0 || state.credits.lt(cost);
    }
    row.querySelector('.producer-owned').innerHTML =
      `possuídos: <b>${owned}</b> ${milestoneLabel(def.id)}`;
  }
}

function render() {
  renderHUD();
  renderProducers();
}

// ---------- persistência (§170–§171) ----------
function persist() {
  const str = serialize(state);
  // backup rotativo simples
  const prev = localStorage.getItem(SAVE_KEY);
  if (prev) localStorage.setItem(SAVE_BACKUP_KEY, prev);
  localStorage.setItem(SAVE_KEY, str);
  showSaveFlash();
}

let flashTimer = null;
function showSaveFlash() {
  const el = ui['save-flash'];
  el.classList.add('show');
  clearTimeout(flashTimer);
  flashTimer = setTimeout(() => el.classList.remove('show'), 700);
}

// ---------- util ----------
function toast(msg) {
  const el = ui.toast;
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.remove('show'), 2400);
}

// salva ao sair/fundo (§171)
window.addEventListener('beforeunload', persist);
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    state.applyOffline(Date.now());
    persist();
  }
});

// expõe handlers usados pelo HTML (modais)
window.__confirmPrestige = confirmPrestige;
window.__closePrestige = closePrestige;

boot();

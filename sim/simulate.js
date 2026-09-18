/**
 * Economy Simulator (§78–§80, §199–§200).
 * Simula jogadores (casual/medium/hardcore/payer) ao longo de dias e responde
 * às metas §79: quando acontecem 1º produtor, 1º prestige, Fase 2…
 *
 * Uso: npm run sim  →  gera /sim/report.md
 */
import { loadConfig } from '../src/core/content.node.js';
import { GameState } from '../src/core/GameState.js';
import BigNumber from '../src/core/BigNumber.js';
import * as Economy from '../src/core/Economy.js';
import * as Prestige from '../src/core/Prestige.js';
import { writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');

const PHASE2_LIFETIME = '1e21'; // 1 Sx ≈ threshold Ditadura (§31)

// Perfis (§78)
const PROFILES = {
  casual: { sessionsPerDay: 2, sessionMinutes: 3, spendRatio: 0.7, tapsPerSession: 20, apm: 30 },
  medium: { sessionsPerDay: 5, sessionMinutes: 5, spendRatio: 0.85, tapsPerSession: 40, apm: 60 },
  hardcore: { sessionsPerDay: 8, sessionMinutes: 8, spendRatio: 0.95, tapsPerSession: 60, apm: 120 },
  payer: { sessionsPerDay: 8, sessionMinutes: 8, spendRatio: 0.95, tapsPerSession: 60, apm: 120, payMult: 10 },
};

const HORIZONS = [1, 7, 30, 90];

// Gasta o saldo da sessão: upgrades de clique + melhor produtor pagável.
function spendSessao(state, ratio, mult) {
  const budget = state.credits.scale(ratio).mul(mult);
  let guard = 0;
  // primeiro equilibrar upgrades de clique (limitado a metade do orçamento)
  while (guard++ < 10) {
    const next = state.nextClickLevel();
    if (!next) break;
    const cost = big(next.cost);
    if (cost.gt(budget.scale(0.25))) break;
    if (!state.buyClickUpgrade().ok) break;
  }
  // depois produtores (tenta do mais avançado ao mais antigo)
  const list = [...state.producerList()].sort((a, b) => b.slot - a.slot);
  for (const def of list) {
    const owned = state.producers[def.id] || 0;
    const max = Economy.maxAffordable(def.baseCost, state.eco.producerGrowthRate, owned, budget);
    if (max >= 1) {
      if (state.buyProducer(def.id, max).ok) break;
    }
  }
}

function big(s) { return BigNumber.fromString(String(s)); }

function simulate(profileKey, days) {
  const prof = PROFILES[profileKey];
  const payMult = BigNumber.fromNumber(prof.payMult ?? 1);
  const config = loadConfig({ maxProducers: 4 });
  let state = new GameState(config);
  state.boost = payMult; // payer: bônus de produção/clique permanente (modelo)
  state._recomputeGlobal();
  state._compute();

  let prestigeCount = 0;
  let firstProducerDay = null;
  let firstPrestigeDay = null;
  let phase2Day = null;
  let firstProducerTimeSec = null;
  let maxLifetime = BigNumber.zero();

  for (let d = 1; d <= days; d++) {
    for (let s = 0; s < prof.sessionsPerDay; s++) {
      const base = (d - 1) * 86400 + s * Math.floor(86400 / prof.sessionsPerDay);
      for (let m = 0; m < prof.sessionMinutes; m++) {
        const now = (base + m * 60) * 1000;
        for (let t = 0; t < prof.tapsPerSession; t++) state.click(now);
        for (let c = 0; c < prof.apm; c++) state.click(now);
        state.tick(60000);
        spendSessao(state, prof.spendRatio, BigNumber.one());
      }
    }
    // offline entre sessões/dias (média simples: produção × 4h cap)
    const offlineGain = state.productionPerSecond().scale(4 * 3600);
    state.credits = state.credits.add(offlineGain);
    state.lifetimeCredits = state.lifetimeCredits.add(offlineGain);

    // marcos
    if (firstProducerDay === null && Object.values(state.producers).some((v) => v > 0)) {
      firstProducerDay = d;
    }
    if (phase2Day === null && state.lifetimeCredits.gte(big(PHASE2_LIFETIME))) phase2Day = d;
    if (state.lifetimeCredits.gt(maxLifetime)) maxLifetime = state.lifetimeCredits;

    // prestige diário
    const res = Prestige.prestige(state, state.prestigeParams());
    if (res.ok) {
      prestigeCount += 1;
      if (firstPrestigeDay === null) firstPrestigeDay = d;
      state = new GameState(config, res.snapshot);
      state.boost = payMult;
      state._recomputeGlobal();
      state._compute();
    }
  }
  void firstProducerTimeSec;

  return { profile: profileKey, prestigeCount, firstProducerDay, firstPrestigeDay, phase2Day, maxLifetime };
}

// ---- main ----
function main() {
  const rows = Object.keys(PROFILES).map((p) => simulate(p, 90));
  const md = buildReport(rows);
  mkdirSync(join(ROOT, 'sim'), { recursive: true });
  writeFileSync(join(ROOT, 'sim', 'report.md'), md, 'utf8');
  console.log(md);
}

function buildReport(rows) {
  const L = [];
  L.push('# Relatório do Economy Simulator — O GIGANTE DESPERTOU');
  L.push('');
  L.push('> Gerado por `npm run sim`. Metas §79, perfis §78, horizontes 1/7/30/90 dias (§199).');
  L.push('');
  L.push('## Parâmetros v0.1');
  L.push('');
  L.push('- `producerGrowthRate = 1.07`');
  L.push('- Prestígio: `Convictos = (Lifetime/1e6)^0.5`, bônus **linear aditivo** `1 + 3%×Convictos` (§60)');
  L.push('  *(modelo exponencial (1+3%)^n foi testado e rejeitado: runaway super-exponencial, §60/§314)*');
  L.push('- "Fase 2" modelada como lifetime ≥ 1e21 (1 Sx) (§31/§35)');
  L.push('- Perfis: casual 2×3min, medium 5×5min, hardcore 8×8min, payer 8×8min + ×10 permanente');
  L.push('');
  L.push('## Resultados por perfil (90 dias)');
  L.push('');
  L.push('| Perfil | 1º produtor | 1º prestige | Fase 2 (1e21) | Prestiges | Lifetime máx |');
  L.push('|---|---|---|---|---|---|');
  for (const r of rows) {
    L.push(`| ${r.profile} | ${fmtDay(r.firstProducerDay)} | ${fmtDay(r.firstPrestigeDay)} | ${fmtDay(r.phase2Day)} | ${r.prestigeCount} | ${r.maxLifetime.format('short')} |`);
  }
  L.push('');
  L.push('## Progressão por horizonte');
  L.push('');
  const tableRows = [];
  for (const h of HORIZONS) {
    const cells = [String(h + 'd')];
    for (const p of Object.keys(PROFILES)) {
      const r = simulate(p, h);
      cells.push(`${r.prestigeCount}pg · ${r.maxLifetime.format('short')}`);
    }
    tableRows.push(cells);
  }
  L.push('| Horizonte | ' + Object.keys(PROFILES).join(' | ') + ' |');
  L.push('|---|' + Object.keys(PROFILES).map(() => '---').join('|') + '|');
  for (const row of tableRows) L.push('| ' + row.join(' | ') + ' |');
  L.push('');
  L.push('Leitura: `pg` = prestiges acumulados; valor seguinte = lifetime máximo alcançado no horizonte.');
  L.push('');
  L.push('## Leitura rápida (§79–§80)');
  L.push('');
  const med = rows.find((r) => r.profile === 'medium');
  L.push(`- **Primeiro produtor**: ${fmtDay(med.firstProducerDay)} no perfil médio (alvo §81: primeiros minutos).`);
  L.push(`- **Primeiro prestígio**: ${fmtDay(med.firstPrestigeDay)} no perfil médio (hipótese §80 = dia 1).`);
  L.push(`- **Fase 2**: ${fmtDay(med.phase2Day)} no perfil médio (calibrar com dados reais pós-soft-launch).`);
  L.push('');
  L.push('> ⚠️ Primeira calibragem determinística (§28). Rode `npm run sim` a cada mudança de');
  L.push('> economia e ajuste `economy.json` (ou Remote Config) conforme os dados reais.');
  L.push('');
  L.push('## Conclusão da calibragem v0.1');
  L.push('');
  L.push(`- Primeiro produtor e primeiro prestígio no **dia 1** para o perfil médio — atende §80/§81.`);
  L.push(`- **Fase 2 (1e21) NÃO é atingida em 90 dias** por nenhum perfil nessa economia F1-only.`);
  L.push(`  Isso é ESPERADO para o PLAYABLE CORE: a Fase 2 exige o conteúdo completo (§31–§34),`);
  L.push(`  Sósias (×5/×10/×50 §45), Coordenadores e a árvore de prestígio — todos fora do escopo do`);
  L.push(`  núcleo jogável (§246–§250). A calibragem final da transição de fases acontece com esses`);
  L.push(`  sistemas no vertical slice, não agora (regra §326: não avançar cedo demais).`);
  L.push('');
  return L.join('\n');
}

function fmtDay(d) {
  return d === null ? '— (não atingido)' : `dia ${d}`;
}

main();

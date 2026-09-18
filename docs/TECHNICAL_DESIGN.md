# TECHNICAL_DESIGN.md — O GIGANTE DESPERTOU

> **TDD v0.1.0** — arquitetura, módulos, engine, padrões e infraestrutura técnica.

---

## 1. Plataforma e engine (§10–§12)

| Item | Decisão |
|---|---|
| Engine | **Unity 6.x LTS** (C#) — versão LTS de produção vigente no momento da build |
| Plataforma | **Android-first** (Google Play); arquitetura pronta para iOS/tablets |
| Orientação | **Portrait**, jogável com **uma mão** |
| Android | target SDK 35+/36 conforme requisito vigente do Google Play na publicação (rever antes de enviar) |
| Performance | 60 FPS em aparelhos compatíveis; **mínimo aceitável 30 FPS estáveis** |
| Qualidade | Tiers LOW / MEDIUM / HIGH (VFX, sombras, resolução) |

---

## 2. Princípio: domínio engine-agnóstico

Todo o **núcleo de regras** (BigNumber, economia, prestígio, save, recompensas)
é escrito **sem dependência de engine** — apenas tipos puros e dados. Isso permite:

1. Testar o design **hoje** em JS/Node (mesma semântica);
2. Portar **1:1** para C#/Unity (o espelho já está em `unity/`);
3. Manter uma única fonte de verdade de comportamento.

**Contrato:** as APIs públicas de `src/core/*` === APIs públicas de `unity/*`.
O teste que prova o comportamento no core é o `tests/`; o mesmo comportamento é
esperado na porta C# (testes NUnit na produção Unity).

---

## 3. Arquitetura modular (§13)

Sistemas separados por responsabilidade; comunicação via interfaces e eventos.
Nenhum módulo conhece detalhe interno de outro.

```
Core          // motores de regra (engine-agnóstico)
  BigNumber     numbers gigantes + formatação BR
  Economy       custos, produção, multiplicadores, buy modes, milestones
  Producers     catálogo + estado de compra
  Automation    Coordenadores (nível, bônus de velocidade)
  Clones        Sósias (raridade, bônus por produtor, duplicatas→Puxa-Sacos)
  Prestige      Convictos, bônus global, árvore (Maçonaria)
  Phases        estágios/fases, thresholds, transições
  ZapVazado     mensagens, decisão, medidor de desconfiança, streak, recompensas
  Missions      diárias/semanais
  Achievements  regras + secretos
  Collection    Sósias/documentos/fitas/OVNIs/objetos
  LiveOps       eventos, temporadas, dossiê da temporada, calendário
  Ads           rewarded/interstitial (interface; implementação por SDK)
  IAP           produtos, validação, restore, pending (interface)
  Analytics     taxonomia de eventos (interface)
  RemoteConfig  parâmetros remotos + kill switch (interface)
  Save          serialização, autosave, versionamento/migração, backup, cloud
  Audio         SFX/Música (interface)
  VFX           gatilhos visuais
UI             camada de apresentação (canvas, telas, componentes) — por engine
Localization   pt-BR (primário), en-US, es
```

> Nota: no **núcleo jogável web** (`src/`), `UI` é DOM/Canvas 2D e `Audio` é Web
> Audio — ambos **descartáveis** na porta Unity; todo o resto é idêntico.

---

## 4. Data-driven (§14)

- **Nunca hardcode centenas de valores.** Conteúdo vive em dados:
  - **Unity:** `ScriptableObject` + JSON/config (importados no editor).
  - **Core web:** JSON em `src/content/`.
- Tabelas de: produtores, custos, milestones, upgrades de clique, Coordenadores,
  Sósias, fase/thresholds, prestige tree, missões, achievements, Zaps, eventos.
- **Remote Config** para tudo que pode mudar sem release:
  economia, milestones, ad frequency, boost duration, rewards, preços internos,
  event schedules, prestige tuning (§182) e **kill switch** (§183).

Convenção de ids (nomenclatura, §223):

```
CMAP_click_lvl_01        // upgrade de clique
PRD_phase1_01            // produtor
MGR_01 .. MGR_12, MGR_ALU (Zé)   // coordenadores
CLN_phase1_01            // sósias
PHASE_1 .. PHASE_4       // fases
ZAP_0001                 // mensagens de Zap
UPC_pres_01              // upgrade permanente (prestígio)
```

---

## 5. BigNumber (§20–§21)

- Representação **expoente + mantissa** (logarítmica), `safe` por construção
  (sem overflow de `double` na faixa útil) + faixa estendida quando necessário.
- Operações: add, sub, mul, div, pow, compare, custom.
- Formatação BR: `1 mil`, `1 milhão`, `1 bilhão`, `1 trilhão`; depois abreviado
  (`K, M, B, T, Qa, Qi, Sx, Sp, Oc, No, Dc…`) e **científico** (`1,50e6`);
  padrão de configuração: **nomes / abreviado / científico**.
- **Proibido overflow silencioso** — operações inválidas lançam/cap explicitamente.

Testes: `tests/BigNumber.test.js`; espelho: `unity/BigNumber.cs`.

---

## 6. Formulas de domínio (referência v0.1)

### Produtor (§28)
```
costBuy(n)    = round(BaseCost * GrowthRate^owned)     // por quantidade (x1/x10/...)
production    = BaseProduction * owned * multipliers
multipliers   = prod( milestoneBonus(i), i<=owned )
              * phaseMultiplier
              * prestigeGlobalBonus
              * cloneBonus(producer, phase)            // ×5/×10/×50
              * adBoost * eventBoost
```

Buy modes (§29): `x1`, `x10`, `x25`, `x100`, `MAX` — `MAX` = maior compra
possível com o saldo atual (fechado, calculado via progressão geométrica).

### Milestones (§30)
Limiares `10, 25, 50, 100, 250, 500, 1000` → bônus multiplicativo encadeado
(ex.: ×2 por limiar atingido; mudanças maiores em milestones destacados).

### Prestígio (§59–§60)
```
Convictos  = floor((LifetimeMentes / LimiarPrestígio) ^ Expoente)
bonusGlobal= (1 + taxaPorConvicto)^Convictos        // taxa inicial 3% (hipo)
```
Calibração: `sim/simulate.js` (§78–§80). Primeiro prestígio alvo: ~1º dia.

### Offline (§86–§88)
```
ganhoOffline = min(duracao, limiteHoras) * productionPerHour * fatoresDeAutomação
ganhoOffline *= 2   // se DUPLICAR RELATÓRIO (rewarded)
```
Limite inicial 2–4h, extensível 8/12/24h via upgrades de prestígio.

---

## 7. Save system (§170–§174)

| Requisito | Implementação |
|---|---|
| O que salva | moedas, produtores, coordenadores, Sósias, prestige, fases, missões, eventos, settings, purchases |
| Autosave | compra, prestige, pause, background, IAP, + intervalo (ex.: 30s/60s) |
| Corrupção | save primário + **backup rotativo**; checagem de integridade (versão+hash); rollback automático ao backup válido |
| Versionamento | campo `version` (V1→V2→V3) + **migrações explícitas** |
| Cloud | Google Play Games Saved Games / solução apropriada; **não bloqueia** o MVP |

Formato: JSON (comprimido quando conveniente). `Save` v1 implementado/testado no core (`src/core/Save.js`).

---

## 8. Analytics (§175–§181)

- Firebase Analytics (ou equivalente) desde a primeira build de teste.
- Taxonomia (§176): `first_open, tutorial_start, tutorial_complete, click_main,
  producer_buy, producer_milestone, manager_unlock, manager_upgrade, clone_open,
  clone_duplicate, zap_open, zap_choice, prestige_preview, prestige_complete,
  phase_unlock, upgrade_buy, daily_claim, mission_complete, event_join,
  rewarded_offer, rewarded_complete, interstitial_impression, shop_view,
  iap_start, iap_success, iap_fail`.
- Parâmetros (§177): `producer_id, phase, currency, value, manager_id, clone_id,
  rarity, event_id, prestige_number`.
- **Nenhum PII** (§178): nunca nome, telefone, conteúdo real de mensagens.
- KPIs (§180): D1/D3/D7/D14/D30, DAU/MAU, sessões/dia, session length, ARPDAU,
  ad ARPDAU, IAP ARPDAU, conversion, LTV, CPI, ROAS. Funil (§179):
  install → tutorial → 1º produtor → 1º manager → 1º Zap → 1º Sósia → 1º prestige → fase 2.
- Crashlytics: crash, nonfatal, breadcrumbs (§186); meta crash-free > 99%.

Ver `ANALYTICS.md` (schema completo).

---

## 9. Performance (§187–§192)

- Object pooling em partículas, floating text, ícones voadores, efeitos.
- Lista de produtores: reciclagem/scroll eficiente (Unity `ScrollRect` + pool;
  nunca instanciar 48+ objetos). Web: DOM mínimo (re-render delta).
- Atlas para UI/ícones/portraits.
- Loading curto; serviços online iniciam em background.
- **Offline-first** (§193): core funciona sem internet; online só para ads, IAP,
  ranking, Remote Config/event sync.

---

## 10. Backend e ferramentas (§194–§199)

- Backend caro só quando necessário; preferir serviços gerenciados/free tier.
- **Ferramentas internas** (editores data-driven):
  - Editor de Produtores (id, nome, desc, icon, cost, production, milestones, fase);
  - Editor de Zap (texto, categoria, decisão, recompensa, imagem opcional);
  - Editor de Eventos (duração, economia, produtores, recompensas, milestones);
  - Dashboard de Economia (curvas custo/produção/tempo);
  - Simulador automático (bots casual/active/hardcore/payer) → relatório.
- No repositório atual: **simulador Node** em `sim/` (economia + bots) gera
  `sim/report.md`; os editores web com UI vêm no vertical slice.

---

## 11. Segurança, anti-cheat, compliance (§206–§208, §161–§163, §261–§263)

- Nunca confiar só no cliente para IAP/premium crítica; **validação de IAP** +
  restore + pending purchase.
- Anti-cheat proporcional: proteger premium currency, rankings, IAP (não é jogo
  competitivo militar).
- Privacidade: consent flow (UMP da Google), privacy policy, data safety, SDK
  disclosure. Classificação IARC conforme conteúdo real. Ver `PRIVACY.md`.

---

## 12. Git, branches, CI/CD, builds (§209–§214)

- Repo configurado (`.gitignore` com segredos/Unity/Node).
- Branches: `main`, `develop`, `feature/*`, `release/*`, `hotfix/*` (ou
  equivalente simplificado). Sessão atual trabalha em
  `arena/01a0b1eb-ogigantedespertou` com commits pequenos/descritivos.
- CI/CD quando viável: testes → build → versionamento.
- Versionamento semântico `1.0.0 (build 100)`.
- **Credenciais nunca versionadas** (keystore, API secrets) — variáveis de
  ambiente + `secrets/` ignorado.

---

## 13. Monorepo/estrutura de pastas (núcleo)

```
docs/           # todos os documentos de produção
src/            # PLAYABLE CORE (web) — núcleo testável
  core/         # domínio engine-agnóstico (espelha unity/)
  content/      # JSON data-driven (produtores, economia, upgrades de clique…)
  theme/        # CSS/design tokens (cromo provisório do núcleo)
  app.js        # bootstrap + loop + binding (camada UI descartável)
  index.html    # shell da Sede Secreta
unity/          # espelho C# Unity-ready (BigNumber, Economy, Prestige…)
sim/            # Economy Simulator (Node) + bots + relatório
tools/          # utilitários (servidor local etc.)
tests/          # Node test runner (BigNumber, Economy, Prestige, Save, buy)
```

---

## 14. Testes (§201–§205)

| Tipo | Escopo | Onde |
|---|---|---|
| Unit | BigNumber, Economy, Prestige, Save, Rewards, IAP state, event schedule | `tests/` |
| Integração | tutorial→produtor; prestige→reset; IAP→reward; rewarded→reward; save→reload | `tests/` (fluxos do core) |
| Edge case | offline, queda de internet, background, relógio alterado, ad falha, compra pendente | suite + documento QA |
| Device matrix | Android antigo/atual, low RAM, tablet, telas altas/baixas, safe area/notch | `QA.md` |

Comando: `npm test`.

---

## 15. Roadmap técnico imediato

1. ✅ Estrutura + Git + documentos (M0).
2. ✅ BigNumber + Economia + Prestígio + Save (testados).
3. ✅ Economy Simulator (+ relatório de calibragem).
4. ✅ Playable core (Sede, Zap, produção/s, 4 produtores, buy modes, milestones, offline, save).
5. ⏳ Vertical slice (12 produtores, Coordenadores, Zap, Sósia, prestige, Arquivo).
6. ⏳ Porta Unity/C# (mesma API) + ScriptableObjects dos conteúdos.
7. ⏳ Alpha → Beta → Soft Launch → V1.0 (checklist em `RELEASE.md`).

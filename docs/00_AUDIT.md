# AUDITORIA DA ESPECIFICAÇÃO — v0.1.0

> Documento obrigatório da PRIMEIRA TAREFA (§324). Registra como cada bloco da
> especificação será atendido, o que já existe, o que é bloqueado pelo ambiente
> e as decisões profissionais tomadas. Regra §314: **nada de reduzir escopo em
> silêncio** — tudo está documentado aqui.

---

## 1. Leitura — resumo executivo

A proposta é um **idle clicker/incremental mobile** (Android-first, Unity/C#,
portrait, uma mão) original brasileiro: uma organização secreta incompetente
que escala de "grupo de zap" até "economia intergaláctica", satirizando a
*maquinação conspiratória* (nunca pessoas/grupos reais). O brief pede produto
comercial completo, mas é explícito (§324–§326, §246–§249, §339) que a execução
começa por **documentação → estrutura → BigNumber → Economy Simulator →
PLAYABLE CORE**, validando o núcleo antes de produzir massa de conteúdo.

---

## 2. Estado do ambiente (capacidades reais)

| Recurso | Estado | Impacto |
|---|---|---|
| Node.js v22 | ✅ | Playable core + simulador + testes |
| Python 3.11 | ✅ | Servidor estático local |
| Unity Editor / .NET SDK | ❌ ausente neste sandbox | AAB/APK **não podem ser produzidos/validados aqui** |
| Git + `gh` autenticado | ✅ | Commits por módulo + push na branch da sessão |
| Preview HTTP | ✅ | Núcleo jogável visível no navegador |

### Decisões decorrentes (documentadas, §314)

1. **Playable core como referência executável no navegador.**
   O design de domínio (BigNumber, Economia, Prestígio, Save) é **engine-agnóstico por
   arquitetura** (§13). Entrego:
   - Implementação **JS (ES modules)** testada de todo o núcleo lógico em `src/core/`;
   - Espelho **C# / Unity-ready** em `unity/` (mesmas APIs e mesmos testes de referência);
   - Camada de apresentação web em `src/theme/` + `src/app.js` validando o game
     feel do §325 (HUD, Compartilhar no Zap, produtores, buy modes, milestones, offline, save).
   → Permite **testar, calibrar e commitar hoje** o que §326 exige provar antes da massa de assets.

2. **Unity/Android (AAB, SDK, keystore) fica planejado e especificado**, com
   checklist de build em `BUILD.md` e `RELEASE.md`, mas a produção da build
   nativa depende de uma máquina com Unity Editor — fora deste ambiente. Não vou
   fingir que gerei um AAB.

3. **Sem segredos/credenciais reais** serão usados (regra §214). Tudo usa
   placeholders e variáveis de ambiente documentadas.

---

## 3. Mapa da especificação → entrega (por seção)

### Núcleo de produto

| Seções | Tema | Status |
|---|---|---|
| §1–9 | Missão, referências, identidade, tom, promessa, fantasia de poder | ✅ Documentado (GDD §1–§5); tom satírico fixado como pilar |
| §10–12 | Plataforma, Android, hardware | ✅ Documentado (TDD + BUILD). Build nativa = máquina c/ Unity (ver §2) |
| §13–14 | Arquitetura modular, data-driven | ✅ Implementado no core (módulos) + JSON de conteúdo |

### Gameplay & sistemas

| Seções | Sistema | Status |
|---|---|---|
| §15–16 | Core loop / longo prazo | ✅ GDD |
| §17–19 | Moedas (Crédulos, Chumbo, Convictos) | ✅ Implementado no core (Crédulos + offline; Chumbo/Convictos no modelo de dados, UI fase 2) |
| §20–21 | Big Numbers + formatos | ✅ **Implementado + testado** (`src/core/BigNumber.js`, espelho C#) |
| §22–26 | Botão Compartilhar no Zap, feedback, combo, autoclick, upgrades de clique | ✅ Core (clique, combo Engajamento Viral, lista de upgrades de clique definida em JSON) |
| §27–30 | 12 produtores/fase, fórmula, buy modes x1/x10/x25/x100/MAX, milestones | ✅ **Implementado + testado** (buy modes e milestones 10/25/50/100/250/500/1000) |
| §31–34 | Fases 1–4 (48 produtores) | ✅ Conteúdo Fase 1 completo no core; Fases 2–4 catalogadas no GDD/CONTENT_BIBLE (produção em milestones seguintes, §326) |
| §35–37 | Desbloqueio/transição de fase | ✅ Modelo + threshold Fase 2 no core; cinemáticas planejadas na Art Bible |
| §38–42 | Coordenadores + Zé do Chapéu de Alumínio | ⏳ Planejado (vertical slice §327) |
| §43–49 | Laboratório de Sósias, duplicatas→Puxa-Sacos, catálogo | ⏳ Planejado (vertical slice) |
| §50–56 | Zap Vazado + gerador, Desconfiança, streak | ⏳ Planejado (vertical slice); data-model definido no CONTENT_BIBLE |
| §57–63 | Prestígio "Despertar o Gigante", Maçonaria, árvore | ✅ Modelo de prestígio **implementado + testado** (fórmula + bônus por Convicto); árvore visual no vertical slice |
| §64–75 | 9 telas + navegação | ⏳ Sede Secreta é o core; demais telas no vertical slice (mapa de telas no GDD) |
| §76–80 | Economia, curva, simulador, primeiro prestígio | ✅ **Economy Simulator implementado** (`sim/`) + calibragem inicial |

### Conteúdo & arte

| Seções | Tema | Status |
|---|---|---|
| §99–109 | Narrativa, O Arquivista, Agência do Óbvio, direção de arte, Coordenadores/Sósias/produtores/backgrounds | ✅ Definições no GDD/ART_BIBLE/CONTENT_BIBLE |
| §110–115 | UI, botões, tipografia, números, iconografia | ✅ Direções no ART_BIBLE; sistema de UI do core aplica (fontes do sistema + fallback) |
| §116–122 | Motion, VFX, haptics, áudio, música | ✅ Especificado (ART_BIBLE/audio); implementação de SFX no core via Web Audio (placeholder original) |

### Pós-launch, monetização, técnica

| Seções | Tema | Status |
|---|---|---|
| §123–129 | FTUE, disclosure progressivo, retenção | ✅ Fluxo do core segue §124/§125; plano FTUE no GDD |
| §130–140 | LiveOps, eventos, temporadas, social | ✅ LIVEOPS.md |
| §141–160 | Monetização (ads, IAP, probabilidades, pity) | ✅ MONETIZATION.md |
| §161–169 | Privacidade, classificação, localização | ✅ PRIVACY.md + padrão de localização no TDD |
| §170–174 | Save, autosave, recovery, cloud, migrations | ✅ Save com versionamento **implementado + testado** |
| §175–186 | Analytics, Crashlytics, estabilidade | ✅ ANALYTICS.md (taxonomia §176 mapeada) |
| §187–192 | Performance, pooling, atlas, quality, loading | ✅ TDD |
| §193–207 | Offline-first, backend, editores, dashboards, testes, segurança/IAP | ✅ TDD/BUILD + testes unitários |
| §209–219 | Git, branches, CI/CD, builds, credenciais, docs, inventários | ✅ Git configurado + docs em `docs/` |
| §220–265 | Anti-asset-flip, anti-cara-de-IA, nomenclatura, Google Play, ASO, criativos, IP/legal | ✅ Direções em ART_BIBLE/CONTENT_BIBLE/RELEASE |
| §266–283 | Copy, microcopy, easter eggs, decoração, skins, notificações, deep links | ✅ CONTENT_BIBLE |
| §284–305 | Ratings, suporte, settings, background, server time, telemetria, unit economics, release flags, passes finais | ✅ TDD/RELEASE/ANALYTICS |
| §306–340 | Passes finais, relatório, checklist, prontidão, autonomia, prioridades, ordem de execução | ✅ Este documento + RAMOADMAP |

---

## 4. Riscos e mitigação

| # | Risco | Mitigação |
|---|---|---|
| R1 | Build Android/AAB fora deste ambiente (§310) | Documentar BUILD/RELEASE; entregar core testado e portável; produzir AAB quando houver Unity Editor (máquina com .NET/Android SDK). **Explicitamente** não prometido neste sandbox. |
| R2 | Balanceamento sem playtest real | Economy Simulator com perfis (casual/médio/hardcore/payer) + Remote Config para tuning pós-lançamento (§180–182). |
| R3 | Conteúdo satírico sensível | SATIRE_GUIDELINES + revisão humana de conteúdo político (§244) + "Modo Humor" (§278). |
| R4 | Colisão de IP (nomes de Sósias §48) | Lista de verificação pré-uso comercial no CONTENT_BIBLE; nomes marcados como *provisórios*. |
| R5 | Dívida técnica por pressa | Arquitetura modular, testes desde o M0, CI quando viável (§212). |

---

## 5. Conclusão

A especificação é **viável e coerente**. Neste milestone inicial entrego o que a
própria especificação define como PRIMEIRA TAREFA (§324) e PLAYABLE CORE (§325):
documentos fundamentais, estrutura de pastas, Git, BigNumber, Economy Simulator
e núcleo jogável — com a transparência de que a compilação nativa Unity/Android
depende de ambiente externo (documentado acima e no BUILD.md).

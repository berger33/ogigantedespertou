# ROADMAP.md — O GIGANTE DESPERTOU

> Ordem de execução (§339) e registro de progresso por milestone (§246–§254).
> Atualizado a cada commit relevante.

---

## Ordem de execução

AUDITORIA → GDD → TDD → ART BIBLE → ECONOMY SIMULATOR → PLAYABLE CORE → TESTE →
VERTICAL SLICE → TESTE → ALPHA → BETA → SOFT LAUNCH → ANÁLISE → POLIMENTO →
PUBLICAÇÃO → LIVEOPS → OTIMIZAÇÃO.

## Milestones

| # | Milestone | Escopo | Estado |
|---|---|---|---|
| 0 | **Playable Core** | Sede, Compartilhar no Zap, Mentes, produção/s, 4 produtores, x1/x10/MAX, milestones, save, offline, UI inicial, SFX, analytics básico | ✅ |
| 1 | **Vertical Slice** | 12 produtores F1, 12 Coordenadores, Zap Vazado completo, fluxo de 1 Sósia, prestige, Arquivo, arte ~final, áudio, VFX | ⏳ |
| 2 | **Alpha** | Fases 1–2, collection, achievements, offline, ads test | ⏳ |
| 3 | **Beta** | 4 fases, 9 telas, economia completa, LiveOps | ⏳ |
| 4 | **Soft Launch** | dados reais; parar spec grande sem dados | ⏳ |
| 5 | **V1.0** | conteúdo completo + polimento + publicação | ⏳ |

## Registro de progresso

- **M0** — Estrutura de pastas, Git, documentos (GDD/TDD/Economia/Arte/Conteúdo/
  Sátira/Analytics/Monetização/LiveOps/Privacy/QA/Build/Release/ARCHITECTURE/
  BIG_NUMBERS), BigNumber (JS+C#), Economy, GameState, Prestige, Save, Economy
  Simulator, Playable Core (Sede Secreta), testes (35/35 ✅), espelho C# parcial.
- **Próximo** — M1 Vertical Slice: GameState.cs, 12 produtores, Coordenadores,
  Zap Vazado, Laboratório de Sósias, Arquivo, arte ~final, áudio, VFX.

---

## Critério de DONE (§311)

Feature pronta = funciona + UI + feedback + som (quando apropriado) + analytics
+ testada + documentada.

# ARCHITECTURE.md — O GIGANTE DESPERTOU

> Visão diagramática da arquitetura modular (§13) e fluxo de dados em runtime.
> Detalhes de decisão estão no `TECHNICAL_DESIGN.md`.

---

## 1. Camadas

```
┌───────────────────────────────────────────────────────────┐
│ UI (apresentação) — por engine: DOM/Canvas 2D (core web)  │
│                ou uGUI/Canvas (Unity). DESCARTAVEL.       │
└───────────────────────────┬──────────────────────────────┘
                            │ eventos/commands (não conhece regras)
┌───────────────────────────▼──────────────────────────────┐
│ CORE (regras, engine-agnóstico, testável)                 │
│  GameState (estado agregado)                              │
│  BigNumber · Economy · Producers · Automation · Clones    │
│  Prestige · Phases · ZapVazado · Missions · Achievements  │
│  Collection · LiveOps · Save                              │
└───────┬──────────────────┬──────────────────┬─────────────┘
        │                  │                  │
┌───────▼──────┐  ┌────────▼────────┐  ┌───────▼──────────────┐
│ Content JSON │  │ Adaptadores     │  │ Infra/telemetria     │
│ (data-driven)│  │ Ads · IAP       │  │ Analytics · Crashlyt │
│ prod./econ.  │  │ RemoteConfig    │  │ (interfaces)         │
└──────────────┘  └─────────────────┘  └──────────────────────┘
```

**Regra de ouro:** a UI nunca calcula economia. Ela dispara comandos (`buy`,
`click`, `prestige`, `zapChoice`) e renderiza o estado resultante.

## 2. Loop de runtime (core)

```
input (tap) → GameState.command → Core reduz estado → publica emissores
      → [Save autosave throttle] → [Analytics event] → UI re-render delta
```

- Offline: no boot, `Save.load()` → `Economy.applyOffline(elapsed, cap)`
  → relatório exibido (§86–§88). Sem duplicar recompensa em reconexão (§290).

## 3. Responsabilidades por módulo

| Módulo | Responsabilidade | Depende de |
|---|---|---|
| BigNumber | números gigantes + formatação | — |
| Economy | custos, produção/s, buy modes, milestones | BigNumber |
| Producers | catálogo + estado | Content |
| Automation | Coordenadores (nível, velocidade) | Producers |
| Clones | Sósias (raridade ×5/×10/×50, duplicatas→Puxa-Sacos) | Producers |
| Prestige | Convictos, bônus global, árvore | BigNumber |
| Phases | estágios, thresholds, transições | Economy |
| ZapVazado | mensagens, decisão, desconfiança, streak, recompensas | Content |
| Missions / Achievements / Collection | metas, coleção, dossiês | GameState |
| LiveOps | eventos, temporadas, passe, calendário | Content + RemoteConfig |
| Save | serialização+hash, autosave, migrations, backup | BigNumber (toJSON) |
| Ads / IAP / RemoteConfig / Analytics | interfaces (implementação por SDK) | — |

## 4. Data-driven (§14)

Todo conteúdo estático vive em `src/content/*.json` (espelho: ScriptableObject
no Unity). Parâmetros de tunagem em `economy.json`; **Remote Config** para
mudanças pós-release (defaults versionados no repo).

## 5. Estado de referência atual

- Implementado no M0: BigNumber, Economy, Producers (4 primeiros), BuyModes,
  Milestones, Offline, Save (V1), Prestige (modelo), ClickCombo.
- Felicidade do game testada via `tests/` + `npm run sim`.

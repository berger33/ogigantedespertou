# O GIGANTE DESPERTOU 👁

**Idle Clicker / Incremental / Management / Collection — satírico brasileiro.**

Você **não cria teorias. Você planta. E colhe crédulos.**

> Este jogo é uma obra de ficção e sátira. Teorias, organizações e acontecimentos apresentados fazem parte de um universo humorístico e **não devem ser interpretados como fatos**.

---

## O que é este repositório

Estrutura de produção completa de um idle/incremental mobile comercial, além do
**Núcleo Jogável (PLAYABLE CORE)** implementado e testado. Toda a base de
domínio (números grandes, economia, prestígio, save) é *engine-agnóstica* e foi
projetada para portar 1:1 para **Unity 6.x LTS / C#** (Android-first).

| Área | Onde | Observações |
|---|---|---|
| Documentos de produção | [`docs/`](docs/) | GDD, TDD, Economia, Arte, Conteúdo, Sátira, Monetização, Analytics, LiveOps… |
| Núcleo jogável (referência) | [`src/`](src/) | Web, sem dependências. Roda no navegador (preview) e valida o design |
| Domain C# (Unity) | [`unity/`](unity/) | BigNumber, Economy, Prestige — espelho do código testado |
| Simulador de economia | [`sim/`](sim/) | Calibra custos/curvas/primeiro prestígio (§78–80) |
| Testes | [`tests/`](tests/) | BigNumber, Economia, Prestígio, Save, Buy Modes |
| Conteúdo (data-driven) | [`src/content/`](src/content/) | JSON: produtores, economia, milestones (§14) |

## Executar

```bash
npm test            # testes unitários (Node, sem dependências)
npm run sim         # simulador de economia (gera relatório em sim/report.md)
npm run serve       # servidor local do núcleo jogável em http://localhost:8000
```

O núcleo jogável é 100% offline-first: sem internet ele roda completo
(ads/IAP/ranking são camadas posteriores, definidas nos documentos mas fora do
MVP de núcleo).

## Estado atual (milestones)

Veja o cronograma e o registro de progresso em [`docs/ROADMAP.md`](docs/ROADMAP.md)
e a auditoria da especificação em [`docs/00_AUDIT.md`](docs/00_AUDIT.md).

**Status:** MILESTONE 0 — PLAYABLE CORE ✅ (núcleo jogável + BigNumber + simulador + documentos)

## Aviso legal

Obra de ficção e sátira. Nenhuma teoria apresentada deve ser interpretada como
fato; nenhuma pessoa real é representada; instituições são caricaturas fictícias.
Consulte [`docs/SATIRE_GUIDELINES.md`](docs/SATIRE_GUIDELINES.md) e
[`docs/PRIVACY.md`](docs/PRIVACY.md).

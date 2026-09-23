# QA.md — O GIGANTE DESPERTOU

> Estratégia de testes e matriz de qualidade (§200–§205, §239, §260, §302–§308).

---

## 1. Níveis de teste

| Nível | Escopo | Como |
|---|---|---|
| Unit | BigNumber, Economy, Prestige, Save, Rewards, IAP state, event schedule | `npm test` |
| Integração | tutorial→produtor, prestige→reset, save→reload | `tests/` |
| Edge case | sem internet, queda, background, relógio alterado, ad falha, compra pendente | suite + rotina manual |
| Device matrix | Android antigo/atual, low RAM, tablet, tela alta/pequena, notch | relatório de device matrix |

## 2. Edge cases mapeados (§203)

1. Sem internet → core funciona; evento "aguardando sinal".
2. Internet cai no meio de rewarded → recompensa não concedida em dobro §290.
3. App minimizado segundos → session reconnect, **não** trata como offline enorme.
4. App morto/relógio alterado → sem duplicar recompensa; proteção de relógio sem punir falso positivo.
5. Anúncio falha → fallback, sem travar fluxo.
6. Compra pendente → não bloqueia; resolve pendência.
7. Save corrompido → rollback ao backup; sem perda.

## 3. Prioridade de bugs (§260)

- **P0**: crash, perda de save, compra.
- **P1**: bloqueio de progressão.
- **P2**: visual/gameplay maior.
- **P3**: cosmético.

## 4. Passes finais (§303–§308)

1. **Final art pass**: auditar tela por tela — "parece jogo profissional?".
2. **Final UX pass**: tap targets, legibilidade, scroll, feedback, loading, erro.
3. **Final audio pass**: nenhuma tela importante muda; nenhum som repetido demais.
4. **Final economy pass**: simulador → identificar walls/explosões/soft locks.
5. **Final monetization pass**: sem ads agressivos, preço claro, reward correto.
6. **Final policy pass**: regras vigentes das lojas imediatamente antes do envio.

## 5. Estabilidade (§186)

Crash-free users **> 99%**; ANR mínimo; Crashlytics com nonfatal + breadcrumbs.

## 6. Migração de save (§301–§302)

Todo update testado com saves da versão anterior (migrations V1→V2→V3).

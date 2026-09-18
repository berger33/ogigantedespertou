# Relatório do Economy Simulator — O GIGANTE DESPERTOU

> Gerado por `npm run sim`. Metas §79, perfis §78, horizontes 1/7/30/90 dias (§199).

## Parâmetros v0.1

- `producerGrowthRate = 1.07`
- Prestígio: `Convictos = (Lifetime/1e6)^0.5`, bônus **linear aditivo** `1 + 3%×Convictos` (§60)
  *(modelo exponencial (1+3%)^n foi testado e rejeitado: runaway super-exponencial, §60/§314)*
- "Fase 2" modelada como lifetime ≥ 1e21 (1 Sx) (§31/§35)
- Perfis: casual 2×3min, medium 5×5min, hardcore 8×8min, payer 8×8min + ×10 permanente

## Resultados por perfil (90 dias)

| Perfil | 1º produtor | 1º prestige | Fase 2 (1e21) | Prestiges | Lifetime máx |
|---|---|---|---|---|---|
| casual | dia 1 | dia 2 | — (não atingido) | 79 | 332,53 M |
| medium | dia 1 | dia 1 | dia 14 | 90 | 672,07 Sp |
| hardcore | dia 1 | dia 1 | dia 7 | 90 | 1,3 Oc |
| payer | dia 1 | dia 1 | dia 3 | 90 | 249,47 Oc |

## Progressão por horizonte

| Horizonte | casual | medium | hardcore | payer |
|---|---|---|---|---|
| 1d | 0pg · 45,55 mil | 1pg · 249,6 M | 1pg · 7,51 B | 1pg · 3,43 T |
| 7d | 3pg · 9,31 M | 7pg · 213,56 B | 7pg · 10,53 Sx | 7pg · 67,54 Sp |
| 30d | 21pg · 42,76 M | 30pg · 18,53 Sp | 30pg · 72,59 Sp | 30pg · 13,67 Oc |
| 90d | 79pg · 332,53 M | 90pg · 672,07 Sp | 90pg · 1,3 Oc | 90pg · 249,47 Oc |

Leitura: `pg` = prestiges acumulados; valor seguinte = lifetime máximo alcançado no horizonte.

## Leitura rápida (§79–§80)

- **Primeiro produtor**: dia 1 no perfil médio (alvo §81: primeiros minutos).
- **Primeiro prestígio**: dia 1 no perfil médio (hipótese §80 = dia 1).
- **Fase 2**: dia 14 no perfil médio (calibrar com dados reais pós-soft-launch).

> ⚠️ Primeira calibragem determinística (§28). Rode `npm run sim` a cada mudança de
> economia e ajuste `economy.json` (ou Remote Config) conforme os dados reais.

## Conclusão da calibragem v0.2 (modelo ciclo + Coordenadores)

- **Primeiro produtor**: dia 1 em todos os perfis — atende §81 (primeiros minutos).
- **Primeiro prestígio (1e6)**: dia 1 (médio), dia 1 (hardcore), dia 2 (casual), dia 1 (payer).
- **Fase 2 (1e21)**: dia 14 (médio), dia 7 (hardcore), dia 3 (payer), — (não atingido) (casual).
  Dentro da meta de gênero (Fase 2 no horizonte de semanas para perfis ativos).

> O modelo de CICLO (coleta manual sem Coordenador) é o que aproxima o pacing da referência:
> sem coleta o casual jamais prestigia; com coleta 1×/min todos os perfis ativos prestigiam
> no dia 1–2. Recalibrar com dados reais de soft launch (§326).

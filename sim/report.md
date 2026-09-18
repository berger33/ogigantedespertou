# Relatório do Economy Simulator — O GIGANTE DESPERTOU

> Gerado por `npm run sim`. Metas §79, perfis §78, horizontes 1/7/30/90 dias (§199).

## Parâmetros v0.1

- `producerGrowthRate = 1.07`
- Prestígio: `Convictos = (Lifetime/1e6)^0.5`, bônus **linear aditivo** `1 + 3%×Convictos` (§60)
  *(modelo exponencial (1+3%)^n foi testado e rejeitado: runaway super-exponencial, §60/§314)*
- "Mapa 2" (Democracia Relativa) modelado como conclusão da MISSÃO FINAL do Deep Web (mapa 1) — §82
- Perfis: casual 2×3min, medium 5×5min, hardcore 8×8min, payer 8×8min + ×10 permanente

## Resultados por perfil (90 dias)

| Perfil | 1º produtor | 1º prestige | Mapa 2 | Prestiges | Lifetime máx |
|---|---|---|---|---|---|
| casual | dia 1 | dia 2 | — (não atingido) | 87 | 79,92 M |
| medium | dia 1 | dia 1 | dia 10 | 16 | 6,65 T |
| hardcore | dia 1 | dia 1 | dia 3 | 32 | 6,28 T |
| payer | dia 1 | dia 1 | dia 1 | 90 | 6,25 T |

## Progressão por horizonte

| Horizonte | casual | medium | hardcore | payer |
|---|---|---|---|---|
| 1d | 0pg · 269,16 mil | 1pg · 196,86 M | 1pg · 3,93 B | 1pg · 6,25 T |
| 7d | 5pg · 29,83 M | 7pg · 38,74 B | 4pg · 6,28 T | 7pg · 6,25 T |
| 30d | 27pg · 38,9 M | 11pg · 6,65 T | 12pg · 6,28 T | 30pg · 6,25 T |
| 90d | 87pg · 79,92 M | 16pg · 6,65 T | 32pg · 6,28 T | 90pg · 6,25 T |

Leitura: `pg` = prestiges acumulados; valor seguinte = lifetime máximo alcançado no horizonte.

## Leitura rápida (§79–§80)

- **Primeiro produtor**: dia 1 no perfil médio (alvo §81: primeiros minutos).
- **Primeiro prestígio**: dia 1 no perfil médio (hipótese §80 = dia 1).
- **Mapa 2**: dia 10 no perfil médio (calibrar com dados reais pós-soft-launch).

> ⚠️ Primeira calibragem determinística (§28). Rode `npm run sim` a cada mudança de
> economia e ajuste `economy.json` (ou Remote Config) conforme os dados reais.

## Conclusão da calibragem v0.2 (modelo ciclo + Coordenadores)

- **Primeiro produtor**: dia 1 em todos os perfis — atende §81 (primeiros minutos).
- **Primeiro prestígio (1e6)**: dia 1 (médio), dia 1 (hardcore), dia 2 (casual), dia 1 (payer).
- **Mapa 2 (Democracia Relativa)**: dia 10 (médio), dia 3 (hardcore), dia 1 (payer), — (não atingido) (casual).
  Aberto ao concluir a missão final do Deep Web (paridade: última missão do mapa).

> O modelo de CICLO (coleta manual sem Coordenador) é o que aproxima o pacing da referência:
> sem coleta o casual jamais prestigia; com coleta 1×/min todos os perfis ativos prestigiam
> no dia 1–2. Recalibrar com dados reais de soft launch (§326).

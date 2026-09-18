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
| casual | dia 1 | dia 2 | — (não atingido) | 83 | 771,96 M |
| medium | dia 1 | dia 1 | — (não atingido) | 90 | 11,6 T |
| hardcore | dia 1 | dia 1 | — (não atingido) | 90 | 27,97 T |
| payer | dia 1 | dia 1 | — (não atingido) | 90 | 16,38 Qa |

## Progressão por horizonte

| Horizonte | casual | medium | hardcore | payer |
|---|---|---|---|---|
| 1d | 0pg · 120,96 mil | 1pg · 83,55 M | 1pg · 715,29 M | 1pg · 21,62 B |
| 7d | 3pg · 30,88 M | 7pg · 3,14 B | 7pg · 37,69 B | 7pg · 7,39 T |
| 30d | 23pg · 771,96 M | 30pg · 561,75 B | 30pg · 1,55 T | 30pg · 1 Qa |
| 90d | 83pg · 771,96 M | 90pg · 11,6 T | 90pg · 27,97 T | 90pg · 16,38 Qa |

Leitura: `pg` = prestiges acumulados; valor seguinte = lifetime máximo alcançado no horizonte.

## Leitura rápida (§79–§80)

- **Primeiro produtor**: dia 1 no perfil médio (alvo §81: primeiros minutos).
- **Primeiro prestígio**: dia 1 no perfil médio (hipótese §80 = dia 1).
- **Fase 2**: — (não atingido) no perfil médio (calibrar com dados reais pós-soft-launch).

> ⚠️ Primeira calibragem determinística (§28). Rode `npm run sim` a cada mudança de
> economia e ajuste `economy.json` (ou Remote Config) conforme os dados reais.

## Conclusão da calibragem v0.1

- Primeiro produtor e primeiro prestígio no **dia 1** para o perfil médio — atende §80/§81.
- **Fase 2 (1e21) NÃO é atingida em 90 dias** por nenhum perfil nessa economia F1-only.
  Isso é ESPERADO para o PLAYABLE CORE: a Fase 2 exige o conteúdo completo (§31–§34),
  Sósias (×5/×10/×50 §45), Coordenadores e a árvore de prestígio — todos fora do escopo do
  núcleo jogável (§246–§250). A calibragem final da transição de fases acontece com esses
  sistemas no vertical slice, não agora (regra §326: não avançar cedo demais).

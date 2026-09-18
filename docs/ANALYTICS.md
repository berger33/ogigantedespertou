# ANALYTICS.md — O GIGANTE DESPERTOU

> Taxonomia de eventos, parâmetros, funis e KPIs (§175–§181, §294–§297).
> Implementação: Firebase Analytics (ou equivalente) via camada `Analytics`
> (interface no core; implementação por SDK na build de produção).

---

## 1. Eventos (§176)

| Evento | Quando |
|---|---|
| first_open | primeira abertura |
| tutorial_start | FTUE iniciou |
| tutorial_complete | FTUE concluído |
| click_main | toque em Compartilhar no Zap (com combo quando aplicável) |
| producer_buy | compra de produtor (id, phase, qty, custo) |
| producer_milestone | milestone de produtor atingido |
| manager_unlock | Coordenador contratado |
| manager_upgrade | Coordenador upado |
| clone_open | abertura de Sósia |
| clone_duplicate | duplicata → Puxa-Sacos |
| zap_open | abre Zap Vazado (id, categoria) |
| zap_choice | decisão APROVAR/NEGAR (acerto/erro, streak) |
| prestige_preview | abre preview de Convictos |
| prestige_complete | reset concluído (prestige_number) |
| phase_unlock | nova fase liberada (phase) |
| upgrade_buy | upgrade comprado (tipo: clique/global/produtor/offline/evento) |
| daily_claim | recompensa diária coletada (dia) |
| mission_complete | missão concluída (id, tipo diária/semanal) |
| event_join | entra em evento (event_id) |
| rewarded_offer | oferta de rewarded exibida (placement) |
| rewarded_complete | reward resgatado (placement, recompensa) |
| interstitial_impression | interstitial exibido (posição, cap) |
| shop_view | abre Loja de Chumbo / shop |
| iap_start | inicia compra (sku) |
| iap_success | compra concluída (sku, valor) |
| iap_fail | compra falhou (sku, motivo) |

## 2. Parâmetros (§177)

`producer_id, phase, currency, value, manager_id, clone_id, rarity, event_id,
prestige_number, qty, buy_mode`.

## 3. Funil (§179)

install → tutorial → 1º produtor → 1º Coordenador → 1º Zap → 1º Sósia →
1º prestige → Fase 2.

## 4. KPIs (§180, §296)

- Retenção: D1, D3, D7, D14, D30.
- Engajamento: DAU, MAU, DAU/MAU, sessions/day, session length.
- Receita: ARPDAU, ad ARPDAU, IAP ARPDAU, conversion, LTV.
- Aquisição: CPI, ROAS (D1/D7/D30).
- Economia (§181): tempo entre upgrades, frequência de prestige, distribuição de
  produtores, fonte/poço de premium, Chumbo acumulado.

## 5. Decisões baseadas em dados (§241)

| Sintoma | Ação |
|---|---|
| D1 ruim | corrigir FTUE/core |
| D1 bom, D7 ruim | corrigir metagame |
| retenção boa, receita ruim | monetização/economia |
| receita boa, CPI ruim | criativos/ASO |

## 6. Anúncios (§294–§295)

Medir `offer/show/complete/revenue`; impression-level revenue quando suportado
(ad LTV).

## 7. Privacidade (§178)

**Nenhum PII**: nunca nome, telefone, e-mail ou conteúdo real de mensagens.
O "Zap" é 100% fictício interno ao jogo. Ver `PRIVACY.md`.

## 8. Estabilidade (§186)

Crashlytics: crash, nonfatal, breadcrumbs. Meta: crash-free users **> 99%**.

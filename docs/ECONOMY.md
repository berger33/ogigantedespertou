# ECONOMY.md — O GIGANTE DESPERTOU

> Projeto e calibragem da economia. Acompanha o **Economy Simulator**
> (`sim/simulate.js` → `sim/report.md`), fonte de verdade dos números do game.

---

## 1. Objetivos (§76–§83)

1. Oscilações satisfatórias: crescimento rápido → desaceleração → prestige →
   explosão → repetir (§76).
2. Custos **exponenciais**, produção com multiplicadores em **milestones**,
   prestige em **picos**, Sósias em **saltos específicos** (§77).
3. Primeiro prestígio **cedo o suficiente para ensinar** o sistema — hipótese
   §80: **1º dia**.
4. Early game (10 min) com progresso rápido e muitos unlocks (§81);
   endgame sem soft lock.

---

## 2. Moedas e fontes/poços (§17–§19, §181)

| Moeda | Fontes primárias | Poços primários |
|---|---|---|
| Mentes 🧠 | clique, produtores, eventos, bônus, offline | produtores, upgrades, Coordenadores, expansão |
| Chumbo 🛸 | raras (Zap/achievements/eventos), rewarded, IAP | Sósias, cosméticos, conveniência |
| Convictos 🙇 | prestige | árvore permanente (Maçonaria) |

Monitoramento (economy KPI §181): tempo entre upgrades, frequência de prestige,
distribuição de produtores, fonte/poço de premium, Chumbo acumulado.

---

## 3. Constantes de tunagem v0.1 (data-driven → `src/content/economy.json`)

| Parâmetro | Valor v0.1 | Justificativa |
|---|---|---|
| `clickPower` | 1 | 1 toque = 1 Crédulo |
| `producerGrowthRate` | 1.07 | custo exponencial ~×4.9 a cada 25 unidades (ritmo clássico idle) |
| `baseCost` p/ produtor | 15, 100, 1.1k, 12k (4 primeiros) | tutorial rápido no 1º minuto |
| `baseProduction` p/ produtor | 0.1, 1, 8, 47 | 1º produtor paga-se em ~150s de produção |
| `milestones` | 10/25/50/100/250/500/1000 → ×2 cada (encadeado) | §30 |
| `prestigeThreshold` | 1.0e6 Mentes (lifetime) | ≈ primeiro prestígio no dia 1 |
| `prestigeExponent` | 0.5 | Convictos = (Lifetime/1e6)^0.5 |
| `convictBonus` | +3% (multiplicativo) por Convicto | hipótese §60 (calibrar) |
| `offlineCapHours` | 4 (base) | §87 |
| `viralComboMax` | ×2 | teto Engajamento Viral §24 |

> **IMPORTANTE §28/§45/§60/§76/§80:** nenhum destes números é dogma — a
> calibragem vem do simulador + Remote Config pós-lançamento.

---

## 4. Curvas-alvo (referência)

```
Custo(n)       ≈ BaseCost * 1.07^n            (exponencial)
Produção/Temps ≈ Σ BaseProd_i * owned_i * MilestoneProd_i * Globais
Globais         = Prestigio * Clones(por produtor) * events * shop
Mentes(t)       ≈ ∫ produção dt              (idle) + clique * combo
```

**Regra de não-runaway (§60):** Convictos usam fórmula sublinear
(`^expoente < 1`) e bônus multiplicativo por Convicto tem teto de tuning via
Remote Config, impedindo progressão infinita sem investimento adicional.

---

## 5. Raridade de Sósias (§45) — hipótese a validar

| Raridade | × | Papel no ritmo |
|---|---|---|
| Comum | ×5 | salto frequente |
| Incomum | ×10 | salto médio |
| Raro | ×50 | pico perceptível |
| (Épico/Lendário) | — | só se a economia justificar (§44) |

*Regra:* Sósias são **multiplicador por produtor/estágio** (não global), o que
controla o impacto e mantém a coleção relevante por fase.

---

## 6. Perfis de simulação (§78–§79, §199)

| Perfil | Comportamento |
|---|---|
| casual | poucas sessões/dia, gasta "quando dá" |
| medium | 2–5 sessões, compra ótimo aproximado |
| hardcore | ativo, compra ótimo, prestigia cedo |
| payer | hardcore + Chumbo/Sósias pagas |

Horizontes: 1h, 1d, 7d, 30d, 90d. **Meta de relatório:** responder
"quando ocorre 1º produtor, 1º Coordenador, 1º Sósia, 1º prestige, Fase 2/3/4".

---

## 7. Resultados atuais

Ver `sim/report.md` (gerado por `npm run sim`). Resumo v0.1: primeiro produtor e
primeiro prestígio no **dia 1** (perfil médio); Fase 2 não é alcançada no core
(esperado — depende de Sósias/Coordenadores/árvore de prestígio, fora do escopo
do PLAYABLE CORE §246–§250). Detalhe: ver conclusão da calibragem no relatório.

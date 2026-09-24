# MONETIZATION.md — O GIGANTE DESPERTOU

> Estratégia de monetização (§141–§160, §332–§333). Princípio: **retenção em
> primeiro lugar**; jogador free joga tudo; nunca explorar vulnerabilidade.

---

## 1. Ordem de prioridade (§141)

1. Retenção
2. Rewarded ads
3. IAP
4. Interstitial moderado

Jogador gratuito deve conseguir: jogar tudo, progredir, prestigiar e terminar o
conteúdo principal (§142).

---

## 2. Rewarded Ads (§143–§145)

| Placement | Recompensa |
|---|---|
| 2× offline (DUPLICAR RELATÓRIO) | dobra ganho offline |
| 2× produção temporária (TURBINAR ALGORITMO) | ×2 por 15–30 min (testar) |
| Chumbo pequeno | quantidade calibrada |
| Reroll do Zap | nova mensagem |
| Boost de clique | duração testada |
| Abrir dossiê bônus | conteúdo |
| Tempo de evento | prolonga evento |

- **1 abertura de Sósia gratuita periódica via rewarded** (frequency cap).
- Nunca rewarded no clique, durante reveal, ou quebrando flow.

## 3. Interstitial (§146–§147)

- Só em **transições naturais**; nunca no clique, no Zap, durante reveal.
- **Zero interstitials nas primeiras sessões.**
- Frequency cap via Remote Config (tempo mínimo entre anúncios).

## 4. Banners & App-open (§148–§149)

- Banners: evitar inicialmente (espaço/imersão).
- App-open: **não** por padrão; testar só se dados mostrarem sem dano à retenção.

## 5. IAP (§150–§153)

Produtos: **Starter Pack, No Ads, Chumbo pequeno/médio/grande, Dossiê Premium**.

- **No Ads**: remove interstitials; rewarded permanece opcional.
- **Starter Pack**: após o jogador entender a economia; Chumbo + boost + Sósia
  garantido + No Ads (permanente/temporário conforme config).
- **Chumbo**: comunicação clara; **nunca** "500% de desconto" falso.

## 6. Probabilidades, pity e fairness (§154–§155, §68)

- Abertura comprável de Sósias → **probabilidades exibidas**.
- **Pity system**: após N aberturas, garantir raridade superior.
- Nada de mecânica predatória.

## 7. Bundles & ofertas (§156–§157)

- Bundles temáticos (ex.: Operação Varginha: skin + Sósia + Chumbo + boost).
- Ofertas segmentadas por **progresso**, nunca por vulnerabilidade pessoal.
- **Preços localizados** para Brasil (§158); A/B apenas quando permitido.

## 8. Mediação (§159–§160)

- Arquitetura compatível com **AdMob Mediation**; preparar bidding.
- Não integrar 10 redes no MVP.
- **Test mode**: só test ads em desenvolvimento; nunca clicar ad real interno.

## 9. Anti-cheat & IAP (§206–§208)

- Nunca confiar só no cliente para IAP/premium crítica.
- Validação de IAP + restore + pending purchase.

## 10. Custo de aquisição & escala (§296–§298)

Escalar só quando **LTV esperado > CAC** (com margem); corrigir produto antes de
comprar tráfego grande. Revenue vem de: ads + IAP + eventos + passe — sem
depender de um único whale (§332).

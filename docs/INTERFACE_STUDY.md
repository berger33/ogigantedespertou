# ESTUDO DE INTERFACE & MECÂNICA — REFERÊNCIA We Are Illuminati

> Reconstrução minuciosa da **estrutura de interface e das mecânicas** do
> We Are Illuminati (Tapps), a partir da wiki da comunidade (todas as páginas) e
> do comportamento padrão do gênero. Objetivo: **paridade estrutural** para
> O GIGANTE DESPERTOU (§2: referência de gênero; nomes/artes/lore são nossos).
>
> ⚠️ Nota do ambiente: as imagens que você anexou NÃO puderam ser visualizadas
> nesta sessão (sem recurso de visão + arquivos não disponíveis no workspace).
> Este estudo é baseado em fontes textuais completas da wiki + descrições
> públicas de cada tela. Onde houver incerteza de pixel, marco como [reconstrução].

---

## 1. Telas e menus do jogo referência (mapeamento completo)

### 1.1 Tela principal (sede / "HQ" / palco de influência)
Elementos por região (topo → base):

- **Canto superior esquerdo**: botão ⚙ **Settings** (sempre visível) +, ao lado,
  o ícone do **Laboratório de Clonagem** (desbloqueado após a Deep Web; "oposto
  ao botão de wiretaps").
- **Canto superior direito**: contador de **💎 diamantes** + botão da **Loja**;
  e o botão de **📡 Wiretaps** (grampos) — ícone no topo direito.
- **Centro/topo**: o **contador de influência (pessoas)** em fonte grande — o
  número que domina a tela — acompanhado do nome/fase atual.
- **Faixa de cenário (banner)**: ilustração full-width do **estágio atual**
  (Deep Web = Nailitper no computador à noite; Ditadura = púlpito/comício;
  Área 51 = estrada+UFOs; Bancos = cofre/cidade dourada). Setas **← →** nas
  laterais navegam entre estágios desbloqueados.
- **Região central (rolável)**: a **lista vertical de produtores**. Cada card:
  - **À esquerda**: ilustração **emoldurada em loop** (animação do produtor);
  - nome do produtor acima da moldura;
  - **inferior esquerdo**: **timer/cooldown** (tempo até o próximo lucro);
  - **inferior direito**: **botão de upgrade** do produtor (mostra custo) +
    **rating de estrelas** (canto sup. direito do card: 5 bronze → prata → ouro)
    + **ícone de tanque de clone** (cinza = vazio; ocupado = mostra perfil).
- **Dock inferior**: barra fixa de botões dos menus — Upgrades, Managers,
  Inner Circle (prestígio), Shop. Navegação por uma mão, portrait.

### 1.2 Menus (acessados pelo dock/topos)
| Menu | Função | Elementos-chave |
|---|---|---|
| **Upgrades** | compras com **pessoas** | cards de upgrade (×3 por produtor + global), botão **Buy All** (lib. por Aleister Raw) |
| **Managers** | automação (compra c/ pessoas) | 12 retratos + nome + produtor + custo; Aleister Raw no rodapé (custa lackeys) |
| **Inner Circle** | **brainwash/prestígio** | % de bônus por lackey, 2 botões (Hypnotizing bomb=reset grátis / Buy loyalty=manter por 10💎), lista de lackey upgrades |
| **Cloning lab** | gacha de clones | tanque central, custo 💎, revelação em 3 toques (rachadura→luz→abre), lista de clones/tiers |
| **Wiretaps** | minigame | mensagens pró/anti (verde/vermelha), botões **Aprovar/Negar**, recompensas (💎/pessoas/lackeys) |
| **Shop** | premium | área VIP no topo, compras com 💎 (Production×3, Speed×2, Buy lackeys, Time warp 1/7/14d, Ad boost), pacotes de 💎 + Remove Ads |

### 1.3 Diálogos/overlays
- **Offline report / Welcome back!**: "double people earned" (rewarded).
- **Rate Us**: popup ao comprar "foment conspiracy theories".
- **Exit game**: popup de confirmação ao sair (back arrow).
- **Special offers**: ofertas com cronômetro (diamantes/clone raro) com ícone lateral.

---

## 2. Mecânicas (com números documentados pela wiki)

### 2.1 Moedas
| Referência | Nossa equivalente |
|---|---|
| People (pessoas) | **Crédulos 👁** |
| Diamonds 💎 (premium) | **Chumbo 🛸** |
| Lackeys (prestígio) | **Convictos 👁‍🗨** |

- Lackeys: +3%/unidade **na base**, escalando até ~49% via upgrades do Inner Circle.
- Diamantes: wiretaps, ofertas, IAP; usados em clones, shop, Buy loyalty.

### 2.2 Produção
- 10 produtores (nós: 12, por spec §27). Nomes idênticos em todos os estágios;
  custo/lucro crescem por estágio.
- **Custo do 1º de cada produtor (Deep Web, wiki):**
  `12 · 60 · 700 · 8340 · 90 680 · 1,04M · 14,93M · 179,16M · 2,15B · 25,80B`
  (razão ≈ ×11–12 entre produtores consecutivos).
- **GrowthRate 1,07** (padrão do gênero; custo exponencial por unidade).
- **Timer/cooldown** por produtor; upgrades de estrelas reduzem até **0s** (lucro contínuo).
- **Milestones por produtor** (quantidade → bônus) — reforçado pelo design §30.

### 2.3 Automação (Managers) — MECÂNICA CENTRAL
- Antes do manager: o produtor **acumula** lucro no ciclo; o jogador **toca para coletar**.
- Depois: **produção automática**, inclusive offline.
- Custos (wiki): `1k · 15k · 100k · 500k · 1,2M · 10M · 500M · 60B · 720B · 8,6T`.
- **Aleister Raw** (10 lackeys) desbloqueia o **Buy All**. → nosso **Zé do Chapéu de Alumínio** (10 Convictos), frase *"Eu já sabia que você ia clicar."*

### 2.4 Upgrades (pessoas) — Deep Web (wiki)
- Por produtor ×3: `25k · 50k · 150k · 500k · 5M · 15M · 5B · 150B · 50T · 15Qa`.
- Global ×3: `50 Qi` ("Are we having fun yet?").
- Tier ×10: `10,0 Dtg` cada (endgame) + global extra.

### 2.5 Clones (gacha) — wiki
- Preço: **15💎** (extra a 10💎 logo após; página principal diz 5💎 — divergência, usar 15/10).
- Raridades: **Comum ×5 (verde) · Incomum ×10 (roxo) · Raro ×50 (dourado+aura)**.
- Bônus **por produtor de um estágio** (não global). Duplicatas → **lackeys**.
- Reveal em 3 toques; 1º clone grátis (Agent Smite).

### 2.6 Brainwash (prestígio)
- **Hypnotizing bomb** (grátis) = reset total → lackeys; **Buy loyalty** (10💎) = ganha lackeys **sem** resetar.
- Preserva: 💎, clones, lackeys atuais, upgrades permanentes da loja.
- Ad pós-brainwash: +~20% lackeys.

### 2.7 Wiretaps (minigame)
- Mensagens **pró** (verde) / **anti** (vermelho); **aprovar/negar**; acerto → recompensa ocasional (💎/pessoas/lackeys); erro → neutro/zero.
- Fonte-chave de diamantes.

### 2.8 Shop 💎 (wiki, custos)
`Production x3 (30) · Speed x2 (20) · Buy lackeys (10) · Time warp 1d (10) / 7d (40) / 14d (70) · Ad boost +1 (10)` + pacotes de 💎 + Remove Ads + VIP (tiers com %).

### 2.9 Prestígio "lackeys" (tabela completa de lackey upgrades)
`Industrial spy 12.7k · Immortality serum 634k · Wealthy members 31,7M · Freak followers 1,6B · Symbols in paper money 79,2B · Secret doctrine 4,0T · Necronomicon 198T · Emerald tables 9,9Qa · Technobabble 495Qa · Atlantis was real 22,5Qi · Professional liars 1,0Sx · Otherkin followers 46,5Sx · Emotive hymn 2,1Sp · Star people 96Sp · Obliviated praisers 4,4Oc · Book of quotes 198Oc · VIP social media 9,0No · Skin-walkers 410No · Solemn vow 18,6Dc · Golden apple 847Dc · Mad Scientist's Cat 38,5Ud · Mask Play 1,8Dd · A Trilogy Book 79,5Dd · Irrational Rationalism 3,6Td · Wererobots 164Td · Citadel of Science 7,5Qad · Five Tons of Flax 340Qad · Consciousness Exploration 15,4Qid`
(bônus por lackey acumulado: 4% → 7% → 9% → 14% → 19% → 26% → 33% → 40% → 49% → +10%…).

---

## 3. Tradução para O GIGANTE DESPERTOU (paridade)

| Referência | Nosso sistema | Status |
|---|---|---|
| Prestígio/brainwash (Inner Circle) | **Despertar o Gigante** (Maçonaria Nacional) | ✅ core (ajustar UI) |
| Managers → automação | **Coordenadores** | ✅ implementar agora |
| Upgrades (pessoas) | **Loja de Melhorias** | ✅ implementar agora |
| Clones (gacha) | **Laboratório de Sósias** | ✅ implementar agora |
| Wiretaps | **Zap Vazado** | ✅ implementar agora |
| Shop (💎) | **Loja de Chumbo** | ✅ implementar agora |
| Workers/estágios | **Mapa da Dominação** (4 fases) | ✅ implementar agora |
| Offline/duplo | **Relatório offline** | ✅ core (UI ok) |
| Coleta manual → auto por manager | **tal abrir** | ✅ implementar agora (mecânica central) |

**Curva/pacing (§2):** carregar a MESMA curva (custos 12→60↔…, growth 1.07,
managers 1k→8,6T, upgrades 25k→15Qa, prestige linear +3%/Convicto) para a
sensaão de "mesma quantidade de cliques".

---

## 4. Plano de paridade visual (9 telas + dock)

Reconstruo a tela principal e os 8 menus na ordem e posições padrão:

```
HUD topo: [⚙][🔬lab]         [💎][📡zaps]
          [👁👁👁 grandão contador de Crédulos]
          [ banner do estágio + ← → ]
          [ lista vertical de produtores (ilustração + timer + upgrade + estrelas + tanque) ]
dock:     [Melhorias][Coordenadores][Maçonaria][Loja][Arquivo]
```
> Botões/menus equivalentes a: Upgrades, Managers, Inner Circle, Shop — e
> Zap Vazado/Laboratório acessíveis pelo topo, como no jogo referência.

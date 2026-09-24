# PLANO DE ANIMAÇÃO — O GIGANTE DESPERTOU

> **⚠ SUCESSOR:** a produção visual agora é regida por
> **[`VISUAL_IMPLEMENTATION_PLAN.md`](VISUAL_IMPLEMENTATION_PLAN.md)** (estudo
> quadro-a-quadro do gameplay real + pipeline IA + lotes A–H). A **auditoria do
> movimento** (por que o loop parecia simples/quebrado, e o que mudou) está em
> **[`ANIMATION_AUDIT.md`](ANIMATION_AUDIT.md)**. Este documento permanece como
> fonte do **inventário criativo das 50 cenas** e do histórico de lotes.
>
> **Objetivo:** criar animações próprias para cada **ação/missão** (e telas/efeitos),
> com o *ritmo, enquadramento e densidade* do gênero (We Are Illuminati), porém com
> **tema, personagens e arte 100% originais** (regra anti-cópia §2/§66).
> Este plano é o complemento de `ART_BIBLE.md` e `VISUAL_PARITY.md`.

---

## 1. O que o vídeo de referência mostra (estudo objetivo)

Fonte: `We are Illuminati- Conspiracy Simulator Clicker.mp4` (subido pelo autor).
Características técnicas do trailer:

| Propriedade | Valor | O que significa |
|---|---|---|
| Duração | 40,25 s | trailer promocional, não catálogo de missões |
| Resolução | 400×720 (retrato) | tela de celular vertical → cenas curtas e legíveis em formato alto |
| FPS | 30 | loops suaves, sem economia de frames visível |
| Cenas | ~9 cortes | 1 tela de HQ longa + ~6 planos de ação de ~3s + 1 tela final |

**Cronograma de cenas (por medição de corte + movimento):**

| Tempo | Leitura |
|---|---|
| 0,0–13,7s | **Tela principal (HQ)** quase estática; movimento só no *centro* (painel de clique/ator principal). Fundo imóvel |
| 13,7–16,9s | corte + movimento em todas as regiões → transição de tela |
| 16,9–19,7s | ação nº1 (~3s) |
| 19,7–22,8s | ação nº2 (~3s) |
| 22,8–23,3s | **pico de movimento** → reveal/prestígio (transição monumental) |
| 23,3–25,9s | ação nº3 |
| 25,9–29,4s | ação nº4 (maior movimento central do vídeo) |
| 29,4–32,9s | ação nº5 |
| 32,9–40,1s | **tela final** (escura/roxo, parada) — resultado/rate-us |

**Leituras de design (o que copiar em *estrutura*, nunca em arte):**

1. **Uma ação = uma "cena emoldurada"** que loopa num quadro. Não é animação de tela
   cheia; é um **diorama** dentro do card do produtor/missão.
2. **Fundo paradão, ator em loop.** A energia do vídeo está quase toda no *centro*
   do quadro (o ator + partículas), o fundo serve de cenário.
3. **~3s por ação no trailer** = cada cena precisa ler-se em 2–3s (silhueta + cor + 1 movimento forte).
4. **Transições "monumentais"** para prestígio/fase (pico de movimento 22,8s): tela
   treme, luz, explosão de partículas — ver §9 do ART_BIBLE (VFX).
5. **Paleta dominante:** base convicta com **roxo/rosa hipnótico** como cor de "ação forte"
   (corresponde ao nosso "Alien verde-neon" + adicionar roxo hipnótico como acento de VFX).

---

## 2. Como o gênero FAZ a animação (gramática técnica)

Idle clickers do tipo "conspiracy/empire" quase sempre usam a mesma receita barata e
escalável — **não** vídeo 3D pesado:

| Técnica | Quando usam | Custo relativo |
|---|---|---|
| **Skeletal 2D** (Spine/DragonBones/Animator) | personagens (chefes, sósias, ator central) | alto por personagem, baixo por variação |
| **Transform-lerp em camadas** (PNG/SVG + translate/rotate/scale loop) | a maioria dos produtores: objeto/figura que treme/sobe/gira | **baixo** — é o carro-chefe |
| **Sprite frame-a-frame** (Aseprite/PS) | efeitos cíclicos (moedas, olhos piscando, espiral) | baixo (poucos frames: 4–8) |
| **Partículas** (pool) | moedas/pessoas voando, confete, carimbos | baixo, reaproveitável |
| **Screen FX** (shake, flash, vignette) | prestige, fase, raro | 1× global, reusado |

**Tradução para o nosso jogo (original, mesmo ritmo):**

- **Moldura:** dossiê/pasta (nosso "OS clandestino", ART_BIBLE §8), não a moldura deles.
- **Camadas por cena (3):** `bg` (fundo fixo) → `actor` (ator em loop) → `fx` (partículas/efeito).
- **2 estados por cena:**
  - `idle` — loop sutil (respiração, piscada); usado quando a missão existe mas sem produção;
  - `running` — loop principal (a "ação" acontecendo, ~0,8–1,6s); ativado pelo Coordenador.
- **Regra de loop:** tudo é infinito e sem "fim", para ficar barato e estável no celular.

---

## 3. Inventário criativo — a cena de cada uma das 40 missões

> Formato: **bg / actor / fx** (o que cada camada mostra). Humor pt-BR original, sátira
> do "maquinário da conspiração", nunca alvos reais (regras de sátira do `SATIRE_GUIDELINES.md`).

### Mapa 1 — Deep Web (`p1_01..p1_10`)

| Missão | bg | actor (loop) | fx |
|---|---|---|---|
| Comprar as maiores empresas com cripto | pregão de bolsa verde | mão clicando "COMPRAR" em notebook | gráfico subindo + 🧠 cifradas |
| Plantar fake news na mídia | banca de jornal | manchete gigante se **reescrevendo** | "BREAKING" piscando |
| Fazer amizade com os reptilianos | embaixada escamosa | lagarto de terno tomando café | olho escamoso piscando |
| Colocar informante no governo | gabinete oficial | pasta "CONSELHEIRO" passando de mão em mão | carimbo CONFIDENCIAL |
| Fomentar teorias da conspiração | quadro de barbante | linhas/alfinetes ligando fotos | post-its vibrando |
| Lavar o cérebro de artistas pop | camarim | diva de fones + espiral hipnótica no olho | notas musicais em espiral |
| Começar guerras por lucro | mapa tático | alfinete de mira caindo no mapa | cifrões de "fumaça" (sem violência) |
| Controlar mentes pelo Wi-Fi | torre-roteador | ondas saindo do roteador | cérebros 🧠 viajando nas ondas |
| Manipular governantes fantoches | palanque | marionete de terno pendurada por cordas | cordas sendo puxadas |
| Gerenciar sistemas de controle do clima | painel meteorológico | botão SOL/CHUVA alternando | nuvem + sol + raio cômico |

### Mapa 2 — Democracia Relativa (`p2_01..p2_10`)

| Missão | bg | actor | fx |
|---|---|---|---|
| Comprar o voto do tio do grupo | sala de família | santinho + voto trocando de mão | votos voando |
| Encomendar a pesquisa que prova o que a gente quer | infográfico | pesquisador "tendencioso" girando gráfico | barras subindo até 99% |
| Fundar o partido do meio-termo | sede de partido | político **em cima do muro** (literal) | muro balançando |
| Espalhar a emenda "totalmente pública" | Diário Oficial | caneta assinando | letras impressas saindo |
| Sessão plenária com robôs | plenário | robô digitando na mesa | luzes de votação |
| Cabo eleitoral com megafone | praça | cidadão com megafone | ondas sonoras |
| Comício com promessas em dupla | palco | dupla sertaneja prometendo | confete |
| Escrever a "Constituição do Zap" | documento oficial | mensagens de Zap virando artigos | "encaminhando…" |
| Eleger um sósia por procuração | urna eletrônica | sósia de óculos entrando | carimbo ELEITO |
| Proclamar a Democracia Relativa™ | praça lotada | martelo batendo | "50%" gigante + confete |

### Mapa 3 — Ratanabá (`p3_01..p3_10`)

| Missão | bg | actor | fx |
|---|---|---|---|
| Escavar a entrada da cidade subterrânea | terreno | broca/perfuratriz vibrando | terra voando |
| Ativar o Wi-Fi da cidade invisível | caverna | roteador subterrâneo | ondas "ocultas" |
| Contratar o cartógrafo que viu o mapa | mesa de mapa | mapa se **redesenhando sozinho** | traços surgindo |
| Comprar terreno na capital oculta | escritório | caneta assinando escritura do nada | papel voando |
| Vender excursão para o subsolo | entrada de túnel | guia com lanterna acenando | tickets voando |
| Abrir o consulado de Ratanabá | embaixada | mastro **sem bandeira** tremulando | vento |
| Exportar ouro dos incas por Sedex | correros | caixa Sedex brilhando | ouro caindo do pacote |
| Eleger o prefeito do nada | prefeitura | cadeira vazia com faixa | poeira/mato rolando |
| Imprimir a moeda de Ratanabá | casa da moeda | prensa cunhando | notas voando |
| Revelar a entrada oficial (com catraca) | porta secreta | catraca dourada girando | brilho |

### Mapa 4 — Religião (`p4_01..p4_10`)

| Missão | bg | actor | fx |
|---|---|---|---|
| Fundar o templo da fé com cashback | caixa/totem | "TROCO DA FÉ" na tela | moedas voltando |
| Transmitir o sermão em 8K com IA | tela gigante | avatar-pastora/or de glitch | pixels |
| Autenticar a relíquia "do milênio" | vitrine | relíquia girando | auréola |
| Vender a água da torneira abençoada | torneira | jato caindo na garrafa | gotas com halo |
| Adiar o apocalipse (de novo) | calendário | mão remarcando a data | páginas virando |
| Bingo solidário do juízo final | cartela | números sendo chamados | "BINGO!" |
| Restaurar a imagem que "chora" xarope | quadro na parede | rosto "chorando" | gotas de xarope dourado |
| Comandar o retiro do arrepio garantido | tenda | pessoa arrepiando | calafrio/estrelas |
| Redescobrir o 13º mandamento (no áudio) | celular | waveform de 11 min | barra de áudio mexendo |
| Abrir a filial no céu | nuvens | prédio "FILIAL ™" flutuando | raio cômico + luz |

---

## 4. Pipeline técnico (dado → tela)

### 4.1 Fonte única: spec de animação data-driven

Cada missão ganha um objeto `anim` (arquivo `src/content/animations.json`, gerado por
`tools/gen_animations.py` junto de `gen_campaign.py` — mesma disciplina data-driven):

```json
{
  "p1_01": {
    "layers": [
      { "role": "bg",    "src": "anim/p1_01_bg",   "loop": null },
      { "role": "actor", "src": "anim/p1_01_actor","loop": { "type": "bob",   "dur": 1.6, "amp": 6 } },
      { "role": "actor", "src": "anim/p1_01_hand", "loop": { "type": "press", "dur": 1.6 } },
      { "role": "fx",    "src": "anim/p1_01_fx",   "loop": { "type": "rise",  "dur": 1.6, "spawn": 3 } }
    ],
    "states": {
      "idle":    { "actor": "bob-slow", "fx": "off" },
      "running": { "actor": "loop",     "fx": "on" }
    },
    "accent": "#B57BFF"
  }
}
```

- `loop.type` ∈ { `bob`, `press`, `rise`, `spin`, `pulse`, `wiggle`, `blink`, `scroll`, `shake` }.
- O **renderer** interpreta o spec; a **arte** é trocável sem tocar código.

### 4.2 Renderizadores

| Alvo | Como renderiza | Observação |
|---|---|---|
| **Protótipo web (hoje)** | camadas SVG/PNG + timeline CSS/Canvas (já temos keyframes no `app.css`) | prova rápida, vira a "referência de ritmo" |
| **Unity (alvo final)** | importa o mesmo `animations.json` + **Animator/DOTween** (transform-lerp) ou **Spine/DragonBones** para personagens | espelho C# já em `unity/` |

### 4.3 Produção do asset (por cena)

1. Definir a cena no brief (tabela §3) → 2. gerar camadas (bg/actor/fx) →
3. **padronizar** na Art Bible (paleta/linha/sombra — anti-cara-de-IA §220) →
4. exportar (PNG com alpha ou SVG) → 5. plumb no `animations.json` → 6. QA em celular.

> Regra de ouro (ART_BIBLE §12): aprovada a direção (Lote 0) ANTES de produção em massa.

---

## 5. Lotes (batches) — sim, faremos em lotes

Cada lote termina com: assets commitados + spec no `animations.json` + renderizável
no protótipo web + revisão visual sua + QA no device.

| Lote | Escopo | Entregável | Status |
|---|---|---|---|
| **0 — Fundação/POC** | 1 cena completa ponta-a-ponta (p1_01) + paleta/reference sheet + o `animations.json` + renderer do protótipo | prova de pipeline: 1 ação animando de verdade | ✅ **entregue** |
| **1 — Deep Web** | p1_02..p1_10 (10 cenas) + refinamento da p1_01 | mapas rodando com 10 ações animadas | ✅ **entregue** |
| **2 — Democracia Relativa** | p2_01..p2_10 | +10 ações | ✅ **entregue** (100% ilustrado) |
| **3 — Pindorama** (renomeado de Ratanabá) | p3_01..p3_10 | +10 ações | ✅ **entregue** (100% ilustrado) |
| **4 — Religião** | p4_01..p4_10 | as 50 ações animadas | ✅ **entregue** (100% ilustrado) |
| **4b — Singularidade** (5º mapa novo) | p5_01..p5_10 | +10 ações (chip como missão final) | ✅ **entregue** (set/2026, lote G) |
| **5 — Personagens** | 40 bustos de Coordenadores (4 expressões) + 40 sósias por raridade | coleção completa | ⏳ |
| **6 — Telas & VFX** | backgrounds HQ por mapa (parallax) + transições de fase/prestígio + carimbos | polimento "quadro completo" | ⏳ |

**Ordem de prioridade** = ordem acima (core jogável primeiro; personagens por último —
antes do conteúdo volumoso, provar o loop da economia/ritmo — regra MVP).

### Produção set/2026 — Substituição gradual por ilustrações pintadas originais

Para garantir que **cada missão tenha um elenco visual único e original** no
estilo cartum de *We Are Illuminati* (sem figuras procedurais repetidas e sem
reutilização de personagens entre missões), os quadros-mestres são gerados em
lotes dedicados de IA com prompts de cena específicos e gags satíricos próprios.

- **Deep Web (Mapa 1): 10/10 pintadas (100% completo)**
  - `p1_01`: pregão cripto (investidor com laptop)
  - `p1_02`: banca de jornal com manchete se reescrevendo
  - `p1_03`: embaixada escamosa (reptiliano de terno e café)
  - `p1_04`: gabinete oficial (pasta conselheiro e carimbo)
  - `p1_05`: quadro conspiratório de barbante e alfinetes
  - `p1_06`: camarim de diva pop com fones hipnóticos
  - `p1_07`: mapa tático de guerra com mira e cifrões
  - `p1_08`: torre-roteador de controle mental com ondas
  - `p1_09`: **teatro de marionete** (diretor com monóculo e boneco de terno no palco)
  - `p1_10`: **laboratório meteorológico** (cientista louco com alavanca e radar de sol/raio)

- **Democracia Relativa (Mapa 2): 10/10 pintadas (100% completo)**
  - `p2_01`: **varanda de praia com churrasco** (tio com espetinho e santinho de campanha)
  - `p2_02`: **sala de estatística** (pesquisador com vara apontando gráfico 99% verde)
  - `p2_03`: palanque em cima do muro (político literal no muro 50/50)
  - `p2_04`: **desfile na praça** (prefeito com chapéu de caubói no trator de ouro)
  - `p2_05`: **plenário à meia-noite** (robôs retrô apertando botões de votação)
  - `p2_06`: **praça pública** (cabo eleitoral com megafone vermelho e panfletos voando)
  - `p2_07`: **palco de comício** (dupla sertaneja com violas, ternos brilhantes e confete)
  - `p2_08`: **gabinete de leis** (escriba com pena verde reluzente e rolo de pergaminho de Zap)
  - `p2_09`: **cabine de votação** (sósia suando com bigode postiço torto saindo da cortina)
  - `p2_10`: **salão do conselho** (magistrado cerimonioso de peruca batendo martelo de ouro na balança 50/50)

- **Pindorama (Mapa 3): 10/10 pintadas (100% completo)**
  - `p3_01`: **escavação de Ratanabá** (broca monumental perfurando ruínas douradas)
  - `p3_02`: **E.T. de Varginha** (alienígena verde amigável com boné e café na lanchonete)
  - `p3_03`: **indústria da multa** (guarda camuflado de moita disparando flash de radar na rodovia)
  - `p3_04`: **o chupa-cabra** (criaturinha roxa com asas de morcego tomando suco de canudo com cabra estilosa)
  - `p3_05`: **carro elétrico nacional** (mecânico com óculos de solda ligando tomada gigante em carro retrô faiscante)
  - `p3_06`: **o túnel subterrâneo** (conspiracionistas com lanternas no metrô secreto)
  - `p3_07`: **GPS de todo mundo** (espião de bigode e fones espremido dentro do orelhão gigante, farejando trilhas de GPS em painéis holográficos — um deles com o mapa do Brasil em pontinhos)
  - `p3_08`: **chip no papel timbre** (perito de unibrow e viseira verde com lupa gigante revelando o circuito impresso verde escondido no RG, entre torres de papel e carimbo CONFIDENCIAL)
  - `p3_09`: **taxa na transferência instantânea** (mão gigante do fisco de terno saindo da nuvem roxa e mordendo um naco da moeda no meio do feixe de transferência do celular — sem citar marcas)
  - `p3_10`: **moeda magnética** (superímã vermelho no topo do cofre puxando em espiral as cédulas e moedas dos bolsos virados dos pedestres zonzo)

- **Religião (Mapa 4): 10/10 pintadas (100% completo)**
  - `p4_01`: **mensagem invertida no vinil** — DJ de batinha roxa rodando o disco ao contrário numa vitrola com chifrinhos, entre velas e espirais hipnóticas
  - `p4_02`: **desenho da indução** — criança de olhos em espiral hipnotizada pelo diabinho fofo da TV de tubo, com o gato igualmente hipnotizado ao lado
  - `p4_03`: **fábrica do boneco possuído** — boneção rechonchudo levitando entre orbes roxos e botões flutuantes, chavinha girando, artesão de avental apavorado com o pincel de cola
  - `p4_04`: **cidade maçônica** (geometria secreta pulsando)
  - `p4_05`: **milagre na TV** (facho varrendo o palco)
  - `p4_06`: **imagem que chora xarope** — retrato dourado derramando lágrimas de xarope e o espertinho de colete recolhendo a pinga no potinho com conchinha
  - `p4_07`: **13º mandamento só no áudio** — arquivista de manto cochichando no microfone de fita enquanto a onda sonora sobe em espiral e vira uma tábua de puro som
  - `p4_08`: **água da torneira abençoada** — torneira de pedestal enchendo garrafinhas em esteira, cada tampa recebendo auréola dourada do inspetor de jaleco
  - `p4_09`: **apocalipse adiado (de novo)** — profetinha de camisola e chapéu de festa empurrando suado o bloco vermelho X do fim do mundo para frente no calendário rabiscado
  - `p4_10`: **arrebatamento holográfico / Blue Beam** (grade LED + raio)

- **Singularidade (Mapa 5): 10/10 pintadas (100% completo)**
  - `p5_01`: **feixe sobre o cerrado** — técnico de chapéu de palha armando a chave de facão monumental, acendendo a coluna verde da antena no meio dos cupins e vaga-lumes
  - `p5_02`: **fórmula da água** — técnico de óculos pingando a dose ciano no tanque; o manômetro pulsa no vermelho
  - `p5_03`: **ensaio do apagão** — as janelinhas do painel apagam em onda; só o alarme vermelho fica
  - `p5_04`: **Skynet terminal**, `p5_07`: **pombo drone**, `p5_10`: **o chip no restaurante**
  - `p5_05`: **aparelhos escutando** — ondas do alto-falante e a varredura fica dentro da TV do anúncio de pneu
  - `p5_06`: **presidente 2.0** — robô sorridente de faixa dourada, faíscas no compartimento da bateria
  - `p5_08`: **malha de torres** — torre caída no canteiro, regada pelo jardineiro, anéis de sinal
  - `p5_09`: **prato-QR** — chef fecha o código de arroz e feijão com a última gota de molho
  - **Total pintado: 50/50 (100%)**. Lote H (`rec_p5_02`, `rec_p5_03`, `rec_p5_05`, `rec_p5_06`, `rec_p5_08`, `rec_p5_09`: dose que cai, apagão célula a célula, varredura na tela, faísca da bateria, led da torre, gota no QR).

### Produção set/2026 — lotes E, F e G (50 cenas 100% animadas em 2D)

Conteúdo novo (antes da arte):
- **Mapa 3 renomeado para Pindorama** (10 conspirações brasileiras: Ratanabá,
  E.T. de Varginha, indústria da multa, chupa-cabra, carro elétrico nacional,
  túnel subterrâneo, celulares monitores, chips em documentos, dinheiro
  instantâneo — **nunca o nome "Pix"** — e moeda magnética).
- **Mapa 4 Religião** com as 10 missões reescritas (vinil invertido, desenho da
  indução, brinquedos possuídos, cidade ocultista, milagre na TV, imagem que
  chora, 13º mandamento, água abençoada, apocalipse adiado, arrebatamento
  holográfico/Blue Beam).
- **Mapa 5 novo: Singularidade** (10 conspirações tech; **implantação do chip =
  missão final**). Economia do `phase5` extrapolada no `producers.json`
  (base 7.349e39, custo ×1.2 por slot); `managers.json` completo com 50.

Arte (mesma spec v4: 4 quadros, flat-toon, outline grosso, dark teal + acento
por missão, elenco e verbo únicos por cena — We Are Illuminati como estudo de
estrutura/ritmo, nunca de arte, regra anti-cópia §2/§66; sem pessoas/
instituições reais, `docs/SATIRE_GUIDELINES.md`):
- **Lote E — Pindorama**: 3 mestres pintados (p3_01, p3_02, p3_06) + 7 keyframes
  desenhados em código.
- **Lote F — Religião**: 3 mestres pintados (p4_04, p4_05, p4_10) + 7 keyframes
  desenhados em código.
- **Lote G — Singularidade**: 3 mestres pintados (p5_04, p5_07, p5_10 — este com
  prompting "fofo" após bloqueio de moderação) + 7 keyframes desenhados em
  código.
- **Lote H — Singularidade fecha**: os 6 mestres que faltavam (`p5_02`, `p5_03`,
  `p5_05`, `p5_06`, `p5_08`, `p5_09`) pintados no mesmo flat-toon, com recipes
  próprias. O apagão escurece só as janelinhas (sem retângulo duro); a varredura
  da TV não sai da tela; o robô não leva borrão no rosto.
- **Movimento**: as cenas pintadas ganharam recipes próprias em
  `tools/build_motion_frames.py` (rec_p3_01..rec_p5_10, verbo único cada:
  glow do ET+raio, radar+multa, feixe de busca, LED grid, rotor do pombo-dron,
  chip no prato, etc.); as 21 cenas de código usam os 4 keyframes direto no
  loop (`tools/scene_draw2.py`, helpers flat-toon compartilhados com
  `tools/scene_draw.py`).
- `tools/gen_animations.py` agora cobre 5 tabelas (50 cenas); `animations.json`
  = **50 cenas, 50 animadas em 2D**. Testes 50/50 verdes.

### Estilo "desenho animado 2D real" (direção de arte v3, em andamento)

A direção anterior (SVG geométrico) foi rejeitada como "muito amadora, feita com
formas geométricas". Nova direção: **animações 2D pintadas, estilo desenho animado**,
uma cena por missão — mesma ideia de "cena emoldurada" da referência (uma ação em
loop), agora com personagem de verdade.

Pipeline por missão:
1. `gerar quadros` — 4+ PNGs por cena (personagem original "O Grifter", cartoon 2D
   flat com contorno à tinta, cores vibrantes) compartilhando 1 quadro-mestre como
   referência de consistência. Quadros brutos em `src/assets/anim/<id>/frames/f*.png`
   (ignorados no Git; ficam no disco para regeneração).
2. `tools/wai_animate.py <id>` — anima o poster (fundo travado, 10 quadros × 100 ms,
   verbo único, loop sem pulo). Substitui o zoom de câmera das recipes antigas.
   `tools/build_animation_loop.py` continua válido para montar um loop a partir de
   PNGs crus, mas o caminho de produção das 50 cenas pintadas é o `wai_animate`.
3. `tools/gen_animations.py` — detecta `loop.webp` e marca a cena `animated:true`
   no `animations.json` (spec v3); o renderizador exibe poster em `off` e o loop em
   `idle`/`running`.

Métricas de sanidade (ambiente sem visão): consistência entre quadros adjacentes
(diferença em 64×64) < ~15 = mesmo cenário/personagem (mudou só a pose); usada como
alarme de "o modelo redesenhou a cena".

Status: `p1_01` (Comprar com cripto) entregue como **primeira prova de estilo**;
demais 39 missões aguardam aprovação desta direção de arte.

### Status do Lote 1 (entregue) — Deep Web completa

- Arte: `src/assets/anim/p1_01..p1_10/scene.svg` — cada missão vira um **dossiê
  conspiratório ilustrado** (sala secreta + personagem "O Grifter" em pose temática
  + objeto sob holofote + plaqueta com a piada + olho vigiando), paleta ART_BIBLE.
- **Rig de marionete (v2.1):** o personagem NÃO é mais uma caixa única. Ele expõe
  ossos articulados — `root` (tronco), `leg-l/leg-r` (pivô no quadril), `arm-l/arm-r`
  (pivô no ombro, objetos `gadget` segurados dentro do braço), `head` (pivô no pescoço),
  `fingers`, `headgear` — cada um com `transform-origin` em px do viewBox. O CSS roda
  cada osso num **ritmo próprio** (pernas ~0,62s, braços ~0,9–1,05s, cabeça ~1,3s),
  com `--phase` por card para vizinhos não dançarem em sincronia. Isso corrige a
  rejeição "parece uma imagem só balançando" — agora são várias partes se articulando
  como nas cenas emolduradas da referência.
- Objeto de cena (`spot-*`) separado do wrapper `translate` para o CSS não sobrescrever
  a posição; `transform-box` explícito (`view-box`/`fill-box`) garante pivôs corretos
  em qualquer navegador; `@media (prefers-reduced-motion)` preservado.
- Spec: `src/content/animations.json` **v2** — cenas por id com `accent` + `loops`
  (vocabulário: `marcha`, `bracos`, `cabeca`, `throb`, `sway`, `levitate`, `spin`,
  `drop`, `rise`, `rain`, `blink`, `flicker`).
- Gerador: `tools/gen_animations.py` + kit procedural `tools/art_kit.py`
  (arte 100% original, sem assets externos).
- Renderizador: estados `off/idle/running`; loops por classe; moldura de dossiê
  (scanlines + carimbo "CONFIDENCIAL").
- Testes: `tests/Animations.test.js` agora também fixa a rig (tronco/braços/pernas/
  cabeça como grupos separados com pivôs) contra regressão visual.

### Status do Lote 0 (entregue)

- Arte: `src/assets/anim/p1_01/scene.svg` (320×88, paleta ART_BIBLE, camadas `bg/actor/fx`).
- Spec: `src/content/animations.json` (`version:1`, `stage`, `scenes.p1_01.layers[].loop`).
- Gerador: `tools/gen_animations.py` (data-driven; mesmas entradas do `gen_campaign.py`).
- Renderizador: `app.js` `buildAnimStage()` + estados `off/idle/running` (CSS `app.css`).
- Carregamento: `content.js`/`content.node.js` incluem `animations.json`; `GameState.animationFor(id)`.
- Testes: `tests/Animations.test.js` (spec íntegro + arte presente/maintainable).
- Perf: uma cena = 1 SVG de ~5 KB; animações só rodam em `running`; cache de fetch; loops GPU (transform/opacity) — não afeta o scrolling/lista.
|---|---|---|
| **0 — Fundação/POC** | 1 cena completa ponta-a-ponta (p1_01) + paleta/reference sheet + o `animations.json` + renderer do protótipo | prova de pipeline: 1 ação animando de verdade |
| **1 — Deep Web** | p1_02..p1_10 (10 cenas) + refinamento da p1_01 | mapas rodando com 10 ações animadas |
| **2 — Democracia Relativa** | p2_01..p2_10 | +10 ações |
| **3 — Ratanabá** | p3_01..p3_10 | +10 ações |
| **4 — Religião** | p4_01..p4_10 | as 40 ações animadas |
| **5 — Personagens** | 40 bustos de Coordenadores (4 expressões) + 40 sósias por raridade | coleção completa |
| **6 — Telas & VFX** | backgrounds HQ por mapa (parallax) + transições de fase/prestígio + carimbos | polimento "quadro completo" |

**Ordem de prioridade** = ordem acima (core jogável primeiro; personagens por último —
antes do conteúdo volumoso, provar o loop da economia/ritmo — regra MVP).

---

## 6. O que eu consigo fazer vs. o que precisa de você/Unity

**Eu faço agora (no ambiente):**
- Gerar as **camadas de arte** (bg/actor/fx) por missão com geração de imagem;
- montar **spritesheets/recortes** (Pillow) e exportar PNG/SVG;
- escrever o **modelo de dados** (`animations.json` + `tools/gen_animations.py`);
- implementar o **renderizador do protótipo web** (camadas + loops em CSS/Canvas);
- baterias de teste de **perf/tamanho** e commit/push por lote.

**Preciso de você para:**
- **aprovar a direção de arte** do Lote 0 (é o "sinal verde" para os demais);
- **revisar visualmente** cada lote (eu não enxergo os frames neste ambiente — sou o
  executor, você é o diretor de arte);
- decidir **ferramenta de rig para Unity**: DOTween/Animator (grátis, já tem) ou
  **Spine** (pago — me avise antes de qualquer compra, per regra de autonomia).

**Não dá neste ambiente:** compilar/testar o projeto Unity real (não há editor Unity
aqui) → entrego specs + espelhos C# + assets prontos para arrastar; e áudio não-fala
(SFX/música) → mantenho o sintetizador WebAudio atual até termos um dia de áudio.

---

## 7. Critérios de "pronto" por ação (Definition of Done de animação)

- [ ] Cena lê-se em ~2–3s (silhueta + cor + 1 movimento forte).
- [ ] 2 estados funcionando: `idle` sutil + `running` em loop (~0,8–1,6s).
- [ ] Paleta/linha/sombra conformes à Art Bible (sem "cara de IA").
- [ ] Sem texto ilegível dentro do quadro em 400×720 (legibilidade §113).
- [ ] Ativo ≤ ~120 KB por cena (meta celular), animação GPU-friendly (transform/opacity, sem blur pesado).
- [ ] Sons/VFX ligados ao loop (carimbo, moedas, confete) sem excesso.
- [ ] Original IP: **nenhum** traço/asset/inimigo copiado da referência (§2/§66).

---
*Próximo passo: revisar o **Lote 0** (cena p1_01 no preview) e, aprovado, seguir o **Lote 1** (Deep Web).*

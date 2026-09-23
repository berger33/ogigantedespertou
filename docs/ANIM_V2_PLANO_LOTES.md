# PLANO DE ANIMAÇÃO V3 — LOOPS NARRATIVOS (50 missões, lotes de 10)

> **Status:** vigente a partir de 2026-09-23. Substitui o plano v2
> (mesmo arquivo, lotes de 3+7) e o estado v1 (50/50 loops de movimento
> sutil). Este é o plano de **produção** pedido pelo dono: história de
> verdade em cada missão, validação de **10 em 10**.
>
> **Branch de origem inspecionada:** `arena/01a0cb93-ogigantedespertou`
> (commit `1d32928`, a mais recente do jogo em 2026-09-23). O trabalho
> desta sessão continua nessa base, na branch da sessão atual.
>
> **Lote 1 (em execução logo após este plano):** mapa **Religião**
> `p4_01`…`p4_10`. Não é o primeiro mapa da campanha — é o primeiro lote
> de validação porque os três exemplos de complexidade do dono estão
> todos aqui (`p4_10` arrebatamento, `p4_08` água da torneira, `p4_06`
> xarope). Os lotes 2–5 seguem a ordem da campanha.

---

## 1. Objetivo

Transformar as 50 cenas de missão de "quadro quase estático com respiro" em
**loops narrativos de verdade**: cada missão conta uma micro-história em
2–4 s (ação com começo, meio e volta), no padrão de complexidade definido
pelo dono do jogo (exemplos de referência — todos do mapa **Religião**):

| Missão | O que o loop deve contar |
|---|---|
| **p4_10 · Projetar o arrebatamento holográfico** | frame 1: luz azul **desligada** e botão **não apertado**; o personagem se move e **aperta o botão**; a luz **acende**; as pessoas são **arrebatadas** (subem e desaparecem); a luz **apaga** e o loop recomeça do estado inicial. |
| **p4_08 · Bendizer a água da torneira** | as **esteiras com garrafas andam**; a **torneira enche** as garrafas vazias; as garrafas cheias **passam para o outro lado** e recebem **adesivo santo** (aureola); **todo** mecanismo com água quente, vapor, água em movimento ou goteiras anima; o **homem com a prancheta** alterna o olhar entre as garrafas e a prancheta, **anotando**. |
| **p4_06 · Mandar a imagem chorar xarope** | a **imagem (quadro) chora xarope**: gotas formam, **caem e enchem o copo/vidro**; o **personagem enche/retira o copo**; as **chamas de velas/lamparinas tremulam** como fogo de verdade. |

**Regra de ouro:** imagem-base pintada atual **se mantém** (o dono aprovou o
visual); só se adapta a imagem quando a mecânica exigir (ex.: garrafas
estáticas viram esteira vazia para as garrafas desenhadas poderem andar).
Adaptações são **locais** (recorte do que obstrui a mecânica), nunca redesenho.

## 2. O que existe hoje (v1) e o que muda

- **v1:** 50/50 missões com `loop.webp` de 12 quadros. Movimento global
  (zoom/pan) + FX genéricos compostos sobre o mestre pintado. Lês como "fundo
  vivo", não como "ação acontecendo".
- **v2 (este plano):** por missão, uma **peça de keyframes** (12–16 quadros)
  com:
  - **ato de setup** (estado inicial — ex.: luz apagada, botão sem mão);
  - **ato de ação** (a mecânica acontecendo, vários elementos simultâneos);
  - **ato de resolução** (resultado lido — pessoas sumidas, garrafa rotulada,
    copo cheio);
  - **ataque de reset** (volta suave ao estado inicial, sem "pulo" no loop).
- **O que continua idêntico (compatibilidade):**
  - layout de arquivos `src/assets/anim/<id>/{frames,loop.webp,poster.webp,contact.png,scene.svg}`;
  - `src/content/animations.json` (spec v4: `animated`, `src`, `poster`, `accent`, `loops`) —
    ganha apenas campos aditivos `v2: true`, `frames: N`, `story: "..."`;
  - `src/app.js` (o `<img>` do webp animado roda nativamente — nada muda);
  - testes de `tests/Animations.test.js` (≥12 quadros `ff_*.webp`, RIFF/WebP,
    spec completa, rig do `scene.svg`) — **permanecem verdes**.

## 3. Técnica (pipeline v3 — pintura travada)

A pintura aprovada (`poster.webp`, 640×360) é a placa. **Não se regenera a
cena inteira** — uma geração nova muda rosto, câmera e paleta, e o dono
aprovou estas imagens. O loop é montado por recorte:

| Etapa | Ferramenta | Saída |
|---|---|---|
| 1. Placa | `poster.webp` intacto | fundo de todos os quadros |
| 2. Recortes | `tools/narrative/kit.py` — máscaras, sprites, inpaint local do que precisa sumir (feixe, xarope, garrafa) | sprites em memória |
| 3. Cena | `tools/narrative/lote1_religiao.py` — setup / ação / resolução / reset. FX no traço do ART_BIBLE (gota, aureola, vapor, chama) só onde o pixel pintado não basta | 12 ou 16 quadros |
| 4. Build | `tools/narrative/build_loop.py` — **não sobrescreve** `poster.webp` | `ff_*.webp`, `loop.webp`, `contact.png` |
| 5. Spec | `animations.json` ganha campos aditivos | `v2: true`, `frames`, `story` |

**Gramática de loop:**
- 12 quadros = cenas de 1 mecânica forte (padrão); 16 quadros = narrativas
  multi-elemento (as 3 de referência + p1_09, p1_10, p4_03, p4_05, p5_03, p5_10).
- Durações por quadro variam (90–260 ms) para dar **ritmo**: setup lento,
  ação rápida, hold curto, reset suave.
- **Loop fechado:** f(N-1) deve continuar em f(0) sem salto (posição/alpha dos
  elementos retornam ao valor inicial).
- **Consistência:** o fundo pintado é o MESMO em todos os quadros; só mudam
  camadas compostas +FX. Auditoria: `contact.png` + diff adjacente (o
  `build_animation_loop.py` imprime o score de consistência).

## 4. Especificação por missão (o que anima)

> Formato: `setup → ação → resolução`. Elementos = camadas que mudam.

### Mapa 4 — Religião (Lote 1)

| ID | Missão | Loop (setup → ação → resolução) | Qtd. |
|---|---|---|---|
| p4_01 | Gravar a mensagem invertida no vinil | toca-discos parado → disco gira, agulha vibra, letras do display **invertem** revelando a mensagem → volta ao normal | 12 |
| p4_02 | Exibir o desenho da indução espiritual | TV acesa neutra → símbolo (olho/triângulo) **aparece traço a traço**, olhos do público arregalam → TV volta ao neutro | 12 |
| p4_03 | Fábrica do boneco possuído | boneco na esteira → **olhos acendem**, braço espasmo, carimbo "MAL EM ESCALA" → próximo boneco entra (esteira anda) | 16 |
| p4_04 | Traçar a capital em sigilo geométrico | mapa em branco → **linhas se desenham** formando a silhueta, bússola gira, alfinete cai → traço brilha e apaga | 12 |
| p4_05 | Encenar o milagre ao vivo | palco escuro → luz certa **acende** no santo, lágrima gigante cai, multidão em êxtase (confete de luz) → luz apaga | 16 |
| **p4_06** | **Mandar a imagem chorar xarope** | gota **forma no olho** → **cai e enche o copo**, comerciante **retira o copo cheio** e repor vazio → novas gotas; chamas de velas/lamparinas **tremulam** em todos os quadros | **16** |
| p4_07 | Gravar o 13º mandamento só no áudio | fita rodando neutra → **onda sonar** cresce, "13" pisca no display, agulha trema → onda volta ao mínimo | 12 |
| **p4_08** | **Bendizer a água da torneira** | esteira anda com garrafas vazias → **torneira enche** a garrafa sob o bico, **adesivo de aureola** carimbado no lado cheio, **vapor/goteiras/mecanismos** animados, inspetor **olha garrafa → prancheta e anota** | **16** |
| p4_09 | Empurrar o apocalipse (de novo) | letreiro com data → **data rasura e vira "EM BREVE"**, calendário com X's, multidão com guarda-chuva → letreiro pisca | 12 |
| **p4_10** | **Projetar o arrebatamento holográfico** | **luz azul desligada, botão sem mão** → personagem **aperta o botão**, luz **acende** → pessoas **subem e desaparecem** → luz **apaga**, volta ao início | **16** |

### Mapa 3 — Pindorama (Lote 4)

| ID | Missão | Loop (setup → ação → resolução) | Qtd. |
|---|---|---|---|
| p3_01 | Escavar a cidade debaixo do cerrado | broca parada → **vibra e fura**, terra voa, medidor de profundidade desce → broca recua | 12 |
| p3_02 | Aprovar a permuta do E.T. de Varginha | alien à mesa com contrato → **carimbo cai**, antenas balançam, OVNIs na janela → alien levanta "obrigado" | 12 |
| p3_03 | Faturar com o radar torto | radar parado → **gira**, carro passa, **multa sai impressa** voando, contador sobe → radar gira de novo | 12 |
| p3_04 | Caçar o chupa-cabra por encomenda | lanternas acesas → **silhueta persegue** (salto), mira vermelha acerta, carimbo "PEDIDO ATENDIDO" → lanternas tremem | 12 |
| p3_05 | Lançar o carro elétrico brasileiro | carro parado → **bateria carrega** (barra sobe), faísca no plugue, pneu fumaça → barra completa "até a esquina" | 12 |
| p3_06 | Ligar São Tomé a Machu Picchu | mapa com 2 pontos → **linha de túnel se desenha**, brocas nas duas pontas, % sobe → linha pulsada | 12 |
| p3_07 | Ler o Brasil pelo GPS de todo mundo | mapa com pontos parados → **pontos se movem**, linhas ligam ao painel, carimbo "DADO" → pontos seguem | 12 |
| p3_08 | Gravar chip em todo o papel timbre | impressora parada → **folhas saem**, cada folha **carimbada com chip**, folhas voam para a caixa → caixa enche | 12 |
| p3_09 | Segurar a transferência instantânea | ampulheta com moedas → **areia/moedas caem**, relógio gira, "PENDENTE" pisca → ampulheta vira | 12 |
| p3_10 | Magnetizar as cédulas da nação | cédula neutra → **ímã atrai** a cédula que **volta sozinha**, medidor sobe, carimbo "MERCADO" → cédula repousa | 12 |

### Mapa 2 — Democracia Relativa (Lote 3)

| ID | Missão | Loop (setup → ação → resolução) | Qtd. |
|---|---|---|---|
| p2_01 | Comprar o voto do tio do grupo | santinho parado → **troca de mão** (voto ⇄ cédula), tio sorri e dá 👍, voto voa para a urna → recomeça | 12 |
| p2_02 | Encomendar a pesquisa que prova o que a gente quer | gráfico neutro → **barras sobem até 99%**, pesquisador gira o mostrador, carimbo "CONFIRMADO" → gráfico volta | 12 |
| p2_03 | Fundar o partido do meio-termo | político no chão → **sobe no muro** (literal), **muro balança**, bandeiras tremulam → político se equilibra | 12 |
| p2_04 | Espalhar a emenda "totalmente pública" | Diário Oficial aberto → **caneta assina**, letras de tinta aparecem, **carimbo** bate → página vira | 12 |
| p2_05 | Sessão plenária com robôs no contra-turno | robôs parados → **digitam**, luzes de votação acendem em sequência, máquina de café pinga → luzes apagam | 12 |
| p2_06 | Cabo eleitoral com megafone na praça | cidadão parado → **grita no megafone**, **ondas sonoras** saem, povo levanta mãos → ondas se dissipam | 12 |
| p2_07 | Comício com promessas em formato de dupla | palco com a dupla → **cantam** (bocas/mãos alternadas), **confete**, notas musicais → confete cai | 12 |
| p2_08 | Escrever a "Constituição do Zap" | celular parado → **mensagens viram artigos** (retângulos de texto descem), "encaminhando…" pisca → tela limpa | 12 |
| p2_09 | Eleger um sósia por procuração | procuração em branco → **sósia de óculos entra na urna**, papel flutua, **carimbo ELEITO** → urna fecha | 12 |
| p2_10 | Proclamar a Democracia Relativa™ | martelo no ar → **bate no bloco**, "**50%**" gigante aparece, **confete** → martelo volta | 12 |

### Mapa 1 — Deep Web (Lote 2)

| ID | Missão | Loop (setup → ação → resolução) | Qtd. |
|---|---|---|---|
| p1_01 | Comprar as maiores empresas com cripto | notebook com tela neutra → **clicam "COMPRAR"**, **gráfico sobe**, cifrões voam → gráfico segura o topo | 12 |
| p1_02 | Plantar fake news na mídia | manchete antiga → **texto se reescreve** (letras substituídas), "BREAKING" pisca → manchete nova | 12 |
| p1_03 | Fazer amizade com os reptilianos | lagarto de terno parado → **bebe café** (vapor da caneca), **olho escamoso pisca** → assente | 12 |
| p1_04 | Colocar um informante no governo | pasta fechada → **passa de mão em mão**, abre, **carimbo CONFIDENCIAL** bate → fecha | 12 |
| p1_05 | Fomentar teorias da conspiração | quadro de cortiça → **linha vermelha se desenha** ligando fotos, **alfinete cai**, post-its vibram → linha completa pisca | 12 |
| p1_06 | Lavar o cérebro de artistas pop | diva de fones parada → **espiral gira no olho**, **notas musicais em espiral** → espiral desacelera | 12 |
| p1_07 | Começar guerras por lucro | mapa tático → **alfinete de mira cai** (sem violência), **cifrões de fumaça** sobem → mira segura | 12 |
| p1_08 | Controlar mentes através do Wi-Fi | roteador parado → **ondas saem em leques**, **cérebros 🧠 viajam** nas ondas → ondas seguem | 12 |
| p1_09 | Manipular governantes fantoches | marionete parada → **cordas se puxam**, marionete acena/abaixa o braço → cordas relaxam | 16 |
| p1_10 | Gerenciar sistemas de controle do clima | painel parado → **botão SOL/CHUVA alterna**, **nuvem + sol + raio cômico** trocam → painel pisca | 16 |

### Mapa 5 — Singularidade (Lote 6)

| ID | Missão | Loop (setup → ação → resolução) | Qtd. |
|---|---|---|---|
| p5_01 | Acender o feixe sobre o cerrado | antena fria → **feixe acende** sobre o cerrado, **chuva num lado, sol no outro** → feixe pulsado | 12 |
| p5_02 | Ajustar a fórmula da água nacional | proveta neutra → **gota cai na proveta**, medidor "dose" sobe, **carimbo SEGREDO** → proveta balança | 12 |
| p5_03 | Ensaio geral: apagar o país | cidade com luzes → **22h01: tudo apaga**, nota "foi um acidente" → **22h02: luzes voltam** | 16 |
| p5_04 | Deixar a máquina decidir | máquina parada → **braço aperta o botão**, **carimbo DECIDIDO**, mão humana confirma → máquina descansa | 12 |
| p5_05 | Mapear a conversa pelo aparelho | celular parado → **balões de fala saem**, anúncio de pneu aparece 2 min depois, "MAPADO" → balões viram dados | 12 |
| p5_06 | Instalar o presidente 2.0 | presidente 1.0 parado → **troca de cabeça** para robô (mesmo sorriso), **bateria carrega** → 2.0 acena | 12 |
| p5_07 | Trocar o pombo pela frota | pombo voando → **frota de 9 drones em linha** substitui, luzes piscam em sequência → pombo volta (confusão) | 12 |
| p5_08 | Adensar a malha de torres | torre parada → **ondas se expandem** em anéis, **zumbido** (linhas de vibração), "EXPLICA TUDO" pisca → anéis seguem | 12 |
| p5_09 | Codificar o prato com QR | prato com comida → **QR aparece no prato**, **escaneiam**, **carimbo "COMA"** → prato gira | 12 |
| p5_10 | Implantar o chip em todos | pessoas neutras → **ponto acende na nuca** de uma em uma, **sincronia** (linhas ligando) → "SINCRONIZADO" | 16 |

## 5. Lotes (ordem de execução) — 10 missões por lote

> Pedido do dono (2026-09-23): **de 10 em 10**, com validação entre lotes.
> Cada lote = commit + push + relatório (o que foi feito / próximo passo).
> Não avançar o lote seguinte antes da validação.

| Lote | Mapa | Missões | Por que nesta ordem |
|---|---|---|---|
| **L1** | **Religião** | p4_01 … p4_10 | Contém os 3 exemplos de complexidade do dono. É o padrão-ouro a validar. |
| **L2** | Deep Web | p1_01 … p1_10 | Primeiro mapa da campanha. |
| **L3** | Democracia Relativa | p2_01 … p2_10 | Segundo mapa. |
| **L4** | Pindorama | p3_01 … p3_10 | Terceiro mapa. |
| **L5** | Singularidade | p5_01 … p5_10 | Fecha as 50 + auditoria final de loop/testes. |

**Quadros:** 12 no mínimo (teste `Animations.test.js`). As narrativas
multi-elemento usam 16: p4_03, p4_05, p4_06, p4_08, p4_10 e, nos lotes
futuros, p1_09, p1_10, p5_03, p5_10. Durações por quadro variam
(90–280 ms): setup lento, ação rápida, hold curto, reset suave.
Total do projeto: 50 missões.

### O que o Lote 1 precisa mostrar (checklist de validação)

| ID | Beat que tem que ser legível num ciclo |
|---|---|
| p4_10 | frame 1: luz azul **desligada** e botão **não apertado** → mão aperta → luz **acende** → pessoas **sobem e somem** → luz **apaga** → loop |
| p4_08 | esteiras **andam** → torneira **enche** garrafa vazia → garrafa cheia segue e ganha **adesivo de aureola** → vapor, bolhas, goteira e engrenagens animam → inspetor **olha garrafa, olha prancheta e anota** |
| p4_06 | quadro **chora xarope** (gotas caem e enchem o copo) → personagem **enche/retira o copo** → velas e lamparinas **tremulam** o tempo todo |
| p4_01 | disco e rolos **giram**, agulha vibra, mensagem do rótulo **inverte**, velas tremulam |
| p4_02 | espiral da TV **gira**, diabinho flutua, olhos do menino e do gato **giram** |
| p4_03 | esteira **anda** com as bonecas, boneca possuída flutua com olhos acesos, engrenagens giram, pincel pinga |
| p4_04 | sigilo **se desenha** sobre a capital, olho alado circula, linhas pulsam e apagam |
| p4_05 | holofote **apaga e acende**, confete cai, megafone grita, milagre (brilho/lágrima) aparece no arco |
| p4_07 | rolos giram, onda sonora flui, **“13”** pisca no tablete |
| p4_09 | homem **afasta e bate** o X vermelho no calendário, papéis caem, sirene e lâmpada piscam |

**Poster aprovado não é redesenhado.** `poster.webp` continua a pintura
heroica. O `loop.webp` conta a história por cima da mesma pintura
(recortes + FX no traço do ART_BIBLE). Adaptação só local, quando a
mecânica exige (ex.: céu sem o feixe, para a luz poder apagar).

**Card no jogo:** o palco passa a 16:9 (as pinturas são 640×360). O
recorte antigo 320×88 cortava botão, torneira e copo — a história não
cabia. A revisão também fica em `src/review/lote1.html`.

## 6. Critérios de aceite (todo lote)

1. **Quadros:** ≥12 `ff_*.webp` por missão (16 nas narrativas); `loop.webp`
   RIFF válido; `poster.webp` permanece a pintura aprovada (não é o frame 0);
   `contact.png` gerada para revisão.
2. **Loop fechado:** f(N-1) → f(0) sem salto perceptível.
3. **Legibilidade:** história legível no tamanho do card (~300 px de largura)
   em 1 ciclo (≤ 4 s).
4. **Consistência de cena:** mesmo fundo em todos os quadros (score de diff
   adjacente baixo; sem "redesenho" de cenário).
5. **Spec:** `animations.json` com `v2: true`, `frames`, `story` (e
   `animated`/`src`/`poster`/`accent`/`loops` intactos).
6. **Testes:** `npm test` 100% verde (especialmente `tests/Animations.test.js`).
7. **`scene.svg` preservado** (rig articulada — exigido pelos testes).

## 7. Como rodar o pipeline (dev)

```bash
python3 tools/narrative/render_lote1.py      # 10 missões de Religião
npm test                                     # QA
# revisão: src/review/lote1.html
```

Re-render é puro (sem geração de imagem). PNGs crus de quadro ficam fora
do git (`.gitignore`); entram `ff_*.webp`, `loop.webp` e `contact.png`.

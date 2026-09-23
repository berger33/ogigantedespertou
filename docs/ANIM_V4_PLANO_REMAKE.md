# PLANO DE REMAKE DAS ANIMAÇÕES — v4 "animação de verdade"

> **Status:** plano APROVADO pelo dono (set/2026). **Passo 0 concluído:** piloto `p4_10`
> promovido a oficial com 9/9 checagens verdes (commit da promoção em
> `arena/01a0cc5f-ogigantedespertou`); padrão de camadas/fps/lints **congelado**.
> Lote 1 em andamento — boards em `docs/ANIM_V4_LOTE1_BOARDS.md`.
> **Sucessor de:** `ANIM_V2_PLANO_LOTES.md` (loops narrativos v2 — **reprovados**: "viraram gelatinas") e
> `ANIMATION_PLAN.md` (v1, movimento sutil).
> **Escopo:** **reconstruir do zero as 50 animações de missão**, 5 s por clip, padrão profissional,
> estilo e tom de comunicação no padrão *We Are Illuminati*.
>
> **Regra anti-cópia (inalterada):** replicamos **estrutura, ritmo, técnica e acabamento** da referência.
> Nunca arte, traço, personagem, texto ou ícone da Tapps. O jogo é IP própria.

---

## 1. Diagnóstico — por que a v2 virou "gelatina"

A v2 animava **esticando a própria pintura** (warp com máscara suave sobre a placa). Isso tem um nome
na prática: *rubber-hose involuntário*. A causa não é estética, é de arquitetura:

| # | Sintoma visto | Causa técnica na v2 | Correção obrigatória na v4 |
|---|---|---|---|
| 1 | Contorno "derretendo", traço que estica | warp desloca **pixels da pintura** com mistura bilinear → a linha do desenho se deforma | **Proibido deformar a pintura.** Só transformações **afins** (translação/rotação/escala) em **recortes com alpha** |
| 2 | Tudo se move junto, "feito de gelatina" | **placa única**; não havia separação real de camadas | **backplate + N camadas independentes**, cada uma com pivô próprio e ordem Z |
| 3 | Movimento sem peso, elástico | easing senoidal contínuo, sem pausa | curvas com **antecipação → ação → overshoot → settle**, com **holds** de leitura |
| 4 | Clip curto demais (1,5 s, 12 quadros) | não cabe um beat profissional em 1,5 s | **5,00 s** com segmentos de fps distintos (§2) |
| 5 | FX infantis (bolinhas, riscos, arcos padrão) | primitivas genéricas desenhadas no código | **vocabulário FX WAI** com sprites de IA + partículas com dissipação e follow-through |
| 6 | Bagunça de leitura | 4–6 eventos simultâneos de mesma força | **1 evento primário**; secundários a 30–50% de amplitude |
| 7 | Borda quadrada/"fantasma" aparecendo | recortes retangulares com fundo do cenário junto | **silhueta real (alpha)** + limpeza de franja + validação de borda (lint L2) |

**Conclusão:** o problema não é "faltar frames", é **arquitetura de camadas**. A v4 não refina a v2 —
**substitui o método**.

---

## 2. Especificação técnica v4 (o padrão que todo clip deve cumprir)

| Item | Regra |
|---|---|
| Duração | **5,00 s ± 0,05** por missão |
| Segmento A | **3,0–4,0 s a 10 fps** (setup + ação principal) |
| Segmento B | **1,0–2,0 s a 12–18 fps** (rajada/impacto/finalização) |
| Total de quadros | **52 a 66** por missão (o "roteiro de imagens" do dono) |
| Loop | **fechado**: `f(N-1) → f(0)` sem salto (lint L3) |
| Câmera | **travada** — zero zoom/pan/tremor de tela (padrão da referência) |
| Quadro (frame) | 640×360 (mantém a arte aprovada pixel-perfect no card 320×88 @DPR2) |
| Encoding | **WebP animado** com **duração por quadro** (fps variável de verdade) + `loop=0` |
| Peso | `loop.webp` **≤ 900 KB** (alvo 600–750 KB) — holds deduplicados (§4, L8) |
| Poster | `poster.webp` **permanece a arte aprovada** (frame 0 do clip). Só muda com pedido explícito no E0 e aprovação do dono |
| Extra | `frames/` guarda apenas **8 quadros-chave** (QA/imprensa), não o clip inteiro (economia de repositório) |

### Perfis de tempo (escolha por missão no E0)

| Perfil | Uso | A (10 fps) | B (12–18 fps) | Total |
|---|---|---|---|---|
| **P1 · ação pesada** | impacto/colisão no fim (ex.: carimbo, chicote de luz) | 3,0 s → 30 f | 2,0 s @15 → 30 f | **60 f** |
| **P2 · clímax no meio** | pico narrativo + resolução (ex.: arrebatamento) | 3,4 s → 34 f | 1,6 s @16 → 26 f | **60 f** |
| **P3 · ritual/soleno** | cerimônia, líquidos, chamas (ex.: xarope, vinil) | 4,0 s → 40 f | 1,0 s @14 → 14 f | **54 f** |

> Os fps variáveis são o que dá o "cheiro" de animação profissional: o olho lê **lentidão ritmada** e
> **rajada curta** — exatamente o que a v2 não tinha.

---

## 3. Pipeline por missão — 6 etapas com 2 portões de aprovação

```
E0 BOARD ──▶ [PORTÃO 1: dono aprova roteiro + lista de assets]
             │
E1 ASSETS IA ──▶ E2 RIG (separação de camadas) ──▶ E3 ANIMAÇÃO + FX (procedural) ──▶ E4 QA (lints)
             │
             └──▶ E5 FOLHA DE REVISÃO ──▶ [PORTÃO 2: dono aprova o clip 5 s] ──▶ commit
```

**E0 · Board (roteiro dos 5 s).** Beat sheet com: 4 tempos (setup / gatilho / ação / reset), mapa de
fps, quem é o evento primário, quais secundários, **lista fechada de imagens IA × procedurais**, curvas
de movimento e poses-chave. Entrega: `board.png` + `meta.json` (rascunho) + 1 linha de descrição.

**E1 · Assets IA (≥20% das imagens finais).** Geradas/editas por IA: backplate limpo, **poses-chave**
dos personagens, props com detalhe pintado, letreiros/marcações. Cada asset entra com **proveniência**
declarada (`ai` ou `proc`) no `meta.json`.

**E2 · Rig (separação de camadas).** Cada elemento que se move vira **camada com alpha** (silhueta
real, franja limpa), com **pivô anatômico** (ombro, cotovelo, dobradiça, boca da garrafa) e limite de
deformação. Nada de máscara elíptica "elástica" sobre a pintura.

**E3 · Animação + FX (procedural).** Curvas por camada (`tools/anim/motion.py`), holds, smear de 1
quadro, follow-through; FX procedurais (líquidos, vapor, faíscas, luz varrendo, confete, poeira) com
dissipação e defasagem; composição quadro a quadro (`build_clip.py`).

**E4 · QA automático.** `qa_lint.py` roda os **8 lints** (§4) e emite relatório por missão. Sem lint
verde, não vai para revisão.

**E5 · Folha de revisão + entrega.** Página com: preview do clip 5 s (com controle de fps/quadro),
board, contact sheet, **contagem IA × procedural**, lints e diff vs. arte aprovada. Aprovado → commit.

---

## 4. Regras anti-gelatina (hard rules) + lints automáticos

### Regras de produção (R1–R10)

| # | Regra |
|---|---|
| **R1** | **A placa não se deforma.** Fora das máscaras de camada, o quadro é idêntico ao poster, sempre |
| **R2** | Só **afim** em recorte (translação/rotação/escala). Proibido warp não-uniforme sobre pintura |
| **R3** | *Squash & stretch* só em partes macias (barriga, gota, balão) e **≤ 8%** |
| **R4** | **Pivô anatômico** obrigatório: nada gira em volta do próprio meio por conveniência |
| **R5** | Todo deslocamento é **em arco**, nunca em linha reta mecânica |
| **R6** | **Antecipação** antes de toda ação principal; **overshoot** e **settle** depois |
| **R7** | **Holds** de 2–3 quadros nas poses-chave (leitura). É o que separa animação de "movimento" |
| **R8** | FX com **follow-through** e dissipação; nunca colidem com o impacto no mesmo quadro (defasagem 1–2 f) |
| **R9** | **1 evento primário** por vez; secundários a 30–50% de amplitude |
| **R10** | **Loop fechado**: o último quadro já prepara o primeiro (pose/energia compatíveis) |

### Lints (`tools/anim/qa_lint.py`)

| # | Verificação | Limite |
|---|---|---|
| **L1** | `plate_stability` — pixels alterados fora das máscaras de camada | **≤ 0,5 %** (mataria a v2) |
| **L2** | `edge_integrity` — nitidez da borda dos recortes; sem *smear* de alpha | ≥ limiar de gradiente + 0 px de halo |
| **L3** | `loop_closure` — `\|f(0) − f(N−1)\|` | ≤ 1,5× mediana dos deltas adjacentes |
| **L4** | `timing` — total e segmentos | 5,00 ± 0,05 s; A ∈ [3,0–4,0 s]@10fps; B ∈ [1,0–2,0 s]@12–18fps |
| **L5** | `scale_consistency` — deformação não-uniforme por camada | ≤ 8 % |
| **L6** | `palette_outline` — paleta/contorno vs. poster (ΔE médio) | ≤ 4 ΔE; 0 troca de família de cor |
| **L7** | `occlusion` — ordem Z sem inversão (interseção de máscaras) | 0 inversões não intencionais |
| **L8** | `perf` — peso do `loop.webp`, contagem de quadros, fps real | ≤ 900 KB; 52–66 f; fps conforme spec |

---

## 5. IA × procedural — regra de decisão (≥ 20% IA garantido)

| Sempre **IA** (imagem gerada/editada) | Sempre **procedural** (código) |
|---|---|
| Backplate limpo do cenário (fundo sem os elementos que se movem) | **Quadros in-between** (interpolação por curvas entre poses) |
| **Poses-chave expressivas** de personagem (mão, cabeça, boca, corpo) | Transforms afins das camadas (rig), holds, smear |
| Props com detalhe pintado (garrafa, pote, calendário, letreiro) | **Líquidos, vapor, fumaça, faíscas, confete, poeira, luz varrendo** |
| Lettering / números / marcas de cena ("13", "EM BREVE", adesivo de auréola) | Glow, rim-light, sombra projetada, "sticker pop", flash |
| Folhas FX de partículas (atlas de sparkles/spray) quando o desenho pede traço pintado | Texto de HUD, marcações temporárias, encode/decodificação |

**Orçamento por missão (perfil P2, 60 quadros):**

| Categoria | Qtde | % dos quadros |
|---|---|---|
| Assets **IA** (backplate 1 + poses 6–10 + props 3–5 + lettering 1–2 + atlas FX 1–2) | **14–18** | **23–30 %** ✅ |
| Quadros **procedurais** compostos | ~42–46 | ~70–77 % |
| `frames/` de QA (recorte de 8 quadros-chave) | 8 | — |

> Ou seja: a IA entrega **os desenhos que exigem traço pintado**; o código entrega **movimento e efeitos**.
> Um não substitui o outro — foi exatamente essa mistura que faltou na v2.

---

## 6. Direção de animação (vocabulário WAI)

**Tokens de timing** (mapeados no nosso fps):

| Token | Duração | Quadros | Onde usar |
|---|---|---|---|
| `anticipate` | 300 ms | 3 @10fps | antes de qualquer ação principal |
| `act` | 200–400 ms | 2–4 @10fps | ação em si |
| `impact` | 125–250 ms | 2–4 @16fps | colisão, carimbo, estouro |
| `follow` | 250–500 ms | 4–6 @14fps | follow-through (cabelo, roupa, líquido) |
| `settle` | 600–1000 ms | 6–10 @10fps | assentamento antes do reset |
| `hold` | 300 ms | 3 @10fps (1 quadro encodado) | leitura da pose-chave |
| `blink` | 167 ms | 2 @12fps | piscada, tremulação de chama |

**Vocabulário de movimento:** `pop`, `squash`, `sweep`, `stamp`, `rise`, `pour`, `shake`, `spin`,
`twinkle`, `cascade`. Cada beat do board escolhe tokens desse vocabulário — nada de "sobe e desce genérico".

**FX WAI (o que a referência usa):** sparkles ✦ dourados, **pessoas douradas subindo** na coleta,
**spray/granulado**, poeira de impacto, **luz varrendo** a cena, **sticker pop** (adesivo), confete de
luz, revoada de notas/papéis. Todos com atlas + partículas e **defasagem** do evento primário.

**Regra de câmera:** travada. A "câmera" da referência é o próprio enquadramento; o movimento acontece
dentro da cena (medido no estudo `docs/VISUAL_IMPLEMENTATION_PLAN.md` §1.3).

---

## 7. Tom de comunicação (títulos e falas) no padrão *We Are Illuminati*

**Voz:** corporativa-burocrática aplicada ao absurdo, dita com naturalidade de manual interno.
O jogador é o **gestor do plano**; a piada nasce do contraste entre linguagem técnica e objetivo ridículo.

**7 regras de tom:**
1. **Título = verbo no infinitivo + objeto concreto**, ≤ 42 caracteres. Nunca explica a piada.
2. **Fala (flavor) = 1 reviravolta**, ≤ 90 caracteres. Começa plausível, termina errado.
3. **Jargão corporativo** no lugar do jargão conspiratório óbvio: *entregável, permuta, contra-turno, sincronizar, permuta, homologar*.
4. **Números absurdos e específicos** ("2 km", "22h01", "40 unidades/dia", "7 mil km") — a referência usa precisão para vender o ridículo.
5. **Auto-incriminação debochada**: a empresa admite tudo em letra miúda. Nunca nega.
6. **Zero política real, zero pessoa real, zero denominação religiosa.** Sátira de **vigaristas**, não da fé (`docs/SATIRE_GUIDELINES.md`).
7. **Silêncio cômico**: quando a piada é boa, o texto para. Nada de explicação extra.

**Antes → depois (amostra do lote de Religião):**

| id | Título atual | Título v4 | Fala v4 |
|---|---|---|---|
| p4_01 | Gravar a mensagem invertida no vinil | **Inverter a mensagem no vinil** | Na letra, amor. No replay, obediência. |
| p4_05 | Encenar o milagre ao vivo | **Encenar o milagre ao vivo** | Luz certa, ângulo certo, lágrima certa. O resto é fé. |
| p4_06 | Mandar a imagem chorar xarope | **Fazer o quadro chorar xarope** | Choro a cada 5 minutos. Uso diário. |
| p4_09 | Empurrar o apocalipse (de novo) | **Adiar o apocalipse (de novo)** | Nova data confirmada: em breve. A outra também. |
| p4_10 | Projetar o arrebatamento holográfico | **Projetar o arrebatamento em LED** | Céu de verdade, nuvem de LED. Fé com nota fiscal. |

### 7.1 Reescrita completa das 50 missões (proposta para aprovação)

> Aplicada **por lote**, junto com o remake da animação daquela missão (o texto só entra quando o clip entra).
> Nenhuma linha cita pessoa, partido ou denominação real.

| id | Título v4 | Fala v4 (tom WAI) |
|---|---|---|
| **p1_01** | Comprar o mercado com moeda inventada | Lance na bolsa com o arquivo 'carteira_final_v2_REAL.docx'. |
| **p1_02** | Plantar a manchete antes do fato | O fato chega atrasado. A manchete, pontual. |
| **p1_03** | Firmar acordo com os reptilianos | Café com um escamoso que fala sete línguas. Nenhuma humana. |
| **p1_04** | Instalar um informante no governo | Cargo na placa: 'Conselheiro'. Função: escutar. |
| **p1_05** | Regar teorias da conspiração | Cada boato é semente. O grupo é estufa. |
| **p1_06** | Assinar o hit com mensagem embutida | Se dançarem, está pago. |
| **p1_07** | Financiar conflitos com margem | Paz é quando ninguém mais lucra com ela. |
| **p1_08** | Sincronizar mentes pelo roteador | Sinal forte. Convicção mais forte. |
| **p1_09** | Trocar o roteiro dos fantoches | Não trocamos o elenco. Só as falas. |
| **p1_10** | Administrar o clima por bloco | Chuva no bloco A. Sol no B. Reclamação: zero. |
| **p2_01** | Comprar o voto do tio do grupo | Ele votava no meme. Agora vota na gente. |
| **p2_02** | Encomendar a pesquisa com a resposta pronta | A pergunta foi feita depois. Por gentileza. |
| **p2_03** | Fundar o partido do meio-termo | Nem esquerda, nem direita: reels. |
| **p2_04** | Emendar o sigilo em 'totalmente público' | Transparência em PDF com senha. |
| **p2_05** | Ligar os robôs no contra-turno | O adversário é bot. A derrota é viral. |
| **p2_06** | Pagar o cabo eleitoral do megafone | Verdade ao alcance do ouvido alheio. |
| **p2_07** | Prometer em dupla no palanque | Entrada franca. Convicção inclusa. |
| **p2_08** | Redigir a Constituição do Zap | Artigo 1º: encaminhem. |
| **p2_09** | Empossar o sósia por procuração | O original assina. O sósia comparece. |
| **p2_10** | Proclamar a Democracia Relativa™ | Metade vota. A outra metade concorda. |
| **p3_01** | Escavar a capital sob o cerrado | A broca parou a 2 km. O GPS, ali do lado. |
| **p3_02** | Aprovar a permuta do visitante | Ele só quer voltar pra casa. A casa é aqui. |
| **p3_03** | Faturar com o radar torto | A multa é o produto. O motorista, o mercado. |
| **p3_04** | Caçar o chupa-cabra sob encomenda | Suga o cabra. Literal. Fonte: boato confiável. |
| **p3_05** | Lançar o elétrico do cerrado | Alcance: até a esquina. Com estilo. |
| **p3_06** | Ligar São Tomé ao Machu Picchu | 7 mil km. Prazo: 3 mil anos. Status: em obras. |
| **p3_07** | Ler o país pelo GPS do povo | Cada passo é um dado. Cada dado, uma prova. |
| **p3_08** | Gravar chip em todo papel timbrado | O carimbo registra. A folha lembra. |
| **p3_09** | Reter a transferência instantânea | O dinheiro chega na hora em que a gente deixa. |
| **p3_10** | Magnetizar a cédula nacional | Sai da máquina e já volta. (É o mercado.) |
| **p4_01** | Inverter a mensagem no vinil | Na letra, amor. No replay, obediência. |
| **p4_02** | Exibir o desenho que induz | A cada 4 episódios, um símbolo. O público conta. |
| **p4_03** | Fabricar o boneco possuído | 40 unidades por dia. O mal, em escala. |
| **p4_04** | Traçar a capital em sigilo geométrico | De cima: um avião. De dentro: fé. |
| **p4_05** | Encenar o milagre ao vivo | Luz certa, ângulo certo, lágrima certa. |
| **p4_06** | Fazer o quadro chorar xarope | Choro a cada 5 minutos. Uso diário. |
| **p4_07** | Gravar o 13º mandamento na estática | 11 minutos de chiado. O mandamento no meio. |
| **p4_08** | Bendizer a água da torneira | Fonte: 2014, torneira da capela. Rótulo: milagrosa. |
| **p4_09** | Adiar o apocalipse (de novo) | Nova data confirmada: em breve. A outra também. |
| **p4_10** | Projetar o arrebatamento em LED | Céu de verdade, nuvem de LED. Fé com nota fiscal. |
| **p5_01** | Acender o feixe sobre o cerrado | Chuva no bloco A. Seco no B. O feixe decide. |
| **p5_02** | Ajustar a fórmula da água encanada | Cada gota, uma dose. De quê? Segredo. |
| **p5_03** | Ensaiar o apagão geral | 22h: luz. 22h01: nada. 22h02: 'foi um acidente.' |
| **p5_04** | Deixar a máquina decidir | Ela não erra. Ela decide. A gente só confirma. |
| **p5_05** | Mapear a conversa pelo aparelho | O anúncio do pneu chegou 2 minutos depois do café. |
| **p5_06** | Instalar o governante 2.0 | Mesmo sorriso, bateria melhor. Discurso do manual. |
| **p5_07** | Trocar o pombo pela frota | Nove em linha? Coincidência. (Sete não voa em fila.) |
| **p5_08** | Adensar a malha de torres | A torre nova explica: zumbido, formigamento, intuição. |
| **p5_09** | Codificar o prato com QR | Escaneie e coma. Depois pense: e o código? |
| **p5_10** | Implantar o chip em todos | Um ponto na nuca e o mundo em sincronia. |

---

## 8. Roteiro de 5 s por missão (resumo para o board; detalhamento no E0 de cada uma)

`A` = 10 fps (setup + ação) · `B` = 12–18 fps (rajada/final) · `IA` = imagens geradas/editadas por IA
(≥ 20 % do total de quadros).

| id | A — setup + ação (10 fps) | B — rajada (12–18 fps) | Perfil | IA |
|---|---|---|---|---|
| p1_01 | Cofre/orbes girando; mão hesita sobre o terminal | **stamp** no terminal → cascata dourada cai e o cofre fecha | P2 | 16 |
| p1_02 | Rotativas paradas; editor cheira a manchete | **cascata** de jornais voa da prensa; flash de câmera | P1 | 15 |
| p1_03 | Mesa de conferência; o escamoso ajusta a gravata | aperto de mão → brilho de escama percorre o braço | P3 | 14 |
| p1_04 | Corredor do gabinete; o informante cumprimenta | **pop** do crachá → microfone escondido pisca | P3 | 14 |
| p1_05 | Post-its; a linha vermelha ainda solta | **puxada** da linha conecta os pinos (fio estica e vibra) | P2 | 16 |
| p1_06 | Estúdio; o artista dança um passo | beat → sparkles sincronizados com a batida | P1 | 15 |
| p1_07 | Sala de mapas; dedo desliza sobre a fronteira | **stamp** de carimbo vermelho; poeira de impacto | P1 | 16 |
| p1_08 | Torre de Wi-Fi acesa; técnico ajusta a antena | anel de sinal percorre a cidade; cidadãos param | P2 | 15 |
| p1_09 | Palco vazio; o fantoche está sem fio | fios descem e o prendem; braço levanta de repente | P2 | 16 |
| p1_10 | Painel meteorológico; botão SOL/CHUVA alterna | nuvem acima do bloco A despeja chuva; bloco B, estiagem | P1 | 16 |
| p2_01 | Porta de casa; o tio abre o santinho | cedulha troca de mão → voto voa para a urna | P2 | 15 |
| p2_02 | Escritório; analista digita a pergunta | gráfico sobe a 99 % → carimbo CONFIRMADO | P2 | 15 |
| p2_03 | Cartório; terno bege assina o registro | faixa do partido cai e cobre a bandeira antiga | P3 | 14 |
| p2_04 | Plenário; pilha enorme de páginas | 1000 páginas folheiam; 'totalmente público' carimbado | P1 | 16 |
| p2_05 | Bastidores; braço robótico no teclado | 500 perfis curtindo em sincronia; contador dispara | P2 | 16 |
| p2_06 | Praça; megafone aponta para o povo | onda sonora visível; praça em transe | P2 | 15 |
| p2_07 | Comício em dupla; os dois ajeitam o microfone | confete; promessas em dupla ditas em uníssono | P1 | 16 |
| p2_08 | Mesa de redação; caneta pousa no papel | artigos 1–99 saem digitados de uma vez; carimbo | P2 | 15 |
| p2_09 | Cartório 2; dois bonecos idênticos na cadeira | a mão do sósia assina no lugar; pose trava em hold | P3 | 14 |
| p2_10 | Púlpito; martelo preparado | martelo desce; '50 %' explode em confete | P1 | 16 |
| p3_01 | Cerrado; broca enterrada, poeira no ar | broca gira em **rajada** e some no túnel; terra voa | P1 | 16 |
| p3_02 | Escritório de imigração; bolha de flores | formulário carimbado; o visitante flutua leve | P3 | 14 |
| p3_03 | Beira de estrada; radar torto gira | multa sai impressa e voa para o motorista | P2 | 15 |
| p3_04 | Pasto à noite; lanternas varrem a mata | arbusto treme; par de olhos acende; bicho some | P2 | 16 |
| p3_05 | Fábrica; linha do elétrico no berço | carro desce, liga e some atrás da esquina | P1 | 15 |
| p3_06 | Canteiro de obras; esteiras vazias | máquinas a postos ligam todas juntas; barro sobe | P1 | 16 |
| p3_07 | Central; malha de pontos acesos | mapa acende ponto a ponto; painel fecha | P2 | 15 |
| p3_08 | Cartório; papéis timbrados empilhados | carimbo múltiplo: chip gravado linha por linha | P2 | 15 |
| p3_09 | Banco; tela de transferência travada | ponteiro trava em 99 %; 'na fila' pisca | P3 | 14 |
| p3_10 | Casa da moeda; cédulas na esteira | campo magnético atrai a nota de volta à máquina | P2 | 15 |
| p4_01 | Estúdio; agulha desce, disco começa a girar | **mensagem invertida** aparece "LIVE" espelhado; notas invertidas | P3 | 14 |
| p4_02 | Sala; TV liga na espiral | anéis giram, olhos do menino e do gato rodam juntos | P2 | 16 |
| p4_03 | Fábrica; bonecas na esteira | chave de corda gira; olhos do possuído acendem; esteira parte | P2 | 16 |
| p4_04 | Mapa limpo visto de cima | **sweep** radial: o sigilo se desenha do centro para fora | P2 | 16 |
| p4_05 | Palco escuro; luz preparada fora de cena | **pop** do holofote → lágrima gigante cai → plateia em êxtase | P1 | 17 |
| p4_06 | Comerciante ajeita o copo; quadro seco | gotas formam, caem e **enchem o copo**; colher serve | P3 | 15 |
| p4_07 | Mosteiro; dois rolos prontos | rolos disparam; onda de áudio corre e o "13" pisca | P2 | 15 |
| p4_08 | Esteira anda; garrafa vazia entra sob o bico | enche → selo de auréola (**stamp**) → segue para o outro lado | P1 | 18 |
| p4_09 | Ele empurra o bloco do X (de novo) | carimbo marca o dia; papéis voam; calendário zera | P1 | 16 |
| p4_10 | Luz apagada, botão livre, pessoas na rua | aperta → feixe acende → sobem aureoladas e somem → luz apaga | P2 | 17 |
| p5_01 | Antena no cerrado; céu dividido | feixe dispara; chuva cai só no bloco A | P1 | 16 |
| p5_02 | Estação de tratamento; válvulas fechadas | válvula abre em **rajada**; gota brilha e cai no cano | P2 | 15 |
| p5_03 | Cidade acesa às 22h00 | 22h01 apaga tudo; 22h02 volta com 'foi um acidente' | P1 | 17 |
| p5_04 | Sala fria; terminal pede confirmação | a máquina decide: tela conclui sozinha; luz muda de cor | P3 | 15 |
| p5_05 | Cozinha; café servido | na tela, o anúncio do pneu aparece 2 min depois | P2 | 15 |
| p5_06 | Laboratório; o 2.0 na plataforma | liga; sorriso idêntico; discurso sai do teleprompter | P2 | 16 |
| p5_07 | Pombal; pombos prontos | a frota sobe em fila de nove; o pombo fica no chão | P1 | 16 |
| p5_08 | Cidade; torre nova ligada | malha de torres acende em cascata; zumbido visível | P1 | 16 |
| p5_09 | Restaurante; prato servido com QR | QR pisca; cliente escaneia; código some do prato | P3 | 15 |
| p5_10 | Filas de gente; chip na mão | **stamp** na nuca de cada um; todos sincronizam ao mesmo tempo | P1 | 18 |

---

## 9. Divisão em passos e lotes

| Passo | Nome | Escopo | Portão de saída |
|---|---|---|---|
| **Passo 0** | **Fundação + missão-piloto** | `tools/anim/{motion,rig,fx,build_clip,qa_lint,review}.py`, schema `animations.json` v4, `meta.json`, página de revisão v4 e **a missão piloto `p4_10`** (a referência do dono) feita ponta a ponta | Piloto aprovado = padrão congelado |
| **Lote 1** | **Religião (restante)** — p4_01…p4_09 | 9 missões, 1 a 1 | Aprovação por missão |
| **Lote 2** | **Deep Web** — p1_01…p1_10 | 10 missões | Aprovação por missão |
| **Lote 3** | **Democracia Relativa** — p2_01…p2_10 | 10 missões | Aprovação por missão |
| **Lote 4** | **Pindorama** — p3_01…p3_10 | 10 missões | Aprovação por missão |
| **Lote 5** | **Singularidade** — p5_01…p5_10 | 10 missões | Aprovação por missão + auditoria final das 50 |

**Regra de fluxo (vale para todos os lotes):** uma missão por vez. Para cada missão o dono recebe
**dois** pontos de decisão: (1) board + lista de assets; (2) clip 5 s + relatório de QA. Reprovação em
qualquer portão → ajuste e nova rodada; aprovado → commit + atualização da spec e da página de revisão.

**Por que Religião primeiro (no remake):** é o mapa onde o dono definiu o padrão de complexidade
(arrebatamento, água da torneira, xarope) e onde plate_off e assets de referência já existem.

---

## 10. Critérios de aceite (o que "pronto" significa)

- [ ] 5,00 s ± 0,05, com segmentos A/B nos fps especificados (L4);
- [ ] **8 lints verdes** (L1–L8) no `qa_lint.py`;
- [ ] nenhuma deformação da pintura aprovada (L1 e L2);
- [ ] loop fechado e imperceptível (L3);
- [ ] 1 evento primário com leitura clara em 320 px de largura (teste de miniatura);
- [ ] assets com proveniência declarada (`ai`/`proc`) e **≥ 20 % IA**;
- [ ] `loop.webp` ≤ 900 KB; `frames/` com 8 quadros-chave;
- [ ] texto de título/fala no tom WAI aprovado (§7);
- [ ] spec atualizada (`v4: true`, `duration_ms: 5000`, `frames`, `fps_segments`, `assets`, `story`);
- [ ] página de revisão publicada e commitado.

---

## 11. O que muda no repositório

```
src/assets/anim/<id>/
  poster.webp          (arte aprovada — frame 0; só muda com aprovação explícita)
  plate.png            (IA: backplate limpo)
  layers/*.png         (IA/editado: recortes com alpha e pivô declarado)
  poses/*.png          (IA: poses-chave dos personagens)
  fx/*.png             (IA/proc: atlas de partículas, spray, sparkles)
  meta.json            (board: beats, fps, curvas, proveniência, lints)
  frames/ff_XX.webp    (8 quadros-chave para QA)
  board.png            (beat sheet visual com timing)
  contact.png          (folha de contato do clip)
  loop.webp            (ENTREGA: 5 s, fps variável, loop fechado)
tools/anim/
  motion.py            (curvas, tokens de timing, holds, smear)
  rig.py               (camadas, pivôs, afins, squash limitado)
  fx.py                (líquidos, vapor, faíscas, luz, confete, poeira)
  build_clip.py        (compositor + encoder WebP com duração por quadro)
  qa_lint.py           (L1–L8 + relatório por missão)
  review.py            (página de revisão v4 e diff vs. poster)
docs/ANIM_V4_PLANO_REMAKE.md   (este documento)
```

**Repositório:** `src/assets/anim` hoje ocupa **56 MB** (com `frames/` duplicando tudo). A v4 fica
**no mesmo orçamento**: clips maiores compensados por `frames/` enxuto (8 quadros-chave) e holds
deduplicados.

---

## 12. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| IA gerar poses inconsistentes entre si (traço/paleta) | todo asset IA nasce de **edição da própria pintura aprovada** (image-to-image) + lint L6 (ΔE ≤ 4) |
| Clip de 5 s ficar pesado demais | holds deduplicados, q≈74, lint L8 (≤ 900 KB) |
| "Gelatina" voltar por descuido | L1 (placa) e L2 (borda) reprovam automaticamente; rig só afim (R2) |
| Texto novo descaracterizar o tom | §7 aplicado por lote, com portão do dono junto do clip |
| Prazo por missão | 6 etapas com escopo fechado; nenhuma missão avança sem lint verde |

---

## 13. Próximo passo imediato

1. **Aprovação deste plano** (este documento).
2. **Passo 0** — construir as ferramentas `tools/anim/*`, o schema v4 e a **missão piloto `p4_10`**
   (arrebatamento holográfico) ponta a ponta, com board, assets IA, rig, FX, QA e folha de revisão.
3. **Portão 1 do piloto:** você aprova board + assets → eu executo a animação.
4. **Portão 2 do piloto:** você assiste ao clip de 5 s → aprovado, o padrão fica congelado e o
   **Lote 1 (p4_01…p4_09)** começa, uma missão por vez.

> Nada do que já está aprovado é jogado fora: `poster.webp` de cada missão continua sendo a arte oficial.
> O que é substituído é **o clip** (`loop.webp`) e o método que o produziu.

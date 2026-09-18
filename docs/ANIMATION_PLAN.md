# PLANO DE ANIMAÇÃO — O GIGANTE DESPERTOU

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
| **2 — Democracia Relativa** | p2_01..p2_10 | +10 ações | ⏳ |
| **3 — Ratanabá** | p3_01..p3_10 | +10 ações | ⏳ |
| **4 — Religião** | p4_01..p4_10 | as 40 ações animadas | ⏳ |
| **5 — Personagens** | 40 bustos de Coordenadores (4 expressões) + 40 sósias por raridade | coleção completa | ⏳ |
| **6 — Telas & VFX** | backgrounds HQ por mapa (parallax) + transições de fase/prestígio + carimbos | polimento "quadro completo" | ⏳ |

**Ordem de prioridade** = ordem acima (core jogável primeiro; personagens por último —
antes do conteúdo volumoso, provar o loop da economia/ritmo — regra MVP).

### Status do Lote 1 (entregue) — Deep Web completa

- Arte: `src/assets/anim/p1_01..p1_10/scene.svg` — cada missão vira um **dossiê
  conspiratório ilustrado** (sala secreta + personagem "O Grifter" em pose temática
  + objeto sob holofote + plaqueta com a piada + olho vigiando), paleta ART_BIBLE.
- Spec: `src/content/animations.json` **v2** — cenas por id com `accent` + `loops`.
- Gerador: `tools/gen_animations.py` + kit procedural `tools/art_kit.py`
  (arte 100% original, sem assets externos).
- Renderizador: estados `off/idle/running`; loops por classe (`char`, `spot-*`,
  `prop-*`, `eye`, `lamp`); moldura de dossiê (scanlines + carimbo "CONFIDENCIAL").

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

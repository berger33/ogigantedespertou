# PLANO DE IMPLEMENTAÇÃO VISUAL — Fidelidade ao *We Are Illuminati*

> **Documento-mestre da produção visual.** Sucessa e consolida:
> `INTERFACE_STUDY.md` (estrutura), `ANIMATION_PLAN.md` (animação por missão),
> `ART_BIBLE.md` (direção de arte), `VISUAL_PARITY.md` (checklist de UI).
>
> **Base empírica:** análise quadro-a-quadro do gameplay real
> (`We are Illuminati- Conspiracy Simulator Clicker.mp4`, 40,3 s, 400×720 @ 30 fps —
> 1202 frames analisados, 34 frames-chave inspecionados visualmente) +
> wiki do jogo (fandom) + pesquisa de pipeline 2D com IA (set/2026).
>
> **Regra anti-cópia (inalterada, §2/§66):** replicamos *estrutura, posição, ritmo,
> técnica e qualidade*. Nunca arte, traços, personagens, textos ou ícones da Tapps.
> Nosso jogo é IP própria — "fiel" = fiel ao *padrão de acabamento*, não à imagem deles.

---

# PARTE 1 — O ESTUDO: como o We Are Illuminati é feito

## 1.1 Anatomia medida da tela principal (400×720 retrato)

Zonas verticais (medidas nos frames):

| Zona | Altura | Conteúdo |
|---|---|---|
| Barra de status/HUD | 0–8,5% | ícone de menu (esq., grade 3×3 amarela) · ícone de moeda (pessoas douradas) + contador grande · `⋮` + cartão de buy-mode `x1/x10/MAX` (dir.) |
| Faixa de fase | 8,5–15,5% | pote de lackeys (esq., pote com líquido verde) · **TÍTULO DA FASE** em fonte toon ("DEEP WEB") + seta `▶` de troca de mapa · nota adesiva de missões com badge `+N` (dir.) |
| Banner do QG | 15,5–36% | **cena pintada animada do esconderijo** (personagem à mesa, luminária-pirâmide acesa, pôsteres de olho) — ocupa a largura toda |
| Lista de produtores | 36–93% | cards grandes (~34% de altura cada; ~2,7 visíveis), fundo verde-petróleo com *marca-d'água* de olhos/pirâmides |
| Barra de abas | 93–100% | **4 abas-pasta** bege com ícones-olho: rosto (círculo interno), torre (base), mão/seta (upgrades), sacola (loja) |

Floaters fixos na borda **direita** (coluna de "figurinhas" com outline creme):

| Floater | Função | Comportamento |
|---|---|---|
| 📋 prancheta com laço | missões/objetivos | badge quando há recompensa |
| 📱 celular branco (olho) | wiretaps aprovar/negar | **treme** periodicamente (ring) |
| 📦 pirâmide-na-caixa | oferta/special | timer laranja embaixo (`2d 08:07`) |
| 🎁 presente (spray dourado) | bônus gratuito | timer verde embaixo (`09:10:31`) |

Floaters fixos na borda **esquerda**: pote de lackeys (topo) + **cronômetro dourado** (boost ×2) na altura da lista.

### Cartão de produtor — anatomia exata (esta é a peça central do jogo)

```
┌───────────────────────────────────────────────────────────┐
│ ┌─label escuro (2 linhas, caps)───────────┐  ┌─★★★★★──┐  │  ← pill de nome (sup. esq.)
│ │ Plant fake news in the media.           │  │ 5 slots │  │  ← placa metálica (sup. dir.)
│ └──────────────────────────────────────────┘  └────┬────┘  │     + contador (ex.: 140/150)
│ ┌─────────────────────────────────────────────────┐│
│ │                                                 ││  ← CENA PINTADA ANIMADA (~55% do card)
│ │        ilustração flat-toon da missão           ││     crossfade 2–4 quadros + sprites
│ │                                                 ││
│ └─────────────────────────────────────────────────┘│
│ [⏱ 00:06 ████████░░ → 1.0 Qa]  ← overlay de ciclo (barra ciano; some com coordenador)
├───────────────────────────────────────────────────────────┤
│ [tanque]  「MAX」 💰 182.0 B/s (placa amarela)   [ 5.83 Q ]│  ← linha de controle
└───────────────────────────────────────────────────────────┘
   tanque de sósia (esq.)                        botão-preço
   vazio = bateria cinza                         grosso, dourado,
   cheio = rosto do clone                        chanfrado (dir.)
```

Estado **travado**: cartão vira placa cinza lisa, estrelas como silhuetas escuras,
texto "Unlock" + botão-preço. Sem arte até a compra.

## 1.2 Inventário de telas (o que existe na referência)

| # | Tela | Como apresenta | Animações-chave |
|---|---|---|---|
| T1 | Sede/Produtores | tela principal (acima) | cena por produtor em loop, overlay de ciclo, coleta, estrelas |
| T2 | Upgrades | lista de upgrades (aba mão/seta) | flash na compra, estrelas douradas grandes chovendo |
| T3 | Shop | aba sacola | brilho em item premium |
| T4 | Managers | aba torre | busto respirando; "contratado" com carimbo |
| T5 | Inner Circle | aba rosto | medidor de lavagem; transição monumental no reset |
| T6 | Cloning lab | via pote/floater | tanque com líquido; clone colecionável pop |
| T7 | Wiretaps | **modal branco** sobre dim (frame analisado) | pop spring, partículas "+1" verde/vermelha, botão "Done" madeira |
| T8 | Settings | modal/sheet | slide-up |
| T9 | Bônus de anúncio | modal "Bonus reward!!" | burst + timer |
| T10 | Offline | modal "Welcome back!" | moedas rain, botão ×2 |
| T11 | Troca de fase | seta `▶` na faixa | transição cinematográfica curta |
| T12 | Prestige/brainwash | tela cheia | **pico de movimento do vídeo (22,8 s)**: pirâmide racha a Terra, shake+flash+partículas |
| T13 | Rate-us popup | modal | aparece na compra do 5º produtor |

Modal padrão (medido no frame dos Wiretaps): **card branco de cantos arredondados**,
título preto bold centrado, linhas de conteúdo, **botões ✓ verde / ✗ vermelho
quadrados chanfrados (pseudo-3D)**, botão inferior com textura de madeira,
fundinho escurecido ~60%, aba lateral com `?`.

## 1.3 Gramática de animação — o que medimos no vídeo

| Animação | Onde | Técnica da referência | Timing medido | Como reproduzimos |
|---|---|---|---|---|
| Cena de produtor | T1, por card | **pintura com crossfade entre 2–4 quadros** + sprites sobrepostos (mão, tanque, pessoa dourada, notas) | loop ~2–3 s; leitura em 2–3 s | IA gera 3–4 quadros da cena; montamos `loop.webp`; sprites CSS/canvas por cima |
| Overlay de ciclo | T1 | barra de progresso ciano + contador `00:06` | enche 1×/ciclo | DOM/CSS `scaleX` + texto |
| Coleta de lucro | T1 | **5–8 pessoas douradas voam** do card para cima-direita com fade | ~0,8 s | pool de sprites (atlas FX) |
| Upgrade de estrela | T1/T2 | **estrelas douradas GRANDES caem pela tela** + sparkles ✦ nos cards | chuva ~1 s | pool de sprites + twinkle CSS |
| Fone tocando | floater | shake rotacional ±8° em rajadas | rajada ~0,5 s, intervalo ~4 s | CSS `@keyframes ring` (já temos) |
| Modal | T7–T10 | **pop spring**: scale 0,85→1,04→1 + fade do dim | ~240 ms | `cubic-bezier(.2,1.4,.4,1)` |
| Scroll da lista | T1 | momentum com rajadas de 0,2–0,3 s; cards entram por baixo | — | scroll nativo + snap leve |
| Transição de fase | T11 | corte + flash, banner desliza | ~0,5 s | slide-x + flash |
| Prestige | T12 | **sequência monumental**: shake da tela, flash branco, estouro de partículas | ~2,5 s | 6–8 frames IA + shake/flash/pool |
| Personagem do QG | banner | bob sutil (respiração), luz da luminária pulsa | ~3 s | 2–4 quadros crossfade ou bob CSS |
| Sparkle ✦ | upgrades | twinkle 2-fps nos cantos brilhantes | contínuo | 2-frame sprite, opacity flicker |
| Badge/pop | floaters | scale bounce | ~200 ms | CSS |

**Descobertas estruturais (mapa de movimento do take 0–13,5 s):**
o movimento concentra-se na **faixa da cena do produtor** (região central do card);
HUD, banner e fundo ficam ~parados. Ou seja: **a referência gasta GPU só onde o olho
está** — 1 cena animada por card, resto estático. É exatamente o nosso modelo
`off/idle/running` (só anima o que produz), validado pelo vídeo.

## 1.4 Sistema visual da referência (amostrado nos frames)

| Elemento | Referência (medido) | Nosso alvo correspondente |
|---|---|---|
| Fundo da lista | verde-petróleo `#296D60` + marca-d'água de olhos | `--green-deep` + marca-d'água própria (olho do Gigante) |
| Faixa de fase | teal `#40A59E` | faixa teal derivada da nossa paleta |
| Placas/bege | creme com outline marrom-escuro + textura papel | `--paper` com outline `--ink` (já temos) |
| Placa de renda | amarelo-dourado `#CDB340` listrado | `--gold` listrado |
| Barra de ciclo | ciano brilhante | ciano/verde-neon `--green-neon` |
| Fonte display | **caps itálica gordinha tipo "Bangers/Komika"**, branco + outline preto grosso | Google Font *Bangers* (latin-ext p/ PT-BR) + `text-shadow` de outline |
| Fonte números | mesma família toon, contadores grandes | idem |
| Outline de cena | **traço preto grosso uniforme (~4 px), cores chapadas, sombra cel de 1 tom** | style lock (§3.1) — *amostra já gerada* |
| Cenas | fundo teal escuro + 1 acento quente (rosa/vermelho/luz) | idem, com acento por mapa |
| Botões compra | chanfro pseudo-3D, highlight superior, sombra dura | CSS 9-slice + sombra dura |

---

# PARTE 2 — GAP ANALYSIS: nosso jogo vs. referência

## 2.1 Diferenças de UI/UX (decisões de paridade)

| # | Referência | Hoje em O GIGANTE DESPERTOU | Decisão |
|---|---|---|---|
| G1 | Cena do produtor **grande** (~55% de um card de ~245 px) | stage fino (320×88) | **ADOTAR**: stage 16:10 (~320×200) — muda `animations.json.stage` + CSS |
| G2 | Card = cena + pill de nome + placa de estrelas + renda + preço + tanque | card atual tem informação, cena é magra | **ADOTAR** anatomia medida (§1.1) como layout do card v2 |
| G3 | Floaters na **borda direita** (fone, gift, prancheta, oferta) | nosso menu inferior tem 8 itens | **ADOTAR**: floaters laterais; menu inferior volta a 4 abas (Melhorias, Chefes, Sósias, Loja) |
| G4 | 4 abas-pasta na base | 8 itens no menu | **ADOTAR** 4 abas; Anúncios/Chumbo valem floaters; Arquivo/Gigante viram ícone/floater desbloqueável |
| G5 | Clique = **tocar no card** p/ coletar ciclo (+ sem botão gigante) | temos botão "Compartilhar no Zap" central | **HÍBRIDO** (nosso diferencial): manter o botão do Zap como *ação de clique manual* e adicionar coleta por toque no card |
| G6 | Modal branco spring-pop + ✓/✗ chanfrados | sheet própria estilo dossiê | **ADAPTAR**: nosso dossiê vira card claro com pop spring (mesma cinemática) |
| G7 | Barra de ciclo ciano com tempo→lucro | texto de timer | **ADOTAR** barra-overlay no card |
| G8 | Estrelas douradas chovendo ao upar estrela | bounce do card | **ADOTAR** chuva de estrelas (pool de sprites) |
| G9 | Pessoas douradas voando na coleta | floaters "+1 🧠" | **ADOTAR** sprites de figura dourada próprios (nosso "Convicto dourado") |
| G10 | Banner do QG pintado animado | banner estático/emoji | **PRODUZIR** 4 banners (1/mapa) com 2–4 quadros crossfade |
| G11 | Fonte toon com outline nos contadores | fonte de sistema | **ADOTAR** Bangers (display) + Rubik (UI/números) |
| G12 | Alloy de lots x1/x10/MAX como cartão do topo | seletor próprio | manter função, reskin "cartão" |
| G13 | Progressão de desbloqueio: menu revela Managers→Inner Circle | já temos desbloqueio progressivo | manter (✔ paridade já) |
| G14 | Tela travada = placa cinza "Unlock" | nosso card travado mostra dados | **ADOTAR** placa cinza minimalista |

## 2.2 Diferenças de ARTE (o salto de qualidade)

| # | Gap | Correção no pipeline |
|---|---|---|
| A1 | Nossa v3 atual (p1_01) é "graphic novel" hachurada/escura; referência é **flat-toon** (contorno grosso, cores chapadas, sombra cel) | Novo **style lock flat-toon** (§3.1) — amostras provadas: `docs/assets/style_lock_sample_scene.png` + `style_lock_sample_bust.png` |
| A2 | SVG procedural geométrico (p1_02..p1_10) foi rejeitado como amador | Aposentar do caminho principal: vira **fallback de placeholder**; caminho oficial = quadros IA pintados |
| A3 | Personagem-padrão inconsistente | **Character sheet âncora** ("O Grifter" e coadjuvantes) gerada primeiro; toda citação de personagem usa a âncora |
| A4 | Falta sprites FX (pessoas, estrelas, carimbos, sparkles) | Lote FX: 1 atlas (gerado + recortado) reutilizável |
| A5 | Sem banners de QG pintados | 4 banners 3-quadros (1 por mapa) |
| A6 | UI kit (botão chanfrado, placas, modal) em CSS simples | Kit 9-slice + tokens de motion (§4) |

---

# PARTE 3 — A FÁBRICA: pipeline de produção com IA + edição de frames/sprites

## 3.1 Style Lock (fase 0 — o "molde" aprovado antes da massa)

**Direção flat-toon (alvo de fidelidade à referência):**

1. Contorno **preto grosso uniforme** (~4–6% da altura do personagem), cantos arredondados.
2. **Cores chapadas** (sem gradiente difuso) + **sombra cel de 1 tom** (escurecimento ~25% da cor base, nunca cinza multiplicado).
3. Fundo de cena sempre **teal/verde escuro** + **1 acento quente** por mapa:
   Deep Web = rosa neon · Democracia Relativa = amarelo-palco · Ratanabá = dourado-caixa · Religião = roxo-vitral.
4. Silhueta legível em 48 px; máx. 3 "atores" por cena; 1 piada visual por cena.
5. Textura de papel só em UI, **nunca** dentro da cena.
6. PT-BR visual: plaquetas com piadas curtas entram como **camada separada** (nunca rasterizadas na pintura — o modelo erra texto).

**Ancoragem de estilo (processo):**

```
STYLE_GUIDE.txt (texto-âncora usado em TODOS os prompts):
"flat 2D cartoon mobile idle-game art, thick uniform black outlines,
chunky rounded shapes, bold flat colors, single-tone cel shadows,
dark teal grade with one warm accent, no gradients, no noise, no text"
```

- Sprite de referência de estilo (amostra aprovada) é anexado como **imagem-guia**
  em toda geração de cena (image-conditioning), não só texto.
- Character sheets: 1 folha por personagem recorrente (Grifter, Zé, coordenadores-chave)
  com frente + ¾ + paleta — gerada antes das cenas que o usam.

## 3.2 Pipeline por tipo de asset

### Tipo P1 — Cena de produtor (40 unidades; o coração do jogo)

**Saída por missão:** `loop.webp` (12 quadros ~10 fps, 640×400) + `poster.webp` + `contact.png` (folha de revisão) + entrada no `animations.json` v4.

**Passos:**

1. **Brief da cena** (tabela do `ANIMATION_PLAN.md` §3 — já temos as 40).
2. **Quadro-base (f1)**: text-to-image com `STYLE_GUIDE` + descrição da cena + câmera
   "wide interior shot, 16:10". Gate: legível em 320 px.
3. **Quadros de ação (f2–f4)**: **edição instruída sobre f1** ("same scene, the hand now
   presses the button; keep camera, palette and character identical") — edição de imagem
   preserva cenário/paleta; só a pose do ator muda. Métrica de guarda: diff médio 64×64
   entre vizinhos < 15 = consistência ok (já usada no Lote 0).
4. **(Opcional) suavização**: interpolação f1→f2→f3 (RIFE/ToonCrafter web) **somente**
   se o crossfade de 3 quadros parecer "slide show" no teste de tela. Cenas de objeto
   único grande aceitam bem 3–4 quadros diretos (é o que a referência faz).
5. **Montagem**: `tools/build_animation_loop.py v2` — recorte 16:10, 640 px,
   loop com crossfade de 120 ms, exporta `loop.webp` + `poster.webp` + `contact.png`.
6. **Spec** (`gen_animations.py v4`): `stage` 16:10, `fps`, `accent`, `overrides` de estado.
7. **QA**: contact sheet revisada + teste em 400×720 real + checklist DoD (§6).

Orçamento-alvo: ≤ 180 KB/cena, 4 gerações + 3 edições por missão (~40 missões ≈ 280 gerações).

### Tipo P2 — Banners de QG (4 unidades, 1 por mapa)

Pintura wide (16:6) do esconderijo do mapa, 3 quadros (luz pulsando/personagem respirando)
+ camada recortável do personagem para bob opcional. Mesma régua de estilo.

### Tipo P3 — Bustos de Coordenadores (40) e Sósias (40)

- **Template de busto**: enquadramento fechado cabeça-e-ombros, fundo teal circular
  (amostra: `style_lock_sample_bust.png`).
- 4 expressões cada (`idle/feliz/suspeito/surpreso`): gerar base `idle`
  → **edição instruída** para as outras 3 (preserva rosto/roupa).
- Sósias: base 1 corpo comum + variação de moldura por raridade (Comum selo papel /
  Incomum selo verde / Raro dourado + aura / Especial roxo + brilho animado CSS).
- Anim idle do busto: 2 quadros (olhos piscam) — crossfade 4 s.

### Tipo P4 — Atlas FX (1 spritesheet reutilizável)

Sprites gerados com fundo sólido → `rembg` (U²Net) → recorte → pack MaxRects:

| Grupo | Frames | Uso |
|---|---|---|
| `convicto_dourado` | 1 sprite × 3 poses | coleta (voo com rotação) |
| `moeda_mente` | 4 | spin da moeda-cérebro |
| `estrela` | 3 tamanhos | chuva de upgrade |
| `carimbo` | 4 | compra/upgrade (bate + mola) |
| `sparkle` | 2 | twinkle |
| `confete` | 6 | comemorações |
| `mais1` | 1 | "+1" flutuante |
| `olho_pisca` | 2 | marca-d'água do fundo |

Ferramenta nova: `tools/build_fx_atlas.py` (rembg + pack + JSON de frames
compatível com nosso pool JS e com Unity TextureImporter).

### Tipo P5 — UI kit (placas, botões, modal, abas)

- Base: **CSS** (tokens da ART_BIBLE) com cantos/sombras duras.
- Texturas: 3 9-slices gerados (placa papel, botão dourado chanfrado, modal creme),
  exportados 128 px, `border-image` no web / 9-slice sprite no Unity.
- Ícones: conjunto próprio (olho do Gigante, cérebro, lata de chumbo, Zap, sósia…)
  gerados como sticker com outline creme — 1 folha, recortada.

### Tipo P6 — Sequências monumentais (2 unidades)

- **Prestígio "O Gigante Desperta"**: 6–8 quadros (olho abrindo sobre a cidade) +
  shake + flash + partículas. É o nosso "pico 22,8 s" da referência.
- **Troca de fase**: 1 quadro "cartão de capítulo" por mapa + slide/flash.
- Gerados como pintura full-frame 720; o resto é VFX de engine (barato, reusa).

## 3.3 Ferramentas (o que já existe e o que vamos construir)

| Ferramenta | Estado | Função |
|---|---|---|
| `tools/build_animation_loop.py` | existe (v1: 16:9 strip) | **v2**: 16:10, crossfade, poster, contact |
| `tools/gen_animations.py` | existe | **v4**: spec 16:10 + fps + atlas FX |
| `tools/art_kit.py` | existe | manter p/ placeholders procedurais |
| `tools/build_fx_atlas.py` | **novo** | rembg + MaxRects + JSON (web+Unity) |
| `tools/style_metrics.py` | **novo** | guardas: consistência entre quadros, histograma de paleta, contraste, leitura em 320 px |
| interpolação externa (ToonCrafter/RIFE) | opcional | só se crossfade falhar no teste de tela |

## 3.4 Onde roda o quê

| Etapa | Onde | Por quê |
|---|---|---|
| Geração de quadros/bustos/ícones | **generate_image no Arena** (já provado nas amostras) | sem custo extra, iteração junto ao código |
| Edição instruída de quadros | generate_image (modo edição com imagem-base) | preserva cenário, muda pose |
| Edição programática de frames | Pillow/OpenCV no sandbox (já instalados) | recorte, resize, webp, atlas, métricas |
| rembg de sprites | sandbox (pip) ou web (transformers.js) | alpha limpo p/ atlas |
| Interpolação (se necessária) | HuggingFace Space ToonCrafter (externo, pontual) | suavizar 4→12 quadros |
| Preview e paridade | protótipo web (preview ao vivo) | validar ritmo/posição em 400×720 |
| Build final | Unity 6 (fora do sandbox) | importa `animations.json` + atlases |

---

# PARTE 4 — RENDERER & MOTION DESIGN (protótipo web → espelho Unity)

## 4.1 AnimStage v2 (player de cena por card)

- `stage`: 16:10 responsivo (`aspect-ratio: 16/10`), `overflow hidden`, cantos 10 px.
- Estados: `off` (poster estático) → `idle` (loop 6 fps sutil) → `running` (loop 10 fps +
  sprites FX) → `ready` (barra cheia + brilho pulsante) → **toque = `collect`** (burst
  de 5–8 sprites + retorna a `idle`).
- Player: `<img>` trocando `src` por frames webp pré-carregados (cache em `Map`);
  fallback: `loop.webp` animado único (já suporta) — manter ambos.
- Perf guard: só cards visíveis ganham `requestAnimationFrame`; IntersectionObserver;
  `prefers-reduced-motion` → poster estático.

## 4.2 Pool de partículas (FX sprites, 1 atlas)

`VFX.spawn(kind, x, y, n)` — kinds: `convictos` (coleta), `estrelas` (upgrade de estrela),
`carimbo` (compra), `sparkle`, `confete`, `mais1`.
Trajetórias: arco com easing `cubic-bezier(.3,.7,.4,1)`, rotação ±25°, fade-out final
30% — durações 0,7–1,0 s. Pool fixo (máx. 64 nós) — zero GC em jogo.

## 4.3 Cinemática de UI (tokens de motion — web e Unity espelham)

| Token | Valor | Uso |
|---|---|---|
| `--ease-pop` | `cubic-bezier(.2,1.4,.4,1)` | modal/botão pop |
| `--ease-out` | `cubic-bezier(.2,.7,.3,1)` | floaters, listas |
| `--dur-pop` | 240 ms | modais |
| `--dur-bounce` | 200 ms | badge/seleção de aba |
| `--dur-collect` | 800 ms | burst de coleta |
| `--dur-rain` | 1000 ms | chuva de estrelas |
| `--dur-cine` | 2500 ms | prestígio/troca de fase |
| shake | 6 × ±6 px x, 60 fps, 350 ms | prestígio |
| flash | overlay branco 0→80%→0, 400 ms | prestígio/fase |

## 4.4 Lista e scroll

Scroll nativo com momentum; `scroll-snap` fraco nos cards (alinha card ao parar);
banner do QG com **parallax leve** (traduz -10% ao scroll) — medido na referência
(banner some mais devagar que os cards).

## 4.5 Espelho Unity

`animations.json` v4 é a fonte única. Unity: `SpriteRenderer` + Animator por estado
(clips gerados dos mesmos frames) ou DOTween para transform-loops; partículas via
ParticleSystem com o mesmo atlas FX (mesmos tempos/easings da tabela).

---

# PARTE 5 — LOTES DE EXECUÇÃO

Cada lote fecha com: assets commitados + spec atualizado + preview funcionando +
contact sheets revisadas **por você** + testes verdes.

| Lote | Escopo | Saída | Status |
|---|---|---|---|
| **A — Style lock + card v2** | style guide, fontes, tokens, anatomia do card medida, floaters laterais, modal pop, 1 cena flat-toon (p1_01 refeita) ponta-a-ponta | card idêntico em *estrutura* à referência com arte nossa | ⏳ **próximo** |
| **B — Atlas FX + partículas + coleta/estrelas** | 1 atlas FX, pool de partículas, overlay de ciclo, bursts | ciclo completo de "juice" da T1 | ⏳ |
| **C — Deep Web flat-toon** | p1_01..p1_10 (10 cenas 4-quadros) | primeiro mapa 100% animado | ✅ **entregue** (hybrido, set/2026) |
| **D — Democracia Relativa** | p2_01..p2_10 + banner QG 2 | +10 cenas | ✅ **entregue** (hybrido, set/2026) |
| **E — Pindorama** (renomeado de Ratanabá) | p3_01..p3_10 + banner QG 3 | +10 cenas | ✅ **entregue** (set/2026) |
| **F — Religião** | p4_01..p4_10 + banner QG 4 | 40 cenas completas | ✅ **entregue** (set/2026) |
| **F2 — Singularidade** (5º mapa novo) | p5_01..p5_10 | 50 cenas completas | ✅ **entregue** (set/2026) |
| **G — Personagens** | 40 bustos ×4 expressões + 40 sósias + molduras de raridade | coleção completa | ⏳ |
| **H — Monumentais & telas** | prestígio (8 quadros), 4 cartões de fase, modais T7–T10 no padrão, UI kit 9-slice | quadro completo de polimento | ⏳ |

**Dependências:** A → B → C → (D/E/F paralelizável) → G → H.

> **Nota set/2026:** C, D, E, F e F2 fecharam em regime híbrido e o **Lote H**
> pintou as 6 cenas que ainda eram keyframes de código (`p5_02`, `p5_03`,
> `p5_05`, `p5_06`, `p5_08`, `p5_09`). **50/50 cenas pintadas e animadas em 2D**,
> testes 50/50 verdes — ver `ANIMATION_PLAN.md`.
Estimativa de gerações: A ~12 · B ~20 · C–F ~70/lote · G ~120 · H ~30.

## Definition of Done (por cena e por tela)

- [ ] Lê a piada em 2–3 s em 400×720 (silhueta + acento + 1 movimento forte).
- [ ] 3+ quadros consistentes (guarda de diff < 15) ou rig declarado; loop sem "pulo".
- [ ] Paleta flat-toon + acento do mapa; sem texto rasterizado; outline grosso uniforme.
- [ ] ≤ 180 KB por cena; só anima em `running`/visível; `prefers-reduced-motion` respeitado.
- [ ] Estados `off/idle/running/ready/collect` ligados ao jogo; coleta dispara burst.
- [ ] Token de motion correto (pop/bounce/collect/rain) + SFX associado.
- [ ] Rastro legal limpo: nada copiado da referência (estrutura ok, arte nunca).

---

# PARTE 6 — LIMITE DE FIDELIDADE & LEGAL

1. **O que copiamos:** anatomia das telas, posições, ritmos, durações, técnicas
   (crossfade de quadros pintados + sprites + motion tokens), padrões de modal e de
   feedback (chuva de estrelas, burst de coleta, fone tremendo).
2. **O que é 100% nosso:** personagens, cenários, piadas, ícones, paleta derivada da
   ART_BIBLE, nomes, textos, lore, código, SFX.
3. Frames do vídeo de referência: usados **só para estudo interno** — não commitados,
   não viram asset, não são retocados/reexportados.
4. Amostras geradas (`docs/assets/style_lock_sample_*.png`): arte nossa original,
   seguem para referência de estilo no repositório.

---

# APÊNDICE A — Templates de prompt (prontos para produção)

**Cena de produtor (quadro-base):**
> flat 2D cartoon mobile idle-game art, wide interior scene. Thick uniform black
> outlines, chunky rounded shapes, bold flat colors, single-tone cel shadows, dark
> teal grade with one {ACCENT} accent. {CENA}. Simple readable silhouettes, max 3
> characters, no gradients, no noise, no text, no watermark.

**Edição de ação (f2–f4 sobre f1):**
> same exact scene, camera, palette and characters as the reference image; change
> only: {AÇÃO}. Keep outlines and flat colors identical. No text.

**Busto (base + expressões):**
> flat 2D cartoon mobile game character bust, head and shoulders, {PERSONAGEM},
> {EXPRESSÃO}, thick black outlines, flat colors, dark teal circular background,
> no text. → edições: "same bust, expression: feliz / suspeito / surpreso".

**Banner de QG:**
> wide flat-cartoon secret hideout interior, {MAPA} theme, one conspirator at a desk,
> warm lamp glow as single accent, thick outlines, dark teal grade, no text.

# APÊNDICE B — Medidas do vídeo (bruto)

- Arquivo: 400×720, 30 fps, 1208 frames, 40,27 s.
- Cortes/scrolls fortes: 13,6 · 16,5–17,0 · 19,8–20,0 · 22,7–23,4 · 24,9–25,0 ·
  25,9 · 26,1–27,3 · 29,2–29,6 · 33,0 s.
- Mapa de movimento do take 0–13,5 s: cena do produtor concentra ~85% do movimento.
- Wiretaps modal: card ≈ 92% largura, cantos ~16 px, dim ≈ 60%.
- Ciclo de produtor medido: 6 s (barra ciano `00:06 → 1.0 Qa`).
- Amostras de cor: fundo lista `#296D60` · faixa `#40A59E` · renda `#CDB340`.

# APÊNDICE C — Amostras de style lock geradas (artes nossas, aprovadas p/ produção)

- `docs/assets/style_lock_sample_scene.png` — cena de produtor (alvo visual).
- `docs/assets/style_lock_sample_bust.png` — busto de coordenadora (alvo visual).

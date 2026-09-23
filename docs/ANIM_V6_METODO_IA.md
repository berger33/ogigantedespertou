# MÉTODO DE ANIMAÇÃO POR IA — v6 "keyframes gerados em sequência"

> **Status:** APROVADO pelo dono (set/2026). Substitui os métodos v2/v4/v5 (procedurais,
> arquivados no git). **Reset executado:** nenhuma missão está animada; em disco sobrou
> apenas o **frame original** (`poster.webp`) de cada uma das 50 missões.
> **Estudo que fundamenta o método:** ver `ANEXO` no fim deste documento.

## 1. A resposta curta à pergunta do dono

**Sim — dá para animar por IA sem tantas inconsistências**, mas não gerando quadro solto
por quadro. As inconsistências (flicker, morphing, deriva de personagem) nascem de gerar
cada imagem de forma independente. Os três antídotos, validados no estudo:

1. **Âncora permanente:** o poster aprovado entra como **imagem de referência em TODAS as
   gerações** (nunca acorrente um quadro no quadro anterior — o erro se acumula; acorrente
   tudo no quadro 0, que não deriva porque é arte aprovada e imutável).
2. **Tudo é edição, nada é criação:** cada keyframe é gerado por **image-to-image com a
   instrução de mudar UMA coisa** e "keep everything else exactly the same — style,
   palette, outline, proportions, background, lighting". Uma mudança por imagem.
3. **Poucos keyframes, movimentos pequenos:** 10 desenhos em 5 s = 1 desenho a cada
   500 ms (clips confortáveis para leitura de idle-game). Movimento pequeno entre
   keyframes = deriva pequena.

## 2. Pipeline por missão (v6)

```
E0 BOARD (10 poses com beats no tom WAI) → PORTÃO 1 (dono)
E1 KEYFRAMES IA (10 edições do poster, 1 mudança por edição)
E2 QA DE CONSISTÊNCIA (lints Q1–Q7 automáticos) → refazer keyframe reprovado
E3 ENTREGA: loop.webp (5s, 10fps, loop=0) + frames/ (10 quadros) + contact.png
E4 PORTÃO 2 (dono assiste) → promote.py → animated:true na spec
```

## 3. Os 10 keyframes — anatomia de um ciclo de 5 s

| Q | t (ms) | Papel no ciclo |
|---|---|---|
| 01 | 0 | **O POSTER ORIGINAL** (sem geração). Âncora e quadro de abertura. |
| 02–05 | 500–2000 | **antecipação → ação → pico** (o arco principal da piada) |
| 06–07 | 2500–3000 | **consequência/impacto** (a virada cômica) |
| 08–09 | 3500–4500 | **resolução + assentamento** |
| 10 | ~4750 | **pré-loop**: idêntico ao Q01 (lint Q6 exige) — o ciclo recomeça |

Regras de arco: começa no estado do poster, aplica antecipação antes da ação principal,
um evento primário por vez, e **retorna exatamente ao estado inicial** (loop perfeito).

## 4. Os 7 lints de consistência (`tools/animia/qa_frames.py`)

| # | Lint | Limiar | O que pega |
|---|---|---|---|
| Q1 | anchor_diff | cada Q ≤ 60 px médios de diff vs. poster (128px) | metamorfose da cena |
| Q2 | anchor_hue | Δ matiz ≥ 0.90 vs. poster | troca de paleta/estilo |
| Q3 | delta_progress | Δ(Qk,Qk+1) ≤ 45 p Médio | teletransporte entre quadros |
| Q4 | brightness | desvio-padrão de luminância ≤ 22 | flicker de exposição |
| Q5 | palette_shift | Δshare de matiz ≤ 0.035 por bin | re-tiling de cores |
| Q6 | loop_closure | |Q10 − Q01| ≤ 12 p | loop aberto |
| Q7 | palette_count | Δ #matizes dominantes ≤ 3 | Simplificação/richeza de cor |

Reprovou → o keyframe é re-gerado com instrução mais dura (até 3 tentativas;
persistindo, o quadro volta ao estado do poster + regeneração só da região).

## 4.1 Suavidade — camada de in-betweens (v6.1)

Crítica do dono ao primeiro piloto: "movimentações aleatórias e não contínuas". Correção:
entre cada par de poses-chave IA o pipeline gera **4 in-betweens** (`tools/animia/tween.py`)
com translação estimada por correlação FFT dos elementos em movimento (sem deformar pintura)
+ crossfade smoothstep no resto. Resultado: **41 desenhos @ ~122 ms**, delta médio entre
desenhos **1,35** (era o salto inteiro entre poses), emenda do loop **delta 0** (o último
desenho É o poster). Lint novo **Q8_smoothness**: max Δ entre desenhos consecutivos ≤ 12.
Keyframe reprovado no QA de frames (ex.: k05) é **excluído da sequência** — o tween entre
os vizinhos cobre o beat, e o quadro é regenerado por IA na rodada seguinte.

## 5. Especificação de entrega (por missão)

| Item | Valor |
|---|---|
| Duração | 5,00 s (5000 ms) |
| Desenhos | **10 desenhos únicos** (Q01…Q10), 1 a cada 500 ms |
| Contêiner | 10 fps (1 quadro = 100 ms) — reproduz a cadência "on twos" desejada |
| Loop | infinito (`loop=0`), Q10 = Q01 (lint Q6) |
| Quadro | 640×360 (padrão dos posters) |
| Peso | loop.webp ≤ 900 KB (q≈80) |
| Spec | `v6: true`, `frames: 10`, `duration_ms: 5000`, `fps: 10`, `loop_perfect: true` |
| Disco | `loop.webp` + `frames/ff_00…ff_09.webp` + `contact.png` (poster é intocado) |

## 6. Promote (v6)

`tools/animia/promote.py`: copia loop/frames/contact para a missão, marca
`animated: true, v6: true` na spec (`src/content/animations.json`) e grava
título/fala WAI em `producers.json`. O **poster jamais é substituído** — é o Q01.

## ANEXO — Estudo: como manter consistência em animação IA (set/2026)

**Princípio geral (todas as fontes):** consistência é propriedade do *fluxo de trabalho*,
não de um ajuste do modelo. Sem âncora visual, cada geração reinventa o personagem.

**Técnicas ranqueadas (flick.art, comparativo 2026):** Character Reference/img2img (alto,
baixo esforço) → Turnaround/multi-angle sheets (alto) → seed+prompt travados (médio) →
LoRA treinada (altíssimo, alto esforço) → face-swap de limpeza (alto, só rosto).

**Regras de ouro extraídas:**
- **Nunca acorrente quadro→quadro** ("every shot references the canonical sheet directly,
  never the previous shot" — martini.art): erro se acumula em cadeia; a âncora imutável é
  o poster.
- **Uma mudança por geração** + "keep everything else exactly the same" (modernphototools,
  receita de inpainting localizado, strength ≈ 0.75).
- **Framing/batching por condição visual** (Kittl): agrupar gerações com mesmo enquadramento
  e luz; movimentos controlados primeiro.
- **Primeiro/último quadro travados** (Kittl, flick): para loop, definir Q01=Q10 explícito.
- **Seed/estilo congelados** (animateai.pro): mesmos parâmetros em toda a sequência.
- **Poucos movimentos de alta leitura** batem melhor que micromovimentos generosos.

**Aplicação ao nosso caso:** episódio de 5 s com 10 desenhos, cena fixa de fundo (o poster),
sujeito principal com movimento pequeno e físico (1 mudança por keyframe), QA automático de
consistência com retrys — o mesmo espírito dos 8 lints da era procedural, agora medindo
**drift de geração** em vez de deformação de warp.

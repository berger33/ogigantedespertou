# MÉTODO DE ANIMAÇÃO v7 — RIG ESTRUTURAL (30 quadros @ 5 fps, 6 s, loop perfeito)

> **Status:** piloto `p5_02` (“A Fórmula da Água”) entregue set/2026, QA 6/6.
> Substitui o v6 (re-desenho por IA + tweens), **apagado** por inconsistências
> entre quadros (camisa/tanque/ponteiro derivavam — o erro era estrutural:
> cada quadro era uma imagem nova).

## 1. Por que o v6 falhou e o v7 não pode falhar igual

No v6 a consistência era **estatística**: cada quadro vinha de uma geração/edição
diferente, então personagem e cenário derivavam quadro a quadro.
No v7 a consistência é **estrutural**: todos os 30 quadros são compostos dos
*MESMOS pixels* (o poster aprovado), e o movimento é matemática periódica por
cima. Não há nenhuma imagem re-desenhada por quadro — logo, não há deriva possível.

## 2. Anatomia do rig (`tools/animia/rig_v7.py`)

| Camada | Origem | Movimento |
|---|---|---|
| Fundo (base) | poster + 2 furos inpaintados por interpolação horizontal das faixas vizinhas (procedural) | **nenhum — imutável nos 30 quadros** |
| Pipeta + mãos | sprite recortado do poster (polígono featherizado); furo inpaintado por trecho/linha + 2ª passada no halo de glow | **inclina 0→2,5° e volta** — o homem despeja; a gota cai no pico do tilt |
| Gota principal | recortada dos **próprios pixels do poster**; flood com barreira no outline **nítido do poster original** (`v7/outline_ref.png`, gravado pelo recolor) + silhueta paramétrica — a água do tanque (mesma cor) e a beirada NUNCA entram no sprite; outline do sprite = anel da própria máscara com cor constante | cai no pico do tilt → **afunda e se mistura** (squash + fade + anéis; sem coroa) |
| Gotinha da torneira | recortada do poster (sprite próprio, ciano = água do tanque) | forma → cai → **se incorpora à água do copinho** (squash + fade + anéis + glint) |
| Relógio/manômetro | **NÃO mexe** (pedido do dono) — fica o do poster | — |
| Anéis/brilhos/sparkles/glint | vetores procedurais (gaussianas, estrelas) | funções periódicas de k |
| Ponteiro do manômetro | tampa o original e redesenha (vetor) | balança + coice no splash, periódico |
| Gotinha da torneira | mesmo sprite da gota do poster em escala .38 | 1 queda por ciclo + glint no copinho |

Período = 30 quadros: todo parâmetro é soma de `sin(2π·n·k/30)` (n inteiro) e
gaussianas com suporte dentro do ciclo → **frame(30) ≡ frame(0) exato**
(QA Q1 = 0.0000).

## 3. Entrega por missão

| Item | Valor |
|---|---|
| Duração / fps | 6,00 s / 5 fps (200 ms por quadro) |
| Quadros | 30 (`v7/frames/f00..f29.webp`) |
| Contêiner | `v7/loop.webp` (RIFF, 30× ANMF 200 ms, loop=0) ≤ 900 KB |
| Quadro | 640×360 (o do poster) |
| Spec | `animated:true, method:"rig-v7", fps:5, frames:30, duration_ms:6000, loop_perfect:true` |
| Revisão | `src/review/v7_<id>.html` (`tools/animia/review_v7.py`) |

### 3.1 Padrão de exibição (pedido do dono, set/2026)

**Toda animação nova é mostrada ao dono EM TEMPO REAL, fora do jogo, ANTES de
qualquer promoção na spec** — e o loop novo **substitui o anterior no mesmo
caminho** (`v7/loop.webp`), nunca convivem dois. Na prática:

1. render + QA 6/6;
2. `present_file` do `v7/loop.webp` (o webp animado roda direto no viewer) **e**
   link direto de download/preview (`https://8000-<sandbox>.e2b.app/assets/anim/<id>/v7/loop.webp`)
   + folha `review/v7_<id>.html`;
3. só depois do ok do dono: `animated:true` na spec (substituindo o loop anterior).

## 4. QA (`tools/animia/qa_v7.py`) — piloto 6/6

| # | Lint | Resultado do piloto |
|---|---|---|
| Q1 | loop_closure: frame(30) == frame(0) | 0.0000 |
| Q2 | fundo_intacto: fora das regiões animadas, diff ≤ 2/255 vs. base | 2 |
| Q3 | fundo_cobertura: regiões animadas ≤ 40% da imagem | 16,95% |
| Q4 | flicker: desvio da luminância média ≤ 6 | 0.4 |
| Q5 | step_delta: diff média entre consecutivos ≤ 20 | máx 1.2 |
| Q6 | entrega: RIFF, 30× ANMF 200 ms, ≤ 900 KB | 296 KB |

## 5. IA neste método — papel zero

O piloto final é **100% procedural**: nem o splash veio da IA (a coroa foi
substituída pela própria gota afundando). Tentativas de usar IA para editar o
cenário (plates “sem a gota”) foram testadas e **descartadas**: o modelo
re-desenha a composição inteira (pose/rosto/ponteiro mudam), exatamente a deriva
que o método existe para eliminar. Tudo que exige fidelidade de pixel é
procedural ou recortado do poster.

### 5.1 Veneno verde (recolor_v7.py)

Pedido do dono: o líquido da pipeta e as gotas que caem dela são **verde
veneno**; a água do tanque/torneira/copinho continua ciano. Implementação:
hue shift −45° (S/V preservados) restrito ao bbox da pipeta, e a gota central é
recortada limpa, recolored e colada de volta sobre o furo inpaintado — o halo
vira overlay procedural no rig (nunca baked, para não carregar pixels da
beirada). Idempotente.

## 6. Rollout das demais missões

Mesmo rig, missão a missão: medir geometria no poster (bicos, superfícies,
mostradores), definir beats, rodar `rig_v7.py --mission <id>` + `qa_v7.py` +
`review_v7.py`, promover na spec só com QA 6/6 e portão do dono.

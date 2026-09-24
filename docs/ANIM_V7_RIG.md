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
| Gota principal | recortada dos **próprios pixels do poster** (máscara = diff poster×base, limitada a silhueta de gota paramétrica) | forma no bico → desce → some no splash (periódico) |
| Splash | **único asset de IA** (`v7/ai/splash.png`, sprite isolado em fundo magenta, chroma-key) | pop + fade no impacto |
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

## 4. QA (`tools/animia/qa_v7.py`) — piloto 6/6

| # | Lint | Resultado do piloto |
|---|---|---|
| Q1 | loop_closure: frame(30) == frame(0) | 0.0000 |
| Q2 | fundo_intacto: fora das regiões animadas, diff ≤ 2/255 vs. base | 2 |
| Q3 | fundo_cobertura: regiões animadas ≤ 40% da imagem | 16,95% |
| Q4 | flicker: desvio da luminância média ≤ 6 | 0.4 |
| Q5 | step_delta: diff média entre consecutivos ≤ 20 | máx 1.2 |
| Q6 | entrega: RIFF, 30× ANMF 200 ms, ≤ 900 KB | 296 KB |

## 5. IA neste método — papel deliberadamente pequeno

A IA entra **uma vez**, para gerar um sprite de estilo (o splash), isolado em
fundo magenta e aplicado por chroma-key. Tentativas de usar IA para editar o
cenário (plates “sem a gota”) foram testadas e **descartadas**: o modelo
re-desenha a composição inteira (pose/rosto/ponteiro mudam), exatamente a deriva
que o método existe para eliminar. Tudo que exige fidelidade de pixel é
procedural ou recortado do poster.

## 6. Rollout das demais missões

Mesmo rig, missão a missão: medir geometria no poster (bicos, superfícies,
mostradores), definir beats, rodar `rig_v7.py --mission <id>` + `qa_v7.py` +
`review_v7.py`, promover na spec só com QA 6/6 e portão do dono.

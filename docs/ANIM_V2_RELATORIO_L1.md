# Relatório — Parte 1 (Lote 1): Religião

> Execução do plano `docs/ANIM_V2_PLANO_LOTES.md`, Parte 1: as 10 missões do mapa
> **Religião** (`p4_01`…`p4_10`) deixaram de ser "movimento sutil" e passaram a ser
> **loops narrativos**: setup → ação → resolução → reset, com emenda fechada.
> Este é o lote padrão-ouro, porque contém os três exemplos de complexidade do dono.

## Regra de ouro respeitada

A pintura aprovada **continua sendo a base** e não foi redesenhada. Por cima dela
entram, em camadas:

* **warps locais** (deslocamento/rotação com máscara) no que já está pintado —
  mão, cabeça, boneca, engrenagem, chama, disco — sem abrir buraco na arte;
* **recorte por silhueta** para o que precisa viajar na cena (a garrafa do p4_08);
* **inpaint** (interpolação por linha + difusão) só onde a mecânica exige apagar
  algo pintado — o feixe apagado do p4_05, as pessoas no céu do p4_10, a estação
  do bico do p4_08, o interior do copo do p4_06;
* **FX desenhados** no mesmo traço flat-toon (gotas, auréola, lágrima, confete,
  chamas, vapor, papéis, pessoas).

Todas as adaptações são **locais** e existem só onde a mecânica pede — nada mais
do desenho foi alterado.

## O que cada missão faz (checklist do plano × entregue)

| Missão | Beats entregues |
| --- | --- |
| **p4_10 · Projetar o arrebatamento holográfico** | quadro 1 **sem luz e com o botão livre** → aperta → **feixe acende** → pessoas **sobem aureoladas e somem** → luz apaga → pessoas voltam em pé (loop). |
| **p4_08 · Bendizer a água da torneira** | **esteiras andam** com as garrafas → **torneira enche** a garrafa vazia sob o bico → a cheia **segue para o outro lado** e ganha **adesivo de auréola** → **vapor, bolhas, goteira e engrenagens** animam → inspetor **olha, anota e vira a página**. |
| **p4_06 · Mandar a imagem chorar xarope** | o **quadro chora**: gotas formam no fio, caem e **enchem o copo** → o comerciante **mergulha a colher, serve o vidro** no pote e o copo esvazia → **velas e lamparinas tremulam** o tempo todo. |
| p4_01 · Mensagem invertida no vinil | disco gira (com brilho orbitando — círculo perfeito não revela giro), agulha vibra, espirais oscilam, letreiro revela **"LIVE" espelhado**, notas invertidas saem das caixas, velas tremulam. |
| p4_02 · Indução espiritual | TV pulsa, diabinho balança, **olhos do menino e do gato giram**, rabo do gato mexe, pipocas saltam. |
| p4_03 · Fábrica do boneco possuído | **esteira/engrenagens andam**, bonecas marcham, a **possuída flutua** com aura roxa, olhos acendem e a **chave gira**, o pincel pinga. |
| p4_04 · Sigilo geométrico | o mapa aparece **limpo** e o **sigilo se desenha do centro para fora** sobre a capital, o olho alado circula, o alfinete crava, o traço pulsa e **apaga no reset**. |
| p4_05 · Milagre ao vivo | **palco escuro → holofote acende**, confete de luz desce, a **lágrima gigante cai** no arco, a plateia entra em êxtase e a **luz apaga**. |
| p4_07 · 13º mandamento no áudio | dois rolos giram, a **onda de áudio corre** pela fita, o **"13" pisca** na tábua, agulhas do painel tremem, o monge oscila. |
| p4_09 · Empurrar o apocalipse (de novo) | ele **empurra** o bloco do X, a sirene gira, **papéis voam**, o **carimbo marca mais um dia** e o calendário zera no reset. |

## Qualidade medida

* **Quadros**: 12 nas missões de ritmo simples e **16** nas multi-elemento
  (p4_03, p4_05, p4_06, p4_08, p4_10) — acima do mínimo de 12 que a QA exige.
* **Duração**: 1,56 s a 2,66 s por loop, com ritmo (setup lento → ação rápida →
  hold → reset suave), sem corte de câmera.
* **Emenda de loop auditada nas 50 cenas** (razão entre a diferença do quadro
  final↔inicial e a diferença média entre quadros vizinhos; >2,2 = salto):
  **todas fechadas**. O lote 1 ficou em: p4_10 = 0,00 · p4_05 = 0,22 · p4_04 =
  0,65 · p4_01 = 0,94 · p4_08 = 1,00 · p4_06 = 1,21 · p4_07 = 1,23 · p4_03 =
  1,37 · p4_09 = 0,46 · p4_02 = 1,23.
* **Consistência de cena** (o quanto muda entre quadros): 0,26 (p4_06) a 3,88
  (p4_10) — a variação é intencional: cenas com mais história mudam mais.

## Como conferir

```bash
python3 -m tools.narrative.render_lote1          # re-renderiza o lote inteiro (~40 s)
python3 -m tools.narrative.render_lote1 p4_10    # só uma missão
npm test                                          # QA do jogo (inclui o contrato v2)
```

* Página de revisão do lote: **`src/review/lote1.html`** (compara os loops e
  o quadro a quadro).
* Folha de contato por missão: `src/assets/anim/<id>/contact.png`.
* Spec: `src/content/animations.json` ganhou `v2`, `frames`, `story` e
  `duration_ms` (campos aditivos, nada removido).

## Próximo passo (Parte 2)

**Deep Web — `p1_01`…`p1_10`**, com 12 quadros por missão e 16 nas
multi-elemento (p1_09 marionete, p1_10 controle do clima). Reaproveita o motor
`tools/narrative/kit.py` já provado aqui; entram inpainting só onde a mecânica
pedir, seguindo a mesma regra de ouro. Só começa **depois da validação desta
Parte 1**.

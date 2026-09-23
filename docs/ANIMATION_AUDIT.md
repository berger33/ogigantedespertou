# AUDITORIA DE ANIMAÇÃO — as 50 cenas × We Are Illuminati

Fonte da referência: `We are Illuminati- Conspiracy Simulator Clicker.mp4`
(trailer 400×720, 30 fps, 40 s), medido quadro a quadro. Arte deles **não**
foi copiada. O que se copia é a gramática do movimento.

As pinturas já estavam boas. O que falhava era a **sequência** que faz a
cena se mexer.

---

## 1. O que o gênero faz de verdade

Medido no trailer, não chutado:

| O que se vê | O que NÃO se vê |
|---|---|
| Fundo **parado**. A diferença entre quadros do cenário é preta. | Câmera dando zoom na cena inteira. |
| Um ator (ou um objeto) em ciclo: braço, alavanca, prédio que sobe, janela que acende. | Quatro poses desconectadas. |
| Efeito viajando: moeda, onda, faísca, papel. Nasce, cruza, some. | Anel/brilho colado em cima da pintura, sem trajetória. |
| Loop de ~1 s, contínuo, sem corte no retorno. | Segurar o último quadro e pular de volta. |
| O card mostra o **diorama inteiro**. A piada cabe no quadro. | Um rasgo horizontal que corta cabeça e chão. |

A ficha do produtor deles é uma cena emoldurada em loop. O clique do
jogador só liga/desliga esse loop — não é um filme de 3 segundos com começo
e fim.

---

## 2. O que as nossas 50 estavam fazendo (antes)

Medição automática nos `ff_*.webp` de então (4 quadros, durações
260/180/220/420 ms):

| Classe | Cenas | O que o olho lia |
|---|---|---|
| **CAMERA** | 28 | o quadro inteiro pulava de escala (o `zoom_pan` das recipes). Parece quebrado. |
| **MIXED** | 17 | um pouco de efeito, mas o fundo também andava. |
| **STICKER** | 5 (`p5_02`, `p5_05`, `p5_06`, `p5_08`, `p5_09`) | quase nenhum pixel mudava. A "animação" era um adesivo. |

Três causas, todas estruturais:

1. **4 quadros não são um ciclo.** Sem intermediários, o olho vê um corte,
   não um gesto. O gênero usa dezenas de quadros por segundo; o mínimo que
   ainda lê como movimento é um seno amostrado em ~10 passos.
2. **O zoom era a câmera, não o ator.** `zoom_pan` deslocava a pintura
   inteira. No retorno para o quadro 0 (sem zoom) havia um pulo.
3. **O card escondia a cena.** `.prod-frame` estava em `320/88` (o viewBox
   do SVG antigo). `object-fit: cover` mostrava só ~49% da altura, centrado
   em 32%. O verbo — prato, pé, gota, disco — caía fora do rasgo.

---

## 3. O que mudou

Motor: `tools/wai_animate.py`. Roda em cima do **poster limpo**
(a pintura aprovada). As três cenas de Religião que o autor pediu
como régua de qualidade (`p4_06` xarope, `p4_08` torneira, `p4_10`
arrebatamento) têm **história** — não seno em cima da placa:

- `p4_10` (16 q): luz apagada → aperta o botão → feixe acende →
  civis sobem com auréola e somem → luz apaga → o loop recomeça.
- `p4_08` (12 q): esteira das garrafas, jato da torneira, bolhas
  nos tanques, vapor, pingos, auréola de “rótulo santo”, inspetor
  anota na prancheta.
- `p4_06` (12 q): lágrimas de xarope caem no potinho, o nível sobe,
  velas/lamparinas tremulam.

Gramática, uma por cena, em `P` no próprio script (ou `STORIES`):

| Verbo | Onde aparece | Como |
|---|---|---|
| `bob` / `swing` | marionete, político no muro, dupla, boneco | o pedaço se mexe; o fundo fica |
| `spin` | globo do tempo, vinil | giro rígido de N voltas, pena só na borda |
| `wave` | apagão, robôs votando | as luzes já pintadas apagam em onda e voltam |
| `scan` | jornal, TV do pneu, QR, palco | faixa que atravessa e some nas pontas |
| `arcs` | Wi-Fi, megafone, torre-palmeira, GPS | anel nasce, cresce, morre; outro já está no meio |
| `travel` | moeda, gota, nota, panfleto | trajetória com fade nas pontas — o loop não corta |
| `sparks` / `pulse` | bateria do robô, tomada, olhos, telas | o que já estava pintado acende; a faísca orbita |

Regras que fecham o loop:

- todo deslocamento é `sin(2π · t)` ou um número **inteiro** de voltas;
- partícula soma e nasce dentro do ciclo (`fade` nas pontas);
- 10 quadros × 100 ms = **1,0 s**, passo igual, sem o hold de 420 ms.

O card passou a `aspect-ratio: 16/9` com `object-position: center`. A cena
inteira aparece. É assim que o gênero mostra o produtor.

---

## 4. Números depois

| | Antes | Depois |
|---|---|---|
| Quadros | 4, durações desiguais | 12 × 110 ms (16 no Blue Beam) |
| Câmera andando a cena | 28 cenas | 0 (fundo travado) |
| Pulo do loop vs passo normal | o retorno era o maior corte | 1,9 vs 1,3 (mesmo passo) |
| Peso do `loop.webp` | — | 46–363 KB, mediana 172 KB, total 8,7 MB |
| Testes de animação | 50/50 | 50/50 |

Cenas que valem abrir para conferir o verbo:

- `p1_09` marionete balança no fio, palco parado
- `p1_10` globo do tempo gira dentro do aro (a cabeça do cientista ficou)
- `p4_01` vinil dá a volta
- `p5_03` as janelinhas apagam em onda; o alarme fica
- `p5_06` faísca no compartimento, sem borrão no rosto
- `p5_09` a varredura fica em cima do prato
- `p2_06` o anel sai do megafone e o panfleto atravessa o céu

---

## 5. O que isto ainda não é

Não é rig de Spine. Não temos o ator separado do fundo — a pintura é uma
placa só. Por isso:

- um braço não articula osso a osso; o `swing` gira uma região com queda
  suave na borda, amplitude curta de propósito (8–12°) para não virar gelatina;
- o `bob` é de 3–9 px. Mais que isso mancha o cenário;
- partícula é desenhada por cima, no mesmo contorno grosso, não é um
  segundo personagem.

Isso é o teto honesto de animar uma pintura pronta sem redesenhar 500
quadros. O próximo salto (se um dia valer) é exportar ator/fundo em
camadas e aí sim ter o braço, a perna e a piscada como no CSS da rig
SVG antiga (`arm-swing`, `leg-kick`, `head-nod` em `src/theme/app.css`).

---

## 6. Como regenerar

```bash
.venv/bin/python tools/wai_animate.py p5_06     # uma cena
.venv/bin/python tools/wai_animate.py --all     # as 50
```

A performance de cada id está no dicionário `P` de `tools/wai_animate.py`.
Trocar o verbo é editar essa lista e rodar de novo. O `poster.webp` não
é tocado — continua o estado "não comprado".

# LOTE 1 (Religião, p4_01…p4_09) — Boards E0 para Gate 1

> Fluxo (docs/ANIM_V4_PLANO_REMAKE.md §3): **uma missão por vez**. Este documento traz o
> board da missão da vez; aprovado no Gate 1 → E1 (assets IA) → E2–E4 → Gate 2 → promote.py.
> **Padrão congelado:** piloto `p4_10` (9/9 checagens verdes, 5,00 s = 3,4 s@10 fps +
> 1,6 s@16 fps, camadas afins, holds, smear, loop fechado).

---

## Missão da vez: `p4_01` — *Inverter a mensagem no vinil*

**Fala (tom WAI):** “Na letra, amor. No replay, obediência.”
**Perfil de tempo:** **P3 · ritual/solene** — 4,0 s @10 fps (40 f) + 1,0 s @14 fps (14 f) = **54 quadros**.
**Evento primário (R9):** a virada do disco com a mensagem invertida.
**Secundários (30–50 %):** espirais girando, reels, velas, neon.
**Leitura em 320 px:** mão → disco → letreiro invertido; espirais como moldura de movimento.

### Beats (ms · tokens §6)

| t (ms) | Beat | Tokens | Camada/FX envolvido |
|---|---|---|---|
| 0–300 | establish: estúdio, mão no mixer, disco parado, neon apagado | `hold` | plate |
| 300–700 | antecipação: mão ergue sobre o prato | `anticipate` | patch `hand_raise` |
| 700–1000 | ato: mão vira o disco; label trocado com smear de 1 quadro | `act`, `impact` | patch `hand_flip` + smear + dust |
| 1000–1400 | impacto: neon “olho” acende com flicker; espirais começam a girar | `blink`, `act` | stamp neon + rotação swirlL/R |
| 1400–2600 | ação: espirais giram (esq. anti-horário, dir. horário); notas INVERTIDAS sobem do prato | `act` | rotação + partículas notes |
| 2600–3400 | secundários: reels giram; cabeça do DJ acompanha o beat (±3°, pivô no pescoço) | `follow` | rotação reels + camada head |
| 3400–4000 | hold de leitura: letreiro “ƎVI⅃” brilha no label + luz varrendo | `hold`, `sweep` | stamp lettering + light_sweep |
| 4000–4500 | **rajada B @14 fps**: espirais aceleram; confete de notas invertidas; cones pulsam | `impact` | rotação spike + lightbits + pulso |
| 4500–4800 | follow-through: espirais desaceleram; notas dissipam | `follow` | easing settle |
| 4800–5000 | settle: neon apaga, mão volta ao mixer, disco parado = **frame 0** | `settle` | loop fecha (L3) |

### Assets IA (11 = 20,4 % de 54 ✓ L9)

| # | Asset | Como nasce | Papel |
|---|---|---|---|
| 1 | `plate.png` (S0) | edição IA do poster: sem espirais/notas voadoras, neon apagado | backplate |
| 2 | S1 mão virando o disco | edição de S0 | patch `hand_flip` |
| 3 | S2 espirais+notas + neon aceso | edição de S0 | camadas `swirlL`, `swirlR`, `neon` |
| 4 | S3 mão erguida | edição de S0 | patch `hand_raise` |
| 5 | S4 cabeça no beat (grin/tilt) | edição de S0 | camada `head` (pivô pescoço) |
| 6 | S5 cones dos speakers pulsados | edição de S0 | camada `cones` (escala uniforme 4 %) |
| 7 | S6 estúdio sem reels | edição de S0 | camada `reels` (rotação procedural) |
| 8 | atlas notas invertidas | text-to-image (fundo preto) | partículas espelhadas/rot 180° |
| 9 | atlas letreiro “ƎVI⅃” | text-to-image (fundo preto) | stamp no label |
| 10 | atlas chamas de vela (3 variantes) | text-to-image (fundo preto) | flicker das velas |
| 11 | atlas glow do neon olho | text-to-image (fundo preto) | bloom do neon |

### Procedural (código, 0 imagens)

Rotações afins (swirlL/swirlR/reels/label), curvas de flicker, partículas de notas e
confete, smear de 1 quadro, light sweep, dust de impacto, pulso uniforme dos cones,
holds e agenda de fps (motion.py), encode WebP com duração por quadro.

### Lints aplicados (idem piloto)

L1 placa ≤0,5 % · L2 borda · L3 loop · L4 5,00 s/P3 · L5 ≤8 % (cones usam escala
**uniforme**, isentos de squash) · L6 paleta/contorno · L7 Z (patches acima da plate) ·
L8 ≤2.600 KB @1280×720 · L9 IA ≥20 %.

### Gate 1 — decisão do dono

- [ ] Aprova o beat sheet acima (10 beats, primário = virada do disco)?
- [ ] Aprova a lista de 11 assets IA + o restante procedural?
- Aprovo e digo “prossiga” → executo E1–E5 e trago o clip + QA no Gate 2.

---

## Fila do lote (boards seguintes, um por vez)

| Ordem | Missão | Perfil previsto | Primário |
|---|---|---|---|
| 2 | p4_02 Exibir o desenho que induz | P2 | anéis da espiral girando + olhos rodando |
| 3 | p4_03 Fabricar o boneco possuído | P2 | chave de corda girando + olhos acendendo |
| 4 | p4_04 Traçar a capital em sigilo geométrico | P2 | sweep radial desenhando o sigilo |
| 5 | p4_05 Encenar o milagre ao vivo | P1 | holofote pop + lágrima gigante |
| 6 | p4_06 Fazer o quadro chorar xarope | P3 | gotas formam, caem e enchem o copo |
| 7 | p4_07 Gravar o 13º mandamento na estática | P2 | rolos disparam + “13” pisca |
| 8 | p4_08 Bendizer a água da torneira | P1 | esteira + garrafa enchendo + stamp auréola |
| 9 | p4_09 Adiar o apocalipse (de novo) | P1 | empurrão do bloco + carimbo + papéis voam |

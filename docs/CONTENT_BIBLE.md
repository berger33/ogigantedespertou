# CONTENT_BIBLE.md — O GIGANTE DESPERTOU

> DefinE universo, nomenclatura, tom do texto, e os inventários de conteúdo e
> arte. Todo texto novo de jogo segue `SATIRE_GUIDELINES.md`.

---

## 1. Universo & lore (§3, §99–§102)

Você lidera a **organização secreta mais incompetente e, ao mesmo tempo,
inexplicavelmente poderosa do Brasil**. Escala narrativa:

grupo de zap → bairro → cidade → país → planeta → galáxia → economia universal.

### Personagens-núcleo
- **O ARQUIVISTA** (§100): narrador de humor seco, rosto nunca revelado;
  explica sistemas e pode quebrar a 4ª parede.
- **AGÊNCIA DO ÓBVIO** (§101): rival fictícia que tenta "desmentir tudo".
- **Nailitper-equivalente:** *não existe* — substituído por O Arquivista (evita
  qualquer semelhança com o mascote do jogo de referência, §2 regra anti-cópia).

### Twist de endgame (§84)
Após dominar a Religião: **"A VERDADEIRA CONSPIRAÇÃO ERA VOCÊ"** — a organização
descobre estar dentro de um idle game (4ª parede) → desbloqueia **ARQUIVO Ω**.

---

## 2. Moedas no universo

| Moeda | Lore |
|---|---|
| Mentes 🧠 | a "unidade de gente convencida" (contador com desenho de cérebro ao lado) |
| Chumbo 🛸 | visual inspirado no *Mistério das Máscaras de Chumbo* — tratado como **lenda urbana/ficção**, nunca como relato factual (§98, §277) |
| Convictos 🙇 | os mais convencidos, que permanecem após o reset |

---

## 3. InvenTário de conteúdo

### 3.1 Produtores = missões (40 = 10 × 4 mapas) — §31–§34
Ids e ordem lógica em `src/content/producers.json` (gerados por
`tools/gen_campaign.py`; os 4 mapas operam em paralelo):

```
p1_01 Comprar as maiores empresas com cripto            (12)
p1_02 Plantar fake news na mídia                        (60)
p1_03 Fazer amizade com os reptilianos                  (700)
p1_04 Colocar um informante no governo                  (8.340)
p1_05 Fomentar teorias da conspiração                   (90.680)
p1_06 Lavar o cérebro de artistas pop                   (1,04 M)
p1_07 Começar guerras por lucro                         (14,93 M)
p1_08 Controlar mentes através do Wi-Fi                 (179,16 M)
p1_09 Manipular governantes fantoches                   (2,15 B)
p1_10 Gerenciar sistemas de controle do clima           (25,8 B — missão final)
p2_01..p2_10 Democracia Relativa (309,6 B → 1,597 Qd)
p3_01..p3_10 Ratanabá (19,17 Se → 9,891 Otg)
p4_01..p4_10 Religião (1,187 Vg → 6,124 Cré)
```

### 3.2 Coordenadores (§38) — 40 + Zé do Chapéu de Alumínio
`MGR_01..MGR_40` e `MGR_ALU`. Cada um: silhueta, personalidade, idle anim,
descrição, **frase de contratação**, **frase de upgrade** (§39).

### 3.3 Sósias (§44–§49) — raridades COMUM/INCOMUM/RARO/ESPECIAL
> ⚠️ **Aviso IP (§48):** todos os nomes abaixo são **PROVISÓRIOS**. Antes de uso
> comercial: verificar colisão com propriedade intelectual/personalidade real.
> Em dúvida, substituir.

Um sósia por missão (40; catalogado em `src/content/clones.json`). Exemplos por
mapa — Deep Web: Tio do Zap, Mancheteira, Zé Escamoso, Conselheiro, Boateiro,
Diva Hipnotizada… Democracia Relativa: Eleitor do Meme, Deputado do Meio, Sósia
Eleito… Ratanabá: Escavador de Lumiar, Cartógrafo Cego, Prefeito Fantasma…
Religião: Pastor do Cashback, Restaurador do Xarope, Franqueado Celeste.
Duplicata vira **Puxa-Saco** (+1% produção global), com pity de 25 aberturas
para Raro (transparência §48).

### 3.4 Zap Vazado (§52, §56) — meta: centenas
Schema: `id, headline, body, categoria, fase, respostaCerta, recompensa,
raridade, tags`. Exemplos iniciais:
- "Áudio de 11 minutos afirma que a água do filtro está ouvindo a conversa."
- "Foto mostra suposto disco voador estacionado em vaga de idoso."
- "Print afirma que Ratanabá tem estacionamento subterrâneo."
- "A tia do grupo diz que a Lua mudou de CEP."

### 3.5 Achievements (§95) — ≥60 no lançamento (300+ suportados)
Primeiros: "Você Também Acha Que É Plano", "Chapéu de Alumínio Platinado",
"Todo Mundo no Grupo", "A Fonte É Confia", "Eu Vi Num Vídeo",
"Agora Tudo Faz Sentido", "O Gigante Despertou". Secretos (§96) + easter eggs
(20+, §269) + estatísticas absurdas (§268).

---

## 4. Escrita: copy & microcopy (§266–§267)

- Curta, engraçada, legível. Nada de piada longa em telas de economia.
- Microcopy fixada:
  - BUY MAX: **"Comprar Tudo"**
  - Offline: **"Enquanto você sumiu…"**
  - Prestige: **"Tem certeza que quer acordar esse negócio?"**

---

## 5. Inventário de assets (referência §216–§217)

| Categoria | Meta |
|---|---|
| HQ themes | 4 |
| Enviroments de tela | 9 |
| Visuals de produtores | 40 (missões) |
| Coordenadores (bustos + expressões) | 40 |
| Sósias/colecionáveis | 40+ ao longo do conteúdo |
| Ícones de UI | 80+ |
| VFX | dezenas |

Não gerar tudo antes do vertical slice (§217).

---

## 6. Inventário de áudio (§218)

20–40 SFX principais, 5+ músicas, feedback de UI e ambiências. Placeholder só
em protótipo — proibido na build final (§219).

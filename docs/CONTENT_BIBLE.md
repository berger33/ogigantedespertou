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
Após dominar os Bancos: **"A VERDADEIRA CONSPIRAÇÃO ERA VOCÊ"** — a organização
descobre estar dentro de um idle game (4ª parede) → desbloqueia **ARQUIVO Ω**.

---

## 2. Moedas no universo

| Moeda | Lore |
|---|---|
| Crédulos 👁 | a "unidade de gente convencida" |
| Chumbo 🛸 | visual inspirado no *Mistério das Máscaras de Chumbo* — tratado como **lenda urbana/ficção**, nunca como relato factual (§98, §277) |
| Convictos 👁‍🗨 | os mais convencidos, que permanecem após o reset |

---

## 3. InvenTário de conteúdo

### 3.1 Produtores (48 = 12 × 4 fases) — §31–§34
Ids e ordem lógica em `src/content/producers.json` (Fase 1 completa no core;
Fases 2–4 abaixo idênticas ao GDD §8, com ids mentorreservados):

```
PRD_phase1_01 Comprar Big Techs com cripto
PRD_phase1_02 Barriga Viral Misteriosa
PRD_phase1_03 Amizade com Reptilianos
PRD_phase1_04 Profeta Autoproclamado como Informante
PRD_phase1_05 Espalhar Lenda de Ratanabá
PRD_phase1_06 Mensagens Subliminares em Clipes
PRD_phase1_07 Venda da Copa de 98
PRD_phase1_08 Internacionalizar a Amazônia pelo Wi-Fi
PRD_phase1_09 Controlar Prefeitos e Governadores Fictícios
PRD_phase1_10 Controle do Clima no Carnaval
PRD_phase1_11 Clonar Celebridades Fictícias
PRD_phase1_12 Capturar o ET de Varginha
```

### 3.2 Coordenadores (§38) — 12 + Zé do Chapéu de Alumínio
`MGR_01..MGR_12` e `MGR_ALU`. Cada um: silhueta, personalidade, idle anim,
descrição, **frase de contratação**, **frase de upgrade** (§39).

### 3.3 Sósias (§44–§49) — raridades COMUM/INCOMUM/RARO
> ⚠️ **Aviso IP (§48):** todos os nomes abaixo são **PROVISÓRIOS**. Antes de uso
> comercial: verificar colisão com propriedade intelectual/personalidade real.
> Em dúvida, substituir.

Fase 2 (proposta do brief, original e adaptada):
Marechal Confisco-Geral, Sargento Barriga-Postiça, General Escama-de-Aço,
Chanceler Aleluia, Coronel Selva-Perdida, Dod Bylan, Napigleon, Fnord T,
Of Handmaid, Mirror Broker, Ministro Apagou-Tudo, Capitão Zona-51-BR.

> *Nota de auditoria:* alguns nomes ("Dod Bylan", "Napigleon", "Fnord T",
> "Of Handmaid", "Mirror Broker") ecoam clones do jogo de referência. Mantidos
> como placeholder a pedido do brief §48, com **flag de revisão de IP** ativa.

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
| Visuals de produtores | 48 |
| Coordenadores (bustos + expressões) | 12 (+variantes de fase) |
| Sósias/colecionáveis | 48+ ao longo do conteúdo |
| Ícones de UI | 80+ |
| VFX | dezenas |

Não gerar tudo antes do vertical slice (§217).

---

## 6. Inventário de áudio (§218)

20–40 SFX principais, 5+ músicas, feedback de UI e ambiências. Placeholder só
em protótipo — proibido na build final (§219).

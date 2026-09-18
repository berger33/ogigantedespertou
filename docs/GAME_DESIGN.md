# GAME_DESIGN.md — O GIGANTE DESPERTOU

> **GDD v0.1.0** — documento vivo. Cada sistema aponta para a seção da
> especificação original (§n) que atende e para onde está implementado/planejado.

---

## 1. Visão

**Gênero:** Idle Clicker / Incremental / Management / Collection.

**Fantasia:** o jogador controla uma organização secreta brasileira
absurdamente incompetente e, ao mesmo tempo, inexplicavelmente poderosa. Ela
tenta dominar **Brasil → instituições fictícias → mídia → tecnologia →
alienígenas → sistema financeiro mundial → a própria realidade**, tudo pela
disseminação de teorias absurdas (§3).

**Promessa ao jogador (§8):** começa tocando um botão num porão suspeito e
termina controlando a economia intergaláctica por meio de uma corporação secreta
brasileira. O crescimento precisa parecer **AB SURDO** — a escalada é parte da
comédia (§9).

**Frase de marca (§320):** *"Você não cria teorias. Você planta. E colhe crédulos."*

---

## 2. Tom e linha editorial (§4–§7, §164–§166)

- Humor **ácido, nonsense, surreal, autoconsciente**, de internet brasileira:
  grupos de mensagem, boatos, lendas urbanas, cultura pop, burocracia fictícia.
- Rimos **da máquina conspiratória e seus absurdos**, não de grupos vulneráveis.
- Nunca desinformação eleitoral, acusações a pessoas reais, alegações médicas
  falsas, discriminação, políticos reais como personagens, partidos, slogans.
- Pessoas reais: apenas inspiração cultural, nunca réplica (nome/rosto/voz/bio).
- Sátira é da *mecânica* da conspiração, nunca de ideologia ou de partido.
- Aviso permanente em tela e store: **obra de ficção e sátira** (§5).

Ver `SATIRE_GUIDELINES.md` para o checklist editorial aplicável a TODO texto novo.

---

## 3. Público e fantasia de poder (§9, §318)

Fantasia central: **"Como isso foi de um áudio de WhatsApp para controle do FMI
intergaláctico?"**

Escada conceitual: grupo de mensagens → bairro → cidade → país → planeta →
galáxia → economia universal.

---

## 4. Core Loop (§15–§16)

```
COMPARTILHAR (clique) → GERAR CRÉDULOS → COMPRAR PRODUTORES
→ GERAR MAIS → AUTOMATIZAR (Coordenadores) → COMPRAR UPGRADES
→ DESBLOQUEAR CONSPIRAÇÕES → ABRIR NOVA FASE → PRESTIGE
→ GANHAR CONVICTOS → VOLTAR MUITO MAIS FORTE
```

**Horizontes de retenção (§16, §129):**
| Janela | Foco |
|---|---|
| Minutos | comprar produtor / upgrades |
| Horas | automatizar (Coordenadores) |
| Dias | Prestige |
| Semanas | colecionar Sósias |
| Meses | eventos + fases + coleção |

---

## 5. Moedas (§17–§19)

| Moeda | Emoji | Obtida por | Usada para |
|---|---|---|---|
| **Mentes** | 🧠 | clique, produtores, eventos, bônus, offline | produtores, upgrades, automação, expansão |
| **Chumbo** | 🛸 | recompensas raras, achievements, Zap Vazado, eventos, rewarded, IAP | Laboratório de Sósias, cosméticos, conveniência |
| **Convictos** | 🙇 | **Despertar o Gigante** (prestígio) | bônus permanentes (aquém/entre resets) |

- Mentes = gente convencida pela organização (contador com desenho de cérebro ao lado).
- Chumbo faz referência visual ao Mistério das Máscaras de Chumbo (contexto
  cultural, tratado como ficção — ver CONTENT_BIBLE).
- Convictos permanecem após reset e aplicam **bônus global permanente**.

---

## 6. Big Numbers (§20–§21)

- Sem `float`/`double` para economia tardia; sistema dedicado (`BigNumber`).
- Formatos configuráveis: **nomes completos** (`1 milhão`, `1 bilhão`…),
  **abreviado** (`1,5 M`, `2,3 Qa`…), **científico** (`1,5e6`) — padrão BR.
- Overflow silencioso é proibido (testado).

Implementação: `src/core/BigNumber.js` + espelho `unity/`.

---

## 7. Ação principal — Compartilhar no Zap (§22–§26)

Botão **COMPARTILHAR NO ZAP** (celular → mensagem encaminhada → contatos → Mentes).

- **Feedback do clique:** bounce, contador, partículas (celulares voando),
  vibração leve, som de notificação, multiplicador flutuante.
- **Combo (§24):** cliques consecutivos elevam o **Engajamento Viral** de
  `x1 → x1.1 → x1.2 → … → x2` (teto); inatividade curta reseta. Sem spam forçado.
- **Autoclick (§25):** com o tempo o idle assume; o clique segue útil no início
  de runs, em eventos e em boosters.
- **Upgrades de clique (§26):** progressão temática de 10 níveis
  (Dedo Cansado → Grupo da Família no Zap → … → O Gigante Finalmente Acordou).
  Cada nível muda número + um pequeno elemento visual + descrição humorística.

---

## 8. Produtores = missões por mapa (§27–§30)

- **10 missões únicas × 4 mapas = 40 missões temáticas.** Os 4 mapas operam
  **em paralelo**: produção, ciclos e melhorias enxergam o conjunto todo; a
  Sede exibe o mapa ativo selecionável na faixa.
- **Fórmula base (§28):**
  - `Cost(n) = BaseCost × GrowthRate^Owned`
  - `Production = BaseProduction × Owned × Multipliers`
- **Buy modes (§29):** `x1 x10 MAX` (custo sempre exibido).
- **Milestones (§30)** por missão em `10, 25, 50, 100, 250, 500, 1000`
  (bônus ex.: ×2 produção; mudanças maiores em milestones específicos).
- **Progressão entre mapas:** a 1ª missão do mapa seguinte custa mais que a
  última do anterior (Deep Web 25,8 B → Democracia Relativa 309,6 B → Ratanabá
  19,17 Se → Religião 1,187 Vg); razão ×12 contínua, fluida como a referência.

### Mapa 1 — Deep Web (§31, imagem: porão improvisado, CRTs, cabos, quadros de barbante)

Custos na faixa da referência: 12 → 25,8 B.

1. Comprar as maiores empresas com cripto
2. Plantar fake news na mídia
3. Fazer amizade com os reptilianos
4. Colocar um informante no governo
5. Fomentar teorias da conspiração
6. Lavar o cérebro de artistas pop
7. Começar guerras por lucro
8. Controlar mentes através do Wi-Fi
9. Manipular governantes fantoches
10. Gerenciar sistemas de controle do clima

### Mapa 2 — Democracia Relativa (§32, sátira fictícia, sem candidatos reais)

Política é show: pesquisas encomendadas, sósias eleitos e a Constituição do Zap.

1. Comprar o voto do tio do grupo
2. Encomendar a pesquisa que prova o que a gente quer
3. Fundar o partido do meio-termo
4. Espalhar a emenda "totalmente pública"
5. Sessão plenária com robôs no contra-turno
6. Cabo eleitoral com megafone na praça
7. Comício com promessas em formato de dupla
8. Escrever a "Constituição do Zap"
9. Eleger um sósia por procuração
10. Proclamar a Democracia Relativa™

### Mapa 3 — Ratanabá (§33, a cidade secreta que todo mundo já viu no mapa)

1. Escavar a entrada da cidade subterrânea
2. Ativar o Wi-Fi da cidade invisível
3. Contratar o cartógrafo que viu o mapa
4. Comprar terreno na capital oculta
5. Vender excursão para o subsolo
6. Abrir o consulado de Ratanabá
7. Exportar ouro dos incas por Sedex
8. Eleger o prefeito do nada
9. Imprimir a moeda de Ratanabá
10. Revelar a entrada oficial (com catraca)

### Mapa 4 — Religião (§34, sátira de vigaristas, sem ofender a fé de ninguém)

1. Fundar o templo da fé com cashback
2. Transmitir o sermão em 8K com IA
3. Autenticar a relíquia "do milênio"
4. Vender a água da torneira abençoada
5. Adiar o apocalipse (de novo)
6. Bingo solidário do juízo final
7. Restaurar a imagem que "chora" xarope
8. Comandar o retiro do arrepio garantido
9. Redescobrir o 13º mandamento (no áudio)
10. Abrir a filial no céu

---

## 9. Mapas e transições (§35–§37)

| Mapa | Nome | Desbloqueio (missão final do anterior) | Transição cinematográfica |
|---|---|---|---|
| 1 | Deep Web | Inicial | — |
| 2 | Democracia Relativa | concluir "Gerenciar sistemas de controle do clima" | urna confete estourando |
| 3 | Ratanabá | concluir "Proclamar a Democracia Relativa™" | mapa se redesenha sozinho |
| 4 | Religião | concluir "Revelar a entrada oficial" | catraca dourada se abre |

- Navegação por **faixa horizontal** no topo (nome do mapa ao centro, ◀/▶ nas
  pontas); revisitar mapas concluídos é permitido. Navegação linear: cada mapa
  abre ao concluir a missão final do anterior.
- Desbloqueio deve parecer **monumental**, não um número arbitrário (§35).
- A Sede muda por completo de fundo/iluminação/objetos/VFX/sons/produtores,
  preservando a UX (§37).

---

## 10. Coordenadores (automação) (§38–§42)

**40 Coordenadores** (um por missão; 4 mapas × 10), com silhueta, personalidade,
expressão, idle anim, descrição, **frase de contratação** e **frase de upgrade**
próprias (§39). Definidos data-driven em `src/content/managers.json` (ex.: CEO
Invisível, Editor de Manchetes, Embaixador Escamoso, Pastor do Cashback…).

**Zé do Chapéu de Alumínio** (§40): Coordenador especial que desbloqueia
**COMPRAR TUDO**. Frase: *"Eu já sabia que você ia clicar."*

Regras (§41–§42): antes do Coordenador o produtor exige coleta/tap; depois,
produção automática (conquista perceptível). Coordenadores têm nível que melhora
velocidade/produção/milestones — progressão simples no início.

---

## 11. Laboratório de Sósias (§43–§49)

- Tela própria: laboratório clandestino, tanques, líquido verde/amarelo neon,
  vidros, monitores CRT.
- **Sósias**: colecionáveis que fortalecem produtores. Raridades: COMUM ×5,
  INCOMUM ×10, RARO ×50 (ÉPICO/LENDÁRIO só se a economia justificar — §44/§45).
- **Reveal (§46):** tanque fechado → 1º toque racha → 2º luzes → 3º abre
  (drama). 
- **Duplicatas (§47):** viram **Puxa-Sacos**, que aumentam eficiência
  permanentemente (valor da duplicata sempre claro).
- **Catálogo (§49):** coleção com `????` até desbloquear; depois portrait, nome,
  raridade, bônus, produtor afetado e lore.
- **Probabilidades transparentes** se abrir for comprável (§68/§154) + **pity**
  (§155).

---

## 12. Zap Vazado (§50–§56)

- Notificação com mensagem suspeita; decisão binária **APROVAR / NEGAR** —
  dentro da lógica da sociedade secreta: **PUBLICAR** ou **MANTER SIGILO**
  (não existe "fact-checking real").
- Ex.: "A tia do grupo diz que a Lua mudou de CEP." → criar **centenas**.
- **Medidor de Desconfiança Pública:** escolhas ruins aumentam; cheio = pequena
  penalidade temporária; baixo = bônus; nada de perda irrecuperável (§53).
- **Streak:** acertos consecutivos (1/2/3/5/10…) aumentam recompensa (§54).
- **Recompensas:** Mentes, Chumbo, boost temporário, fragmentos de Sósia (§55).
- **Data model (§56):** `id, headline, body, categoria, fase, respostaCertagurada,
  recompensa, raridade, tags` → centenas sem código novo.

---

## 13. Prestígio — Despertar o Gigante (§57–§63)

- Reseta a run e entrega **Convictos**.
- Confirmação clara (nunca reset acidental); preview de Convictos e do bônus.
- **Fórmula (§59):** `Convictos = floor((LifetimeMentes / Limiar)^Expoente)`
  → calibrada em `sim/`.
- **Nota de nomenclatura:** o "lifetime" da fórmula corresponde às Mentes
  acumuladas na vida (antiga denominação "Crédulos" foi substituída; saves
  continuam compatíveis).
- **Bônus hipótese (§60):** `+3% produção global por Convicto` (multiplicativo),
  validado no simulador para evitar runaway impossível.
- **Maçonaria Nacional (§61–§63):** tela de árvore de prestígio — sociedade
  totalmente inventada nesta ficção. Ramos: **PROPAGANDA, TECNOLOGIA, SÓSIAS,
  PRODUTORES, ZAP, OFFLINE, PRESTÍGIO**. Upgrades permanentes com efeito claro
  (ex.: "Servidor Debaixo da Escada", "Backup em Disquete").

---

## 14. As 9 telas principais (§64–§75)

1. **Sede Secreta** — Home: Mentes, Chumbo, produção/seg, botão Compartilhar,
   produtores do mapa ativo, faixa de mapas no topo, atalhos, eventos.
2. **Coordenadores** — dossiês das missões do mapa ativo (portrait, nome, produtor, status, nível, bônus, custo).
3. **Laboratório de Sósias** — tanque central, Chumbo, abrir, coleção, probabilidades.
4. **Zap Vazado** — smartphone fictício, conversa, APROVAR/NEGAR.
5. **Maçonaria Nacional** — sala secreta, mesa, arquivos, símbolos fictícios.
6. **Loja de Melhorias** — categorias: Clique, Global, Produtores, Offline, Eventos.
7. **Mapa da Dominação** — estilizado: Deep Web → Democracia Relativa → Ratanabá → Religião. A troca rápida de mapa ativo vive na **faixa horizontal** no topo (◀/▶).
8. **Loja de Chumbo** — compra de premium, clara/rápida/não manipulativa.
9. **Arquivo Secreto** — achievements, lore, coleção, estatísticas (pasta confidencial).

**Navegação (§75):** barra inferior com **máx. 5 acessos principais**; demais
via menus contextuais. Sede sempre a 1 tap. Modais ≠ telas principais.

---

## 15. Sistemas de meta & progressão longa

### Offline & relógio (§86–§89)
- Produção continua offline (produtores com automação). Volta com relatório:
  *"Enquanto você estava desconectado, a operação convenceu X."*
- Limite inicial 2–4h, upgrades até 8h/12h/24h.
- **DUPLICAR RELATÓRIO** (rewarded = 2× offline).
- Proteção de relógio: detectar manipulação grosseira, sem punir falso positivo.

### Daily/Streak (§90–§91)
- Maleta secreta de 7 dias (Mentes → boost → Chumbo → … → dossiê no dia 7).
- Streak com **1 recuperação semanal** (nunca zerar bruto).

### Missões (§92–§93)
- Diárias: compartilhar 100×, comprar 50 produtores, abrir 1 Zap, ganhar X, upgrade.
- Semanais: 30 Zaps, 3 prestiges, comprar 500 produtores.

### Achievements (§94–§96)
- ≥60 no lançamento, sistema preparado p/ 300+; secretos (ex.: clicar 100× no
  ET decorativo); recompensas pequenas.

### Coleções & Dossiês (§97–§98)
- Colecionar Sósias, documentos, fitas, OVNIs, objetos suspeitos.
- Cada teoria tem card (nome fictício, categoria, fase, lore satírico) podendo
  marcar `lenda urbana / paródia / ficção`.

### Narrativa fragmentada (§99–§102)
- Sem cutscenes longas; história via dossiês/mensagens/upgrades/eventos/frases.
- **O ARQUIVISTA**: narrador de rosto nunca revelado, humor seco, explica
  sistemas, quebra a 4ª parede.
- **AGÊNCIA DO ÓBVIO**: rival fictícia que tenta desmentir tudo.

### Endgame & New Game+ (§84–§85)
- Após a Religião, twist: **A VERDADEIRA CONSPIRAÇÃO ERA VOCÊ** — a organização
  descobre estar dentro de um idle game (quebra da 4ª parede).
- Desbloqueia **ARQUIVO Ω** (multiplicador/endless mode) sem apagar conteúdo.

---

## 16. Economia & calibragem (§76–§83)

- Ritmo alvo: crescimento rápido → desaceleração → prestige → explosão → repete.
- Curvas: custos exponenciais; produção com multiplicadores em milestones;
  prestige em picos; Sósias em saltos específicos.
- **Economy Simulator obrigatório** (ver `sim/` e `ECONOMY.md`) com perfis
  casual/médio/hardcore/payer e horizontes 1h/1d/7d/30d/90d.
- Metas: responder quando acontecem 1º produtor, 1º Coordenador, 1º Sósia,
  1º prestige, Fases 2/3/4. **1º prestige no dia 1** (hipótese, calibrar).

Detalhamento do simulador e resultados atuais: `ECONOMY.md`.

---

## 17. FTUE & disclosure progressivo (§123–§128)

- **Primeiros 60s:** sem loja, sem anúncio, sem excesso de menus.
- **1º minuto:** Compartilhar → Mentes → 1º produtor → gera → 2º produtor → recompensa grande.
- **5 min:** click, producer, upgrade, produção/seg. (sem Sósias ainda).
- **1ª hora:** Coordenador, Zap Vazado, offline.
- **1º dia:** Prestige, Laboratório de Sósias.
- Menus bloqueados mostram `???` (curiosidade) (§128).

---

## 18. MVP / milestones de entrega (§246–§254, §324–§331)

| Milestone | Conteúdo | Status |
|---|---|---|
| M0 — Playable Core | Sede, Zap, Mentes, produção/s, 4 produtores, x1/x10/MAX, milestones, save, offline, UI, SFX, analytics básico | ✅ |
| M1 — Vertical Slice | 10 missões Deep Web, Coordenadores, Zap completo, 1 fluxo de Sósia, prestige, Arquivo, arte quase final, áudio, VFX | ✅ |
| M2 — Alpha | campanha por mapas (Deep Web → Democracia Relativa → Ratanabá → Religião), collection, achievements, offline, ads test | ✅ |
| M3 — Beta | 4 mapas rodando em paralelo, 9 telas, economia completa, LiveOps | ⏳ |
| M4 — Soft Launch | dados reais; sem spec grande sem dados | ⏳ |
| M5 — V1.0 | conteúdo completo + polimento + publicação | ⏳ |

---

## 19. Prioridades absolutas (§316–§317)

1. Core divertido → 2. Retenção → 3. Economia → 4. Polimento → 5. Estabilidade
→ 6. Monetização → 7. Volume de conteúdo.

Nunca sacrificar retenção por receita D0: se um anúncio derrubar D7, ele sai.

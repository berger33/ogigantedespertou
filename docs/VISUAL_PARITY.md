# Paridade Visual (Visual Parity) — build web

Este arquivo é o **checklist vivo** do que a interface deve replicar da referência de
gênero **apenas em estrutura/posição/ritmo**. Conteúdo é sempre original do
O GIGANTE DESPERTOU (nunca copiar ativos da referência).

> **2026-09-21 — estudo quadro-a-quadro do gameplay real** consolidado em
> [`VISUAL_IMPLEMENTATION_PLAN.md`](VISUAL_IMPLEMENTATION_PLAN.md). Novos itens de
> checklist (extraídos dos frames) marcados abaixo com 🎞.

## Descobertas novas do vídeo (🎞 — a implementar nos lotes A/B)

### Cartão de produtor (anatomia medida)
- [ ] Cena pintada **grande** (~55% do card; card ≈ 34% da tela) 🎞
- [ ] Pill de nome escuro, 2 linhas, sobrepondo topo-esq da cena 🎞
- [ ] Placa metálica de 5 estrelas (silhueta → bronze → prata → ouro) + contador 🎞
- [ ] Barra-overlay de ciclo ciano (`00:06 → valor`) sobre a cena 🎞
- [ ] Placa de renda amarela listrada com ícone dourado 🎞
- [ ] Botão-preço chanfrado grosso à direita 🎞
- [ ] Tanque de sósia circular na borda **esquerda** do card 🎞
- [ ] Estado travado = placa cinza lisa "Unlock" + estrelas-sombra 🎞

### Chrome & floaters
- [ ] Floaters fixos na **borda direita** (prancheta, fone, oferta, presente) com timers 🎞
- [ ] Cronômetro de boost na **borda esquerda** na altura da lista 🎞
- [ ] 4 abas-pasta na base (menu reduzido; demais itens viram floaters/ícones) 🎞
- [ ] Banner do QG pintado animado (2–4 quadros + parallax leve) 🎞
- [ ] Modal creme **spring-pop** (scale .85→1.04→1, 240 ms; dim 60%) 🎞
- [ ] Botões ✓ verde / ✗ vermelho chanfrados pseudo-3D + botão madeira 🎞
- [ ] Fonte display toon com outline (Bangers) nos contadores/títulos 🎞

### Juice (VFX)
- [ ] Burst de 5–8 figuras douradas na coleta (arco + rotação + fade, ~800 ms) 🎞
- [ ] Chuva de estrelas douradas grandes ao subir estrela (~1 s) 🎞
- [ ] Sparkle ✦ twinkle nos cards recém-upgradados 🎞
- [ ] Prestígio monumental: shake + flash + sequência de frames (~2,5 s) 🎞

---

## HUD superior
- [x] ⚙️ Config no canto **sup. esquerdo** (sempre visível)
- [x] Barra de moedas ao centro (principal / prestígio / premium)
- [x] 📳 Botão de telefone no canto **sup. direito** (badge + sheet)
- [x] Fone treme periodicamente quando há novidade

## Tela principal
- [x] Área de clique central com animação (Compartilhar no Zap)
- [x] Botão redondo grande de clique no centro do menu inferior
- [x] Lista de produtores logo abaixo (cards emoldurados)
- [x] Mentes/s (pps) + combo viral em linha discreta
- [x] Upgrade de clique como faixa expansível

## Card de produtor (paridade de referência)
- [x] Nome + sabor (lore original)
- [x] ★ Classificação (bronze → prata → ouro) no canto sup. direito
- [x] ⏱ Timer de ciclo no canto inf. esquerdo (tende a 0s com Coordenador)
- [x] 🛠 Botão de upgrade no canto inf. direito
- [x] 🧫 Tanque de sósia (cinza = vazio; colorido = ocupado)
- [x] x1 / x10 / MAX

## Menu inferior (registro)
- [x] ⏱️ Cronômetro permanente no canto **inf. esquerdo** (boost ×2 stack)
- [x] Botão central grande (clique)
- [x] Botões de menu à direita, ordem próxima da referência
- [x] Desbloqueio progressivo (Chefes → Sósias → Gigante) com cadeado

## Prestígio
- [x] Dois caminhos: bomba grátis (reset) e lealdade premium (mantém)
- [x] Prévia de Convictos
- [x] Animação de "acordar" (substitui a pirâmide rachando a Terra)

## Bônus de anúncio (simulados)
- [x] Time warp 2h / 4h
- [x] ×5 por 260s
- [x] ×2 empilhável (cronômetro)
- [x] Offline ×2 ("Bem-vindo de volta!")
- [x] +50% Convictos no próximo Despertar

## Termos espelhados (nosso nome / referência)
- Comprar tudo = buy all (desbloqueado por gerente especial)
- Zap Vazado = wiretaps (aprovar/negar)
- Sósias = clones (tanque, raridades, duplicata→bônus)
- Convictos = faltaeys (+3% cada)
- Chumbo = diamantes (premium)
- Despertar o Gigante = brainwashing (prestígio)

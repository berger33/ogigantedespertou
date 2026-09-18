# PRIVACY.md — O GIGANTE DESPERTOU

> Privacidade e conformidade (§161–§163, §261, §310).

---

## 1. Princípios

- **Offline-first:** o core (jogar, progredir, prestigiar) funciona sem conta e
  sem internet (§193).
- **Nenhum PII coletado no núcleo** (§178): nunca nome, telefone, e-mail ou
  conteúdo real de mensagens. O "Zap" é totalmente **fictício** interno ao jogo.
- Dados de analytics são eventos agregados de gameplay + parâmetros técnicos
  (ids internos de conteúdo), nunca identificadores pessoais.

## 2. Consentimento e SDKs (§161–§162)

- Consentimento de publicidade via **UMP (Google)** quando aplicável, **antes**
  de carregar anúncios onde exigido (EEA etc.), com fallback para áreas sem
  exigência.
- Data safety no Google Play: declarar tipos de dados coletados, uso e
  compartilhamento.
- SDK disclosure: Firebase Analytics, Crashlytics, AdMob (e integrações
  futuras) listadas.

## 3. Classificação etária (§163)

- O jogo **não é apresentado como infantil**; preencher **IARC** conforme o
  conteúdo real (humor adulto, sem violência gráfica).

## 4. Recursos obrigatórios

- Privacy policy (URL pública) — modelo a publicar antes do release.
- FAQ + contato de suporte (§285): Ajuda, FAQ, Contato, versão/build, Player ID.
- **Diagnostic export** sem PII (§286).
- **Reset account** com confirmação forte (§287).
- **Restore purchases** (§288).
- Settings (§289): Music, SFX, Haptics, Notifications, Number format, Language,
  Privacy.

## 5. Notificações (§279–§281)

- Push moderado; solicitar permissão **após demonstrar valor**, nunca no 1º
  segundo.
- Exemplos: "👁 Seus produtores convenceram gente demais enquanto você estava
  fora." / "🛸 O laboratório terminou um Sósia." / "📱 Tem Zap Vazado esperando."

## 6. Anti-cheat & segurança (§206–§208, §292)

- IAP validado no servidor/Play; premium nunca confiável só pelo cliente.
- Anti-cheat proporcional (premium, ranking, IAP). Sem coleta invasiva.

## 7. Checklist pré-release (§262)

- Privacy policy publicada; data safety preenchido; IARC preenchido; SDKs
  declarados; consent flow ativo.

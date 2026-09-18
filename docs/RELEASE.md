# RELEASE.md — O GIGANTE DESPERTOU

> Roteiro de publicação e operação pós-lançamento (§224–§261, §309–§310).

---

## 1. Antes de publicar (google play)

- [ ] AAB assinado; target API vigente (rever no dia).
- [ ] Data safety form preenchido; IARC classificado; privacy policy pública.
- [ ] SDK disclosure (Firebase, Crashlytics, AdMob/mediation).
- [ ] Store listing: ícone, feature graphic, screenshots, descrição satírica
      ("construa a organização secreta mais absurda do Brasil").
- [ ] ASO auditado (idle, clicker, incremental, tycoon, Brasil, humor, simulação;
      **sem** marcas de concorrentes).
- [ ] Trailer 20–30s (estrutura §230) + 5 famílias de criativos (§231–§236),
      **sem fake gameplay**.
- [ ] Store policy audit (§261) + legal/IP audit (§262) + license inventory (§263).

## 2. Sequência de lançamento (§238–§253)

Soft launch (público pequeno) → checklist (§239: crash, FTUE, retention,
economia, ads, IAP, prestige, events) → análise → polimento → lançamento.

## 3. Staged rollout & flags (§299–§300)

Atualizações importantes liberadas progressivamente (se o canal permitir);
feature flags por sistema para rollback rápido.

## 4. Pós-lançamento (§255–§256)

| Momento | Ação |
|---|---|
| Semana 1 | hotfix |
| Semana 2 | economy tuning (Remote Config) |
| Mês 1 | primeiro evento novo |

Cadência fixa: Zap frequente; evento semanal/quinzenal; conteúdo grande mensal.

## 5. Relatório de entrega (§309)

Arquitetura, features, assets, economia, monetização, analytics, LiveOps,
performance, bugs conhecidos, publicação, roadmap.

## 6. Checklist de entrega ao cliente (§310)

- [ ] projeto Unity completo + source
- [ ] AAB + APK de teste
- [ ] assets fonte
- [ ] documentação (docs/)
- [ ] economy data (sim/ + content JSON)
- [ ] analytics schema (ANALYTICS.md)
- [ ] Remote Config defaults
- [ ] store assets
- [ ] privacy docs

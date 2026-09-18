# BUILD.md — O GIGANTE DESPERTOU

> Como compilar, gerar builds e versionar (§10–§11, §210–§214, §224).

---

## 1. Visão

O repositório mantém o **núcleo lógico engine-agnóstico** (JS testado + espelho
C#). A build de produção é Unity/C# para Android (AAB). A compilação nativa
exige máquina com **Unity Editor + .NET + Android SDK/NDK** (não disponíveis
neste sandbox de desenvolvimento — ver `00_AUDIT.md` §2).

## 2. Build web (núcleo jogável de referência)

```bash
npm test          # testes
npm run sim       # gera sim/report.md
npm run serve     # http://localhost:8000 (canvas da Sede Secreta)
```

Sem dependências externas; rode com qualquer Node ≥18.

## 3. Build Unity/Android (produção)

1. Abrir a pasta `unity/` em **Unity 6.x LTS**.
2. Portar a camada UI (os módulos `Core/*` são 1:1 com `src/core/`).
3. `Player Settings`: portrait; target API 35+/36 (conforme exigência vigente
   na publicação — rever!); minSdk conforme matriz de dispositivos.
4. **Signing**: keystore fora do repo (variáveis de ambiente/`secrets/`).
5. Gerar **AAB** para Google Play + APK de teste interno.
6. Ativar: multidex (nativo), IL2CPP Liberação, ARM64, R8/ProGuard conforme SDKs.

## 4. Versionamento (§213)

Semântico: `MAJOR.MINOR.PATCH` + build incrementado (ex.: `1.0.0 (100)`).
CI/CD automatiza testes → build → versionamento quando viável.

## 5. Segredos (§214)

Nunca commit: `keystore password`, `API secrets`, `production keys`,
`google-services.json`, `GoogleService-Info.plist`. Todos já no `.gitignore`.

## 6. Checklist de release (§224–§228, §310)

AAB, target API, signing, data safety, IARC, ícone (48px), feature graphic,
screenshots, store description (tom satírico), ASO sem trademarks de
concorrentes, trailer 20–30s.

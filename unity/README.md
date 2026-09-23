# Pasta `unity/` — espelho C# (Unity-ready)

Esta pasta contém a porta **1:1** do núcleo de regras (engine-agnóstico) para
**Unity 6.x LTS / C#**. A fonte de verdade do comportamento é `src/core/*` (Node)
validada por `tests/`; os arquivos `.cs` aqui expõem a **mesma API/semântica** e
devem reproduzir os mesmos testes (NUnit) quando importados no projeto Unity.

## Como usar

1. Crie um projeto Unity (6.x LTS) e copie esta pasta para `Assets/ODespertou/Core/`.
2. Adicione `using ODespertou.Core;`.
3. Use `BigNumber` para toda a economia; `Economy.*` para custos/buy modes;
   `Prestige.*` para Convictos; `SaveUtil.*` para serialização com hash.
4. Conteúdo estático (`producers.json` etc.) vira **ScriptableObject** gerados a
   partir dos mesmos JSONs de `src/content/` (spec §14) — não duplicar valores.

## Estado atual

| Arquivo | Espelha | Status |
|---|---|---|
| `BigNumber.cs` | `src/core/BigNumber.js` | ✅ |
| `Economy.cs` | `src/core/Economy.js` | ✅ |
| `Prestige.cs` | `src/core/Prestige.js` | ✅ |
| `Save.cs` | `src/core/Save.js` | ✅ (serialização + hash) |
| `GameState.cs` | `src/core/GameState.js` | ⏳ próximo milestone |

## Aviso

A build nativa (AAB/APK) exige máquina com **Unity Editor + .NET/Android SDK**
(não disponíveis no sandbox de desenvolvimento). Ver `docs/BUILD.md` e
`docs/00_AUDIT.md` §2.

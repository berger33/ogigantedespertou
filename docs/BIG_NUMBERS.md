# BIG_NUMBERS.md — O GIGANTE DESPERTOU

> Sistema de números gigantes (§20–§21). Implementação `src/core/BigNumber.js` e
> espelho `unity/BigNumber.cs`.

---

## 1. Por que um sistema dedicado

Idle games alcançam ordens de magnitude que estouram (ou corrompem por precisão)
qualquer `double`/`float` puro na economia tardia. A especificação exige (§20–§21):

- não depender de `float`/`double` puro para economia tardia;
- suportar ordens absurdamente altas;
- exibição brasileira (`1 mil`, `1 milhão`, `1 trilhão`…);
- notação científica/engenharia configurável;
- **nunca permitir overflow silencioso**.

## 2. Representação

```
valor = mantissa × 10^expoente      mantissa ∈ (-10, 10) \ {0}, expoente ∈ ℤ
```

- A mantissa cabe com folga num `double` (precisão relativa ~1e-15).
- O expoente é inteiro ilimitado (com teto defensivo `MAX_EXP = 1e6`).
- Multiplicação/divisão somam/subtraem expoentes → não há estouro de faixa.
- Adição/subtração alinham expoentes; diferença > 17 despreza o menor operando
  (abaixo da precisão relativa da mantissa).
- `pow(n)` é calculado em **espaço logarítmico** (`10^(n·log10|v|)`), então não
  estoura mesmo para expoentes enormes — essencial para bônus de prestígio.

### Operações suportadas
`add, sub, mul, div, pow(int≥0), scale, neg, floor, ceil, min, max, cmp`
(`eq/gt/gte/lt/lte`), `log10`, `.format(mode)`, serialização `toJSON/fromJSON`.

## 3. Formatos de exibição (§21)

| Modo | Exemplo |
|---|---|
| `full` | `1,5 mil`, `2,5 milhões`, `1 trilhão` |
| `short` | `4,2 mil`, `1,5 M`, `2,5 B`, `12,3 Qa` |
| `scientific` | `4,2e3`, `1e120` |

- Decimal usa vírgula; milhar usa ponto (padrão BR).
- Singular/plural correto (`1 milhão` / `2 milhões`; "mil" invariável).
- Acima da faixa nomeada (~decilhão / `1e33`), cai automaticamente em
  `scientific` — sem código especial por estágio.

### Nomes (escala curta, pt-BR)
`mil (10³), milhão (10⁶), bilhão (10⁹), trilhão (10¹²), quatrilhão (10¹⁵),
quintilhão (10¹⁸), sextilhão (10²¹), septilhão (10²⁴), octilhão (10²⁷),
nonilhão (10³⁰), decilhão (10³³)`.

Abreviações: `mil, M, B, T, Qa, Qi, Sx, Sp, Oc, No, Dc`.

## 4. Contrato portável

- `src/core/BigNumber.js` (Node/web) e `unity/BigNumber.cs` (C#) expõem a **mesma
  API pública** e a mesma semântica; o comportamento é cravado em
  `tests/BigNumber.test.js`. A porta C# deve reproduzir esses testes (NUnit).

## 5. Regras de segurança

- `new BigNumber(NaN/∞)` → erro explícito.
- Divisão por zero → erro explícito.
- `pow` com expoente negativo → erro explícito.
- `fromString` inválida → erro explícito.
- Nenhuma operação retorna calculadamente `Infinity` sem lançar.

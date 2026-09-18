/**
 * BigNumber — representação de números gigantes para economia de idle.
 *
 * Registro (mantissa, expoente) em base 10:
 *   value = mantissa * 10^exp, mantissa em (-10, 10) \ {0}, exp inteiro.
 *
 * Motivação (spec §20–§21): não depender de float/double puro para a economia
 * tardia — a mantissa cabe em double e o expoente é inteiro, então NÃO há
 * overflow silencioso na faixa útil do jogo. Overflow detectável vira erro
 * explícito (nunca silencioso).
 *
 * API pública == espelho C# em `unity/BigNumber.cs` (porta 1:1).
 */

/** Limite máximo de expoente (defensivo; nunca deve ser atingido pelo game). */
export const MAX_EXP = 1000000;

// Nomes brasileiros (escala curta), por expoente.
const FULL_NAMES = {
  3: 'mil',
  6: 'milhão',
  9: 'bilhão',
  12: 'trilhão',
  15: 'quatrilhão',
  18: 'quintilhão',
  21: 'sextilhão',
  24: 'septilhão',
  27: 'octilhão',
  30: 'nonilhão',
  33: 'decilhão',
};

// Abreviações, por expoente (grupo de 3).
const SHORT_NAMES = {
  3: 'mil',
  6: 'M',
  9: 'B',
  12: 'T',
  15: 'Qa',
  18: 'Qi',
  21: 'Sx',
  24: 'Sp',
  27: 'Oc',
  30: 'No',
  33: 'Dc',
};

/** Pluraliza nomes terminados em "lhão" → "lhões"; "mil" é invariável. */
function pluralize(name) {
  if (name === 'mil') return name;
  if (name.endsWith('lhão')) return name.slice(0, -4) + 'lhões';
  return name;
}

/** Formata um valor [~1..999] com até 2 casas, vírgula decimal e sem zeros extras. */
function trimLead(value) {
  if (Math.abs(value - Math.round(value)) < 1e-9) {
    return Math.round(value).toString();
  }
  return value.toFixed(2).replace('.', ',').replace(/0+$/, '').replace(/,$/, '');
}

/** Agrupa inteiro com pontos de milhar (padrão BR). */
function intGroup(n) {
  return Math.floor(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

/** Igualdade com tolerância relativa (robustez a ruído de float). */
function close(a, b) {
  return Math.abs(a - b) <= 1e-12 * Math.max(1, Math.abs(a), Math.abs(b));
}

/**
 * Interpreta uma string numérica aceitando:
 *  - inteiro "1500"
 *  - decimal pt "1,5" ou en "1.5"
 *  - milhar pt "1.500" (ponto como separador de milhar)
 *  - notação "1.5e6" / "1,5e6" / "1500"
 */
function parseBrNumber(raw) {
  const num = raw.trim();
  // Notação científica: divide antes de interpretar a mantissa.
  const [mant, expPart] = num.toLowerCase().split('e');
  let mantissa;
  const hasThousands = /^\d{1,3}(\.\d{3})+$/.test(mant);
  if (hasThousands) {
    mantissa = parseFloat(mant.replace(/\./g, ''));
  } else if (mant.includes(',')) {
    // vírgula decimal pt ("1,5") — pontos seriam milhar, aqui só decimal
    mantissa = parseFloat(mant.replace(/\./g, '').replace(',', '.'));
  } else {
    mantissa = parseFloat(mant);
  }
  const exp = expPart !== undefined ? parseInt(expPart, 10) : 0;
  return { mantissa, exp };
}

export class BigNumber {
  /**
   * @param {number} m mantissa (pode ser negativa)
   * @param {number} e expoente inteiro (ex.: 1.5e6 => m=1.5, e=6)
   */
  constructor(m, e = 0) {
    m = Number(m);
    e = Number(e);
    if (!Number.isFinite(m) || !Number.isFinite(e)) {
      throw new Error('BigNumber: mantissa/expoente devem ser finitos (overflow explícito proibido)');
    }
    // normaliza mantissa para [-10,10) e expoente inteiro
    if (m === 0 || Math.abs(m) < 1e-300) {
      this.m = 0;
      this.e = 0;
      return;
    }
    while (Math.abs(m) >= 10) { m /= 10; e += 1; }
    while (Math.abs(m) < 1) { m *= 10; e -= 1; }
    if (Math.abs(e) > MAX_EXP) {
      throw new Error(`BigNumber: expoente ${e} excede o limite ${MAX_EXP} (overflow explícito proibido)`);
    }
    this.m = m;
    this.e = e;
  }

  static zero() { return new BigNumber(0, 0); }
  static one() { return new BigNumber(1, 0); }

  static fromNumber(n) {
    if (!Number.isFinite(n)) throw new Error('BigNumber: fromNumber recebeu valor não-finita');
    if (n === 0) return BigNumber.zero();
    return new BigNumber(n, 0);
  }

  /** Aceita "1500", "1.5e6", "1,5e6", "1.500". */
  static fromString(str) {
    const s = String(str).trim();
    if (s === '' || s === '0') return BigNumber.zero();
    const { mantissa, exp } = parseBrNumber(s);
    if (!Number.isFinite(mantissa)) throw new Error(`BigNumber: string inválida "${str}"`);
    return new BigNumber(mantissa, exp);
  }

  isZero() { return this.m === 0; }
  isNegative() { return this.m < 0; }
  sign() { return this.m < 0 ? -1 : this.m > 0 ? 1 : 0; }

  /** Compara contra outro; retorna -1/0/1. */
  cmp(other) {
    const sa = this.sign();
    const sb = other.sign();
    if (sa !== sb) return sa < sb ? -1 : 1;
    if (sa === 0) return 0; // ambos zero
    const ma = Math.abs(this.m), mb = Math.abs(other.m);
    const base = this.e === other.e
      ? (close(ma, mb) ? 0 : (ma > mb ? 1 : -1))
      : (this.e > other.e ? 1 : -1);
    return base * sa;
  }

  eq(o) { return this.cmp(o) === 0; }
  gt(o) { return this.cmp(o) > 0; }
  gte(o) { return this.cmp(o) >= 0; }
  lt(o) { return this.cmp(o) < 0; }
  lte(o) { return this.cmp(o) <= 0; }

  neg() { return new BigNumber(-this.m, this.e); }

  add(o) {
    if (this.isZero()) return o;
    if (o.isZero()) return this;
    if (this.e === o.e) return new BigNumber(this.m + o.m, this.e);
    const big = this.e >= o.e ? this : o;
    const small = this.e >= o.e ? o : this;
    const diff = big.e - small.e;
    if (diff > 17) return big; // desprezível abaixo da precisão de double
    return new BigNumber(big.m + small.m * Math.pow(10, -diff), big.e);
  }

  sub(o) { return this.add(o.neg()); }

  mul(o) {
    if (this.isZero() || o.isZero()) return BigNumber.zero();
    return new BigNumber(this.m * o.m, this.e + o.e);
  }

  scale(k) { return this.mul(BigNumber.fromNumber(k)); }

  div(o) {
    if (o.isZero()) throw new Error('BigNumber: divisão por zero');
    if (this.isZero()) return BigNumber.zero();
    return new BigNumber(this.m / o.m, this.e - o.e);
  }

  /** Potência com expoente inteiro não-negativo: (m·10^e)^n = m^n · 10^(e·n). */
  pow(n) {
    n = Math.floor(n);
    if (n < 0) throw new Error('BigNumber: expoente negativo não suportado');
    if (n === 0) return BigNumber.one();
    return new BigNumber(Math.pow(this.m, n), this.e * n);
  }

  floor() {
    if (this.isZero()) return BigNumber.zero();
    if (this.e >= 15) return this; // magnitude >= 10^15: inteiro para todos os efeitos (mantissa < 10)
    const n = this.toNumberSafe();
    return BigNumber.fromNumber(n === null ? 0 : Math.floor(n));
  }

  ceil() {
    if (this.isZero()) return BigNumber.zero();
    if (this.e >= 15) return this;
    const n = this.toNumberSafe();
    return BigNumber.fromNumber(n === null ? 1 : Math.ceil(n));
  }

  max(o) { return this.gte(o) ? this : o; }
  min(o) { return this.lte(o) ? this : o; }

  /** Converte para Number se couber com segurança inteira; senão null. */
  toNumberSafe() {
    if (this.isZero()) return 0;
    const v = this.m * Math.pow(10, this.e);
    if (Number.isFinite(v) && Math.abs(v) <= Number.MAX_SAFE_INTEGER) return v;
    return null;
  }

  /** Converte para Number aproximado (pode imprecisar em valores gigantes). */
  toNumber() {
    const v = this.toNumberSafe();
    if (v !== null) return v;
    return this.m * Math.pow(10, this.e);
  }

  /** log10 aproximado (para dashboards/curvas do simulador). */
  log10() {
    if (this.isZero()) return -Infinity;
    return Math.log10(Math.abs(this.m)) + this.e;
  }

  /**
   * Formata no modo pedido.
   * @param {'full'|'short'|'scientific'} mode
   */
  format(mode = 'short') {
    if (this.isZero()) return '0';
    const sign = this.m < 0 ? '-' : '';
    const am = Math.abs(this.m);
    const e = this.e;

    if (mode === 'scientific') {
      return `${sign}${trimLead(am)}e${e}`;
    }

    if (e < 3) {
      // números "pequenos": inteiro normal com pontos de milhar
      const n = this.toNumberSafe();
      if (n !== null) {
        const rounded = am * Math.pow(10, e);
        if (rounded < 1 && Math.abs(rounded) > 0 && e < 0) {
          return `${sign}${trimLead(rounded)}`;
        }
        return `${sign}${intGroup(n)}`;
      }
    }

    const group = Math.floor(e / 3) * 3;
    const lead = am * Math.pow(10, e - group);
    const leadStr = trimLead(lead);

    if (mode === 'short') {
      const abbr = SHORT_NAMES[group];
      if (!abbr) return this.format('scientific');
      return `${sign}${leadStr} ${abbr}`;
    }

    // full
    const name = FULL_NAMES[group];
    if (!name) return this.format('scientific');
    if (name === 'mil') return `${sign}${leadStr} mil`;
    const isSingular = Math.abs(lead - 1) < 1e-9;
    return `${sign}${leadStr} ${isSingular ? name : pluralize(name)}`;
  }

  /** Serialização para save (sem perda). */
  toJSON() { return { m: this.m, e: this.e }; }

  static fromJSON(obj) {
    if (!obj || typeof obj !== 'object') return BigNumber.zero();
    return new BigNumber(obj.m ?? 0, obj.e ?? 0);
  }
}

export default BigNumber;

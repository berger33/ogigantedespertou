// BigNumber — espelho C# (Unity-ready) de src/core/BigNumber.js
// Porta 1:1 da mesma semântica. Registro logarítmico (mantissa, expoente).
// Espec §20–§21: sem overflow silencioso — erros explícitos em operações inválidas.
using System;
using System.Globalization;

namespace ODespertou.Core
{
    public class BigNumberException : Exception
    {
        public BigNumberException(string message) : base(message) { }
    }

    public readonly struct BigNumber : IEquatable<BigNumber>
    {
        public const long MaxExp = 1000000L;
        public readonly double M; // mantissa, em (-10,10) \ {0}, ou 0
        public readonly long E;   // expoente inteiro

        public BigNumber(double m, long e)
        {
            if (double.IsNaN(m) || double.IsInfinity(m))
                throw new BigNumberException("BigNumber: mantissa inválida (overflow explícito proibido)");
            if (m == 0.0 || Math.Abs(m) < 1e-300) { M = 0.0; E = 0L; return; }
            while (Math.Abs(m) >= 10.0) { m /= 10.0; e += 1; }
            while (Math.Abs(m) < 1.0) { m *= 10.0; e -= 1; }
            if (Math.Abs(e) > MaxExp)
                throw new BigNumberException($"BigNumber: expoente {e} excede o limite {MaxExp}");
            M = m; E = e;
        }

        public static BigNumber Zero => new BigNumber(0, 0);
        public static BigNumber One => new BigNumber(1, 0);
        public static BigNumber FromNumber(double n) => n == 0 ? Zero : new BigNumber(n, 0);
        public static BigNumber FromString(string s)
        {
            s = (s ?? "").Trim().Replace(" ", "");
            if (s.Length == 0 || s == "0") return Zero;
            var parts = s.ToLowerInvariant().Split('e');
            var num = parts[0].Replace(",", ".");
            double value;
            if (num.Contains(".") && num.Contains(",") == false)
            {
                // "1.500" em pt-BR é 1500 → reinterpreta: remove pontos de milhar
            }
            else
            {
            }
            value = ParseBrNumber(parts[0]);
            long exp = parts.Length > 1 ? long.Parse(parts[1], CultureInfo.InvariantCulture) : 0L;
            return new BigNumber(value, exp);
        }

        private static double ParseBrNumber(string num)
        {
            // Aceita "1,5", "1500", "1.500,5"
            string t = num.Trim();
            bool hasComma = t.Contains(",");
            string normalized;
            if (hasComma)
            {
                normalized = t.Replace(".", "").Replace(",", ".");
            }
            else
            {
                normalized = t.Replace(",", "."); // "1.500" é mantido como está
            }
            return double.Parse(normalized, CultureInfo.InvariantCulture);
        }

        public bool IsZero => M == 0.0;
        public bool IsNegative => M < 0.0;
        public int Sign => M < 0 ? -1 : M > 0 ? 1 : 0;

        public int Cmp(BigNumber o)
        {
            int sa = Sign, sb = o.Sign;
            if (sa != sb) return sa < sb ? -1 : 1;
            if (sa == 0) return 0;
            double ma = Math.Abs(M), mb = Math.Abs(o.M);
            int baseCmp = E == o.E ? (ma == mb ? 0 : (ma > mb ? 1 : -1)) : (E > o.E ? 1 : -1);
            return baseCmp * sa;
        }

        public bool Eq(BigNumber o) => Cmp(o) == 0;
        public bool Gt(BigNumber o) => Cmp(o) > 0;
        public bool Gte(BigNumber o) => Cmp(o) >= 0;
        public bool Lt(BigNumber o) => Cmp(o) < 0;
        public bool Lte(BigNumber o) => Cmp(o) <= 0;

        public BigNumber Neg() => new BigNumber(-M, E);

        public BigNumber Add(BigNumber o)
        {
            if (IsZero) return o;
            if (o.IsZero) return this;
            if (E == o.E) return new BigNumber(M + o.M, E);
            var big = E >= o.E ? this : o;
            var small = E >= o.E ? o : this;
            long diff = big.E - small.E;
            if (diff > 17) return big;
            return new BigNumber(big.M + small.M * Math.Pow(10, -diff), big.E);
        }

        public BigNumber Sub(BigNumber o) => Add(o.Neg());
        public BigNumber Mul(BigNumber o) => (IsZero || o.IsZero) ? Zero : new BigNumber(M * o.M, E + o.E);
        public BigNumber Scale(double k) => Mul(FromNumber(k));

        public BigNumber Div(BigNumber o)
        {
            if (o.IsZero) throw new BigNumberException("BigNumber: divisão por zero");
            if (IsZero) return Zero;
            return new BigNumber(M / o.M, E - o.E);
        }

        public BigNumber Pow(long n)
        {
            if (n < 0) throw new BigNumberException("BigNumber: expoente negativo não suportado");
            if (n == 0) return One;
            var b = this; var r = One; var k = n;
            while (k > 0) { if ((k & 1) == 1) r = r.Mul(b); b = b.Mul(b); k >>= 1; }
            return r;
        }

        public double Log10() => IsZero ? double.NegativeInfinity : Math.Log10(Math.Abs(M)) + E;

        public string ToJson() => $"{{\"m\":{(M.ToString(CultureInfo.InvariantCulture))},\"e\":{E}}}";

        public override string ToString() => ShortFormat();

        public string ShortFormat()
        {
            if (IsZero) return "0";
            string sign = M < 0 ? "-" : "";
            double am = Math.Abs(M);
            long group = (E / 3) * 3;
            double lead = am * Math.Pow(10, E - group);
            if (group == 0) return sign + FormatLead(lead);
            if (group == 3) return sign + FormatLead(lead) + " mil";
            string[] shorts = { "", "", "", "", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc" };
            int idx = (int)(group / 3);
            if (idx >= shorts.Length) return Scientific();
            return sign + FormatLead(lead) + " " + shorts[idx];
        }

        public string Scientific()
        {
            if (IsZero) return "0";
            return (M < 0 ? "-" : "") + FormatLead(Math.Abs(M)) + "e" + E.ToString(CultureInfo.InvariantCulture);
        }

        private static string FormatLead(double v)
        {
            if (Math.Abs(v - Math.Round(v)) < 1e-9) return Math.Round(v).ToString(CultureInfo.InvariantCulture);
            string s = v.ToString("0.00", CultureInfo.InvariantCulture);
            s = s.TrimEnd('0').TrimEnd('.');
            return s;
        }

        public bool Equals(BigNumber o) => Eq(o);
        public override bool Equals(object obj) => obj is BigNumber b && Eq(b);
        public override int GetHashCode() => (M, E).GetHashCode();
    }
}

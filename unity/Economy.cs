// Economy — espelho C# (Unity-ready) de src/core/Economy.js
// Custos, produção, buy modes e milestones (spec §27–§30). Porta 1:1.
using System;

namespace ODespertou.Core
{
    public static class Economy
    {
        public static readonly int[] BuyModes = { 1, 10, 25, 100, -1 }; // -1 = MAX

        public static BigNumber BuyCost(double baseCost, double growthRate, long owned, long qty)
        {
            var baseBn = BigNumber.FromNumber(baseCost);
            var g = BigNumber.FromNumber(growthRate);
            var num = g.Pow(qty).Sub(BigNumber.One);
            var den = BigNumber.FromNumber(growthRate - 1);
            return baseBn.Mul(g.Pow(owned)).Mul(num).Div(den);
        }

        public static long MaxAffordable(double baseCost, double growthRate, long owned, BigNumber balance)
        {
            var baseBn = BigNumber.FromNumber(baseCost);
            var g = BigNumber.FromNumber(growthRate);
            var den = BigNumber.FromNumber(growthRate - 1);
            var budget = balance.Mul(den).Div(baseBn.Mul(g.Pow(owned))).Add(BigNumber.One);
            if (budget.Lte(BigNumber.One)) return 0;
            long n = (long)Math.Floor(budget.Log10() / Math.Log10(growthRate));
            long best = 0;
            for (long cand = Math.Max(0, n - 1); cand <= n + 1; cand++)
            {
                if (BuyCost(baseCost, growthRate, owned, cand).Lte(balance)) best = cand;
                else break;
            }
            return best;
        }
    }

    public class MilestoneDef
    {
        public long Count;
        public double Factor;
    }

    public static class Milestones
    {
        public static BigNumber Multiplier(MilestoneDef[] defs, long owned)
        {
            var mult = BigNumber.One;
            foreach (var d in defs) if (owned >= d.Count) mult = mult.Scale(d.Factor);
            return mult;
        }

        public static BigNumber Production(double baseProduction, long owned, MilestoneDef[] defs)
        {
            return BigNumber.FromNumber(baseProduction).Scale(owned).Mul(Multiplier(defs, owned));
        }
    }
}

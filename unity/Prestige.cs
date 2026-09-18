// Prestige — espelho C# (Unity-ready) de src/core/Prestige.js
// "Despertar o Gigante" (§57–§63): Convictos e bônus linear aditivo (§60).
using System;

namespace ODespertou.Core
{
    public class PrestigeParams
    {
        public string Threshold = "1e6";
        public double Exponent = 0.5;
        public double ConvictBonus = 0.03;
    }

    public static class Prestige
    {
        /// <summary>Convictos ganhos: floor((lifetime/threshold)^exponent).</summary>
        public static double ConvictosFrom(BigNumber lifetime, PrestigeParams p)
        {
            var baseBn = BigNumber.FromString(p.Threshold);
            if (lifetime.Lt(baseBn)) return 0;
            var ratio = lifetime.Div(baseBn);
            double logResult = ratio.Log10() * p.Exponent;
            if (logResult <= 0) return 0;
            double value = Math.Pow(10.0, logResult);
            return Math.Floor(value);
        }

        /// <summary>Bônus global: 1 + taxa × Convictos (linear aditivo, §60).</summary>
        public static BigNumber GlobalBonus(double convictos, PrestigeParams p)
        {
            return BigNumber.One.Add(BigNumber.FromNumber(p.ConvictBonus * Math.Max(0, Math.Floor(convictos))));
        }
    }
}

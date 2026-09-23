// Save — espelho C# (Unity-ready) de src/core/Save.js
// Serialização, versionamento e proteção contra corrupção (§170–§174, §301–§302).
using System;
using System.Text;

namespace ODespertou.Core
{
    public static class SaveUtil
    {
        public const int SaveVersion = 1;

        /// <summary>Hash FNV-1a 32 bits — integridade (não é criptografia).</summary>
        public static string Hash32(string input)
        {
            uint h = 0x811c9dc5;
            foreach (char ch in input)
            {
                h ^= (uint)ch;
                h = (uint)((h * 0x01000193) & 0xFFFFFFFF);
            }
            return h.ToString("x8");
        }

        /// <summary>Serializa com separador de hash `body\n#hash32`.</summary>
        public static string Serialize(string jsonBody)
        {
            return jsonBody + "\n#" + Hash32(jsonBody);
        }

        /// <summary>Valida hash; retorna true e o body, ou false.</summary>
        public static bool TryDeserialize(string raw, out string body)
        {
            body = null;
            if (string.IsNullOrEmpty(raw)) return false;
            int idx = raw.LastIndexOf("\n#", StringComparison.Ordinal);
            if (idx < 0) { body = raw; return true; }
            body = raw.Substring(0, idx);
            string hash = raw.Substring(idx + 2).Trim();
            return Hash32(body) == hash;
        }
    }
}

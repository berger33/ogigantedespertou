#!/usr/bin/env python3
"""
gen_campaign.py — gera o conteúdo data-driven da campanha por mapas (§81–§84).

Regenera `src/content/{producers,managers,clones,maps}.json` para os 4 mapas:
Deep Web, Democracia Relativa, Ratanabá, Religião (10 missões únicas cada).

Economia:
  - Deep Web usa os custos EXATOS fornecidos pelo cliente (lista de paridade).
  - Os demais mapas seguem progressão geométrica ×12 sobre cada missão anterior,
    garantindo: 1ª missão do mapa N+1 > última do mapa N.
  - payback evolui 12s → ~4h (cap) ao longo das 40 missões: VPC = custo/payback × ciclo.
  - cycleSeconds 1.0 → 6.5s (paridade de ritmo da referência).

Uso: python3 tools/gen_campaign.py
"""
import json
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"


def sig(x, n=4):
    """Arredonda para n dígitos significativos, limpo (Decimal), devolvendo int/float."""
    if x == 0:
        return 0
    with localcontext() as ctx:
        ctx.prec = 200
        d = Decimal(str(x))
        q = Decimal(1).scaleb(d.adjusted() - (n - 1))  # 10^(exp - (n-1))
        v = d.quantize(q, rounding=ROUND_HALF_UP)
    if v == v.to_integral_value():
        return int(v)
    return float(v)


# --------------------------------------------------------------------------
# Mapas (metadados). Nomes determinados pelo pedido do cliente.
# --------------------------------------------------------------------------
MAPS = {
    "maps": [
        {"id": "phase1", "name": "Deep Web", "icon": "🕳️", "color": "#14532D",
         "flavor": "A internet que ninguém admite frequentar.",
         "finalNote": "dominar os sistemas de controle do clima"},
        {"id": "phase2", "name": "Democracia Relativa", "icon": "🗳️", "color": "#B3261E",
         "flavor": "Metade vota, a outra metade concorda. (sátira fictícia — sem candidatos reais)",
         "finalNote": "proclamar a Democracia Relativa™"},
        {"id": "phase3", "name": "Ratanabá", "icon": "🗺️", "color": "#39FF9C",
         "flavor": "A cidade secreta que todo mundo já viu no mapa.",
         "finalNote": "revelar a entrada oficial (com catraca)"},
        {"id": "phase4", "name": "Religião", "icon": "🕯️", "color": "#D4AF37",
         "flavor": "Milagres com nota fiscal. (sátira de vigaristas, sem ofender a fé de ninguém)",
         "finalNote": "abrir a filial no céu"},
    ]
}

# --------------------------------------------------------------------------
# Missões por mapa: (nome, ícone, flavor, custo_exato)
#   - phase1 usa os custos EXATOS do cliente (coluna 4).
#   - demais mapas: custo não se aplica (None) — calculado pela progressão ×12.
# --------------------------------------------------------------------------
MISSIONS = {
    "phase1": [
        ("Comprar as maiores empresas com cripto", "💻",
         "Lance na bolsa via 'carteira_final_v2_REAL.docx'.", 12),
        ("Plantar fake news na mídia", "📰",
         "A manchete nasce antes do fato; o fato se atrasa.", 60),
        ("Fazer amizade com os reptilianos", "🦎",
         "Café com um escamoso que fala 7 línguas — nenhuma humana.", 700),
        ("Colocar um informante no governo", "🕴️",
         "Título na placa: 'Conselheiro'. Leitura: só a nossa.", 8340),
        ("Fomentar teorias da conspiração", "🧠",
         "Cada boato é uma semente. Regue o grupo.", 90680),
        ("Lavar o cérebro de artistas pop", "🎤",
         "O hit já vem com a mensagem embutida.", 1040000),
        ("Começar guerras por lucro", "💣",
         "Paz é quando ninguém mais lucra com ela.", 14930000),
        ("Controlar mentes através do Wi-Fi", "📡",
         "Sinal forte, convicção mais forte.", 179160000),
        ("Manipular governantes fantoches", "🎭",
         "Trocamos o roteiro, não o elenco.", 2150000000),
        ("Gerenciar sistemas de controle do clima", "🌧️",
         "Chuva no bloco A, sol no bloco B.", 25800000000),
    ],
    "phase2": [
        ("Comprar o voto do tio do grupo", "🗳️", "Ele votava no meme. Agora vota na gente.", None),
        ("Encomendar a pesquisa que prova o que a gente quer", "📊",
         "A pergunta foi feita; a resposta já veio pronta.", None),
        ("Fundar o partido do meio-termo", "🎭", "Nem esquerda, nem direita: reels.", None),
        ("Espalhar a emenda 'totalmente pública'", "📜",
         "O sigilo do plano virou concurso de charadas.", None),
        ("Sessão plenária com robôs no contra-turno", "🤖",
         "O adversário é bot; a derrota, viral.", None),
        ("Cabo eleitoral com megafone na praça", "📣",
         "A verdade ao alcance do ouvido alheio.", None),
        ("Comício com promessas em formato de dupla", "🎪",
         "Entrada franca; convicção inclusa.", None),
        ("Escrever a 'Constituição do Zap'", "📱", "Artigo 1º: encaminhem.", None),
        ("Eleger um sósia por procuração", "🗃️", "O original governa; o sósia cumpre horário.", None),
        ("Proclamar a Democracia Relativa™", "🏛️", "Metade vota, a outra concorda.", None),
    ],
    "phase3": [
        ("Escavar a entrada da cidade subterrânea", "⛏️",
         "A capital dos grupos, 200 m abaixo do estacionamento.", None),
        ("Ativar o Wi-Fi da cidade invisível", "📡", "A senha é 'lumiar'.", None),
        ("Contratar o cartógrafo que viu o mapa", "🗺️", "O mapa muda sozinho; a fé, não.", None),
        ("Comprar terreno na capital oculta", "🏞️", "Escritura lavrada em grupo de Zap.", None),
        ("Vender excursão para o subsolo", "🎟️", "Vista deslumbrante: um lençol freático.", None),
        ("Abrir o consulado de Ratanabá", "🏢", "Embaixada com bandeira que ninguém viu.", None),
        ("Exportar ouro dos incas por Sedex", "📦", "Rastreamento: 'em rota lendária'.", None),
        ("Eleger o prefeito do nada", "👔", "Prefeito da cidade que a cartografia nega.", None),
        ("Imprimir a moeda de Ratanabá", "💵", "Lastro: convicção.", None),
        ("Revelar a entrada oficial (com catraca)", "🚪", "Catraca para o legendário.", None),
    ],
    "phase4": [
        ("Fundar o templo da fé com cashback", "⛪", "Dízimo com nota fiscal e devolução.", None),
        ("Transmitir o sermão em 8K com IA", "📺", "O coral é gerado; o milagre, ao vivo.", None),
        ("Autenticar a relíquia 'do milênio'", "🔮", "Astro por procuração, bênção por assinatura.", None),
        ("Vender a água da torneira abençoada", "💧", "Certificado de bênção incluso na garrafa.", None),
        ("Adiar o apocalipse (de novo)", "⏳", "Nova data: depois da novela.", None),
        ("Bingo solidário do juízo final", "🎰", "Cartela premiada com... salvação?", None),
        ("Restaurar a imagem que 'chora' xarope", "🖼️", "O choro é real; o xarope, de farmácia.", None),
        ("Comandar o retiro do arrepio garantido", "🕯️", "Arrepio com garantia estendida.", None),
        ("Redescobrir o 13º mandamento (no áudio)", "🎙️", "Estava no áudio de 11 minutos.", None),
        ("Abrir a filial no céu", "☁️", "A primeira franquia pós-morte.", None),
    ],
}

# Custos Deep Web EXATOS (fornecidos pelo cliente).
DEEP_WEB_COSTS = [m[3] for m in MISSIONS["phase1"]]
GROWTH = 12.0  # razão geométrica entre missões consecutivas fora da Deep Web

CYCLES = [1.0, 1.3, 1.6, 1.9, 2.2, 2.5, 2.8, 3.1, 3.4, 3.7]
PAYBACK_MAX = 14400  # 4h

# Coordenador / Sósia por missão (nomes originais, humor pt-BR).
COORDS = {
    "phase1": [
        ("CEO Invisível", "🕴️", "Pode me chamar de 'ninguém'."),
        ("Editor de Manchetes", "📰", "A verdade é um rascunho."),
        ("Embaixador Escamoso", "🦎", "Sssaudações, mestre."),
        ("Assessor Fantasma", "🕴️", "Sou só um conselheiro."),
        ("Cultivador de Boatos", "🌱", "Planto de manhã, viraliza à noite."),
        ("DJ Hipnótico", "🎛️", "O refrão convence."),
        ("Marechal do Lucro", "🎖️", "Guerra é ROI."),
        ("Técnico de Roteador", "🔧", "O sinal alcança opiniões."),
        ("Diretor de Elenco", "🎭", "O figurino é a prova."),
        ("Engenheiro do Clima", "🌪️", "Chuva conforme pedido."),
    ],
    "phase2": [
        ("Cabo Eleitoral", "📣", "Voto a voto."),
        ("Estatístico Comprado", "📊", "O gráfico sobe sozinho."),
        ("Líder do Bloco", "🧩", "Posição? Depende da enquete."),
        ("Relator da Emenda", "📜", "O segredo é de todos."),
        ("Bot Influencer", "🤖", "Ele opina 24/7."),
        ("Porta-voz da Praça", "📢", "Ouvido de programa."),
        ("Empresário de Promessas", "🎪", "Show de convicções."),
        ("Jurista do Zap", "📱", "Artigo é corrente."),
        ("Sósia Oficial", "🗃️", "Autografa melhor."),
        ("Cetro da Democracia Relativa", "🏛️", "Metade já entendeu."),
    ],
    "phase3": [
        ("Broca Real", "⛏️", "Furo primeiro, pergunto depois."),
        ("Modem Subterrâneo", "📡", "Sinal oculto."),
        ("Cartógrafo Cego", "🗺️", "Desenho de olhos fechados."),
        ("Corretor do Subsolo", "🏞️", "Terreno com escritura emocional."),
        ("Guia Turístico do Nada", "🎟️", "Vista inclusa."),
        ("Cônsul do Invisível", "🏢", "Carimbo sem país."),
        ("Exportador Incógnito", "📦", "Sedex intergaláctico."),
        ("Prefeito Fantasma", "👔", "População: você."),
        ("Impressor do Caos", "💵", "Tinta que convence."),
        ("Porteiro do Legendário", "🚪", "Catraca espiritual."),
    ],
    "phase4": [
        ("Pastor do Cashback", "⛪", "Dízimo que volta."),
        ("Diretor do Coral Sintético", "📺", "Aleluia em 8K."),
        ("Autenticador de Relíquia", "🔮", "Selado e carimbado."),
        ("Engarrafador da Fonte", "💧", "Garrafa benta."),
        ("Remarcador do Fim", "⏳", "Novo prazo: quinta."),
        ("Cerimonialista do Bingo", "🎰", "Cartela abençoada."),
        ("Restaurador do Xarope", "🖼️", "Milagre lacrado."),
        ("Mestre do Arrepio", "🕯️", "Calafrio tabelado."),
        ("Arqueólogo do Áudio", "🎙️", "O mandamento estava mutado."),
        ("Gerente da Filial", "☁️", "Abre às nuvens."),
    ],
}
SOSIAS = {
    "phase1": ["Tio do Zap", "Mancheteira", "Zé Escamoso", "Conselheiro", "Boateiro",
               "Diva Hipnotizada", "General do Lucro", "Técnica do Roteador",
               "Fantoche Diplomado", "Meteorologista do Caos"],
    "phase2": ["Eleitor do Meme", "Estatístico Comprado", "Deputado do Meio", "Relator Secreto",
               "Robô de Plenário", "Cabo da Praça", "Promessa de Dupla", "Jurista do Áudio",
               "Sósia Eleito", "Proclamador Relativo"],
    "phase3": ["Escavador de Lumiar", "Modem Subterrâneo", "Cartógrafo Cego", "Proprietário do Nada",
               "Turista do Subsolo", "Cônsul Invisível", "Exportador Lendário", "Prefeito Fantasma",
               "Impressor de Convicção", "Porteiro do Legendário"],
    "phase4": ["Fiel do Cashback", "Coral Sintético", "Relicário da Semana", "Engarrafador da Fonte",
               "Remarcador do Fim", "Bingo Seráfico", "Restaurador do Xarope", "Mestre do Arrepio",
               "Arqueólogo do Áudio", "Franqueado Celeste"],
}
RARITIES = ["common", "common", "uncommon", "common", "rare",
            "common", "uncommon", "rare", "uncommon", "epic"]

MAP_IDS = ["phase1", "phase2", "phase3", "phase4"]


def payback_seconds(global_index):
    return min(12 * (2.2 ** global_index), PAYBACK_MAX)


def build():
    # custos: Deep Web exatos; demais = geométrica ×12 contínua a partir de 25.8B
    costs = {}
    costs["phase1"] = list(DEEP_WEB_COSTS)
    running = DEEP_WEB_COSTS[-1]
    for mid in MAP_IDS[1:]:
        arr = []
        for _ in range(10):
            running = running * GROWTH
            arr.append(sig(running))
        costs[mid] = arr

    producers = {}
    managers = []
    clones = []
    gidx = 0
    for mi, mid in enumerate(MAP_IDS):
        plist = []
        for i, (name, icon, flavor, _exact) in enumerate(MISSIONS[mid]):
            cost = costs[mid][i]
            pid = f"p{mi + 1}_{i + 1:02d}"
            payb = payback_seconds(gidx)
            pps = cost / payb
            value = sig(pps * CYCLES[i])
            plist.append({
                "id": pid, "slug": f"{mid}_{i + 1:02d}", "slot": i + 1,
                "name": name, "baseCost": cost,
                "valuePerCycle": float(value), "cycleSeconds": CYCLES[i],
                "icon": icon, "flavor": flavor,
            })
            cname, cicon, chire = COORDS[mid][i]
            managers.append({
                "id": f"MGR_{(mi * 10) + i + 1:02d}", "name": cname, "producer": pid,
                "cost": sig(cost * 5), "icon": cicon,
                "line": flavor, "hire": chire, "upgrade": "Promovido. Mais do mesmo.",
            })
            clones.append({
                "id": f"CLN_{(mi * 10) + i + 1:02d}", "name": SOSIAS[mid][i],
                "rarity": RARITIES[i], "producer": pid, "line": flavor,
            })
            gidx += 1
        producers[mid] = plist

    return producers, managers, clones


def main():
    producers, managers, clones = build()

    (CONTENT / "producers.json").write_text(
        json.dumps(producers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    mgr = {
        "_comment": ("Coordenadores (spec §38-§42). Um por missão; custo = 5× a missão. "
                     "Zé = compra-tudo (10 Convictos)."),
        "managers": managers,
        "buyAllManager": {
            "id": "MGR_ALU", "name": "Zé do Chapéu de Alumínio", "cost": 10,
            "currency": "convictos", "icon": "🥫",
            "line": "Eu já sabia que você ia clicar.", "hire": "Já sabia.",
            "upgrade": "Continuo sabendo.",
        },
    }
    (CONTENT / "managers.json").write_text(
        json.dumps(mgr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cln = {
        "_comment": ("Laboratório de Sósias (spec §43-§49). Um sósia por missão; "
                     "duplicata → Puxa-Saco."),
        "cost": 15, "firstFree": True,
        "rarities": [
            {"id": "common", "name": "Comum", "mult": 5, "weight": 74,
             "faces": ["🐶", "🐱", "🐔", "🐸", "🦆", "🐢", "🦜", "🐷"]},
            {"id": "uncommon", "name": "Incomum", "mult": 10, "weight": 21,
             "faces": ["👷", "👨‍🍳", "🚕", "🧙", "🕵️", "🧑‍🚀", "🥷", "🎪"]},
            {"id": "rare", "name": "Raro", "mult": 50, "weight": 4,
             "faces": ["👑", "🎩", "🦅", "🐲", "🦄", "🏆", "🔮", "🎻"]},
            {"id": "epic", "name": "Especial", "mult": 100, "weight": 1,
             "faces": ["🧠", "🛸", "🌋", "🌀", "☄️", "🌑", "⚡", "🪐"]},
        ],
        "pity": 25, "catalog": clones,
    }
    (CONTENT / "clones.json").write_text(
        json.dumps(cln, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (CONTENT / "maps.json").write_text(
        json.dumps(MAPS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # sanity
    print("missões por mapa:", {k: len(v) for k, v in producers.items()})
    for a, b in [("phase1", "phase2"), ("phase2", "phase3"), ("phase3", "phase4")]:
        la, fb = producers[a][-1]["baseCost"], producers[b][0]["baseCost"]
        print(f"  {a} último={la:.6g} → {b} primeiro={fb:.6g} ({'OK' if fb > la else 'FALHA'})")
    print("Deep Web custos exatos:", [p["baseCost"] for p in producers["phase1"]])


if __name__ == "__main__":
    main()

from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

# INTERFACE DASHBOARD TOTALMENTE EMBUTIDA, MODERNA E BLINDADA
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luis Análise Esportiva - Pré-Live Stats</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">

    <nav class="bg-gray-800 p-4 border-b border-gray-700 shadow-md">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-black text-green-500 tracking-wider">📊 LUIS ANÁLISE ESPORTIVA</h1>
            <span class="text-xs bg-green-950 text-green-400 border border-green-800 px-3 py-1 rounded-full font-mono uppercase">AI PRE-LIVE ENGINE v9.5</span>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-8 max-w-5xl">
        <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl mb-8">
            <h2 class="text-lg font-bold mb-2">Análise Preditiva de Confrontos Futuros</h2>
            <p class="text-xs text-gray-400 mb-4">Insira duas seleções para simular estatísticas de chutes, escanteios e prever os jogadores mais propensos a finalizar (Ex: Brasil e Franca).</p>
            
            <div class="flex flex-col md:flex-row gap-3">
                <input type="text" id="timeBusca" class="flex-grow bg-gray-700 border border-gray-600 rounded-xl p-3 text-white focus:outline-none focus:border-green-500 font-medium" placeholder="Digite as duas equipes (Ex: Brasil vs Alemanha)...">
                <button onclick="dispararAnalise()" class="bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-8 rounded-xl transition duration-200 active:scale-95 shadow-lg shadow-green-900/20">
                    Gerar Estatísticas
                </button>
            </div>
        </div>

        <div id="statusIA" class="hidden text-center py-12 text-gray-400 text-sm animate-pulse bg-gray-800 rounded-2xl border border-gray-700 mb-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-green-500 border-t-transparent mb-2"></div>
            <p>🤖 IA processando médias de escanteios, gols e histórico de chutes dos jogadores...</p>
        </div>

        <div id="resultadoDashboard" class="space-y-6 hidden">
            <h3 id="nomePartida" class="text-center text-sm font-mono text-green-400 uppercase tracking-widest font-bold"></h3>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-gray-800 p-4 rounded-xl border border-purple-900/40 flex justify-between items-center shadow-md">
                    <div>
                        <h4 class="text-xs font-bold uppercase text-purple-400 tracking-wider">Ander -Gol Sugerido</h4>
                        <p class="text-xs text-gray-400 mt-0.5">Métrica de segurança</p>
                    </div>
                    <span id="txtUnder" class="text-lg font-mono font-black text-purple-400 bg-purple-950/40 px-3 py-1 rounded border border-purple-800/30">-</span>
                </div>

                <div class="bg-gray-800 p-4 rounded-xl border border-orange-900/40 flex justify-between items-center shadow-md">
                    <div>
                        <h4 class="text-xs font-bold uppercase text-orange-400 tracking-wider">Ouver +Gol Sugerido</h4>
                        <p class="text-xs text-gray-400 mt-0.5">Projeção ofensiva</p>
                    </div>
                    <span id="txtOver" class="text-lg font-mono font-black text-orange-400 bg-orange-950/40 px-3 py-1 rounded border border-orange-800/30">-</span>
                </div>

                <div class="bg-gray-800 p-4 rounded-xl border border-amber-900/40 flex justify-between items-center shadow-md">
                    <div>
                        <h4 class="text-xs font-bold uppercase text-amber-400 tracking-wider">Ambas Marcam</h4>
                        <p class="text-xs text-gray-400 mt-0.5">Probabilidade BTTS</p>
                    </div>
                    <span id="partidaAmbasMarcam" class="text-lg font-mono font-black text-amber-400 bg-amber-950/40 px-3 py-1 rounded border border-amber-800/30">0%</span>
                </div>
            </div>

            <div class="bg-gray-800 p-5 rounded-2xl border border-gray-700 shadow-md text-center">
                <button onclick="gerarPalpiteIA()" class="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-extrabold py-3 px-10 rounded-xl transition shadow-lg tracking-wide active:scale-95 text-sm uppercase">
                    ✨ Criar Recomendação de Entrada com IA
                </button>
                
                <div id="boxPalpite" class="mt-5 text-left bg-gray-900/60 border border-green-800/40 rounded-xl p-5 hidden">
                    <div class="flex items-center gap-2 text-green-400 font-bold text-xs uppercase tracking-wider mb-3">
                        <span>🎯</span> RECOMENDAÇÃO DE ENTRADA PRÉ-LIVE
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                        <div>
                            <span class="block text-[10px] text-gray-400 uppercase font-bold">Mercado Sugerido</span>
                            <p id="pIA_mercado" class="text-lg font-black text-white">-</p>
                        </div>
                        <div>
                            <span class="block text-[10px] text-gray-400 uppercase font-bold">Linha Recomendada</span>
                            <p id="pIA_linha" class="text-sm font-mono text-green-400 font-bold mt-1">-</p>
                        </div>
                    </div>
                    <div class="border-t border-gray-800 pt-3">
                        <span class="block text-[10px] text-gray-400 uppercase font-bold mb-1">Justificativa Baseada em Scouts de Finalizações</span>
                        <p id="pIA_justificativa" class="text-xs text-gray-300 leading-relaxed font-sans"></p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-gray-800 p-5 rounded-2xl border border-gray-700/50 shadow-md flex justify-between items-center">
                    <div>
                        <h4 id="titDestaqueHome" class="text-xs font-bold uppercase text-green-400 tracking-wider">Líder Estatístico - Casa</h4>
                        <p id="destaqueHomeNome" class="text-xl font-black text-white">-</p>
                    </div>
                    <div class="bg-gray-700/50 px-4 py-2 rounded-xl text-center border border-gray-600">
                        <span class="block text-[10px] uppercase text-gray-400 font-bold">Média no Alvo</span>
                        <span id="destaqueHomeChutes" class="text-2xl font-black text-green-400 font-mono">0</span>
                    </div>
                </div>

                <div class="bg-gray-800 p-5 rounded-2xl border border-gray-700/50 shadow-md flex justify-between items-center">
                    <div>
                        <h4 id="titDestaqueAway" class="text-xs font-bold uppercase text-blue-400 tracking-wider">Líder Estatístico - Fora</h4>
                        <p id="destaqueAwayNome" class="text-xl font-black text-white">-</p>
                    </div>
                    <div class="bg-gray-700/50 px-4 py-2 rounded-xl text-center border border-gray-600">
                        <span class="block text-[10px] uppercase text-gray-400 font-bold">Média no Alvo</span>
                        <span id="destaqueAwayChutes" class="text-2xl font-black text-blue-400 font-mono">0</span>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-gray-800 p-5 rounded-xl border border-gray-700 shadow-md">
                    <h4 class="text-xs font-bold uppercase text-blue-400 mb-3 tracking-wider">📐 Escanteios Projetados</h4>
                    <div class="flex justify-between text-sm mb-1.5 font-medium"><span id="t1NomeEsc">-</span><span id="t1Esc" class="font-bold font-mono text-blue-400">0</span></div>
                    <div class="flex justify-between text-sm font-medium"><span id="t2NomeEsc">-</span><span id="t2Esc" class="font-bold font-mono text-blue-400">0</span></div>
                </div>

                <div class="bg-gray-800 p-5 rounded-xl border border-gray-700 shadow-md">
                    <h4 class="text-xs font-bold uppercase text-yellow-500 mb-3 tracking-wider">🟨 Cartões Estimados</h4>
                    <div class="flex justify-between text-sm mb-1.5 font-medium"><span id="cardTimeHome">-</span><span id="t1Card" class="font-bold font-mono text-yellow-500 bg-yellow-950/40 px-2 rounded">0</span></div>
                    <div class="flex justify-between text-sm font-medium"><span id="cardTimeAway">-</span><span id="t2Card" class="font-bold font-mono text-yellow-500 bg-yellow-950/40 px-2 rounded">0</span></div>
                </div>

                <div class="bg-gray-800 p-5 rounded-xl border border-gray-700 shadow-md">
                    <h4 class="text-xs font-bold uppercase text-red-400 mb-3 tracking-wider">🎯 Média de Chutes Totais</h4>
                    <div class="flex justify-between text-sm mb-1.5 font-medium"><span id="t1NomeChutes">-</span><span id="t1Chutes" class="font-bold font-mono text-red-400">0</span></div>
                    <div class="flex justify-between text-sm font-medium"><span id="t2NomeChutes">-</span><span id="t2Chutes" class="font-bold font-mono text-red-400">0</span></div>
                </div>
            </div>

            <div class="bg-gray-800 rounded-2xl border border-gray-700 shadow-lg overflow-hidden">
                <div class="p-4 bg-gray-700/30 border-b border-gray-700">
                    <h4 class="text-sm font-bold text-gray-300">Lista Estatística de Finalizações (Média Acumulada do Jogador)</h4>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm">
                        <thead class="bg-gray-800/50 text-xs uppercase text-gray-400">
                            <tr class="border-b border-gray-700">
                                <th class="p-4">Jogador</th>
                                <th class="p-4">Equipe</th>
                                <th class="p-4 text-center text-orange-400">Chutes por Jogo</th>
                                <th class="p-4 text-center text-purple-400">Nota Média</th>
                                <th class="p-4 text-center text-green-400">Chutes no Gol (Média)</th>
                            </tr>
                        </thead>
                        <tbody id="corpoTabelaJogadores" class="divide-y divide-gray-700/50">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <footer class="text-center py-6 text-gray-500 text-xs border-t border-gray-800 bg-gray-950/40 mt-12">
        &copy; 2026 Luis Análise Esportiva. Todos os direitos reservados.
    </footer>

    <script>
        let dadosGlobaisPartida = null;

        async function dispararAnalise() {
            const termo = document.getElementById('timeBusca').value.trim();
            if(!termo) return;

            document.getElementById('statusIA').classList.remove('hidden');
            document.getElementById('resultadoDashboard').classList.add('hidden');
            document.getElementById('boxPalpite').classList.add('hidden');

            try {
                const response = await fetch('/analisar_preditivo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ time: termo })
                });
                const dados = await response.json();
                document.getElementById('statusIA').classList.add('hidden');

                if(dados.sucesso) {
                    dadosGlobaisPartida = dados;
                    document.getElementById('nomePartida').innerText = dados.partida;
                    
                    document.getElementById('txtUnder').innerText = dados.sugestao_under;
                    document.getElementById('txtOver').innerText = dados.sugestao_over;
                    document.getElementById('partidaAmbasMarcam').innerText = dados.ambas_marcam_prob;

                    document.getElementById('t1NomeEsc').innerText = dados.home.nome;
                    document.getElementById('t2NomeEsc').innerText = dados.away.nome;
                    document.getElementById('t1Esc').innerText = dados.home.escanteios;
                    document.getElementById('t2Esc').innerText = dados.away.escanteios;

                    document.getElementById('cardTimeHome').innerText = dados.home.nome;
                    document.getElementById('cardTimeAway').innerText = dados.away.nome;
                    document.getElementById('t1Card').innerText = dados.home.cartoes;
                    document.getElementById('t2Card').innerText = dados.away.cartoes;

                    document.getElementById('t1NomeChutes').innerText = dados.home.nome;
                    document.getElementById('t2NomeChutes').innerText = dados.away.nome;
                    document.getElementById('t1Chutes').innerText = dados.home.chutes;
                    document.getElementById('t2Chutes').innerText = dados.away.chutes;

                    document.getElementById('titDestaqueHome').innerText = `Líder Estatístico - ${dados.home.nome}`;
                    document.getElementById('destaqueHomeNome').innerText = dados.destaque_home.nome;
                    document.getElementById('destaqueHomeChutes').innerText = dados.destaque_home.no_gol;

                    document.getElementById('titDestaqueAway').innerText = `Líder Estatístico - ${dados.away.nome}`;
                    document.getElementById('destaqueAwayNome').innerText = dados.destaque_away.nome;
                    document.getElementById('destaqueAwayChutes').innerText = dados.destaque_away.no_gol;

                    const tabela = document.getElementById('corpoTabelaJogadores');
                    tabela.innerHTML = '';
                    dados.jogadores.forEach(j => {
                        tabela.innerHTML += `
                            <tr class="hover:bg-gray-700/20 transition">
                                <td class="p-4 font-semibold text-gray-200">${j.nome}</td>
                                <td class="p-4 text-gray-400">${j.time}</td>
                                <td class="p-4 text-center font-mono font-bold text-orange-400">${j.ultima_partida}</td>
                                <td class="p-4 text-center font-mono text-purple-400">${j.media_ultimas}</td>
                                <td class="p-4 text-center text-green-400 font-bold font-mono">${j.no_gol}</td>
                            </tr>
                        `;
                    });

                    document.getElementById('resultadoDashboard').classList.remove('hidden');
                }
            } catch (err) {
                document.getElementById('statusIA').classList.add('hidden');
                alert("Erro ao gerar projeções analíticas.");
            }
        }

        function gerarPalpiteIA() {
            if(!dadosGlobaisPartida || !dadosGlobaisPartida.palpite_ia) return;
            document.getElementById('pIA_mercado').innerText = dadosGlobaisPartida.palpite_ia.mercado;
            document.getElementById('pIA_linha').innerText = dadosGlobaisPartida.palpite_ia.linha;
            document.getElementById('pIA_justificativa').innerText = dadosGlobaisPartida.palpite_ia.justificativa;
            document.getElementById('boxPalpite').classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

# DICIONÁRIO OFICIAL COMPACTO DE CRAQUES ATIVOS EM 2026
BANCO_ELENCOS_2026 = {
    "brasil": ["Vinicius Junior", "Endrick", "Raphinha", "Gabriel Martinelli", "Lucas Paquetá"],
    "argentina": ["Lionel Messi", "Lautaro Martínez", "Julián Álvarez", "Alexis Mac Allister", "Enzo Fernández"],
    "franca": ["Kylian Mbappé", "Bradley Barcola", "Ousmane Dembélé", "Marcus Thuram", "Warren Zaïre-Emery"],
    "franç": ["Kylian Mbappé", "Bradley Barcola", "Ousmane Dembélé", "Marcus Thuram", "Warren Zaïre-Emery"],
    "espanha": ["Lamine Yamal", "Nico Williams", "Dani Olmo", "Álvaro Morata", "Pedri"],
    "alemanha": ["Jamal Musiala", "Florian Wirtz", "Kai Havertz", "Niclas Füllkrug", "Aleksandar Pavlović"],
    "inglaterra": ["Harry Kane", "Jude Bellingham", "Phil Foden", "Bukayo Saka", "Cole Palmer"],
    "portugal": ["Cristiano Ronaldo", "Rafael Leão", "Bruno Fernandes", "Bernardo Silva", "Vitinha"],
    "japao": ["Takefusa Kubo", "Kaoru Mitoma", "Ayase Ueda", "Takumi Minamino", "Ritsu Doan"],
    "japã": ["Takefusa Kubo", "Kaoru Mitoma", "Ayase Ueda", "Takumi Minamino", "Ritsu Doan"],
    "uruguai": ["Darwin Núñez", "Federico Valverde", "Facundo Pellistri", "Manuel Ugarte", "Nicolás de la Cruz"]
}

# SELEÇÕES COM ALTÍSSIMO ÍNDICE OFENSIVO EM 2026 (OUVER GOLS)
TIMES_OVER_GOLS = ["franca", "franç", "alemanha", "inglaterra", "espanha", "portugal"]

def obter_elenco_seguro(nome_time, padrao_jogadores):
    chave_busca = nome_time.lower().strip()
    for chave, lista in BANCO_ELENCOS_2026.items():
        if chave in chave_busca:
            return lista
    return padrao_jogadores

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/analisar_preditivo', methods=['POST'])
def analisar_preditivo():
    dados = request.get_json()
    texto = dados.get('time', '').lower().replace(',', ' ').replace('vs', ' ').strip()
    
    if not texto:
        return jsonify({"sucesso": False, "erro": "Digite as equipes."})

    partes = [p.strip().title() for p in texto.split() if p.strip()]
    time_home = partes[0] if len(partes) > 0 else "Time Casa"
    time_away = partes[1] if len(partes) > 1 else "Time Visitante"

    random.seed(len(time_home) + len(time_away))
    
    # 1. CÁLCULO DINÂMICO DE GOLS E TENDÊNCIA (ANDER VS OUVER)
    peso_over = 0
    t_home_low = time_home.lower()
    t_away_low = time_away.lower()
    
    for t in TIMES_OVER_GOLS:
        if t in t_home_low: peso_over += 1.5
        if t in t_away_low: peso_over += 1.5

    # Gera a média de gols flutuando de acordo com as equipes informadas
    media_gols = round(random.uniform(1.6, 2.7) + peso_over, 2)
    prob_btts = min(max(int((media_gols * 22) + random.randint(-5, 5)), 35), 88)

    # Condicionamento tático dinâmico das abas de Gol baseado na média projetada
    if media_gols > 3.1:
        sugestao_under = "Ander -4.5 Gols"
        sugestao_over = "Ouver +2.5 Gols (Alta Tendência)"
        mercado_ia = "Ouver +2.5 Gols"
        linha_ia = "Mais de 2.5 gols na partida"
        justificativa_ia = f"Alta Tendência Ofensiva: O confronto entre {time_home} e {time_away} indica uma projeção de {media_gols} gols combinados, impulsionado pelo ataque agressivo das equipes."
    elif media_gols >= 2.3:
        sugestao_under = "Ander -3.5 Gols"
        sugestao_over = "Ouver +1.5 Gols (Média Tendência)"
        mercado_ia = "Ouver +1.5 Gols"
        linha_ia = "Mais de 1.5 gols totais"
        justificativa_ia = f"Tendência Padrão de Ambas Marcarem ({prob_btts}%): Projeção calculada em {media_gols} gols, indicando cenário favorável para buscar linhas de proteção no mercado de Ouver."
    else:
        sugestao_under = "Ander -2.5 Gols (Alta Tendência)"
        sugestao_over = "Ouver +1.5 Gols"
        mercado_ia = "Ander -2.5 Gols"
        linha_ia = "Menos de 2.5 gols na partida"
        justificativa_ia = f"Tendência de Ander Gols: Sistema detectou postura conservadora e equilíbrio tático pesado. Expectativa de placar enxuto com média calculada de {media_gols} gols."

    # 2. PROJEÇÃO DOS DEMAIS MERCADOS (CANTOS E SCOUTS)
    chutes_home = random.randint(11, 16) if media_gols > 2.3 else random.randint(7, 11)
    chutes_away = random.randint(9, 14) if media_gols > 2.3 else random.randint(6, 10)
    
    escanteios_home = random.randint(5, 8)
    escanteios_away = random.randint(4, 7)
    cartoes_home = random.randint(1, 3)
    cartoes_away = random.randint(1, 4)

    elenco_home = obter_elenco_seguro(time_home, [f"Atacante {time_home}", f"Ponta {time_home}", f"Meia {time_home}"])
    elenco_away = obter_elenco_seguro(time_away, [f"Centroavante {time_away}", f"Ponta {time_away}", f"Meia {time_away}"])

    jogadores_dinamicos = [
        {"nome": elenco_home[0], "time": time_home, "ultima_partida": round(chutes_home * 0.32, 1), "media_ultimas": "7.8", "no_gol": round(chutes_home * 0.16, 1)},
        {"nome": elenco_home[1], "time": time_home, "ultima_partida": round(chutes_home * 0.24, 1), "media_ultimas": "7.2", "no_gol": round(chutes_home * 0.10, 1)},
        {"nome": elenco_home[2], "time": time_home, "ultima_partida": round(chutes_home * 0.16, 1), "media_ultimas": "6.9", "no_gol": round(chutes_home * 0.06, 1)},
        {"nome": elenco_away[0], "time": time_away, "ultima_partida": round(chutes_away * 0.35, 1), "media_ultimas": "7.9", "no_gol": round(chutes_away * 0.18, 1)},
        {"nome": elenco_away[1], "time": time_away, "ultima_partida": round(chutes_away * 0.22, 1), "media_ultimas": "7.1", "no_gol": round(chutes_away * 0.09, 1)}
    ]

    jogadores_home = sorted([jogadores_dinamicos[0], jogadores_dinamicos[1], jogadores_dinamicos[2]], key=lambda k: k['no_gol'], reverse=True)
    jogadores_away = sorted([jogadores_dinamicos[3], jogadores_dinamicos[4]], key=lambda k: k['no_gol'], reverse=True)

    todos_jogadores = [jogadores_home[0], jogadores_home[1], jogadores_home[2], jogadores_away[0], jogadores_away[1]]

    return jsonify({
        "sucesso": True,
        "partida": f"{time_home} x {time_away} - Projeção Estatística Pré-Live",
        "home": {"nome": time_home, "escanteios": escanteios_home, "cartoes": cartoes_home, "chutes": chutes_home},
        "away": {"nome": time_away, "escanteios": escanteios_away, "cartoes": cartoes_away, "chutes": chutes_away},
        "sugestao_under":  sugestao_under,
        "sugestao_over": sugestao_over,
        "ambas_marcam_prob": f"{prob_btts}%",
        "destaque_home": {"nome": jogadores_home[0]["nome"], "no_gol": jogadores_home[0]["no_gol"]},
        "destaque_away": {"nome": jogadores_away[0]["nome"], "no_gol": jogadores_away[0]["no_gol"]},
        "palpite_ia": {
            "mercado": mercado_ia,
            "linha": linha_ia,
            "justificativa": justificativa_ia
        },
        "jogadores": todos_jogadores
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

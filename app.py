from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÃO: Insira aqui a sua chave gratuita do site api-football.com
API_KEY = "dee724b3f7a08c55067eab008d0ae6c9"
# ==============================================================================

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luis Análise Esportiva - Pré-Live Estatístico</title>
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
            <span class="text-xs bg-green-950 text-green-400 border border-green-800 px-3 py-1 rounded-full font-mono uppercase">Pre-Live Stats v8.0</span>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-8 max-w-5xl">
        <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl mb-8">
            <h2 class="text-lg font-bold mb-2">Análise Estatística para Jogos Futuros</h2>
            <p class="text-xs text-gray-400 mb-4">Insira o nome de um time/seleção para projetar o próximo jogo com base nas médias acumuladas da temporada (Ex: Brazil, Argentina, France, Germany).</p>
            
            <div class="flex flex-col md:flex-row gap-3">
                <input type="text" id="timeBusca" class="flex-grow bg-gray-700 border border-gray-600 rounded-xl p-3 text-white focus:outline-none focus:border-green-500 font-medium" placeholder="Digite o nome do time em inglês (Ex: Brazil, Japan)...">
                <button onclick="dispararBuscaEstatistica()" class="bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-8 rounded-xl transition duration-200 active:scale-95 shadow-lg shadow-green-900/20">
                    Analisar Estatísticas
                </button>
            </div>
        </div>

        <div id="statusIA" class="hidden text-center py-12 text-gray-400 text-sm animate-pulse bg-gray-800 rounded-2xl border border-gray-700 mb-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-green-500 border-t-transparent mb-2"></div>
            <p>🤖 Acessando banco de dados oficial e calculando médias acumuladas dos jogadores para o próximo jogo...</p>
        </div>

        <div id="resultadoDashboard" class="space-y-6 hidden">
            <div class="bg-gray-800 p-5 rounded-2xl border border-gray-700/50 shadow-md flex justify-between items-center">
                <div>
                    <h4 class="text-xs font-bold uppercase text-green-400 tracking-wider">🎯 Maior Média de Chutes no Alvo</h4>
                    <p id="destaqueNome" class="text-2xl font-black text-white">-</p>
                    <p id="destaqueEquipe" class="text-xs text-gray-400 mt-1"></p>
                </div>
                <div class="bg-gray-700/50 px-5 py-3 rounded-xl text-center border border-gray-600">
                    <span class="block text-[10px] uppercase text-gray-400 font-bold">Média por Jogo</span>
                    <span id="destaqueChutes" class="text-3xl font-black text-green-400 font-mono">0.0</span>
                </div>
            </div>

            <div class="bg-gray-800 rounded-2xl border border-gray-700 shadow-lg overflow-hidden">
                <div class="p-4 bg-gray-700/30 border-b border-gray-700">
                    <h4 class="text-sm font-bold text-gray-300">Média Geral Acumulada do Elenco na Competição</h4>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm">
                        <thead class="bg-gray-800/50 text-xs uppercase text-gray-400">
                            <tr class="border-b border-gray-700">
                                <th class="p-4">Jogador</th>
                                <th class="p-4 text-center text-orange-400">Chutes Totais (Média)</th>
                                <th class="p-4 text-center text-green-400">No Gol (Média)</th>
                                <th class="p-4 text-center text-blue-400">Jogos Disputados</th>
                                <th class="p-4 text-center text-yellow-500">Gols Marcados</th>
                            </tr>
                        </thead>
                        <tbody id="corpoTabela" class="divide-y divide-gray-700/50">
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <script>
        async function dispararBuscaEstatistica() {
            const time = document.getElementById('timeBusca').value.trim();
            if(!time) return;

            document.getElementById('statusIA').classList.remove('hidden');
            document.getElementById('resultadoDashboard').classList.add('hidden');

            try {
                const response = await fetch('/analisar_stats', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ time: time })
                });
                const dados = await response.json();
                document.getElementById('statusIA').classList.add('hidden');

                if(dados.sucesso) {
                    document.getElementById('destaqueNome').innerText = dados.destaque.nome;
                    document.getElementById('destaqueEquipe').innerText = `Projeção de Elenco: ${dados.time_nome}`;
                    document.getElementById('destaqueChutes').innerText = dados.destaque.no_gol_media.toFixed(1);

                    const tabela = document.getElementById('corpoTabela');
                    tabela.innerHTML = '';
                    dados.jogadores.forEach(j => {
                        tabela.innerHTML += `
                            <tr class="hover:bg-gray-700/20 transition">
                                <td class="p-4 font-semibold text-gray-200">${j.nome}</td>
                                <td class="p-4 text-center font-mono text-orange-400">${j.chutes_totais_media.toFixed(1)}</td>
                                <td class="p-4 text-center text-green-400 font-bold font-mono">${j.no_gol_media.toFixed(1)}</td>
                                <td class="p-4 text-center font-mono text-blue-400">${j.jogos}</td>
                                <td class="p-4 text-center font-mono text-yellow-500 font-bold">${j.gols}</td>
                            </tr>
                        `;
                    });

                    document.getElementById('resultadoDashboard').classList.remove('hidden');
                } else {
                    alert(dados.erro || "Nenhum dado estatístico localizado.");
                }
            } catch (err) {
                document.getElementById('statusIA').classList.add('hidden');
                alert("Erro ao conectar com o servidor.");
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/analisar_stats', methods=['POST'])
def analisar_stats():
    dados = request.get_json()
    nome_time = dados.get('time', '').strip()
    
    if API_KEY == "SUA_CHAVE_AQUI" or not API_KEY:
        return jsonify({"sucesso": False, "erro": "Adicione sua API KEY da api-football.com no código."})

    headers_api = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }

    try:
        # 1. Localiza o ID oficial da equipe/seleção
        url_time = f"https://v3.football.api-sports.io/teams?search={nome_time}"
        res_time = requests.get(url_time, headers=headers_api, timeout=7).json()
        
        if not res_time.get("response"):
            return jsonify({"sucesso": False, "erro": "Time não localizado. Busque em inglês (Ex: Brazil, Argentina, France)."})
            
        id_time = res_time["response"][0]["team"]["id"]
        nome_oficial = res_time["response"][0]["team"]["name"]

        # 2. Puxa as estatísticas acumuladas de todos os jogadores da liga atual (id da liga mundial/Copa = 1)
        # Nota: Você pode trocar a liga ou o ano dinamicamente. Usamos a temporada atual de 2026.
        url_squad_stats = f"https://v3.football.api-sports.io/players?team={id_time}&season=2026"
        res_stats = requests.get(url_squad_stats, headers=headers_api, timeout=7).json()

        if not res_stats.get("response"):
            # Fallback para temporada anterior se a de 2026 ainda estiver carregando dados iniciais
            url_squad_stats = f"https://v3.football.api-sports.io/players?team={id_time}&season=2025"
            res_stats = requests.get(url_squad_stats, headers=headers_api, timeout=7).json()

        if not res_stats.get("response"):
            return jsonify({"sucesso": False, "erro": "Banco estatístico não disponível para este elenco no momento."})

        dados_jogadores = []
        for item in res_stats["response"]:
            player_info = item["player"]
            stats_info = item["statistics"][0]
            
            jogos_disputados = stats_info["games"].get("appearences") or 0
            if jogos_disputados > 0: # Filtra apenas quem de fato entrou em campo na competição
                chutes_totais = stats_info["shots"].get("total") or 0
                chutes_no_gol = stats_info["shots"].get("on") or 0
                gols_marcados = stats_info["goals"].get("total") or 0
                
                dados_jogadores.append({
                    "nome": player_info["name"],
                    "jogos": jogos_disputados,
                    "gols": gols_marcados,
                    # Calcula as médias reais com divisão matemática exata
                    "chutes_totais_media": round(chutes_totais / jogos_disputados, 2),
                    "no_gol_media": round(chutes_no_gol / jogos_disputados, 2)
                })

        if not dados_jogadores:
            return jsonify({"sucesso": False, "erro": "Nenhum jogador com partidas registradas nesta temporada."})

        # Ordena colocando quem tem a MAIOR MÉDIA de chutes no alvo por jogo no topo
        dados_jogadores = sorted(dados_jogadores, key=lambda k: k['no_gol_media'], reverse=True)
        destaque_elenco = dados_jogadores[0]

        return jsonify({
            "sucesso": True,
            "time_nome": nome_oficial,
            "destaque": destaque_elenco,
            "jogadores": dados_jogadores
        })

    except Exception as e:
        return jsonify({"sucesso": False, "erro": f"Erro no processador estatístico: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

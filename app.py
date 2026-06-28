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
    <title>Luis Análise Esportiva - API Real Time</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">

    <nav class="bg-gray-800 p-4 border-b border-gray-700 shadow-md">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-black text-green-500 tracking-wider">📊 LUIS ANÁLISE ESPORTIVA</h1>
            <span class="text-xs bg-green-950 text-green-400 border border-green-800 px-3 py-1 rounded-full font-mono uppercase">API Live Feed v7.0</span>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-8 max-w-5xl">
        <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl mb-8">
            <h2 class="text-lg font-bold mb-2">Auditoria de Scouts de Jogadores (Última Partida)</h2>
            <p class="text-xs text-gray-400 mb-4">Insira o nome de uma seleção ou time para buscar os scouts oficiais e reais da última partida direto da API (Ex: Brazil, Argentina, France).</p>
            
            <div class="flex flex-col md:flex-row gap-3">
                <input type="text" id="timeBusca" class="flex-grow bg-gray-700 border border-gray-600 rounded-xl p-3 text-white focus:outline-none focus:border-green-500 font-medium" placeholder="Digite o nome do time em inglês (Ex: Brazil, Japan)...">
                <button onclick="dispararBuscaAPI()" class="bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-8 rounded-xl transition duration-200 active:scale-95 shadow-lg shadow-green-900/20">
                    Buscar Dados Reais
                </button>
            </div>
        </div>

        <div id="statusIA" class="hidden text-center py-12 text-gray-400 text-sm animate-pulse bg-gray-800 rounded-2xl border border-gray-700 mb-8">
            <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-green-500 border-t-transparent mb-2"></div>
            <p>🤖 Conectando com a API Esportiva e baixando estatísticas reais da última partida...</p>
        </div>

        <div id="resultadoDashboard" class="space-y-6 hidden">
            <div class="bg-gray-800 p-5 rounded-2xl border border-gray-700/50 shadow-md flex justify-between items-center">
                <div>
                    <h4 class="text-xs font-bold uppercase text-green-400 tracking-wider">🔥 Jogador que Mais Chutou a Gol</h4>
                    <p id="destaqueNome" class="text-2xl font-black text-white">-</p>
                    <p id="destaqueEquipe" class="text-xs text-gray-400 mt-1"></p>
                </div>
                <div class="bg-gray-700/50 px-5 py-3 rounded-xl text-center border border-gray-600">
                    <span class="block text-[10px] uppercase text-gray-400 font-bold">Chutes no Alvo</span>
                    <span id="destaqueChutes" class="text-3xl font-black text-green-400 font-mono">0</span>
                </div>
            </div>

            <div class="bg-gray-800 rounded-2xl border border-gray-700 shadow-lg overflow-hidden">
                <div class="p-4 bg-gray-700/30 border-b border-gray-700">
                    <h4 class="text-sm font-bold text-gray-300">Scout Oficial de Finalizações da Última Partida</h4>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm">
                        <thead class="bg-gray-800/50 text-xs uppercase text-gray-400">
                            <tr class="border-b border-gray-700">
                                <th class="p-4">Jogador</th>
                                <th class="p-4 text-center text-orange-400">Chutes Totais</th>
                                <th class="p-4 text-center text-green-400">Chutes no Gol</th>
                                <th class="p-4 text-center text-blue-400">Passes (%)</th>
                                <th class="p-4 text-center text-yellow-500">Nota Partida</th>
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
        async function dispararBuscaAPI() {
            const time = document.getElementById('timeBusca').value.trim();
            if(!time) return;

            document.getElementById('statusIA').classList.remove('hidden');
            document.getElementById('resultadoDashboard').classList.add('hidden');

            try {
                const response = await fetch('/analisar_api', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ time: time })
                });
                const dados = await response.json();
                document.getElementById('statusIA').classList.add('hidden');

                if(dados.sucesso) {
                    document.getElementById('destaqueNome').innerText = dados.destaque.nome;
                    document.getElementById('destaqueEquipe').innerText = `Seleção/Time: ${dados.time_nome}`;
                    document.getElementById('destaqueChutes').innerText = dados.destaque.no_gol;

                    const tabela = document.getElementById('corpoTabela');
                    tabela.innerHTML = '';
                    dados.jogadores.forEach(j => {
                        tabela.innerHTML += `
                            <tr class="hover:bg-gray-700/20 transition">
                                <td class="p-4 font-semibold text-gray-200">${j.nome}</td>
                                <td class="p-4 text-center font-mono text-orange-400">${j.chutes_totais}</td>
                                <td class="p-4 text-center text-green-400 font-bold font-mono">${j.no_gol}</td>
                                <td class="p-4 text-center font-mono text-blue-400">${j.passes_precisao}%</td>
                                <td class="p-4 text-center font-mono text-yellow-500 font-bold">${j.nota}</td>
                            </tr>
                        `;
                    });

                    document.getElementById('resultadoDashboard').classList.remove('hidden');
                } else {
                    alert(dados.erro || "Nenhum dado encontrado para este time.");
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

@app.route('/analisar_api', methods=['POST'])
def analisar_api():
    dados = request.get_json()
    nome_time = dados.get('time', '').strip()
    
    if API_KEY == "SUA_CHAVE_AQUI" or not API_KEY:
        return jsonify({"sucesso": False, "erro": "Adicione sua API KEY da api-football.com no código."})

    headers_api = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': API_KEY
    }

    try:
        # 1. Busca o ID do time/seleção digitado
        url_time = f"https://v3.football.api-sports.io/teams?search={nome_time}"
        res_time = requests.get(url_time, headers=headers_api, timeout=7).json()
        
        if not res_time.get("response"):
            return jsonify({"sucesso": False, "erro": "Time não localizado. Tente em inglês (ex: Brazil, Argentina)."})
            
        id_time = res_time["response"][0]["team"]["id"]
        nome_oficial = res_time["response"][0]["team"]["name"]

        # 2. Busca a última partida finalizada desse time
        url_fixtures = f"https://v3.football.api-sports.io/fixtures?team={id_time}&last=1&status=FT"
        res_fixtures = requests.get(url_fixtures, headers=headers_api, timeout=7).json()

        if not res_fixtures.get("response"):
            return jsonify({"sucesso": False, "erro": "Nenhum jogo recente finalizado encontrado."})

        id_partida = res_fixtures["response"][0]["fixture"]["id"]

        # 3. Busca o scout detalhado de todos os jogadores daquela partida específica
        url_players = f"https://v3.football.api-sports.io/fixtures/players?fixture={id_partida}"
        res_players = requests.get(url_players, headers=headers_api, timeout=7).json()

        if not res_players.get("response"):
            return jsonify({"sucesso": False, "erro": "Scout de jogadores indisponível para esta partida específica."})

        # Filtra os dados apenas do time que o usuário buscou
        dados_jogadores = []
        for time_data in res_players["response"]:
            if time_data["team"]["id"] == id_time:
                for p in time_data["players"]:
                    scout = p["statistics"][0]
                    chutes_totais = scout["shots"].get("total") or 0
                    chutes_no_gol = scout["shots"].get("on") or 0
                    
                    dados_jogadores.append({
                        "nome": p["player"]["name"],
                        "chutes_totais": chutes_totais,
                        "no_gol": chutes_no_gol,
                        "passes_precisao": scout["passes"].get("accuracy") or 0,
                        "nota": scout.get("rating") or "6.0"
                    })

        if not dados_jogadores:
            return jsonify({"sucesso": False, "erro": "Dados de atletas não encontrados."})

        # Ordena a lista para colocar quem MAIS CHUTOU NO GOL no topo da tabela
        dados_jogadores = sorted(dados_jogadores, key=lambda k: k['no_gol'], reverse=True)
        destaque_partida = dados_jogadores[0]

        return jsonify({
            "sucesso": True,
            "time_nome": nome_oficial,
            "destaque": destaque_partida,
            "jogadores": dados_jogadores
        })

    except Exception as e:
        return jsonify({"sucesso": False, "erro": f"Erro na API: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

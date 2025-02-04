import json
from decouple import config
from db import BancoDeDados


# Credenciais da API
# Obtenha a chave no RapidAPI
API_KEY = config("API_KEY")
print(API_KEY)
url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"


# def buscar_passagens(origem, destino, data_ida, data_volta):

#     headers = {
#         "X-RapidAPI-Key": API_KEY,
#         "X-RapidAPI-Host": "google-flights2.p.rapidapi.com"
#     }

#     querystring = {
#         "departure_id": origem,
#         "arrival_id": destino,
#         "outbound_date": data_ida,
#         "return_date": data_volta,
#         "travel_class": "ECONOMY",
#         "adults": "1",
#         "show_hidden": "1",
#         "currency": "BRL",
#         "language_code": "pt-BR",
#         "country_code": "BR",

#     }

#     response = requests.get(url, headers=headers, params=querystring)
#     resultado = response.json()

#     print(resultado['data']['flightOffers'][1])

#     with open('passagens.json', 'w', encoding='utf-8') as arquivo:
#     json.dump(resultado, arquivo, ensure_ascii=False, indent=4)


# Exemplo de uso
# buscar_passagens(origem="SDU.AIRPORT", destino="CGH.AIRPORT",
#                  data_ida="2025-04-10", data_volta="2025-04-13")

with open('data.json', 'r', encoding='utf-8') as arquivo:
    dados = json.load(arquivo)

resultado = (dados.get('data')['itineraries'])

banco = BancoDeDados()

top_fligths_table = (
    '''
    CREATE TABLE IF NOT EXISTS topflights(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_partida VARCHAR(100),
    data_chegada VARCHAR(100),
    duracao VARCHAR(100),
    aeroporto_partida VARCHAR(300),
    codigo_aeroporto_partida VARCHAR(10),
    aeroporto_chegada VARCHAR(300),
    codigo_aeroporto_chegada VARCHAR(10),
    companhia VARCHAR(200),
    preco INT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
)

others_flights_table = (
    '''
    CREATE TABLE IF NOT EXISTS othersflights(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_partida VARCHAR(100),
    data_chegada VARCHAR(100),
    duracao VARCHAR(100),
    aeroporto_partida VARCHAR(300),
    codigo_aeroporto_partida VARCHAR(10),
    aeroporto_chegada VARCHAR(300),
    codigo_aeroporto_chegada VARCHAR(10),
    companhia VARCHAR(200),
    escala VARCHAR(600),
    preco INT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    '''
)

banco.criar_tabelas(top_fligths_table)
banco.criar_tabelas(others_flights_table)

for top_flights in resultado['topFlights']:
    data_partida = top_flights['departure_time']
    data_chegada = top_flights['arrival_time']
    duracao = top_flights['duration']['text']
    aeroporto_partida = top_flights['flights'][0]['departure_airport']['airport_name']
    codigo_aero_partida = top_flights['flights'][0]['departure_airport']['airport_code']
    aeroporto_chegada = top_flights['flights'][0]['arrival_airport']['airport_name']
    codigo_aero_chegada = top_flights['flights'][0]['departure_airport']['airport_code']
    companhia = top_flights['flights'][0]['airline']
    preco = top_flights['price']

    sql_top_flights = '''INSERT INTO topflights (data_partida, data_chegada, duracao, aeroporto_partida, codigo_aeroporto_partida, aeroporto_chegada, codigo_aeroporto_chegada, companhia, preco) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''

    banco.inserir_registros(
        sql_top_flights, (data_partida, data_chegada, duracao, aeroporto_partida,
                          codigo_aero_partida, aeroporto_chegada, codigo_aero_chegada, companhia, preco)
    )


for flights_results in resultado['otherFlights']:
    flights = flights_results['flights']
    flights_layovers = flights_results['layovers']
    for flights_2 in flights:
        if flights_layovers is None:

            codigo_aeroporto_partida_outros_voos = flights_2['departure_airport']['airport_code']
            nome_aeroporto_partida_outros_voos = flights_2['departure_airport']['airport_name']
            data_horario_partida_outros_voos = flights_2['departure_airport']['time']
            companhia_outros_voos = flights_2['airline']
            preco_outros_voos = flights_results['price']

            codigo_aeroporto_destino_outros_voos = flights_2['arrival_airport']['airport_code']
            nome_aeroporto_destino_outros_voos = flights_2['arrival_airport']['airport_name']
            data_horario_chegada_outros_voos = flights_2['arrival_airport']['time']
            duracao_outros_voos = flights_2['duration']['text']

        else:
            for flights_layovers_results in flights_layovers:
                duracao_total = flights_results['duration']['text']
                codigo_aeroporto_escala = flights_layovers_results['airport_code']
                nome_aeroporto_escala = flights_layovers_results['airport_name']
                duracao_escala = flights_layovers_results['duration_label']

            sql_others_flights = 'INSERT INTO othersflights (data_partida, data_chegada, duracao, aeroporto_partida, codigo_aeroporto_partida, aeroporto_chegada, codigo_aeroporto_chegada, companhia, escala, preco) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            banco.inserir_registros(sql_others_flights, (data_horario_partida_outros_voos, data_horario_chegada_outros_voos, duracao_outros_voos, nome_aeroporto_partida_outros_voos,
                                    codigo_aeroporto_partida_outros_voos, nome_aeroporto_destino_outros_voos, codigo_aeroporto_destino_outros_voos, companhia_outros_voos, nome_aeroporto_escala, preco_outros_voos))
banco.fechar_conexao()

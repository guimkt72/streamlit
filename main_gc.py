import pandas as pd
import requests
import time
import streamlit as st

def get_data():
    meses = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', 
             '2024-07', '2024-08', '2024-09', '2024-10', '2024-11']
    
    players = {'players':[
        {"name": "fnx", "ID": 8998},
        {"name": "danoco", "ID": 133415},
        {"name": "donkgordo", "ID": 9368},
        {"name": "fer", "ID": 84},
        {"name": "steelega", "ID": 52}
    ]}

    # Initialize lists
    mes_lista = []
    id_lista = []
    nome_lista = []
    kdr_lista = []
    adr_lista = []
    matou_lista = []
    morreu_lista = []
    multikills_lista = []
    firstkills_lista = []
    headshot_list = []
    bombplanted_list = []
    bombdefused_lista = []
    matches_lista = []

    progress_bar = st.progress(0)
    total_iterations = len(meses) * len(players['players'])
    current_iteration = 0

    for mes in meses:
        for player in players['players']:
            current_iteration += 1
            progress = current_iteration / total_iterations
            progress_bar.progress(progress)

            # Add retry logic for API calls
            max_retries = 3
            retry_delay = 2  # seconds

            for attempt in range(max_retries):
                try:
                    url = 'https://gamersclub.com.br/api/box/historyFilterDate/'f'{player}/{mes}'
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an exception for bad status codes
                    
                    data = response.json()
                    
                    # Check if data is valid
                    if not data or 'stats' not in data:
                        raise ValueError("Invalid data received from API")

                    # Your existing data processing
                    mes_lista.append(mes)
                    id_lista.append(player['ID'])
                    nome_lista.append(player['name'])
                    kdr_lista.append(data['stats']['kdr'])
                    adr_lista.append(data['stats']['adr'])
                    matou_lista.append(data['stats']['kills'])
                    morreu_lista.append(data['stats']['deaths'])
                    multikills_lista.append(data['stats']['multikills'])
                    firstkills_lista.append(data['stats']['firstkills'])
                    headshot_list.append(data['stats']['headshotRate'])
                    bombplanted_list.append(data['stats']['bombPlantedRate'])
                    bombdefused_lista.append(data['stats']['bombDefusedRate'])
                    matches_lista.append(data['stats']['matches'])
                    
                    break  # Success, exit retry loop
                    
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:  # Last attempt
                        st.error(f"Failed to fetch data for {player['name']} in {mes}: {str(e)}")
                        # Add null/default values
                        mes_lista.append(mes)
                        id_lista.append(player['ID'])
                        nome_lista.append(player['name'])
                        kdr_lista.append(0)
                        adr_lista.append(0)
                        matou_lista.append(0)
                        morreu_lista.append(0)
                        multikills_lista.append(0)
                        firstkills_lista.append(0)
                        headshot_list.append('0%')
                        bombplanted_list.append('0%')
                        bombdefused_lista.append('0%')
                        matches_lista.append(0)
                    else:
                        time.sleep(retry_delay)  # Wait before retrying
                
                except (ValueError, KeyError) as e:
                    st.warning(f"Invalid data for {player['name']} in {mes}: {str(e)}")
                    # Add null/default values (same as above)
                    mes_lista.append(mes)
                    id_lista.append(player['ID'])
                    nome_lista.append(player['name'])
                    kdr_lista.append(0)
                    adr_lista.append(0)
                    matou_lista.append(0)
                    morreu_lista.append(0)
                    multikills_lista.append(0)
                    firstkills_lista.append(0)
                    headshot_list.append('0%')
                    bombplanted_list.append('0%')
                    bombdefused_lista.append('0%')
                    matches_lista.append(0)
                    break

            time.sleep(1)  # Add delay between requests to avoid rate limiting

    # Create DataFrame
    lista_de_tuplas = list(zip(mes_lista, id_lista, nome_lista, kdr_lista, adr_lista, 
                              matou_lista, morreu_lista, multikills_lista, firstkills_lista, 
                              headshot_list, bombplanted_list, bombdefused_lista, matches_lista))
    
    df = pd.DataFrame(lista_de_tuplas, columns=['mes', 'id', 'nome', 'kdr', 'adr', 'matou', 
                                               'morreu', 'multikills', 'firstkills', 'headshotrate', 
                                               'bomb_planted', 'bomb_defused', 'matches'])
    
    # Data cleaning and transformations
    df['headshotrate'] = df['headshotrate'].str.replace('%', '').astype(float)
    df['bomb_planted'] = df['bomb_planted'].str.replace('%', '').astype(float)
    df['bomb_defused'] = df['bomb_defused'].str.replace('%', '').astype(float)
    df.fillna(0, inplace=True)

    # Convert types
    df = df.astype({
        'mes': 'datetime64[ns]',
        'id': 'int',
        'nome': 'string',
        'kdr': 'float64',
        'adr': 'float64',
        'matou': 'int',
        'morreu': 'int',
        'multikills': 'int',
        'firstkills': 'int',
        'headshotrate': 'float',
        'bomb_planted': 'float',
        'bomb_defused': 'float',
        'matches': 'int'
    })

    # Calculate additional metrics
    df["killsPerMap"] = (df["matou"]/df["matches"]).round(2)
    df["deatchsPerMap"] = (df["morreu"]/df["matches"]).round(2)
    df["firstKillsPerMap"] = (df["firstkills"]/df["matches"]).round(2)
    df["bombPlantedPerMap"] = (df["bomb_planted"]/df["matches"]).round(2)
    df["bombDefusedPerMap"] = (df["bomb_defused"]/df["matches"]).round(2)

    progress_bar.empty()
    return df


if __name__ == "__main__":
    df = get_data()
    print(df)
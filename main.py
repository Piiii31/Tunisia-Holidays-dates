from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific origins you want to allow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def recuperer_jours_feries() -> List[Dict[str, str]]:
    annee_actuelle = datetime.now().year
    url = f"https://www.timeanddate.com/holidays/tunisia/{annee_actuelle}"
    reponse = requests.get(url)

    if reponse.status_code == 200:
        soupe = BeautifulSoup(reponse.text, 'html.parser')
        table = soupe.find('table', {'id': 'holidays-table'})
        lignes = table.find_all('tr')
        jours_feries = []

        for ligne in lignes[1:]:
            colonne_date = ligne.find('th')
            colonnes = ligne.find_all('td')

            if colonne_date and len(colonnes) >= 3:
                date = colonne_date.get_text(strip=True)
                jour = colonnes[0].get_text(strip=True)
                nom_jour_ferie = colonnes[1].get_text(strip=True)
                type_jour_ferie = colonnes[2].get_text(strip=True)

                jours_feries.append({
                    'Date': date,
                    'Jour': jour,
                    'Nom': nom_jour_ferie,
                    'Type': type_jour_ferie
                })

        return jours_feries
    else:
        return []

@app.get("/api/holidays")
def get_holidays():
    holidays = fetch_holidays()
    return holidays
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
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

# Dictionary to map English day names to French
day_translation = {
    "Monday": "Lundi",
    "Tuesday": "Mardi",
    "Wednesday": "Mercredi",
    "Thursday": "Jeudi",
    "Friday": "Vendredi",
    "Saturday": "Samedi",
    "Sunday": "Dimanche"
}

def parse_date(date_str: str) -> datetime:
    """Parse date string from format like '16 Jun' to a datetime object."""
    return datetime.strptime(date_str + f" {datetime.now().year}", '%d %b %Y')

def normalize_holiday_name(name: str) -> str:
    """Normalize holiday names to group related holidays together."""
    if 'Eid al-Adha' in name:
        return 'Eid al-Adha'
    if 'Eid al-Fitr' in name:
        return 'Eid al-Fitr'
    return name.strip()

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

                # Skip "Ramadan Start"
                if nom_jour_ferie == "Ramadan Start":
                    continue

                # Translate the day name to French
                if jour in day_translation:
                    jour = day_translation[jour]

                jours_feries.append({
                    'Date': parse_date(date),
                    'Jour': jour,
                    'Nom': normalize_holiday_name(nom_jour_ferie),
                })

        # Group holidays by normalized name and date range
        grouped_holidays = []
        holiday_map = {}

        for holiday in jours_feries:
            name = holiday['Nom']
            date = holiday['Date']

            if name not in holiday_map:
                holiday_map[name] = {'start': date, 'end': date}
            else:
                if date == holiday_map[name]['end'] + timedelta(days=1):
                    holiday_map[name]['end'] = date
                elif date > holiday_map[name]['end'] + timedelta(days=1):
                    # Add the current range to the grouped holidays and start a new range
                    grouped_holidays.append({
                        'Nom': name,
                        'Date Start': holiday_map[name]['start'].strftime('%d %b %Y'),
                        'Date End': holiday_map[name]['end'].strftime('%d %b %Y'),
                        'Days': (holiday_map[name]['end'] - holiday_map[name]['start']).days + 1
                    })
                    holiday_map[name] = {'start': date, 'end': date}

        # Add the last ranges to the grouped holidays
        for name, dates in holiday_map.items():
            grouped_holidays.append({
                'Nom': name,
                'Date Start': dates['start'].strftime('%d %b %Y'),
                'Date End': dates['end'].strftime('%d %b %Y'),
                'Days': (dates['end'] - dates['start']).days + 1
            })

        return grouped_holidays
    else:
        return []

@app.get("/api/holidays")
def get_holidays():
    holidays = recuperer_jours_feries()
    return holidays
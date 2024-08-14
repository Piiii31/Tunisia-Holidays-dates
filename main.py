from fastapi import FastAPI
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

app = FastAPI()

def fetch_holidays() -> List[Dict[str, str]]:
    current_year = datetime.now().year
    url = f"https://www.timeanddate.com/holidays/tunisia/{current_year}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'holidays-table'})
        rows = table.find_all('tr')
        holidays = []

        for row in rows[1:]:
            date_column = row.find('th')
            columns = row.find_all('td')

            if date_column and len(columns) >= 3:
                date = date_column.get_text(strip=True)
                day = columns[0].get_text(strip=True)
                holiday_name = columns[1].get_text(strip=True)
                holiday_type = columns[2].get_text(strip=True)

                holidays.append({
                    'Date': date,
                    'Day': day,
                    'Name': holiday_name,
                    'Type': holiday_type
                })

        return holidays
    else:
        return []

@app.get("/api/holidays")
def get_holidays():
    holidays = fetch_holidays()
    return holidays
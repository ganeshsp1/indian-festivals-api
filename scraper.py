import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import time

# Astrosage Regional Calendars
CALENDARS = {
    "national": "monthly-calendar",
    "kerala": "malayalam-calendar",
    "tamil-nadu": "tamil-calendar",
    "andhra-telangana": "telugu-calendar",
    "karnataka": "kannada-calendar",
    "maharashtra": "marathi-calendar",
    "west-bengal": "bengali-calendar",
    "gujarat": "gujarati-calendar"
}

MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]

def clean_date(date_raw, month_name, year="2026"):
    try:
        day_match = re.search(r'(\d+)', str(date_raw))
        if day_match:
            day = day_match.group(1)
            date_str = f"{day} {month_name} {year}"
            dt = datetime.strptime(date_str, "%d %B %Y")
            return dt.strftime("%Y-%m-%d")
        return str(date_raw)
    except:
        return str(date_raw)

def scrape_astrosage(calendar_key, calendar_slug, month_name, year="2026"):
    url = f"https://panchang.astrosage.com/calendars/{calendar_slug}?language=en&year={year}&month={month_name}"
    print(f"Scraping {calendar_key} - {month_name}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        target_table = None
        for t in tables:
            # Look for a table that has "Festivals" and month name in it
            text = t.get_text()
            if "Festivals" in text and month_name.title() in text:
                target_table = t
                break
        
        if not target_table:
            # Search again with less strict criteria
            for t in tables:
                if "Festivals" in t.get_text():
                    target_table = t
                    break

        if not target_table:
            return []
            
        festivals = []
        rows = target_table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) == 2:
                if "Festivals" in cols[1].get_text(): continue
                date_raw = cols[0].get_text(strip=True)
                festival_cell = cols[1]
                festival_links = festival_cell.find_all('a')
                if festival_links:
                    festival_names = [link.get_text(strip=True) for link in festival_links if link.get_text(strip=True)]
                    if festival_names:
                        full_name = ", ".join(festival_names)
                        festivals.append({
                            "date": clean_date(date_raw, month_name, year),
                            "name": full_name,
                            "state_proxy": calendar_key,
                            "month": month_name
                        })
        return festivals
    except Exception as e:
        print(f"  Error: {e}")
        return []

def main():
    years_to_scrape = [datetime.now().year]
    
    # If it's late in the year (Oct-Dec), also seed the next year
    if datetime.now().month >= 10:
        years_to_scrape.append(datetime.now().year + 1)

    for year_val in years_to_scrape:
        year_str = str(year_val)
        output_dir = f"data/{year_str}"
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n--- Processing Year: {year_str} ---")
        
        all_data = {}
        for state, slug in CALENDARS.items():
            state_festivals = []
            for month in MONTHS:
                month_data = scrape_astrosage(state, slug, month, year=year_str)
                state_festivals.extend(month_data)
                time.sleep(0.3) 
                
            if state_festivals:
                print(f"Total {state}: {len(state_festivals)}")
                with open(f"{output_dir}/{state}.json", "w") as f:
                    json.dump(state_festivals, f, indent=2)
                all_data[state] = state_festivals

        # Save year summary
        with open(f"{output_dir}/hindu_festivals_{year_str}_all_states.json", "w") as f:
            json.dump(all_data, f, indent=2)
            
        # If this is the 'fresher' year, update latest.json
        if year_val == datetime.now().year:
            with open("data/latest.json", "w") as f:
                json.dump(all_data, f, indent=2)

if __name__ == "__main__":
    main()

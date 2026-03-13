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

def scrape_astrosage_public_holidays(year="2026"):
    url = f"https://www.astrosage.com/{year}/public-holidays-{year}-eng.asp"
    print(f"Scraping Supplemental Holidays for {year}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    holidays_by_state = {}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) == 4:
                    date_text = cols[0].get_text(strip=True)
                    # Skip header row
                    if "Date" in date_text: continue
                    
                    name = cols[2].get_text(strip=True)
                    states_raw = cols[3].get_text(strip=True)
                    
                    # Parse date: "14 April, 2026"
                    clean_dt = date_text
                    try:
                        # Normalize date string for parsing
                        norm_date = date_text.replace(",", "").strip()
                        dt = datetime.strptime(norm_date, "%d %B %Y")
                        clean_dt = dt.strftime("%Y-%m-%d")
                        month_name = dt.strftime("%B").lower()
                    except:
                        month_name = "unknown"

                    # Split states and map them
                    states_list = [s.strip() for s in re.split(r',|&', states_raw)]
                    for state_name in states_list:
                        key = state_name.lower().replace(" ", "-")
                        
                        # Mapping
                        mapped_key = None
                        if "india" in key or "national" in key: mapped_key = "national"
                        elif "kerala" in key: mapped_key = "kerala"
                        elif "tamil" in key: mapped_key = "tamil-nadu"
                        elif "andhra" in key or "telangana" in key: mapped_key = "andhra-telangana"
                        elif "karnataka" in key: mapped_key = "karnataka"
                        elif "maharashtra" in key: mapped_key = "maharashtra"
                        elif "bengal" in key: mapped_key = "west-bengal"
                        elif "gujarat" in key: mapped_key = "gujarat"
                        
                        if mapped_key:
                            if mapped_key not in holidays_by_state:
                                holidays_by_state[mapped_key] = []
                            
                            holidays_by_state[mapped_key].append({
                                "date": clean_dt,
                                "name": name,
                                "state_proxy": mapped_key,
                                "month": month_name
                            })
        return holidays_by_state
    except Exception as e:
        print(f"  Error scraping public holidays: {e}")
        return {}

def merge_festivals(base_list, supplemental_list):
    # Use a set of (date, name) to avoid duplicates
    seen = set()
    merged = []
    
    for item in base_list:
        # Standardize name for comparison (remove spaces/special chars)
        norm = (item['date'], re.sub(r'\W+', '', item['name'].lower()))
        if norm not in seen:
            merged.append(item)
            seen.add(norm)
            
    for item in supplemental_list:
        norm = (item['date'], re.sub(r'\W+', '', item['name'].lower()))
        if norm not in seen:
            merged.append(item)
            seen.add(norm)
            
    # Sort by date
    merged.sort(key=lambda x: x['date'])
    return merged

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
        
        # 1. Fetch supplemental holidays first
        supplemental_data = scrape_astrosage_public_holidays(year=year_str)
        
        all_data = {}
        for state, slug in CALENDARS.items():
            # 2. Fetch regional panchang festivals
            state_festivals = []
            for month in MONTHS:
                month_data = scrape_astrosage(state, slug, month, year=year_str)
                state_festivals.extend(month_data)
                time.sleep(0.3) 
            
            # 3. Merge with supplemental regional holidays (vishu, baisakhi etc)
            supp_for_state = supplemental_data.get(state, [])
            merged_festivals = merge_festivals(state_festivals, supp_for_state)
                
            if merged_festivals:
                print(f"Total {state}: {len(merged_festivals)} (Merged {len(supp_for_state)} supplemental)")
                with open(f"{output_dir}/{state}.json", "w") as f:
                    json.dump(merged_festivals, f, indent=2)
                all_data[state] = merged_festivals

        # Save year summary
        with open(f"{output_dir}/hindu_festivals_{year_str}_all_states.json", "w") as f:
            json.dump(all_data, f, indent=2)
            
        # If this is the 'fresher' year, update latest.json
        if year_val == datetime.now().year:
            with open("data/latest.json", "w") as f:
                json.dump(all_data, f, indent=2)

if __name__ == "__main__":
    main()

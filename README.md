# 🪔 Hindu Festivals API (Panchang)

A programmatic, state-wise collection of Hindu festivals and public holidays in JSON format. This project automatically sources data every month from regional Panchang calendars and provides a clean API for developers building apps for the global Hindu community.

> [!IMPORTANT]
> This API specifically focuses on festivals tracked via the Hindu Lunar Calendar (Panchang).

## 🚀 How to use (API)

You don't need to clone this repo to use the data. Fetch the JSON directly via JSDelivr CDN:

**Latest Full Dataset:**  
`https://cdn.jsdelivr.net/gh/ganeshsp1/hindu-festivals-api/data/latest.json`

**Specific State (e.g., Kerala 2026):**  
`https://cdn.jsdelivr.net/gh/ganeshsp1/hindu-festivals-api/data/2026/kerala.json`

## 📊 Data Coverage

We aggregate data from multiple regional Panchang calendars to provide a proxy for state-wise observances:

*   **National:** Pan-India major festivals.
*   **Regional:** Maharashtra (Marathi), Karnataka (Kannada), Tamil Nadu (Tamil), Kerala (Malayalam), Andhra Pradesh/Telangana (Telugu), West Bengal (Bengali), and Gujarat (Gujarati).

## 🛠️ How it Works

1.  **Automated Scraper (`scraper.py`)**: A Python script that crawls regional panchang sources on Astrosage.
2.  **GitHub Actions**: A cron job runs on the 1st of every month to refresh the data.
3.  **Dynamic Yearing**: In the last quarter of every year, the scraper automatically seeds the upcoming year's data.

## 📝 Data Structure

```json
{
  "date": "2026-03-19",
  "name": "Ugadi, Gudi Padwa",
  "state_proxy": "maharashtra",
  "month": "march"
}
```

## 🤝 Contributing

We welcome contributions! You can help by:
*   **Fixing Logic**: Improving the `scraper.py` to handle edge cases or new source structures.
*   **Adding Regions**: Identifying more regional calendar slugs to improve accuracy.
*   **Manual Overrides**: Adding localized festivals that aren't appearing in the automated panchang.

### Local Setup
1. Clone the repo
2. `pip install -r requirements.txt`
3. `python scraper.py`

## 📜 License
MIT License. Feel free to use this in your projects.

---
*Data sourced from publicly available Panchang calendars. Please verify dates locally for specific religious ceremonies.*

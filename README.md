# 🪔 Indian Festivals API

A programmatic, state-wise collection of Indian festivals and public holidays in JSON format. This project automatically sources data every month and provides a clean API for developers building apps for the Indian community.

> [!IMPORTANT]
> This is a community-driven project aiming to bridge the gap in open-source festival data for India.

## 🚀 How to use (API)

You don't need to clone this repo to use the data. Fetch the JSON directly via JSDelivr CDN:

**Latest Full Dataset:**  
`https://cdn.jsdelivr.net/gh/ganeshsp1/indian-festivals-api/data/latest.json`

**Specific State (e.g., Kerala 2026):**  
`https://cdn.jsdelivr.net/gh/ganeshsp1/indian-festivals-api/data/2026/kerala.json`

## 📊 Data Coverage

We currently aggregate data from multiple regional calendars to provide a proxy for state-wise observances:

*   **National:** Pan-India gazetted holidays.
*   **Regional:** Maharashtra, Karnataka, Tamil Nadu, Kerala, Andhra Pradesh/Telangana, West Bengal, and Gujarat.

## 🛠️ How it Works

1.  **Automated Scraper (`scraper.py`)**: A Python script that crawls reputable calendar sources.
2.  **GitHub Actions**: A cron job runs on the 1st of every month to refresh the data.
3.  **Dynamic Yearing**: In the last quarter of every year, the scraper automatically seeds the upcoming year's data.

## 📝 Data Structure

```json
{
  "date": "2026-01-14",
  "name": "Pongal, Makar Sankranti",
  "state_proxy": "tamil-nadu",
  "month": "january"
}
```

## 🤝 Contributing

We welcome contributions! You can help by:
*   **Fixing Logic**: Improving the `scraper.py` to handle edge cases or new source structures.
*   **Adding Sources**: Identifying more state-specific URLs to improve regional accuracy.
*   **Manual Overrides**: Adding localized festivals that aren't appearing in the automated scrape.

### Local Setup
1. Clone the repo
2. `pip install -r requirements.txt`
3. `python scraper.py`

## 📜 License
MIT License. Feel free to use this in your commercial or personal projects.

---
*Data sourced from publicly available calendars. Please verify dates locally for religious ceremonies.*

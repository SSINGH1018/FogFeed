# 🤖 Automated Lofty.ai Scraper

## TL;DR - Get Started in 30 Seconds

```bash
cd /path/to/FogFeed
./start_lofty_scraper.sh
```

That's it! The scraper now runs automatically every 3 hours.

---

## What This Does

✅ Scrapes all 145+ Lofty.ai properties automatically  
✅ Downloads 12-16 documents per property (appraisals, leases, inspections, etc.)  
✅ Runs every 3 hours in the background  
✅ Saves data in JSON and CSV formats  
✅ Detects new property listings  
✅ Logs all activity  

---

## Commands

### Start Scraper
```bash
./start_lofty_scraper.sh
```

### Check Status
```bash
./status_lofty_scraper.sh
```

### Stop Scraper
```bash
./stop_lofty_scraper.sh
```

### View Live Logs
```bash
tail -f logs/lofty_scraper.log
```

---

## Configuration

Edit `.env` file to change interval:

```bash
# Run every 6 hours instead of 3
SCRAPER_INTERVAL_HOURS=6
```

---

## Where's My Data?

```
data/lofty/
├── properties_TIMESTAMP.json    ← All property data
├── properties_TIMESTAMP.csv     ← Spreadsheet format
└── documents/                   ← All PDFs (appraisals, leases, etc.)
```

---

## Using the Data

### Python
```python
from api import PropertyDataAPI

api = PropertyDataAPI()
properties = api.get_all_properties(platform='lofty')
print(f"Found {len(properties)} properties")
```

### JavaScript/Frontend
```javascript
// Load the latest JSON file
import properties from './data/lofty/properties_latest.json';
```

### Excel/Sheets
Open `data/lofty/properties_TIMESTAMP.csv`

---

## Troubleshooting

**Scraper won't start?**
```bash
./stop_lofty_scraper.sh  # Clean up
./start_lofty_scraper.sh  # Restart
```

**Check for errors:**
```bash
tail -50 logs/lofty_scraper.log
```

**Test manually:**
```bash
python3 run_all_scrapers.py --platforms lofty
```

---

## Full Documentation

- **LOFTY_AUTOMATION_GUIDE.md** - Complete automation guide
- **README.md** - Project overview
- **INTEGRATION_GUIDE.md** - Integration with your website

---

## What Gets Scraped?

For each property:
- Address, city, state
- Price, returns, yields
- Bedrooms, bathrooms, sqft
- Property type, year built
- Monthly rent, lease terms
- 10+ property images
- 12-16 documents:
  - Appraisal
  - Inspection report
  - Lease agreement
  - Insurance policy
  - Property management agreement
  - Operating agreement
  - Title documents
  - Transaction data
  - Offering documents
  - And more...

---

## Performance

- **Time per scrape**: 30-60 minutes
- **Recommended interval**: 3-6 hours
- **Data size**: ~50-100 MB per scrape

---

## Need Help?

1. Check logs: `tail -f logs/lofty_scraper.log`
2. Read LOFTY_AUTOMATION_GUIDE.md
3. Review INTEGRATION_GUIDE.md

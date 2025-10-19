# Lofty.ai Automated Scraper Guide

## Overview

This guide explains how to run the Lofty.ai scraper automatically every few hours. The scraper will:
- Scrape all 145+ properties from Lofty.ai marketplace
- Download all property documents (12-16 PDFs per property)
- Save data in JSON and CSV formats
- Detect new listings automatically
- Run continuously in the background

## Quick Start

### 1. Start the Automated Scraper

```bash
cd /path/to/FogFeed
./start_lofty_scraper.sh
```

This will:
- Start the scraper in the background
- Run immediately on startup
- Schedule automatic runs every 3 hours (configurable)
- Log all activity to `logs/lofty_scraper.log`

### 2. Check Status

```bash
./status_lofty_scraper.sh
```

This shows:
- Whether the scraper is running
- When it last ran
- How many properties were scraped
- Recent log entries

### 3. Stop the Scraper

```bash
./stop_lofty_scraper.sh
```

## Configuration

### Change Scraping Interval

Edit the `.env` file:

```bash
# Run every 6 hours instead of 3
SCRAPER_INTERVAL_HOURS=6
```

Or set it when starting:

```bash
SCRAPER_INTERVAL_HOURS=6 ./start_lofty_scraper.sh
```

### View Logs in Real-Time

```bash
tail -f logs/lofty_scraper.log
```

## Output Data

### Directory Structure

```
FogFeed/
├── data/
│   └── lofty/
│       ├── properties_20251019_195500.json    # All property data
│       ├── properties_20251019_195500.csv     # Spreadsheet format
│       ├── property_history.json              # Track new listings
│       └── documents/                         # All downloaded PDFs
│           ├── property1_appraisal_1.pdf
│           ├── property1_inspection_1.pdf
│           ├── property1_lease_1.pdf
│           └── ...
└── logs/
    └── lofty_scraper.log                      # Scraper activity log
```

### Property Data Format

Each property includes:

```json
{
  "platform": "Lofty.ai",
  "url": "https://www.lofty.ai/property_deal/...",
  "property_id": "2489-Charlene-Ct_Macon-GA-31206",
  "title": "2489 Charlene Ct",
  "city_state": "Macon, GA",
  "estimated_price": "$150,000",
  "projected_annual_return": "10.52%",
  "rental_yield": "8.5%",
  "bedrooms": "5",
  "bathrooms": "3",
  "square_feet": "2400",
  "property_type": "Single family",
  "year_built": "1995",
  "monthly_rent": "$1,500",
  "images": ["url1", "url2", ...],
  "documents": {
    "appraisal": [{"url": "...", "label": "Appraisal"}],
    "inspection": [{"url": "...", "label": "Inspection Report"}],
    "lease": [{"url": "...", "label": "Lease Agreement"}],
    "insurance": [{"url": "...", "label": "Insurance Policy"}],
    "property_management": [{"url": "...", "label": "PM Agreement"}],
    "operating_agreement": [{"url": "...", "label": "Operating Agreement"}],
    "title_documents": [{"url": "...", "label": "Title"}],
    "transaction_data": [{"url": "...", "label": "Transaction Data"}],
    "offering_document": [{"url": "...", "label": "Offering"}]
  },
  "document_count": 12,
  "scraped_at": "2025-10-19 19:55:00"
}
```

## Using the Data

### Option 1: Python API

```python
from api import PropertyDataAPI

api = PropertyDataAPI()

# Get all Lofty properties
properties = api.get_all_properties(platform='lofty')

# Search for high-return properties
high_return = api.search_properties(min_return=15.0)

# Get properties in specific location
florida_props = api.search_properties(location='FL')

# Get platform statistics
stats = api.get_platform_stats()
print(f"Lofty properties: {stats['lofty']['total_properties']}")
```

### Option 2: Direct JSON Access

```python
import json
from pathlib import Path

# Load latest properties file
data_dir = Path('data/lofty')
json_files = list(data_dir.glob('properties_*.json'))
latest_file = max(json_files, key=lambda f: f.stat().st_mtime)

with open(latest_file) as f:
    properties = json.load(f)

print(f"Loaded {len(properties)} properties")
```

### Option 3: CSV for Excel/Sheets

Open the latest `properties_*.csv` file in Excel, Google Sheets, or any spreadsheet application.

## Troubleshooting

### Scraper Won't Start

```bash
# Check if already running
./status_lofty_scraper.sh

# If stuck, force stop and restart
./stop_lofty_scraper.sh
./start_lofty_scraper.sh
```

### Check for Errors

```bash
# View recent logs
tail -50 logs/lofty_scraper.log

# Search for errors
grep -i error logs/lofty_scraper.log
```

### Scraper Stopped Unexpectedly

The scraper might have crashed. Check the logs and restart:

```bash
./stop_lofty_scraper.sh  # Clean up
./start_lofty_scraper.sh  # Restart
```

### No Data Being Scraped

1. Check if Chrome/Chromium is installed:
   ```bash
   which google-chrome || which chromium-browser
   ```

2. Verify dependencies are installed:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Test the scraper manually:
   ```bash
   python3 run_all_scrapers.py --platforms lofty
   ```

## Advanced Usage

### Run Scraper Once Manually

```bash
python3 run_all_scrapers.py --platforms lofty
```

### Test with Enhanced Scraper

```bash
python3 scrapers/lofty_scraper_enhanced.py
```

### Run All Platform Scrapers

```bash
python3 run_all_scrapers.py
```

### Include Additional Platforms

```bash
# Include Propbase (requires credentials in .env)
python3 run_all_scrapers.py --include-propbase

# Include RealT (requires proxy for US users)
python3 run_all_scrapers.py --include-realt
```

## Automation with Systemd (Optional)

For production servers, you can create a systemd service:

1. Create service file `/etc/systemd/system/lofty-scraper.service`:

```ini
[Unit]
Description=Lofty.ai Property Scraper
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/repos/FogFeed
Environment="SCRAPER_INTERVAL_HOURS=3"
ExecStart=/usr/bin/python3 /home/ubuntu/repos/FogFeed/run_lofty_scheduler.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

2. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable lofty-scraper
sudo systemctl start lofty-scraper
sudo systemctl status lofty-scraper
```

## GitHub Actions (Cloud Automation)

The repository includes GitHub Actions workflow that runs automatically every 6 hours. See `.github/workflows/scrape-properties.yml`.

To enable:
1. Push your code to GitHub
2. The workflow runs automatically
3. Data is committed back to the repository

## Performance Notes

- **Full scrape time**: ~30-60 minutes for all 145+ properties
- **Data size**: ~50-100 MB per scrape (including PDFs)
- **Recommended interval**: 3-6 hours
- **Network usage**: ~100-200 MB per scrape

## Support

For issues or questions:
1. Check the logs: `tail -f logs/lofty_scraper.log`
2. Review the main README.md
3. See INTEGRATION_GUIDE.md for more details

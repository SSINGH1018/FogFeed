# RWA Property Scraper - FogFeed Integration

Automated scraping system for tokenized real estate platforms, ready to integrate into your FogFeed project.

## 🚀 Quick Start

1. **Copy all files** from this folder into your FogFeed repository
2. **Set GitHub secrets** (see INTEGRATION_GUIDE.md)
3. **Push to GitHub** - scraping starts automatically!

## 📦 What It Does

- Scrapes 7 tokenized real estate platforms every 6 hours
- Downloads all property documents (PDFs, images, reports)
- Detects new listings automatically
- Saves data in JSON/CSV format
- Provides API for your website to access data

## 🏢 Platforms Covered

1. **Lofty.ai** - 146+ US residential properties
2. **Reental.co** - International properties
3. **Fraxtor** - Singapore/global real estate
4. **Binaryx** - Asia-Pacific properties
5. **Mogul.club** - US properties
6. **Propbase.app** - Marketplace (credentials configured)
7. **RealT** - US properties (optional, needs proxy)

## 📖 Full Documentation

See **INTEGRATION_GUIDE.md** for:
- Step-by-step integration instructions
- API usage examples
- Data structure reference
- Configuration options
- Troubleshooting guide

## 🎯 Collected Data Per Property

- Complete property details (beds, baths, sqft, type)
- Financial metrics (returns, yields, rent, loan details)
- 10+ property images
- 12-16 documents per property:
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

## ⚡ Usage

### Automatic (GitHub Actions)
Runs every 6 hours automatically after setup.

### Manual
```bash
python run_all_scrapers.py --include-propbase
```

### API
```python
from api import PropertyDataAPI

api = PropertyDataAPI()
properties = api.get_all_properties()
```

## 🔧 Requirements

- Python 3.8+
- Chrome/Chromium browser
- Dependencies in `requirements.txt`

## 📁 Output Structure

```
data/
├── lofty/
│   ├── properties_TIMESTAMP.json
│   ├── properties_TIMESTAMP.csv
│   └── documents/
│       └── [all PDFs]
├── reental/
├── fraxtor/
└── ...
```

## 🎉 Ready to Go!

Follow INTEGRATION_GUIDE.md for complete setup instructions.

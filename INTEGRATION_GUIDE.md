# FogFeed Integration Guide

## 📦 What's Included

This package contains a complete RWA property scraping system ready to integrate into your FogFeed project:

- **7 Platform Scrapers**: Lofty, Reental, Fraxtor, Binaryx, Mogul, Propbase, RealT
- **GitHub Actions**: Automated scraping every 6 hours
- **API Layer**: Ready-to-use API for serving property data to your website
- **Comprehensive Data**: Full property details, financials, images, and PDFs

## 🚀 Quick Integration (5 Steps)

### Step 1: Copy Files to Your FogFeed Repo

Copy these folders/files into your FogFeed repository:

```
FogFeed/
├── .github/
│   └── workflows/
│       └── scrape-properties.yml    ← Copy this
├── scrapers/                         ← Copy entire folder
├── base_scraper.py                   ← Copy this
├── run_all_scrapers.py              ← Copy this
├── api.py                            ← Copy this  
├── requirements.txt                  ← Merge with yours
└── .env.example                      ← Copy and rename to .env
```

### Step 2: Set Up GitHub Secrets

Your scrapers need credentials. Add these secrets to your GitHub repo:

1. Go to: `https://github.com/SSINGH1018/FogFeed/settings/secrets/actions`
2. Click "New repository secret"
3. Add these secrets:

   - **PROPBASE_EMAIL**: `rwafogfeed@gmail.com`
   - **PROPBASE_PASSWORD**: `FogFeed$12`
   - **(Optional) PROXY_URL**: For RealT if you want to scrape it from US

### Step 3: Enable GitHub Actions

1. Go to `https://github.com/SSINGH1018/FogFeed/actions`
2. Enable workflows if not already enabled
3. The scraper will now run automatically every 6 hours!

### Step 4: Manual First Run (Optional)

Trigger the first scrape manually:

1. Go to Actions tab
2. Click "Scrape RWA Properties"
3. Click "Run workflow"
4. Wait 10-30 minutes for first scrape

OR run locally:
```bash
cd FogFeed
pip install -r requirements.txt
python run_all_scrapers.py --include-propbase
```

### Step 5: Use the Data in Your Website

The scraped data will be in `data/` folder, organized by platform:

```
data/
├── lofty/
│   ├── properties_20251018_200000.json
│   ├── properties_20251018_200000.csv
│   └── documents/
│       ├── property1_appraisal_1.pdf
│       ├── property1_lease_1.pdf
│       └── ...
├── reental/
├── fraxtor/
├── binaryx/
├── mogul/
└── propbase/
```

## 💻 Using the API in Your Code

### Option A: Direct File Access (Simplest)

```javascript
// In your Next.js/React code
import properties from './data/lofty/properties_latest.json';

function PropertyList() {
  return (
    <div>
      {properties.map(prop => (
        <PropertyCard 
          key={prop.property_id}
          title={prop.title}
          location={prop.city_state}
          return={prop.projected_annual_return}
          images={prop.images}
          documents={prop.documents}
        />
      ))}
    </div>
  );
}
```

### Option B: Python API (Recommended)

```python
from api import PropertyDataAPI

api = PropertyDataAPI()

# Get all properties
all_properties = api.get_all_properties()

# Get properties from specific platform
lofty_properties = api.get_all_properties(platform='lofty')

# Search with filters
high_return_props = api.search_properties(min_return=15.0)
florida_props = api.search_properties(location='FL')

# Get new properties (last 7 days)
new_listings = api.get_new_properties()

# Get platform statistics
stats = api.get_platform_stats()
```

### Option C: FastAPI REST API (For Frontend)

Add to your backend (if you have FastAPI):

```python
from fastapi import FastAPI
from api import PropertyDataAPI

app = FastAPI()
api = PropertyDataAPI()

@app.get("/api/properties")
def get_properties(platform: str = None):
    return api.get_all_properties(platform=platform)

@app.get("/api/properties/{property_id}")
def get_property(property_id: str):
    return api.get_property_by_id(property_id)

@app.get("/api/search")
def search(min_return: float = None, location: str = None):
    return api.search_properties(min_return=min_return, location=location)
```

Then call from your frontend:
```javascript
// Fetch all properties
fetch('/api/properties')
  .then(res => res.json())
  .then(properties => console.log(properties));

// Search properties
fetch('/api/search?min_return=15&location=FL')
  .then(res => res.json())
  .then(filtered => console.log(filtered));
```

## 📊 Data Structure

Each property includes:

```json
{
  "platform": "Lofty.ai",
  "property_id": "2489-Charlene-Ct_Macon-GA-31206",
  "url": "https://www.lofty.ai/property_deal/...",
  "title": "2489 Charlene Ct",
  "address": "2489 Charlene Ct",
  "city_state": "Macon, GA 31206",
  "projected_annual_return": "10.52%",
  "rental_yield": "14.71%",
  "bedrooms": "5",
  "bathrooms": "3",
  "square_feet": "1924",
  "property_type": "Single family",
  "year_built": "2010",
  "monthly_rent": "$1,700",
  "lease_term": "1 year lease",
  "security_deposit": "$2,000",
  "loan_amount": "$153,316.98",
  "mortgage_rate": "5.99%",
  "niche_rating": "C",
  "images": [
    "https://images.lofty.ai/...",
    ...
  ],
  "documents": {
    "appraisal": [{"url": "...", "label": "Appraisal"}],
    "inspection": [{"url": "...", "label": "Inspection Report"}],
    "lease": [{"url": "...", "label": "Lease Agreement"}],
    "insurance": [{"url": "...", "label": "Insurance Policy"}],
    "property_management": [{"url": "...", "label": "Management Agreement"}],
    "operating_agreement": [{"url": "...", "label": "Operating Agreement"}],
    "title_documents": [{"url": "...", "label": "Title Report"}],
    "transaction_data": [{"url": "...", "label": "Transaction Data"}],
    "offering_document": [{"url": "...", "label": "Offering Document"}]
  },
  "document_count": 12,
  "scraped_at": "2025-10-18 19:59:56"
}
```

## ⚙️ Configuration

### Change Scraping Frequency

Edit `.github/workflows/scrape-properties.yml`:

```yaml
schedule:
  # Every hour
  - cron: '0 * * * *'
  
  # Every 6 hours (default)
  - cron: '0 */6 * * *'
  
  # Daily at midnight
  - cron: '0 0 * * *'
```

### Select Specific Platforms

Edit `run_all_scrapers.py` or run manually:

```bash
# Run only Lofty and Reental
python run_all_scrapers.py --platforms lofty reental

# Run all including Propbase
python run_all_scrapers.py --include-propbase

# Run all including RealT (needs proxy)
python run_all_scrapers.py --include-realt
```

## 🎯 New Property Alerts

The system automatically detects new properties. To get notified:

### Option 1: GitHub Issues (Automated)

Add to `.github/workflows/scrape-properties.yml` after the scraping step:

```yaml
- name: Check for new properties
  run: |
    python check_new_properties.py
    # This will create GitHub issues for new listings
```

### Option 2: Email Notifications

Use a service like SendGrid:

```python
from api import PropertyDataAPI

api = PropertyDataAPI()
new_props = api.get_new_properties()

if new_props:
    send_email(
        subject=f"🆕 {len(new_props)} New Properties!",
        body=format_properties(new_props)
    )
```

## 🐛 Troubleshooting

### GitHub Actions Failing?

1. Check Actions tab for error logs
2. Verify secrets are set correctly
3. Make sure `data/` directory exists in repo

### No Data Showing Up?

1. Check if workflow has run (Actions tab)
2. Look in `data/` folder for JSON files
3. Run manually to test: `python run_all_scrapers.py`

### Want to Test Locally First?

```bash
# Clone your repo
git clone https://github.com/SSINGH1018/FogFeed.git
cd FogFeed

# Install dependencies
pip install -r requirements.txt

# Run scraper
python run_all_scrapers.py --include-propbase

# Check data
ls data/lofty/
```

## 📈 Scaling Up

### Add More Platforms

1. Create new scraper in `scrapers/` (use `lofty_scraper.py` as template)
2. Add to `run_all_scrapers.py`
3. Done!

### Store in Database

Modify scrapers to push to your database instead of files:

```python
# In base_scraper.py
def save_properties(self):
    for prop in self.properties:
        db.insert('properties', prop)
```

### Build Dashboard

Create a dashboard to visualize:
- Total properties across platforms
- Average returns by platform
- New listings timeline
- Market trends

## 🎉 You're All Set!

Your FogFeed website now has:
- ✅ Automated scraping every 6 hours
- ✅ 7 tokenized real estate platforms
- ✅ Complete property data + PDFs
- ✅ Auto-detection of new listings
- ✅ Ready-to-use API

Questions? Check the main README.md or test the scrapers locally first!

#!/bin/bash

echo "🚀 Setting up RWA Property Scraper for FogFeed..."
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt -q

echo "✅ Dependencies installed"

if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials"
fi

echo ""
echo "📁 Creating data directory..."
mkdir -p data

echo "✅ Data directory created"

echo ""
echo "🧪 Testing scraper setup..."
python3 -c "from scrapers.lofty_scraper import LoftyScraperEnhanced; print('✅ Scraper imports working!')"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials (if needed)"
echo "2. Run: python3 run_all_scrapers.py --include-propbase"
echo "3. Or set up GitHub Actions (see INTEGRATION_GUIDE.md)"
echo ""

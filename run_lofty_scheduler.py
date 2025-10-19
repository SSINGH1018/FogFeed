"""
Automated scheduler for Lofty.ai scraper
Runs the scraper every few hours automatically
"""
import sys
import os
import time
import schedule
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.lofty_scraper_enhanced import LoftyScraperEnhanced


def run_lofty_scraper():
    """Run the Lofty scraper"""
    print("\n" + "="*80)
    print(f"🏢 LOFTY.AI AUTOMATED SCRAPER")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    try:
        scraper = LoftyScraperEnhanced()
        scraper.run(full_scrape=True)
        
        print("\n✅ Lofty scraper completed successfully!")
        print(f"Next run scheduled in {INTERVAL_HOURS} hours")
        
    except Exception as e:
        print(f"\n❌ Error running Lofty scraper: {str(e)}")
        print("Will retry at next scheduled time")


def main():
    """Main scheduler loop"""
    print("\n" + "="*80)
    print("🤖 LOFTY.AI AUTOMATED SCRAPER - STARTED")
    print("="*80)
    print(f"\n⏰ Schedule: Every {INTERVAL_HOURS} hours")
    print(f"📍 Data directory: data/lofty/")
    print(f"🚀 First run: Starting now...")
    print("\n" + "="*80 + "\n")
    
    run_lofty_scraper()
    
    schedule.every(INTERVAL_HOURS).hours.do(run_lofty_scraper)
    
    print("\n" + "="*80)
    print("⏳ Scheduler running... Press Ctrl+C to stop")
    print("="*80 + "\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    INTERVAL_HOURS = int(os.getenv('SCRAPER_INTERVAL_HOURS', '3'))  # Default: 3 hours
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("🛑 Scheduler stopped by user")
        print("="*80 + "\n")
        sys.exit(0)

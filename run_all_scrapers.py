"""
Main script to run all RWA platform scrapers
"""
import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

from scrapers.lofty_scraper import LoftyScraper
from scrapers.reental_scraper import ReentalScraper
from scrapers.fraxtor_scraper import FraxtorScraper
from scrapers.binaryx_scraper import BinaryxScraper
from scrapers.mogul_scraper import MogulScraper
from scrapers.realt_scraper import RealTScraper
from scrapers.propbase_scraper import PropbaseScraper


def run_all_scrapers(include_realt=False, include_propbase=False):
    """Run all platform scrapers"""
    
    print("\n" + "="*80)
    print("RWA TOKENIZED REAL ESTATE AGGREGATOR")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    scrapers = []
    
    scrapers.append(('Lofty.ai', LoftyScraper()))
    scrapers.append(('Reental.co', ReentalScraper()))
    scrapers.append(('Fraxtor', FraxtorScraper()))
    scrapers.append(('Binaryx', BinaryxScraper()))
    scrapers.append(('Mogul.club', MogulScraper()))
    
    if include_realt:
        scrapers.append(('RealT', RealTScraper(use_proxy=False)))
    else:
        print("⏭️  Skipping RealT (blocks US IPs - set include_realt=True and configure proxy to enable)")
    
    if include_propbase:
        scrapers.append(('Propbase.app', PropbaseScraper()))
    else:
        print("⏭️  Skipping Propbase (requires login - set include_propbase=True and configure credentials to enable)")
    
    print(f"\n📊 Running {len(scrapers)} scrapers...")
    print("-"*80 + "\n")
    
    results = {}
    
    for platform_name, scraper in scrapers:
        try:
            print(f"\n{'='*80}")
            print(f"🏢 {platform_name}")
            print(f"{'='*80}\n")
            
            start_time = time.time()
            scraper.run(full_scrape=True)
            elapsed_time = time.time() - start_time
            
            results[platform_name] = {
                'status': 'success',
                'properties_count': len(scraper.properties),
                'elapsed_time': f"{elapsed_time:.2f}s"
            }
            
            print(f"\n✅ {platform_name} completed in {elapsed_time:.2f}s")
            print(f"   Found {len(scraper.properties)} properties")
            
        except Exception as e:
            print(f"\n❌ Error scraping {platform_name}: {str(e)}")
            results[platform_name] = {
                'status': 'failed',
                'error': str(e)
            }
        
        if scraper != scrapers[-1][1]:
            print("\n⏸️  Pausing 5 seconds before next platform...")
            time.sleep(5)
    
    print("\n\n" + "="*80)
    print("SCRAPING SUMMARY")
    print("="*80)
    
    total_properties = 0
    successful = 0
    failed = 0
    
    for platform, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        print(f"\n{status_icon} {platform}: {result['status'].upper()}")
        
        if result['status'] == 'success':
            successful += 1
            print(f"   Properties: {result['properties_count']}")
            print(f"   Time: {result['elapsed_time']}")
            total_properties += result['properties_count']
        else:
            failed += 1
            print(f"   Error: {result['error']}")
    
    print("\n" + "-"*80)
    print(f"\n📈 Total Statistics:")
    print(f"   Platforms scraped: {successful}/{len(results)}")
    print(f"   Total properties: {total_properties}")
    print(f"   Failed: {failed}")
    print(f"\n   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80 + "\n")
    
    return results


def run_scrapers_for_platform(platform_names):
    """Run scrapers for specific platforms only"""
    platform_map = {
        'lofty': LoftyScraper(),
        'reental': ReentalScraper(),
        'fraxtor': FraxtorScraper(),
        'binaryx': BinaryxScraper(),
        'mogul': MogulScraper(),
        'realt': RealTScraper(use_proxy=False),
        'propbase': PropbaseScraper()
    }
    
    for platform_name in platform_names:
        platform_key = platform_name.lower()
        if platform_key in platform_map:
            scraper = platform_map[platform_key]
            print(f"\n🏢 Running {platform_name} scraper...")
            scraper.run(full_scrape=True)
        else:
            print(f"❌ Unknown platform: {platform_name}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RWA Tokenized Real Estate Aggregator')
    parser.add_argument('--include-realt', action='store_true', help='Include RealT (requires proxy for US users)')
    parser.add_argument('--include-propbase', action='store_true', help='Include Propbase (requires login credentials)')
    parser.add_argument('--platforms', nargs='+', help='Run specific platforms only (e.g., lofty reental)')
    
    args = parser.parse_args()
    
    if args.platforms:
        run_scrapers_for_platform(args.platforms)
    else:
        run_all_scrapers(
            include_realt=args.include_realt,
            include_propbase=args.include_propbase
        )

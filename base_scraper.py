"""
Base scraper class for RWA tokenized real estate platforms
"""
import os
import json
import time
import requests
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class BaseScraper(ABC):
    """Base class for all platform scrapers"""
    
    def __init__(self, platform_name: str, base_url: str, use_proxy: bool = False):
        self.platform_name = platform_name
        self.base_url = base_url
        self.use_proxy = use_proxy
        self.driver = None
        self.properties = []
        self.output_dir = f"data/{platform_name}"
        self.documents_dir = f"data/{platform_name}/documents"
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.documents_dir, exist_ok=True)
        
    def setup_driver(self, headless: bool = True):
        """Setup Selenium WebDriver with Chrome"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        if self.use_proxy:
            proxy_url = os.getenv('PROXY_URL')
            if proxy_url:
                chrome_options.add_argument(f'--proxy-server={proxy_url}')
        
        try:
            # Try using ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.implicitly_wait(10)
        
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def download_file(self, url: str, filename: str) -> Optional[str]:
        """Download a file (PDF, image, etc.) from a URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            filepath = os.path.join(self.documents_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filename}")
            return filepath
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return None
    
    def save_properties(self, format: str = 'json'):
        """Save scraped properties to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            filepath = os.path.join(self.output_dir, f"properties_{timestamp}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.properties, f, indent=2, ensure_ascii=False)
        elif format == 'csv':
            import pandas as pd
            filepath = os.path.join(self.output_dir, f"properties_{timestamp}.csv")
            df = pd.DataFrame(self.properties)
            df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"Saved {len(self.properties)} properties to {filepath}")
        return filepath
    
    def load_previous_properties(self) -> set:
        """Load previously scraped property IDs to detect new listings"""
        history_file = os.path.join(self.output_dir, 'property_history.json')
        
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
                return set(history.get('property_ids', []))
        
        return set()
    
    def update_property_history(self):
        """Update the history file with current property IDs"""
        history_file = os.path.join(self.output_dir, 'property_history.json')
        
        current_ids = [prop.get('property_id') or prop.get('url') for prop in self.properties]
        
        history = {
            'last_updated': datetime.now().isoformat(),
            'property_ids': current_ids,
            'total_count': len(current_ids)
        }
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def detect_new_properties(self) -> List[Dict]:
        """Detect new properties compared to previous scrape"""
        previous_ids = self.load_previous_properties()
        
        new_properties = []
        for prop in self.properties:
            prop_id = prop.get('property_id') or prop.get('url')
            if prop_id not in previous_ids:
                new_properties.append(prop)
        
        return new_properties
    
    @abstractmethod
    def scrape_marketplace(self) -> List[Dict]:
        """Scrape the marketplace listings - must be implemented by each platform"""
        pass
    
    @abstractmethod
    def scrape_property_details(self, property_url: str) -> Dict:
        """Scrape detailed information for a single property - must be implemented by each platform"""
        pass
    
    def run(self, full_scrape: bool = True):
        """Main execution method"""
        print(f"\n{'='*60}")
        print(f"Starting scrape for {self.platform_name}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        try:
            self.setup_driver(headless=True)
            
            print(f"Scraping marketplace listings...")
            property_urls = self.scrape_marketplace()
            print(f"Found {len(property_urls)} properties")
            
            if full_scrape:
                print(f"\nScraping detailed information...")
                for i, prop_url in enumerate(property_urls, 1):
                    print(f"[{i}/{len(property_urls)}] Scraping {prop_url}")
                    try:
                        details = self.scrape_property_details(prop_url)
                        if details:
                            self.properties.append(details)
                        time.sleep(2)  # Be respectful to servers
                    except Exception as e:
                        print(f"Error scraping {prop_url}: {str(e)}")
                        continue
            
            self.save_properties(format='json')
            self.save_properties(format='csv')
            
            new_props = self.detect_new_properties()
            if new_props:
                print(f"\n🆕 Found {len(new_props)} NEW properties!")
                for prop in new_props:
                    print(f"  - {prop.get('title', 'Unknown')}")
            
            self.update_property_history()
            
            print(f"\n{'='*60}")
            print(f"Scraping completed for {self.platform_name}")
            print(f"Total properties: {len(self.properties)}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
            raise
        finally:
            self.close_driver()

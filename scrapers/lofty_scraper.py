"""
Scraper for Lofty.ai tokenized real estate platform
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import re
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base_scraper import BaseScraper


class LoftyScraper(BaseScraper):
    """Scraper for Lofty.ai platform"""
    
    def __init__(self):
        super().__init__(
            platform_name="lofty",
            base_url="https://www.lofty.ai"
        )
        self.marketplace_url = f"{self.base_url}/marketplace"
    
    def scrape_marketplace(self) -> List[str]:
        """Scrape all property URLs from the marketplace"""
        self.driver.get(self.marketplace_url)
        time.sleep(3)  # Wait for page to load
        
        property_urls = []
        
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/property_deal/']")
            
            for element in property_elements:
                url = element.get_attribute('href')
                if url and url not in property_urls:
                    property_urls.append(url)
            
        except Exception as e:
            print(f"Error scraping marketplace: {str(e)}")
        
        return property_urls
    
    def scrape_property_details(self, property_url: str) -> Dict:
        """Scrape detailed information for a single property"""
        self.driver.get(property_url)
        time.sleep(3)
        
        property_data = {
            'platform': 'Lofty.ai',
            'url': property_url,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'property_id': property_url.split('/')[-1]
        }
        
        try:
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                property_data['title'] = title
                property_data['address'] = title  # Address is usually in the title
            except:
                pass
            
            try:
                metrics = self.driver.find_elements(By.CSS_SELECTOR, "[class*='metric'], [class*='stat'], [class*='value']")
                
                for metric in metrics:
                    text = metric.text
                    
                    if '$' in text and 'price' not in property_data:
                        property_data['price'] = text
                    elif '%' in text and 'yield' not in property_data:
                        property_data['yield'] = text
                    elif 'APY' in text or 'Return' in text:
                        property_data['annual_return'] = text
                    elif 'Token' in text:
                        property_data['token_info'] = text
            except:
                pass
            
            try:
                details_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='detail'], div[class*='info']")
                
                for element in details_elements:
                    text = element.text
                    if 'Bed' in text or 'bed' in text:
                        property_data['bedrooms'] = text
                    elif 'Bath' in text or 'bath' in text:
                        property_data['bathrooms'] = text
                    elif 'sqft' in text or 'sq ft' in text:
                        property_data['square_feet'] = text
                    elif 'Year Built' in text or 'year built' in text:
                        property_data['year_built'] = text
            except:
                pass
            
            try:
                rental_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Rental') or contains(text(), 'Income')]")
                for element in rental_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['rental_income'] = parent.text
                    break
            except:
                pass
            
            try:
                images = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='lofty'], img[src*='property']")
                image_urls = []
                for img in images[:5]:  # Limit to first 5 images
                    src = img.get_attribute('src')
                    if src and 'http' in src:
                        image_urls.append(src)
                property_data['images'] = image_urls
            except:
                pass
            
            try:
                try:
                    docs_tab = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Documents') or contains(text(), 'documents')]")
                    docs_tab.click()
                    time.sleep(2)
                except:
                    pass
                
                pdf_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf'], a[href*='/asset.lofty.ai/'], a[href*='documents']")
                
                document_urls = []
                for link in pdf_links:
                    href = link.get_attribute('href')
                    if href:
                        document_urls.append(href)
                        
                        try:
                            filename = f"{property_data['property_id']}_{len(document_urls)}.pdf"
                            self.download_file(href, filename)
                        except:
                            pass
                
                property_data['documents'] = document_urls
            except:
                pass
            
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                token_match = re.search(r'\$(\d+(?:\.\d{2})?)\s*(?:per token|/token)', page_text, re.IGNORECASE)
                if token_match:
                    property_data['token_price'] = f"${token_match.group(1)}"
                
                tokens_match = re.search(r'(\d+(?:,\d{3})*)\s*tokens?', page_text, re.IGNORECASE)
                if tokens_match:
                    property_data['total_tokens'] = tokens_match.group(1)
                
                yield_match = re.search(r'(\d+(?:\.\d+)?%)\s*(?:yield|return|APY)', page_text, re.IGNORECASE)
                if yield_match:
                    property_data['rental_yield'] = yield_match.group(1)
            except:
                pass
            
        except Exception as e:
            print(f"Error scraping property details: {str(e)}")
        
        return property_data


if __name__ == "__main__":
    scraper = LoftyScraper()
    scraper.run(full_scrape=True)

"""
Scraper for RealT tokenized real estate platform
NOTE: RealT blocks US IP addresses, so a proxy may be needed
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from typing import List, Dict
from selenium.webdriver.common.by import By
from base_scraper import BaseScraper


class RealTScraper(BaseScraper):
    """Scraper for RealT platform"""
    
    def __init__(self, use_proxy: bool = False):
        super().__init__(
            platform_name="realt",
            base_url="https://realt.co",
            use_proxy=use_proxy
        )
        self.marketplace_url = f"{self.base_url}/marketplace"
    
    def scrape_marketplace(self) -> List[str]:
        """Scrape all property URLs from the marketplace"""
        self.driver.get(self.marketplace_url)
        time.sleep(3)
        
        property_urls = []
        
        try:
            if "not available" in self.driver.page_source.lower() or "blocked" in self.driver.page_source.lower():
                print("WARNING: RealT appears to be blocking access. You may need to use a proxy.")
                print("Set PROXY_URL environment variable and rerun with use_proxy=True")
                return []
            
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/property'], a[href*='/token']")
            
            for element in property_elements:
                url = element.get_attribute('href')
                if url and url not in property_urls and self.base_url in url:
                    property_urls.append(url)
            
        except Exception as e:
            print(f"Error scraping marketplace: {str(e)}")
        
        return property_urls
    
    def scrape_property_details(self, property_url: str) -> Dict:
        """Scrape detailed information for a single property"""
        self.driver.get(property_url)
        time.sleep(3)
        
        property_data = {
            'platform': 'RealT',
            'url': property_url,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'property_id': property_url.split('/')[-1]
        }
        
        try:
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                property_data['title'] = title
                property_data['address'] = title
            except:
                pass
            
            try:
                token_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Token Price') or contains(text(), 'token price')]")
                for element in token_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['token_price'] = parent.text
                    break
            except:
                pass
            
            try:
                yield_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Yield') or contains(text(), 'yield') or contains(text(), 'APY')]")
                for element in yield_elements:
                    text = element.text
                    if '%' in text:
                        property_data['yield'] = text
                        break
            except:
                pass
            
            try:
                rental_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Rental') or contains(text(), 'rental')]")
                for element in rental_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['rental_income'] = parent.text
                    break
            except:
                pass
            
            try:
                detail_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Bed') or contains(text(), 'Bath') or contains(text(), 'sqft')]")
                details = []
                for element in detail_elements:
                    details.append(element.text)
                property_data['property_details'] = ' | '.join(details[:5])
            except:
                pass
            
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                property_data['full_description'] = body_text[:1000]
            except:
                pass
            
            try:
                images = self.driver.find_elements(By.CSS_SELECTOR, "img")
                image_urls = [img.get_attribute('src') for img in images[:5] if img.get_attribute('src') and 'http' in img.get_attribute('src')]
                property_data['images'] = image_urls
            except:
                pass
            
            try:
                pdf_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href$='.pdf']")
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
            
        except Exception as e:
            print(f"Error scraping property details: {str(e)}")
        
        return property_data


if __name__ == "__main__":
    scraper = RealTScraper(use_proxy=False)
    scraper.run(full_scrape=True)

"""
Scraper for Binaryx tokenized real estate platform
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from typing import List, Dict
from selenium.webdriver.common.by import By
from base_scraper import BaseScraper


class BinaryxScraper(BaseScraper):
    """Scraper for Binaryx platform"""
    
    def __init__(self):
        super().__init__(
            platform_name="binaryx",
            base_url="https://www.binaryx.com"
        )
    
    def scrape_marketplace(self) -> List[str]:
        """Scrape all property URLs from the marketplace"""
        self.driver.get(self.base_url)
        time.sleep(3)
        
        property_urls = []
        
        try:
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/property'], a[href*='/listing'], a[href*='/project']")
            
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
            'platform': 'Binaryx',
            'url': property_url,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'property_id': property_url.split('/')[-1]
        }
        
        try:
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                property_data['title'] = title
            except:
                pass
            
            try:
                location_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Location') or contains(text(), 'location')]")
                for element in location_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['location'] = parent.text
                    break
            except:
                pass
            
            try:
                price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '$') or contains(text(), 'Price') or contains(text(), 'Investment')]")
                for element in price_elements:
                    text = element.text
                    if '$' in text:
                        property_data['price'] = text
                        break
            except:
                pass
            
            try:
                yield_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Yield') or contains(text(), 'Return') or contains(text(), '%')]")
                for element in yield_elements:
                    text = element.text
                    if '%' in text:
                        property_data['return'] = text
                        break
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
    scraper = BinaryxScraper()
    scraper.run(full_scrape=True)

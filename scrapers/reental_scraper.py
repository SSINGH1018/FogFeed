"""
Scraper for Reental.co tokenized real estate platform
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import re
from typing import List, Dict
from selenium.webdriver.common.by import By
from base_scraper import BaseScraper


class ReentalScraper(BaseScraper):
    """Scraper for Reental.co platform"""
    
    def __init__(self):
        super().__init__(
            platform_name="reental",
            base_url="https://www.reental.co"
        )
    
    def scrape_marketplace(self) -> List[str]:
        """Scrape all property URLs from the marketplace"""
        self.driver.get(self.base_url)
        time.sleep(3)
        
        property_urls = []
        
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(5):  # Scroll a few times to load more content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/property'], a[href*='/proyecto'], a[href*='/project']")
            
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
            'platform': 'Reental.co',
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
                location = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Ubicación') or contains(text(), 'Location')]")
                parent = location.find_element(By.XPATH, "./..")
                property_data['location'] = parent.text
            except:
                pass
            
            try:
                investment_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Inversión') or contains(text(), 'Investment')]")
                for element in investment_elements:
                    text = element.text
                    if '$' in text or '€' in text:
                        property_data['investment_amount'] = text
                        break
            except:
                pass
            
            try:
                return_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Retorno') or contains(text(), 'Return') or contains(text(), 'Rentabilidad')]")
                for element in return_elements:
                    text = element.text
                    if '%' in text:
                        property_data['annual_return'] = text
                        break
            except:
                pass
            
            try:
                date_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Inicio de rentas') or contains(text(), 'Start date')]")
                for element in date_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['rental_start_date'] = parent.text
                    break
            except:
                pass
            
            try:
                all_text = self.driver.find_element(By.TAG_NAME, "body").text
                property_data['full_description'] = all_text[:1000]  # First 1000 chars
            except:
                pass
            
            try:
                images = self.driver.find_elements(By.CSS_SELECTOR, "img")
                image_urls = []
                for img in images[:5]:
                    src = img.get_attribute('src')
                    if src and 'http' in src and 'reental' in src:
                        image_urls.append(src)
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
    scraper = ReentalScraper()
    scraper.run(full_scrape=True)

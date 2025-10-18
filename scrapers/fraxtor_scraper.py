"""
Scraper for Fraxtor tokenized real estate platform
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from typing import List, Dict
from selenium.webdriver.common.by import By
from base_scraper import BaseScraper


class FraxtorScraper(BaseScraper):
    """Scraper for Fraxtor platform"""
    
    def __init__(self):
        super().__init__(
            platform_name="fraxtor",
            base_url="https://www.fraxtor.com"
        )
    
    def scrape_marketplace(self) -> List[str]:
        """Scrape all property URLs from the marketplace"""
        self.driver.get(self.base_url)
        time.sleep(3)
        
        property_urls = []
        
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/project'], a[href*='/property'], a[href*='/deal']")
            
            for element in property_elements:
                url = element.get_attribute('href')
                if url and url not in property_urls and self.base_url in url:
                    property_urls.append(url)
            
            if not property_urls:
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    url = link.get_attribute('href')
                    if url and self.base_url in url and url != self.base_url and url not in property_urls:
                        if not any(x in url for x in ['about', 'contact', 'terms', 'privacy', 'login', 'signup']):
                            property_urls.append(url)
            
        except Exception as e:
            print(f"Error scraping marketplace: {str(e)}")
        
        return property_urls
    
    def scrape_property_details(self, property_url: str) -> Dict:
        """Scrape detailed information for a single property"""
        self.driver.get(property_url)
        time.sleep(3)
        
        property_data = {
            'platform': 'Fraxtor',
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
                irr_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'IRR') or contains(text(), 'irr')]")
                for element in irr_elements:
                    text = element.text
                    if '%' in text:
                        property_data['irr'] = text
                        break
            except:
                pass
            
            try:
                term_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Holding') or contains(text(), 'Term') or contains(text(), 'Duration')]")
                for element in term_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['holding_term'] = parent.text
                    break
            except:
                pass
            
            try:
                investment_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Investment') or contains(text(), 'Minimum')]")
                for element in investment_elements:
                    text = element.text
                    if '$' in text or 'S$' in text:
                        property_data['investment_info'] = text
                        break
            except:
                pass
            
            try:
                type_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Property Type') or contains(text(), 'Type')]")
                for element in type_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['property_type'] = parent.text
                    break
            except:
                pass
            
            try:
                manager_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Manager') or contains(text(), 'Developer')]")
                for element in manager_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['manager'] = parent.text
                    break
            except:
                pass
            
            try:
                cis_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'CIS') or contains(text(), 'Structure')]")
                for element in cis_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['cis_structure'] = parent.text
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
                image_urls = []
                for img in images[:5]:
                    src = img.get_attribute('src')
                    if src and 'http' in src:
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
    scraper = FraxtorScraper()
    scraper.run(full_scrape=True)

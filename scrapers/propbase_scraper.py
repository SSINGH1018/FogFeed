"""
Scraper for Propbase.app tokenized real estate platform
NOTE: Requires login credentials
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from typing import List, Dict
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
from base_scraper import BaseScraper

load_dotenv()


class PropbaseScraper(BaseScraper):
    """Scraper for Propbase.app platform"""
    
    def __init__(self, email: str = None, password: str = None):
        super().__init__(
            platform_name="propbase",
            base_url="https://www.propbase.app"
        )
        self.email = email or os.getenv('PROPBASE_EMAIL')
        self.password = password or os.getenv('PROPBASE_PASSWORD')
        self.logged_in = False
    
    def login(self):
        """Login to Propbase"""
        if not self.email or not self.password:
            print("ERROR: Propbase credentials not provided!")
            print("Set PROPBASE_EMAIL and PROPBASE_PASSWORD environment variables or pass credentials to constructor")
            return False
        
        try:
            self.driver.get(f"{self.base_url}/login")
            time.sleep(3)
            
            email_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email' i]")
            email_input.send_keys(self.email)
            
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            password_input.send_keys(self.password)
            
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Login'), button:contains('Sign In')")
            login_button.click()
            
            time.sleep(5)
            
            if "login" not in self.driver.current_url.lower():
                print("Login successful!")
                self.logged_in = True
                return True
            else:
                print("Login may have failed. Please check credentials.")
                return False
                
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False
    
    def scrape_marketplace(self) -> List[str]:
        """Scrape all property URLs from the marketplace"""
        if not self.logged_in:
            if not self.login():
                print("Cannot scrape marketplace without login")
                return []
        
        self.driver.get(f"{self.base_url}/marketplace")
        time.sleep(3)
        
        property_urls = []
        
        try:
            for _ in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            property_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/property'], a[href*='/listing']")
            
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
            'platform': 'Propbase.app',
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
                location_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Location') or contains(text(), 'location') or contains(text(), 'Address')]")
                for element in location_elements:
                    parent = element.find_element(By.XPATH, "./..")
                    property_data['location'] = parent.text
                    break
            except:
                pass
            
            try:
                price_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '$') or contains(text(), 'Price') or contains(text(), 'Value')]")
                for element in price_elements:
                    text = element.text
                    if '$' in text:
                        property_data['price'] = text
                        break
            except:
                pass
            
            try:
                metric_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '%') or contains(text(), 'ROI') or contains(text(), 'Return') or contains(text(), 'Yield')]")
                for element in metric_elements:
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
    scraper = PropbaseScraper()
    scraper.run(full_scrape=True)

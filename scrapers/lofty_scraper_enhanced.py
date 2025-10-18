"""
Enhanced scraper for Lofty.ai - captures ALL property details
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import re
from typing import List, Dict
from selenium.webdriver.common.by import By
from base_scraper import BaseScraper


class LoftyScraperEnhanced(BaseScraper):
    """Enhanced scraper for Lofty.ai platform - captures comprehensive property data"""
    
    def __init__(self):
        super().__init__(
            platform_name="lofty",
            base_url="https://www.lofty.ai"
        )
        self.marketplace_url = f"{self.base_url}/marketplace"
    
    def scrape_marketplace(self) -> List[str]:
        """Scrape all property URLs from the marketplace"""
        self.driver.get(self.marketplace_url)
        time.sleep(3)
        
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
        """Scrape comprehensive property information"""
        self.driver.get(property_url)
        time.sleep(4)
        
        property_data = {
            'platform': 'Lofty.ai',
            'url': property_url,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'property_id': property_url.split('/')[-1]
        }
        
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            try:
                title = self.driver.find_element(By.CSS_SELECTOR, "h1").text
                property_data['title'] = title
                property_data['address'] = title
            except:
                pass
            
            try:
                city_state = self.driver.find_element(By.CSS_SELECTOR, "h4").text
                property_data['city_state'] = city_state
            except:
                pass
            
            try:
                price_match = re.search(r'Estimated Price[^\$]*\$([0-9,]+\.?\d*)', page_text, re.IGNORECASE)
                if price_match:
                    property_data['estimated_price'] = f"${price_match.group(1)}"
            except:
                pass
            
            try:
                return_match = re.search(r'Projected Annual Return[^\d]*([\d.]+)%', page_text, re.IGNORECASE)
                if return_match:
                    property_data['projected_annual_return'] = f"{return_match.group(1)}%"
            except:
                pass
            
            try:
                yield_match = re.search(r'Rental Yield[^\d]*([\d.]+)%', page_text, re.IGNORECASE)
                if yield_match:
                    property_data['rental_yield'] = f"{yield_match.group(1)}%"
            except:
                pass
            
            try:
                beds_match = re.search(r'(\d+)\s*Bed', page_text)
                if beds_match:
                    property_data['bedrooms'] = beds_match.group(1)
            except:
                pass
            
            try:
                baths_match = re.search(r'(\d+)\s*Bath', page_text)
                if baths_match:
                    property_data['bathrooms'] = baths_match.group(1)
            except:
                pass
            
            try:
                sqft_match = re.search(r'(\d+)\s*sqft', page_text)
                if sqft_match:
                    property_data['square_feet'] = sqft_match.group(1)
            except:
                pass
            
            try:
                type_match = re.search(r'(Single family|Multi-family|Condo|Townhouse)', page_text, re.IGNORECASE)
                if type_match:
                    property_data['property_type'] = type_match.group(1)
            except:
                pass
            
            try:
                built_match = re.search(r'Built in (\d{4})', page_text)
                if built_match:
                    property_data['year_built'] = built_match.group(1)
            except:
                pass
            
            try:
                rent_match = re.search(r'\$([0-9,]+)/month', page_text)
                if rent_match:
                    property_data['monthly_rent'] = f"${rent_match.group(1)}"
            except:
                pass
            
            try:
                lease_match = re.search(r'(\d+)\s*(?:year|month)\s*lease', page_text, re.IGNORECASE)
                if lease_match:
                    property_data['lease_term'] = lease_match.group(0)
            except:
                pass
            
            try:
                deposit_match = re.search(r'\$([0-9,]+)\s*Security Deposit', page_text)
                if deposit_match:
                    property_data['security_deposit'] = f"${deposit_match.group(1)}"
            except:
                pass
            
            try:
                loan_match = re.search(r'loan of \$([0-9,]+\.?\d*)', page_text, re.IGNORECASE)
                if loan_match:
                    property_data['loan_amount'] = f"${loan_match.group(1)}"
            except:
                pass
            
            try:
                rate_match = re.search(r'(\d+\.\d+)%\s*mortgage', page_text, re.IGNORECASE)
                if rate_match:
                    property_data['mortgage_rate'] = f"{rate_match.group(1)}%"
            except:
                pass
            
            try:
                rating_match = re.search(r'"([A-F])".*Rating.*Zip Code', page_text)
                if rating_match:
                    property_data['niche_rating'] = rating_match.group(1)
            except:
                pass
            
            try:
                images = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='images.lofty.ai']")
                image_urls = []
                for img in images[:10]:
                    src = img.get_attribute('src')
                    if src and src not in image_urls:
                        image_urls.append(src)
                property_data['images'] = image_urls
            except:
                pass
            
            documents = {}
            document_urls = []
            
            try:
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                
                for link in all_links:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and ('dropbox.com' in href or 'asset.lofty.ai' in href):
                        doc_type = 'unknown'
                        
                        if 'appraisal' in text.lower() or 'appraisal' in href.lower():
                            doc_type = 'appraisal'
                        elif 'inspection' in text.lower():
                            doc_type = 'inspection'
                        elif 'lease' in text.lower():
                            doc_type = 'lease'
                        elif 'insurance' in text.lower():
                            doc_type = 'insurance'
                        elif 'loan' in text.lower() or 'mortgage' in text.lower():
                            doc_type = 'loan_documents'
                        elif 'management' in text.lower():
                            doc_type = 'property_management'
                        elif 'operating agreement' in text.lower():
                            doc_type = 'operating_agreement'
                        elif 'llc' in text.lower():
                            doc_type = 'llc_documents'
                        elif 'title' in text.lower() or 'deed' in text.lower():
                            doc_type = 'title_documents'
                        elif 'transaction' in text.lower():
                            doc_type = 'transaction_data'
                        elif 'asset.lofty.ai' in href:
                            doc_type = 'offering_document'
                        
                        if href not in document_urls:
                            document_urls.append(href)
                            
                            if doc_type not in documents:
                                documents[doc_type] = []
                            documents[doc_type].append({
                                'url': href,
                                'label': text if text else doc_type
                            })
                            
                            filename = f"{property_data['property_id']}_{doc_type}_{len(documents[doc_type])}"
                            if href.endswith('.pdf') or 'asset.lofty.ai' in href:
                                filename += '.pdf'
                            
                            try:
                                self.download_file(href, filename)
                            except:
                                pass
                
                property_data['documents'] = documents
                property_data['document_count'] = len(document_urls)
                
            except Exception as e:
                print(f"Error extracting documents: {str(e)}")
            
            property_data['full_description'] = page_text[:2000]
            
        except Exception as e:
            print(f"Error scraping property details: {str(e)}")
        
        return property_data


if __name__ == "__main__":
    scraper = LoftyScraperEnhanced()
    scraper.run(full_scrape=True)

"""
Simple API to serve scraped property data
Can be used with FastAPI, Flask, or as standalone functions
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class PropertyDataAPI:
    """API for accessing scraped property data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
    
    def get_all_properties(self, platform: Optional[str] = None) -> List[Dict]:
        """Get all properties, optionally filtered by platform"""
        all_properties = []
        
        platforms = [platform] if platform else self._get_platforms()
        
        for plat in platforms:
            properties = self._load_latest_properties(plat)
            all_properties.extend(properties)
        
        return all_properties
    
    def get_property_by_id(self, property_id: str) -> Optional[Dict]:
        """Get a specific property by ID"""
        all_properties = self.get_all_properties()
        
        for prop in all_properties:
            if prop.get('property_id') == property_id:
                return prop
        
        return None
    
    def get_platforms(self) -> List[str]:
        """Get list of all available platforms"""
        return self._get_platforms()
    
    def get_platform_stats(self) -> Dict:
        """Get statistics for each platform"""
        stats = {}
        
        for platform in self._get_platforms():
            properties = self._load_latest_properties(platform)
            stats[platform] = {
                'total_properties': len(properties),
                'last_updated': self._get_last_update_time(platform)
            }
        
        return stats
    
    def search_properties(self, 
                         min_return: Optional[float] = None,
                         max_price: Optional[float] = None,
                         property_type: Optional[str] = None,
                         location: Optional[str] = None) -> List[Dict]:
        """Search properties with filters"""
        properties = self.get_all_properties()
        filtered = []
        
        for prop in properties:
            if min_return:
                return_str = prop.get('projected_annual_return', '0%')
                try:
                    return_val = float(return_str.replace('%', ''))
                    if return_val < min_return:
                        continue
                except:
                    pass
            
            if max_price:
                price_str = prop.get('estimated_price', '$0')
                try:
                    price_val = float(price_str.replace('$', '').replace(',', ''))
                    if price_val > max_price:
                        continue
                except:
                    pass
            
            if property_type:
                if property_type.lower() not in prop.get('property_type', '').lower():
                    continue
            
            if location:
                loc_fields = [
                    prop.get('city_state', ''),
                    prop.get('location', ''),
                    prop.get('address', '')
                ]
                if not any(location.lower() in field.lower() for field in loc_fields):
                    continue
            
            filtered.append(prop)
        
        return filtered
    
    def get_new_properties(self, since_date: Optional[str] = None) -> List[Dict]:
        """Get properties added since a specific date"""
        all_properties = self.get_all_properties()
        
        if not since_date:
            from datetime import timedelta
            since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        new_properties = []
        for prop in all_properties:
            scraped_at = prop.get('scraped_at', '')
            if scraped_at >= since_date:
                new_properties.append(prop)
        
        return new_properties
    
    def _get_platforms(self) -> List[str]:
        """Get list of platform directories"""
        if not self.data_dir.exists():
            return []
        
        return [d.name for d in self.data_dir.iterdir() if d.is_dir()]
    
    def _load_latest_properties(self, platform: str) -> List[Dict]:
        """Load the most recent properties file for a platform"""
        platform_dir = self.data_dir / platform
        
        if not platform_dir.exists():
            return []
        
        json_files = list(platform_dir.glob('properties_*.json'))
        
        if not json_files:
            return []
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _get_last_update_time(self, platform: str) -> str:
        """Get last update timestamp for a platform"""
        platform_dir = self.data_dir / platform
        
        if not platform_dir.exists():
            return "Never"
        
        json_files = list(platform_dir.glob('properties_*.json'))
        
        if not json_files:
            return "Never"
        
        latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        timestamp = datetime.fromtimestamp(latest_file.stat().st_mtime)
        
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')


"""
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()
api = PropertyDataAPI()

@app.get("/properties")
def get_properties(platform: Optional[str] = None):
    return api.get_all_properties(platform=platform)

@app.get("/properties/{property_id}")
def get_property(property_id: str):
    return api.get_property_by_id(property_id)

@app.get("/platforms")
def get_platforms():
    return api.get_platforms()

@app.get("/stats")
def get_stats():
    return api.get_platform_stats()

@app.get("/search")
def search_properties(
    min_return: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    location: Optional[str] = None
):
    return api.search_properties(
        min_return=min_return,
        max_price=max_price,
        property_type=property_type,
        location=location
    )
"""

if __name__ == "__main__":
    api = PropertyDataAPI()
    
    print("Available platforms:", api.get_platforms())
    print("\nPlatform stats:", json.dumps(api.get_platform_stats(), indent=2))
    
    all_props = api.get_all_properties()
    print(f"\nTotal properties: {len(all_props)}")
    
    high_return = api.search_properties(min_return=15.0)
    print(f"Properties with >15% return: {len(high_return)}")

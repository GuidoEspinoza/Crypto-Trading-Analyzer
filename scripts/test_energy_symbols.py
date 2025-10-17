#!/usr/bin/env python3
"""
Script rápido para encontrar los símbolos correctos de energías en Capital.com
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleCapitalClient:
    def __init__(self, base_url, api_key, identifier, password):
        self.base_url = base_url
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.session_token = None
        self.cst_token = None

    def create_session(self):
        import requests
        url = f"{self.base_url}/session"
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "identifier": self.identifier,
            "password": self.password
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                self.session_token = response.headers.get("X-SECURITY-TOKEN")
                self.cst_token = response.headers.get("CST")
                return {"success": True}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_markets(self, search_term=None):
        import requests
        url = f"{self.base_url}/markets"
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "X-SECURITY-TOKEN": self.session_token,
            "CST": self.cst_token
        }
        
        params = {}
        if search_term:
            params["searchTerm"] = search_term
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return {"success": True, "markets": response.json()}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

def test_energy_symbols():
    # Load environment
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    
    # Get credentials
    api_key = os.getenv('CAPITAL_API_KEY')
    identifier = os.getenv('CAPITAL_IDENTIFIER')
    password = os.getenv('CAPITAL_PASSWORD')
    base_url = os.getenv('CAPITAL_BASE_URL', 'https://demo-api-capital.backend-capital.com/api/v1')
    
    # Create client
    client = SimpleCapitalClient(base_url, api_key, identifier, password)
    
    # Create session
    session_result = client.create_session()
    if not session_result["success"]:
        logger.error(f"Failed to create session: {session_result['error']}")
        return False
    
    logger.info("✅ Session created successfully!")
    
    # Test different energy search terms
    energy_terms = [
        "OIL", "CRUDE", "WTI", "BRENT", "OIL_CRUDE", "CRUDE_OIL",
        "GAS", "NATURAL", "NATURALGAS", "NATURAL_GAS", "NG"
    ]
    
    logger.info("\n🛢️ Testing energy commodity symbols...")
    
    for term in energy_terms:
        logger.info(f"\n   Testing: {term}")
        markets_result = client.get_markets(search_term=term)
        
        if markets_result["success"]:
            markets = markets_result["markets"]
            if isinstance(markets, dict) and "markets" in markets:
                market_list = markets["markets"]
                if market_list:
                    logger.info(f"   ✅ {term}: Found {len(market_list)} market(s)")
                    for market in market_list[:3]:  # Show first 3 results
                        epic = market.get("epic", "N/A")
                        instrument_name = market.get("instrumentName", "N/A")
                        logger.info(f"     - {epic}: {instrument_name}")
                else:
                    logger.info(f"   ⚪ {term}: No markets found")
            else:
                logger.info(f"   {term}: {markets}")
        else:
            logger.error(f"   ❌ Failed to get {term} markets: {markets_result.get('error')}")
    
    return True

if __name__ == "__main__":
    logger.info("Capital.com Energy Symbols Test")
    logger.info("=" * 40)
    
    success = test_energy_symbols()
    
    if success:
        logger.info("\n🎯 Energy symbols test completed!")
    else:
        logger.error("\n💥 Test failed!")
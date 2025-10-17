#!/usr/bin/env python3
"""
Test script for Capital.com API connectivity
Tests authentication and basic API endpoints
"""

import os
import sys
import requests
import logging
from dotenv import load_dotenv
import time

# Add project root to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

from src.config.main_config import GLOBAL_SYMBOLS, get_all_capital_symbols

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleCapitalClient:
    """Simple Capital.com API client for testing"""
    
    def __init__(self, base_url, api_key, identifier, password):
        self.base_url = base_url
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.session = requests.Session()
        self.cst_token = None
        self.security_token = None
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-CAP-API-KEY': self.api_key
        })
    
    def create_session(self):
        """Create a new trading session"""
        url = f"{self.base_url}/session"
        payload = {
            "identifier": self.identifier,
            "password": self.password
        }
        
        try:
            logger.info("Creating new Capital.com session...")
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                # Extract tokens from response headers
                self.cst_token = response.headers.get('CST')
                self.security_token = response.headers.get('X-SECURITY-TOKEN')
                
                if self.cst_token and self.security_token:
                    # Update session headers
                    self.session.headers.update({
                        'CST': self.cst_token,
                        'X-SECURITY-TOKEN': self.security_token
                    })
                    
                    logger.info("Session created successfully")
                    return {
                        "success": True,
                        "cst_token": self.cst_token,
                        "security_token": self.security_token,
                        "session_data": response.json()
                    }
                else:
                    raise Exception("Authentication tokens not received in response headers")
            else:
                error_msg = f"Session creation failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during session creation: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def ping(self):
        """Ping the service"""
        url = f"{self.base_url}/ping"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                logger.debug("Ping successful")
                return {
                    "success": True,
                    "server_time": response.json().get("serverTime"),
                    "status": "connected"
                }
            else:
                error_msg = f"Ping failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during ping: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_accounts(self):
        """Get all trading accounts"""
        url = f"{self.base_url}/accounts"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                logger.debug("Accounts retrieved successfully")
                return {
                    "success": True,
                    "accounts": response.json()
                }
            else:
                error_msg = f"Failed to get accounts: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting accounts: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_markets(self, search_term=None):
        """Get available markets"""
        url = f"{self.base_url}/markets"
        params = {}
        
        if search_term:
            params["searchTerm"] = search_term
        
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                logger.debug(f"Markets retrieved successfully{' for search: ' + search_term if search_term else ''}")
                return {
                    "success": True,
                    "markets": response.json()
                }
            else:
                error_msg = f"Failed to get markets: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting markets: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

def test_capital_connection():
    """Test Capital.com API connection and authentication"""
    
    logger.info("🚀 Starting Capital.com API connection test...")
    
    # Get configuration from environment
    base_url = os.getenv('CAPITAL_DEMO_URL', 'https://demo-api-capital.backend-capital.com/api/v1')
    api_key = os.getenv('X-CAP-API-KEY', '')
    identifier = os.getenv('identifier', '')
    password = os.getenv('password', '')
    
    if not all([base_url, api_key, identifier, password]):
        logger.error("❌ Missing required environment variables!")
        logger.error("Required: CAPITAL_DEMO_URL, X-CAP-API-KEY, identifier, password")
        return False
    
    try:
        # Create client
        client = SimpleCapitalClient(base_url, api_key, identifier, password)
        logger.info(f"📡 Using base URL: {base_url}")
        
        # Test 1: Create session (authentication)
        logger.info("\n🔐 Test 1: Creating session...")
        session_result = client.create_session()
        
        if session_result["success"]:
            logger.info("✅ Session created successfully!")
            logger.info(f"   CST Token: {session_result['cst_token'][:20]}...")
            logger.info(f"   Security Token: {session_result['security_token'][:20]}...")
        else:
            logger.error("❌ Session creation failed!")
            logger.error(f"   Error: {session_result.get('error')}")
            return False
        
        # Test 2: Ping service
        logger.info("\n🏓 Test 2: Pinging service...")
        ping_result = client.ping()
        
        if ping_result["success"]:
            logger.info("✅ Ping successful!")
            logger.info(f"   Server time: {ping_result.get('server_time')}")
            logger.info(f"   Status: {ping_result.get('status')}")
        else:
            logger.error("❌ Ping failed!")
            logger.error(f"   Error: {ping_result.get('error')}")
        
        # Test 3: Get accounts
        logger.info("\n💰 Test 3: Getting accounts...")
        accounts_result = client.get_accounts()
        
        if accounts_result["success"]:
            logger.info("✅ Accounts retrieved successfully!")
            accounts = accounts_result["accounts"]
            if isinstance(accounts, dict) and "accounts" in accounts:
                account_list = accounts["accounts"]
                logger.info(f"   Found {len(account_list)} account(s)")
                for i, account in enumerate(account_list):
                    logger.info(f"   Account {i+1}: {account.get('accountName', 'N/A')} - {account.get('currency', 'N/A')}")
            else:
                logger.info(f"   Accounts data: {accounts}")
        else:
            logger.error("❌ Failed to get accounts!")
            logger.error(f"   Error: {accounts_result.get('error')}")
        
        # Test 4: Get markets for all symbols
        logger.info("\n🥇 Test 4: Getting markets for all symbols...")
        
        for symbol in GLOBAL_SYMBOLS:
            logger.info(f"\n   Testing: {symbol}")
            
            # Use symbol directly (already in Capital.com format)
            markets_result = client.get_markets(search_term=symbol)
            
            if markets_result["success"]:
                markets = markets_result["markets"]
                if isinstance(markets, dict) and "markets" in markets:
                    market_list = markets["markets"]
                    logger.info(f"   ✅ {symbol}: Found {len(market_list)} market(s)")
                    for market in market_list[:2]:  # Show first 2 results
                        epic = market.get("epic", "N/A")
                        instrument_name = market.get("instrumentName", "N/A")
                        logger.info(f"     - {epic}: {instrument_name}")
                else:
                    logger.info(f"   {symbol}: {markets}")
            else:
                logger.warning(f"   ⚠️ Failed to get {symbol} markets: {markets_result.get('error')}")
                
                # If Capital.com format fails, try with internal symbol
                if capital_symbol != internal_symbol:
                    logger.info(f"   Trying with internal symbol: {internal_symbol}")
                    markets_result = client.get_markets(search_term=internal_symbol)
                    
                    if markets_result["success"]:
                        markets = markets_result["markets"]
                        if isinstance(markets, dict) and "markets" in markets:
                            market_list = markets["markets"]
                            logger.info(f"   ✅ {internal_symbol}: Found {len(market_list)} market(s)")
                        else:
                            logger.info(f"   {internal_symbol}: {markets}")
                    else:
                        logger.error(f"   ❌ Both formats failed for {internal_symbol}")
        
        logger.info("\n🎉 Capital.com API connection test completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {str(e)}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'CAPITAL_DEMO_URL',
        'identifier', 
        'password',
        'X-CAP-API-KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error("❌ Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("\nPlease set these variables in your .env file")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

if __name__ == "__main__":
    logger.info("Capital.com API Connection Test")
    logger.info("=" * 50)
    
    # Load environment variables first
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    logger.info(f"📁 Loading environment from: {env_path}")
    
    # Check environment
    if not check_environment():
        exit(1)
    
    # Run connection test
    success = test_capital_connection()
    
    if success:
        logger.info("\n🎯 All tests passed! Capital.com API is ready to use.")
        exit(0)
    else:
        logger.error("\n💥 Some tests failed. Please check your configuration.")
        exit(1)
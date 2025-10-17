"""
Capital.com API Client
Handles authentication and API requests for Capital.com trading platform
"""

import os
import requests
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CapitalConfig:
    """Configuration for Capital.com API"""
    live_url: str
    demo_url: str
    identifier: str
    password: str
    api_key: str
    encrypted_password: str = ""
    use_demo: bool = True

class CapitalClient:
    """
    Capital.com API Client
    
    Handles authentication, session management, and API requests
    for Capital.com trading platform.
    """
    
    def __init__(self, config: CapitalConfig):
        self.config = config
        self.base_url = config.demo_url if config.use_demo else config.live_url
        self.session = requests.Session()
        
        # Authentication tokens
        self.cst_token: Optional[str] = None
        self.security_token: Optional[str] = None
        self.session_active: bool = False
        self.last_activity: float = 0
        
        # Session timeout (10 minutes as per API docs)
        self.session_timeout = 600  # 10 minutes in seconds
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-CAP-API-KEY': self.config.api_key
        })
    
    def _is_session_expired(self) -> bool:
        """Check if the current session has expired"""
        if not self.session_active:
            return True
        
        return (time.time() - self.last_activity) > self.session_timeout
    
    def _update_session_headers(self):
        """Update session headers with authentication tokens"""
        if self.cst_token and self.security_token:
            self.session.headers.update({
                'CST': self.cst_token,
                'X-SECURITY-TOKEN': self.security_token
            })
    
    def create_session(self) -> Dict[str, Any]:
        """
        Create a new trading session with Capital.com
        
        Returns:
            Dict containing session information
            
        Raises:
            Exception: If session creation fails
        """
        url = f"{self.base_url}/session"
        
        # Build payload - use regular password for now
        # The encryptedPassword in .env appears to be an RSA key, not an encrypted password
        payload = {
            "identifier": self.config.identifier,
            "password": self.config.password
        }
        
        try:
            logger.info("Creating new Capital.com session...")
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                # Extract tokens from response headers
                self.cst_token = response.headers.get('CST')
                self.security_token = response.headers.get('X-SECURITY-TOKEN')
                
                if self.cst_token and self.security_token:
                    self.session_active = True
                    self.last_activity = time.time()
                    self._update_session_headers()
                    
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
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during session creation: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def ping(self) -> Dict[str, Any]:
        """
        Ping the service to keep session alive
        
        Returns:
            Dict containing ping response
        """
        if self._is_session_expired():
            logger.info("Session expired, creating new session...")
            self.create_session()
        
        url = f"{self.base_url}/ping"
        
        try:
            response = self.session.get(url)
            self.last_activity = time.time()
            
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
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during ping: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_accounts(self) -> Dict[str, Any]:
        """
        Get all trading accounts
        
        Returns:
            Dict containing accounts information
        """
        if self._is_session_expired():
            self.create_session()
        
        url = f"{self.base_url}/accounts"
        
        try:
            response = self.session.get(url)
            self.last_activity = time.time()
            
            if response.status_code == 200:
                logger.debug("Accounts retrieved successfully")
                return {
                    "success": True,
                    "accounts": response.json()
                }
            else:
                error_msg = f"Failed to get accounts: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting accounts: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_markets(self, search_term: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available markets/instruments
        
        Args:
            search_term: Optional search term to filter markets
            
        Returns:
            Dict containing markets information
        """
        if self._is_session_expired():
            self.create_session()
        
        url = f"{self.base_url}/markets"
        params = {}
        
        if search_term:
            params["searchTerm"] = search_term
        
        try:
            response = self.session.get(url, params=params)
            self.last_activity = time.time()
            
            if response.status_code == 200:
                logger.debug(f"Markets retrieved successfully{' for search: ' + search_term if search_term else ''}")
                return {
                    "success": True,
                    "markets": response.json()
                }
            else:
                error_msg = f"Failed to get markets: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting markets: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def close_session(self) -> Dict[str, Any]:
        """
        Close the current trading session
        
        Returns:
            Dict containing session closure status
        """
        if not self.session_active:
            return {"success": True, "message": "No active session to close"}
        
        url = f"{self.base_url}/session"
        
        try:
            response = self.session.delete(url)
            
            if response.status_code == 200:
                self.session_active = False
                self.cst_token = None
                self.security_token = None
                self.last_activity = 0
                
                # Remove auth headers
                self.session.headers.pop('CST', None)
                self.session.headers.pop('X-SECURITY-TOKEN', None)
                
                logger.info("Session closed successfully")
                return {"success": True, "message": "Session closed"}
            else:
                error_msg = f"Failed to close session: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error closing session: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

def create_capital_client_from_env() -> CapitalClient:
    """
    Create a CapitalClient instance from environment variables
    
    Returns:
        Configured CapitalClient instance
    """

    
    config = CapitalConfig(
        live_url=os.getenv('CAPITAL_LIVE_URL', 'https://api-capital.backend-capital.com/api/v1'),
        demo_url=os.getenv('CAPITAL_DEMO_URL', 'https://demo-api-capital.backend-capital.com/api/v1'),
        identifier=os.getenv('identifier', ''),
        password=os.getenv('password', ''),
        api_key=os.getenv('X-CAP-API-KEY', ''),
        encrypted_password=os.getenv('encryptedPassword', ''),
        use_demo=os.getenv('IS_DEMO', 'true').lower() == 'true'
    )
    
    return CapitalClient(config)
"""
Capital.com API Client
Handles authentication and API requests for Capital.com trading platform
"""

import os
import requests
import time
import json
import threading
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

# Import symbol functions from main_config
from ..config.main_config import (
    get_all_capital_symbols,
    GLOBAL_SYMBOLS
)

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
        self.session_created_at: Optional[datetime] = None
        
        # Session timeout (10 minutes as per API docs, but we'll renew at 8 minutes)
        self.session_timeout = 600  # 10 minutes in seconds
        self.renewal_threshold = 480  # 8 minutes - renew before expiration
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1  # Initial delay in seconds
        self.max_retry_delay = 30  # Maximum delay in seconds
        
        # Session health monitoring
        self.failed_requests = 0
        self.max_failed_requests = 5
        self.last_health_check: Optional[datetime] = None
        self.health_check_interval = 300  # 5 minutes
        
        # Thread safety
        self._session_lock = threading.Lock()
        
        # Session persistence
        self.session_file = f".capital_session_{'demo' if config.use_demo else 'live'}.json"
        
        # Session monitoring
        self.session_renewals = 0
        self.session_failures = 0
        self.last_session_failure = None
        self.monitoring_enabled = True
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-CAP-API-KEY': self.config.api_key
        })
        
        # Try to load existing session
        self._load_session_from_file()
    
    def _is_session_expired(self) -> bool:
        """Check if the current session has expired"""
        if not self.session_active or not self.session_created_at:
            return True
        
        # Check if session has exceeded timeout
        session_age = (datetime.now() - self.session_created_at).total_seconds()
        return session_age > self.session_timeout
    
    def _should_renew_session(self) -> bool:
        """Check if session should be renewed proactively"""
        if not self.session_active or not self.session_created_at:
            return True
        
        # Check if we're approaching expiration
        session_age = (datetime.now() - self.session_created_at).total_seconds()
        return session_age > self.renewal_threshold
    
    def _is_session_healthy(self) -> bool:
        """Check if session is healthy based on recent failures"""
        return self.failed_requests < self.max_failed_requests
    
    def _update_session_headers(self):
        """Update session headers with authentication tokens"""
        if self.cst_token and self.security_token:
            self.session.headers.update({
                'CST': self.cst_token,
                'X-SECURITY-TOKEN': self.security_token
            })
    
    def create_session(self) -> Dict[str, Any]:
        """
        Create a new trading session with Capital.com with retry logic
        
        Returns:
            Dict containing session information
            
        Raises:
            Exception: If session creation fails after all retries
        """
        with self._session_lock:
            return self._create_session_with_retry()
    
    def _create_session_with_retry(self) -> Dict[str, Any]:
        """Internal method to create session with retry logic"""
        url = f"{self.base_url}/session"
        
        # Build payload
        payload = {
            "identifier": self.config.identifier,
            "password": self.config.password
        }
        
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = min(self.retry_delay * (2 ** (attempt - 1)), self.max_retry_delay)
                    logger.info(f"Retrying session creation in {delay} seconds... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(delay)
                
                logger.info(f"Creating new Capital.com session... (attempt {attempt + 1}/{self.max_retries})")
                response = self.session.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    # Extract tokens from response headers
                    self.cst_token = response.headers.get('CST')
                    self.security_token = response.headers.get('X-SECURITY-TOKEN')
                    
                    if self.cst_token and self.security_token:
                        self.session_active = True
                        self.last_activity = time.time()
                        self.session_created_at = datetime.now()
                        self.failed_requests = 0  # Reset failure counter
                        self._update_session_headers()
                        
                        # Save session to file for persistence
                        self._save_session_to_file()
                        
                        logger.info("Session created successfully")
                        return {
                            "success": True,
                            "cst_token": self.cst_token,
                            "security_token": self.security_token,
                            "session_data": response.json(),
                            "created_at": self.session_created_at.isoformat()
                        }
                    else:
                        raise Exception("Authentication tokens not received in response headers")
                else:
                    error_msg = f"Session creation failed: {response.status_code} - {response.text}"
                    logger.warning(error_msg)
                    last_exception = Exception(error_msg)
                    
                    # Don't retry on authentication errors (400)
                    if response.status_code == 400:
                        break
                        
            except requests.exceptions.RequestException as e:
                error_msg = f"Network error during session creation: {str(e)}"
                logger.warning(error_msg)
                last_exception = Exception(error_msg)
        
        # All retries failed
        self.failed_requests += 1
        final_error = f"Session creation failed after {self.max_retries} attempts"
        if last_exception:
            final_error += f": {str(last_exception)}"
        
        logger.error(final_error)
        self._track_session_failure(final_error)
        raise Exception(final_error)
    
    def _ensure_valid_session(self) -> bool:
        """
        Ensure we have a valid, healthy session
        
        Returns:
            bool: True if session is valid, False otherwise
        """
        try:
            # Check if session needs renewal
            if self._should_renew_session():
                self._track_session_renewal("Session approaching expiry")
                self.create_session()
                return True
            elif not self._is_session_healthy():
                self._track_session_renewal("Session health check failed")
                self.create_session()
                return True
            
            # Perform health check if needed
            if self._should_perform_health_check():
                return self._perform_health_check()
            
            return self.session_active
            
        except Exception as e:
            self._track_session_failure(f"Failed to ensure valid session: {str(e)}")
            return False
    
    def _should_perform_health_check(self) -> bool:
        """Check if we should perform a health check"""
        if not self.last_health_check:
            return True
        
        time_since_check = (datetime.now() - self.last_health_check).total_seconds()
        return time_since_check > self.health_check_interval
    
    def _perform_health_check(self) -> bool:
        """
        Perform a health check using ping
        
        Returns:
            bool: True if session is healthy, False otherwise
        """
        try:
            self.last_health_check = datetime.now()
            ping_result = self._ping_internal()
            
            if ping_result.get("success", False):
                logger.debug("Session health check passed")
                self.failed_requests = max(0, self.failed_requests - 1)  # Reduce failure count on success
                return True
            else:
                logger.warning("Session health check failed")
                self.failed_requests += 1
                return False
                
        except Exception as e:
            logger.warning(f"Session health check error: {str(e)}")
            self.failed_requests += 1
            return False

    def ping(self) -> Dict[str, Any]:
        """
        Ping the service to keep session alive with automatic session management
        
        Returns:
            Dict containing ping response
        """
        # Ensure we have a valid session before pinging
        if not self._ensure_valid_session():
            return {
                "success": False,
                "error": "Failed to establish valid session",
                "status": "session_error"
            }
        
        return self._ping_internal()
    
    def _ping_internal(self) -> Dict[str, Any]:
        """
        Internal ping method without session validation
        
        Returns:
            Dict containing ping response
        """
        url = f"{self.base_url}/ping"
        
        try:
            response = self.session.get(url, timeout=10)
            self.last_activity = time.time()
            
            if response.status_code == 200:
                logger.debug("Ping successful")
                return {
                    "success": True,
                    "server_time": response.json().get("serverTime"),
                    "status": "connected"
                }
            else:
                logger.warning(f"Ping failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "status": "disconnected"
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ping network error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": "network_error"
            }
    
    def get_accounts(self) -> Dict[str, Any]:
        """
        Get all trading accounts
        
        Returns:
            Dict containing accounts information
        """
        if not self._ensure_valid_session():
            return {
                "success": False,
                "error": "Failed to establish valid session"
            }
        
        url = f"{self.base_url}/accounts"
        
        try:
            response = self.session.get(url, timeout=10)
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
                self.failed_requests += 1
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting accounts: {str(e)}"
            logger.error(error_msg)
            self.failed_requests += 1
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_markets(self, search_term: Optional[str] = None, epics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get available markets/instruments
        
        Args:
            search_term: Optional search term to filter markets
            epics: Optional list of specific market epics to retrieve
            
        Returns:
            Dict containing markets information
        """
        if not self._ensure_valid_session():
            return {
                "success": False,
                "error": "Failed to establish valid session"
            }
        
        url = f"{self.base_url}/markets"
        params = {}
        
        if search_term:
            params["searchTerm"] = search_term
        elif epics:
            # Join epics with comma for API request
            params["epics"] = ",".join(epics)
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            self.last_activity = time.time()
            
            if response.status_code == 200:
                logger.debug(f"Markets retrieved successfully{' for search: ' + search_term if search_term else ''}{' for epics: ' + str(epics) if epics else ''}")
                return {
                    "success": True,
                    "markets": response.json()
                }
            else:
                error_msg = f"Failed to get markets: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self.failed_requests += 1
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting markets: {str(e)}"
            logger.error(error_msg)
            self.failed_requests += 1
            return {
                    "success": False,
                    "error": error_msg
                }

    def get_market_data(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get market data (bid/offer prices) for specific symbols
        
        Args:
            symbols: List of Capital.com symbols (epics)
            
        Returns:
            Dict mapping symbol to price data: {symbol: {"bid": float, "offer": float, "mid": float}}
        """
        if not symbols:
            return {}
        
        # Capital.com API supports max 50 epics per request
        batch_size = 50
        all_market_data = {}
        
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            
            try:
                result = self.get_markets(epics=batch_symbols)
                
                if result["success"]:
                    markets_response = result["markets"]
                    
                    # Handle different response formats
                    if "marketDetails" in markets_response:
                        # Detailed response format (when using epics parameter)
                        for market_detail in markets_response["marketDetails"]:
                            epic = market_detail["instrument"]["epic"]
                            snapshot = market_detail["snapshot"]
                            
                            bid = snapshot.get("bid", 0.0)
                            offer = snapshot.get("offer", 0.0)
                            mid = (bid + offer) / 2 if bid and offer else 0.0
                            
                            all_market_data[epic] = {
                                "bid": bid,
                                "offer": offer,
                                "mid": mid,
                                "status": snapshot.get("marketStatus", "UNKNOWN")
                            }
                    
                    elif "markets" in markets_response:
                        # Simple response format (when using searchTerm)
                        for market in markets_response["markets"]:
                            epic = market["epic"]
                            
                            bid = market.get("bid", 0.0)
                            offer = market.get("offer", 0.0)
                            mid = (bid + offer) / 2 if bid and offer else 0.0
                            
                            all_market_data[epic] = {
                                "bid": bid,
                                "offer": offer,
                                "mid": mid,
                                "status": market.get("marketStatus", "UNKNOWN")
                            }
                
                else:
                    logger.warning(f"Failed to get market data for batch {batch_symbols}: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error getting market data for batch {batch_symbols}: {str(e)}")
        
        return all_market_data
    

    
    def get_all_supported_symbols(self) -> List[str]:
        """
        Get all symbols supported by this client (from GLOBAL_SYMBOLS)
        
        Returns:
            List of internal symbol names
        """
        return GLOBAL_SYMBOLS.copy()
    
    def get_capital_symbol(self, symbol: str) -> str:
        """
        Return symbol as-is (symbols are already in Capital.com format)
        
        Args:
            symbol: Symbol in Capital.com format
            
        Returns:
            Same symbol (no conversion needed)
        """
        return symbol
    
    def get_internal_symbol(self, symbol: str) -> str:
        """
        Return symbol as-is (symbols are already in Capital.com format)
        
        Args:
            symbol: Symbol in Capital.com format
            
        Returns:
            Same symbol (no conversion needed)
        """
        return symbol
    
    def _save_session_to_file(self):
        """Save current session data to file for persistence"""
        if not self.session_active or not self.cst_token or not self.security_token:
            return
        
        session_data = {
            "cst_token": self.cst_token,
            "security_token": self.security_token,
            "session_created_at": self.session_created_at.isoformat() if self.session_created_at else None,
            "last_activity": self.last_activity
        }
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            logger.debug("Session saved to file")
        except Exception as e:
            logger.warning(f"Failed to save session to file: {str(e)}")
    
    def _load_session_from_file(self):
        """Load session data from file if available and valid"""
        try:
            if not os.path.exists(self.session_file):
                return
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session data is complete
            if not all(key in session_data for key in ["cst_token", "security_token", "session_created_at"]):
                logger.debug("Incomplete session data in file")
                return
            
            # Parse session creation time
            session_created_at = datetime.fromisoformat(session_data["session_created_at"])
            
            # Check if session is still valid (not expired)
            session_age = (datetime.now() - session_created_at).total_seconds()
            if session_age > self.session_timeout:
                logger.debug("Saved session has expired")
                self._delete_session_file()
                return
            
            # Restore session data
            self.cst_token = session_data["cst_token"]
            self.security_token = session_data["security_token"]
            self.session_created_at = session_created_at
            self.last_activity = session_data.get("last_activity", time.time())
            self.session_active = True
            
            # Update session headers
            self._update_session_headers()
            
            logger.info(f"Session restored from file (age: {session_age:.0f}s)")
            
        except Exception as e:
            logger.warning(f"Failed to load session from file: {str(e)}")
            self._delete_session_file()
    
    def _delete_session_file(self):
        """Delete the session file"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                logger.debug("Session file deleted")
        except Exception as e:
            logger.warning(f"Failed to delete session file: {str(e)}")
    
    def get_session_status(self) -> Dict[str, Any]:
        """
        Get comprehensive session status information
        
        Returns:
            Dict containing session status and health metrics
        """
        session_age = 0
        if self.session_created_at:
            session_age = (datetime.now() - self.session_created_at).total_seconds()
        
        time_until_expiry = self.session_timeout - session_age if self.session_active else 0
        time_until_renewal = self.renewal_threshold - session_age if self.session_active else 0
        
        return {
            "session_active": self.session_active,
            "session_age_seconds": session_age,
            "time_until_expiry_seconds": max(0, time_until_expiry),
            "time_until_renewal_seconds": max(0, time_until_renewal),
            "failed_requests": self.failed_requests,
            "max_failed_requests": self.max_failed_requests,
            "session_renewals": self.session_renewals,
            "session_failures": self.session_failures,
            "last_session_failure": self.last_session_failure.isoformat() if self.last_session_failure else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "session_healthy": self._is_session_healthy(),
            "needs_renewal": self._should_renew_session(),
            "environment": "demo" if self.config.use_demo else "live"
        }
    
    def _log_session_alert(self, alert_type: str, message: str, level: str = "warning"):
        """
        Log session alerts with consistent formatting
        
        Args:
            alert_type: Type of alert (e.g., "SESSION_FAILURE", "SESSION_RENEWAL")
            message: Alert message
            level: Log level (debug, info, warning, error)
        """
        if not self.monitoring_enabled:
            return
        
        alert_msg = f"[CAPITAL.COM SESSION ALERT] {alert_type}: {message}"
        
        if level == "error":
            logger.error(alert_msg)
        elif level == "warning":
            logger.warning(alert_msg)
        elif level == "info":
            logger.info(alert_msg)
        else:
            logger.debug(alert_msg)
    
    def _track_session_failure(self, error_msg: str):
        """Track session failures for monitoring"""
        self.session_failures += 1
        self.last_session_failure = datetime.now()
        
        self._log_session_alert(
            "SESSION_FAILURE",
            f"Session failure #{self.session_failures}: {error_msg}",
            "error"
        )
        
        # Alert if too many failures
        if self.session_failures > 3:
            self._log_session_alert(
                "HIGH_FAILURE_RATE",
                f"High session failure rate detected: {self.session_failures} failures",
                "error"
            )
    
    def _track_session_renewal(self, reason: str):
        """Track session renewals for monitoring"""
        self.session_renewals += 1
        
        self._log_session_alert(
            "SESSION_RENEWAL",
            f"Session renewal #{self.session_renewals}: {reason}",
            "info"
        )
    
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
                self.session_created_at = None
                
                # Remove auth headers
                self.session.headers.pop('CST', None)
                self.session.headers.pop('X-SECURITY-TOKEN', None)
                
                # Delete session file
                self._delete_session_file()
                
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
    
    # Debug: Log configuration (without sensitive data)
    logger.info(f"Capital.com config - Demo mode: {config.use_demo}")
    logger.info(f"Capital.com config - Base URL: {config.demo_url if config.use_demo else config.live_url}")
    logger.info(f"Capital.com config - Identifier set: {'Yes' if config.identifier else 'No'}")
    logger.info(f"Capital.com config - Password set: {'Yes' if config.password else 'No'}")
    logger.info(f"Capital.com config - API Key set: {'Yes' if config.api_key else 'No'}")
    
    return CapitalClient(config)
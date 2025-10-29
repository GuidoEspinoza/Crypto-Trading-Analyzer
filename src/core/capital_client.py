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
try:
    from ..config.main_config import get_all_capital_symbols, GLOBAL_SYMBOLS
    from ..utils.market_hours import market_hours_checker
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.main_config import get_all_capital_symbols, GLOBAL_SYMBOLS
    from utils.market_hours import market_hours_checker

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
        self.session_file = (
            f".capital_session_{'demo' if config.use_demo else 'live'}.json"
        )

        # Session monitoring
        self.session_renewals = 0
        self.session_failures = 0
        self.last_session_failure = None
        self.monitoring_enabled = True

        # Trailing stop capabilities
        self.trailing_stops_enabled = False
        self.account_info = {}

        # Set default headers
        self.session.headers.update(
            {"Content-Type": "application/json", "X-CAP-API-KEY": self.config.api_key}
        )

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
            self.session.headers.update(
                {"CST": self.cst_token, "X-SECURITY-TOKEN": self.security_token}
            )

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

        # Build payload with plain text password
        payload = {
            "identifier": self.config.identifier,
            "password": self.config.password,
        }

        logger.info("🔐 Using plain text password for authentication")
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                if attempt > 0:
                    delay = min(
                        self.retry_delay * (2 ** (attempt - 1)), self.max_retry_delay
                    )
                    logger.info(
                        f"Retrying session creation in {delay} seconds... (attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)

                logger.info(
                    f"Creating new Capital.com session... (attempt {attempt + 1}/{self.max_retries})"
                )
                response = self.session.post(url, json=payload, timeout=30)

                if response.status_code == 200:
                    # Extract tokens from response headers
                    self.cst_token = response.headers.get("CST")
                    self.security_token = response.headers.get("X-SECURITY-TOKEN")

                    if self.cst_token and self.security_token:
                        self.session_active = True
                        self.last_activity = time.time()
                        self.session_created_at = datetime.now()
                        self.failed_requests = 0  # Reset failure counter
                        self._update_session_headers()

                        # Tokens are managed in memory only (like encryptedPassword)
                        logger.info("🔄 Authentication tokens generated in memory")

                        # Extract account info and trailing stop capabilities
                        session_data = response.json()
                        self.account_info = session_data
                        self.trailing_stops_enabled = session_data.get(
                            "trailingStopsEnabled", False
                        )

                        # Log trailing stop capability
                        if self.trailing_stops_enabled:
                            logger.info(
                                "✅ Trailing stops are ENABLED for this account"
                            )
                        else:
                            logger.warning(
                                "⚠️  Trailing stops are DISABLED for this account"
                            )

                        # Save session to file for persistence
                        self._save_session_to_file()

                        logger.info("Session created successfully")
                        return {
                            "success": True,
                            "cst_token": self.cst_token,
                            "security_token": self.security_token,
                            "session_data": session_data,
                            "created_at": self.session_created_at.isoformat(),
                            "trailing_stops_enabled": self.trailing_stops_enabled,
                        }
                    else:
                        raise Exception(
                            "Authentication tokens not received in response headers"
                        )
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
                self.failed_requests = max(
                    0, self.failed_requests - 1
                )  # Reduce failure count on success
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
                "status": "session_error",
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
                    "status": "connected",
                }
            else:
                logger.warning(f"Ping failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "status": "disconnected",
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ping network error: {str(e)}")
            return {"success": False, "error": str(e), "status": "network_error"}

    def get_accounts(self) -> Dict[str, Any]:
        """
        Get all trading accounts

        Returns:
            Dict containing accounts information
        """
        if not self._ensure_valid_session():
            return {"success": False, "error": "Failed to establish valid session"}

        url = f"{self.base_url}/accounts"

        try:
            response = self.session.get(url, timeout=10)
            self.last_activity = time.time()

            if response.status_code == 200:
                logger.debug("Accounts retrieved successfully")
                return {"success": True, "accounts": response.json()}
            else:
                error_msg = (
                    f"Failed to get accounts: {response.status_code} - {response.text}"
                )
                logger.error(error_msg)
                self.failed_requests += 1
                return {"success": False, "error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting accounts: {str(e)}"
            logger.error(error_msg)
            self.failed_requests += 1
            return {"success": False, "error": error_msg}

    def get_available_balance(self) -> Dict[str, Any]:
        """
        💰 Obtener balance disponible de la cuenta principal

        Returns:
            Dict con el balance disponible y información adicional
        """
        accounts_result = self.get_accounts()

        if not accounts_result.get("success"):
            return {
                "success": False,
                "error": f"Failed to get accounts: {accounts_result.get('error')}",
            }

        try:
            accounts_data = accounts_result.get("accounts", {})
            accounts_list = accounts_data.get("accounts", [])

            if not accounts_list:
                return {"success": False, "error": "No accounts found"}

            # Buscar la cuenta principal (preferred=True) o tomar la primera
            main_account = None
            for account in accounts_list:
                if account.get("preferred", False):
                    main_account = account
                    break

            if not main_account:
                main_account = accounts_list[0]

            balance_info = main_account.get("balance", {})

            return {
                "success": True,
                "account_id": main_account.get("accountId"),
                "account_name": main_account.get("accountName"),
                "currency": main_account.get("currency"),
                "symbol": main_account.get("symbol"),
                "available": balance_info.get("available", 0),
                "balance": balance_info.get("balance", 0),
                "deposit": balance_info.get("deposit", 0),
                "profit_loss": balance_info.get("profitLoss", 0),
                "full_balance_info": balance_info,
            }

        except Exception as e:
            error_msg = f"Error parsing account balance: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def get_account_preferences(self) -> Dict[str, Any]:
        """
        Get account preferences including leverage settings for different asset types

        Returns:
            Dict containing account preferences with leverage information
        """
        if not self._ensure_valid_session():
            return {"success": False, "error": "Failed to establish valid session"}

        try:
            response = self.session.get(
                f"{self.base_url}/accounts/preferences",
                headers={
                    "CST": self.cst_token,
                    "X-SECURITY-TOKEN": self.security_token,
                },
            )

            if response.status_code == 200:
                preferences_data = response.json()
                self.last_activity = time.time()

                return {
                    "success": True,
                    "preferences": preferences_data,
                    "leverages": preferences_data.get("leverages", {}),
                    "hedging_mode": preferences_data.get("hedgingMode", False),
                }
            else:
                error_msg = f"Failed to get account preferences: {response.status_code}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                }

        except Exception as e:
            error_msg = f"Error getting account preferences: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def get_leverage_for_asset_type(self, asset_type: str) -> Dict[str, Any]:
        """
        Get leverage information for a specific asset type

        Args:
            asset_type: Asset type (CRYPTOCURRENCIES, SHARES, CURRENCIES, INDICES, COMMODITIES)

        Returns:
            Dict containing current and available leverage for the asset type
        """
        preferences = self.get_account_preferences()

        if not preferences.get("success"):
            return {
                "success": False,
                "error": f"Failed to get preferences: {preferences.get('error')}",
            }

        leverages = preferences.get("leverages", {})
        asset_leverage = leverages.get(asset_type.upper())

        if not asset_leverage:
            return {
                "success": False,
                "error": f"Asset type '{asset_type}' not found in preferences",
            }

        return {
            "success": True,
            "asset_type": asset_type.upper(),
            "current_leverage": asset_leverage.get("current", 1),
            "available_leverages": asset_leverage.get("available", [1]),
            "max_leverage": max(asset_leverage.get("available", [1])),
        }

    def get_asset_type_from_symbol(self, symbol: str) -> str:
        """
        Determine asset type from symbol

        Args:
            symbol: Trading symbol (e.g., BTCUSD, ETHUSD, EURUSD, etc.)

        Returns:
            Asset type string (CRYPTOCURRENCIES, CURRENCIES, SHARES, INDICES, COMMODITIES)
        """
        symbol_upper = symbol.upper()

        # Cryptocurrency symbols
        crypto_symbols = [
            "BTC",
            "ETH",
            "XRP",
            "ADA",
            "SOL",
            "DOT",
            "AVAX",
            "MATIC",
            "LINK",
            "UNI",
            "LTC",
            "BCH",
            "XLM",
            "ALGO",
            "ATOM",
            "ICP",
            "VET",
            "FIL",
            "TRX",
            "ETC",
            "AAVE",
            "MKR",
            "COMP",
            "YFI",
            "SNX",
            "CRV",
            "BAL",
            "REN",
            "KNC",
            "ZRX",
        ]

        # Check if it's a cryptocurrency
        for crypto in crypto_symbols:
            if symbol_upper.startswith(crypto) and (
                "USD" in symbol_upper or "EUR" in symbol_upper or "GBP" in symbol_upper
            ):
                return "CRYPTOCURRENCIES"

        # Currency pairs (Forex)
        major_currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]
        if len(symbol_upper) == 6:  # Standard forex pair format like EURUSD
            base = symbol_upper[:3]
            quote = symbol_upper[3:]
            if base in major_currencies and quote in major_currencies:
                return "CURRENCIES"

        # Indices (usually contain numbers or specific patterns)
        index_patterns = ["SPX", "NAS", "DOW", "FTSE", "DAX", "CAC", "NIKKEI", "ASX"]
        for pattern in index_patterns:
            if pattern in symbol_upper:
                return "INDICES"

        # Commodities
        commodity_symbols = [
            "GOLD",
            "SILVER",
            "OIL",
            "BRENT",
            "GAS",
            "COPPER",
            "PLATINUM",
        ]
        for commodity in commodity_symbols:
            if commodity in symbol_upper:
                return "COMMODITIES"

        # Default to SHARES if no other type matches
        return "SHARES"

    def get_leverage_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Get leverage information for a specific trading symbol

        Args:
            symbol: Trading symbol

        Returns:
            Dict containing leverage information for the symbol
        """
        asset_type = self.get_asset_type_from_symbol(symbol)
        leverage_info = self.get_leverage_for_asset_type(asset_type)

        if leverage_info.get("success"):
            leverage_info["symbol"] = symbol
            leverage_info["detected_asset_type"] = asset_type

        return leverage_info

    def get_markets(
        self, search_term: Optional[str] = None, epics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get available markets/instruments

        Args:
            search_term: Optional search term to filter markets
            epics: Optional list of specific market epics to retrieve

        Returns:
            Dict containing markets information
        """
        if not self._ensure_valid_session():
            return {"success": False, "error": "Failed to establish valid session"}

        url = f"{self.base_url}/markets"
        params = {}

        if search_term:
            params["searchTerm"] = search_term
        elif epics:
            # Filter out empty or None epics before joining
            valid_epics = [epic for epic in epics if epic and epic.strip()]
            if valid_epics:
                # Join epics with comma for API request
                params["epics"] = ",".join(valid_epics)
            else:
                # If no valid epics, return empty result
                return {"success": False, "error": "No valid epics provided"}

        try:
            # Add small delay to avoid rate limiting
            time.sleep(0.5)
            response = self.session.get(url, params=params, timeout=10)
            self.last_activity = time.time()

            if response.status_code == 200:
                logger.debug(
                    f"Markets retrieved successfully{' for search: ' + search_term if search_term else ''}{' for epics: ' + str(epics) if epics else ''}"
                )
                return {"success": True, "markets": response.json()}
            elif response.status_code == 429:
                # Rate limit exceeded - wait longer before next request
                error_msg = (
                    f"Rate limit exceeded: {response.status_code} - {response.text}"
                )
                logger.warning(error_msg)
                logger.info("Waiting 5 seconds due to rate limiting...")
                time.sleep(5)
                self.failed_requests += 1
                return {"success": False, "error": error_msg}
            else:
                error_msg = (
                    f"Failed to get markets: {response.status_code} - {response.text}"
                )
                logger.error(error_msg)
                self.failed_requests += 1
                return {"success": False, "error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting markets: {str(e)}"
            logger.error(error_msg)
            self.failed_requests += 1
            return {"success": False, "error": error_msg}

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

        # Filtrar símbolos vacíos o None antes del procesamiento
        valid_symbols = [symbol for symbol in symbols if symbol and symbol.strip()]
        if not valid_symbols:
            logger.warning("No valid symbols provided to get_market_data")
            return {}

        # Capital.com API supports max 50 epics per request, but using smaller batches to avoid rate limiting
        batch_size = 25
        all_market_data = {}

        for i in range(0, len(valid_symbols), batch_size):
            batch_symbols = valid_symbols[i : i + batch_size]

            # Add delay between batches to avoid rate limiting (429 errors)
            if i > 0:  # No delay for first batch
                time.sleep(2.0)  # 2 second delay between batches

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
                                "status": snapshot.get("marketStatus", "UNKNOWN"),
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
                                "status": market.get("marketStatus", "UNKNOWN"),
                            }

                else:
                    logger.warning(
                        f"Failed to get market data for batch {batch_symbols}: {result.get('error')}"
                    )

            except Exception as e:
                logger.error(
                    f"Error getting market data for batch {batch_symbols}: {str(e)}"
                )

        return all_market_data

    def get_historical_prices(
        self,
        epic: str,
        resolution: str = "HOUR",
        max_points: int = 100,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical price data for a specific instrument

        Args:
            epic: Capital.com symbol (epic)
            resolution: Time resolution (MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, 
                       MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK)
            max_points: Maximum number of data points to return (max 1000)
            from_date: Start date in ISO format (e.g., "2023-01-01T00:00:00")
            to_date: End date in ISO format (e.g., "2023-01-31T23:59:59")

        Returns:
            Dict with success status and historical price data
        """
        if not self._ensure_valid_session():
            return {
                "success": False,
                "error": "No valid session available",
                "prices": []
            }

        # Validate parameters
        valid_resolutions = [
            "MINUTE", "MINUTE_2", "MINUTE_3", "MINUTE_5", "MINUTE_10",
            "MINUTE_15", "MINUTE_30", "HOUR", "HOUR_2", "HOUR_3", 
            "HOUR_4", "DAY", "WEEK"
        ]
        
        if resolution not in valid_resolutions:
            return {
                "success": False,
                "error": f"Invalid resolution. Must be one of: {valid_resolutions}",
                "prices": []
            }

        if max_points > 1000:
            max_points = 1000
            logger.warning("max_points limited to 1000 as per API constraints")

        # Build URL and parameters
        url = f"{self.base_url}/prices/{epic}"
        params = {
            "resolution": resolution,
            "max": max_points
        }

        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process the price data to make it more usable
                processed_prices = []
                if "prices" in data:
                    for price_point in data["prices"]:
                        # Extract bid/ask prices
                        open_bid = price_point.get("openPrice", {}).get("bid", 0.0)
                        open_ask = price_point.get("openPrice", {}).get("ask", 0.0)
                        high_bid = price_point.get("highPrice", {}).get("bid", 0.0)
                        high_ask = price_point.get("highPrice", {}).get("ask", 0.0)
                        low_bid = price_point.get("lowPrice", {}).get("bid", 0.0)
                        low_ask = price_point.get("lowPrice", {}).get("ask", 0.0)
                        close_bid = price_point.get("closePrice", {}).get("bid", 0.0)
                        close_ask = price_point.get("closePrice", {}).get("ask", 0.0)
                        
                        # Calculate mid prices as average of bid and ask
                        open_mid = (open_bid + open_ask) / 2 if open_bid > 0 and open_ask > 0 else 0.0
                        high_mid = (high_bid + high_ask) / 2 if high_bid > 0 and high_ask > 0 else 0.0
                        low_mid = (low_bid + low_ask) / 2 if low_bid > 0 and low_ask > 0 else 0.0
                        close_mid = (close_bid + close_ask) / 2 if close_bid > 0 and close_ask > 0 else 0.0
                        
                        processed_point = {
                            "timestamp": price_point.get("snapshotTime"),
                            "timestamp_utc": price_point.get("snapshotTimeUTC"),
                            "open": open_mid,
                            "high": high_mid,
                            "low": low_mid,
                            "close": close_mid,
                            "volume": price_point.get("lastTradedVolume", 0),
                            "open_bid": open_bid,
                            "open_ask": open_ask,
                            "high_bid": high_bid,
                            "high_ask": high_ask,
                            "low_bid": low_bid,
                            "low_ask": low_ask,
                            "close_bid": close_bid,
                            "close_ask": close_ask,
                        }
                        processed_prices.append(processed_point)

                return {
                    "success": True,
                    "epic": epic,
                    "resolution": resolution,
                    "instrument_type": data.get("instrumentType", "UNKNOWN"),
                    "prices": processed_prices,
                    "metadata": {
                        "total_points": len(processed_prices),
                        "from_date": from_date,
                        "to_date": to_date,
                        "max_requested": max_points
                    }
                }
            
            elif response.status_code == 401:
                logger.warning("Session expired, attempting to renew")
                if self.create_session()["success"]:
                    # Retry once with new session
                    response = self.session.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        # Process data same as above
                        processed_prices = []
                        if "prices" in data:
                            for price_point in data["prices"]:
                                processed_point = {
                                    "timestamp": price_point.get("snapshotTime"),
                                    "timestamp_utc": price_point.get("snapshotTimeUTC"),
                                    "open": price_point.get("openPrice", {}).get("mid", 0.0),
                                    "high": price_point.get("highPrice", {}).get("mid", 0.0),
                                    "low": price_point.get("lowPrice", {}).get("mid", 0.0),
                                    "close": price_point.get("closePrice", {}).get("mid", 0.0),
                                    "volume": price_point.get("lastTradedVolume", 0),
                                    "open_bid": price_point.get("openPrice", {}).get("bid", 0.0),
                                    "open_ask": price_point.get("openPrice", {}).get("ask", 0.0),
                                    "high_bid": price_point.get("highPrice", {}).get("bid", 0.0),
                                    "high_ask": price_point.get("highPrice", {}).get("ask", 0.0),
                                    "low_bid": price_point.get("lowPrice", {}).get("bid", 0.0),
                                    "low_ask": price_point.get("lowPrice", {}).get("ask", 0.0),
                                    "close_bid": price_point.get("closePrice", {}).get("bid", 0.0),
                                    "close_ask": price_point.get("closePrice", {}).get("ask", 0.0),
                                }
                                processed_prices.append(processed_point)

                        return {
                            "success": True,
                            "epic": epic,
                            "resolution": resolution,
                            "instrument_type": data.get("instrumentType", "UNKNOWN"),
                            "prices": processed_prices,
                            "metadata": {
                                "total_points": len(processed_prices),
                                "from_date": from_date,
                                "to_date": to_date,
                                "max_requested": max_points
                            }
                        }

            # Handle error responses
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                if "errorCode" in error_data:
                    error_msg = f"{error_data['errorCode']}: {error_data.get('message', 'Unknown error')}"
            except:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"

            logger.error(f"Failed to get historical prices for {epic}: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "prices": []
            }

        except requests.exceptions.Timeout:
            logger.error(f"Timeout getting historical prices for {epic}")
            return {
                "success": False,
                "error": "Request timeout",
                "prices": []
            }
        except Exception as e:
            logger.error(f"Error getting historical prices for {epic}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "prices": []
            }

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
            "session_created_at": (
                self.session_created_at.isoformat() if self.session_created_at else None
            ),
            "last_activity": self.last_activity,
        }

        try:
            with open(self.session_file, "w") as f:
                json.dump(session_data, f)
            logger.debug("Session saved to file")
        except Exception as e:
            logger.warning(f"Failed to save session to file: {str(e)}")

    def _load_session_from_file(self):
        """Load session data from file if available and valid"""
        try:
            if not os.path.exists(self.session_file):
                return

            with open(self.session_file, "r") as f:
                session_data = json.load(f)

            # Check if session data is complete
            if not all(
                key in session_data
                for key in ["cst_token", "security_token", "session_created_at"]
            ):
                logger.debug("Incomplete session data in file")
                return

            # Parse session creation time
            session_created_at = datetime.fromisoformat(
                session_data["session_created_at"]
            )

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

        time_until_expiry = (
            self.session_timeout - session_age if self.session_active else 0
        )
        time_until_renewal = (
            self.renewal_threshold - session_age if self.session_active else 0
        )

        return {
            "session_active": self.session_active,
            "session_age_seconds": session_age,
            "time_until_expiry_seconds": max(0, time_until_expiry),
            "time_until_renewal_seconds": max(0, time_until_renewal),
            "failed_requests": self.failed_requests,
            "max_failed_requests": self.max_failed_requests,
            "session_renewals": self.session_renewals,
            "session_failures": self.session_failures,
            "last_session_failure": (
                self.last_session_failure.isoformat()
                if self.last_session_failure
                else None
            ),
            "last_health_check": (
                self.last_health_check.isoformat() if self.last_health_check else None
            ),
            "session_healthy": self._is_session_healthy(),
            "needs_renewal": self._should_renew_session(),
            "environment": "demo" if self.config.use_demo else "live",
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
            "error",
        )

        # Alert if too many failures
        if self.session_failures > 3:
            self._log_session_alert(
                "HIGH_FAILURE_RATE",
                f"High session failure rate detected: {self.session_failures} failures",
                "error",
            )

    def _track_session_renewal(self, reason: str):
        """Track session renewals for monitoring"""
        self.session_renewals += 1

        self._log_session_alert(
            "SESSION_RENEWAL",
            f"Session renewal #{self.session_renewals}: {reason}",
            "info",
        )

    def place_order(
        self,
        epic: str,
        direction: str,
        size: float,
        order_type: str = "MARKET",
        stop_level: Optional[float] = None,
        limit_level: Optional[float] = None,
        guaranteed_stop: bool = False,
        force_open: bool = True,
        trailing_stop: bool = False,
        stop_distance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Place a trading order on Capital.com

        Args:
            epic: Market identifier (e.g., "ETHUSD")
            direction: "BUY" or "SELL"
            size: Order size
            order_type: "MARKET" or "LIMIT" (default: "MARKET")
            stop_level: Stop loss level (optional, cannot be used with trailing_stop)
            limit_level: Take profit level (optional)
            guaranteed_stop: Whether to use guaranteed stop (default: False, cannot be used with trailing_stop)
            force_open: Whether to force open new position (default: True)
            trailing_stop: Whether to use trailing stop (default: False)
            stop_distance: Distance for trailing stop in points (required if trailing_stop=True)

        Returns:
            Dict containing order result
        """
        if not self._ensure_valid_session():
            return {"success": False, "error": "Failed to establish valid session"}

        # Validar parámetros de trailing stop según documentación de Capital.com
        if trailing_stop:
            if stop_distance is None:
                return {
                    "success": False,
                    "error": "stopDistance is required when trailingStop is true",
                }
            if guaranteed_stop:
                return {
                    "success": False,
                    "error": "trailingStop cannot be used with guaranteedStop",
                }
            if stop_level is not None:
                logger.warning(
                    "stopLevel will be ignored when using trailingStop, using stopDistance instead"
                )

        # Verificar si el mercado está disponible para operar usando la API de Capital.com
        market_check = self.is_market_tradeable(epic)
        if not market_check.get("tradeable", False):
            market_status = market_check.get("market_status", "UNKNOWN")
            logger.warning(f"Market {epic} is not tradeable: status is {market_status}")
            return {
                "success": False,
                "error": f"Market not tradeable: {epic} status is {market_status}",
                "epic": epic,
                "market_status": market_status,
            }

        # Endpoint correcto según documentación oficial
        url = f"{self.base_url}/positions"

        # Prepare order data según formato oficial de Capital.com
        order_data = {
            "epic": epic,
            "direction": direction.upper(),
            "size": size,  # Enviar como número, no string
            "guaranteedStop": guaranteed_stop,
        }

        # Configurar trailing stop o stop loss tradicional
        if trailing_stop:
            order_data["trailingStop"] = True
            order_data["stopDistance"] = stop_distance
            logger.info(f"🎯 Using trailing stop with distance: {stop_distance} points")
        else:
            # Add stop and limit levels if provided (nombres correctos según API)
            if stop_level is not None:
                order_data["stopLevel"] = stop_level

        # Add take profit level if provided
        if limit_level is not None:
            order_data["profitLevel"] = (
                limit_level  # Capital.com usa 'profitLevel' no 'limitLevel'
            )

        try:
            logger.info(
                f"Placing {direction} order for {epic}: size={size}, type={order_type}"
            )
            logger.info(f"Order payload: {order_data}")

            response = self.session.post(url, json=order_data)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Order placed successfully: {result}")
                return {
                    "success": True,
                    "deal_reference": result.get("dealReference"),
                    "deal_id": result.get("dealId"),
                    "epic": epic,
                    "direction": direction,
                    "size": size,
                    "order_type": order_type,
                    "response": result,
                }
            else:
                error_msg = (
                    f"Failed to place order: {response.status_code} - {response.text}"
                )
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code,
                }

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error placing order: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def buy_market_order(
        self,
        epic: str,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trailing_stop: bool = False,
        stop_distance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Place a market buy order

        Args:
            epic: Market identifier (e.g., "ETHUSD")
            size: Order size
            stop_loss: Stop loss level (optional, ignored if trailing_stop=True)
            take_profit: Take profit level (optional)
            trailing_stop: Whether to use trailing stop (default: False)
            stop_distance: Distance for trailing stop in points (required if trailing_stop=True)

        Returns:
            Dict containing order result
        """
        return self.place_order(
            epic=epic,
            direction="BUY",
            size=size,
            order_type="MARKET",
            stop_level=stop_loss,
            limit_level=take_profit,
            trailing_stop=trailing_stop,
            stop_distance=stop_distance,
        )

    def sell_market_order(
        self,
        epic: str,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trailing_stop: bool = False,
        stop_distance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Place a market sell order

        Args:
            epic: Market identifier (e.g., "ETHUSD")
            size: Order size
            stop_loss: Stop loss level (optional, ignored if trailing_stop=True)
            take_profit: Take profit level (optional)
            trailing_stop: Whether to use trailing stop (default: False)
            stop_distance: Distance for trailing stop in points (required if trailing_stop=True)

        Returns:
            Dict containing order result
        """
        return self.place_order(
            epic=epic,
            direction="SELL",
            size=size,
            order_type="MARKET",
            stop_level=stop_loss,
            limit_level=take_profit,
            trailing_stop=trailing_stop,
            stop_distance=stop_distance,
        )

    def get_positions(self) -> Dict[str, Any]:
        """
        Get all open positions

        Returns:
            Dict containing positions data
        """
        if not self._ensure_valid_session():
            return {"success": False, "error": "Failed to establish valid session"}

        url = f"{self.base_url}/positions"

        try:
            response = self.session.get(url)

            if response.status_code == 200:
                result = response.json()
                return {"success": True, "positions": result.get("positions", [])}
            else:
                error_msg = (
                    f"Failed to get positions: {response.status_code} - {response.text}"
                )
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error getting positions: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def find_position_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        Find open positions for a specific symbol
        
        Args:
            symbol: The symbol to search for (e.g., 'EURUSD')
            
        Returns:
            Dict containing matching positions or error
        """
        positions_result = self.get_positions()
        
        if not positions_result.get("success"):
            return positions_result
            
        positions = positions_result.get("positions", [])
        
        # Convert symbol to Capital.com format for comparison
        capital_symbol = self.get_capital_symbol(symbol)
        
        # Find positions matching the symbol
        matching_positions = []
        for position in positions:
            position_epic = position.get("epic", "")
            if position_epic == capital_symbol:
                matching_positions.append(position)
                
        return {
            "success": True,
            "positions": matching_positions,
            "symbol": symbol,
            "capital_symbol": capital_symbol,
            "count": len(matching_positions)
        }

    def find_position_by_deal_id(self, deal_id: str) -> Dict[str, Any]:
        """
        Find a specific position by deal ID
        
        Args:
            deal_id: The deal ID to search for
            
        Returns:
            Dict containing the position or error
        """
        positions_result = self.get_positions()
        
        if not positions_result.get("success"):
            return positions_result
            
        positions = positions_result.get("positions", [])
        
        # Find position with matching deal ID
        for position in positions:
            if position.get("dealId") == deal_id:
                return {
                    "success": True,
                    "position": position,
                    "found": True
                }
                
        return {
            "success": True,
            "position": None,
            "found": False,
            "message": f"Position with deal ID {deal_id} not found"
        }

    def close_position(
        self, deal_id: str, direction: str = None, size: float = None
    ) -> Dict[str, Any]:
        """
        Close an existing position using DELETE method with pre-verification

        Args:
            deal_id: Deal ID of the position to close
            direction: Not used with DELETE method (kept for compatibility)
            size: Not used with DELETE method (kept for compatibility)

        Returns:
            Dict containing close result
        """
        if not self._ensure_valid_session():
            return {"success": False, "error": "Failed to establish valid session", "error_type": "session"}

        # First, verify the position exists before attempting to close it
        logger.info(f"Verifying position {deal_id} exists before closing")
        position_check = self.find_position_by_deal_id(deal_id)
        
        if not position_check["success"]:
            # Error getting positions (session, network, etc.)
            logger.error(f"Failed to verify position {deal_id}: {position_check.get('error')}")
            return position_check
        
        if not position_check.get("found", False):
            # Position not found - already closed or invalid
            logger.warning(f"⚠️ Position {deal_id} not found - already closed or invalid")
            return {
                "success": True,  # Treat as success since position is already closed
                "deal_id": deal_id,
                "error_type": "already_closed",
                "message": "Position already closed or not found"
            }

        # Position exists, proceed with closing
        position_data = position_check["position"]
        logger.info(f"Position {deal_id} verified - Symbol: {position_data.get('market', {}).get('instrumentName')}, "
                   f"Direction: {position_data.get('direction')}, Size: {position_data.get('size')}")

        # Use DELETE method with deal_id in URL path as per Capital.com API documentation
        url = f"{self.base_url}/positions/{deal_id}"

        try:
            logger.info(f"Closing position {deal_id} using DELETE method")
            response = self.session.delete(url)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Position closed successfully: {result}")
                return {
                    "success": True,
                    "deal_reference": result.get("dealReference"),
                    "deal_id": deal_id,
                    "response": result,
                    "position_data": position_data  # Include original position data
                }
            else:
                # Parse error response to get specific error details
                error_details = self._parse_api_error(response)
                error_msg = f"Failed to close position: {response.status_code} - {response.text}"
                
                # Handle specific error types
                if error_details.get("errorCode") == "error.invalid.dealId":
                    logger.warning(f"⚠️ Position {deal_id} became invalid during close attempt - marking as resolved")
                    return {
                        "success": True,  # Treat as success since position is no longer available
                        "deal_id": deal_id,
                        "error_type": "already_closed",
                        "message": "Position became invalid during close attempt"
                    }
                
                logger.error(error_msg)
                return {
                    "success": False, 
                    "error": error_msg,
                    "error_type": error_details.get("errorCode", "api_error"),
                    "error_details": error_details,
                    "position_data": position_data
                }

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error closing position: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "error_type": "network", "position_data": position_data}

    def _parse_api_error(self, response) -> Dict[str, Any]:
        """
        Parse API error response to extract error details
        
        Args:
            response: HTTP response object
            
        Returns:
            Dict containing parsed error details
        """
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                return {
                    "errorCode": error_data.get("errorCode", "unknown"),
                    "errorMessage": error_data.get("errorMessage", ""),
                    "status_code": response.status_code
                }
        except (ValueError, KeyError):
            pass
        
        return {
            "errorCode": "parse_error",
            "errorMessage": response.text,
            "status_code": response.status_code
        }

    def is_market_tradeable(self, symbol: str) -> Dict[str, Any]:
        """
        Check if a market is currently tradeable

        Args:
            symbol: Trading symbol (epic)

        Returns:
            Dict containing market status information
        """
        try:
            # Usar tanto searchTerm como epics para obtener el estado correcto del mercado
            # Esto sigue el patrón de los ejemplos: /markets?searchTerm=btcusd&epics=BTCUSD
            search_term = symbol.lower()  # searchTerm en minúsculas
            epics_param = symbol.upper()  # epics en mayúsculas

            if not self._ensure_valid_session():
                return {
                    "success": False,
                    "tradeable": False,
                    "error": "Failed to establish valid session",
                }

            url = f"{self.base_url}/markets"
            params = {"searchTerm": search_term, "epics": epics_param}

            try:
                response = self.session.get(url, params=params, timeout=10)
                self.last_activity = time.time()

                if response.status_code != 200:
                    error_msg = f"Failed to get market status: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return {"success": False, "tradeable": False, "error": error_msg}

                markets_response = response.json()
                logger.debug(f"Markets response for {symbol}: {markets_response}")

                # Handle different response formats
                markets = []
                if "markets" in markets_response:
                    markets = markets_response["markets"]
                elif "marketDetails" in markets_response:
                    markets = markets_response["marketDetails"]

                if not markets:
                    return {
                        "success": False,
                        "tradeable": False,
                        "error": f"Market {symbol} not found",
                    }

                # Find the specific market
                market_info = None
                for market in markets:
                    # Check both epic and instrument.epic for different response formats
                    market_epic = market.get("epic") or market.get(
                        "instrument", {}
                    ).get("epic")
                    # Compare with both original symbol and uppercase version
                    if market_epic == symbol or market_epic == epics_param:
                        market_info = market
                        break

                if not market_info:
                    return {
                        "success": False,
                        "tradeable": False,
                        "error": f"Market {symbol} not found in response",
                    }

                # Get market status from different possible locations
                market_status = (
                    market_info.get("marketStatus")
                    or market_info.get("snapshot", {}).get("marketStatus")
                    or "UNKNOWN"
                )

                is_tradeable = market_status == "TRADEABLE"

                logger.info(
                    f"📊 Market {symbol} status: {market_status} (tradeable: {is_tradeable})"
                )

                return {
                    "success": True,
                    "tradeable": is_tradeable,
                    "market_status": market_status,
                    "symbol": symbol,
                    "market_info": market_info,
                }

            except requests.exceptions.RequestException as e:
                error_msg = f"Network error checking market status: {str(e)}"
                logger.error(error_msg)
                return {"success": False, "tradeable": False, "error": error_msg}

        except Exception as e:
            error_msg = f"Error checking market status for {symbol}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "tradeable": False, "error": error_msg}

    def is_trailing_stop_available(self, epic: str) -> Dict[str, Any]:
        """
        Check if trailing stops are available for a specific instrument

        Args:
            epic: Instrument epic identifier

        Returns:
            Dict containing trailing stop availability information
        """
        try:
            # First check if trailing stops are enabled at account level
            if not self.trailing_stops_enabled:
                return {
                    "success": True,
                    "available": False,
                    "reason": "Trailing stops are disabled for this account",
                    "account_enabled": False,
                    "instrument_supported": None,
                }

            # Get market details to check instrument-specific trailing stop support
            market_info = self.get_markets(epics=[epic])

            if not market_info.get("success", False):
                return {
                    "success": False,
                    "available": False,
                    "reason": f"Failed to get market information for {epic}",
                    "account_enabled": True,
                    "instrument_supported": None,
                }

            # Check if market data contains dealing rules
            market_details = market_info.get("data", {}).get("marketDetails", [])
            if not market_details:
                return {
                    "success": True,
                    "available": False,
                    "reason": f"No market details found for {epic}",
                    "account_enabled": True,
                    "instrument_supported": False,
                }

            # Check trailing stop preference in dealing rules
            dealing_rules = market_details[0].get("dealingRules", {})
            trailing_preference = dealing_rules.get(
                "trailingStopsPreference", "NOT_AVAILABLE"
            )

            is_available = trailing_preference != "NOT_AVAILABLE"

            return {
                "success": True,
                "available": is_available,
                "reason": f"Trailing stops preference: {trailing_preference}",
                "account_enabled": True,
                "instrument_supported": is_available,
                "trailing_preference": trailing_preference,
            }

        except Exception as e:
            logger.error(f"Error checking trailing stop availability for {epic}: {e}")
            return {
                "success": False,
                "available": False,
                "reason": f"Error checking trailing stop availability: {str(e)}",
                "account_enabled": self.trailing_stops_enabled,
                "instrument_supported": None,
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
                self.session_created_at = None

                # Remove auth headers
                self.session.headers.pop("CST", None)
                self.session.headers.pop("X-SECURITY-TOKEN", None)

                # Delete session file
                self._delete_session_file()

                logger.info("Session closed successfully")
                return {"success": True, "message": "Session closed"}
            else:
                error_msg = (
                    f"Failed to close session: {response.status_code} - {response.text}"
                )
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
        live_url=os.getenv(
            "CAPITAL_LIVE_URL", "https://api-capital.backend-capital.com/api/v1"
        ),
        demo_url=os.getenv(
            "CAPITAL_DEMO_URL", "https://demo-api-capital.backend-capital.com/api/v1"
        ),
        identifier=os.getenv("identifier", ""),
        password=os.getenv("password", ""),
        api_key=os.getenv("X-CAP-API-KEY", ""),
        encrypted_password=os.getenv("encryptedPassword", ""),
        use_demo=os.getenv("IS_DEMO", "true").lower() == "true",
    )

    # Debug: Log configuration (without sensitive data)
    logger.info(f"Capital.com config - Demo mode: {config.use_demo}")
    logger.info(
        f"Capital.com config - Base URL: {config.demo_url if config.use_demo else config.live_url}"
    )
    logger.info(
        f"Capital.com config - Identifier set: {'Yes' if config.identifier else 'No'}"
    )
    logger.info(
        f"Capital.com config - Password set: {'Yes' if config.password else 'No'}"
    )
    logger.info(
        f"Capital.com config - API Key set: {'Yes' if config.api_key else 'No'}"
    )

    return CapitalClient(config)

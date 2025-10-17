"""
🗄️ Universal Trading Analyzer - Database Manager
Gestor de base de datos SQLite con SQLAlchemy
"""

import os
import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator, Optional
from datetime import datetime
import time

from src.config.main_config import CacheConfig

from .models import Base, Trade, Portfolio, Strategy, BacktestResult, TradingSignal, Settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    🗄️ Gestor principal de la base de datos SQLite
    """
    
    def __init__(self, database_url: str = None):
        """
        Inicializar el gestor de base de datos
        
        Args:
            database_url: URL de la base de datos SQLite
        """
        # Configurar ruta de base de datos usando ruta absoluta
        if database_url is None:
            # Obtener directorio actual del archivo (database/)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Crear ruta completa para la base de datos en el mismo directorio
            db_path = os.path.join(current_dir, "trading_bot.db")
            database_url = f"sqlite:///{db_path}"
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},  # Necesario para SQLite
            echo=False  # Cambiar a True para ver SQL queries
        )
        
        # Crear session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Crear tablas si no existen
        self.create_tables()
        
        # Inicializar PAPER_GLOBAL_INITIAL_BALANCE en settings si no existe
        from src.config.main_config import PAPER_GLOBAL_INITIAL_BALANCE
        try:
            self.set_global_initial_balance_if_absent(PAPER_GLOBAL_INITIAL_BALANCE)
        except Exception as e:
            logger.error(f"⚠️ No se pudo inicializar PAPER_GLOBAL_INITIAL_BALANCE desde config: {e}")
        
        # Inicializar portfolio base si no existe
        self.initialize_base_portfolio()
        
        logger.info(f"✅ Database initialized: {database_url}")
    
    def create_tables(self):
        """
        🏗️ Crear todas las tablas en la base de datos
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables created/verified")
        except SQLAlchemyError as e:
            logger.error(f"❌ Error creating tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        🔗 Obtener una nueva sesión de base de datos
        
        Returns:
            Session: Nueva sesión de SQLAlchemy
        """
        return self.SessionLocal()
    
    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """
        🔗 Context manager para sesiones de base de datos
        
        Yields:
            Session: Sesión de base de datos con auto-cleanup
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Database error: {e}")
            raise
        finally:
            session.close()
    
    # === Global Settings helpers ===
    def get_global_initial_balance(self) -> float:
        """
        Obtener el balance inicial global desde la DB (Settings), fallback seguro a 0.0
        """
        try:
            with self.get_db_session() as session:
                setting = session.query(Settings).filter(Settings.key == "GLOBAL_INITIAL_BALANCE").first()
                return float(setting.value) if setting and setting.value is not None else 0.0
        except Exception as e:
            logger.error(f"❌ Error leyendo GLOBAL_INITIAL_BALANCE: {e}")
            return 0.0
    
    def set_global_initial_balance_if_absent(self, value: float) -> None:
        """
        Setear GLOBAL_INITIAL_BALANCE en DB si no existe. No sobreescribe si ya está definido.
        """
        try:
            with self.get_db_session() as session:
                existing = session.query(Settings).filter(Settings.key == "GLOBAL_INITIAL_BALANCE").first()
                if not existing:
                    setting = Settings(key="GLOBAL_INITIAL_BALANCE", value=float(value) if value is not None else 0.0)
                    session.add(setting)
                    session.commit()
                    logger.info(f"💾 GLOBAL_INITIAL_BALANCE seteado en DB: ${setting.value:,.2f}")
        except Exception as e:
            logger.error(f"❌ Error seteando GLOBAL_INITIAL_BALANCE: {e}")
    
    def initialize_base_portfolio(self):
        """
        💼 Inicializar portfolio base con USD virtual
        """
        try:
            with self.get_db_session() as session:
                # Verificar si ya existe portfolio USD
                existing_USD = session.query(Portfolio).filter(
                    Portfolio.symbol == "USD",
                    Portfolio.is_paper == True
                ).first()
                
                if not existing_USD:
                    initial_balance_db = self.get_global_initial_balance()
                    # Crear portfolio inicial con USD del setting global (fallback segura a 0)
                    initial_portfolio = Portfolio(
                        symbol="USD",
                        quantity=initial_balance_db,
                        avg_price=1.0,
                        current_price=1.0,
                        current_value=initial_balance_db,
                        unrealized_pnl=0.0,
                        unrealized_pnl_percentage=0.0,
                        is_paper=True
                    )
                    
                    session.add(initial_portfolio)
                    session.commit()
                    logger.info(f"💰 Initialized paper trading portfolio with ${initial_balance_db:,.2f} USD")
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error initializing portfolio: {e}")
    
    def _get_current_price(self, symbol: str) -> float:
        """
        Obtener precio actual del símbolo usando Capital.com para símbolos mapeados.
        """
        try:
            if symbol and symbol.upper() == "USD":
                return 1.0
                
            # Cache management
            now = time.time()
            ttl = CacheConfig.get_ttl_for_operation("price_data")
            cache = getattr(self, "_price_cache", {})
            cache_ts = getattr(self, "_price_cache_ts", {})
            last_ts = cache_ts.get(symbol, 0)
            if symbol in cache and (now - last_ts) < ttl:
                return float(cache[symbol])
            
            # Verificar si el símbolo está en GLOBAL_SYMBOLS (Capital.com)
            try:
                from src.config.main_config import GLOBAL_SYMBOLS
                
                # Buscar el símbolo directamente en GLOBAL_SYMBOLS
                if symbol in GLOBAL_SYMBOLS:
                    # Usar Capital.com para símbolos en GLOBAL_SYMBOLS
                    from src.core.capital_client import create_capital_client_from_env
                    capital_client = create_capital_client_from_env()
                    
                    # Obtener precio de Capital.com usando el nuevo método get_market_data
                    market_data = capital_client.get_market_data([symbol])
                    if market_data and symbol in market_data and market_data[symbol]:
                        symbol_data = market_data[symbol]
                        # Usar el precio medio entre bid y offer
                        if 'mid' in symbol_data and symbol_data['mid']:
                            current_price = float(symbol_data['mid'])
                        elif 'bid' in symbol_data and 'offer' in symbol_data:
                            bid = float(symbol_data['bid']) if symbol_data['bid'] else 0
                            offer = float(symbol_data['offer']) if symbol_data['offer'] else 0
                            current_price = (bid + offer) / 2 if bid > 0 and offer > 0 else 0
                        else:
                            current_price = 0.0
                        
                        if current_price > 0:
                            # Guardar en cache
                            cache[symbol] = current_price
                            cache_ts[symbol] = now
                            setattr(self, "_price_cache", cache)
                            setattr(self, "_price_cache_ts", cache_ts)
                            
                            logger.debug(f"✅ Precio obtenido de Capital.com para {symbol}: ${current_price:.4f}")
                            return current_price
                    
                    logger.warning(f"⚠️ No se pudo obtener precio de Capital.com para {symbol}")
                        
            except Exception as capital_error:
                logger.warning(f"⚠️ Error obteniendo precio de Capital.com para {symbol}: {capital_error}")
            
            # Si llegamos aquí, no pudimos obtener el precio
            logger.error(f"❌ No se pudo obtener precio para {symbol} - no disponible en Capital.com")
            return 0.0
        except Exception as e:
            logger.error(f"❌ Error fetching current price for {symbol}: {e}")
            return 0.0
    
    def _convert_symbol_to_usd_format(self, symbol: str) -> str:
        """
        Convierte un símbolo almacenado en el portfolio de vuelta al formato USD para obtener precios.
        Ejemplo: ETH -> ETHUSD, BTC -> BTCUSD
        """
        if symbol == "USD" or symbol.endswith("USD"):
            return symbol
        return f"{symbol}USD"

    def get_portfolio_summary(self, is_paper: bool = True) -> dict:
        """
        📊 Obtener resumen del portfolio
        
        Args:
            is_paper: Si es paper trading (True) o real (False)
            
        Returns:
            dict: Resumen del portfolio
        """
        try:
            with self.get_db_session() as session:
                portfolio_items = session.query(Portfolio).filter(
                    Portfolio.is_paper == is_paper
                ).all()
                
                # Refrescar precios y valores actuales
                for item in portfolio_items:
                    try:
                        if item.symbol == "USD":
                            item.current_price = 1.0
                            item.current_value = float(item.quantity or 0.0)
                        else:
                            # Convertir el símbolo de vuelta al formato USD para obtener el precio
                            price_symbol = self._convert_symbol_to_usd_format(item.symbol)
                            price = self._get_current_price(price_symbol)
                            if price > 0:
                                item.current_price = price
                                item.current_value = float(item.quantity or 0.0) * price
                                if (item.quantity or 0.0) > 0 and (item.avg_price or 0.0) > 0:
                                    cost_basis = float(item.quantity) * float(item.avg_price)
                                    item.unrealized_pnl = item.current_value - cost_basis
                                    item.unrealized_pnl_percentage = (item.unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0.0
                        item.last_updated = datetime.now()
                    except Exception as e:
                        logger.error(f"❌ Error refreshing portfolio item {item.symbol}: {e}")
                session.commit()
                
                total_value = sum(item.current_value or 0 for item in portfolio_items)
                total_pnl = sum(item.unrealized_pnl or 0 for item in portfolio_items)
                base_value = self.get_global_initial_balance()
                
                # Disponible en USD (cash)
                USD_entry = session.query(Portfolio).filter(
                    Portfolio.symbol == "USD",
                    Portfolio.is_paper == is_paper
                ).first()
                available_balance = float(USD_entry.quantity) if USD_entry and USD_entry.quantity is not None else 0.0
                
                return {
                    "total_value": round(total_value, 2),
                    "total_pnl": round(total_pnl, 2),
                    "total_pnl_percentage": round((total_pnl / base_value) * 100, 2) if base_value > 0 else 0,
                    "available_balance": round(available_balance, 2),
                    "initial_balance": round(base_value, 2),
                    "assets": [
                        {
                            "symbol": item.symbol,
                            "quantity": item.quantity,
                            "current_value": item.current_value,
                            "unrealized_pnl": item.unrealized_pnl
                        }
                        for item in portfolio_items
                        if item.quantity > 0.00001
                    ]
                }
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting portfolio summary: {e}")
            return {"error": str(e)}
    
    def get_active_trades(self, is_paper: bool = True) -> list:
        """
        📈 Obtener trades activos (posiciones abiertas)
        
        Args:
            is_paper: Si es paper trading (True) o real (False)
            
        Returns:
            list: Lista de trades activos
        """
        try:
            with self.get_db_session() as session:
                active_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper,
                    Trade.status == 'OPEN'
                ).all()
                
                # Convertir a formato esperado por PositionAdjuster
                trades_data = []
                for trade in active_trades:
                    trade_data = {
                        'id': trade.id,
                        'symbol': trade.symbol,
                        'side': trade.trade_type,  # BUY/SELL
                        'quantity': trade.quantity,
                        'entry_price': trade.entry_price,
                        'current_price': trade.entry_price,  # Se actualizará con precio actual
                        'stop_loss': trade.stop_loss,
                        'take_profit': trade.take_profit,
                        'pnl': trade.pnl if trade.pnl else 0.0,
                        'status': trade.status,
                        'entry_time': trade.entry_time
                    }
                    trades_data.append(trade_data)
                
                return trades_data
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting active trades: {e}")
            return []
    
    def get_last_trade_for_symbol(self, symbol: str, is_paper: bool = True) -> Optional[float]:
        """
        💰 Obtener el precio del último trade para un símbolo
        
        Args:
            symbol: Símbolo del activo (ej: BTCUSD)
            is_paper: Si es paper trading (True) o real (False)
            
        Returns:
            float: Precio del último trade o None si no hay trades
        """
        try:
            with self.get_db_session() as session:
                last_trade = session.query(Trade).filter(
                    Trade.symbol == symbol,
                    Trade.is_paper_trade == is_paper
                ).order_by(Trade.entry_time.desc()).first()
                
                if last_trade:
                    # Retornar exit_price si está cerrado, sino entry_price
                    return last_trade.exit_price if last_trade.exit_price else last_trade.entry_price
                else:
                    logger.warning(f"⚠️ No se encontraron trades para {symbol}")
                    return None
                    
        except SQLAlchemyError as e:
            logger.error(f"❌ Error getting last trade for {symbol}: {e}")
            return None

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    """
    🔗 Dependency para FastAPI - obtener sesión de base de datos
    
    Yields:
        Session: Sesión de base de datos
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
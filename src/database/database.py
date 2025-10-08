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
        
        # Inicializar GLOBAL_INITIAL_BALANCE en settings si no existe
        from src.config.main_config import GLOBAL_INITIAL_BALANCE
        try:
            self.set_global_initial_balance_if_absent(GLOBAL_INITIAL_BALANCE)
        except Exception as e:
            logger.error(f"⚠️ No se pudo inicializar GLOBAL_INITIAL_BALANCE desde config: {e}")
        
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
        💼 Inicializar portfolio base con USDT virtual
        """
        try:
            with self.get_db_session() as session:
                # Verificar si ya existe portfolio USDT
                existing_usdt = session.query(Portfolio).filter(
                    Portfolio.symbol == "USDT",
                    Portfolio.is_paper == True
                ).first()
                
                if not existing_usdt:
                    initial_balance_db = self.get_global_initial_balance()
                    # Crear portfolio inicial con USDT del setting global (fallback segura a 0)
                    initial_portfolio = Portfolio(
                        symbol="USDT",
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
                    logger.info(f"💰 Initialized paper trading portfolio with ${initial_balance_db:,.2f} USDT")
                
        except SQLAlchemyError as e:
            logger.error(f"❌ Error initializing portfolio: {e}")
    
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
                
                total_value = sum(item.current_value or 0 for item in portfolio_items)
                total_pnl = sum(item.unrealized_pnl or 0 for item in portfolio_items)
                base_value = self.get_global_initial_balance()
                
                # Disponible en USDT (cash)
                usdt_entry = session.query(Portfolio).filter(
                    Portfolio.symbol == "USDT",
                    Portfolio.is_paper == is_paper
                ).first()
                available_balance = float(usdt_entry.quantity) if usdt_entry and usdt_entry.quantity is not None else 0.0
                
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
            symbol: Símbolo del activo (ej: BTCUSDT)
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
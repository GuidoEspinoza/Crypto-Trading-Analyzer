"""
📊 Universal Trading Analyzer - Database Models
Modelos de datos para SQLite usando SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

# Importar constante global para consistencia
try:
    from ..config.global_constants import GLOBAL_INITIAL_BALANCE
except ImportError:
    # Fallback en caso de importación circular
    GLOBAL_INITIAL_BALANCE = 1000.0

Base = declarative_base()

class Trade(Base):
    """
    💰 Modelo para trades ejecutados (tanto paper como real)
    """
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información básica del trade
    symbol = Column(String(20), nullable=False, index=True)  # BTC/USDT
    strategy_name = Column(String(50), nullable=False, index=True)  # RSI_Basic
    trade_type = Column(String(10), nullable=False)  # BUY, SELL
    
    # Precios y cantidades
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)  # NULL si está abierto
    quantity = Column(Float, nullable=False)
    
    # Métricas financieras
    entry_value = Column(Float, nullable=False)  # entry_price * quantity
    exit_value = Column(Float, nullable=True)   # exit_price * quantity
    pnl = Column(Float, nullable=True)          # Profit/Loss realizado
    pnl_percentage = Column(Float, nullable=True)  # % return
    
    # Estado del trade
    status = Column(String(10), default="OPEN")  # OPEN, CLOSED, CANCELLED
    is_paper_trade = Column(Boolean, default=True)  # True = virtual, False = real
    
    # Risk management
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    trailing_stop = Column(Float, nullable=True)  # Trailing stop dinámico
    
    # Metadatos
    timeframe = Column(String(10), nullable=False)  # 1h, 4h, 1d
    confidence_score = Column(Float, nullable=True)  # Score de la señal
    notes = Column(Text, nullable=True)  # Notas adicionales
    
    # Timestamps
    entry_time = Column(DateTime, default=func.now(), nullable=False)
    exit_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, type={self.trade_type}, pnl={self.pnl})>"

class Portfolio(Base):
    """
    💼 Modelo para tracking del portfolio virtual/real
    """
    __tablename__ = "portfolio"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Asset information
    symbol = Column(String(20), nullable=False, index=True)  # BTC, USDT, ETH
    quantity = Column(Float, nullable=False, default=0.0)
    avg_price = Column(Float, nullable=False, default=0.0)
    
    # Valores calculados
    current_price = Column(Float, nullable=True)  # Último precio conocido
    current_value = Column(Float, nullable=True)  # quantity * current_price
    unrealized_pnl = Column(Float, nullable=True)  # Ganancia/pérdida no realizada
    unrealized_pnl_percentage = Column(Float, nullable=True)
    
    # Tipo de portfolio
    is_paper = Column(Boolean, default=True)  # True = virtual, False = real
    
    # Timestamps
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Portfolio(symbol={self.symbol}, quantity={self.quantity}, value={self.current_value})>"

class Strategy(Base):
    """
    🧠 Modelo para estrategias de trading y su performance
    """
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información de la estrategia
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    parameters = Column(Text, nullable=True)  # JSON string con parámetros
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)  # Porcentaje de trades ganadores
    
    # Financial metrics
    total_pnl = Column(Float, default=0.0)
    total_return_percentage = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    
    # Risk metrics
    avg_win = Column(Float, default=0.0)
    avg_loss = Column(Float, default=0.0)
    max_win = Column(Float, default=0.0)
    max_loss = Column(Float, default=0.0)
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_paper_only = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    last_trade_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Strategy(name={self.name}, trades={self.total_trades}, pnl={self.total_pnl})>"

class BacktestResult(Base):
    """
    📈 Modelo para resultados de backtesting
    """
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información del backtest
    strategy_name = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    
    # Período del backtest
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_days = Column(Integer, nullable=False)
    
    # Capital inicial
    initial_capital = Column(Float, nullable=False, default=GLOBAL_INITIAL_BALANCE)
    final_capital = Column(Float, nullable=False)
    
    # Performance metrics
    total_return = Column(Float, nullable=False)  # Dollar amount
    total_return_percentage = Column(Float, nullable=False)  # Percentage
    annualized_return = Column(Float, nullable=True)
    
    # Trade statistics
    total_trades = Column(Integer, nullable=False, default=0)
    winning_trades = Column(Integer, nullable=False, default=0)
    losing_trades = Column(Integer, nullable=False, default=0)
    win_rate = Column(Float, nullable=False, default=0.0)
    
    # Risk metrics
    max_drawdown = Column(Float, nullable=True)
    max_drawdown_percentage = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    calmar_ratio = Column(Float, nullable=True)
    
    # Trading metrics
    avg_trade_duration_hours = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)  # Gross profit / Gross loss
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)
    largest_win = Column(Float, nullable=True)
    largest_loss = Column(Float, nullable=True)
    
    # Strategy parameters (JSON)
    strategy_parameters = Column(Text, nullable=True)
    
    # Metadatos
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<BacktestResult(strategy={self.strategy_name}, return={self.total_return_percentage}%)>"

class TradingSignal(Base):
    """
    🎯 Modelo para señales de trading generadas
    """
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Signal information
    symbol = Column(String(20), nullable=False, index=True)
    strategy_name = Column(String(50), nullable=False, index=True)
    signal_type = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    timeframe = Column(String(10), nullable=False)
    
    # Signal data
    price = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=True)
    strength = Column(String(20), nullable=True)  # Weak, Moderate, Strong, Very Strong
    
    # Indicators data (JSON)
    indicators_data = Column(Text, nullable=True)  # JSON con todos los indicadores
    
    # Action taken
    action_taken = Column(String(20), default="NONE")  # EXECUTED, IGNORED, NONE
    trade_id = Column(Integer, nullable=True)  # FK to trades table
    
    # Timestamps
    generated_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)  # Opcional: señal expira
    
    def __repr__(self):
        return f"<TradingSignal(symbol={self.symbol}, type={self.signal_type}, confidence={self.confidence_score})>"
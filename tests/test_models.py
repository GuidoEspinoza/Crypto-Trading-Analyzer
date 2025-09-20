#!/usr/bin/env python3
"""
🧪 Tests para modelos de base de datos
Validación de todos los modelos SQLAlchemy del sistema
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import tempfile
import os

# Agregar el directorio raíz al path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Intentar importar las clases reales
try:
    from src.database.models import Trade, Portfolio, Strategy, BacktestResult, TradingSignal, Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import models: {e}")
    # Fallback a mocks si no están disponibles
    Trade = Mock
    Portfolio = Mock
    Strategy = Mock
    BacktestResult = Mock
    TradingSignal = Mock
    Base = Mock
    create_engine = Mock
    sessionmaker = Mock
    MODELS_AVAILABLE = False


class TestTradeModel(unittest.TestCase):
    """Tests para el modelo Trade."""
    
    def setUp(self):
        """Configuración inicial para tests."""
        if MODELS_AVAILABLE:
            # Crear base de datos en memoria para tests
            self.engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = Mock()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        if hasattr(self, 'session') and MODELS_AVAILABLE:
            self.session.close()
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Trade model not available")
    def test_trade_creation(self):
        """Test creación básica de trade."""
        trade = Trade(
            symbol="BTC/USDT",
            strategy_name="RSI_Basic",
            trade_type="BUY",
            entry_price=50000.0,
            quantity=0.1,
            entry_value=5000.0,
            timeframe="1h"
        )
        
        # Verificar atributos básicos
        self.assertEqual(trade.symbol, "BTC/USDT")
        self.assertEqual(trade.strategy_name, "RSI_Basic")
        self.assertEqual(trade.trade_type, "BUY")
        self.assertEqual(trade.entry_price, 50000.0)
        self.assertEqual(trade.quantity, 0.1)
        self.assertEqual(trade.entry_value, 5000.0)
        self.assertEqual(trade.timeframe, "1h")
        # Los valores por defecto se aplican al guardar en DB, no al crear el objeto
        self.assertIsNone(trade.status)  # Se aplicará "OPEN" por defecto en DB
        self.assertIsNone(trade.is_paper_trade)  # Se aplicará True por defecto en DB
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Trade model not available")
    def test_trade_with_exit(self):
        """Test trade con precio de salida y PnL."""
        trade = Trade(
            symbol="ETH/USDT",
            strategy_name="MACD_Cross",
            trade_type="BUY",
            entry_price=3000.0,
            exit_price=3150.0,
            quantity=1.0,
            entry_value=3000.0,
            exit_value=3150.0,
            pnl=150.0,
            pnl_percentage=5.0,
            status="CLOSED",
            timeframe="4h"
        )
        
        # Verificar cálculos de PnL
        self.assertEqual(trade.exit_price, 3150.0)
        self.assertEqual(trade.exit_value, 3150.0)
        self.assertEqual(trade.pnl, 150.0)
        self.assertEqual(trade.pnl_percentage, 5.0)
        self.assertEqual(trade.status, "CLOSED")
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Trade model not available")
    def test_trade_with_risk_management(self):
        """Test trade con stop loss y take profit."""
        trade = Trade(
            symbol="ADA/USDT",
            strategy_name="Bollinger_Bands",
            trade_type="BUY",
            entry_price=1.0,
            quantity=1000.0,
            entry_value=1000.0,
            stop_loss=0.95,
            take_profit=1.10,
            timeframe="1d"
        )
        
        # Verificar risk management
        self.assertEqual(trade.stop_loss, 0.95)
        self.assertEqual(trade.take_profit, 1.10)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Trade model not available")
    def test_trade_persistence(self):
        """Test persistencia en base de datos."""
        trade = Trade(
            symbol="DOT/USDT",
            strategy_name="RSI_Divergence",
            trade_type="SELL",
            entry_price=25.0,
            quantity=40.0,
            entry_value=1000.0,
            timeframe="2h",
            confidence_score=0.85
        )
        
        # Guardar en base de datos
        self.session.add(trade)
        self.session.commit()
        
        # Recuperar y verificar
        retrieved_trade = self.session.query(Trade).filter_by(symbol="DOT/USDT").first()
        self.assertIsNotNone(retrieved_trade)
        self.assertEqual(retrieved_trade.strategy_name, "RSI_Divergence")
        self.assertEqual(retrieved_trade.confidence_score, 0.85)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Trade model not available")
    def test_trade_repr(self):
        """Test representación string del trade."""
        trade = Trade(
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=50000.0,
            quantity=0.1,
            entry_value=5000.0,
            timeframe="1h"
        )
        trade.id = 1
        trade.pnl = 100.0
        
        repr_str = repr(trade)
        self.assertIn("Trade", repr_str)
        self.assertIn("id=1", repr_str)
        self.assertIn("BTC/USDT", repr_str)
        self.assertIn("BUY", repr_str)
        self.assertIn("100.0", repr_str)


class TestPortfolioModel(unittest.TestCase):
    """Tests para el modelo Portfolio."""
    
    def setUp(self):
        """Configuración inicial para tests."""
        if MODELS_AVAILABLE:
            self.engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = Mock()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        if hasattr(self, 'session') and MODELS_AVAILABLE:
            self.session.close()
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Portfolio model not available")
    def test_portfolio_creation(self):
        """Test creación básica de portfolio."""
        portfolio = Portfolio(
            symbol="BTC",
            quantity=0.5,
            avg_price=45000.0,
            current_price=50000.0,
            current_value=25000.0,
            is_paper=True
        )
        
        # Verificar atributos básicos
        self.assertEqual(portfolio.symbol, "BTC")
        self.assertEqual(portfolio.quantity, 0.5)
        self.assertEqual(portfolio.avg_price, 45000.0)
        self.assertEqual(portfolio.current_price, 50000.0)
        self.assertEqual(portfolio.current_value, 25000.0)
        self.assertTrue(portfolio.is_paper)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Portfolio model not available")
    def test_portfolio_pnl_calculation(self):
        """Test cálculo de PnL no realizado."""
        portfolio = Portfolio(
            symbol="ETH",
            quantity=10.0,
            avg_price=2000.0,
            current_price=2200.0,
            current_value=22000.0,
            unrealized_pnl=2000.0,
            unrealized_pnl_percentage=10.0
        )
        
        # Verificar cálculos de PnL
        self.assertEqual(portfolio.unrealized_pnl, 2000.0)
        self.assertEqual(portfolio.unrealized_pnl_percentage, 10.0)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Portfolio model not available")
    def test_portfolio_persistence(self):
        """Test persistencia en base de datos."""
        portfolio = Portfolio(
            symbol="USDT",
            quantity=10000.0,
            avg_price=1.0,
            current_price=1.0,
            current_value=10000.0,
            is_paper=False
        )
        
        # Guardar en base de datos
        self.session.add(portfolio)
        self.session.commit()
        
        # Recuperar y verificar
        retrieved_portfolio = self.session.query(Portfolio).filter_by(symbol="USDT").first()
        self.assertIsNotNone(retrieved_portfolio)
        self.assertEqual(retrieved_portfolio.quantity, 10000.0)
        self.assertFalse(retrieved_portfolio.is_paper)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Portfolio model not available")
    def test_portfolio_repr(self):
        """Test representación string del portfolio."""
        portfolio = Portfolio(
            symbol="ADA",
            quantity=1000.0,
            current_value=1200.0
        )
        
        repr_str = repr(portfolio)
        self.assertIn("Portfolio", repr_str)
        self.assertIn("ADA", repr_str)
        self.assertIn("1000.0", repr_str)
        self.assertIn("1200.0", repr_str)


class TestStrategyModel(unittest.TestCase):
    """Tests para el modelo Strategy."""
    
    def setUp(self):
        """Configuración inicial para tests."""
        if MODELS_AVAILABLE:
            self.engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = Mock()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        if hasattr(self, 'session') and MODELS_AVAILABLE:
            self.session.close()
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Strategy model not available")
    def test_strategy_creation(self):
        """Test creación básica de estrategia."""
        strategy = Strategy(
            name="RSI_Basic",
            description="Estrategia básica usando RSI",
            total_trades=100,
            winning_trades=65,
            losing_trades=35,
            win_rate=65.0,
            total_pnl=5000.0,
            is_active=True,
            is_paper_only=True
        )
        
        # Verificar atributos básicos
        self.assertEqual(strategy.name, "RSI_Basic")
        self.assertEqual(strategy.description, "Estrategia básica usando RSI")
        self.assertEqual(strategy.total_trades, 100)
        self.assertEqual(strategy.winning_trades, 65)
        self.assertEqual(strategy.losing_trades, 35)
        self.assertEqual(strategy.win_rate, 65.0)
        self.assertEqual(strategy.total_pnl, 5000.0)
        self.assertTrue(strategy.is_active)
        self.assertTrue(strategy.is_paper_only)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Strategy model not available")
    def test_strategy_performance_metrics(self):
        """Test métricas de performance de estrategia."""
        strategy = Strategy(
            name="MACD_Advanced",
            total_return_percentage=25.5,
            max_drawdown=-8.2,
            sharpe_ratio=1.85,
            profit_factor=2.1,
            avg_win=150.0,
            avg_loss=-75.0,
            max_win=500.0,
            max_loss=-200.0
        )
        
        # Verificar métricas de performance
        self.assertEqual(strategy.total_return_percentage, 25.5)
        self.assertEqual(strategy.max_drawdown, -8.2)
        self.assertEqual(strategy.sharpe_ratio, 1.85)
        self.assertEqual(strategy.profit_factor, 2.1)
        self.assertEqual(strategy.avg_win, 150.0)
        self.assertEqual(strategy.avg_loss, -75.0)
        self.assertEqual(strategy.max_win, 500.0)
        self.assertEqual(strategy.max_loss, -200.0)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "Strategy model not available")
    def test_strategy_persistence(self):
        """Test persistencia en base de datos."""
        strategy = Strategy(
            name="Bollinger_Squeeze",
            description="Estrategia de compresión de Bollinger Bands",
            parameters='{"period": 20, "std_dev": 2}',
            total_trades=50,
            win_rate=72.0
        )
        
        # Guardar en base de datos
        self.session.add(strategy)
        self.session.commit()
        
        # Recuperar y verificar
        retrieved_strategy = self.session.query(Strategy).filter_by(name="Bollinger_Squeeze").first()
        self.assertIsNotNone(retrieved_strategy)
        self.assertEqual(retrieved_strategy.description, "Estrategia de compresión de Bollinger Bands")
        self.assertEqual(retrieved_strategy.win_rate, 72.0)


class TestBacktestResultModel(unittest.TestCase):
    """Tests para el modelo BacktestResult."""
    
    def setUp(self):
        """Configuración inicial para tests."""
        if MODELS_AVAILABLE:
            self.engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = Mock()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        if hasattr(self, 'session') and MODELS_AVAILABLE:
            self.session.close()
    
    @unittest.skipIf(not MODELS_AVAILABLE, "BacktestResult model not available")
    def test_backtest_result_creation(self):
        """Test creación básica de resultado de backtest."""
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        
        backtest = BacktestResult(
            strategy_name="RSI_Optimized",
            symbol="BTC/USDT",
            timeframe="1h",
            start_date=start_date,
            end_date=end_date,
            total_days=365,
            initial_capital=10000.0,
            final_capital=12500.0,
            total_return=2500.0,
            total_return_percentage=25.0
        )
        
        # Verificar atributos básicos
        self.assertEqual(backtest.strategy_name, "RSI_Optimized")
        self.assertEqual(backtest.symbol, "BTC/USDT")
        self.assertEqual(backtest.timeframe, "1h")
        self.assertEqual(backtest.start_date, start_date)
        self.assertEqual(backtest.end_date, end_date)
        self.assertEqual(backtest.total_days, 365)
        self.assertEqual(backtest.initial_capital, 10000.0)
        self.assertEqual(backtest.final_capital, 12500.0)
        self.assertEqual(backtest.total_return, 2500.0)
        self.assertEqual(backtest.total_return_percentage, 25.0)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "BacktestResult model not available")
    def test_backtest_trading_metrics(self):
        """Test métricas de trading del backtest."""
        backtest = BacktestResult(
            strategy_name="MACD_Backtest",
            symbol="ETH/USDT",
            timeframe="4h",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 6, 30),
            total_days=180,
            initial_capital=10000.0,
            final_capital=11800.0,
            total_trades=45,
            winning_trades=28,
            losing_trades=17,
            win_rate=62.22,
            avg_trade_duration_hours=24.5
        )
        
        # Verificar métricas de trading
        self.assertEqual(backtest.total_trades, 45)
        self.assertEqual(backtest.winning_trades, 28)
        self.assertEqual(backtest.losing_trades, 17)
        self.assertEqual(backtest.win_rate, 62.22)
        self.assertEqual(backtest.avg_trade_duration_hours, 24.5)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "BacktestResult model not available")
    def test_backtest_risk_metrics(self):
        """Test métricas de riesgo del backtest."""
        backtest = BacktestResult(
            strategy_name="Risk_Test",
            symbol="BTC/USDT",
            timeframe="1d",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 12, 31),
            total_days=365,
            initial_capital=10000.0,
            final_capital=11500.0,
            max_drawdown=-1200.0,
            max_drawdown_percentage=-12.0,
            sharpe_ratio=1.45,
            sortino_ratio=1.78,
            calmar_ratio=1.25
        )
        
        # Verificar métricas de riesgo
        self.assertEqual(backtest.max_drawdown, -1200.0)
        self.assertEqual(backtest.max_drawdown_percentage, -12.0)
        self.assertEqual(backtest.sharpe_ratio, 1.45)
        self.assertEqual(backtest.sortino_ratio, 1.78)
        self.assertEqual(backtest.calmar_ratio, 1.25)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "BacktestResult model not available")
    def test_backtest_persistence(self):
        """Test persistencia en base de datos."""
        backtest = BacktestResult(
            strategy_name="Persistence_Test",
            symbol="ADA/USDT",
            timeframe="2h",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 3, 31),
            total_days=90,
            initial_capital=5000.0,
            final_capital=5750.0,
            total_return=750.0,
            total_return_percentage=15.0,
            strategy_parameters='{"rsi_period": 14, "rsi_oversold": 30}'
        )
        
        # Guardar en base de datos
        self.session.add(backtest)
        self.session.commit()
        
        # Recuperar y verificar
        retrieved_backtest = self.session.query(BacktestResult).filter_by(
            strategy_name="Persistence_Test"
        ).first()
        self.assertIsNotNone(retrieved_backtest)
        self.assertEqual(retrieved_backtest.symbol, "ADA/USDT")
        self.assertEqual(retrieved_backtest.total_return_percentage, 15.0)


class TestTradingSignalModel(unittest.TestCase):
    """Tests para el modelo TradingSignal."""
    
    def setUp(self):
        """Configuración inicial para tests."""
        if MODELS_AVAILABLE:
            self.engine = create_engine('sqlite:///:memory:')
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = Mock()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        if hasattr(self, 'session') and MODELS_AVAILABLE:
            self.session.close()
    
    @unittest.skipIf(not MODELS_AVAILABLE, "TradingSignal model not available")
    def test_trading_signal_creation(self):
        """Test creación básica de señal de trading."""
        signal = TradingSignal(
            symbol="BTC/USDT",
            strategy_name="RSI_Signal",
            signal_type="BUY",
            timeframe="1h",
            price=50000.0,
            confidence_score=0.85,
            strength="Strong"
        )
        
        # Verificar atributos básicos
        self.assertEqual(signal.symbol, "BTC/USDT")
        self.assertEqual(signal.strategy_name, "RSI_Signal")
        self.assertEqual(signal.signal_type, "BUY")
        self.assertEqual(signal.timeframe, "1h")
        self.assertEqual(signal.price, 50000.0)
        self.assertEqual(signal.confidence_score, 0.85)
        self.assertEqual(signal.strength, "Strong")
        # Los valores por defecto se aplican al guardar en DB, no al crear el objeto
        self.assertIsNone(signal.action_taken)  # Se aplicará "NONE" por defecto en DB
    
    @unittest.skipIf(not MODELS_AVAILABLE, "TradingSignal model not available")
    def test_trading_signal_with_indicators(self):
        """Test señal con datos de indicadores."""
        indicators_data = '{"rsi": 25.5, "macd": 0.15, "bb_position": "lower"}'
        
        signal = TradingSignal(
            symbol="ETH/USDT",
            strategy_name="Multi_Indicator",
            signal_type="SELL",
            timeframe="4h",
            price=3200.0,
            confidence_score=0.92,
            strength="Very Strong",
            indicators_data=indicators_data,
            action_taken="EXECUTED",
            trade_id=123
        )
        
        # Verificar datos de indicadores y acción
        self.assertEqual(signal.indicators_data, indicators_data)
        self.assertEqual(signal.action_taken, "EXECUTED")
        self.assertEqual(signal.trade_id, 123)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "TradingSignal model not available")
    def test_trading_signal_with_expiration(self):
        """Test señal con fecha de expiración."""
        generated_at = datetime.now()
        expires_at = generated_at + timedelta(hours=2)
        
        signal = TradingSignal(
            symbol="ADA/USDT",
            strategy_name="Scalping_Strategy",
            signal_type="BUY",
            timeframe="15m",
            price=1.25,
            confidence_score=0.75,
            expires_at=expires_at
        )
        
        # Verificar expiración
        self.assertEqual(signal.expires_at, expires_at)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "TradingSignal model not available")
    def test_trading_signal_persistence(self):
        """Test persistencia en base de datos."""
        signal = TradingSignal(
            symbol="DOT/USDT",
            strategy_name="Momentum_Strategy",
            signal_type="HOLD",
            timeframe="1d",
            price=25.50,
            confidence_score=0.65,
            strength="Moderate"
        )
        
        # Guardar en base de datos
        self.session.add(signal)
        self.session.commit()
        
        # Recuperar y verificar
        retrieved_signal = self.session.query(TradingSignal).filter_by(
            symbol="DOT/USDT"
        ).first()
        self.assertIsNotNone(retrieved_signal)
        self.assertEqual(retrieved_signal.strategy_name, "Momentum_Strategy")
        self.assertEqual(retrieved_signal.signal_type, "HOLD")
        self.assertEqual(retrieved_signal.confidence_score, 0.65)
    
    @unittest.skipIf(not MODELS_AVAILABLE, "TradingSignal model not available")
    def test_trading_signal_repr(self):
        """Test representación string de la señal."""
        signal = TradingSignal(
            symbol="BTC/USDT",
            signal_type="BUY",
            confidence_score=0.88
        )
        
        repr_str = repr(signal)
        self.assertIn("TradingSignal", repr_str)
        self.assertIn("BTC/USDT", repr_str)
        self.assertIn("BUY", repr_str)
        self.assertIn("0.88", repr_str)


if __name__ == '__main__':
    unittest.main()
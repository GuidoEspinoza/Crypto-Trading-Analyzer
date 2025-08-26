"""📊 Enhanced Backtesting System
Sistema de backtesting avanzado con métricas profesionales
y análisis de rendimiento detallado.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path

# Importaciones con manejo de errores
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from trading_engine.enhanced_strategies import EnhancedTradingStrategy
    from trading_engine.signal_filters import FilteredSignal
    from data_fetcher import DataFetcher
except ImportError:
    # Fallback adicional
    try:
        from data_fetcher import DataFetcher
    except ImportError:
        # Si data_fetcher no existe, crear una clase mock
        class DataFetcher:
            def __init__(self):
                pass
            def get_historical_data(self, symbol, timeframe, limit):
                return pd.DataFrame()

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Registro de una operación"""
    entry_time: datetime
    exit_time: Optional[datetime] = None
    symbol: str = ""
    side: str = ""  # BUY/SELL
    entry_price: float = 0.0
    exit_price: float = 0.0
    quantity: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    pnl: float = 0.0
    pnl_percentage: float = 0.0
    commission: float = 0.0
    signal_quality: str = ""
    filter_score: float = 0.0
    confidence: float = 0.0
    market_regime: str = ""
    notes: List[str] = field(default_factory=list)
    
@dataclass
class BacktestResults:
    """Resultados completos del backtesting"""
    # Métricas básicas
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    # Rendimiento
    total_return: float = 0.0
    total_return_percentage: float = 0.0
    annualized_return: float = 0.0
    
    # Riesgo
    max_drawdown: float = 0.0
    max_drawdown_percentage: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    # Métricas avanzadas
    profit_factor: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    
    # Análisis temporal
    best_month: str = ""
    worst_month: str = ""
    monthly_returns: Dict[str, float] = field(default_factory=dict)
    
    # Filtros y calidad
    signals_generated: int = 0
    signals_filtered_out: int = 0
    filter_effectiveness: float = 0.0
    average_signal_quality: float = 0.0
    
    # Datos detallados
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    drawdown_curve: List[float] = field(default_factory=list)
    
class EnhancedBacktester:
    """🚀 Sistema de backtesting avanzado"""
    
    def __init__(self, initial_capital: float = 10000, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission  # 0.1% por defecto
        self.data_fetcher = DataFetcher()
        
    def run_backtest(
        self, 
        strategy: EnhancedTradingStrategy,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = "1h",
        use_filters: bool = True
    ) -> BacktestResults:
        """🎯 Ejecuta backtesting completo"""
        try:
            logger.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
            
            # Obtener datos históricos
            data = self._get_historical_data(symbol, start_date, end_date, timeframe)
            if data.empty:
                raise ValueError(f"No data available for {symbol}")
            
            # Inicializar variables
            capital = self.initial_capital
            position = None
            trades = []
            equity_curve = [capital]
            signals_generated = 0
            signals_filtered_out = 0
            
            # Simular trading
            for i in range(100, len(data)):  # Empezar después de 100 períodos para indicadores
                current_data = data.iloc[:i+1]
                current_price = current_data['close'].iloc[-1]
                current_time = current_data.index[-1]
                
                # Generar señal
                if use_filters and hasattr(strategy, 'analyze_with_filters'):
                    signal_result = strategy.analyze_with_filters(symbol, timeframe)
                    signal = signal_result.filtered_signal
                    signal_quality = signal_result.quality_grade
                    filter_score = signal_result.filter_score
                    
                    signals_generated += 1
                    if signal == "HOLD" and signal_result.original_signal.signal != "HOLD":
                        signals_filtered_out += 1
                else:
                    original_signal = strategy.analyze(symbol, timeframe)
                    signal = original_signal.signal
                    signal_quality = "B"
                    filter_score = 75.0
                    signals_generated += 1
                
                # Gestionar posiciones existentes
                if position:
                    exit_signal = self._check_exit_conditions(position, current_price, current_data)
                    if exit_signal:
                        trade = self._close_position(position, current_price, current_time, exit_signal)
                        trades.append(trade)
                        capital += trade.pnl
                        position = None
                
                # Abrir nueva posición
                if not position and signal in ["BUY", "SELL"]:
                    position = self._open_position(
                        signal, current_price, current_time, capital,
                        symbol, signal_quality, filter_score
                    )
                
                equity_curve.append(capital)
            
            # Cerrar posición final si existe
            if position:
                final_price = data['close'].iloc[-1]
                final_time = data.index[-1]
                trade = self._close_position(position, final_price, final_time, "END_OF_BACKTEST")
                trades.append(trade)
                capital += trade.pnl
            
            # Calcular métricas
            results = self._calculate_metrics(
                trades, equity_curve, self.initial_capital,
                signals_generated, signals_filtered_out, start_date, end_date
            )
            
            logger.info(f"Backtest completed: {len(trades)} trades, {results.win_rate:.1f}% win rate")
            return results
            
        except Exception as e:
            logger.error(f"Error in backtest: {str(e)}")
            return BacktestResults()
    
    def _get_historical_data(self, symbol: str, start_date: str, end_date: str, timeframe: str) -> pd.DataFrame:
        """Obtiene datos históricos"""
        try:
            # Convertir fechas
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Calcular número de períodos necesarios
            if timeframe == "1h":
                periods = int((end_dt - start_dt).total_seconds() / 3600)
            elif timeframe == "4h":
                periods = int((end_dt - start_dt).total_seconds() / (4 * 3600))
            elif timeframe == "1d":
                periods = (end_dt - start_dt).days
            else:
                periods = 1000
            
            # Obtener datos
            data = self.data_fetcher.get_historical_data(symbol, timeframe, periods)
            
            # Filtrar por fechas
            if not data.empty:
                data = data[(data.index >= start_dt) & (data.index <= end_dt)]
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return pd.DataFrame()
    
    def _open_position(self, signal: str, price: float, time: datetime, 
                      capital: float, symbol: str, quality: str, score: float) -> Dict:
        """Abre una nueva posición"""
        # Calcular tamaño de posición (risk management básico)
        risk_per_trade = 0.02  # 2% del capital por operación
        position_size = (capital * risk_per_trade) / price
        
        # Calcular stop loss y take profit (simplificado)
        if signal == "BUY":
            stop_loss = price * 0.98  # 2% stop loss
            take_profit = price * 1.06  # 6% take profit
        else:  # SELL
            stop_loss = price * 1.02
            take_profit = price * 0.94
        
        return {
            "entry_time": time,
            "symbol": symbol,
            "side": signal,
            "entry_price": price,
            "quantity": position_size,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "signal_quality": quality,
            "filter_score": score
        }
    
    def _check_exit_conditions(self, position: Dict, current_price: float, data: pd.DataFrame) -> Optional[str]:
        """Verifica condiciones de salida"""
        if position["side"] == "BUY":
            if current_price <= position["stop_loss"]:
                return "STOP_LOSS"
            elif current_price >= position["take_profit"]:
                return "TAKE_PROFIT"
        else:  # SELL
            if current_price >= position["stop_loss"]:
                return "STOP_LOSS"
            elif current_price <= position["take_profit"]:
                return "TAKE_PROFIT"
        
        # Verificar tiempo máximo en posición (opcional)
        time_in_position = data.index[-1] - position["entry_time"]
        if time_in_position > timedelta(days=7):  # Máximo 7 días
            return "TIME_LIMIT"
        
        return None
    
    def _close_position(self, position: Dict, exit_price: float, exit_time: datetime, reason: str) -> Trade:
        """Cierra una posición y calcula PnL"""
        quantity = position["quantity"]
        entry_price = position["entry_price"]
        
        # Calcular PnL
        if position["side"] == "BUY":
            pnl = (exit_price - entry_price) * quantity
        else:  # SELL
            pnl = (entry_price - exit_price) * quantity
        
        # Descontar comisiones
        commission = (entry_price + exit_price) * quantity * self.commission
        pnl -= commission
        
        pnl_percentage = (pnl / (entry_price * quantity)) * 100
        
        return Trade(
            entry_time=position["entry_time"],
            exit_time=exit_time,
            symbol=position["symbol"],
            side=position["side"],
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            stop_loss=position["stop_loss"],
            take_profit=position["take_profit"],
            pnl=pnl,
            pnl_percentage=pnl_percentage,
            commission=commission,
            signal_quality=position["signal_quality"],
            filter_score=position["filter_score"],
            notes=[reason]
        )
    
    def _calculate_metrics(self, trades: List[Trade], equity_curve: List[float], 
                          initial_capital: float, signals_generated: int, 
                          signals_filtered: int, start_date: str, end_date: str) -> BacktestResults:
        """Calcula todas las métricas de rendimiento"""
        if not trades:
            return BacktestResults()
        
        # Métricas básicas
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        # Rendimiento
        final_capital = equity_curve[-1]
        total_return = final_capital - initial_capital
        total_return_percentage = (total_return / initial_capital) * 100
        
        # Calcular rendimiento anualizado
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_dt - start_dt).days
        years = days / 365.25
        annualized_return = ((final_capital / initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # Drawdown
        peak = initial_capital
        max_drawdown = 0
        drawdown_curve = []
        
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            drawdown_curve.append(drawdown)
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        max_drawdown_percentage = (max_drawdown / peak) * 100 if peak > 0 else 0
        
        # Volatilidad y ratios
        returns = []
        for i in range(1, len(equity_curve)):
            daily_return = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(daily_return)
        
        volatility = np.std(returns) * np.sqrt(252) * 100 if returns else 0  # Anualizada
        
        # Sharpe Ratio (asumiendo risk-free rate = 2%)
        risk_free_rate = 0.02
        excess_return = annualized_return/100 - risk_free_rate
        sharpe_ratio = excess_return / (volatility/100) if volatility > 0 else 0
        
        # Sortino Ratio
        negative_returns = [r for r in returns if r < 0]
        downside_deviation = np.std(negative_returns) * np.sqrt(252) if negative_returns else 0
        sortino_ratio = excess_return / downside_deviation if downside_deviation > 0 else 0
        
        # Calmar Ratio
        calmar_ratio = (annualized_return/100) / (max_drawdown_percentage/100) if max_drawdown_percentage > 0 else 0
        
        # Métricas de trading
        wins = [t.pnl for t in trades if t.pnl > 0]
        losses = [t.pnl for t in trades if t.pnl < 0]
        
        average_win = np.mean(wins) if wins else 0
        average_loss = np.mean(losses) if losses else 0
        largest_win = max(wins) if wins else 0
        largest_loss = min(losses) if losses else 0
        
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Rachas consecutivas
        consecutive_wins = 0
        consecutive_losses = 0
        current_win_streak = 0
        current_loss_streak = 0
        
        for trade in trades:
            if trade.pnl > 0:
                current_win_streak += 1
                current_loss_streak = 0
                consecutive_wins = max(consecutive_wins, current_win_streak)
            else:
                current_loss_streak += 1
                current_win_streak = 0
                consecutive_losses = max(consecutive_losses, current_loss_streak)
        
        # Efectividad de filtros
        filter_effectiveness = (signals_filtered / signals_generated) * 100 if signals_generated > 0 else 0
        average_signal_quality = np.mean([t.filter_score for t in trades]) if trades else 0
        
        return BacktestResults(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_return=total_return,
            total_return_percentage=total_return_percentage,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            max_drawdown_percentage=max_drawdown_percentage,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            profit_factor=profit_factor,
            average_win=average_win,
            average_loss=average_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            signals_generated=signals_generated,
            signals_filtered_out=signals_filtered,
            filter_effectiveness=filter_effectiveness,
            average_signal_quality=average_signal_quality,
            trades=trades,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve
        )
    
    def save_results(self, results: BacktestResults, filename: str):
        """Guarda los resultados en un archivo JSON"""
        try:
            # Convertir a diccionario serializable
            results_dict = {
                "summary": {
                    "total_trades": results.total_trades,
                    "win_rate": results.win_rate,
                    "total_return_percentage": results.total_return_percentage,
                    "annualized_return": results.annualized_return,
                    "max_drawdown_percentage": results.max_drawdown_percentage,
                    "sharpe_ratio": results.sharpe_ratio,
                    "profit_factor": results.profit_factor
                },
                "detailed_metrics": results.__dict__,
                "trades": [{
                    "entry_time": trade.entry_time.isoformat(),
                    "exit_time": trade.exit_time.isoformat() if trade.exit_time else None,
                    "symbol": trade.symbol,
                    "side": trade.side,
                    "pnl_percentage": trade.pnl_percentage,
                    "signal_quality": trade.signal_quality
                } for trade in results.trades]
            }
            
            with open(filename, 'w') as f:
                json.dump(results_dict, f, indent=2, default=str)
            
            logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
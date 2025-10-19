"""📊 PROFESSIONAL BACKTESTING SYSTEM
Sistema de backtesting de nivel institucional con métricas avanzadas
para evaluación rigurosa de estrategias de trading.

Incluye métricas como Sharpe, Sortino, Calmar, Maximum Drawdown,
Win Rate, Profit Factor y análisis de distribución de retornos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """📈 Representación de un trade individual"""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    side: str  # 'long' or 'short'
    quantity: float
    pnl: float
    pnl_pct: float
    duration_hours: float
    strategy: str
    symbol: str
    
    @property
    def is_winner(self) -> bool:
        return self.pnl > 0

class BacktestMetrics:
    """📊 Métricas de backtesting profesional"""
    
    def __init__(self, trades: List[Trade], initial_capital: float = 10000):
        self.trades = trades
        self.initial_capital = initial_capital
        self.returns = self._calculate_returns()
        
    def _calculate_returns(self) -> pd.Series:
        """Calcula serie de retornos"""
        if not self.trades:
            return pd.Series([])
        
        # Crear serie temporal de retornos
        dates = [trade.exit_time for trade in self.trades]
        returns = [trade.pnl_pct / 100 for trade in self.trades]
        
        return pd.Series(returns, index=dates).sort_index()
    
    def total_return(self) -> float:
        """Retorno total del período"""
        if not self.trades:
            return 0.0
        
        total_pnl = sum(trade.pnl for trade in self.trades)
        return (total_pnl / self.initial_capital) * 100
    
    def annualized_return(self) -> float:
        """Retorno anualizado"""
        if not self.trades or len(self.returns) == 0:
            return 0.0
        
        days = (self.returns.index[-1] - self.returns.index[0]).days
        if days == 0:
            return 0.0
        
        total_ret = self.total_return() / 100
        years = days / 365.25
        
        return ((1 + total_ret) ** (1/years) - 1) * 100
    
    def volatility(self) -> float:
        """Volatilidad anualizada"""
        if len(self.returns) < 2:
            return 0.0
        
        return self.returns.std() * np.sqrt(252) * 100
    
    def sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Ratio de Sharpe"""
        if self.volatility() == 0:
            return 0.0
        
        excess_return = self.annualized_return() - (risk_free_rate * 100)
        return excess_return / self.volatility()
    
    def sortino_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Ratio de Sortino (solo considera volatilidad negativa)"""
        if len(self.returns) < 2:
            return 0.0
        
        negative_returns = self.returns[self.returns < 0]
        if len(negative_returns) == 0:
            return float('inf')
        
        downside_deviation = negative_returns.std() * np.sqrt(252)
        if downside_deviation == 0:
            return 0.0
        
        excess_return = (self.annualized_return() - (risk_free_rate * 100)) / 100
        return excess_return / downside_deviation
    
    def maximum_drawdown(self) -> Tuple[float, int]:
        """Máximo drawdown y duración en días"""
        if not self.trades:
            return 0.0, 0
        
        # Calcular equity curve
        equity = [self.initial_capital]
        for trade in self.trades:
            equity.append(equity[-1] + trade.pnl)
        
        equity = np.array(equity)
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak * 100
        
        max_dd = abs(drawdown.min())
        
        # Calcular duración del máximo drawdown
        dd_start = np.argmax(drawdown == drawdown.min())
        dd_end = len(drawdown) - 1
        for i in range(dd_start, len(drawdown)):
            if drawdown[i] >= 0:
                dd_end = i
                break
        
        dd_duration = dd_end - dd_start
        
        return max_dd, dd_duration
    
    def calmar_ratio(self) -> float:
        """Ratio de Calmar (retorno anualizado / máximo drawdown)"""
        max_dd, _ = self.maximum_drawdown()
        if max_dd == 0:
            return float('inf')
        
        return self.annualized_return() / max_dd
    
    def win_rate(self) -> float:
        """Porcentaje de trades ganadores"""
        if not self.trades:
            return 0.0
        
        winners = sum(1 for trade in self.trades if trade.is_winner)
        return (winners / len(self.trades)) * 100
    
    def profit_factor(self) -> float:
        """Factor de beneficio (ganancias brutas / pérdidas brutas)"""
        if not self.trades:
            return 0.0
        
        gross_profit = sum(trade.pnl for trade in self.trades if trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in self.trades if trade.pnl < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
    
    def average_win(self) -> float:
        """Ganancia promedio por trade ganador"""
        winners = [trade.pnl for trade in self.trades if trade.is_winner]
        return np.mean(winners) if winners else 0.0
    
    def average_loss(self) -> float:
        """Pérdida promedio por trade perdedor"""
        losers = [trade.pnl for trade in self.trades if not trade.is_winner]
        return np.mean(losers) if losers else 0.0
    
    def expectancy(self) -> float:
        """Expectativa matemática por trade"""
        if not self.trades:
            return 0.0
        
        win_rate = self.win_rate() / 100
        avg_win = self.average_win()
        avg_loss = abs(self.average_loss())
        
        return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    def kelly_criterion(self) -> float:
        """Criterio de Kelly para sizing óptimo"""
        if not self.trades:
            return 0.0
        
        win_rate = self.win_rate() / 100
        avg_win = self.average_win()
        avg_loss = abs(self.average_loss())
        
        if avg_loss == 0:
            return 0.0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        return max(0, min(kelly, 0.25))  # Cap at 25%
    
    def var_95(self) -> float:
        """Value at Risk al 95%"""
        if len(self.returns) < 2:
            return 0.0
        
        return np.percentile(self.returns, 5) * 100
    
    def cvar_95(self) -> float:
        """Conditional Value at Risk al 95%"""
        if len(self.returns) < 2:
            return 0.0
        
        var_95 = self.var_95() / 100
        tail_returns = self.returns[self.returns <= var_95]
        
        return tail_returns.mean() * 100 if len(tail_returns) > 0 else 0.0

class ProfessionalBacktester:
    """🔬 Sistema de backtesting profesional"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]
        self.timestamps: List[datetime] = []
    
    def add_trade(self, trade: Trade):
        """Añade un trade al backtest"""
        self.trades.append(trade)
        new_equity = self.equity_curve[-1] + trade.pnl
        self.equity_curve.append(new_equity)
        self.timestamps.append(trade.exit_time)
    
    def get_metrics(self) -> BacktestMetrics:
        """Obtiene métricas del backtest"""
        return BacktestMetrics(self.trades, self.initial_capital)
    
    def generate_report(self) -> Dict:
        """Genera reporte completo de performance"""
        metrics = self.get_metrics()
        max_dd, dd_duration = metrics.maximum_drawdown()
        
        return {
            # Retornos
            "total_return_pct": round(metrics.total_return(), 2),
            "annualized_return_pct": round(metrics.annualized_return(), 2),
            "volatility_pct": round(metrics.volatility(), 2),
            
            # Ratios de riesgo-retorno
            "sharpe_ratio": round(metrics.sharpe_ratio(), 3),
            "sortino_ratio": round(metrics.sortino_ratio(), 3),
            "calmar_ratio": round(metrics.calmar_ratio(), 3),
            
            # Drawdown
            "max_drawdown_pct": round(max_dd, 2),
            "max_drawdown_duration_days": dd_duration,
            
            # Estadísticas de trading
            "total_trades": len(self.trades),
            "win_rate_pct": round(metrics.win_rate(), 2),
            "profit_factor": round(metrics.profit_factor(), 3),
            "expectancy": round(metrics.expectancy(), 2),
            
            # Análisis de trades
            "average_win": round(metrics.average_win(), 2),
            "average_loss": round(metrics.average_loss(), 2),
            "kelly_criterion": round(metrics.kelly_criterion(), 3),
            
            # Métricas de riesgo
            "var_95_pct": round(metrics.var_95(), 2),
            "cvar_95_pct": round(metrics.cvar_95(), 2),
            
            # Capital final
            "final_capital": round(self.equity_curve[-1], 2),
            "total_pnl": round(self.equity_curve[-1] - self.initial_capital, 2)
        }
    
    def plot_performance(self, save_path: Optional[str] = None):
        """Genera gráficos de performance"""
        if not self.trades:
            print("No hay trades para graficar")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Equity Curve
        ax1.plot(self.timestamps, self.equity_curve[1:], linewidth=2, color='blue')
        ax1.set_title('Equity Curve', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Capital ($)')
        ax1.grid(True, alpha=0.3)
        
        # 2. Drawdown
        equity = np.array(self.equity_curve)
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak * 100
        
        ax2.fill_between(range(len(drawdown)), drawdown, 0, 
                        color='red', alpha=0.3)
        ax2.plot(drawdown, color='red', linewidth=1)
        ax2.set_title('Drawdown (%)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Distribución de retornos
        returns = [trade.pnl_pct for trade in self.trades]
        ax3.hist(returns, bins=30, alpha=0.7, color='green', edgecolor='black')
        ax3.axvline(np.mean(returns), color='red', linestyle='--', 
                   label=f'Media: {np.mean(returns):.2f}%')
        ax3.set_title('Distribución de Retornos', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Retorno por Trade (%)')
        ax3.set_ylabel('Frecuencia')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Rolling Sharpe Ratio (ventana de 30 trades)
        if len(self.trades) >= 30:
            rolling_sharpe = []
            for i in range(30, len(self.trades) + 1):
                subset_trades = self.trades[i-30:i]
                subset_metrics = BacktestMetrics(subset_trades, self.initial_capital)
                rolling_sharpe.append(subset_metrics.sharpe_ratio())
            
            ax4.plot(range(30, len(self.trades) + 1), rolling_sharpe, 
                    linewidth=2, color='purple')
            ax4.axhline(y=1.0, color='red', linestyle='--', alpha=0.7, 
                       label='Sharpe = 1.0')
            ax4.set_title('Rolling Sharpe Ratio (30 trades)', 
                         fontsize=14, fontweight='bold')
            ax4.set_xlabel('Número de Trade')
            ax4.set_ylabel('Sharpe Ratio')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'Insuficientes trades\npara Rolling Sharpe', 
                    ha='center', va='center', transform=ax4.transAxes,
                    fontsize=12)
            ax4.set_title('Rolling Sharpe Ratio', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def compare_strategies(self, other_backtests: Dict[str, 'ProfessionalBacktester']) -> pd.DataFrame:
        """Compara múltiples estrategias"""
        comparison_data = []
        
        # Añadir esta estrategia
        self_metrics = self.get_metrics()
        comparison_data.append({
            'Strategy': 'Current',
            'Total Return (%)': self_metrics.total_return(),
            'Sharpe Ratio': self_metrics.sharpe_ratio(),
            'Max Drawdown (%)': self_metrics.maximum_drawdown()[0],
            'Win Rate (%)': self_metrics.win_rate(),
            'Profit Factor': self_metrics.profit_factor(),
            'Total Trades': len(self.trades)
        })
        
        # Añadir otras estrategias
        for name, backtester in other_backtests.items():
            metrics = backtester.get_metrics()
            comparison_data.append({
                'Strategy': name,
                'Total Return (%)': metrics.total_return(),
                'Sharpe Ratio': metrics.sharpe_ratio(),
                'Max Drawdown (%)': metrics.maximum_drawdown()[0],
                'Win Rate (%)': metrics.win_rate(),
                'Profit Factor': metrics.profit_factor(),
                'Total Trades': len(backtester.trades)
            })
        
        return pd.DataFrame(comparison_data).round(2)

# Ejemplo de uso
if __name__ == "__main__":
    # Crear backtester
    backtester = ProfessionalBacktester(initial_capital=10000)
    
    # Simular algunos trades
    trades_example = [
        Trade(
            entry_time=datetime.now() - timedelta(days=10),
            exit_time=datetime.now() - timedelta(days=9),
            entry_price=100.0,
            exit_price=105.0,
            side='long',
            quantity=1.0,
            pnl=50.0,
            pnl_pct=5.0,
            duration_hours=24.0,
            strategy='TrendFollowing',
            symbol='BTCUSD'
        )
    ]
    
    for trade in trades_example:
        backtester.add_trade(trade)
    
    # Generar reporte
    report = backtester.generate_report()
    print("📊 REPORTE DE PERFORMANCE:")
    for key, value in report.items():
        print(f"{key}: {value}")
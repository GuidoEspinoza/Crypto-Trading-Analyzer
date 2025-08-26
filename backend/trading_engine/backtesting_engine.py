"""📊 Backtesting Engine - Sistema Profesional de Backtesting
Sistema completo de backtesting para validar estrategias de trading
con métricas avanzadas y análisis de rendimiento.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from enum import Enum
import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Importar componentes del sistema
from .enhanced_strategies import EnhancedSignal, EnhancedTradingStrategy
from .enhanced_risk_manager import EnhancedRiskManager, EnhancedRiskAssessment
from .data_fetcher import DataFetcher

logger = logging.getLogger(__name__)

class TradeStatus(Enum):
    """Estados de un trade"""
    OPEN = "OPEN"
    CLOSED_PROFIT = "CLOSED_PROFIT"
    CLOSED_LOSS = "CLOSED_LOSS"
    CLOSED_STOP = "CLOSED_STOP"
    CLOSED_TARGET = "CLOSED_TARGET"

@dataclass
class BacktestTrade:
    """Información de un trade en backtesting"""
    trade_id: str
    symbol: str
    signal_type: str  # BUY/SELL
    entry_time: datetime
    entry_price: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    quantity: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    pnl: float = 0.0
    pnl_percentage: float = 0.0
    status: TradeStatus = TradeStatus.OPEN
    confidence_score: float = 0.0
    risk_reward_ratio: float = 0.0
    max_favorable_excursion: float = 0.0  # MFE
    max_adverse_excursion: float = 0.0    # MAE
    duration_hours: float = 0.0
    commission: float = 0.0
    slippage: float = 0.0
    market_regime: str = ""
    strategy_name: str = ""

@dataclass
class BacktestMetrics:
    """Métricas de rendimiento del backtesting"""
    # Métricas básicas
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    # Métricas de rentabilidad
    total_return: float = 0.0
    total_return_percentage: float = 0.0
    annualized_return: float = 0.0
    average_trade_return: float = 0.0
    average_winning_trade: float = 0.0
    average_losing_trade: float = 0.0
    
    # Métricas de riesgo
    max_drawdown: float = 0.0
    max_drawdown_percentage: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    # Métricas avanzadas
    profit_factor: float = 0.0
    recovery_factor: float = 0.0
    expectancy: float = 0.0
    largest_winning_trade: float = 0.0
    largest_losing_trade: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    
    # Métricas de tiempo
    average_trade_duration: float = 0.0
    total_time_in_market: float = 0.0
    
    # Costos
    total_commission: float = 0.0
    total_slippage: float = 0.0
    
    # Fechas
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_days: int = 0

@dataclass
class BacktestConfig:
    """Configuración del backtesting"""
    initial_capital: float = 10000.0
    commission_rate: float = 0.001  # 0.1%
    slippage_rate: float = 0.0005   # 0.05%
    max_positions: int = 5
    position_sizing_method: str = "FIXED_RISK"  # FIXED_RISK, FIXED_AMOUNT, KELLY
    risk_per_trade: float = 0.02    # 2%
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timeframe: str = "1h"
    symbols: List[str] = None
    benchmark_symbol: str = "BTCUSDT"
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT"]

class BacktestingEngine:
    """📊 Motor de Backtesting Profesional"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.data_fetcher = DataFetcher()
        self.risk_manager = EnhancedRiskManager()
        
        # Estado del backtesting
        self.current_capital = config.initial_capital
        self.peak_capital = config.initial_capital
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        
        # Trades y posiciones
        self.trades: List[BacktestTrade] = []
        self.open_positions: Dict[str, BacktestTrade] = {}
        self.equity_curve: List[Dict] = []
        
        # Datos de mercado
        self.market_data: Dict[str, pd.DataFrame] = {}
        
        # Resultados
        self.metrics: Optional[BacktestMetrics] = None
        self.results_summary: Dict = {}
        
    def run_backtest(self, strategy: EnhancedTradingStrategy, 
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> BacktestMetrics:
        """Ejecutar backtesting completo"""
        try:
            logger.info(f"🚀 Iniciando backtesting de {strategy.__class__.__name__}")
            
            # Configurar fechas
            if start_date:
                self.config.start_date = start_date
            if end_date:
                self.config.end_date = end_date
            
            # Cargar datos de mercado
            self._load_market_data()
            
            # Ejecutar simulación
            self._run_simulation(strategy)
            
            # Calcular métricas
            self.metrics = self._calculate_metrics()
            
            # Generar resumen
            self._generate_results_summary(strategy)
            
            logger.info(f"✅ Backtesting completado: {len(self.trades)} trades ejecutados")
            return self.metrics
            
        except Exception as e:
            logger.error(f"Error en backtesting: {e}")
            raise
    
    def _load_market_data(self):
        """Cargar datos históricos para todos los símbolos"""
        try:
            logger.info("📥 Cargando datos históricos...")
            
            for symbol in self.config.symbols:
                try:
                    # Obtener datos históricos
                    data = self.data_fetcher.get_historical_data(
                        symbol=symbol,
                        timeframe=self.config.timeframe,
                        start_date=self.config.start_date,
                        end_date=self.config.end_date
                    )
                    
                    if data is not None and not data.empty:
                        self.market_data[symbol] = data
                        logger.info(f"✅ Datos cargados para {symbol}: {len(data)} barras")
                    else:
                        logger.warning(f"⚠️ No se pudieron cargar datos para {symbol}")
                        
                except Exception as e:
                    logger.error(f"Error cargando datos para {symbol}: {e}")
                    
            if not self.market_data:
                raise ValueError("No se pudieron cargar datos para ningún símbolo")
                
        except Exception as e:
            logger.error(f"Error cargando datos de mercado: {e}")
            raise
    
    def _run_simulation(self, strategy: EnhancedTradingStrategy):
        """Ejecutar simulación de trading"""
        try:
            logger.info("🔄 Ejecutando simulación de trading...")
            
            # Obtener todas las fechas únicas y ordenarlas
            all_timestamps = set()
            for data in self.market_data.values():
                all_timestamps.update(data.index)
            
            timestamps = sorted(list(all_timestamps))
            
            # Simular trading bar por bar
            for i, timestamp in enumerate(timestamps):
                try:
                    # Actualizar posiciones abiertas
                    self._update_open_positions(timestamp)
                    
                    # Generar señales para cada símbolo
                    for symbol in self.config.symbols:
                        if symbol in self.market_data:
                            data = self.market_data[symbol]
                            
                            # Verificar que tenemos datos para este timestamp
                            if timestamp in data.index:
                                # Obtener datos hasta este punto
                                historical_data = data.loc[:timestamp]
                                
                                # Generar señal
                                signal = strategy.analyze(symbol, self.config.timeframe, historical_data)
                                
                                if signal and signal.signal_type in ["BUY", "SELL"]:
                                    # Procesar señal
                                    self._process_signal(signal, timestamp)
                    
                    # Actualizar equity curve
                    self._update_equity_curve(timestamp)
                    
                    # Log progreso cada 100 barras
                    if i % 100 == 0:
                        progress = (i / len(timestamps)) * 100
                        logger.info(f"Progreso: {progress:.1f}% - Capital: ${self.current_capital:.2f}")
                        
                except Exception as e:
                    logger.error(f"Error procesando timestamp {timestamp}: {e}")
                    continue
            
            # Cerrar posiciones abiertas al final
            self._close_all_positions(timestamps[-1] if timestamps else datetime.now())
            
        except Exception as e:
            logger.error(f"Error en simulación: {e}")
            raise
    
    def _process_signal(self, signal: EnhancedSignal, timestamp: datetime):
        """Procesar una señal de trading"""
        try:
            # Verificar si ya tenemos posición abierta para este símbolo
            if signal.symbol in self.open_positions:
                return  # Ya tenemos posición abierta
            
            # Verificar límite de posiciones
            if len(self.open_positions) >= self.config.max_positions:
                return  # Límite de posiciones alcanzado
            
            # Evaluar riesgo
            risk_assessment = self.risk_manager.assess_trade_risk(signal, self.current_capital)
            
            # Verificar si el riesgo es aceptable
            if risk_assessment.risk_level.value in ["VERY_HIGH", "EXTREME"]:
                return  # Riesgo demasiado alto
            
            # Calcular tamaño de posición
            position_size = self._calculate_position_size(signal, risk_assessment)
            
            if position_size <= 0:
                return  # Tamaño de posición inválido
            
            # Calcular costos
            commission = position_size * signal.price * self.config.commission_rate
            slippage = position_size * signal.price * self.config.slippage_rate
            
            # Verificar capital suficiente
            total_cost = position_size * signal.price + commission + slippage
            if total_cost > self.current_capital:
                return  # Capital insuficiente
            
            # Crear trade
            trade = BacktestTrade(
                trade_id=f"{signal.symbol}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                symbol=signal.symbol,
                signal_type=signal.signal_type,
                entry_time=timestamp,
                entry_price=signal.price,
                quantity=position_size,
                stop_loss=signal.stop_loss_price,
                take_profit=signal.take_profit_price,
                confidence_score=signal.confidence_score,
                risk_reward_ratio=signal.risk_reward_ratio,
                commission=commission,
                slippage=slippage,
                market_regime=signal.market_regime,
                strategy_name=signal.strategy_name
            )
            
            # Abrir posición
            self.open_positions[signal.symbol] = trade
            self.current_capital -= total_cost
            
            logger.debug(f"📈 Posición abierta: {signal.symbol} {signal.signal_type} @ {signal.price}")
            
        except Exception as e:
            logger.error(f"Error procesando señal: {e}")
    
    def _update_open_positions(self, timestamp: datetime):
        """Actualizar posiciones abiertas (verificar stops y targets)"""
        try:
            positions_to_close = []
            
            for symbol, trade in self.open_positions.items():
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    
                    if timestamp in data.index:
                        current_bar = data.loc[timestamp]
                        current_price = current_bar['close']
                        high_price = current_bar['high']
                        low_price = current_bar['low']
                        
                        # Actualizar MFE y MAE
                        if trade.signal_type == "BUY":
                            mfe = max(0, high_price - trade.entry_price)
                            mae = max(0, trade.entry_price - low_price)
                        else:  # SELL
                            mfe = max(0, trade.entry_price - low_price)
                            mae = max(0, high_price - trade.entry_price)
                        
                        trade.max_favorable_excursion = max(trade.max_favorable_excursion, mfe)
                        trade.max_adverse_excursion = max(trade.max_adverse_excursion, mae)
                        
                        # Verificar stop loss
                        if trade.stop_loss > 0:
                            if ((trade.signal_type == "BUY" and low_price <= trade.stop_loss) or
                                (trade.signal_type == "SELL" and high_price >= trade.stop_loss)):
                                positions_to_close.append((symbol, trade.stop_loss, TradeStatus.CLOSED_STOP))
                                continue
                        
                        # Verificar take profit
                        if trade.take_profit > 0:
                            if ((trade.signal_type == "BUY" and high_price >= trade.take_profit) or
                                (trade.signal_type == "SELL" and low_price <= trade.take_profit)):
                                positions_to_close.append((symbol, trade.take_profit, TradeStatus.CLOSED_TARGET))
                                continue
            
            # Cerrar posiciones
            for symbol, exit_price, status in positions_to_close:
                self._close_position(symbol, timestamp, exit_price, status)
                
        except Exception as e:
            logger.error(f"Error actualizando posiciones: {e}")
    
    def _close_position(self, symbol: str, timestamp: datetime, 
                       exit_price: float, status: TradeStatus):
        """Cerrar una posición"""
        try:
            if symbol not in self.open_positions:
                return
            
            trade = self.open_positions[symbol]
            
            # Actualizar información del trade
            trade.exit_time = timestamp
            trade.exit_price = exit_price
            trade.status = status
            
            # Calcular duración
            duration = timestamp - trade.entry_time
            trade.duration_hours = duration.total_seconds() / 3600
            
            # Calcular PnL
            if trade.signal_type == "BUY":
                trade.pnl = (exit_price - trade.entry_price) * trade.quantity
            else:  # SELL
                trade.pnl = (trade.entry_price - exit_price) * trade.quantity
            
            # Restar comisiones y slippage
            exit_commission = trade.quantity * exit_price * self.config.commission_rate
            exit_slippage = trade.quantity * exit_price * self.config.slippage_rate
            trade.pnl -= (trade.commission + exit_commission + trade.slippage + exit_slippage)
            
            # Calcular PnL porcentual
            initial_investment = trade.quantity * trade.entry_price
            trade.pnl_percentage = (trade.pnl / initial_investment) * 100 if initial_investment > 0 else 0
            
            # Actualizar capital
            proceeds = trade.quantity * exit_price - exit_commission - exit_slippage
            self.current_capital += proceeds
            
            # Actualizar status basado en PnL
            if status not in [TradeStatus.CLOSED_STOP, TradeStatus.CLOSED_TARGET]:
                trade.status = TradeStatus.CLOSED_PROFIT if trade.pnl > 0 else TradeStatus.CLOSED_LOSS
            
            # Mover a trades completados
            self.trades.append(trade)
            del self.open_positions[symbol]
            
            logger.debug(f"📉 Posición cerrada: {symbol} PnL: ${trade.pnl:.2f} ({trade.pnl_percentage:.2f}%)")
            
        except Exception as e:
            logger.error(f"Error cerrando posición {symbol}: {e}")
    
    def _close_all_positions(self, timestamp: datetime):
        """Cerrar todas las posiciones abiertas al final del backtesting"""
        try:
            symbols_to_close = list(self.open_positions.keys())
            
            for symbol in symbols_to_close:
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    # Usar el último precio disponible
                    last_price = data['close'].iloc[-1]
                    self._close_position(symbol, timestamp, last_price, TradeStatus.CLOSED_LOSS)
                    
        except Exception as e:
            logger.error(f"Error cerrando todas las posiciones: {e}")
    
    def _calculate_position_size(self, signal: EnhancedSignal, 
                               risk_assessment: EnhancedRiskAssessment) -> float:
        """Calcular tamaño de posición"""
        try:
            if self.config.position_sizing_method == "FIXED_RISK":
                # Riesgo fijo por trade
                risk_amount = self.current_capital * self.config.risk_per_trade
                
                if signal.stop_loss_price > 0:
                    stop_distance = abs(signal.price - signal.stop_loss_price)
                    if stop_distance > 0:
                        return risk_amount / stop_distance
                
                # Si no hay stop loss, usar 2% del precio como riesgo
                return risk_amount / (signal.price * 0.02)
                
            elif self.config.position_sizing_method == "FIXED_AMOUNT":
                # Cantidad fija
                return self.current_capital * 0.1 / signal.price  # 10% del capital
                
            elif self.config.position_sizing_method == "KELLY":
                # Usar el tamaño recomendado por el risk manager
                return risk_assessment.position_sizing.recommended_size / signal.price
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculando tamaño de posición: {e}")
            return 0.0
    
    def _update_equity_curve(self, timestamp: datetime):
        """Actualizar curva de equity"""
        try:
            # Calcular valor total (capital + posiciones abiertas)
            total_value = self.current_capital
            
            for symbol, trade in self.open_positions.items():
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    if timestamp in data.index:
                        current_price = data.loc[timestamp, 'close']
                        
                        # Valor de la posición
                        if trade.signal_type == "BUY":
                            position_value = trade.quantity * current_price
                        else:
                            position_value = trade.quantity * (2 * trade.entry_price - current_price)
                        
                        total_value += position_value - (trade.quantity * trade.entry_price)
            
            # Actualizar peak y drawdown
            if total_value > self.peak_capital:
                self.peak_capital = total_value
                self.current_drawdown = 0.0
            else:
                self.current_drawdown = (self.peak_capital - total_value) / self.peak_capital
                self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
            
            # Agregar punto a la curva
            self.equity_curve.append({
                'timestamp': timestamp,
                'equity': total_value,
                'drawdown': self.current_drawdown,
                'open_positions': len(self.open_positions)
            })
            
        except Exception as e:
            logger.error(f"Error actualizando equity curve: {e}")
    
    def _calculate_metrics(self) -> BacktestMetrics:
        """Calcular métricas de rendimiento"""
        try:
            if not self.trades:
                return BacktestMetrics()
            
            # Métricas básicas
            total_trades = len(self.trades)
            winning_trades = len([t for t in self.trades if t.pnl > 0])
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # PnL
            total_pnl = sum(t.pnl for t in self.trades)
            total_return_pct = (total_pnl / self.config.initial_capital) * 100
            
            # Trades ganadores y perdedores
            winning_pnls = [t.pnl for t in self.trades if t.pnl > 0]
            losing_pnls = [t.pnl for t in self.trades if t.pnl < 0]
            
            avg_winning_trade = np.mean(winning_pnls) if winning_pnls else 0
            avg_losing_trade = np.mean(losing_pnls) if losing_pnls else 0
            avg_trade_return = total_pnl / total_trades if total_trades > 0 else 0
            
            # Profit factor
            gross_profit = sum(winning_pnls) if winning_pnls else 0
            gross_loss = abs(sum(losing_pnls)) if losing_pnls else 1
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            # Expectancy
            expectancy = (win_rate/100 * avg_winning_trade) + ((1-win_rate/100) * avg_losing_trade)
            
            # Métricas de tiempo
            durations = [t.duration_hours for t in self.trades if t.duration_hours > 0]
            avg_duration = np.mean(durations) if durations else 0
            
            # Fechas
            start_date = min(t.entry_time for t in self.trades) if self.trades else None
            end_date = max(t.exit_time for t in self.trades if t.exit_time) if self.trades else None
            total_days = (end_date - start_date).days if start_date and end_date else 0
            
            # Retorno anualizado
            if total_days > 0:
                annualized_return = ((1 + total_return_pct/100) ** (365/total_days) - 1) * 100
            else:
                annualized_return = 0
            
            # Ratios de riesgo (simplificados)
            if self.equity_curve:
                returns = []
                for i in range(1, len(self.equity_curve)):
                    prev_equity = self.equity_curve[i-1]['equity']
                    curr_equity = self.equity_curve[i]['equity']
                    if prev_equity > 0:
                        returns.append((curr_equity - prev_equity) / prev_equity)
                
                if returns:
                    volatility = np.std(returns) * np.sqrt(252) * 100  # Anualizada
                    avg_return = np.mean(returns)
                    
                    # Sharpe ratio (asumiendo risk-free rate = 0)
                    sharpe_ratio = (avg_return * 252) / (np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
                    
                    # Sortino ratio
                    negative_returns = [r for r in returns if r < 0]
                    downside_deviation = np.std(negative_returns) if negative_returns else 0.001
                    sortino_ratio = (avg_return * 252) / (downside_deviation * np.sqrt(252)) if downside_deviation > 0 else 0
                else:
                    volatility = 0
                    sharpe_ratio = 0
                    sortino_ratio = 0
            else:
                volatility = 0
                sharpe_ratio = 0
                sortino_ratio = 0
            
            # Calmar ratio
            calmar_ratio = annualized_return / (self.max_drawdown * 100) if self.max_drawdown > 0 else 0
            
            # Costos
            total_commission = sum(t.commission for t in self.trades)
            total_slippage = sum(t.slippage for t in self.trades)
            
            # Rachas
            consecutive_wins = 0
            consecutive_losses = 0
            current_win_streak = 0
            current_loss_streak = 0
            
            for trade in self.trades:
                if trade.pnl > 0:
                    current_win_streak += 1
                    current_loss_streak = 0
                    consecutive_wins = max(consecutive_wins, current_win_streak)
                else:
                    current_loss_streak += 1
                    current_win_streak = 0
                    consecutive_losses = max(consecutive_losses, current_loss_streak)
            
            return BacktestMetrics(
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=round(win_rate, 2),
                total_return=round(total_pnl, 2),
                total_return_percentage=round(total_return_pct, 2),
                annualized_return=round(annualized_return, 2),
                average_trade_return=round(avg_trade_return, 2),
                average_winning_trade=round(avg_winning_trade, 2),
                average_losing_trade=round(avg_losing_trade, 2),
                max_drawdown=round(self.max_drawdown, 4),
                max_drawdown_percentage=round(self.max_drawdown * 100, 2),
                volatility=round(volatility, 2),
                sharpe_ratio=round(sharpe_ratio, 2),
                sortino_ratio=round(sortino_ratio, 2),
                calmar_ratio=round(calmar_ratio, 2),
                profit_factor=round(profit_factor, 2),
                expectancy=round(expectancy, 2),
                largest_winning_trade=max(winning_pnls) if winning_pnls else 0,
                largest_losing_trade=min(losing_pnls) if losing_pnls else 0,
                consecutive_wins=consecutive_wins,
                consecutive_losses=consecutive_losses,
                average_trade_duration=round(avg_duration, 2),
                total_commission=round(total_commission, 2),
                total_slippage=round(total_slippage, 2),
                start_date=start_date,
                end_date=end_date,
                total_days=total_days
            )
            
        except Exception as e:
            logger.error(f"Error calculando métricas: {e}")
            return BacktestMetrics()
    
    def _generate_results_summary(self, strategy: EnhancedTradingStrategy):
        """Generar resumen de resultados"""
        try:
            self.results_summary = {
                'strategy_name': strategy.__class__.__name__,
                'config': asdict(self.config),
                'metrics': asdict(self.metrics) if self.metrics else {},
                'total_trades': len(self.trades),
                'equity_curve_points': len(self.equity_curve),
                'final_capital': self.current_capital,
                'max_drawdown_reached': self.max_drawdown,
                'backtest_completed': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
    
    def save_results(self, output_dir: str = "backtest_results"):
        """Guardar resultados del backtesting"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Guardar métricas
            metrics_file = output_path / f"metrics_{timestamp}.json"
            with open(metrics_file, 'w') as f:
                json.dump(self.results_summary, f, indent=2, default=str)
            
            # Guardar trades
            trades_file = output_path / f"trades_{timestamp}.json"
            trades_data = [asdict(trade) for trade in self.trades]
            with open(trades_file, 'w') as f:
                json.dump(trades_data, f, indent=2, default=str)
            
            # Guardar equity curve
            equity_file = output_path / f"equity_curve_{timestamp}.json"
            with open(equity_file, 'w') as f:
                json.dump(self.equity_curve, f, indent=2, default=str)
            
            logger.info(f"📁 Resultados guardados en {output_path}")
            
        except Exception as e:
            logger.error(f"Error guardando resultados: {e}")
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        if not self.metrics:
            print("❌ No hay métricas disponibles")
            return
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE BACKTESTING")
        print("="*60)
        
        print(f"\n📈 RENDIMIENTO:")
        print(f"  • Retorno Total: ${self.metrics.total_return:.2f} ({self.metrics.total_return_percentage:.2f}%)")
        print(f"  • Retorno Anualizado: {self.metrics.annualized_return:.2f}%")
        print(f"  • Capital Final: ${self.current_capital:.2f}")
        
        print(f"\n📊 TRADES:")
        print(f"  • Total de Trades: {self.metrics.total_trades}")
        print(f"  • Trades Ganadores: {self.metrics.winning_trades} ({self.metrics.win_rate:.1f}%)")
        print(f"  • Trades Perdedores: {self.metrics.losing_trades}")
        print(f"  • Promedio por Trade: ${self.metrics.average_trade_return:.2f}")
        
        print(f"\n⚠️ RIESGO:")
        print(f"  • Máximo Drawdown: {self.metrics.max_drawdown_percentage:.2f}%")
        print(f"  • Volatilidad: {self.metrics.volatility:.2f}%")
        print(f"  • Sharpe Ratio: {self.metrics.sharpe_ratio:.2f}")
        print(f"  • Sortino Ratio: {self.metrics.sortino_ratio:.2f}")
        
        print(f"\n💰 ANÁLISIS:")
        print(f"  • Profit Factor: {self.metrics.profit_factor:.2f}")
        print(f"  • Expectancy: ${self.metrics.expectancy:.2f}")
        print(f"  • Mayor Ganancia: ${self.metrics.largest_winning_trade:.2f}")
        print(f"  • Mayor Pérdida: ${self.metrics.largest_losing_trade:.2f}")
        
        print(f"\n⏱️ TIEMPO:")
        print(f"  • Duración Promedio: {self.metrics.average_trade_duration:.1f} horas")
        print(f"  • Período: {self.metrics.start_date.strftime('%Y-%m-%d') if self.metrics.start_date else 'N/A'} a {self.metrics.end_date.strftime('%Y-%m-%d') if self.metrics.end_date else 'N/A'}")
        
        print(f"\n💸 COSTOS:")
        print(f"  • Comisiones: ${self.metrics.total_commission:.2f}")
        print(f"  • Slippage: ${self.metrics.total_slippage:.2f}")
        
        print("\n" + "="*60)
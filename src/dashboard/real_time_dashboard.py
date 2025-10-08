#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Real-Time Dashboard - Dashboard de Monitoreo en Tiempo Real

Este módulo implementa un dashboard interactivo para monitorear:
- Performance en tiempo real
- Métricas de trading
- Análisis de riesgo
- Visualizaciones dinámicas
- Alertas y notificaciones
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from dataclasses import dataclass
import warnings
from collections import deque
import sys
import os
import requests

# Agregar el directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.database.database import db_manager
from src.database.models import Trade, Portfolio, TradingSignal
from src.core.paper_trader import PaperTrader
from src.config.main_config import TradingBotConfig, PaperTraderConfig, RiskManagerConfig, StrategyConfig, TradingProfiles, TRADING_PROFILE

# Configuración del modo de trading (centralizada)
INITIAL_BALANCE = PaperTraderConfig.INITIAL_BALANCE
USE_PAPER_TRADING = True

warnings.filterwarnings('ignore')

@dataclass
class DashboardConfig:
    """Configuración del dashboard"""
    # Actualización
    REFRESH_INTERVAL: int = 5  # segundos
    MAX_DATA_POINTS: int = 1000
    
    # Colores del tema
    COLORS: Dict[str, str] = None
    
    def __post_init__(self):
        if self.COLORS is None:
            self.COLORS = {
                'primary': '#1f77b4',
                'success': '#2ca02c',
                'danger': '#d62728',
                'warning': '#ff7f0e',
                'info': '#17a2b8',
                'background': '#0e1117',
                'surface': '#262730',
                'text': '#fafafa'
            }

class MetricsCalculator:
    """
    📊 Calculadora de métricas en tiempo real
    """
    
    def __init__(self, max_history: int = 1000):
        self.equity_history = deque(maxlen=max_history)
        self.trade_history = deque(maxlen=max_history)
        self.signal_history = deque(maxlen=max_history)
        # Cache de PaperTrader para evitar múltiples inicializaciones
        self._paper_trader_cache = None
    
    def _get_paper_trader(self) -> PaperTrader:
        """Obtener instancia cached de PaperTrader para evitar múltiples inicializaciones"""
        if self._paper_trader_cache is None:
            self._paper_trader_cache = PaperTrader()
        return self._paper_trader_cache
    
    def _get_trade_filter(self) -> bool:
        """Determinar qué tipo de trades mostrar según la configuración"""
        if not USE_PAPER_TRADING:
            # En modo real testnet, mostrar trades reales (is_paper_trade = False)
            return False
        else:
            # En modo paper trading, mostrar trades simulados (is_paper_trade = True)
            return True
        
    def update_equity(self, timestamp: datetime, equity: float):
        """Actualizar historial de equity"""
        self.equity_history.append({
            'timestamp': timestamp,
            'equity': equity
        })
    
    def update_trade(self, trade_data: Dict):
        """Actualizar historial de trades"""
        self.trade_history.append(trade_data)
    
    def update_signal(self, signal_data: Dict):
        """Actualizar historial de señales"""
        self.signal_history.append(signal_data)
    
    def _build_synthetic_equity_history(self):
        """Construir historial de equity sintético basado en trades de la base de datos"""
        try:
            with db_manager.get_db_session() as session:
                is_paper_trade = self._get_trade_filter()
                
                # Obtener todos los trades cerrados ordenados por fecha
                closed_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper_trade,
                    Trade.status == 'CLOSED',
                    Trade.exit_time.isnot(None)
                ).order_by(Trade.exit_time).all()
                
                if not closed_trades:
                    return
                
                # Construir historial de equity acumulativo
                # Usar balance inicial desde resumen de portfolio si está disponible
                portfolio_summary = db_manager.get_portfolio_summary(is_paper=USE_PAPER_TRADING)
                starting_equity = portfolio_summary.get('initial_balance', 0.0)
                running_equity = starting_equity
                self.equity_history.clear()
                
                # Punto inicial
                self.equity_history.append({
                    'timestamp': closed_trades[0].entry_time or datetime.now(),
                    'equity': running_equity
                })
                
                # Agregar punto por cada trade cerrado
                for trade in closed_trades:
                    if trade.pnl:
                        running_equity += trade.pnl
                        self.equity_history.append({
                            'timestamp': trade.exit_time,
                            'equity': running_equity
                        })
                
                # Agregar punto actual con PnL no realizado
                current_unrealized = 0.0
                active_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper_trade,
                    Trade.status == 'OPEN'
                ).all()
                
                for trade in active_trades:
                    if trade.symbol and trade.entry_price and trade.quantity:
                        current_price = self._get_current_price_simple(trade.symbol, trade.entry_price)
                        unrealized_pnl = self._calculate_unrealized_pnl(
                            trade.trade_type, 
                            trade.entry_price, 
                            current_price, 
                            trade.quantity
                        )
                        current_unrealized += unrealized_pnl
                
                # Punto actual
                self.equity_history.append({
                    'timestamp': datetime.now(),
                    'equity': running_equity + current_unrealized
                })
                
        except Exception as e:
            print(f"Error construyendo historial sintético: {e}")
    
    def get_current_metrics(self) -> Dict:
        """Obtener métricas actuales desde la base de datos"""
        try:
            # Cargar datos reales considerando el modo de trading configurado
            portfolio_summary = self.get_portfolio_summary()
            
            with db_manager.get_db_session() as session:
                # Determinar qué tipo de trades mostrar
                is_paper_trade = self._get_trade_filter()
                
                # Obtener todos los trades
                all_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper_trade
                ).all()
                
                # Obtener trades activos
                active_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper_trade,
                    Trade.status == 'OPEN'
                ).all()
                
                # Obtener trades cerrados
                closed_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper_trade,
                    Trade.status == 'CLOSED'
                ).all()
                
                # Calcular métricas
                total_trades = len(all_trades)
                successful_trades = len([t for t in closed_trades if t.pnl and t.pnl > 0])
                win_rate = (successful_trades / max(1, len(closed_trades))) * 100
                
                # Trades de hoy
                today = datetime.now().date()
                trades_today = len([t for t in all_trades if t.entry_time and t.entry_time.date() == today])
                
                # PnL total
                total_pnl = sum([t.pnl for t in closed_trades if t.pnl]) or 0.0
                
                # Equity actual
                current_equity = portfolio_summary.get('total_value', 0.0)
                
                # Determinar balance inicial correcto (solo paper trading)
                # Usar el balance inicial desde DB (portfolio_summary)
                initial_equity = portfolio_summary.get('initial_balance', 0.0)
                
                # Retorno total
                if initial_equity > 0:
                    total_return = ((current_equity - initial_equity) / initial_equity) * 100
                else:
                    total_return = 0.0
                
                # Calcular drawdown correctamente basado en el historial de equity
                current_drawdown = 0.0
                max_drawdown = 0.0
                
                if len(self.equity_history) > 0:
                    # Obtener valores de equity del historial
                    equity_values = [point['equity'] for point in self.equity_history]
                    equity_values.append(current_equity)  # Incluir valor actual
                    
                    # Encontrar el pico máximo histórico real
                    historical_peak = max(equity_values)
                    
                    # Drawdown actual: diferencia porcentual desde el pico máximo histórico
                    if historical_peak > 0:
                        current_drawdown = ((current_equity - historical_peak) / historical_peak) * 100
                        current_drawdown = min(0, current_drawdown)  # Drawdown siempre ≤ 0
                    
                    # Max drawdown histórico: el peor drawdown registrado en toda la historia
                    max_drawdown_value = 0.0
                    running_peak = equity_values[0] if equity_values else initial_equity
                    
                    for equity in equity_values:
                        # Actualizar el pico corriente
                        if equity > running_peak:
                            running_peak = equity
                        
                        # Calcular drawdown en este punto
                        if running_peak > 0:
                            drawdown = ((equity - running_peak) / running_peak) * 100
                            # Mantener el peor drawdown (más negativo)
                            if drawdown < max_drawdown_value:
                                max_drawdown_value = drawdown
                    
                    max_drawdown = max_drawdown_value
                else:
                    # Si no hay historial, usar el retorno total como referencia
                    if total_return < 0:
                        current_drawdown = total_return
                        max_drawdown = total_return
                
                # Construir historial sintético si está vacío
                if len(self.equity_history) == 0:
                    self._build_synthetic_equity_history()
                
                # Actualizar equity actual en tiempo real si hay cambios significativos
                if len(self.equity_history) > 0:
                    last_equity = self.equity_history[-1]['equity']
                    equity_change = abs(current_equity - last_equity) / last_equity if last_equity > 0 else 0
                    
                    # Si hay un cambio significativo (>0.1%) o han pasado más de 30 segundos, actualizar
                    now = datetime.now()
                    last_update = self.equity_history[-1]['timestamp']
                    time_diff = (now - last_update).total_seconds()
                    
                    if equity_change > 0.001 or time_diff > 30:  # 0.1% de cambio o 30 segundos
                        self.equity_history.append({
                            'timestamp': now,
                            'equity': current_equity
                        })
                        
                        # Mantener solo los últimos 1000 puntos para performance
                        if len(self.equity_history) > 1000:
                            self.equity_history = self.equity_history[-1000:]
                
                # Volatilidad: calcular basada en variación de equity histórica
                volatility = 0.0
                if len(self.equity_history) > 1:
                    equity_values = [point['equity'] for point in self.equity_history]
                    if len(equity_values) > 1:
                        returns = []
                        for i in range(1, len(equity_values)):
                            if equity_values[i-1] > 0:
                                returns.append((equity_values[i] - equity_values[i-1]) / equity_values[i-1])
                        
                        if len(returns) > 1:
                            volatility = np.std(returns) * np.sqrt(252) * 100  # Volatilidad anualizada en %
                
                # Calcular Sharpe Ratio mejorado
                if volatility > 0 and len(self.equity_history) > 1:
                    # Usar retorno anualizado y volatilidad anualizada
                    risk_free_rate = 2.0  # Tasa libre de riesgo asumida del 2%
                    
                    # Si la volatilidad es muy alta (>100%), usar un enfoque más conservador
                    if volatility > 100:
                        # Calcular Sharpe basado en trades individuales como alternativa
                        try:
                            trade_returns = []
                            for trade in closed_trades:
                                if trade.pnl and trade.entry_price and trade.quantity:
                                    if trade.entry_price > 0 and trade.quantity > 0:
                                        trade_return = (trade.pnl / (trade.entry_price * trade.quantity)) * 100
                                        trade_returns.append(trade_return)
                            
                            if len(trade_returns) >= 2:
                                avg_trade_return = sum(trade_returns) / len(trade_returns)
                                std_trade_return = (sum((x - avg_trade_return) ** 2 for x in trade_returns) / len(trade_returns)) ** 0.5
                                daily_risk_free = risk_free_rate / 252
                                sharpe_ratio = (avg_trade_return - daily_risk_free) / std_trade_return if std_trade_return > 0 else 0
                            else:
                                sharpe_ratio = (total_return - risk_free_rate) / volatility
                        except:
                            sharpe_ratio = (total_return - risk_free_rate) / volatility
                    else:
                        sharpe_ratio = (total_return - risk_free_rate) / volatility
                else:
                    sharpe_ratio = 0.0
                
                # Calcular Profit Factor
                winning_trades_pnl = sum([t.pnl for t in closed_trades if t.pnl and t.pnl > 0]) or 0.0
                losing_trades_pnl = abs(sum([t.pnl for t in closed_trades if t.pnl and t.pnl < 0])) or 0.0
                profit_factor = winning_trades_pnl / max(0.01, losing_trades_pnl) if losing_trades_pnl > 0 else winning_trades_pnl
                
                # Calcular Total de Comisiones Pagadas
                total_fees_paid = self._calculate_total_fees(all_trades)
                
                # Calcular PnL No Realizado (suma de todos los unrealized_pnl de trades activos)
                unrealized_pnl_total = 0.0
                for trade in active_trades:
                    if trade.symbol and trade.entry_price and trade.quantity:
                        current_price = self._get_current_price_simple(trade.symbol, trade.entry_price)
                        unrealized_pnl = self._calculate_unrealized_pnl(
                            trade.trade_type, 
                            trade.entry_price, 
                            current_price, 
                            trade.quantity
                        )
                        unrealized_pnl_total += unrealized_pnl
                
                # Calcular PnL Realizado (suma de PnL de trades cerrados)
                closed_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper_trade,
                    Trade.status == 'CLOSED'
                ).all()
                
                realized_pnl_total = sum(trade.pnl for trade in closed_trades if trade.pnl) if closed_trades else 0.0
                
                # Señales recientes (últimas 10)
                recent_signals = []
                for trade in all_trades[-10:]:
                    recent_signals.append({
                        'timestamp': trade.entry_time or datetime.now(),
                        'signal': trade.trade_type,
                        'confidence': 0.8,  # Valor por defecto
                        'price': trade.entry_price or 0,
                        'interpretation': f"{trade.strategy_name} - {trade.symbol}"
                    })
                
                # Obtener balance real de USDT usando PaperTrader (cached)
                try:
                    paper_trader = self._get_paper_trader()
                    real_usdt_balance = paper_trader.get_balance('USDT')
                except Exception as e:
                    # Fallback al valor del portfolio summary si hay error
                    real_usdt_balance = portfolio_summary.get('available_balance', 0.0)
                
                return {
                    'total_return_pct': total_return,
                    'current_equity': current_equity,
                    'available_balance': real_usdt_balance,
                    'current_drawdown_pct': current_drawdown,
                    'max_drawdown_pct': max_drawdown,
                    'volatility_pct': volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'profit_factor': profit_factor,
                    'total_fees_paid': total_fees_paid,
                    'unrealized_pnl_total': unrealized_pnl_total,
                    'realized_pnl': realized_pnl_total,
                    'total_trades': total_trades,
                    'trades_today': trades_today,
                    'win_rate_pct': win_rate,
                    'initial_balance': initial_equity,
                    'recent_signals': recent_signals
                }
                
        except Exception as e:
            print(f"Error cargando métricas desde DB: {e}")
            return self._empty_metrics()
    
    def get_test_metrics(self) -> Dict:
        """Obtener métricas de prueba basadas solo en el historial de equity (sin DB)"""
        try:
            if len(self.equity_history) == 0:
                return {
                    'total_return_pct': 0.0,
                    'current_equity': 0.0,
                    'current_drawdown_pct': 0.0,
                    'max_drawdown_pct': 0.0,
                    'volatility_pct': 0.0,
                    'sharpe_ratio': 0.0,
                    'profit_factor': 1.0,
                    'unrealized_pnl_total': 0.0,
                    'total_trades': 0,
                    'trades_today': 0,
                    'win_rate_pct': 0.0,
                    'recent_signals': [],
                    'initial_balance': 0.0
                }
            
            # Usar datos del historial de equity
            initial_equity = self.equity_history[0]['equity']
            current_equity = self.equity_history[-1]['equity']
            
            # Retorno total
            if initial_equity > 0:
                total_return = ((current_equity - initial_equity) / initial_equity) * 100
            else:
                total_return = 0.0
            
            # Calcular drawdown correctamente basado en el historial de equity
            current_drawdown = 0.0
            max_drawdown = 0.0
            
            if len(self.equity_history) > 0:
                # Obtener valores de equity del historial
                equity_values = [point['equity'] for point in self.equity_history]
                
                # Calcular el pico histórico (running maximum)
                running_max = equity_values[0]
                for equity in equity_values:
                    if equity > running_max:
                        running_max = equity
                
                # Drawdown actual: diferencia porcentual desde el pico
                if running_max > 0:
                    current_drawdown = ((current_equity - running_max) / running_max) * 100
                    current_drawdown = min(0, current_drawdown)  # Drawdown siempre ≤ 0
                
                # Max drawdown histórico: el peor drawdown registrado
                max_drawdown_value = 0.0
                running_peak = equity_values[0]
                
                for equity in equity_values:
                    if equity > running_peak:
                        running_peak = equity
                    
                    if running_peak > 0:
                        drawdown = ((equity - running_peak) / running_peak) * 100
                        if drawdown < max_drawdown_value:
                            max_drawdown_value = drawdown
                
                max_drawdown = max_drawdown_value
            
            # Volatilidad: calcular basada en variación de equity histórica
            volatility = 0.0
            if len(self.equity_history) > 1:
                equity_values = [point['equity'] for point in self.equity_history]
                if len(equity_values) > 1:
                    returns = []
                    for i in range(1, len(equity_values)):
                        if equity_values[i-1] > 0:
                            returns.append((equity_values[i] - equity_values[i-1]) / equity_values[i-1])
                    
                    if len(returns) > 1:
                        volatility = np.std(returns) * np.sqrt(252) * 100  # Volatilidad anualizada en %
            
            # Calcular Sharpe Ratio
            if volatility > 0 and len(self.equity_history) > 1:
                # Usar retorno anualizado y volatilidad anualizada
                risk_free_rate = 2.0  # Tasa libre de riesgo asumida del 2%
                sharpe_ratio = (total_return - risk_free_rate) / volatility if volatility > 0 else 0
            else:
                sharpe_ratio = 0.0
            
            return {
                'total_return_pct': total_return,
                'current_equity': current_equity,
                'current_drawdown_pct': current_drawdown,
                'max_drawdown_pct': max_drawdown,
                'volatility_pct': volatility,
                'sharpe_ratio': sharpe_ratio,
                'profit_factor': 1.0,
                'unrealized_pnl_total': 0.0,
                'total_trades': 0,
                'trades_today': 0,
                'win_rate_pct': 0.0,
                'recent_signals': [],
                'initial_balance': initial_equity
            }
            
        except Exception as e:
            print(f"Error calculando métricas de prueba: {e}")
            return {
                'total_return_pct': 0.0,
                'current_equity': 0.0,
                'current_drawdown_pct': 0.0,
                'max_drawdown_pct': 0.0,
                'volatility_pct': 0.0,
                'sharpe_ratio': 0.0,
                'profit_factor': 1.0,
                'unrealized_pnl_total': 0.0,
                'total_trades': 0,
                'trades_today': 0,
                'win_rate_pct': 0.0,
                'recent_signals': [],
                'initial_balance': 0.0
            }
    
    def _empty_metrics(self) -> Dict:
        """Métricas vacías por defecto"""
        return {
            'current_equity': 0.0,
            'total_return_pct': 0.0,
            'current_drawdown_pct': 0.0,
            'max_drawdown_pct': 0.0,
            'volatility_pct': 0.0,
            'total_fees_paid': 0.0,
            'unrealized_pnl_total': 0.0,
            'trades_today': 0,
            'total_trades': 0,
            'win_rate_pct': 0.0,
            'recent_signals': [],
            'last_update': datetime.now(),
            'initial_balance': 0.0,
            'available_balance': 0.0
        }
    
    def _calculate_unrealized_pnl(self, trade_type: str, entry_price: float, current_price: float, quantity: float) -> float:
        """Calcular PnL no realizado para un trade"""
        if entry_price <= 0 or current_price <= 0 or quantity <= 0:
            return 0.0
        
        if trade_type.upper() == 'BUY':
            return (current_price - entry_price) * quantity
        else:  # SELL
            return (entry_price - current_price) * quantity
    
    def _calculate_total_fees(self, trades: List) -> float:
        """
        💰 Calcular el total de comisiones pagadas extrayendo del campo notes
        
        Args:
            trades: Lista de trades de la base de datos
            
        Returns:
            float: Total de comisiones pagadas
        """
        import re
        total_fees = 0.0
        
        try:
            for trade in trades:
                if trade.notes:
                    # Buscar patrón "Fee: $X.XXXX" en las notas
                    fee_match = re.search(r'Fee: \$(\d+\.?\d*)', trade.notes)
                    if fee_match:
                        fee_amount = float(fee_match.group(1))
                        total_fees += fee_amount
                        
        except Exception as e:
            print(f"Error calculando comisiones totales: {e}")
            
        return round(total_fees, 4)
    
    def _get_current_price_simple(self, symbol: str, entry_price: float = None) -> float:
        """Obtener precio actual con cache para mejor rendimiento"""
        try:
            # Cache simple para evitar llamadas repetidas a la API
            cache_key = f"price_{symbol.replace('/', '')}"
            current_time = time.time()
            
            # Verificar si tenemos el precio en cache (válido por 30 segundos)
            if hasattr(self, '_price_cache'):
                if cache_key in self._price_cache:
                    cached_price, cached_time = self._price_cache[cache_key]
                    if current_time - cached_time < 30:  # Cache válido por 30 segundos
                        return cached_price
            else:
                self._price_cache = {}
            
            # Importar la función del trading monitor
            from src.tools.trading_monitor import get_current_price
            
            # Usar la función real de precios del trading monitor
            current_price = get_current_price(symbol.replace('/', ''))
            
            # Guardar en cache
            if current_price > 0:
                self._price_cache[cache_key] = (current_price, current_time)
                return current_price
            
            # Si no se pudo obtener el precio, usar el precio de entrada como fallback
            if entry_price and entry_price > 0:
                return entry_price
            
            return current_price
        except Exception as e:
            print(f"Error obteniendo precio para {symbol}: {e}")
            return entry_price or 0.0

    def get_active_trades(self) -> List[Dict]:
        """Obtener trades activos desde la base de datos"""
        try:
            with db_manager.get_db_session() as session:
                # Determinar qué tipo de trades mostrar
                is_paper_trade = self._get_trade_filter()
                
                active_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper_trade,
                    Trade.status == 'OPEN'
                ).order_by(Trade.entry_time.desc()).all()
                
                trades_data = []
                for trade in active_trades:
                    # Obtener precio actual y calcular PnL no realizado
                    current_price = self._get_current_price_simple(trade.symbol, trade.entry_price)
                    unrealized_pnl = self._calculate_unrealized_pnl(
                        trade.trade_type, 
                        trade.entry_price or 0, 
                        current_price, 
                        trade.quantity or 0
                    )
                    
                    trades_data.append({
                        'id': trade.id,
                        'symbol': trade.symbol,
                        'type': trade.trade_type,
                        'entry_price': trade.entry_price or 0,
                        'quantity': trade.quantity or 0,
                        'entry_time': trade.entry_time or datetime.now(),
                        'strategy': trade.strategy_name or 'Unknown',
                        'unrealized_pnl': round(unrealized_pnl, 2),
                        'status': trade.status
                    })
                
                return trades_data
        except Exception as e:
            print(f"Error cargando trades activos: {e}")
            return []
    
    def get_closed_trades(self, limit: int = 50) -> List[Dict]:
        """Obtener trades cerrados desde la base de datos"""
        try:
            with db_manager.get_db_session() as session:
                # Determinar qué tipo de trades mostrar
                is_paper_trade = self._get_trade_filter()
                
                closed_trades = session.query(Trade).filter(
                    Trade.is_paper_trade == is_paper_trade,
                    Trade.status == 'CLOSED'
                ).order_by(Trade.exit_time.desc()).limit(limit).all()
                
                trades_data = []
                for trade in closed_trades:
                    trades_data.append({
                        'id': trade.id,
                        'symbol': trade.symbol,
                        'type': trade.trade_type,
                        'entry_price': trade.entry_price or 0,
                        'exit_price': trade.exit_price or 0,
                        'quantity': trade.quantity or 0,
                        'entry_time': trade.entry_time or datetime.now(),
                        'exit_time': trade.exit_time or datetime.now(),
                        'strategy': trade.strategy_name or 'Unknown',
                        'pnl': trade.pnl or 0,
                        'status': trade.status
                    })
                
                return trades_data
        except Exception as e:
            print(f"Error cargando trades cerrados: {e}")
            return []
    
    def get_portfolio_summary(self) -> Dict:
        """Obtener resumen del portfolio desde la base de datos"""
        try:
            # Usar paper trading (estructura actual del proyecto)
            portfolio_summary = db_manager.get_portfolio_summary(is_paper=USE_PAPER_TRADING)
            
            # Calcular PnL No Realizado correctamente sumando todas las operaciones abiertas
            active_trades = self.get_active_trades()
            total_unrealized_pnl = 0.0
            
            for trade in active_trades:
                current_price = self._get_current_price_simple(trade['symbol'], trade['entry_price'])
                trade_unrealized_pnl = self._calculate_unrealized_pnl(
                    trade['type'], 
                    trade['entry_price'], 
                    current_price, 
                    trade['quantity']
                )
                total_unrealized_pnl += trade_unrealized_pnl
            
            # Convertir assets a formato de posiciones para el gráfico
            positions = []
            assets = portfolio_summary.get('assets', [])
            for asset in assets:
                if asset.get('current_value', 0) > 0:  # Solo incluir assets con valor
                    positions.append({
                        'symbol': asset.get('symbol', 'Unknown'),
                        'quantity': asset.get('quantity', 0),
                        'market_value': asset.get('current_value', 0),
                        'unrealized_pnl': asset.get('unrealized_pnl', 0),
                        'unrealized_pnl_pct': (asset.get('unrealized_pnl', 0) / asset.get('current_value', 1)) * 100 if asset.get('current_value', 0) > 0 else 0,
                        'avg_price': asset.get('current_value', 0) / asset.get('quantity', 1) if asset.get('quantity', 0) > 0 else 0,
                        'current_price': asset.get('current_value', 0) / asset.get('quantity', 1) if asset.get('quantity', 0) > 0 else 0
                    })
            
            result = {
                'total_value': portfolio_summary.get('total_value', 0.0),
                'available_balance': portfolio_summary.get('available_balance', 0.0),
                'positions_value': portfolio_summary.get('positions_value', 0.0),
                'unrealized_pnl': total_unrealized_pnl,  # Usar el cálculo correcto
                'realized_pnl': portfolio_summary.get('total_pnl', 0.0),
                'total_pnl': portfolio_summary.get('total_pnl', 0.0),
                'total_pnl_percentage': portfolio_summary.get('total_pnl_percentage', 0.0),
                'initial_balance': portfolio_summary.get('initial_balance', 0.0),
                'trading_mode': 'PAPER_TRADING' if USE_PAPER_TRADING else 'REAL_TRADING',
                'positions': positions  # Agregar las posiciones para el gráfico
            }
            return result
                
        except Exception as e:
            print(f"Error obteniendo portfolio summary: {e}")
            return {
                'total_value': 0.0,
                'available_balance': 0.0,
                'positions_value': 0.0,
                'unrealized_pnl': 0.0,
                'realized_pnl': 0.0,
                'total_pnl': 0.0,
                'total_pnl_percentage': 0.0,
                'initial_balance': 0.0,
                'trading_mode': 'ERROR_FALLBACK',
                'positions': []  # Lista vacía en caso de error
            }

class ChartGenerator:
    """
    📊 Generador de gráficos para el dashboard
    """
    
    def __init__(self, config: DashboardConfig):
        self.config = config
    
    def create_equity_curve(self, equity_data: List[Dict]) -> go.Figure:
        """Crear gráfico de curva de equity con marcadores de eventos y tooltips mejorados"""
        if not equity_data:
            return self._empty_chart("Curva de Equity")
        
        df = pd.DataFrame(equity_data)
        
        # Obtener trades para marcadores de eventos
        try:
            trades = db_manager.get_all_trades()
            trade_events = []
            for trade in trades:
                if trade.entry_time:
                    trade_events.append({
                        'timestamp': trade.entry_time,
                        'type': 'entry',
                        'symbol': trade.symbol,
                        'price': trade.entry_price,
                        'size': trade.size,
                        'trade_type': trade.type
                    })
                if trade.exit_time:
                    trade_events.append({
                        'timestamp': trade.exit_time,
                        'type': 'exit',
                        'symbol': trade.symbol,
                        'price': trade.exit_price,
                        'pnl': trade.pnl,
                        'trade_type': trade.type
                    })
        except Exception:
            trade_events = []
        
        fig = go.Figure()
        
        # Calcular cambios porcentuales y otros datos para tooltips
        df['change'] = df['equity'].pct_change() * 100
        df['change_abs'] = df['equity'].diff()
        df['max_equity'] = df['equity'].cummax()
        df['drawdown'] = ((df['equity'] - df['max_equity']) / df['max_equity'] * 100)
        
        # Línea principal de equity con tooltips mejorados
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['equity'],
            mode='lines',
            name='Equity',
            line=dict(color=self.config.COLORS['primary'], width=2),
            customdata=np.column_stack((df['change'].fillna(0), df['change_abs'].fillna(0), df['drawdown'])),
            hovertemplate='<b>💰 Equity: $%{y:,.2f}</b><br>' +
                         '📅 Tiempo: %{x}<br>' +
                         '📈 Cambio: %{customdata[0]:+.2f}% ($%{customdata[1]:+.2f})<br>' +
                         '📉 Drawdown: %{customdata[2]:.2f}%<br>' +
                         '<extra></extra>'
        ))
        
        # Área de relleno
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['equity'],
            fill='tonexty',
            mode='none',
            fillcolor=f"rgba{tuple(list(bytes.fromhex(self.config.COLORS['primary'][1:])) + [0.1])}",
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Agregar marcadores de eventos de trading
        for event in trade_events:
            if event['type'] == 'entry':
                fig.add_trace(go.Scatter(
                    x=[event['timestamp']],
                    y=[df[df['timestamp'] <= event['timestamp']]['equity'].iloc[-1] if len(df[df['timestamp'] <= event['timestamp']]) > 0 else df['equity'].iloc[0]],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-up',
                        size=12,
                        color='green',
                        line=dict(width=2, color='white')
                    ),
                    name='Entrada',
                    showlegend=False,
                    hovertemplate=f'<b>🟢 ENTRADA</b><br>' +
                                 f'📊 {event["symbol"]}<br>' +
                                 f'💵 Precio: ${event["price"]:,.4f}<br>' +
                                 f'📏 Tamaño: {event["size"]:.4f}<br>' +
                                 f'📈 Tipo: {event["trade_type"]}<br>' +
                                 f'🕐 {event["timestamp"]}<extra></extra>'
                ))
            else:  # exit
                fig.add_trace(go.Scatter(
                    x=[event['timestamp']],
                    y=[df[df['timestamp'] <= event['timestamp']]['equity'].iloc[-1] if len(df[df['timestamp'] <= event['timestamp']]) > 0 else df['equity'].iloc[0]],
                    mode='markers',
                    marker=dict(
                        symbol='triangle-down',
                        size=12,
                        color='red' if event.get('pnl', 0) < 0 else 'green',
                        line=dict(width=2, color='white')
                    ),
                    name='Salida',
                    showlegend=False,
                    hovertemplate=f'<b>🔴 SALIDA</b><br>' +
                                 f'📊 {event["symbol"]}<br>' +
                                 f'💵 Precio: ${event["price"]:,.4f}<br>' +
                                 f'💰 PnL: ${event.get("pnl", 0):+.2f}<br>' +
                                 f'📈 Tipo: {event["trade_type"]}<br>' +
                                 f'🕐 {event["timestamp"]}<extra></extra>'
                ))
        
        # Agregar línea de máximo histórico
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['max_equity'],
            mode='lines',
            name='Máximo Histórico',
            line=dict(color='rgba(255,255,255,0.3)', width=1, dash='dash'),
            hovertemplate='<b>🏆 Máximo: $%{y:,.2f}</b><br>%{x}<extra></extra>'
        ))
        
        # Aplicar zoom inteligente basado en el período seleccionado
        zoom_period = getattr(st.session_state, 'zoom_period', '1d')
        now = datetime.now()
        
        if zoom_period == '1h':
            start_time = now - timedelta(hours=1)
        elif zoom_period == '4h':
            start_time = now - timedelta(hours=4)
        elif zoom_period == '1d':
            start_time = now - timedelta(days=1)
        elif zoom_period == '1w':
            start_time = now - timedelta(weeks=1)
        elif zoom_period == '1m':
            start_time = now - timedelta(days=30)
        else:  # Todo
            start_time = None
        
        # Configurar el layout con zoom inteligente
        layout_config = {
            'title': f'📈 Curva de Equity en Tiempo Real ({zoom_period})',
            'xaxis_title': 'Tiempo',
            'yaxis_title': 'Equity ($)',
            'template': 'plotly_dark',
            'height': 400,
            'showlegend': True,
            'hovermode': 'x unified'
        }
        
        # Aplicar rango de tiempo si está definido
        if start_time:
            layout_config['xaxis'] = dict(range=[start_time, now])
        
        fig.update_layout(**layout_config)
        
        return fig
    
    def create_drawdown_chart(self, equity_data: List[Dict]) -> go.Figure:
        """Crear gráfico de drawdown"""
        if not equity_data:
            return self._empty_chart("Drawdown")
        
        df = pd.DataFrame(equity_data)
        
        # Calcular drawdown
        running_max = df['equity'].expanding().max()
        drawdown = (df['equity'] - running_max) / running_max * 100
        
        fig = go.Figure()
        
        # Área de drawdown
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=drawdown,
            fill='tonexty',
            mode='lines',
            name='Drawdown',
            line=dict(color=self.config.COLORS['danger'], width=2),
            fillcolor=f"rgba{tuple(list(bytes.fromhex(self.config.COLORS['danger'][1:])) + [0.3])}",
            hovertemplate='<b>%{y:.4f}%</b><br>%{x}<extra></extra>'
        ))
        
        # Ajustar el rango del eje Y para mostrar mejor los valores pequeños
        y_min = drawdown.min()
        y_max = max(drawdown.max(), 0.01)  # Asegurar que el máximo sea al menos 0.01%
        
        # Si el drawdown es muy pequeño, ajustar el rango para mejor visualización
        if abs(y_min) < 0.1:
            y_range = [y_min * 1.2, y_max * 1.2]
        else:
            y_range = [y_min * 1.1, y_max * 1.1]
        
        fig.update_layout(
            title='Drawdown en Tiempo Real',
            xaxis_title='Tiempo',
            yaxis_title='Drawdown (%)',
            template='plotly_dark',
            height=300,
            yaxis=dict(
                range=y_range,
                tickformat='.4f'  # Mostrar más decimales para valores pequeños
            )
        )
        
        return fig
    
    def create_performance_metrics(self, metrics: Dict) -> go.Figure:
        """Crear gráfico de métricas de performance con información detallada"""
        # Métricas para mostrar con información adicional
        metric_data = [
            {
                'name': 'Total Return',
                'value': metrics.get('total_return_pct', 0),
                'description': 'Retorno total del portfolio',
                'benchmark': '> 10% Excelente, 5-10% Bueno, < 5% Regular',
                'emoji': '💰'
            },
            {
                'name': 'Win Rate',
                'value': metrics.get('win_rate_pct', 0),
                'description': 'Porcentaje de trades ganadores',
                'benchmark': '> 60% Excelente, 50-60% Bueno, < 50% Regular',
                'emoji': '🎯'
            },
            {
                'name': 'Max Drawdown',
                'value': abs(metrics.get('max_drawdown_pct', 0)),
                'description': 'Máxima pérdida desde el pico',
                'benchmark': '< 10% Excelente, 10-20% Aceptable, > 20% Alto riesgo',
                'emoji': '📉'
            },
            {
                'name': 'Sharpe Ratio',
                'value': metrics.get('sharpe_ratio', 0),
                'description': 'Retorno ajustado por riesgo',
                'benchmark': '> 2.0 Excelente, 1.0-2.0 Bueno, < 1.0 Regular',
                'emoji': '⚖️'
            },
            {
                'name': 'Volatility',
                'value': metrics.get('volatility_pct', 0),
                'description': 'Volatilidad del portfolio',
                'benchmark': '< 15% Bajo, 15-25% Medio, > 25% Alto',
                'emoji': '📊'
            },
            {
                'name': 'Profit Factor',
                'value': metrics.get('profit_factor', 0),
                'description': 'Ratio ganancias/pérdidas',
                'benchmark': '> 2.0 Excelente, 1.5-2.0 Bueno, < 1.5 Regular',
                'emoji': '💹'
            }
        ]
        
        metric_names = [f"{m['emoji']} {m['name']}" for m in metric_data]
        metric_values = [m['value'] for m in metric_data]
        
        # Colores basados en valores y benchmarks
        colors = []
        for i, data in enumerate(metric_data):
            value = data['value']
            name = data['name']
            
            if name == 'Max Drawdown':  # Menor es mejor
                color = (self.config.COLORS['success'] if value < 10 else 
                        self.config.COLORS['warning'] if value < 20 else 
                        self.config.COLORS['danger'])
            elif name == 'Volatility':  # Menor es mejor
                color = (self.config.COLORS['success'] if value < 15 else 
                        self.config.COLORS['warning'] if value < 25 else 
                        self.config.COLORS['danger'])
            elif name == 'Sharpe Ratio':  # Mayor es mejor
                color = (self.config.COLORS['success'] if value > 2.0 else 
                        self.config.COLORS['warning'] if value > 1.0 else 
                        self.config.COLORS['danger'])
            elif name == 'Profit Factor':  # Mayor es mejor
                color = (self.config.COLORS['success'] if value > 2.0 else 
                        self.config.COLORS['warning'] if value > 1.5 else 
                        self.config.COLORS['danger'])
            else:  # Total Return, Win Rate - Mayor es mejor
                color = (self.config.COLORS['success'] if value > 10 else 
                        self.config.COLORS['warning'] if value > 0 else 
                        self.config.COLORS['danger'])
            
            colors.append(color)
        
        # Crear tooltips informativos
        hover_texts = []
        for data in metric_data:
            hover_text = (f"<b>{data['emoji']} {data['name']}</b><br>"
                         f"📊 Valor: {data['value']:.2f}{'%' if 'Ratio' not in data['name'] and 'Factor' not in data['name'] else ''}<br>"
                         f"📋 {data['description']}<br>"
                         f"🎯 Benchmark: {data['benchmark']}<extra></extra>")
            hover_texts.append(hover_text)
        
        fig = go.Figure(data=[
            go.Bar(
                x=metric_names,
                y=metric_values,
                marker_color=colors,
                text=[f'{v:.1f}{"%" if "Ratio" not in metric_data[i]["name"] and "Factor" not in metric_data[i]["name"] else ""}' 
                      for i, v in enumerate(metric_values)],
                textposition='outside',
                textfont=dict(size=12, color='white'),
                hovertemplate=hover_texts,
                customdata=[data['description'] for data in metric_data]
            )
        ])
        
        fig.update_layout(
            title='📊 Métricas Avanzadas de Performance',
            template='plotly_dark',
            height=500,
            showlegend=False,
            xaxis=dict(tickangle=45),
            yaxis=dict(range=[-20, 100]),
            margin=dict(b=100, t=150)
        )
        
        return fig
    
    def create_signal_distribution(self, signals: List[Dict]) -> go.Figure:
        """Crear gráfico de distribución de señales con información contextual"""
        if not signals:
            return self._empty_chart("Distribución de Señales")
        
        # Contar señales por tipo y calcular estadísticas
        signal_counts = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        signal_details = {'BUY': [], 'SELL': [], 'HOLD': []}
        
        for signal in signals:
            signal_type = signal.get('signal', 'HOLD')
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
            
            # Recopilar detalles para tooltips
            signal_details[signal_type].append({
                'timestamp': signal.get('timestamp', ''),
                'symbol': signal.get('symbol', ''),
                'confidence': signal.get('confidence', 0),
                'price': signal.get('price', 0)
            })
        
        # Calcular estadísticas adicionales
        total_signals = sum(signal_counts.values())
        recent_signals = [s for s in signals[-24:]]  # Últimas 24 señales como proxy de 24h
        
        labels = []
        values = []
        colors = []
        hover_texts = []
        
        signal_info = {
            'BUY': {
                'emoji': '🟢',
                'color': self.config.COLORS['success'],
                'description': 'Señales de compra - Oportunidades alcistas'
            },
            'SELL': {
                'emoji': '🔴', 
                'color': self.config.COLORS['danger'],
                'description': 'Señales de venta - Oportunidades bajistas'
            },
            'HOLD': {
                'emoji': '🟡',
                'color': self.config.COLORS['info'],
                'description': 'Señales de mantener - Mercado lateral'
            }
        }
        
        for signal_type, count in signal_counts.items():
            if count > 0:
                info = signal_info[signal_type]
                labels.append(f"{info['emoji']} {signal_type}")
                values.append(count)
                colors.append(info['color'])
                
                # Calcular estadísticas para tooltip
                details = signal_details[signal_type]
                avg_confidence = np.mean([d['confidence'] for d in details if d['confidence'] > 0]) if details else 0
                recent_count = len([s for s in recent_signals if s.get('signal') == signal_type])
                percentage = (count / total_signals) * 100 if total_signals > 0 else 0
                
                # Crear tooltip informativo
                hover_text = (f"<b>{info['emoji']} {signal_type}</b><br>"
                             f"📊 Cantidad: {count}<br>"
                             f"📈 Porcentaje: {percentage:.1f}%<br>"
                             f"🎯 Confianza promedio: {avg_confidence:.1f}%<br>"
                             f"⏰ Recientes: {recent_count}<br>"
                             f"📋 {info['description']}<extra></extra>")
                hover_texts.append(hover_text)
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hovertemplate=hover_texts,
            textinfo='label+percent',
            textposition='auto',
            hole=0.3  # Donut chart para mejor visualización
        )])
        
        # Agregar texto central con total de señales
        fig.add_annotation(
            text=f"<b>Total<br>{total_signals}</b><br><span style='font-size:12px'>señales</span>",
            x=0.5, y=0.5,
            font_size=16,
            font_color="white",
            showarrow=False
        )
        
        fig.update_layout(
            title={
                'text': "📡 Distribución de Señales de Trading",
                'x': 0.5,
                'xanchor': 'center'
            },
            template='plotly_dark',
            height=400,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            ),
            margin=dict(l=20, r=100, t=60, b=20)
        )
        
        return fig
    
    def create_trade_timeline(self, trades: List[Dict]) -> go.Figure:
        """Crear timeline de trades con información detallada"""
        if not trades:
            return self._empty_chart("Timeline de Trades")
        
        # Filtrar trades recientes y calcular estadísticas
        recent_trades = trades[-30:] if len(trades) > 30 else trades
        
        # Separar trades ganadores y perdedores
        winning_trades = [t for t in recent_trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in recent_trades if t.get('pnl', 0) <= 0]
        
        fig = go.Figure()
        
        # Agregar trades ganadores
        if winning_trades:
            win_x = [trade.get('timestamp', datetime.now()) for trade in winning_trades]
            win_y = [trade.get('pnl', 0) for trade in winning_trades]
            win_symbols = ['triangle-up' if trade.get('side') == 'BUY' else 'circle' for trade in winning_trades]
            
            # Crear tooltips detallados para trades ganadores
            win_hovertexts = []
            for trade in winning_trades:
                duration = trade.get('duration_minutes', 0)
                roi = trade.get('roi_pct', 0)
                hover_text = (f"<b>🟢 TRADE GANADOR</b><br>"
                             f"💰 PnL: ${trade.get('pnl', 0):+.2f}<br>"
                             f"📈 ROI: {roi:+.2f}%<br>"
                             f"🏷️ {trade.get('symbol', 'N/A')}<br>"
                             f"📊 {trade.get('side', 'N/A')} @ ${trade.get('price', 0):.4f}<br>"
                             f"⏱️ Duración: {duration:.0f} min<br>"
                             f"📅 {trade.get('timestamp', 'N/A')}<extra></extra>")
                win_hovertexts.append(hover_text)
            
            fig.add_trace(go.Scatter(
                x=win_x,
                y=win_y,
                mode='markers',
                marker=dict(
                    size=12,
                    color=self.config.COLORS['success'],
                    symbol=win_symbols,
                    line=dict(width=2, color='white')
                ),
                name='Trades Ganadores',
                hovertemplate=win_hovertexts,
                showlegend=True
            ))
        
        # Agregar trades perdedores
        if losing_trades:
            loss_x = [trade.get('timestamp', datetime.now()) for trade in losing_trades]
            loss_y = [trade.get('pnl', 0) for trade in losing_trades]
            loss_symbols = ['triangle-down' if trade.get('side') == 'SELL' else 'x' for trade in losing_trades]
            
            # Crear tooltips detallados para trades perdedores
            loss_hovertexts = []
            for trade in losing_trades:
                duration = trade.get('duration_minutes', 0)
                roi = trade.get('roi_pct', 0)
                hover_text = (f"<b>🔴 TRADE PERDEDOR</b><br>"
                             f"💸 PnL: ${trade.get('pnl', 0):+.2f}<br>"
                             f"📉 ROI: {roi:+.2f}%<br>"
                             f"🏷️ {trade.get('symbol', 'N/A')}<br>"
                             f"📊 {trade.get('side', 'N/A')} @ ${trade.get('price', 0):.4f}<br>"
                             f"⏱️ Duración: {duration:.0f} min<br>"
                             f"📅 {trade.get('timestamp', 'N/A')}<extra></extra>")
                loss_hovertexts.append(hover_text)
            
            fig.add_trace(go.Scatter(
                x=loss_x,
                y=loss_y,
                mode='markers',
                marker=dict(
                    size=12,
                    color=self.config.COLORS['danger'],
                    symbol=loss_symbols,
                    line=dict(width=2, color='white')
                ),
                name='Trades Perdedores',
                hovertemplate=loss_hovertexts,
                showlegend=True
            ))
        
        # Agregar línea de break-even
        if recent_trades:
            x_range = [min([t.get('timestamp', datetime.now()) for t in recent_trades]),
                      max([t.get('timestamp', datetime.now()) for t in recent_trades])]
            fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                         annotation_text="Break Even", annotation_position="bottom right")
        
        # Calcular estadísticas para el título
        total_pnl = sum([t.get('pnl', 0) for t in recent_trades])
        win_rate = (len(winning_trades) / len(recent_trades)) * 100 if recent_trades else 0
        
        fig.update_layout(
            title={
                'text': f"📊 Timeline de Trades - PnL Total: ${total_pnl:+.2f} | Win Rate: {win_rate:.1f}%",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='⏰ Tiempo',
            yaxis_title='💰 PnL ($)',
            template='plotly_dark',
            height=400,
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            hovermode='closest'
        )
        
        # Mejorar formato de ejes
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)', zeroline=True)
        
        return fig
    
    def create_portfolio_distribution(self, portfolio_data: Dict) -> go.Figure:
        """Crear gráfico de distribución del portfolio con información detallada"""
        if not portfolio_data or not portfolio_data.get('positions'):
            return self._empty_chart("Distribución del Portfolio")
        
        positions = portfolio_data['positions']
        
        # Preparar datos para el gráfico
        symbols = []
        values = []
        colors = []
        hover_texts = []
        
        total_value = sum([pos.get('market_value', 0) for pos in positions])
        
        for position in positions:
            symbol = position.get('symbol', 'Unknown')
            market_value = position.get('market_value', 0)
            quantity = position.get('quantity', 0)
            avg_price = position.get('avg_price', 0)
            current_price = position.get('current_price', 0)
            pnl = position.get('unrealized_pnl', 0)
            pnl_pct = position.get('unrealized_pnl_pct', 0)
            
            if market_value > 0:
                symbols.append(symbol)
                values.append(market_value)
                
                # Color basado en PnL
                if pnl > 0:
                    color = self.config.COLORS['success']
                    emoji = "🟢"
                elif pnl < 0:
                    color = self.config.COLORS['danger']
                    emoji = "🔴"
                else:
                    color = self.config.COLORS['info']
                    emoji = "🟡"
                
                colors.append(color)
                
                # Calcular porcentaje del portfolio
                portfolio_pct = (market_value / total_value) * 100 if total_value > 0 else 0
                
                # Crear tooltip detallado
                hover_text = (f"<b>{emoji} {symbol}</b><br>"
                             f"💰 Valor: ${market_value:,.2f}<br>"
                             f"📊 Portfolio: {portfolio_pct:.1f}%<br>"
                             f"📈 Cantidad: {quantity:.4f}<br>"
                             f"💵 Precio promedio: ${avg_price:.4f}<br>"
                             f"📍 Precio actual: ${current_price:.4f}<br>"
                             f"💹 PnL: ${pnl:+.2f} ({pnl_pct:+.2f}%)<extra></extra>")
                hover_texts.append(hover_text)
        
        if not symbols:
            return self._empty_chart("Portfolio sin posiciones activas")
        
        fig = go.Figure(data=[go.Pie(
            labels=symbols,
            values=values,
            marker_colors=colors,
            hovertemplate=hover_texts,
            textinfo='label+percent',
            textposition='auto',
            hole=0.4  # Donut chart
        )])
        
        # Agregar información central
        total_pnl = sum([pos.get('unrealized_pnl', 0) for pos in positions])
        total_pnl_pct = (total_pnl / total_value) * 100 if total_value > 0 else 0
        
        fig.add_annotation(
            text=f"<b>Portfolio<br>${total_value:,.0f}</b><br>"
                 f"<span style='font-size:12px'>PnL: ${total_pnl:+.2f}<br>"
                 f"({total_pnl_pct:+.1f}%)</span>",
            x=0.5, y=0.5,
            font_size=14,
            font_color="white",
            showarrow=False
        )
        
        fig.update_layout(
            title={
                'text': "🎯 Distribución del Portfolio",
                'x': 0.5,
                'xanchor': 'center'
            },
            template='plotly_dark',
            height=450,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            ),
            margin=dict(l=20, r=120, t=60, b=20)
        )
        
        return fig
    

    

    
    def _get_gauge_color(self, value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Obtener color del medidor basado en umbrales"""
        if value >= critical_threshold:
            return "red"
        elif value >= warning_threshold:
            return "orange"
        else:
            return "green"
    
    def _empty_chart(self, title: str) -> go.Figure:
        """Crear gráfico vacío"""
        fig = go.Figure()
        fig.add_annotation(
            text="Sin datos disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color=self.config.COLORS['text'])
        )
        fig.update_layout(
            title=title,
            template='plotly_dark',
            height=300
        )
        return fig

class RealTimeDashboard:
    """
    🚀 Dashboard principal de monitoreo en tiempo real
    """
    
    def __init__(self, config: DashboardConfig = None):
        self.config = config or DashboardConfig()
        
        # Usar singleton para MetricsCalculator para evitar múltiples PaperTrader
        if 'metrics_calculator' not in st.session_state:
            st.session_state.metrics_calculator = MetricsCalculator()
        self.metrics_calc = st.session_state.metrics_calculator
        
        self.chart_gen = ChartGenerator(self.config)
        
        # Inicializar session state si no existe
        if 'is_running' not in st.session_state:
            st.session_state.is_running = False
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
        if 'data_history' not in st.session_state:
            st.session_state.data_history = []
        
        # Estado del dashboard usando session state
        self.is_running = st.session_state.is_running
        self.last_update = st.session_state.last_update
        self.data_history = st.session_state.data_history
        
        # Configurar Streamlit
        self._setup_streamlit()
    
    def _setup_streamlit(self):
        """Configurar Streamlit"""
        st.set_page_config(
            page_title="Crypto Trading Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Configuración adicional para evitar efectos de recarga
        if hasattr(st, '_config'):
            st._config.set_option('client.showErrorDetails', False)
            st._config.set_option('client.toolbarMode', 'minimal')
        
        # JavaScript para evitar efectos de recarga
        st.markdown("""
        <script>
        // Evitar que se muestren indicadores de recarga
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) {
                        // Ocultar spinners y overlays
                        if (node.classList && (
                            node.classList.contains('stSpinner') ||
                            node.classList.contains('stAlert') ||
                            node.getAttribute('data-testid') === 'stStatusWidget' ||
                            node.getAttribute('data-testid') === 'stConnectionStatus'
                        )) {
                            node.style.display = 'none';
                            node.style.visibility = 'hidden';
                        }
                        
                        // Buscar en elementos hijos también
                        const spinners = node.querySelectorAll('.stSpinner, .stAlert, [data-testid="stStatusWidget"], [data-testid="stConnectionStatus"]');
                        spinners.forEach(spinner => {
                            spinner.style.display = 'none';
                            spinner.style.visibility = 'hidden';
                        });
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        </script>
        """, unsafe_allow_html=True)
        
        # CSS personalizado
        st.markdown("""
        <style>
        .metric-card {
            background-color: #262730;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #888;
            margin: 0;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-active { background-color: #2ca02c; }
        .status-inactive { background-color: #d62728; }
        .status-warning { background-color: #ff7f0e; }
        
        /* Eliminar completamente el efecto de "apagado" durante recargas */
        .stSpinner, .stSpinner > div, .stSpinner > div > div {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Ocultar todos los overlays de recarga */
        .stApp > div[data-testid="stAppViewContainer"] > div[data-testid="stAppViewBlockContainer"] > div[data-testid="stVerticalBlock"] > div.element-container > div.stAlert,
        div[data-testid="stStatusWidget"],
        .stApp > header[data-testid="stHeader"],
        div[data-testid="stConnectionStatus"] {
            display: none !important;
            visibility: hidden !important;
        }
        
        /* Forzar opacidad completa en todos los elementos principales */
        .main, .main .block-container, .stApp, .stApp > div, 
        div[data-testid="stAppViewContainer"], 
        div[data-testid="stAppViewBlockContainer"],
        div[data-testid="stVerticalBlock"],
        .element-container {
            opacity: 1 !important;
            visibility: visible !important;
        }
        
        /* Evitar cualquier transición de opacidad */
        .main *, .stApp *, div[data-testid="stAppViewContainer"] * {
            transition: none !important;
            opacity: 1 !important;
        }
        
        /* Ocultar indicadores de estado de conexión */
        .stConnectionStatus, .stTooltipHoverTarget {
            display: none !important;
        }
        
        /* Evitar que se oscurezca el contenido */
        .stApp::before, .stApp::after, .main::before, .main::after {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Ejecutar el dashboard"""
        # Header
        self._render_header()
        
        # Sidebar
        self._render_sidebar()
        
        # Contenido principal
        if self.is_running:
            self._render_main_content()
        else:
            self._render_welcome_screen()
    
    def _render_header(self):
        """Renderizar header del dashboard"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("📊 Crypto Trading Dashboard")
        
        with col2:
            status_color = "status-active" if self.is_running else "status-inactive"
            status_text = "ACTIVO" if self.is_running else "INACTIVO"
            st.markdown(f"""
            <div style="text-align: center; margin-top: 1rem;">
                <span class="status-indicator {status_color}"></span>
                <strong>{status_text}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if self.last_update:
                st.markdown(f"""
                <div style="text-align: center; margin-top: 1rem;">
                    <small>Última actualización:<br>{self.last_update.strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_sidebar(self):
        """Renderizar sidebar con controles"""
        st.sidebar.header("⚙️ Controles")
        
        # Control de estado
        if st.sidebar.button("▶️ Iniciar" if not self.is_running else "⏸️ Pausar"):
            st.session_state.is_running = not st.session_state.is_running
            self.is_running = st.session_state.is_running
            st.rerun()
        
        # Configuración
        st.sidebar.subheader("📋 Configuración")
        
        refresh_interval = st.sidebar.slider(
            "Intervalo de actualización (seg)",
            min_value=1,
            max_value=60,
            value=self.config.REFRESH_INTERVAL
        )
        self.config.REFRESH_INTERVAL = refresh_interval
        
        # Información del sistema
        st.sidebar.subheader("ℹ️ Sistema")
        
        # Mostrar modo de trading actual
        trading_mode_info = self._get_trading_mode_info()
        st.sidebar.info(f"**Modo:** {trading_mode_info['mode']}")
        st.sidebar.info(f"**Perfil:** {trading_mode_info['profile']}")
        
        metrics = self.metrics_calc.get_current_metrics()
        
        st.sidebar.metric(
            "Trades Totales",
            metrics['total_trades']
        )
        
        st.sidebar.metric(
            "Trades Hoy",
            metrics['trades_today']
        )
        
        st.sidebar.metric(
            "Tasa de Ganancia",
            f"{metrics['win_rate_pct']:.1f}%"
        )
        
        # Alertas mejoradas
        st.sidebar.subheader("🚨 Alertas Inteligentes")
        
        alert_count = 0
        
        # Alerta de drawdown crítico
        if metrics['current_drawdown_pct'] < -20:
            st.sidebar.error(f"🔴 CRÍTICO: Drawdown extremo {metrics['current_drawdown_pct']:.1f}%")
            alert_count += 1
        elif metrics['current_drawdown_pct'] < -10:
            st.sidebar.warning(f"🟡 ATENCIÓN: Drawdown alto {metrics['current_drawdown_pct']:.1f}%")
            alert_count += 1
        
        # Alerta de volatilidad
        if metrics['volatility_pct'] > 50:
            st.sidebar.warning(f"🟡 Alta volatilidad: {metrics['volatility_pct']:.1f}%")
            alert_count += 1
        
        # Alerta de win rate bajo
        if metrics['win_rate_pct'] < 40:
            st.sidebar.warning(f"🟡 Win rate bajo: {metrics['win_rate_pct']:.1f}%")
            alert_count += 1
        
        # Alerta de Sharpe ratio bajo
        if metrics.get('sharpe_ratio', 0) < 0.5:
            st.sidebar.warning(f"🟡 Sharpe ratio bajo: {metrics.get('sharpe_ratio', 0):.2f}")
            alert_count += 1
        
        # Alerta de profit factor bajo
        if metrics.get('profit_factor', 0) < 1.2:
            st.sidebar.warning(f"🟡 Profit factor bajo: {metrics.get('profit_factor', 0):.2f}")
            alert_count += 1
        
        # Mensaje si no hay alertas
        if alert_count == 0:
            st.sidebar.success("✅ Todo funcionando correctamente")
        else:
            st.sidebar.info(f"📊 {alert_count} alerta(s) activa(s)")
        
        # Controles de zoom inteligente
        st.sidebar.subheader("🔍 Zoom Inteligente")
        
        zoom_period = st.sidebar.selectbox(
            "Período de análisis:",
            ["1h", "4h", "1d", "1w", "1m", "Todo"],
            index=2,
            help="Selecciona el período para enfocar los gráficos"
        )
        
        # Guardar en session state para usar en gráficos
        st.session_state['zoom_period'] = zoom_period
    
    def _render_main_content(self):
        """Renderizar contenido principal del dashboard con datos reales"""
        # Obtener métricas actuales desde la base de datos
        metrics = self.metrics_calc.get_current_metrics()
        
        # Obtener datos reales de trades
        active_trades = self.metrics_calc.get_active_trades()
        closed_trades = self.metrics_calc.get_closed_trades(limit=100)
        portfolio_summary = self.metrics_calc.get_portfolio_summary()
        
        # Mostrar resumen del portfolio
        st.subheader("💼 Resumen del Portfolio")
        
        # Indicador del modo de trading
        trading_mode = portfolio_summary.get('trading_mode', 'UNKNOWN')
        if trading_mode == 'REAL_TRADING':
            st.success("🚀 **Modo Activo:** Trading Real en Binance Testnet")
        elif trading_mode == 'PAPER_TRADING':
            st.info("🎭 **Modo Activo:** Paper Trading (Simulación)")
        else:
            st.warning("⚠️ **Modo Activo:** Modo de trading no identificado")
        
        # Métricas principales
        self._render_key_metrics(metrics)
        
        # Gráficos principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Curva de equity (usar datos reales si están disponibles)
            if closed_trades:
                # Crear datos de equity basados en trades cerrados
                equity_data = []
                running_equity = metrics.get('initial_balance', 0.0)  # Equity inicial desde DB
                for trade in sorted(closed_trades, key=lambda x: x.get('exit_time', datetime.now())):
                    running_equity += trade.get('pnl', 0)
                    equity_data.append({
                        'timestamp': trade.get('exit_time', datetime.now()),
                        'equity': running_equity
                    })
                equity_chart = self.chart_gen.create_equity_curve(equity_data)
            else:
                equity_chart = self.chart_gen._empty_chart("Curva de Equity")
            st.plotly_chart(equity_chart, width='stretch')
            
            # Drawdown (usar datos reales)
            if closed_trades:
                drawdown_chart = self.chart_gen.create_drawdown_chart(equity_data)
            else:
                drawdown_chart = self.chart_gen._empty_chart("Drawdown")
            st.plotly_chart(drawdown_chart, width='stretch')
        
        with col2:
            # Métricas de performance
            perf_chart = self.chart_gen.create_performance_metrics(metrics)
            st.plotly_chart(perf_chart, width='stretch')
            
            # Distribución de señales
            signal_chart = self.chart_gen.create_signal_distribution(metrics['recent_signals'])
            st.plotly_chart(signal_chart, width='stretch')
        
        with col3:
            # Distribución del portfolio
            portfolio_chart = self.chart_gen.create_portfolio_distribution(portfolio_summary)
            st.plotly_chart(portfolio_chart, width='stretch')
        
        # Timeline de trades (usar datos reales)
        if closed_trades:
            trade_chart = self.chart_gen.create_trade_timeline(closed_trades)
        else:
            trade_chart = self.chart_gen._empty_chart("Timeline de Trades")
        st.plotly_chart(trade_chart, width='stretch')
        
        # Tabla de trades activos
        st.subheader("📈 Trades Activos")
        if active_trades:
            active_df = pd.DataFrame(active_trades)
            # Seleccionar y renombrar columnas relevantes
            display_columns = {
                'symbol': 'Symbol',
                'type': 'Type',
                'entry_price': 'Entry Price',
                'quantity': 'Quantity',
                'unrealized_pnl': 'Unrealized PnL',
                'strategy': 'Strategy'
            }
            active_df_display = active_df[list(display_columns.keys())].rename(columns=display_columns)
            
            # Formatear columnas numéricas
            if 'Entry Price' in active_df_display.columns:
                active_df_display['Entry Price'] = active_df_display['Entry Price'].apply(lambda x: f"${x:.4f}")
            if 'Quantity' in active_df_display.columns:
                active_df_display['Quantity'] = active_df_display['Quantity'].apply(lambda x: f"{x:.6f}")
            if 'Unrealized PnL' in active_df_display.columns:
                active_df_display['Unrealized PnL'] = active_df_display['Unrealized PnL'].apply(lambda x: f"${x:.2f}")
            
            st.dataframe(active_df_display, width='stretch', hide_index=True)
        else:
            st.info("No hay trades activos")
        
        # Tabla de señales recientes
        self._render_recent_signals(metrics['recent_signals'])
        
        # Tabla de trades cerrados recientes
        st.subheader("📊 Trades Cerrados Recientes")
        if closed_trades:
            recent_closed = closed_trades[:10]  # Últimos 10
            closed_df = pd.DataFrame(recent_closed)
            st.dataframe(closed_df, width='stretch')
        else:
            st.info("No hay trades cerrados")
        
        # Nuevas secciones: Apalancamiento y Trailing SL
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_leverage_section()
        
        with col2:
            self._render_trailing_sl_section()
        
        # Auto-refresh
        time.sleep(self.config.REFRESH_INTERVAL)
        st.rerun()
    
    def _render_key_metrics(self, metrics: Dict):
        """Renderizar métricas clave con alertas visuales"""
        
        # Notificaciones importantes en la parte superior
        self._render_critical_alerts(metrics)
        
        # Primera fila: Métricas principales del portfolio
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Balance Actual (USDT disponible sin invertir)
            available_balance = metrics.get('available_balance', 0.0)
            emoji = "💵"
            st.metric(
                f"{emoji} USDT Disponibles",
                f"${available_balance:,.2f}"
            )
        
        with col2:
            # Valor Portfolio (Valor total incluyendo posiciones y PnL)
            total_value = metrics['current_equity']
            initial_balance = metrics.get('initial_balance', 0.0)
            growth = total_value - initial_balance
            growth_pct = (growth / initial_balance) * 100 if initial_balance > 0 else 0
            
            emoji = "📊" if growth >= 0 else "📉"
            st.metric(
                f"{emoji} Valor Portfolio (USDT)",
                f"${total_value:,.2f}"
            )
        
        with col3:
            # PnL No Realizado
            unrealized_pnl = metrics.get('unrealized_pnl_total', 0.0)
            emoji = "🔄" if unrealized_pnl >= 0 else "🔻"
            delta_color = "normal" if unrealized_pnl >= 0 else "inverse"
            st.metric(
                f"{emoji} PnL No Realizado",
                f"${unrealized_pnl:,.2f}"
            )
        
        with col4:
            # PnL Realizado (suma de PnL de trades cerrados)
            realized_pnl = metrics.get('realized_pnl', 0.0)
            emoji = "✅" if realized_pnl >= 0 else "❌"
            delta_color = "normal" if realized_pnl >= 0 else "inverse"
            st.metric(
                f"{emoji} PnL Realizado",
                f"${realized_pnl:,.2f}"
            )
        
        # Segunda fila: Métricas de performance
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Retorno Total
            delta_color = "normal"
            emoji = "🚀" if metrics['total_return_pct'] > 10 else "📈" if metrics['total_return_pct'] > 0 else "📉"
            st.metric(
                f"{emoji} Retorno Total",
                f"{metrics['total_return_pct']:.2f}%"
            )
        
        with col2:
            # Total de Comisiones Pagadas
            total_fees = metrics.get('total_fees_paid', 0.0)
            emoji = "💰"
            st.metric(
                f"{emoji} Comisiones Totales",
                f"{total_fees:.4f}"
            )
        
        with col3:
            # Volatilidad
            st.metric(
                "📊 Volatilidad",
                f"{metrics['volatility_pct']:.1f}%"
            )
        

    
    def _render_recent_signals(self, signals: List[Dict]):
        """Renderizar tabla de señales recientes"""
        st.subheader("🎯 Señales Recientes")
        
        if not signals:
            st.info("No hay señales recientes")
            return
        
        # Preparar datos para la tabla
        table_data = []
        for signal in signals[-10:]:  # Últimas 10 señales
            table_data.append({
                'Tiempo': signal.get('timestamp', datetime.now()).strftime('%H:%M:%S'),
                'Señal': signal.get('signal', 'N/A'),
                'Confianza': f"{signal.get('confidence', 0):.2f}",
                'Precio': f"${signal.get('price', 0):.4f}",
                'Interpretación': signal.get('interpretation', 'N/A')[:50] + '...' if len(signal.get('interpretation', '')) > 50 else signal.get('interpretation', 'N/A')
            })
        
        # Mostrar tabla
        df = pd.DataFrame(table_data)
        st.dataframe(df, width='stretch', hide_index=True)
    
    def _render_welcome_screen(self):
        """Renderizar pantalla de bienvenida"""
        # Título principal
        st.markdown("<h2 style='text-align: center;'>🚀 Bienvenido al Dashboard de Trading</h2>", unsafe_allow_html=True)
        
        # Descripción
        st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #888;'>Haz clic en 'Iniciar' en la barra lateral para comenzar el monitoreo en tiempo real.</p>", unsafe_allow_html=True)
        
        # Espaciado
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Características del dashboard
        st.markdown("<h3 style='text-align: center;'>📊 Características del Dashboard:</h3>", unsafe_allow_html=True)
        
        # Lista de características usando Streamlit nativo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            - 📈 **Monitoreo de equity en tiempo real**
            - 📉 **Análisis de drawdown continuo**
            - 📊 **Métricas de performance actualizadas**
            - ⏰ **Timeline de trades y señales**
            - 🚨 **Alertas automáticas de riesgo**
            - 🎯 **Visualizaciones interactivas**
            """)
    
    def update_data(self, equity: float, trade_data: Dict = None, signal_data: Dict = None):
        """Actualizar datos del dashboard"""
        timestamp = datetime.now()
        
        # Actualizar equity
        self.metrics_calc.update_equity(timestamp, equity)
        
        # Actualizar trade si se proporciona
        if trade_data:
            trade_data['timestamp'] = timestamp
            self.metrics_calc.update_trade(trade_data)
        
        # Actualizar señal si se proporciona
        if signal_data:
            signal_data['timestamp'] = timestamp
            self.metrics_calc.update_signal(signal_data)
        
        self.last_update = timestamp
        st.session_state.last_update = timestamp

    def _render_critical_alerts(self, metrics: Dict):
        """Renderizar alertas críticas en tiempo real"""
        alerts = []
        
        # Alerta de drawdown extremo
        if metrics['current_drawdown_pct'] < -25:
            alerts.append({
                'type': 'error',
                'message': f"🚨 ALERTA CRÍTICA: Drawdown extremo de {metrics['current_drawdown_pct']:.1f}%. Considere revisar la estrategia.",
                'priority': 1
            })
        elif metrics['current_drawdown_pct'] < -15:
            alerts.append({
                'type': 'warning',
                'message': f"⚠️ ATENCIÓN: Drawdown significativo de {metrics['current_drawdown_pct']:.1f}%. Monitoree de cerca.",
                'priority': 2
            })
        
        # Alerta de pérdidas consecutivas
        if metrics.get('win_rate_pct', 100) < 30:
            alerts.append({
                'type': 'warning',
                'message': f"📉 Win rate muy bajo: {metrics.get('win_rate_pct', 0):.1f}%. Revise la estrategia de trading.",
                'priority': 2
            })
        
        # Alerta de volatilidad extrema
        if metrics.get('volatility_pct', 0) > 75:
            alerts.append({
                'type': 'warning',
                'message': f"📊 Volatilidad extrema: {metrics.get('volatility_pct', 0):.1f}%. Mercado muy inestable.",
                'priority': 2
            })
        
        # Alerta de Sharpe ratio muy bajo
        if metrics.get('sharpe_ratio', 0) < 0:
            alerts.append({
                'type': 'warning',
                'message': f"⚖️ Sharpe ratio negativo: {metrics.get('sharpe_ratio', 0):.2f}. Retorno no justifica el riesgo.",
                'priority': 2
            })
        
        # Alerta de profit factor bajo
        if metrics.get('profit_factor', 0) < 1.0:
            alerts.append({
                'type': 'error',
                'message': f"💹 Profit factor crítico: {metrics.get('profit_factor', 0):.2f}. Pérdidas superan ganancias.",
                'priority': 1
            })
        
        # Mostrar alertas ordenadas por prioridad
        alerts.sort(key=lambda x: x['priority'])
        
        for alert in alerts[:3]:  # Mostrar máximo 3 alertas críticas
            if alert['type'] == 'error':
                st.error(alert['message'])
            elif alert['type'] == 'warning':
                st.warning(alert['message'])
            else:
                st.info(alert['message'])
        
        # Notificación de estado general
        if not alerts:
            if metrics['total_return_pct'] > 5:
                st.success("🎉 ¡Excelente performance! El portfolio está generando buenos retornos.")
            elif metrics['total_return_pct'] > 0:
                st.info("📈 Performance positiva. El portfolio está en territorio ganador.")
 
    def _get_trading_mode_info(self) -> Dict:
        """Obtener información del modo de trading actual"""
        try:
            # Usar configuración centralizada
            current_profile_cfg = TradingProfiles.get_current_profile()
            profile_name = current_profile_cfg.get('name', TRADING_PROFILE)
            max_positions = TradingBotConfig.get_max_concurrent_positions()
            min_confidence = RiskManagerConfig.get_min_confidence_threshold()
            return {
                'mode': 'PAPER_TRADING' if USE_PAPER_TRADING else 'REAL_TRADING',
                'profile': profile_name,
                'description': f'Trading con perfil {profile_name}',
                'risk_level': self._get_profile_risk_level(profile_name),
                'max_positions': max_positions,
                'min_confidence': min_confidence
            }
        except Exception as e:
            print(f"Error obteniendo trading mode info: {e}")
            return {
                'mode': 'PAPER_TRADING' if USE_PAPER_TRADING else 'REAL_TRADING',
                'profile': TRADING_PROFILE,
                'description': 'Modo de trading virtual para pruebas',
                'risk_level': self._get_profile_risk_level(TRADING_PROFILE),
                'max_positions': TradingBotConfig.get_max_concurrent_positions(),
                'min_confidence': RiskManagerConfig.get_min_confidence_threshold()
            }
    
    def _get_profile_risk_level(self, profile: str) -> str:
        """Obtener nivel de riesgo del perfil"""
        risk_levels = {
            "CONSERVADOR": "LOW",
            "ÓPTIMO": "MEDIUM",
            "AGRESIVO": "HIGH",
            "RÁPIDO": "VERY_HIGH"
        }
        return risk_levels.get(profile, "MEDIUM")
    
    def stop_dashboard(self):
        """Detener dashboard"""
        self.is_running = False
        st.session_state.is_running = False
        print("📊 Dashboard detenido")
    
    def update_data_from_dict(self, trading_data: Dict[str, Any]):
        """Actualizar datos del dashboard desde diccionario"""
        # Agregar timestamp
        trading_data['timestamp'] = datetime.now()
        
        # Agregar a historial
        self.data_history.append(trading_data.copy())
        st.session_state.data_history = self.data_history
        
        # Mantener solo los últimos N registros
        max_history = getattr(self.config, 'MAX_HISTORY_RECORDS', 1000)
        if len(self.data_history) > max_history:
            self.data_history = self.data_history[-max_history:]
            st.session_state.data_history = self.data_history
        
        self.last_update = datetime.now()
        st.session_state.last_update = self.last_update
    
    def get_current_status(self) -> Dict:
        """Obtener estado actual del dashboard"""
        return {
            'is_running': self.is_running,
            'last_update': self.last_update,
            'metrics': self.metrics_calc.get_current_metrics(),
            'data_points': len(self.metrics_calc.equity_history)
        }
    
    def _render_leverage_section(self):
        """Renderizar sección de configuración de trading"""
        st.subheader("⚡ Configuración de Trading")
        
        # Obtener información del modo de trading
        trading_info = self._get_trading_mode_info()
        
        # Mostrar configuración actual
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Configuración Actual:**")
            st.write(f"• Modo: {trading_info['mode']}")
            st.write(f"• Perfil: {trading_info['profile']}")
            st.write(f"• Nivel de Riesgo: {trading_info['risk_level']}")
        
        with col2:
            st.write("**Límites:**")
            st.write(f"• Posiciones Máximas: {trading_info['max_positions']}")
            st.write(f"• Confianza Mínima: {trading_info['min_confidence']:.1f}%")
            # Balance inicial desde DB
            portfolio_summary = self.metrics_calc.get_portfolio_summary()
            initial_balance_db = portfolio_summary.get('initial_balance', 0.0)
            st.write(f"• Balance Inicial: ${initial_balance_db:,.2f}")
        
        # Métricas de configuración
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Número de símbolos configurados desde configuración centralizada
            total_symbols = len(TradingBotConfig.SYMBOLS)
            st.metric("Símbolos Configurados", total_symbols)
        
        with col2:
            # Mostrar balance inicial desde DB
            st.metric("Balance Inicial", f"${initial_balance_db:,.0f}")
        
        with col3:
            # Obtener posiciones activas desde la base de datos
            active_trades = self.metrics_calc.get_active_trades()
            st.metric("Posiciones Activas", len(active_trades))
        
        # Gráfico de distribución de estrategias (config centralizada)
        try:
            strategy_weights = getattr(StrategyConfig.Ensemble, 'STRATEGY_WEIGHTS', None)
            if strategy_weights:
                strategy_names = list(strategy_weights.keys())
                strategy_values = list(strategy_weights.values())
                fig_strategies = go.Figure(data=[
                    go.Pie(
                        labels=strategy_names,
                        values=strategy_values,
                        hole=0.4,
                        marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                    )
                ])
                fig_strategies.update_layout(
                    title="Distribución de Estrategias Configuradas",
                    template='plotly_dark',
                    height=300,
                    showlegend=True
                )
                st.plotly_chart(fig_strategies, width='stretch')
            else:
                st.info("No hay estrategias configuradas")
        except Exception:
            st.info("No hay estrategias configuradas")
    
    def _render_trailing_sl_section(self):
        """Renderizar sección de gestión de riesgo"""
        st.subheader("🎯 Gestión de Riesgo")
        
        # Obtener parámetros de riesgo desde configuración centralizada
        try:
            sl_pct = RiskManagerConfig.get_sl_min_percentage()
            tp_pct = RiskManagerConfig.get_tp_min_percentage()
            max_drawdown_pct = RiskManagerConfig.get_max_drawdown_threshold() * 100.0
            position_size_pct = PaperTraderConfig.get_max_position_size() * 100.0
        except Exception:
            sl_pct = 2.0
            tp_pct = 4.0
            max_drawdown_pct = 10.0
            position_size_pct = 20.0
        
        # Mostrar configuración de riesgo
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Stop Loss:**")
            st.write(f"• Stop Loss: {sl_pct:.1f}%")
            st.write(f"• Take Profit: {tp_pct:.1f}%")
        
        with col2:
            st.write("**Gestión de Posición:**")
            st.write(f"• Tamaño Posición: {position_size_pct:.1f}%")
            st.write(f"• Max Drawdown: {max_drawdown_pct:.1f}%")
        
        # Obtener posiciones activas
        active_trades = self.metrics_calc.get_active_trades()
        
        # Tabla de posiciones activas
        if active_trades:
            df_active = pd.DataFrame(active_trades)
            
            # Formatear columnas si existen
            if not df_active.empty:
                if 'entry_price' in df_active.columns:
                    df_active['entry_price'] = df_active['entry_price'].apply(lambda x: f"${x:,.4f}")
                if 'quantity' in df_active.columns:
                    df_active['quantity'] = df_active['quantity'].apply(lambda x: f"{x:.6f}")
            
            st.dataframe(
                df_active[['symbol', 'type', 'entry_price', 'quantity', 'strategy', 'status']],
                width='stretch',
                hide_index=True
            )
        else:
            st.info("No hay posiciones activas")
        
        # Métricas de riesgo
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Posiciones Activas", len(active_trades))
        
        with col2:
            # Calcular PnL promedio de trades cerrados
            closed_trades = self.metrics_calc.get_closed_trades(limit=10)
            if closed_trades:
                avg_pnl = sum(trade.get('pnl', 0) for trade in closed_trades) / len(closed_trades)
                st.metric("PnL Promedio", f"${avg_pnl:.2f}")
            else:
                st.metric("PnL Promedio", "$0.00")
        
        with col3:
            # Mostrar balance disponible
            portfolio_summary = self.metrics_calc.get_portfolio_summary()
            available_balance = portfolio_summary.get('available_balance', 0)
            st.metric("Balance Disponible", f"${available_balance:,.2f}")
        
        # Gráfico de distribución de PnL
        closed_trades = self.metrics_calc.get_closed_trades(limit=50)
        if closed_trades:
            pnl_values = [trade.get('pnl', 0) for trade in closed_trades]
            
            fig_pnl = go.Figure()
            
            # Histograma de PnL
            fig_pnl.add_trace(go.Histogram(
                x=pnl_values,
                nbinsx=20,
                name='Distribución PnL',
                marker_color='#1f77b4',
                opacity=0.7
            ))
            
            fig_pnl.update_layout(
                title="Distribución de PnL por Trade",
                xaxis_title="PnL ($)",
                yaxis_title="Frecuencia",
                template='plotly_dark',
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig_pnl, width='stretch')
        else:
            st.info("No hay suficientes trades para mostrar distribución")
        
        # Configuración de gestión de riesgo
        with st.expander("⚙️ Configuración de Gestión de Riesgo"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Parámetros de Riesgo:**")
                st.write(f"• Stop Loss: {RiskManagerConfig.get_sl_min_percentage():.1f}%")
                st.write(f"• Take Profit: {RiskManagerConfig.get_tp_min_percentage():.1f}%")
                st.write(f"• Max Drawdown: {RiskManagerConfig.get_max_drawdown_threshold() * 100.0:.1f}%")
            
            with col2:
                st.write("**Configuración de Posición:**")
                st.write(f"• Tamaño: {PaperTraderConfig.get_max_position_size() * 100.0:.1f}% del balance")
                st.write(f"• Posiciones máximas: {TradingBotConfig.get_max_concurrent_positions()}")
                st.write(f"• Estado: {'Activo' if USE_PAPER_TRADING else 'Inactivo'}")



# Función principal para ejecutar el dashboard
def main():
    """Función principal del dashboard"""
    dashboard = RealTimeDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
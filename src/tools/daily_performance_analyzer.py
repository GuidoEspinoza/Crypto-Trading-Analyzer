#!/usr/bin/env python3
"""
📊 ANALIZADOR DE PERFORMANCE DIARIA
==================================

Script completo para analizar la performance del trading bot durante el día.
Incluye métricas de trades, estrategias, riesgo y visualizaciones.

Uso:
    python3 daily_performance_analyzer.py                    # Análisis del día actual
    python3 daily_performance_analyzer.py --date 2024-01-15  # Análisis de fecha específica
    python3 daily_performance_analyzer.py --export           # Exportar reporte a archivo
    python3 daily_performance_analyzer.py --visual           # Incluir gráficos
"""

import sys
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

from src.database import DatabaseManager, Trade, Portfolio, Strategy, TradingSignal
from src.config.global_constants import GLOBAL_INITIAL_BALANCE

@dataclass
class DailyMetrics:
    """📊 Métricas diarias del trading bot"""
    date: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_percentage: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    total_volume: float
    active_positions: int
    portfolio_value: float
    drawdown: float
    sharpe_ratio: Optional[float]
    strategy_performance: Dict[str, Dict[str, Any]]
    hourly_pnl: Dict[str, float]
    signal_accuracy: Dict[str, float]

class DailyPerformanceAnalyzer:
    """🔍 Analizador completo de performance diaria"""
    
    def __init__(self, date: Optional[str] = None):
        """
        Inicializar analizador
        
        Args:
            date: Fecha a analizar (YYYY-MM-DD). Si es None, usa fecha actual
        """
        self.db_manager = DatabaseManager()
        self.target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.now().date()
        self.start_datetime = datetime.combine(self.target_date, datetime.min.time())
        self.end_datetime = datetime.combine(self.target_date, datetime.max.time())
        
        # Configurar estilo de gráficos
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        print(f"📅 Analizando performance del {self.target_date.strftime('%Y-%m-%d')}")
    
    def analyze_daily_trades(self) -> Dict[str, Any]:
        """📈 Analizar todos los trades del día"""
        print("🔍 Analizando trades del día...")
        
        try:
            with self.db_manager.get_db_session() as session:
                # Obtener trades del día
                trades = session.query(Trade).filter(
                    Trade.entry_time >= self.start_datetime,
                    Trade.entry_time <= self.end_datetime,
                    Trade.is_paper_trade == True  # Enfocarse en paper trading
                ).all()
                
                if not trades:
                    return {
                        'total_trades': 0,
                        'message': 'No se encontraron trades para esta fecha'
                    }
                
                # Métricas básicas
                total_trades = len(trades)
                closed_trades = [t for t in trades if t.status == 'CLOSED' and t.pnl is not None]
                winning_trades = [t for t in closed_trades if t.pnl > 0]
                losing_trades = [t for t in closed_trades if t.pnl < 0]
                
                # Calcular métricas
                win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
                total_pnl = sum(t.pnl for t in closed_trades)
                gross_profit = sum(t.pnl for t in winning_trades)
                gross_loss = abs(sum(t.pnl for t in losing_trades))
                
                # Profit factor: manejar casos especiales
                if gross_loss > 0:
                    profit_factor = gross_profit / gross_loss
                elif gross_profit > 0:
                    profit_factor = float('inf')  # Solo ganancias, sin pérdidas
                else:
                    profit_factor = 0  # Sin ganancias ni pérdidas
                
                # Métricas de wins/losses
                avg_win = (gross_profit / len(winning_trades)) if winning_trades else 0
                avg_loss = (gross_loss / len(losing_trades)) if losing_trades else 0
                largest_win = max((t.pnl for t in winning_trades), default=0)
                largest_loss = min((t.pnl for t in losing_trades), default=0)
                
                # Volumen total
                total_volume = sum(t.entry_value for t in trades)
                
                # Análisis por hora
                hourly_pnl = {}
                for trade in closed_trades:
                    hour = trade.entry_time.strftime('%H:00')
                    hourly_pnl[hour] = hourly_pnl.get(hour, 0) + trade.pnl
                
                return {
                    'total_trades': total_trades,
                    'closed_trades': len(closed_trades),
                    'open_trades': total_trades - len(closed_trades),
                    'winning_trades': len(winning_trades),
                    'losing_trades': len(losing_trades),
                    'win_rate': win_rate,
                    'total_pnl': total_pnl,
                    'total_pnl_percentage': (total_pnl / GLOBAL_INITIAL_BALANCE * 100) if total_pnl else 0,
                    'gross_profit': gross_profit,
                    'gross_loss': gross_loss,
                    'profit_factor': profit_factor,
                    'avg_win': avg_win,
                    'avg_loss': avg_loss,
                    'largest_win': largest_win,
                    'largest_loss': largest_loss,
                    'total_volume': total_volume,
                    'hourly_pnl': hourly_pnl,
                    'trades_data': [
                        {
                            'symbol': t.symbol,
                            'strategy': t.strategy_name,
                            'type': t.trade_type,
                            'entry_price': t.entry_price,
                            'exit_price': t.exit_price,
                            'pnl': t.pnl,
                            'pnl_percentage': t.pnl_percentage,
                            'entry_time': t.entry_time.strftime('%H:%M:%S'),
                            'status': t.status
                        } for t in trades
                    ]
                }
                
        except Exception as e:
            print(f"❌ Error analizando trades: {e}")
            return {'error': str(e)}
    
    def analyze_strategy_performance(self) -> Dict[str, Dict[str, Any]]:
        """🧠 Analizar performance por estrategia"""
        print("🎯 Analizando performance por estrategia...")
        
        try:
            with self.db_manager.get_db_session() as session:
                # Obtener trades por estrategia
                trades = session.query(Trade).filter(
                    Trade.entry_time >= self.start_datetime,
                    Trade.entry_time <= self.end_datetime,
                    Trade.is_paper_trade == True,
                    Trade.status == 'CLOSED',
                    Trade.pnl.isnot(None)
                ).all()
                
                strategy_stats = {}
                
                for trade in trades:
                    strategy = trade.strategy_name
                    if strategy not in strategy_stats:
                        strategy_stats[strategy] = {
                            'trades': [],
                            'total_pnl': 0,
                            'wins': 0,
                            'losses': 0,
                            'total_volume': 0
                        }
                    
                    strategy_stats[strategy]['trades'].append(trade)
                    strategy_stats[strategy]['total_pnl'] += trade.pnl
                    strategy_stats[strategy]['total_volume'] += trade.entry_value
                    
                    if trade.pnl > 0:
                        strategy_stats[strategy]['wins'] += 1
                    else:
                        strategy_stats[strategy]['losses'] += 1
                
                # Calcular métricas finales por estrategia
                for strategy, stats in strategy_stats.items():
                    total_trades = len(stats['trades'])
                    win_rate = (stats['wins'] / total_trades * 100) if total_trades > 0 else 0
                    avg_pnl = stats['total_pnl'] / total_trades if total_trades > 0 else 0
                    
                    strategy_stats[strategy].update({
                        'total_trades': total_trades,
                        'win_rate': win_rate,
                        'avg_pnl_per_trade': avg_pnl,
                        'pnl_percentage': (stats['total_pnl'] / GLOBAL_INITIAL_BALANCE * 100) if stats['total_pnl'] else 0
                    })
                
                return strategy_stats
                
        except Exception as e:
            print(f"❌ Error analizando estrategias: {e}")
            return {}
    
    def analyze_portfolio_status(self) -> Dict[str, Any]:
        """💼 Analizar estado actual del portfolio"""
        print("💼 Analizando estado del portfolio...")
        
        try:
            with self.db_manager.get_db_session() as session:
                # Portfolio actual
                portfolio_items = session.query(Portfolio).filter(
                    Portfolio.is_paper == True
                ).all()
                
                total_value = sum(p.current_value or 0 for p in portfolio_items)
                unrealized_pnl = sum(p.unrealized_pnl or 0 for p in portfolio_items)
                
                # Posiciones activas
                active_trades = session.query(Trade).filter(
                    Trade.status == 'OPEN',
                    Trade.is_paper_trade == True
                ).all()
                
                return {
                    'total_portfolio_value': total_value,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_percentage': (unrealized_pnl / GLOBAL_INITIAL_BALANCE * 100) if unrealized_pnl else 0,
                    'active_positions': len(active_trades),
                    'positions_detail': [
                        {
                            'symbol': p.symbol,
                            'quantity': p.quantity,
                            'avg_price': p.avg_price,
                            'current_value': p.current_value,
                            'unrealized_pnl': p.unrealized_pnl
                        } for p in portfolio_items if p.quantity > 0
                    ],
                    'active_trades_detail': [
                        {
                            'symbol': t.symbol,
                            'strategy': t.strategy_name,
                            'type': t.trade_type,
                            'entry_price': t.entry_price,
                            'quantity': t.quantity,
                            'entry_time': t.entry_time.strftime('%H:%M:%S')
                        } for t in active_trades
                    ]
                }
                
        except Exception as e:
            print(f"❌ Error analizando portfolio: {e}")
            return {}
    
    def analyze_signals_accuracy(self) -> Dict[str, Any]:
        """🎯 Analizar precisión de señales"""
        print("🎯 Analizando precisión de señales...")
        
        try:
            with self.db_manager.get_db_session() as session:
                # Señales del día
                signals = session.query(TradingSignal).filter(
                    TradingSignal.generated_at >= self.start_datetime,
                    TradingSignal.generated_at <= self.end_datetime
                ).all()
                
                if not signals:
                    return {'message': 'No se encontraron señales para esta fecha'}
                
                signal_stats = {
                    'total_signals': len(signals),
                    'buy_signals': len([s for s in signals if s.signal_type == 'BUY']),
                    'sell_signals': len([s for s in signals if s.signal_type == 'SELL']),
                    'executed_signals': len([s for s in signals if s.action_taken == 'EXECUTED']),
                    'ignored_signals': len([s for s in signals if s.action_taken == 'IGNORED']),
                    'by_strategy': {},
                    'by_confidence': {}
                }
                
                # Análisis por estrategia
                for signal in signals:
                    strategy = signal.strategy_name
                    if strategy not in signal_stats['by_strategy']:
                        signal_stats['by_strategy'][strategy] = {
                            'total': 0,
                            'executed': 0,
                            'avg_confidence': 0
                        }
                    
                    signal_stats['by_strategy'][strategy]['total'] += 1
                    if signal.action_taken == 'EXECUTED':
                        signal_stats['by_strategy'][strategy]['executed'] += 1
                    
                    if signal.confidence_score:
                        signal_stats['by_strategy'][strategy]['avg_confidence'] += signal.confidence_score
                
                # Calcular promedios
                for strategy_data in signal_stats['by_strategy'].values():
                    if strategy_data['total'] > 0:
                        strategy_data['execution_rate'] = (strategy_data['executed'] / strategy_data['total'] * 100)
                        strategy_data['avg_confidence'] = strategy_data['avg_confidence'] / strategy_data['total']
                
                return signal_stats
                
        except Exception as e:
            print(f"❌ Error analizando señales: {e}")
            return {}
    
    def calculate_risk_metrics(self, trades_data: Dict[str, Any]) -> Dict[str, Any]:
        """⚠️ Calcular métricas de riesgo"""
        print("⚠️ Calculando métricas de riesgo...")
        
        try:
            if not trades_data.get('trades_data'):
                return {'message': 'No hay datos de trades para calcular riesgo'}
            
            all_trades = trades_data['trades_data']
            closed_trades = [t for t in all_trades if t['pnl'] is not None and t['pnl'] != 0]
            
            if not closed_trades:
                # Si no hay trades cerrados con P&L, usar datos básicos
                return {
                    'max_drawdown': 0.0,
                    'max_drawdown_percentage': 0.0,
                    'sharpe_ratio': 0.0,
                    'volatility': 0.0,
                    'best_trade': 0.0,
                    'worst_trade': 0.0,
                    'avg_positive_trade': 0.0,
                    'avg_negative_trade': 0.0,
                    'consecutive_wins': 0,
                    'consecutive_losses': 0,
                    'message': 'Métricas basadas en datos limitados - pocos trades cerrados'
                }
            
            pnl_series = [t['pnl'] for t in closed_trades]
            
            # Drawdown máximo mejorado
            cumulative_pnl = []
            running_total = GLOBAL_INITIAL_BALANCE  # Empezar desde el balance inicial
            for pnl in pnl_series:
                running_total += pnl
                cumulative_pnl.append(running_total)
            
            peak = GLOBAL_INITIAL_BALANCE
            max_drawdown = 0
            for value in cumulative_pnl:
                if value > peak:
                    peak = value
                drawdown = peak - value
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # Calcular returns porcentuales para un Sharpe ratio más preciso
            returns = []
            for trade in closed_trades:
                if trade.get('entry_price') and trade.get('entry_price') > 0 and trade.get('quantity') and trade.get('quantity') > 0:
                    # Calcular return porcentual del trade
                    trade_return = (trade['pnl'] / (trade['entry_price'] * trade['quantity'])) * 100
                    returns.append(trade_return)
            
            if len(returns) >= 2:
                avg_return = sum(returns) / len(returns)
                std_return = (sum((x - avg_return) ** 2 for x in returns) / len(returns)) ** 0.5
                
                # Sharpe ratio con risk-free rate (asumiendo 2% anual, ~0.008% diario)
                daily_risk_free_rate = 2.0 / 252  # 2% anual / 252 días de trading
                sharpe_ratio = (avg_return - daily_risk_free_rate) / std_return if std_return > 0 else 0
            else:
                # Fallback al método anterior si no hay suficientes datos
                avg_return = sum(pnl_series) / len(pnl_series)
                std_return = (sum((x - avg_return) ** 2 for x in pnl_series) / len(pnl_series)) ** 0.5
                sharpe_ratio = avg_return / std_return if std_return > 0 else 0
            
            # Métricas adicionales
            positive_trades = [p for p in pnl_series if p > 0]
            negative_trades = [p for p in pnl_series if p < 0]
            
            return {
                'max_drawdown': max_drawdown,
                'max_drawdown_percentage': (max_drawdown / GLOBAL_INITIAL_BALANCE * 100) if max_drawdown else 0,
                'sharpe_ratio': sharpe_ratio,
                'volatility': std_return,
                'best_trade': max(pnl_series),
                'worst_trade': min(pnl_series),
                'avg_positive_trade': sum(positive_trades) / len(positive_trades) if positive_trades else 0,
                'avg_negative_trade': sum(negative_trades) / len(negative_trades) if negative_trades else 0,
                'consecutive_wins': self._calculate_consecutive_wins(pnl_series),
                'consecutive_losses': self._calculate_consecutive_losses(pnl_series)
            }
            
        except Exception as e:
            print(f"❌ Error calculando métricas de riesgo: {e}")
            return {}
    
    def _calculate_consecutive_wins(self, pnl_series: List[float]) -> int:
        """Calcular máximo de wins consecutivos"""
        max_consecutive = 0
        current_consecutive = 0
        
        for pnl in pnl_series:
            if pnl > 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def _calculate_consecutive_losses(self, pnl_series: List[float]) -> int:
        """Calcular máximo de losses consecutivos"""
        max_consecutive = 0
        current_consecutive = 0
        
        for pnl in pnl_series:
            if pnl < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def generate_visual_report(self, analysis_data: Dict[str, Any], save_path: Optional[str] = None):
        """📊 Generar reporte visual con gráficos"""
        print("📊 Generando reporte visual...")
        
        try:
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle(f'📊 Reporte de Performance Diaria - {self.target_date}', fontsize=16, fontweight='bold')
            
            # 1. P&L por hora
            if analysis_data['trades'].get('hourly_pnl'):
                hours = list(analysis_data['trades']['hourly_pnl'].keys())
                pnl_values = list(analysis_data['trades']['hourly_pnl'].values())
                
                axes[0, 0].bar(hours, pnl_values, color='green' if sum(pnl_values) > 0 else 'red', alpha=0.7)
                axes[0, 0].set_title('💰 P&L por Hora')
                axes[0, 0].set_xlabel('Hora')
                axes[0, 0].set_ylabel('P&L ($)')
                axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. Performance por estrategia
            if analysis_data['strategies']:
                strategies = list(analysis_data['strategies'].keys())
                strategy_pnl = [analysis_data['strategies'][s]['total_pnl'] for s in strategies]
                
                colors = ['green' if pnl > 0 else 'red' for pnl in strategy_pnl]
                axes[0, 1].bar(strategies, strategy_pnl, color=colors, alpha=0.7)
                axes[0, 1].set_title('🎯 P&L por Estrategia')
                axes[0, 1].set_xlabel('Estrategia')
                axes[0, 1].set_ylabel('P&L ($)')
                axes[0, 1].tick_params(axis='x', rotation=45)
            
            # 3. Win Rate por estrategia
            if analysis_data['strategies']:
                win_rates = [analysis_data['strategies'][s]['win_rate'] for s in strategies]
                
                axes[0, 2].bar(strategies, win_rates, color='blue', alpha=0.7)
                axes[0, 2].set_title('📈 Win Rate por Estrategia')
                axes[0, 2].set_xlabel('Estrategia')
                axes[0, 2].set_ylabel('Win Rate (%)')
                axes[0, 2].tick_params(axis='x', rotation=45)
                axes[0, 2].set_ylim(0, 100)
            
            # 4. Distribución de P&L
            if analysis_data['trades'].get('trades_data'):
                pnl_values = [t['pnl'] for t in analysis_data['trades']['trades_data'] if t['pnl'] is not None]
                if pnl_values:
                    axes[1, 0].hist(pnl_values, bins=20, color='purple', alpha=0.7, edgecolor='black')
                    axes[1, 0].set_title('📊 Distribución de P&L')
                    axes[1, 0].set_xlabel('P&L ($)')
                    axes[1, 0].set_ylabel('Frecuencia')
                    axes[1, 0].axvline(x=0, color='red', linestyle='--', alpha=0.8)
            
            # 5. Portfolio composition
            if analysis_data['portfolio'].get('positions_detail'):
                symbols = [p['symbol'] for p in analysis_data['portfolio']['positions_detail']]
                values = [p['current_value'] for p in analysis_data['portfolio']['positions_detail']]
                
                if symbols and values:
                    axes[1, 1].pie(values, labels=symbols, autopct='%1.1f%%', startangle=90)
                    axes[1, 1].set_title('💼 Composición del Portfolio')
            
            # 6. Métricas de riesgo
            if analysis_data.get('risk_metrics'):
                risk_data = analysis_data['risk_metrics']
                metrics = ['Sharpe Ratio', 'Max Drawdown %', 'Volatility']
                values = [
                    risk_data.get('sharpe_ratio', 0),
                    risk_data.get('max_drawdown_percentage', 0),
                    risk_data.get('volatility', 0)
                ]
                
                colors = ['green', 'red', 'orange']
                axes[1, 2].bar(metrics, values, color=colors, alpha=0.7)
                axes[1, 2].set_title('⚠️ Métricas de Riesgo')
                axes[1, 2].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"📁 Gráficos guardados en: {save_path}")
            else:
                plt.show()
            
        except Exception as e:
            print(f"❌ Error generando reporte visual: {e}")
    
    def print_summary_report(self, analysis_data: Dict[str, Any]):
        """📋 Imprimir reporte resumen en consola"""
        print("\n" + "="*80)
        print(f"📊 REPORTE DE PERFORMANCE DIARIA - {self.target_date}")
        print("="*80)
        
        # Resumen de trades
        trades = analysis_data['trades']
        print(f"\n💰 RESUMEN DE TRADES:")
        print(f"   Total trades: {trades.get('total_trades', 0)}")
        print(f"   Trades cerrados: {trades.get('closed_trades', 0)}")
        print(f"   Trades abiertos: {trades.get('open_trades', 0)}")
        print(f"   Win rate: {trades.get('win_rate', 0):.1f}%")
        print(f"   P&L total: ${trades.get('total_pnl', 0):.2f}")
        print(f"   P&L porcentaje: {trades.get('total_pnl_percentage', 0):.2f}%")
        
        # Profit factor con mejor presentación
        pf = trades.get('profit_factor', 0)
        if pf == float('inf'):
            print(f"   Profit factor: ∞ (solo ganancias)")
        elif pf == 0:
            print(f"   Profit factor: N/A (sin trades cerrados)")
        else:
            print(f"   Profit factor: {pf:.2f}")
            
        print(f"   Volumen total: ${trades.get('total_volume', 0):.2f}")
        
        # Performance por estrategia
        if analysis_data['strategies']:
            print(f"\n🎯 PERFORMANCE POR ESTRATEGIA:")
            for strategy, data in analysis_data['strategies'].items():
                print(f"   {strategy}:")
                print(f"     Trades: {data['total_trades']}")
                print(f"     Win rate: {data['win_rate']:.1f}%")
                print(f"     P&L: ${data['total_pnl']:.2f}")
                print(f"     P&L promedio: ${data['avg_pnl_per_trade']:.2f}")
        
        # Estado del portfolio
        portfolio = analysis_data['portfolio']
        print(f"\n💼 ESTADO DEL PORTFOLIO:")
        print(f"   Valor total: ${portfolio.get('total_portfolio_value', 0):.2f}")
        print(f"   P&L no realizado: ${portfolio.get('unrealized_pnl', 0):.2f}")
        print(f"   Posiciones activas: {portfolio.get('active_positions', 0)}")
        
        # Métricas de riesgo
        if analysis_data.get('risk_metrics'):
            risk = analysis_data['risk_metrics']
            print(f"\n⚠️ MÉTRICAS DE RIESGO:")
            print(f"   Max drawdown: ${risk.get('max_drawdown', 0):.2f} ({risk.get('max_drawdown_percentage', 0):.2f}%)")
            print(f"   Sharpe ratio: {risk.get('sharpe_ratio', 0):.3f}")
            print(f"   Mejor trade: ${risk.get('best_trade', 0):.2f}")
            print(f"   Peor trade: ${risk.get('worst_trade', 0):.2f}")
            print(f"   Wins consecutivos máx: {risk.get('consecutive_wins', 0)}")
            print(f"   Losses consecutivos máx: {risk.get('consecutive_losses', 0)}")
        
        # Señales
        if analysis_data.get('signals') and 'total_signals' in analysis_data['signals']:
            signals = analysis_data['signals']
            print(f"\n🎯 ANÁLISIS DE SEÑALES:")
            print(f"   Total señales: {signals['total_signals']}")
            print(f"   Señales ejecutadas: {signals['executed_signals']}")
            print(f"   Tasa de ejecución: {(signals['executed_signals']/signals['total_signals']*100):.1f}%")
        
        print("\n" + "="*80)
    
    def export_report(self, analysis_data: Dict[str, Any], filename: Optional[str] = None):
        """💾 Exportar reporte a archivo JSON"""
        if not filename:
            filename = f"daily_report_{self.target_date.strftime('%Y%m%d')}.json"
        
        try:
            # Preparar datos para exportación
            export_data = {
                'date': self.target_date.strftime('%Y-%m-%d'),
                'generated_at': datetime.now().isoformat(),
                'analysis': analysis_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"📁 Reporte exportado a: {filename}")
            
        except Exception as e:
            print(f"❌ Error exportando reporte: {e}")
    
    def run_complete_analysis(self, export: bool = False, visual: bool = False, export_filename: Optional[str] = None) -> Dict[str, Any]:
        """🚀 Ejecutar análisis completo"""
        print(f"\n🚀 Iniciando análisis completo para {self.target_date}")
        print("="*60)
        
        # Ejecutar todos los análisis
        analysis_data = {
            'trades': self.analyze_daily_trades(),
            'strategies': self.analyze_strategy_performance(),
            'portfolio': self.analyze_portfolio_status(),
            'signals': self.analyze_signals_accuracy()
        }
        
        # Calcular métricas de riesgo
        analysis_data['risk_metrics'] = self.calculate_risk_metrics(analysis_data['trades'])
        
        # Mostrar reporte en consola
        self.print_summary_report(analysis_data)
        
        # Generar visualizaciones si se solicita
        if visual:
            visual_filename = f"daily_performance_{self.target_date.strftime('%Y%m%d')}.png"
            self.generate_visual_report(analysis_data, visual_filename)
        
        # Exportar si se solicita
        if export:
            self.export_report(analysis_data, export_filename)
        
        return analysis_data

def main():
    """🎯 Función principal"""
    parser = argparse.ArgumentParser(description='📊 Analizador de Performance Diaria del Trading Bot')
    parser.add_argument('--date', type=str, help='Fecha a analizar (YYYY-MM-DD). Por defecto: hoy')
    parser.add_argument('--export', action='store_true', help='Exportar reporte a archivo JSON')
    parser.add_argument('--visual', action='store_true', help='Generar gráficos visuales')
    parser.add_argument('--output', type=str, help='Nombre del archivo de salida')
    
    args = parser.parse_args()
    
    try:
        # Crear analizador
        analyzer = DailyPerformanceAnalyzer(args.date)
        
        # Ejecutar análisis completo
        analysis_data = analyzer.run_complete_analysis(
            export=args.export,
            visual=args.visual,
            export_filename=args.output
        )
        
        print("\n✅ Análisis completado exitosamente!")
        
        # Mostrar recomendaciones
        if analysis_data['trades'].get('total_trades', 0) > 0:
            print("\n💡 RECOMENDACIONES:")
            
            win_rate = analysis_data['trades'].get('win_rate', 0)
            if win_rate < 50:
                print("   ⚠️ Win rate bajo - revisar estrategias y filtros de entrada")
            
            profit_factor = analysis_data['trades'].get('profit_factor', 0)
            if profit_factor < 1.5:
                print("   ⚠️ Profit factor bajo - optimizar gestión de riesgo")
            
            if analysis_data.get('risk_metrics', {}).get('max_drawdown_percentage', 0) > 5:
                print("   ⚠️ Drawdown alto - considerar reducir tamaño de posiciones")
            
            if analysis_data['trades'].get('total_pnl', 0) > 0:
                print("   ✅ Día rentable - mantener estrategias actuales")
        
    except Exception as e:
        print(f"❌ Error en el análisis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
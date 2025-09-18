#!/usr/bin/env python3
"""
📊 Sharpe Ratio Analyzer - Crypto Trading Analyzer
Analiza y corrige discrepancias en el cálculo del Sharpe ratio entre dashboard y script diario
"""

import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import numpy as np

# Agregar src al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root)

from src.database.database import db_manager
from src.database.models import Trade, Portfolio
from src.config.global_constants import GLOBAL_INITIAL_BALANCE

class SharpeRatioAnalyzer:
    """Analizador de Sharpe ratio para identificar discrepancias"""
    
    def __init__(self):
        self.initial_balance = GLOBAL_INITIAL_BALANCE
        
    def analyze_dashboard_calculation(self) -> Dict[str, Any]:
        """Analiza cómo calcula el Sharpe ratio el dashboard"""
        print("🔍 Analizando cálculo del Dashboard...")
        
        try:
            with db_manager.get_db_session() as session:
                # Obtener datos de portfolio (como hace el dashboard)
                portfolios = session.query(Portfolio).order_by(Portfolio.last_updated).all()
                
                if len(portfolios) < 2:
                    return {
                        'method': 'Dashboard (equity_history)',
                        'data_points': len(portfolios),
                        'sharpe_ratio': 0.0,
                        'error': 'Insuficientes datos de equity history'
                    }
                
                # Simular equity_history del dashboard
                equity_values = []
                for p in portfolios:
                    # Sumar valor total del portfolio en cada momento
                    total_value = p.current_value or 0
                    equity_values.append(total_value)
                
                # Si solo tenemos valores individuales, necesitamos simular el total
                if len(equity_values) < 2:
                    return {
                        'method': 'Dashboard (equity_history)',
                        'data_points': len(equity_values),
                        'sharpe_ratio': 0.0,
                        'error': 'Insuficientes puntos de equity'
                    }
                
                # Calcular returns como en el dashboard
                returns = []
                for i in range(1, len(equity_values)):
                    if equity_values[i-1] > 0:
                        ret = (equity_values[i] - equity_values[i-1]) / equity_values[i-1]
                        returns.append(ret)
                
                if len(returns) < 2:
                    return {
                        'method': 'Dashboard (equity_history)',
                        'data_points': len(returns),
                        'sharpe_ratio': 0.0,
                        'error': 'Insuficientes returns calculados'
                    }
                
                # Volatilidad anualizada (como en dashboard)
                volatility = np.std(returns) * np.sqrt(252) * 100  # Anualizada en %
                
                # Total return
                total_return = ((equity_values[-1] - equity_values[0]) / equity_values[0]) * 100
                
                # Sharpe ratio (como en dashboard)
                risk_free_rate = 2.0  # 2%
                sharpe_ratio = (total_return - risk_free_rate) / volatility if volatility > 0 else 0
                
                return {
                    'method': 'Dashboard (equity_history)',
                    'data_points': len(returns),
                    'equity_values': equity_values,
                    'returns': returns,
                    'total_return_pct': total_return,
                    'volatility_pct': volatility,
                    'risk_free_rate': risk_free_rate,
                    'sharpe_ratio': sharpe_ratio,
                    'formula': '(total_return - risk_free_rate) / volatility_anualizada'
                }
                
        except Exception as e:
            return {
                'method': 'Dashboard (equity_history)',
                'error': str(e),
                'sharpe_ratio': 0.0
            }
    
    def analyze_script_calculation(self) -> Dict[str, Any]:
        """Analiza cómo calcula el Sharpe ratio el script diario"""
        print("🔍 Analizando cálculo del Script Diario...")
        
        try:
            with db_manager.get_db_session() as session:
                # Obtener trades del día (como hace el script)
                today = date.today()
                trades_today = session.query(Trade).filter(
                    Trade.entry_time >= datetime.combine(today, datetime.min.time())
                ).all()
                
                closed_trades = [t for t in trades_today if t.status == 'CLOSED']
                
                if len(closed_trades) < 2:
                    return {
                        'method': 'Script Diario (trades PnL)',
                        'data_points': len(closed_trades),
                        'sharpe_ratio': 0.0,
                        'error': 'Insuficientes trades cerrados'
                    }
                
                # PnL series (como en script)
                pnl_series = [t.pnl for t in closed_trades if t.pnl is not None]
                
                if len(pnl_series) < 2:
                    return {
                        'method': 'Script Diario (trades PnL)',
                        'data_points': len(pnl_series),
                        'sharpe_ratio': 0.0,
                        'error': 'Insuficientes valores de PnL'
                    }
                
                # Sharpe ratio simplificado (como en script)
                avg_return = sum(pnl_series) / len(pnl_series)
                std_return = (sum((x - avg_return) ** 2 for x in pnl_series) / len(pnl_series)) ** 0.5
                sharpe_ratio = avg_return / std_return if std_return > 0 else 0
                
                return {
                    'method': 'Script Diario (trades PnL)',
                    'data_points': len(pnl_series),
                    'pnl_series': pnl_series,
                    'avg_return': avg_return,
                    'std_return': std_return,
                    'sharpe_ratio': sharpe_ratio,
                    'formula': 'avg_pnl / std_pnl (sin risk-free rate)'
                }
                
        except Exception as e:
            return {
                'method': 'Script Diario (trades PnL)',
                'error': str(e),
                'sharpe_ratio': 0.0
            }
    
    def calculate_correct_sharpe_ratio(self) -> Dict[str, Any]:
        """Calcula el Sharpe ratio correcto usando mejores prácticas"""
        print("✅ Calculando Sharpe ratio correcto...")
        
        try:
            with db_manager.get_db_session() as session:
                # Obtener todos los trades cerrados (no solo del día)
                closed_trades = session.query(Trade).filter(
                    Trade.status == 'CLOSED',
                    Trade.pnl.isnot(None)
                ).order_by(Trade.exit_time).all()
                
                if len(closed_trades) < 10:  # Mínimo para cálculo confiable
                    return {
                        'method': 'Correcto (histórico)',
                        'sharpe_ratio': 0.0,
                        'error': f'Insuficientes trades históricos: {len(closed_trades)}'
                    }
                
                # Usar returns porcentuales en lugar de PnL absoluto
                returns = []
                for trade in closed_trades:
                    if trade.entry_price and trade.entry_price > 0:
                        # Return porcentual del trade
                        trade_return = (trade.pnl / (trade.entry_price * trade.quantity)) * 100
                        returns.append(trade_return)
                
                if len(returns) < 10:
                    return {
                        'method': 'Correcto (histórico)',
                        'sharpe_ratio': 0.0,
                        'error': f'Insuficientes returns válidos: {len(returns)}'
                    }
                
                # Calcular métricas
                avg_return = np.mean(returns)
                std_return = np.std(returns, ddof=1)  # Sample standard deviation
                
                # Sharpe ratio anualizado
                # Asumiendo trading diario, anualizamos
                trading_days_per_year = 252
                avg_return_annualized = avg_return * trading_days_per_year
                std_return_annualized = std_return * np.sqrt(trading_days_per_year)
                
                risk_free_rate = 2.0  # 2% anual
                sharpe_ratio = (avg_return_annualized - risk_free_rate) / std_return_annualized if std_return_annualized > 0 else 0
                
                return {
                    'method': 'Correcto (histórico anualizado)',
                    'data_points': len(returns),
                    'avg_return_daily': avg_return,
                    'std_return_daily': std_return,
                    'avg_return_annualized': avg_return_annualized,
                    'std_return_annualized': std_return_annualized,
                    'risk_free_rate': risk_free_rate,
                    'sharpe_ratio': sharpe_ratio,
                    'formula': '(avg_return_anual - risk_free_rate) / std_return_anual'
                }
                
        except Exception as e:
            return {
                'method': 'Correcto (histórico)',
                'error': str(e),
                'sharpe_ratio': 0.0
            }
    
    def run_analysis(self) -> Dict[str, Any]:
        """Ejecuta análisis completo"""
        print("📊 ANÁLISIS DE SHARPE RATIO")
        print("=" * 50)
        
        # Analizar ambos métodos
        dashboard_result = self.analyze_dashboard_calculation()
        script_result = self.analyze_script_calculation()
        correct_result = self.calculate_correct_sharpe_ratio()
        
        # Mostrar resultados
        print(f"\n🖥️  DASHBOARD: {dashboard_result['sharpe_ratio']:.4f}")
        print(f"   Método: {dashboard_result.get('method', 'N/A')}")
        print(f"   Fórmula: {dashboard_result.get('formula', 'N/A')}")
        if 'error' in dashboard_result:
            print(f"   ⚠️  Error: {dashboard_result['error']}")
        
        print(f"\n📄 SCRIPT DIARIO: {script_result['sharpe_ratio']:.4f}")
        print(f"   Método: {script_result.get('method', 'N/A')}")
        print(f"   Fórmula: {script_result.get('formula', 'N/A')}")
        if 'error' in script_result:
            print(f"   ⚠️  Error: {script_result['error']}")
        
        print(f"\n✅ CORRECTO: {correct_result['sharpe_ratio']:.4f}")
        print(f"   Método: {correct_result.get('method', 'N/A')}")
        print(f"   Fórmula: {correct_result.get('formula', 'N/A')}")
        if 'error' in correct_result:
            print(f"   ⚠️  Error: {correct_result['error']}")
        
        # Análisis de discrepancias
        print(f"\n🔍 ANÁLISIS DE DISCREPANCIAS:")
        print(f"   Dashboard vs Script: {abs(dashboard_result['sharpe_ratio'] - script_result['sharpe_ratio']):.4f}")
        print(f"   Dashboard vs Correcto: {abs(dashboard_result['sharpe_ratio'] - correct_result['sharpe_ratio']):.4f}")
        print(f"   Script vs Correcto: {abs(script_result['sharpe_ratio'] - correct_result['sharpe_ratio']):.4f}")
        
        return {
            'dashboard': dashboard_result,
            'script': script_result,
            'correct': correct_result,
            'recommendation': self._get_recommendation(dashboard_result, script_result, correct_result)
        }
    
    def _get_recommendation(self, dashboard: Dict, script: Dict, correct: Dict) -> str:
        """Genera recomendación basada en el análisis"""
        if 'error' in correct:
            return "Insuficientes datos para determinar el valor correcto"
        
        dashboard_diff = abs(dashboard['sharpe_ratio'] - correct['sharpe_ratio'])
        script_diff = abs(script['sharpe_ratio'] - correct['sharpe_ratio'])
        
        if dashboard_diff < script_diff:
            return "El dashboard está más cerca del valor correcto"
        elif script_diff < dashboard_diff:
            return "El script diario está más cerca del valor correcto"
        else:
            return "Ambos métodos tienen similar precisión"

def main():
    """Función principal"""
    analyzer = SharpeRatioAnalyzer()
    results = analyzer.run_analysis()
    
    print(f"\n💡 RECOMENDACIÓN: {results['recommendation']}")
    print("\n" + "=" * 50)
    
    return 0

if __name__ == "__main__":
    exit(main())
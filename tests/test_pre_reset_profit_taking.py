#!/usr/bin/env python3
"""
🧪 Pruebas unitarias para la funcionalidad de cierre automático de posiciones rentables antes del reset

Este módulo contiene pruebas para verificar que el sistema de cierre automático
de posiciones rentables funcione correctamente 15 minutos antes del reset diario.
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock de configuraciones antes de importar
with patch('src.config.main_config.DAILY_RESET_HOUR', 11), \
     patch('src.config.main_config.DAILY_RESET_MINUTE', 0), \
     patch('src.config.main_config.TIMEZONE', 'America/Santiago'):
    
    # Mock de TradingSignal y otros componentes
    sys.modules['src.config.main_config'] = MagicMock()
    sys.modules['src.utils.market_hours'] = MagicMock()
    
    from src.core.trading_bot import TradingBot


class TestPreResetProfitTaking(unittest.TestCase):
    """Pruebas para el cierre automático de posiciones rentables antes del reset"""
    
    def setUp(self):
        """Configurar el entorno de pruebas"""
        # Mock del capital client
        self.mock_capital_client = Mock()
        
        # Crear instancia del bot con mocks
        with patch('src.core.trading_bot.create_capital_client_from_env') as mock_create_client:
            mock_create_client.return_value = self.mock_capital_client
            self.bot = TradingBot()
            self.bot.capital_client = self.mock_capital_client
    
    def test_get_profitable_positions_success(self):
        """Probar que se obtienen correctamente las posiciones rentables"""
        # Mock de respuesta de Capital.com con posiciones rentables
        mock_positions_response = {
            "success": True,
            "positions": [
                {
                    "market": {"epic": "BTCUSD"},
                    "position": {
                        "dealId": "DEAL123",
                        "direction": "BUY",
                        "size": 0.1,
                        "level": 50000.0,
                        "upl": 150.50,  # Ganancia > 1
                        "currency": "USD"
                    }
                },
                {
                    "market": {"epic": "ETHUSD"},
                    "position": {
                        "dealId": "DEAL456",
                        "direction": "SELL",
                        "size": 0.5,
                        "level": 3000.0,
                        "upl": 75.25,  # Ganancia > 1
                        "currency": "USD"
                    }
                },
                {
                    "market": {"epic": "XRPUSD"},
                    "position": {
                        "dealId": "DEAL789",
                        "direction": "BUY",
                        "size": 100.0,
                        "level": 0.5,
                        "upl": 0.50,  # Ganancia < 1 (no debe incluirse)
                        "currency": "USD"
                    }
                }
            ]
        }
        
        self.mock_capital_client.get_positions.return_value = mock_positions_response
        
        # Ejecutar el método
        profitable_positions = self.bot.get_profitable_positions(min_profit=1.0)
        
        # Verificaciones
        self.assertEqual(len(profitable_positions), 2)  # Solo 2 posiciones rentables
        
        # Verificar primera posición
        self.assertEqual(profitable_positions[0]["deal_id"], "DEAL123")
        self.assertEqual(profitable_positions[0]["epic"], "BTCUSD")
        self.assertEqual(profitable_positions[0]["upl"], 150.50)
        
        # Verificar segunda posición
        self.assertEqual(profitable_positions[1]["deal_id"], "DEAL456")
        self.assertEqual(profitable_positions[1]["epic"], "ETHUSD")
        self.assertEqual(profitable_positions[1]["upl"], 75.25)
    
    def test_get_profitable_positions_no_capital_client(self):
        """Probar comportamiento cuando no hay cliente de Capital.com"""
        self.bot.capital_client = None
        
        profitable_positions = self.bot.get_profitable_positions()
        
        self.assertEqual(len(profitable_positions), 0)
    
    def test_get_profitable_positions_api_error(self):
        """Probar comportamiento cuando la API de Capital.com falla"""
        self.mock_capital_client.get_positions.return_value = {
            "success": False,
            "error": "API Error"
        }
        
        profitable_positions = self.bot.get_profitable_positions()
        
        self.assertEqual(len(profitable_positions), 0)
    
    def test_close_profitable_positions_success(self):
        """Probar el cierre exitoso de posiciones rentables"""
        # Mock de posiciones rentables
        mock_profitable_positions = [
            {
                "deal_id": "DEAL123",
                "epic": "BTCUSD",
                "direction": "BUY",
                "size": 0.1,
                "entry_level": 50000.0,
                "upl": 150.50,
                "currency": "USD"
            },
            {
                "deal_id": "DEAL456",
                "epic": "ETHUSD",
                "direction": "SELL",
                "size": 0.5,
                "entry_level": 3000.0,
                "upl": 75.25,
                "currency": "USD"
            }
        ]
        
        # Mock del método get_profitable_positions
        with patch.object(self.bot, 'get_profitable_positions', return_value=mock_profitable_positions):
            # Mock de respuestas exitosas de cierre
            self.mock_capital_client.close_position.return_value = {"success": True}
            
            # Ejecutar el método
            result = self.bot.close_profitable_positions(min_profit=1.0)
            
            # Verificaciones
            self.assertTrue(result["success"])
            self.assertEqual(result["positions_found"], 2)
            self.assertEqual(result["positions_closed"], 2)
            self.assertEqual(result["total_profit_realized"], 225.75)  # 150.50 + 75.25
            
            # Verificar que se llamó close_position para cada posición
            self.assertEqual(self.mock_capital_client.close_position.call_count, 2)
    
    def test_close_profitable_positions_partial_failure(self):
        """Probar el cierre con fallos parciales"""
        # Mock de posiciones rentables
        mock_profitable_positions = [
            {
                "deal_id": "DEAL123",
                "epic": "BTCUSD",
                "upl": 150.50
            },
            {
                "deal_id": "DEAL456",
                "epic": "ETHUSD",
                "upl": 75.25
            }
        ]
        
        with patch.object(self.bot, 'get_profitable_positions', return_value=mock_profitable_positions):
            # Mock de respuestas mixtas (una exitosa, una fallida)
            self.mock_capital_client.close_position.side_effect = [
                {"success": True},  # Primera posición exitosa
                {"success": False, "error": "Position not found"}  # Segunda posición falla
            ]
            
            result = self.bot.close_profitable_positions(min_profit=1.0)
            
            # Verificaciones
            self.assertTrue(result["success"])  # Parcialmente exitoso
            self.assertEqual(result["positions_found"], 2)
            self.assertEqual(result["positions_closed"], 1)
            self.assertEqual(result["total_profit_realized"], 150.50)
            self.assertEqual(len(result["failed_closes"]), 1)
    
    def test_close_profitable_positions_no_positions(self):
        """Probar comportamiento cuando no hay posiciones rentables"""
        with patch.object(self.bot, 'get_profitable_positions', return_value=[]):
            result = self.bot.close_profitable_positions(min_profit=1.0)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["positions_found"], 0)
            self.assertEqual(result["positions_closed"], 0)
            self.assertEqual(result["total_profit_realized"], 0.0)
    
    def test_schedule_pre_reset_profit_taking(self):
        """Probar que el método de programación no lance errores"""
        try:
            # Ejecutar el método - debería funcionar sin errores
            self.bot.schedule_pre_reset_profit_taking()
            # Si llegamos aquí, el método funcionó correctamente
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"schedule_pre_reset_profit_taking() lanzó una excepción: {e}")

    def test_schedule_pre_reset_profit_taking_midnight_edge_case(self):
        """Probar que el método maneja correctamente el caso límite de medianoche"""
        with patch('src.core.trading_bot.DAILY_RESET_HOUR', 0), \
             patch('src.core.trading_bot.DAILY_RESET_MINUTE', 10):
            
            try:
                # Ejecutar el método - debería manejar el caso límite sin errores
                self.bot.schedule_pre_reset_profit_taking()
                # Si llegamos aquí, el método funcionó correctamente
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"schedule_pre_reset_profit_taking() falló en caso límite: {e}")
    
    def test_execute_pre_reset_profit_taking_success(self):
        """Probar la ejecución del cierre automático"""
        mock_result = {
            "success": True,
            "positions_closed": 3,
            "total_profit_realized": 250.75
        }
        
        with patch.object(self.bot, 'close_profitable_positions', return_value=mock_result):
            # Ejecutar el método
            self.bot._execute_pre_reset_profit_taking()
            
            # Verificar que se llamó con el parámetro correcto
            self.bot.close_profitable_positions.assert_called_with(min_profit=1.0)
    
    def test_execute_pre_reset_profit_taking_no_positions(self):
        """Probar la ejecución cuando no hay posiciones rentables"""
        mock_result = {
            "success": True,
            "positions_closed": 0,
            "total_profit_realized": 0.0
        }
        
        with patch.object(self.bot, 'close_profitable_positions', return_value=mock_result):
            # Ejecutar el método (no debería generar errores)
            self.bot._execute_pre_reset_profit_taking()
            
            # Verificar que se llamó correctamente
            self.bot.close_profitable_positions.assert_called_with(min_profit=1.0)
    
    def test_execute_pre_reset_profit_taking_failure(self):
        """Probar la ejecución cuando falla el cierre"""
        mock_result = {
            "success": False,
            "error": "API connection failed"
        }
        
        with patch.object(self.bot, 'close_profitable_positions', return_value=mock_result):
            # Ejecutar el método (no debería generar excepciones)
            self.bot._execute_pre_reset_profit_taking()
            
            # Verificar que se llamó correctamente
            self.bot.close_profitable_positions.assert_called_with(min_profit=1.0)


if __name__ == '__main__':
    unittest.main()
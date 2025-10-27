#!/usr/bin/env python3
"""
Pruebas unitarias para la funcionalidad de filtrado por días de la semana
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.main_config import (
    is_trading_day_allowed, 
    get_weekend_trading_params,
    TRADING_SCHEDULE,
    PROFILE_TRADING_SCHEDULE
)


class TestWeekendTradingConfig(unittest.TestCase):
    """Pruebas para la configuración de trading por días de la semana"""
    
    def test_trading_schedule_structure(self):
        """Verificar que TRADING_SCHEDULE tiene la estructura correcta"""
        expected_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        # Verificar que todos los días están presentes
        for day in expected_days:
            self.assertIn(day, TRADING_SCHEDULE)
            self.assertIsInstance(TRADING_SCHEDULE[day], bool)
        
        # Verificar configuración por defecto (lunes a viernes activado, fines de semana desactivado)
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        weekends = ["saturday", "sunday"]
        
        for day in weekdays:
            self.assertTrue(TRADING_SCHEDULE[day], f"{day} should be enabled by default")
        
        for day in weekends:
            self.assertFalse(TRADING_SCHEDULE[day], f"{day} should be disabled by default")
    
    def test_profile_trading_schedule_structure(self):
        """Verificar que PROFILE_TRADING_SCHEDULE tiene la estructura correcta"""
        expected_profiles = ["SCALPING", "INTRADAY"]
        expected_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        for profile in expected_profiles:
            self.assertIn(profile, PROFILE_TRADING_SCHEDULE)
            
            # Verificar días de la semana
            for day in expected_days:
                self.assertIn(day, PROFILE_TRADING_SCHEDULE[profile])
                self.assertIsInstance(PROFILE_TRADING_SCHEDULE[profile][day], bool)
            
            # Verificar parámetros de fin de semana
            self.assertIn("weekend_params", PROFILE_TRADING_SCHEDULE[profile])
            weekend_params = PROFILE_TRADING_SCHEDULE[profile]["weekend_params"]
            
            required_params = [
                "min_confidence_multiplier",
                "max_daily_trades_multiplier", 
                "max_position_size_multiplier"
            ]
            
            for param in required_params:
                self.assertIn(param, weekend_params)
                self.assertIsInstance(weekend_params[param], (int, float))
                self.assertGreater(weekend_params[param], 0)


class TestTradingDayAllowed(unittest.TestCase):
    """Pruebas para la función is_trading_day_allowed"""
    
    @patch('src.config.main_config.TRADING_PROFILE', 'SCALPING')
    @patch('datetime.datetime')
    def test_is_trading_day_allowed_monday_scalping(self, mock_datetime):
        """Verificar que el trading está permitido el lunes para SCALPING"""
        mock_datetime.now.return_value.strftime.return_value = "monday"
        result = is_trading_day_allowed()
        self.assertTrue(result)
    
    @patch('src.config.main_config.TRADING_PROFILE', 'SCALPING')
    @patch('datetime.datetime')
    def test_is_trading_day_allowed_saturday_scalping(self, mock_datetime):
        """Verificar que el trading NO está permitido el sábado para SCALPING (por defecto)"""
        mock_datetime.now.return_value.strftime.return_value = "saturday"
        result = is_trading_day_allowed()
        self.assertFalse(result)
    
    @patch('src.config.main_config.TRADING_PROFILE', 'INTRADAY')
    @patch('datetime.datetime')
    def test_is_trading_day_allowed_saturday_intraday(self, mock_datetime):
        """Verificar que el trading SÍ está permitido el sábado para INTRADAY (por defecto)"""
        mock_datetime.now.return_value.strftime.return_value = "saturday"
        result = is_trading_day_allowed()
        self.assertTrue(result)
    
    @patch('datetime.datetime')
    def test_is_trading_day_allowed_with_profile_parameter(self, mock_datetime):
        """Verificar que se puede especificar el perfil como parámetro"""
        mock_datetime.now.return_value.strftime.return_value = "saturday"
        
        # SCALPING no permite sábados
        result_scalping = is_trading_day_allowed("SCALPING")
        self.assertFalse(result_scalping)
        
        # INTRADAY sí permite sábados
        result_intraday = is_trading_day_allowed("INTRADAY")
        self.assertTrue(result_intraday)
    
    @patch('datetime.datetime')
    def test_is_trading_day_allowed_unknown_profile(self, mock_datetime):
        """Verificar fallback a configuración general para perfil desconocido"""
        mock_datetime.now.return_value.strftime.return_value = "monday"
        result = is_trading_day_allowed("UNKNOWN_PROFILE")
        self.assertTrue(result)  # Lunes está habilitado en TRADING_SCHEDULE
        
        mock_datetime.now.return_value.strftime.return_value = "saturday"
        result = is_trading_day_allowed("UNKNOWN_PROFILE")
        self.assertFalse(result)  # Sábado está deshabilitado en TRADING_SCHEDULE


class TestWeekendTradingParams(unittest.TestCase):
    """Pruebas para la función get_weekend_trading_params"""
    
    @patch('src.config.main_config.TRADING_PROFILE', 'SCALPING')
    @patch('datetime.datetime')
    def test_get_weekend_trading_params_weekday_scalping(self, mock_datetime):
        """Verificar parámetros normales en día laborable para SCALPING"""
        mock_datetime.now.return_value.strftime.return_value = "monday"
        params = get_weekend_trading_params()
        
        expected = {
            "min_confidence_multiplier": 1.0,
            "max_daily_trades_multiplier": 1.0,
            "max_position_size_multiplier": 1.0
        }
        self.assertEqual(params, expected)
    
    @patch('src.config.main_config.TRADING_PROFILE', 'SCALPING')
    @patch('datetime.datetime')
    def test_get_weekend_trading_params_weekend_scalping(self, mock_datetime):
        """Verificar parámetros ajustados en fin de semana para SCALPING"""
        mock_datetime.now.return_value.strftime.return_value = "saturday"
        params = get_weekend_trading_params()
        
        # Verificar que se aplican los parámetros de fin de semana de SCALPING
        expected = PROFILE_TRADING_SCHEDULE["SCALPING"]["weekend_params"]
        self.assertEqual(params, expected)
        
        # Verificar que son más conservadores que los normales
        self.assertGreater(params["min_confidence_multiplier"], 1.0)
        self.assertLess(params["max_daily_trades_multiplier"], 1.0)
        self.assertLess(params["max_position_size_multiplier"], 1.0)
    
    @patch('src.config.main_config.TRADING_PROFILE', 'INTRADAY')
    @patch('datetime.datetime')
    def test_get_weekend_trading_params_weekend_intraday(self, mock_datetime):
        """Verificar parámetros ajustados en fin de semana para INTRADAY"""
        mock_datetime.now.return_value.strftime.return_value = "sunday"
        params = get_weekend_trading_params()
        
        # Verificar que se aplican los parámetros de fin de semana de INTRADAY
        expected = PROFILE_TRADING_SCHEDULE["INTRADAY"]["weekend_params"]
        self.assertEqual(params, expected)
        
        # INTRADAY debería ser menos conservador que SCALPING
        scalping_params = PROFILE_TRADING_SCHEDULE["SCALPING"]["weekend_params"]
        self.assertLessEqual(params["min_confidence_multiplier"], scalping_params["min_confidence_multiplier"])
        self.assertGreaterEqual(params["max_daily_trades_multiplier"], scalping_params["max_daily_trades_multiplier"])
        self.assertGreaterEqual(params["max_position_size_multiplier"], scalping_params["max_position_size_multiplier"])
    
    @patch('datetime.datetime')
    def test_get_weekend_trading_params_with_profile_parameter(self, mock_datetime):
        """Verificar que se puede especificar el perfil como parámetro"""
        mock_datetime.now.return_value.strftime.return_value = "saturday"
        
        # Obtener parámetros para SCALPING
        params_scalping = get_weekend_trading_params("SCALPING")
        expected_scalping = PROFILE_TRADING_SCHEDULE["SCALPING"]["weekend_params"]
        self.assertEqual(params_scalping, expected_scalping)
        
        # Obtener parámetros para INTRADAY
        params_intraday = get_weekend_trading_params("INTRADAY")
        expected_intraday = PROFILE_TRADING_SCHEDULE["INTRADAY"]["weekend_params"]
        self.assertEqual(params_intraday, expected_intraday)
    
    @patch('datetime.datetime')
    def test_get_weekend_trading_params_unknown_profile(self, mock_datetime):
        """Verificar fallback a parámetros conservadores para perfil desconocido"""
        mock_datetime.now.return_value.strftime.return_value = "saturday"
        params = get_weekend_trading_params("UNKNOWN_PROFILE")
        
        # Verificar que se usan parámetros conservadores por defecto
        expected = {
            "min_confidence_multiplier": 1.15,
            "max_daily_trades_multiplier": 0.6,
            "max_position_size_multiplier": 0.85
        }
        self.assertEqual(params, expected)


class TestWeekendTradingIntegration(unittest.TestCase):
    """Pruebas de integración para la funcionalidad de trading por días"""
    
    def test_weekend_params_consistency(self):
        """Verificar que los parámetros de fin de semana son consistentes entre perfiles"""
        for profile_name, profile_config in PROFILE_TRADING_SCHEDULE.items():
            weekend_params = profile_config["weekend_params"]
            
            # Los multiplicadores de confianza deberían ser >= 1.0 (más estrictos)
            self.assertGreaterEqual(
                weekend_params["min_confidence_multiplier"], 1.0,
                f"{profile_name}: min_confidence_multiplier should be >= 1.0"
            )
            
            # Los multiplicadores de trades y posición deberían ser <= 1.0 (más conservadores)
            self.assertLessEqual(
                weekend_params["max_daily_trades_multiplier"], 1.0,
                f"{profile_name}: max_daily_trades_multiplier should be <= 1.0"
            )
            self.assertLessEqual(
                weekend_params["max_position_size_multiplier"], 1.0,
                f"{profile_name}: max_position_size_multiplier should be <= 1.0"
            )
    
    def test_all_days_covered(self):
        """Verificar que todos los días de la semana están cubiertos en las configuraciones"""
        days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        # Verificar TRADING_SCHEDULE
        for day in days_of_week:
            self.assertIn(day, TRADING_SCHEDULE)
        
        # Verificar PROFILE_TRADING_SCHEDULE
        for profile_config in PROFILE_TRADING_SCHEDULE.values():
            for day in days_of_week:
                self.assertIn(day, profile_config)
    
    def test_weekend_vs_weekday_differences(self):
        """Verificar que hay diferencias claras entre configuración de fin de semana y días laborables"""
        for profile_name, profile_config in PROFILE_TRADING_SCHEDULE.items():
            weekend_params = profile_config["weekend_params"]
            
            # Al menos uno de los parámetros debería ser diferente de 1.0
            params_different = (
                weekend_params["min_confidence_multiplier"] != 1.0 or
                weekend_params["max_daily_trades_multiplier"] != 1.0 or
                weekend_params["max_position_size_multiplier"] != 1.0
            )
            
            self.assertTrue(
                params_different,
                f"{profile_name}: Weekend parameters should be different from weekday defaults"
            )


if __name__ == '__main__':
    unittest.main()
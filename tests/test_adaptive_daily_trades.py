#!/usr/bin/env python3
"""
Tests para la funcionalidad de límites adaptativos de trades diarios.
"""

import unittest
from unittest.mock import patch
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar después de agregar al path
from src.config.main_config import TradingProfiles


class TestAdaptiveDailyTrades(unittest.TestCase):
    """Tests para límites adaptativos de trades diarios."""
    
    def test_scalping_profile_adaptive_config(self):
        """Test que verifica la configuración adaptativa del perfil SCALPING."""
        profile = TradingProfiles.get_profile("SCALPING")
        
        # Verificar configuración base
        self.assertEqual(profile["max_daily_trades"], 20)
        self.assertTrue(profile["max_daily_trades_adaptive"])
        self.assertEqual(profile["daily_trades_quality_threshold"], 80.0)
        self.assertEqual(profile["max_daily_trades_bonus"], 8)
    
    def test_intraday_profile_adaptive_config(self):
        """Test que verifica la configuración adaptativa del perfil INTRADAY."""
        profile = TradingProfiles.get_profile("INTRADAY")
        
        # Verificar configuración base
        self.assertEqual(profile["max_daily_trades"], 12)
        self.assertTrue(profile["max_daily_trades_adaptive"])
        self.assertEqual(profile["daily_trades_quality_threshold"], 80.0)
        self.assertEqual(profile["max_daily_trades_bonus"], 6)
    
    @patch('src.config.main_config.TradingProfiles.get_current_profile')
    def test_adaptive_daily_trades_limit_normal_confidence(self, mock_get_current_profile):
        """Test límite adaptativo con confianza normal (<80%)."""
        mock_get_current_profile.return_value = TradingProfiles.get_profile("SCALPING")
        
        # Confianza normal (75%) - debe usar límite base
        limit = TradingProfiles.get_adaptive_daily_trades_limit(
            current_trades_count=10,
            signal_confidence=75.0
        )
        
        self.assertEqual(limit, 20)  # Límite base de SCALPING
    
    @patch('src.config.main_config.TradingProfiles.get_current_profile')
    def test_adaptive_daily_trades_limit_high_confidence(self, mock_get_current_profile):
        """Test límite adaptativo con alta confianza (>=80%)."""
        mock_get_current_profile.return_value = TradingProfiles.get_profile("SCALPING")
        
        # Alta confianza (85%) - debe permitir trades adicionales
        limit = TradingProfiles.get_adaptive_daily_trades_limit(
            current_trades_count=10,
            signal_confidence=85.0
        )
        
        self.assertEqual(limit, 28)  # 20 base + 8 bonus = 28
    
    @patch('src.config.main_config.TradingProfiles.get_current_profile')
    def test_adaptive_daily_trades_limit_intraday_high_confidence(self, mock_get_current_profile):
        """Test límite adaptativo INTRADAY con alta confianza."""
        mock_get_current_profile.return_value = TradingProfiles.get_profile("INTRADAY")
        
        # Alta confianza (90%) - debe permitir trades adicionales
        limit = TradingProfiles.get_adaptive_daily_trades_limit(
            current_trades_count=5,
            signal_confidence=90.0
        )
        
        self.assertEqual(limit, 18)  # 12 base + 6 bonus = 18
    
    @patch('src.config.main_config.TradingProfiles.get_current_profile')
    def test_adaptive_daily_trades_limit_threshold_boundary(self, mock_get_current_profile):
        """Test límite adaptativo en el umbral exacto (80%)."""
        mock_get_current_profile.return_value = TradingProfiles.get_profile("SCALPING")
        
        # Confianza exacta en el umbral (80%) - debe permitir trades adicionales
        limit = TradingProfiles.get_adaptive_daily_trades_limit(
            current_trades_count=15,
            signal_confidence=80.0
        )
        
        self.assertEqual(limit, 28)  # 20 base + 8 bonus = 28
    
    @patch('src.config.main_config.TradingProfiles.get_current_profile')
    def test_adaptive_daily_trades_limit_just_below_threshold(self, mock_get_current_profile):
        """Test límite adaptativo justo debajo del umbral (79.9%)."""
        mock_get_current_profile.return_value = TradingProfiles.get_profile("SCALPING")
        
        # Confianza justo debajo del umbral (79.9%) - debe usar límite base
        limit = TradingProfiles.get_adaptive_daily_trades_limit(
            current_trades_count=15,
            signal_confidence=79.9
        )
        
        self.assertEqual(limit, 20)  # Solo límite base
    
    def test_get_max_daily_trades_compatibility(self):
        """Test que la función original sigue funcionando."""
        # La función original debe seguir devolviendo el límite base según el perfil actual
        # Esto depende del perfil configurado en main_config.py
        base_limit = TradingProfiles.get_max_daily_trades()
        self.assertIsInstance(base_limit, int)
        self.assertGreater(base_limit, 0)


if __name__ == "__main__":
    unittest.main()
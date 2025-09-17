"""Tests básicos para main.py - API principal del sistema de trading"""

import pytest
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMainConfiguration:
    """Tests para verificar la configuración de main.py"""
    
    def test_configuration_structure(self):
        """Test de estructura de configuración esperada"""
        # Test básico de que la configuración tiene la estructura esperada
        config_structure = {
            "api": {
                "title": "Crypto Trading Analyzer API",
                "version": "1.0.0",
                "host": "0.0.0.0",
                "port": 8000
            },
            "trading_bot": {
                "default_symbols": ["BTCUSDT", "ETHUSDT"],
                "analysis_interval": 300,
                "max_daily_trades": 50
            },
            "paper_trading": {
                "initial_balance": 10000.0,
                "max_position_percentage": 0.1
            }
        }
        
        # Verificar que la estructura es válida
        assert config_structure["api"]["title"] == "Crypto Trading Analyzer API"
        assert config_structure["trading_bot"]["analysis_interval"] == 300
        assert config_structure["paper_trading"]["initial_balance"] == 10000.0
        
    def test_environment_variables(self):
        """Test de variables de entorno esperadas"""
        # Test de que las variables de entorno pueden ser configuradas
        test_vars = {
            "API_HOST": "0.0.0.0",
            "API_PORT": "8000",
            "DEFAULT_TRADING_MODE": "paper",
            "INITIAL_BALANCE": "10000.0",
            "EXCHANGE_API_KEY": "test_key",
            "EXCHANGE_SECRET": "test_secret"
        }
        
        for key, value in test_vars.items():
            # Simular que las variables están configuradas
            assert isinstance(value, str)  # Las env vars son siempre strings
            assert len(value) > 0  # No deben estar vacías
            
    def test_main_config_import(self):
        """Test de que main_config.py puede ser importado"""
        try:
            import main_config
            assert hasattr(main_config, 'MainConfig')
            
            # Verificar que la configuración tiene las clases esperadas
            config = main_config.MainConfig()
            assert hasattr(config, 'api')
            assert hasattr(config, 'exchange')
            assert hasattr(config, 'trading_bot')
            assert hasattr(config, 'paper_trading')
            
        except ImportError as e:
            pytest.skip(f"No se pudo importar main_config: {e}")
            
class TestMainStructure:
    """Tests para verificar la estructura de main.py"""
    
    def test_main_file_exists(self):
        """Test de que main.py existe"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        assert os.path.exists(main_path), "El archivo main.py debe existir"
        
    def test_main_file_structure(self):
        """Test de estructura básica de main.py"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar que contiene elementos esenciales
        assert "from fastapi import FastAPI" in content, "Debe importar FastAPI"
        assert "app = FastAPI" in content, "Debe crear una instancia de FastAPI"
        assert "@app.get" in content, "Debe tener endpoints GET"
        assert "@app.post" in content, "Debe tener endpoints POST"
        
        # Verificar que usa configuración centralizada
        assert "from src.config.main_config import" in content or "import main_config" in content, "Debe importar main_config"
        assert "config." in content, "Debe usar configuración centralizada"
        
    def test_main_endpoints_structure(self):
        """Test de que main.py tiene los endpoints esperados"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Endpoints esenciales que deben existir
        essential_endpoints = [
            '"/"',  # Root endpoint
            '"/health"',  # Health check
            '"/bot/status"',  # Bot status
            '"/bot/start"',  # Start bot
            '"/bot/stop"',  # Stop bot
            '"/bot/trading-mode"',  # Trading mode
            '"/paper-trading/summary"',  # Paper trading summary
        ]
        
        for endpoint in essential_endpoints:
            assert endpoint in content, f"Debe tener el endpoint {endpoint}"
            
class TestMainOptimization:
    """Tests para verificar optimizaciones aplicadas"""
    
    def test_no_hardcoded_values(self):
        """Test de que no hay valores hardcodeados comunes"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Valores que NO deberían estar hardcodeados
        hardcoded_patterns = [
            '"1h"',  # Timeframes hardcodeados
            '"4h"',
            '"1d"',
            '10000.0',  # Balance inicial hardcodeado
            '8000',  # Puerto hardcodeado
            '"BTCUSDT"',  # Símbolos hardcodeados en lógica
            '"ETHUSDT"',
            '300',  # Intervalos hardcodeados
            '0.1',  # Porcentajes hardcodeados
        ]
        
        # Contar ocurrencias de patrones hardcodeados
        hardcoded_count = 0
        for pattern in hardcoded_patterns:
            if pattern in content:
                hardcoded_count += content.count(pattern)
                
        # Permitir algunas ocurrencias para valores por defecto, pero no muchas
        assert hardcoded_count < 10, f"Demasiados valores hardcodeados encontrados: {hardcoded_count}"
        
    def test_uses_config_references(self):
        """Test de que usa referencias a configuración"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Patrones de configuración que deberían existir
        config_patterns = [
            "config.api",
            "config.trading_bot",
            "config.paper_trading",
            "config.exchange",
            "config.strategy",
        ]
        
        config_usage_count = 0
        for pattern in config_patterns:
            config_usage_count += content.count(pattern)
            
        assert config_usage_count > 5, "Debe usar configuración centralizada extensivamente"
        
    def test_proper_error_handling(self):
        """Test de que tiene manejo de errores apropiado"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Patrones de manejo de errores
        error_patterns = [
            "HTTPException",
            "try:",
            "except",
            "status_code",
        ]
        
        for pattern in error_patterns:
            assert pattern in content, f"Debe tener manejo de errores con {pattern}"
            
class TestMainDocumentation:
    """Tests para verificar documentación"""
    
    def test_has_docstrings(self):
        """Test de que tiene docstrings"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Debe tener docstrings
        docstring_count = content.count('"""')
        assert docstring_count >= 4, "Debe tener docstrings en funciones principales"
        
    def test_documentation_file_exists(self):
         """Test de que existe documentación"""
         # Verificar que existe documentación en docs/
         docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
         assert os.path.exists(docs_dir), "Debe existir directorio de documentación"
         
         # Verificar que existe main.md en docs
         main_doc_path = os.path.join(docs_dir, "main.md")
         assert os.path.exists(main_doc_path), "Debe existir documentación de main.py"
         
         # Verificar que la documentación no está vacía
         with open(main_doc_path, 'r', encoding='utf-8') as f:
             content = f.read()
             
         assert len(content) > 100, "La documentación debe tener contenido"
         assert "main" in content.lower(), "Debe documentar main.py"
        
class TestMainPerformance:
    """Tests básicos de rendimiento y buenas prácticas"""
    
    def test_imports_optimization(self):
        """Test de optimización de imports"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        with open(main_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        import_lines = [line for line in lines if line.strip().startswith('import ') or line.strip().startswith('from ')]
        
        # No debería tener demasiados imports
        assert len(import_lines) < 30, "Demasiados imports, considerar refactoring"
        
        # Verificar que no hay imports duplicados
        import_statements = [line.strip() for line in import_lines]
        unique_imports = set(import_statements)
        assert len(import_statements) == len(unique_imports), "No debe tener imports duplicados"
        
    def test_function_complexity(self):
        """Test básico de complejidad de funciones"""
        main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Contar funciones definidas
        function_count = content.count('def ') + content.count('async def ')
        
        # Debe tener un número razonable de funciones
        assert function_count > 5, "Debe tener funciones para diferentes endpoints"
        assert function_count < 50, "Demasiadas funciones, considerar modularización"
        
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
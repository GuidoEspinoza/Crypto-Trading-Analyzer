#!/usr/bin/env python3
"""
Script para ejecutar las pruebas del sistema de trading.

Uso:
    python run_tests.py                    # Ejecutar todas las pruebas
    python run_tests.py test_cooldown      # Ejecutar solo pruebas de cooldown
"""

import sys
import os
import unittest

def run_tests(test_pattern=None):
    """Ejecutar las pruebas del sistema."""
    # Agregar el directorio actual al path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Configurar el directorio de tests
    test_dir = os.path.join(current_dir, 'tests')
    
    if test_pattern:
        # Ejecutar pruebas específicas
        loader = unittest.TestLoader()
        suite = loader.discover(test_dir, pattern=f'*{test_pattern}*.py')
    else:
        # Ejecutar todas las pruebas
        loader = unittest.TestLoader()
        suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Ejecutar las pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar código de salida basado en el resultado
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    test_pattern = sys.argv[1] if len(sys.argv) > 1 else None
    exit_code = run_tests(test_pattern)
    sys.exit(exit_code)
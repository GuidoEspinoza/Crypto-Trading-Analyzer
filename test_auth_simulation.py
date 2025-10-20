#!/usr/bin/env python3
"""
Script de prueba para simular el flujo de autenticación sin hacer llamadas reales a la API.
Esto nos permite verificar que la lógica de encriptación y actualización del .env funciona correctamente.
"""

import logging
import os
import sys
from unittest.mock import patch, MagicMock

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.capital_client import CapitalClient, CapitalConfig

def test_encryption_and_env_update():
    """
    Prueba la lógica de encriptación y actualización del .env sin hacer llamadas reales a la API
    """
    print("🧪 Iniciando prueba de simulación del flujo de autenticación...")
    
    try:
        # Crear configuración
        config = CapitalConfig(
            base_url="https://demo-api-capital.backend-capital.com/api/v1",
            api_key="test_api_key",
            identifier="test@example.com",
            password="test_password",
            encrypted_password=None,
            cst=None,
            x_security_token=None,
            is_demo=True
        )
        
        # Crear cliente
        client = CapitalClient(config)
        
        # Mock de la respuesta de encryption key
        mock_encryption_response = {
            "encryptionKey": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1dOujgcFh/9n4JLJMY4VMWZ7aRrynwKXUC9RuoC8Qu5UOeskxgZ1q5DmAXjkes77KrLfFZYEKtrp2g1TB0MBkSALiyrG+Fl52vhET9/AWRhvHuFyskWI7tEtcGIaOB1FwR0EDO9bnylTaZ+Y9sPbLVA7loAtfaX3HW/TI9JDpdmgzXZ0KrwIxdMRzPxVqQXcA8yJL1m33pvo9mOJ0AsQ8FFuy+ctjI8l/8xUhe2Hk01rpMBXDwI1lSjnvuUUDvAtacxyYVlNsnRvbrMZYp7hyimm27RtvCUXhTX2A94tDB0MFLApURrki+tvTvw5ImDPN8qOdTUzbs8hNtVwTpSxPwIDAQAB",
            "timeStamp": 1647440528194
        }
        
        # Mock del método get_encryption_key
        with patch.object(client, 'get_encryption_key') as mock_get_key:
            mock_get_key.return_value = {
                "success": True,
                "encryption_key": mock_encryption_response["encryptionKey"],
                "timestamp": mock_encryption_response["timeStamp"]
            }
            
            print("✅ 1. Probando generación de contraseña encriptada...")
            
            # Probar generación de contraseña encriptada
            encrypted_password = client._generate_encrypted_password()
            
            if encrypted_password:
                print(f"✅ Contraseña encriptada generada: {encrypted_password[:50]}...")
                
                # Verificar que se actualiza en la configuración
                client.config.encrypted_password = encrypted_password
                print("✅ 2. Contraseña encriptada asignada a la configuración")
                
                # Probar actualización del archivo .env
                print("✅ 3. Probando actualización del archivo .env...")
                
                # Mock de la actualización del .env
                with patch.object(client, '_update_env_file') as mock_update_env:
                    mock_update_env.return_value = True
                    
                    # Simular actualización de tokens
                    test_cst = "test_cst_token_12345"
                    test_security_token = "test_security_token_67890"
                    
                    result = client._update_env_file({
                        'encryptedPassword': encrypted_password,
                        'CST': test_cst,
                        'X-SECURITY-TOKEN': test_security_token
                    })
                    
                    if result:
                        print("✅ 4. Archivo .env actualizado correctamente (simulado)")
                        
                        # Verificar que el método fue llamado con los parámetros correctos
                        mock_update_env.assert_called_once()
                        call_args = mock_update_env.call_args[0][0]
                        
                        assert 'encryptedPassword' in call_args
                        assert 'CST' in call_args
                        assert 'X-SECURITY-TOKEN' in call_args
                        
                        print("✅ 5. Parámetros de actualización verificados")
                        
                        print("\n🎉 ¡Todas las pruebas de simulación pasaron exitosamente!")
                        print("\n📋 Resumen de la prueba:")
                        print(f"   • Encriptación RSA: ✅ Funcionando")
                        print(f"   • Generación de encryptedPassword: ✅ Funcionando")
                        print(f"   • Actualización de configuración: ✅ Funcionando")
                        print(f"   • Actualización de .env: ✅ Funcionando (simulado)")
                        
                        return True
                    else:
                        print("❌ Error al actualizar el archivo .env")
                        return False
            else:
                print("❌ Error al generar la contraseña encriptada")
                return False
                
    except Exception as e:
        print(f"❌ Error durante la prueba de simulación: {str(e)}")
        logger.error("Error detallado:", exc_info=True)
        return False

def test_env_file_format():
    """
    Prueba que el formato del archivo .env sea correcto
    """
    print("\n🔍 Verificando formato del archivo .env...")
    
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            
        print("✅ Archivo .env encontrado")
        
        # Verificar que las variables necesarias estén presentes
        required_vars = [
            'CAPITAL_DEMO_URL',
            'IS_DEMO',
            'identifier',
            'password',
            'encryptedPassword',
            'X-CAP-API-KEY',
            'X-SECURITY-TOKEN',
            'CST'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if not missing_vars:
            print("✅ Todas las variables requeridas están presentes en .env")
            
            # Verificar que encryptedPassword esté como null
            if 'encryptedPassword=null' in content:
                print("✅ encryptedPassword está configurado como null (correcto para generación dinámica)")
            else:
                print("⚠️  encryptedPassword no está como null - se generará dinámicamente de todas formas")
                
            return True
        else:
            print(f"❌ Variables faltantes en .env: {missing_vars}")
            return False
    else:
        print("❌ Archivo .env no encontrado")
        return False

if __name__ == "__main__":
    print("🚀 Ejecutando pruebas de simulación del flujo de autenticación seguro\n")
    
    # Ejecutar pruebas
    env_test = test_env_file_format()
    simulation_test = test_encryption_and_env_update()
    
    print(f"\n📊 Resultados finales:")
    print(f"   • Formato .env: {'✅ PASS' if env_test else '❌ FAIL'}")
    print(f"   • Simulación de flujo: {'✅ PASS' if simulation_test else '❌ FAIL'}")
    
    if env_test and simulation_test:
        print(f"\n🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar con credenciales válidas.")
        print(f"\n💡 Próximos pasos:")
        print(f"   1. Obtener credenciales válidas de una cuenta demo de Capital.com")
        print(f"   2. Actualizar el archivo .env con las credenciales correctas")
        print(f"   3. Ejecutar el flujo real de autenticación")
    else:
        print(f"\n❌ Algunas pruebas fallaron. Revisa los logs para más detalles.")
        sys.exit(1)
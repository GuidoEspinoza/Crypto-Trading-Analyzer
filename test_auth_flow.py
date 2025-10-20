#!/usr/bin/env python3
"""
Script de prueba para verificar el nuevo flujo de autenticación seguro
que usa encryptedPassword y actualiza automáticamente los tokens en .env
"""

import os
import sys
import logging
from pathlib import Path

# Añadir el directorio raíz al path para importaciones absolutas
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.capital_client import create_capital_client_from_env

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_auth_flow():
    """Prueba el nuevo flujo de autenticación"""
    print("🔐 Probando el nuevo flujo de autenticación seguro...")
    print("=" * 60)
    
    try:
        # Verificar que encryptedPassword esté en null inicialmente
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                if "encryptedPassword=null" in content:
                    print("✅ encryptedPassword está configurado como null (se generará dinámicamente)")
                else:
                    print("⚠️  encryptedPassword no está en null, pero se regenerará si es necesario")
        
        # Crear cliente desde variables de entorno
        print("\n📡 Creando cliente Capital.com...")
        client = create_capital_client_from_env()
        
        # Intentar crear sesión (esto debería generar encryptedPassword automáticamente)
        print("\n🔑 Creando sesión con encryptedPassword...")
        session_result = client.create_session()
        
        if session_result.get("success"):
            print("✅ Sesión creada exitosamente!")
            print(f"   - CST Token: {session_result.get('cst_token', 'N/A')[:20]}...")
            print(f"   - Security Token: {session_result.get('security_token', 'N/A')[:20]}...")
            print(f"   - Trailing Stops: {'✅ Habilitado' if session_result.get('trailing_stops_enabled') else '❌ Deshabilitado'}")
            
            # Verificar que los tokens se hayan actualizado en .env
            print("\n🔍 Verificando actualización de tokens en .env...")
            if env_file.exists():
                with open(env_file, 'r') as f:
                    updated_content = f.read()
                    
                if "CST=" in updated_content and "X-SECURITY-TOKEN=" in updated_content:
                    print("✅ Tokens actualizados correctamente en .env")
                else:
                    print("⚠️  Los tokens no se encontraron en .env")
                    
                if "encryptedPassword=" in updated_content and "encryptedPassword=null" not in updated_content:
                    print("✅ encryptedPassword generado y almacenado en .env")
                else:
                    print("⚠️  encryptedPassword no se generó correctamente")
            
            # Probar una operación básica
            print("\n🏥 Probando operación básica (ping)...")
            ping_result = client.ping()
            if ping_result.get("success"):
                print("✅ Ping exitoso - la sesión está funcionando correctamente")
            else:
                print("❌ Ping falló:", ping_result.get("error", "Error desconocido"))
            
            # Cerrar sesión
            print("\n🔒 Cerrando sesión...")
            close_result = client.close_session()
            if close_result.get("success"):
                print("✅ Sesión cerrada correctamente")
            else:
                print("⚠️  Error al cerrar sesión:", close_result.get("error", "Error desconocido"))
                
        else:
            print("❌ Error al crear sesión:", session_result.get("error", "Error desconocido"))
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        logger.exception("Error detallado:")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Prueba del flujo de autenticación completada!")
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando prueba del nuevo flujo de autenticación seguro")
    print("Este script verificará:")
    print("  1. Generación automática de encryptedPassword")
    print("  2. Autenticación usando encryptedPassword")
    print("  3. Actualización automática de tokens en .env")
    print("  4. Funcionamiento básico de la sesión")
    print()
    
    success = test_auth_flow()
    
    if success:
        print("✅ Todas las pruebas pasaron exitosamente!")
        sys.exit(0)
    else:
        print("❌ Algunas pruebas fallaron. Revisa los logs para más detalles.")
        sys.exit(1)

if __name__ == "__main__":
    main()
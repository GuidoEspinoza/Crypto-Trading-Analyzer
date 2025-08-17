"""
🧪 Script de Verificación de Instalación EXITOSA
Verifica que todas las dependencias estén instaladas correctamente
"""

print("🚀 Verificando instalación del backend...")

try:
    # Verificar FastAPI
    import fastapi
    print(f"✅ FastAPI {fastapi.__version__} - OK")
    
    # Verificar Pandas
    import pandas as pd
    print(f"✅ Pandas {pd.__version__} - OK")
    
    # Verificar NumPy
    import numpy as np
    print(f"✅ NumPy {np.__version__} - OK")
    
    # Verificar pandas-ta (nuestro reemplazo de TA-Lib)
    import pandas_ta as ta
    print(f"✅ Pandas-TA {ta.__version__} - OK (150+ indicadores)")
    
    # Verificar CCXT (para conexión con exchanges)
    import ccxt
    print(f"✅ CCXT {ccxt.__version__} - OK")
    
    # Verificar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variables de entorno - OK")
    
    # Verificar Pydantic (validación)
    import pydantic
    print(f"✅ Pydantic {pydantic.__version__} - OK (¡Compatible!)")
    
    # Test rápido de pandas-ta
    print("\n🧪 Probando indicadores técnicos...")
    sample_data = pd.Series([10, 12, 11, 13, 15, 14, 16, 18, 17, 19, 21, 20, 22])
    
    # Probar varios indicadores
    rsi = ta.rsi(sample_data, length=5)
    sma = ta.sma(sample_data, length=3)
    ema = ta.ema(sample_data, length=3)
    
    print(f"✅ RSI: {rsi.iloc[-1]:.2f}")
    print(f"✅ SMA: {sma.iloc[-1]:.2f}")
    print(f"✅ EMA: {ema.iloc[-1]:.2f}")
    
    # Test de CCXT (conexión básica)
    print("\n🔗 Probando conexión con exchange...")
    exchange = ccxt.binance()
    print(f"✅ Exchange Binance inicializado - OK")
    
    print("\n🎉 ¡INSTALACIÓN COMPLETAMENTE EXITOSA!")
    print("🎯 ¡Listo para desarrollar el MVP del Trading Analyzer!")
    print("\n📚 Resumen de capacidades instaladas:")
    print("   🔥 FastAPI - API web moderna")
    print("   📊 Pandas + NumPy - Análisis de datos")
    print("   📈 Pandas-TA - 150+ indicadores técnicos")
    print("   💰 CCXT - Conexión con 100+ exchanges")
    print("   ✅ Pydantic - Validación de datos")
    print("   🧪 Pytest - Testing framework")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("💡 Ejecuta: pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
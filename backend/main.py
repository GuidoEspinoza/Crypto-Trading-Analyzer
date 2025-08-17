"""
🚀 Universal Trading Analyzer - API Principal
FastAPI backend para análisis técnico de criptomonedas
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import ccxt
import pandas as pd
import pandas_ta as ta
from typing import Dict, List, Optional
import uvicorn

# Importar nuestros indicadores avanzados
from advanced_indicators import AdvancedIndicators, FibonacciLevels, IchimokuCloud

# Crear instancia de FastAPI
app = FastAPI(
    title="🚀 Universal Trading Analyzer",
    description="API para análisis técnico de criptomonedas en tiempo real",
    version="2.0.0",  # Actualizada con indicadores avanzados
    docs_url="/docs",  # Swagger UI en /docs
    redoc_url="/redoc"  # ReDoc en /redoc
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar exchange (Binance público, sin API keys)
exchange = ccxt.binance({
    'sandbox': False,  # Usar datos reales
    'enableRateLimit': True,
})

@app.get("/")
async def root():
    """
    🏠 Endpoint raíz - Bienvenida a la API
    """
    return {
        "message": "🚀 Universal Trading Analyzer API v2.0",
        "status": "active",
        "features": [
            "💰 Precios en tiempo real",
            "📊 Indicadores técnicos básicos",
            "🔥 Indicadores avanzados",
            "🕯️ Patrones de velas japonesas",
            "☁️ Ichimoku Cloud",
            "🔢 Fibonacci Retracements",
            "🎯 Señales de trading profesionales"
        ],
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """
    ❤️ Health check - Verificar estado de la API
    """
    try:
        # Verificar conexión con Binance
        ticker = exchange.fetch_ticker('BTC/USDT')
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "exchange_connection": "OK",
            "last_btc_price": ticker['last'],
            "api_version": "2.0.0"
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "exchange_connection": "FAILED",
            "error": str(e)
        }

@app.get("/price/{symbol}")
async def get_price(symbol: str):
    """
    💰 Obtener precio actual de una criptomoneda
    
    Args:
        symbol: Par de trading (ej: BTC/USDT, ETH/USDT)
    
    Returns:
        Información del precio actual
    """
    try:
        # Formatear símbolo
        symbol = symbol.upper().replace('-', '/')
        
        # Obtener ticker del exchange
        ticker = exchange.fetch_ticker(symbol)
        
        return {
            "symbol": symbol,
            "price": ticker['last'],
            "bid": ticker['bid'],
            "ask": ticker['ask'],
            "volume": ticker['baseVolume'],
            "change_24h": ticker['change'],
            "change_24h_percent": ticker['percentage'],
            "high_24h": ticker['high'],
            "low_24h": ticker['low'],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Error obteniendo precio para {symbol}: {str(e)}"
        )

@app.get("/rsi/{symbol}")
async def get_rsi(symbol: str, timeframe: str = "1h", periods: int = 14):
    """
    📊 Calcular RSI (Relative Strength Index) para una criptomoneda
    
    Args:
        symbol: Par de trading (ej: BTC/USDT)
        timeframe: Marco temporal (1m, 5m, 15m, 1h, 4h, 1d)
        periods: Períodos para el cálculo del RSI (default: 14)
    
    Returns:
        Valor actual del RSI y interpretación
    """
    try:
        # Formatear símbolo
        symbol = symbol.upper().replace('-', '/')
        
        # Obtener datos históricos (100 velas para tener suficientes datos)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        
        # Convertir a DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calcular RSI usando pandas-ta
        df['rsi'] = ta.rsi(df['close'], length=periods)
        
        # Obtener último valor
        current_rsi = df['rsi'].iloc[-1]
        
        # Interpretación del RSI
        if current_rsi >= 70:
            interpretation = "🔴 Sobrecomprado - Posible venta"
        elif current_rsi <= 30:
            interpretation = "🟢 Sobrevendido - Posible compra"
        else:
            interpretation = "⚪ Neutral - Sin señal clara"
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "rsi_current": round(current_rsi, 2),
            "rsi_periods": periods,
            "interpretation": interpretation,
            "signal": "BUY" if current_rsi <= 30 else "SELL" if current_rsi >= 70 else "HOLD",
            "timestamp": datetime.now().isoformat(),
            "data_points": len(df)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculando RSI para {symbol}: {str(e)}"
        )

@app.get("/fibonacci/{symbol}")
async def get_fibonacci_levels(symbol: str, timeframe: str = "1h", lookback: int = 50):
    """
    🔢 Calcular niveles de Fibonacci para retracements
    
    Args:
        symbol: Par de trading (ej: BTC/USDT)
        timeframe: Marco temporal (1m, 5m, 15m, 1h, 4h, 1d)
        lookback: Períodos hacia atrás para encontrar swing high/low
    
    Returns:
        Niveles de Fibonacci y análisis de soporte/resistencia
    """
    try:
        # Formatear símbolo
        symbol = symbol.upper().replace('-', '/')
        
        # Obtener datos históricos
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calcular Fibonacci
        fib_levels = AdvancedIndicators.fibonacci_retracement(df, lookback)
        current_price = df['close'].iloc[-1]
        
        # Determinar nivel más cercano
        levels = [
            ("0%", fib_levels.level_0),
            ("23.6%", fib_levels.level_236),
            ("38.2%", fib_levels.level_382),
            ("50%", fib_levels.level_500),
            ("61.8%", fib_levels.level_618),
            ("78.6%", fib_levels.level_786),
            ("100%", fib_levels.level_100)
        ]
        
        # Encontrar nivel más cercano
        closest_level = min(levels, key=lambda x: abs(x[1] - current_price))
        
        # Análisis de la posición actual
        if current_price > fib_levels.level_382:
            analysis = "🟢 Precio por encima del 38.2% - Tendencia alcista fuerte"
        elif current_price > fib_levels.level_618:
            analysis = "⚪ Precio entre 38.2% y 61.8% - Zona de consolidación"
        else:
            analysis = "🔴 Precio por debajo del 61.8% - Presión bajista"
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": round(current_price, 2),
            "fibonacci_levels": {
                "0_percent": round(fib_levels.level_0, 2),
                "23_6_percent": round(fib_levels.level_236, 2),
                "38_2_percent": round(fib_levels.level_382, 2),
                "50_percent": round(fib_levels.level_500, 2),
                "61_8_percent": round(fib_levels.level_618, 2),
                "78_6_percent": round(fib_levels.level_786, 2),
                "100_percent": round(fib_levels.level_100, 2)
            },
            "closest_level": {
                "level": closest_level[0],
                "price": round(closest_level[1], 2),
                "distance": round(abs(current_price - closest_level[1]), 2)
            },
            "analysis": analysis,
            "lookback_periods": lookback,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculando Fibonacci para {symbol}: {str(e)}"
        )

@app.get("/ichimoku/{symbol}")
async def get_ichimoku_analysis(symbol: str, timeframe: str = "1h"):
    """
    ☁️ Análisis completo del Ichimoku Cloud
    
    Args:
        symbol: Par de trading (ej: BTC/USDT)
        timeframe: Marco temporal (1m, 5m, 15m, 1h, 4h, 1d)
    
    Returns:
        Análisis completo del Ichimoku Cloud
    """
    try:
        # Formatear símbolo
        symbol = symbol.upper().replace('-', '/')
        
        # Obtener datos históricos (más datos para Ichimoku)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calcular Ichimoku
        ichimoku = AdvancedIndicators.ichimoku_cloud(df)
        current_price = df['close'].iloc[-1]
        
        # Generar señal basada en Ichimoku
        if "Arriba" in ichimoku.price_position and ichimoku.cloud_color == "Verde":
            signal = "BUY"
            strength = "Fuerte"
        elif "Debajo" in ichimoku.price_position and ichimoku.cloud_color == "Roja":
            signal = "SELL"
            strength = "Fuerte"
        elif "Dentro" in ichimoku.price_position:
            signal = "HOLD"
            strength = "Neutral"
        else:
            signal = "HOLD"
            strength = "Débil"
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": round(current_price, 2),
            "ichimoku_components": {
                "tenkan_sen": round(ichimoku.tenkan_sen, 2),
                "kijun_sen": round(ichimoku.kijun_sen, 2),
                "senkou_span_a": round(ichimoku.senkou_span_a, 2),
                "senkou_span_b": round(ichimoku.senkou_span_b, 2),
                "chikou_span": round(ichimoku.chikou_span, 2)
            },
            "cloud_analysis": {
                "color": ichimoku.cloud_color,
                "price_position": ichimoku.price_position,
                "signal": signal,
                "strength": strength
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculando Ichimoku para {symbol}: {str(e)}"
        )

@app.get("/advanced-oscillators/{symbol}")
async def get_advanced_oscillators(symbol: str, timeframe: str = "1h"):
    """
    📊 Análisis de osciladores avanzados
    
    Args:
        symbol: Par de trading (ej: BTC/USDT)
        timeframe: Marco temporal (1m, 5m, 15m, 1h, 4h, 1d)
    
    Returns:
        Múltiples osciladores avanzados y sus señales
    """
    try:
        # Formatear símbolo
        symbol = symbol.upper().replace('-', '/')
        
        # Obtener datos históricos
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Calcular todos los osciladores avanzados
        stochastic = AdvancedIndicators.stochastic_oscillator(df)
        williams_r = AdvancedIndicators.williams_percent_r(df)
        awesome_osc = AdvancedIndicators.awesome_oscillator(df)
        cci = AdvancedIndicators.commodity_channel_index(df)
        psar = AdvancedIndicators.parabolic_sar(df)
        
        # Contar señales para consenso
        signals = [stochastic['signal'], williams_r['signal'], awesome_osc['signal'], 
                  cci['signal'], psar['signal']]
        
        buy_count = signals.count('BUY')
        sell_count = signals.count('SELL')
        hold_count = signals.count('HOLD')
        
        # Determinar señal de consenso
        if buy_count > sell_count and buy_count > hold_count:
            consensus = "BUY"
            confidence = f"{buy_count}/5"
        elif sell_count > buy_count and sell_count > hold_count:
            consensus = "SELL"
            confidence = f"{sell_count}/5"
        else:
            consensus = "HOLD"
            confidence = f"{max(buy_count, sell_count, hold_count)}/5"
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": round(df['close'].iloc[-1], 2),
            "oscillators": {
                "stochastic": stochastic,
                "williams_r": williams_r,
                "awesome_oscillator": awesome_osc,
                "cci": cci,
                "parabolic_sar": psar
            },
            "consensus": {
                "signal": consensus,
                "confidence": confidence,
                "buy_signals": buy_count,
                "sell_signals": sell_count,
                "hold_signals": hold_count
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculando osciladores para {symbol}: {str(e)}"
        )

@app.get("/candlestick-patterns/{symbol}")
async def get_candlestick_patterns(symbol: str, timeframe: str = "1h"):
    """
    🕯️ Detectar patrones de velas japonesas
    
    Args:
        symbol: Par de trading (ej: BTC/USDT)
        timeframe: Marco temporal (1m, 5m, 15m, 1h, 4h, 1d)
    
    Returns:
        Patrones de velas detectados y sus implicaciones
    """
    try:
        # Formatear símbolo
        symbol = symbol.upper().replace('-', '/')
        
        # Obtener datos históricos
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=50)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Detectar patrones
        patterns = AdvancedIndicators.detect_candlestick_patterns(df)
        current_price = df['close'].iloc[-1]
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": round(current_price, 2),
            "patterns_analysis": patterns,
            "latest_candle": {
                "open": round(df['open'].iloc[-1], 2),
                "high": round(df['high'].iloc[-1], 2),
                "low": round(df['low'].iloc[-1], 2),
                "close": round(df['close'].iloc[-1], 2),
                "volume": round(df['volume'].iloc[-1], 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error detectando patrones para {symbol}: {str(e)}"
        )

@app.get("/signals/{symbol}")
async def get_trading_signals(symbol: str, timeframe: str = "1h"):
    """
    🎯 Obtener múltiples señales de trading para una criptomoneda
    
    Args:
        symbol: Par de trading (ej: BTC/USDT)
        timeframe: Marco temporal (1m, 5m, 15m, 1h, 4h, 1d)
    
    Returns:
        Múltiples indicadores técnicos y señales de trading
    """
    try:
        # Formatear símbolo
        symbol = symbol.upper().replace('-', '/')
        
        # Obtener datos históricos
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
        
        # Convertir a DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Calcular múltiples indicadores básicos
        df['rsi'] = ta.rsi(df['close'], length=14)
        df['sma_20'] = ta.sma(df['close'], length=20)
        df['sma_50'] = ta.sma(df['close'], length=50)
        df['ema_12'] = ta.ema(df['close'], length=12)
        df['ema_26'] = ta.ema(df['close'], length=26)
        
        # MACD
        macd_data = ta.macd(df['close'])
        df['macd'] = macd_data['MACD_12_26_9']
        df['macd_signal'] = macd_data['MACDs_12_26_9']
        df['macd_histogram'] = macd_data['MACDh_12_26_9']
        
        # Bollinger Bands
        bb_data = ta.bbands(df['close'])
        df['bb_upper'] = bb_data['BBU_5_2.0']
        df['bb_middle'] = bb_data['BBM_5_2.0']
        df['bb_lower'] = bb_data['BBL_5_2.0']
        
        # Obtener valores actuales
        latest = df.iloc[-1]
        current_price = latest['close']
        
        # Generar señales
        signals = {
            "rsi": {
                "value": round(latest['rsi'], 2),
                "signal": "BUY" if latest['rsi'] <= 30 else "SELL" if latest['rsi'] >= 70 else "HOLD"
            },
            "sma_cross": {
                "sma_20": round(latest['sma_20'], 2),
                "sma_50": round(latest['sma_50'], 2),
                "signal": "BUY" if latest['sma_20'] > latest['sma_50'] else "SELL"
            },
            "macd": {
                "macd": round(latest['macd'], 4),
                "signal_line": round(latest['macd_signal'], 4),
                "histogram": round(latest['macd_histogram'], 4),
                "signal": "BUY" if latest['macd'] > latest['macd_signal'] else "SELL"
            },
            "bollinger": {
                "upper": round(latest['bb_upper'], 2),
                "middle": round(latest['bb_middle'], 2),
                "lower": round(latest['bb_lower'], 2),
                "signal": "SELL" if current_price >= latest['bb_upper'] else "BUY" if current_price <= latest['bb_lower'] else "HOLD"
            }
        }
        
        # Calcular señal general
        buy_signals = sum(1 for s in signals.values() if s['signal'] == 'BUY')
        sell_signals = sum(1 for s in signals.values() if s['signal'] == 'SELL')
        
        if buy_signals > sell_signals:
            overall_signal = "BUY"
        elif sell_signals > buy_signals:
            overall_signal = "SELL"
        else:
            overall_signal = "HOLD"
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "overall_signal": overall_signal,
            "confidence": f"{max(buy_signals, sell_signals)}/4",
            "indicators": signals,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando señales para {symbol}: {str(e)}"
        )

@app.get("/pro-analysis/{symbol}")
async def get_professional_analysis(symbol: str, timeframe: str = "1h"):
    """
    🏆 Análisis profesional completo con todos los indicadores
    
    Args:
        symbol: Par de trading (ej: BTC/USDT)
        timeframe: Marco temporal (1m, 5m, 15m, 1h, 4h, 1d)
    
    Returns:
        Análisis técnico completo y profesional
    """
    try:
        # Formatear símbolo
        symbol = symbol.upper().replace('-', '/')
        
        # Obtener datos históricos extensos
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        current_price = df['close'].iloc[-1]
        
        # Calcular todos los indicadores
        fib_levels = AdvancedIndicators.fibonacci_retracement(df, 50)
        ichimoku = AdvancedIndicators.ichimoku_cloud(df)
        stochastic = AdvancedIndicators.stochastic_oscillator(df)
        williams_r = AdvancedIndicators.williams_percent_r(df)
        awesome_osc = AdvancedIndicators.awesome_oscillator(df)
        cci = AdvancedIndicators.commodity_channel_index(df)
        psar = AdvancedIndicators.parabolic_sar(df)
        patterns = AdvancedIndicators.detect_candlestick_patterns(df)
        
        # Recopilar todas las señales
        all_signals = [
            stochastic['signal'],
            williams_r['signal'],
            awesome_osc['signal'],
            cci['signal'],
            psar['signal']
        ]
        
        # Agregar señales de patrones
        for pattern in patterns['patterns']:
            if pattern['signal'] != 'NEUTRAL':
                all_signals.append(pattern['signal'])
        
        # Calcular consenso profesional
        buy_count = all_signals.count('BUY')
        sell_count = all_signals.count('SELL')
        total_signals = len(all_signals)
        
        if buy_count > sell_count:
            professional_signal = "BUY"
            confidence_score = round((buy_count / total_signals) * 100, 1)
        elif sell_count > buy_count:
            professional_signal = "SELL"
            confidence_score = round((sell_count / total_signals) * 100, 1)
        else:
            professional_signal = "HOLD"
            confidence_score = 50.0
        
        # Determinar fuerza de la señal
        if confidence_score >= 70:
            signal_strength = "Muy Fuerte"
        elif confidence_score >= 60:
            signal_strength = "Fuerte"
        elif confidence_score >= 50:
            signal_strength = "Moderada"
        else:
            signal_strength = "Débil"
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": round(current_price, 2),
            "professional_analysis": {
                "signal": professional_signal,
                "confidence_score": confidence_score,
                "signal_strength": signal_strength,
                "total_indicators": total_signals,
                "buy_signals": buy_count,
                "sell_signals": sell_count
            },
            "detailed_analysis": {
                "fibonacci": {
                    "current_level": "Calculado",
                    "key_support": round(fib_levels.level_618, 2),
                    "key_resistance": round(fib_levels.level_382, 2)
                },
                "ichimoku": {
                    "cloud_position": ichimoku.price_position,
                    "cloud_color": ichimoku.cloud_color
                },
                "oscillators": {
                    "stochastic": stochastic,
                    "williams_r": williams_r,
                    "awesome_oscillator": awesome_osc,
                    "cci": cci,
                    "parabolic_sar": psar
                },
                "patterns": patterns
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en análisis profesional para {symbol}: {str(e)}"
        )

# Ejecutar servidor si se ejecuta directamente
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True  # Hot reload en desarrollo
    )
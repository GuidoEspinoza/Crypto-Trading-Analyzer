"""📈 Advanced Sentiment Analysis System
Sistema avanzado de análisis de sentimiento y métricas on-chain
para trading de criptomonedas.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import requests
import json
from textblob import TextBlob
import re

logger = logging.getLogger(__name__)

@dataclass
class SentimentData:
    """Datos de sentimiento del mercado"""
    timestamp: datetime
    symbol: str
    
    # Sentimiento general
    overall_sentiment: str  # BULLISH, BEARISH, NEUTRAL
    sentiment_score: float  # -100 to 100
    confidence: float  # 0 to 100
    
    # Métricas on-chain
    fear_greed_index: Optional[float] = None
    social_volume: Optional[int] = None
    social_sentiment: Optional[float] = None
    
    # Métricas de red
    active_addresses: Optional[int] = None
    transaction_volume: Optional[float] = None
    network_growth: Optional[float] = None
    
    # Indicadores de flujo
    exchange_inflow: Optional[float] = None
    exchange_outflow: Optional[float] = None
    whale_activity: Optional[str] = None
    
    # Señales derivadas
    buy_pressure: float = 0.0
    sell_pressure: float = 0.0
    market_stress: str = "LOW"  # LOW, MEDIUM, HIGH
    
class SentimentAnalyzer:
    """🧠 Analizador avanzado de sentimiento"""
    
    def __init__(self):
        self.fear_greed_cache = {}
        self.social_data_cache = {}
        
    def analyze_sentiment(self, symbol: str, timeframe: str = "1h") -> SentimentData:
        """🎯 Análisis completo de sentimiento"""
        try:
            timestamp = datetime.now()
            
            # Obtener Fear & Greed Index
            fear_greed = self._get_fear_greed_index()
            
            # Análisis de redes sociales (simulado)
            social_data = self._analyze_social_sentiment(symbol)
            
            # Métricas on-chain (simulado)
            onchain_data = self._get_onchain_metrics(symbol)
            
            # Análisis de flujos de exchange
            flow_data = self._analyze_exchange_flows(symbol)
            
            # Calcular sentimiento general
            overall_sentiment, sentiment_score, confidence = self._calculate_overall_sentiment(
                fear_greed, social_data, onchain_data, flow_data
            )
            
            # Calcular presiones de compra/venta
            buy_pressure, sell_pressure = self._calculate_market_pressures(
                social_data, onchain_data, flow_data
            )
            
            # Evaluar estrés del mercado
            market_stress = self._evaluate_market_stress(
                fear_greed, sentiment_score, flow_data
            )
            
            return SentimentData(
                timestamp=timestamp,
                symbol=symbol,
                overall_sentiment=overall_sentiment,
                sentiment_score=sentiment_score,
                confidence=confidence,
                fear_greed_index=fear_greed,
                social_volume=social_data.get("volume", 0),
                social_sentiment=social_data.get("sentiment", 0),
                active_addresses=onchain_data.get("active_addresses"),
                transaction_volume=onchain_data.get("tx_volume"),
                network_growth=onchain_data.get("network_growth"),
                exchange_inflow=flow_data.get("inflow"),
                exchange_outflow=flow_data.get("outflow"),
                whale_activity=flow_data.get("whale_activity", "NORMAL"),
                buy_pressure=buy_pressure,
                sell_pressure=sell_pressure,
                market_stress=market_stress
            )
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return self._create_neutral_sentiment(symbol)
    
    def _get_fear_greed_index(self) -> Optional[float]:
        """Obtiene el índice Fear & Greed"""
        try:
            # Verificar cache (actualizar cada hora)
            now = datetime.now()
            if 'timestamp' in self.fear_greed_cache:
                cache_time = self.fear_greed_cache['timestamp']
                if (now - cache_time).seconds < 3600:  # 1 hora
                    return self.fear_greed_cache.get('value')
            
            # API pública de Fear & Greed Index
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    value = float(data['data'][0]['value'])
                    
                    # Actualizar cache
                    self.fear_greed_cache = {
                        'value': value,
                        'timestamp': now
                    }
                    
                    return value
            
            # Fallback: generar valor simulado basado en volatilidad
            return self._simulate_fear_greed_index()
            
        except Exception as e:
            logger.warning(f"Error getting Fear & Greed index: {str(e)}")
            return self._simulate_fear_greed_index()
    
    def _simulate_fear_greed_index(self) -> float:
        """Simula el índice Fear & Greed"""
        # Simulación basada en hora del día y volatilidad
        hour = datetime.now().hour
        base_value = 50  # Neutral
        
        # Variación por hora (mercados más nerviosos en ciertos horarios)
        if 8 <= hour <= 16:  # Horario de trading tradicional
            base_value += np.random.normal(0, 15)
        else:
            base_value += np.random.normal(-5, 10)  # Más pesimista fuera de horario
        
        return max(0, min(100, base_value))
    
    def _analyze_social_sentiment(self, symbol: str) -> Dict:
        """Analiza sentimiento en redes sociales"""
        try:
            # Simulación de análisis de redes sociales
            # En implementación real, se conectaría a APIs de Twitter, Reddit, etc.
            
            # Generar datos simulados realistas
            base_sentiment = np.random.normal(0, 30)  # -30 a +30
            volume = np.random.randint(1000, 10000)  # Volumen de menciones
            
            # Ajustar por símbolo (Bitcoin más mencionado)
            if symbol.upper() in ['BTC', 'BITCOIN']:
                volume *= 3
                base_sentiment += 5  # Sesgo ligeramente positivo
            elif symbol.upper() in ['ETH', 'ETHEREUM']:
                volume *= 2
                base_sentiment += 2
            
            # Normalizar sentimiento
            sentiment = max(-100, min(100, base_sentiment))
            
            return {
                "sentiment": sentiment,
                "volume": volume,
                "trending": volume > 5000,
                "keywords": self._generate_trending_keywords(symbol, sentiment)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing social sentiment: {str(e)}")
            return {"sentiment": 0, "volume": 0, "trending": False, "keywords": []}
    
    def _generate_trending_keywords(self, symbol: str, sentiment: float) -> List[str]:
        """Genera palabras clave trending simuladas"""
        positive_keywords = ["moon", "bullish", "pump", "hodl", "buy", "rally", "breakout"]
        negative_keywords = ["dump", "bearish", "crash", "sell", "dip", "correction", "fear"]
        neutral_keywords = ["analysis", "chart", "support", "resistance", "volume"]
        
        keywords = []
        
        if sentiment > 20:
            keywords.extend(np.random.choice(positive_keywords, 2, replace=False))
        elif sentiment < -20:
            keywords.extend(np.random.choice(negative_keywords, 2, replace=False))
        else:
            keywords.extend(np.random.choice(neutral_keywords, 2, replace=False))
        
        keywords.append(symbol.lower())
        return keywords
    
    def _get_onchain_metrics(self, symbol: str) -> Dict:
        """Obtiene métricas on-chain"""
        try:
            # Simulación de métricas on-chain
            # En implementación real, se conectaría a APIs como Glassnode, IntoTheBlock, etc.
            
            # Generar métricas simuladas
            base_addresses = 50000
            if symbol.upper() == 'BTC':
                base_addresses = 1000000
            elif symbol.upper() == 'ETH':
                base_addresses = 500000
            
            active_addresses = int(base_addresses * np.random.uniform(0.8, 1.2))
            tx_volume = np.random.uniform(1000000, 10000000)  # USD
            network_growth = np.random.normal(0, 5)  # % cambio
            
            return {
                "active_addresses": active_addresses,
                "tx_volume": tx_volume,
                "network_growth": network_growth,
                "nvt_ratio": np.random.uniform(20, 200),  # Network Value to Transactions
                "mvrv_ratio": np.random.uniform(0.5, 3.0),  # Market Value to Realized Value
                "hodl_waves": self._simulate_hodl_waves()
            }
            
        except Exception as e:
            logger.error(f"Error getting on-chain metrics: {str(e)}")
            return {}
    
    def _simulate_hodl_waves(self) -> Dict:
        """Simula distribución de HODL waves"""
        # Distribución de edad de UTXOs
        return {
            "1d_to_1w": np.random.uniform(5, 15),    # % de coins movidos recientemente
            "1w_to_1m": np.random.uniform(10, 25),
            "1m_to_3m": np.random.uniform(15, 30),
            "3m_to_6m": np.random.uniform(10, 20),
            "6m_to_1y": np.random.uniform(15, 25),
            "1y_to_2y": np.random.uniform(10, 20),
            "2y_plus": np.random.uniform(20, 40)     # HODLers de largo plazo
        }
    
    def _analyze_exchange_flows(self, symbol: str) -> Dict:
        """Analiza flujos de exchanges"""
        try:
            # Simulación de flujos de exchange
            base_flow = np.random.uniform(1000, 10000)  # BTC o ETH
            
            inflow = base_flow * np.random.uniform(0.8, 1.2)
            outflow = base_flow * np.random.uniform(0.8, 1.2)
            
            net_flow = inflow - outflow
            
            # Actividad de ballenas
            whale_threshold = base_flow * 0.1
            if abs(net_flow) > whale_threshold:
                whale_activity = "HIGH" if net_flow > 0 else "SELLING"
            else:
                whale_activity = "NORMAL"
            
            return {
                "inflow": inflow,
                "outflow": outflow,
                "net_flow": net_flow,
                "whale_activity": whale_activity,
                "exchange_reserves": np.random.uniform(100000, 500000)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing exchange flows: {str(e)}")
            return {"inflow": 0, "outflow": 0, "net_flow": 0, "whale_activity": "NORMAL"}
    
    def _calculate_overall_sentiment(self, fear_greed: Optional[float], 
                                   social_data: Dict, onchain_data: Dict, 
                                   flow_data: Dict) -> Tuple[str, float, float]:
        """Calcula sentimiento general"""
        scores = []
        weights = []
        
        # Fear & Greed Index (peso: 30%)
        if fear_greed is not None:
            fg_score = (fear_greed - 50) * 2  # Convertir 0-100 a -100 a 100
            scores.append(fg_score)
            weights.append(0.3)
        
        # Sentimiento social (peso: 25%)
        if 'sentiment' in social_data:
            scores.append(social_data['sentiment'])
            weights.append(0.25)
        
        # Métricas on-chain (peso: 25%)
        if 'network_growth' in onchain_data:
            network_score = onchain_data['network_growth'] * 10  # Escalar
            scores.append(max(-100, min(100, network_score)))
            weights.append(0.25)
        
        # Flujos de exchange (peso: 20%)
        if 'net_flow' in flow_data:
            # Flujo negativo (salida) = bullish, flujo positivo (entrada) = bearish
            flow_score = -flow_data['net_flow'] / 100  # Normalizar
            scores.append(max(-100, min(100, flow_score)))
            weights.append(0.2)
        
        # Calcular promedio ponderado
        if scores and weights:
            sentiment_score = np.average(scores, weights=weights)
            confidence = min(100, len(scores) * 25)  # Más fuentes = más confianza
        else:
            sentiment_score = 0
            confidence = 0
        
        # Determinar sentimiento categórico
        if sentiment_score > 20:
            overall_sentiment = "BULLISH"
        elif sentiment_score < -20:
            overall_sentiment = "BEARISH"
        else:
            overall_sentiment = "NEUTRAL"
        
        return overall_sentiment, sentiment_score, confidence
    
    def _calculate_market_pressures(self, social_data: Dict, 
                                  onchain_data: Dict, flow_data: Dict) -> Tuple[float, float]:
        """Calcula presiones de compra y venta"""
        buy_pressure = 0
        sell_pressure = 0
        
        # Presión social
        if 'sentiment' in social_data and 'volume' in social_data:
            social_impact = (social_data['sentiment'] / 100) * (social_data['volume'] / 10000)
            if social_impact > 0:
                buy_pressure += social_impact * 30
            else:
                sell_pressure += abs(social_impact) * 30
        
        # Presión de flujos
        if 'net_flow' in flow_data:
            flow_impact = flow_data['net_flow'] / 1000  # Normalizar
            if flow_impact < 0:  # Salida de exchanges = presión de compra
                buy_pressure += abs(flow_impact) * 40
            else:  # Entrada a exchanges = presión de venta
                sell_pressure += flow_impact * 40
        
        # Presión on-chain
        if 'network_growth' in onchain_data:
            network_impact = onchain_data['network_growth']
            if network_impact > 0:
                buy_pressure += network_impact * 20
            else:
                sell_pressure += abs(network_impact) * 20
        
        # Normalizar a 0-100
        buy_pressure = max(0, min(100, buy_pressure))
        sell_pressure = max(0, min(100, sell_pressure))
        
        return buy_pressure, sell_pressure
    
    def _evaluate_market_stress(self, fear_greed: Optional[float], 
                              sentiment_score: float, flow_data: Dict) -> str:
        """Evalúa el nivel de estrés del mercado"""
        stress_factors = 0
        
        # Factor Fear & Greed
        if fear_greed is not None:
            if fear_greed < 25:  # Extreme Fear
                stress_factors += 2
            elif fear_greed < 45:  # Fear
                stress_factors += 1
        
        # Factor sentimiento
        if abs(sentiment_score) > 50:  # Sentimiento extremo
            stress_factors += 1
        
        # Factor flujos
        if 'whale_activity' in flow_data:
            if flow_data['whale_activity'] in ['HIGH', 'SELLING']:
                stress_factors += 1
        
        # Determinar nivel de estrés
        if stress_factors >= 3:
            return "HIGH"
        elif stress_factors >= 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _create_neutral_sentiment(self, symbol: str) -> SentimentData:
        """Crea datos de sentimiento neutral por defecto"""
        return SentimentData(
            timestamp=datetime.now(),
            symbol=symbol,
            overall_sentiment="NEUTRAL",
            sentiment_score=0.0,
            confidence=0.0,
            buy_pressure=50.0,
            sell_pressure=50.0,
            market_stress="MEDIUM"
        )
    
    def get_sentiment_signals(self, sentiment_data: SentimentData) -> Dict[str, any]:
        """Genera señales basadas en análisis de sentimiento"""
        signals = {
            "sentiment_signal": "NEUTRAL",
            "strength": 0,
            "confidence": sentiment_data.confidence,
            "notes": []
        }
        
        # Señal principal basada en sentimiento
        if sentiment_data.sentiment_score > 30 and sentiment_data.buy_pressure > 60:
            signals["sentiment_signal"] = "BULLISH"
            signals["strength"] = min(100, sentiment_data.sentiment_score + sentiment_data.buy_pressure)
            signals["notes"].append("Strong bullish sentiment with high buy pressure")
        elif sentiment_data.sentiment_score < -30 and sentiment_data.sell_pressure > 60:
            signals["sentiment_signal"] = "BEARISH"
            signals["strength"] = min(100, abs(sentiment_data.sentiment_score) + sentiment_data.sell_pressure)
            signals["notes"].append("Strong bearish sentiment with high sell pressure")
        
        # Señales especiales
        if sentiment_data.fear_greed_index and sentiment_data.fear_greed_index < 20:
            signals["notes"].append("Extreme fear - potential buying opportunity")
        elif sentiment_data.fear_greed_index and sentiment_data.fear_greed_index > 80:
            signals["notes"].append("Extreme greed - potential selling opportunity")
        
        if sentiment_data.whale_activity == "SELLING":
            signals["notes"].append("High whale selling activity detected")
        elif sentiment_data.whale_activity == "HIGH":
            signals["notes"].append("High whale accumulation detected")
        
        if sentiment_data.market_stress == "HIGH":
            signals["notes"].append("High market stress - increased volatility expected")
        
        return signals
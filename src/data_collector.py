# data_collector.py
import pandas as pd
import requests
from smartapi import SmartConnect
from config import Config
import datetime
import time
import talib
import numpy as np

class DataCollector:
    def __init__(self):
        self.api = SmartConnect(api_key=Config.ANGEL_API_KEY)
        self.session = self._generate_session()
        self.symbols = {
            'NIFTY': {'token': '26000', 'exchange': 'NSE'},
            'BANKNIFTY': {'token': '26009', 'exchange': 'NSE'},
            'SENSEX': {'token': '1', 'exchange': 'BSE'}
        }
        
    def _generate_session(self):
        try:
            session = self.api.generateSession(
                Config.ANGEL_CLIENT_ID, 
                Config.ANGEL_PIN, 
                Config.ANGEL_TOKEN
            )
            return session
        except Exception as e:
            print(f"Session generation failed: {e}")
            return None
    
    def get_historical_data(self, symbol, interval='ONE_MINUTE', days=5):
        token = self.symbols[symbol]['token']
        exchange = self.symbols[symbol]['exchange']
        
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        try:
            data = self.api.getCandleData({
                "exchange": exchange,
                "symboltoken": token,
                "interval": interval,
                "fromdate": start_date.strftime('%Y-%m-%d %H:%M'),
                "todate": end_date.strftime('%Y-%m-%d %H:%M')
            })
            
            df = pd.DataFrame(data['data'], columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Calculate technical indicators
            df['rsi'] = talib.RSI(df['close'], timeperiod=14)
            df['macd'], df['macd_signal'], _ = talib.MACD(df['close'])
            df['bollinger_upper'], df['bollinger_middle'], df['bollinger_lower'] = talib.BBANDS(
                df['close'], timeperiod=20)
            
            return df
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None
    
    def get_option_chain(self, symbol, expiry_date):
        url = f"https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        response = requests.get(url)
        instruments = response.json()
        
        # Filter options for the given symbol and expiry
        options = [
            inst for inst in instruments 
            if inst['name'] == symbol and 
            inst['instrumenttype'] in ['CE', 'PE'] and
            inst['expiry'] == expiry_date
        ]
        
        return pd.DataFrame(options)
    
    def get_market_sentiment(self):
        # In a real implementation, this would fetch news and social media data
        # Here we'll simulate sentiment analysis
        return {
            'news_sentiment': np.random.uniform(-1, 1),  # -1 (bearish) to 1 (bullish)
            'social_sentiment': np.random.uniform(-1, 1),
            'overall_sentiment': np.random.uniform(-1, 1)
        }
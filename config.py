# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Angel One API credentials
    ANGEL_API_KEY = os.getenv('ANGEL_API_KEY')
    ANGEL_CLIENT_ID = os.getenv('ANGEL_CLIENT_ID')
    ANGEL_PIN = os.getenv('ANGEL_PIN')
    ANGEL_TOKEN = os.getenv('ANGEL_TOKEN')
    
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'trading_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Trading parameters
    MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', 1000))  # ₹1000 per trade
    MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', 5000))  # ₹5000 daily limit
    TRADING_HOURS = {'start': '09:15', 'end': '15:15'}
    
    # Model paths
    PREDICTION_MODEL_PATH = 'models/price_prediction.h5'
    SENTIMENT_MODEL_NAME = 'yiyanghkust/finbert-tone'
# ai_analyzer.py
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from transformers import BertTokenizer, BertForSequenceClassification
import torch
from config import Config

class AIAnalyzer:
    def __init__(self):
        # Load price prediction model
        self.price_model = load_model(Config.PREDICTION_MODEL_PATH)
        
        # Load sentiment analysis model
        self.sentiment_tokenizer = BertTokenizer.from_pretrained(Config.SENTIMENT_MODEL_NAME)
        self.sentiment_model = BertForSequenceClassification.from_pretrained(Config.SENTIMENT_MODEL_NAME)
    
    def predict_price_movement(self, historical_data):
        try:
            # Prepare data for the model
            last_60 = historical_data['close'].values[-60:]
            X = np.array([last_60])
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            # Make prediction
            prediction = self.price_model.predict(X)
            return float(prediction[0][0])
        except Exception as e:
            print(f"Price prediction error: {e}")
            return None
    
    def analyze_sentiment(self, text):
        try:
            inputs = self.sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = self.sentiment_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Return probabilities for [positive, neutral, negative]
            return {
                'positive': probs[0][0].item(),
                'neutral': probs[0][1].item(),
                'negative': probs[0][2].item()
            }
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return None
    
    def generate_signal(self, historical_data, sentiment_data, option_chain):
        try:
            # Technical analysis
            last_close = historical_data['close'].iloc[-1]
            rsi = historical_data['rsi'].iloc[-1]
            macd = historical_data['macd'].iloc[-1]
            macd_signal = historical_data['macd_signal'].iloc[-1]
            
            # Price prediction
            predicted_price = self.predict_price_movement(historical_data)
            
            # Sentiment analysis
            sentiment_score = sentiment_data['overall_sentiment']
            
            # Generate signal
            signal = {
                'symbol': 'NIFTY',  # Default for this example
                'timestamp': pd.Timestamp.now(),
                'last_close': last_close,
                'predicted_price': predicted_price,
                'rsi': rsi,
                'macd_diff': macd - macd_signal,
                'sentiment_score': sentiment_score,
                'action': None,  # Will be determined below
                'confidence': 0
            }
            
            # Decision logic
            confidence = 0
            
            # Bullish conditions
            bullish_conditions = 0
            if predicted_price > last_close:
                bullish_conditions += 1
            if rsi < 70 and rsi > 30:
                bullish_conditions += 0.5
            if macd > macd_signal:
                bullish_conditions += 1
            if sentiment_score > 0:
                bullish_conditions += 1
            
            # Bearish conditions
            bearish_conditions = 0
            if predicted_price < last_close:
                bearish_conditions += 1
            if rsi > 70:
                bearish_conditions += 1
            if macd < macd_signal:
                bearish_conditions += 1
            if sentiment_score < 0:
                bearish_conditions += 1
            
            # Determine final signal
            if bullish_conditions > bearish_conditions + 1:  # Strong bullish
                signal['action'] = 'BUY_CALL'
                confidence = bullish_conditions / 4
            elif bearish_conditions > bullish_conditions + 1:  # Strong bearish
                signal['action'] = 'BUY_PUT'
                confidence = bearish_conditions / 4
            else:
                signal['action'] = 'HOLD'
                confidence = 0.5 - abs(bullish_conditions - bearish_conditions) / 8
            
            signal['confidence'] = min(max(confidence, 0), 1)
            
            return signal
        except Exception as e:
            print(f"Signal generation error: {e}")
            return None
# trade_executor.py
from smartapi import SmartConnect
from config import Config
import datetime
import time
import pandas as pd
import numpy as np

class TradeExecutor:
    def __init__(self):
        self.api = SmartConnect(api_key=Config.ANGEL_API_KEY)
        self.session = self._generate_session()
        self.positions = []
        self.today_trades = []
        self.today_pnl = 0
        self.max_daily_loss = Config.MAX_DAILY_LOSS
        self.max_risk_per_trade = Config.MAX_RISK_PER_TRADE
        
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
    
    def get_option_symbol(self, underlying, expiry, strike, option_type):
        # This is a simplified version - in reality, you'd need to map to Angel One's symbol format
        expiry_str = expiry.strftime('%d%b%y').upper()
        return f"{underlying}{expiry_str}{strike}{option_type}"
    
    def place_order(self, signal):
        if self.today_pnl <= -self.max_daily_loss:
            print("Daily loss limit reached. No trades allowed.")
            return None
        
        try:
            # Determine expiry (next Thursday)
            today = datetime.date.today()
            days_to_thursday = (3 - today.weekday()) % 7
            if days_to_thursday == 0 and today.weekday() == 3 and datetime.datetime.now().hour >= 15:
                days_to_thursday = 7  # If today is Thursday after market hours, take next week's expiry
            expiry = today + datetime.timedelta(days=days_to_thursday)
            
            # Get ATM strike
            last_price = signal['last_close']
            strike_step = 50 if signal['symbol'] == 'NIFTY' else 100
            strike = round(last_price / strike_step) * strike_step
            
            # Determine option type
            option_type = 'CE' if signal['action'] == 'BUY_CALL' else 'PE'
            
            # Get option symbol
            tradingsymbol = self.get_option_symbol(
                underlying=signal['symbol'],
                expiry=expiry,
                strike=strike,
                option_type=option_type
            )
            
            # Calculate position size based on risk
            # Simplified calculation - in reality, you'd use option Greeks
            position_size = int(self.max_risk_per_trade / (last_price * 0.05))  # Assuming 5% of strike as risk
            
            if position_size < 1:
                print("Risk too high for current price. Trade skipped.")
                return None
            
            # Place order
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": tradingsymbol,
                "symboltoken": "0",  # This should be the actual token - needs lookup
                "transactiontype": "BUY",
                "exchange": "NFO",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": "0",
                "squareoff": "0",
                "stoploss": "0",
                "quantity": str(position_size)
            }
            
            response = self.api.placeOrder(order_params)
            
            if response['status']:
                trade = {
                    'order_id': response['data']['orderid'],
                    'symbol': tradingsymbol,
                    'type': option_type,
                    'strike': strike,
                    'quantity': position_size,
                    'entry_time': datetime.datetime.now(),
                    'entry_price': float(response['data']['averageprice']),
                    'stop_loss': None,
                    'take_profit': None,
                    'exit_time': None,
                    'exit_price': None,
                    'pnl': None,
                    'status': 'OPEN'
                }
                
                # Calculate SL/TP based on volatility
                atr = np.mean([
                    signal['last_close'] - signal['last_close'] * 0.01,
                    signal['last_close'] * 0.01
                ])  # Simplified ATR
                
                if option_type == 'CE':
                    trade['stop_loss'] = trade['entry_price'] - atr
                    trade['take_profit'] = trade['entry_price'] + 2 * atr
                else:
                    trade['stop_loss'] = trade['entry_price'] + atr
                    trade['take_profit'] = trade['entry_price'] - 2 * atr
                
                self.positions.append(trade)
                self.today_trades.append(trade)
                
                print(f"Order placed: {trade}")
                return trade
            else:
                print(f"Order failed: {response['message']}")
                return None
        except Exception as e:
            print(f"Order placement error: {e}")
            return None
    
    def monitor_positions(self):
        try:
            for position in self.positions:
                if position['status'] != 'OPEN':
                    continue
                
                # Get current price (simplified - in reality, use websocket or API)
                current_price = self.get_option_price(position['symbol'])
                
                # Check for SL/TP
                if position['type'] == 'CE':
                    if current_price <= position['stop_loss']:
                        self.exit_position(position, 'SL')
                    elif current_price >= position['take_profit']:
                        self.exit_position(position, 'TP')
                else:  # PE
                    if current_price >= position['stop_loss']:
                        self.exit_position(position, 'SL')
                    elif current_price <= position['take_profit']:
                        self.exit_position(position, 'TP')
        except Exception as e:
            print(f"Position monitoring error: {e}")
    
    def exit_position(self, position, reason):
        try:
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": position['symbol'],
                "symboltoken": "0",  # This should be the actual token
                "transactiontype": "SELL",
                "exchange": "NFO",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": "0",
                "quantity": str(position['quantity'])
            }
            
            response = self.api.placeOrder(order_params)
            
            if response['status']:
                exit_price = float(response['data']['averageprice'])
                pnl = (exit_price - position['entry_price']) * position['quantity']
                if position['type'] == 'PE':
                    pnl = -pnl  # Inverse for PUTs
                
                position.update({
                    'exit_time': datetime.datetime.now(),
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'status': 'CLOSED',
                    'exit_reason': reason
                })
                
                self.today_pnl += pnl
                print(f"Position closed: {position}")
            else:
                print(f"Exit order failed: {response['message']}")
        except Exception as e:
            print(f"Position exit error: {e}")
    
    def get_option_price(self, symbol):
        # In reality, you'd use websocket or API to get real-time price
        # Here we return a simulated price
        return np.random.uniform(10, 200)
    
    def cancel_all_orders(self):
        try:
            orders = self.api.orderBook()
            for order in orders['data']:
                if order['status'] == 'open':
                    self.api.cancelOrder(order['orderid'])
            print("All open orders cancelled")
        except Exception as e:
            print(f"Order cancellation error: {e}")
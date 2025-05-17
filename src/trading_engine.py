# trading_engine.py
import time
import schedule
from datetime import datetime, time as dt_time
from data_collector import DataCollector
from ai_analyzer import AIAnalyzer
from trade_executor import TradeExecutor
from config import Config
import threading

class TradingEngine:
    def __init__(self, auto_trade=True):
        self.auto_trade = auto_trade
        self.data_collector = DataCollector()
        self.ai_analyzer = AIAnalyzer()
        self.trade_executor = TradeExecutor()
        self.running = False
        
    def run(self):
        self.running = True
        print("Trading engine started")
        
        # Main loop
        while self.running:
            current_time = datetime.now().time()
            trading_start = dt_time(9, 15)
            trading_end = dt_time(15, 15)
            
            # Check if within trading hours
            if trading_start <= current_time <= trading_end:
                self.execute_trading_cycle()
            
            time.sleep(60)  # Run every minute
    
    def execute_trading_cycle(self):
        try:
            print("\n" + "="*50)
            print(f"Executing trading cycle at {datetime.now()}")
            
            # 1. Collect market data
            print("Collecting market data...")
            nifty_data = self.data_collector.get_historical_data('NIFTY')
            sentiment_data = self.data_collector.get_market_sentiment()
            option_chain = self.data_collector.get_option_chain('NIFTY', '2024-05-30')  # Example expiry
            
            # 2. AI Analysis
            print("Running AI analysis...")
            signal = self.ai_analyzer.generate_signal(nifty_data, sentiment_data, option_chain)
            print(f"Generated signal: {signal}")
            
            # 3. Execute trades (if in auto mode and signal is strong)
            if self.auto_trade and signal and signal['action'] in ['BUY_CALL', 'BUY_PUT'] and signal['confidence'] > 0.7:
                print("Executing trade...")
                self.trade_executor.place_order(signal)
            
            # 4. Monitor open positions
            print("Monitoring positions...")
            self.trade_executor.monitor_positions()
            
            print("Trading cycle completed")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"Error in trading cycle: {e}")
    
    def start_scheduled(self):
        # Schedule trading to run every minute during market hours
        schedule.every().minute.between(
            Config.TRADING_HOURS['start'], 
            Config.TRADING_HOURS['end']
        ).do(self.execute_trading_cycle)
        
        print(f"Scheduled trading started (runs every minute between {Config.TRADING_HOURS['start']} and {Config.TRADING_HOURS['end']})")
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        self.running = False
        self.trade_executor.cancel_all_orders()
        print("Trading engine stopped")

def main():
    engine = TradingEngine(auto_trade=True)
    
    try:
        # Run in a separate thread
        trading_thread = threading.Thread(target=engine.start_scheduled)
        trading_thread.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()
        trading_thread.join()
        print("Application terminated")

if __name__ == "__main__":
    main()
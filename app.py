from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from trading_engine import TradingEngine
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global trading engine instance
engine = TradingEngine(auto_trade=False)
engine_thread = None

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# API Endpoints for Trading Controls
@app.route('/api/trading/start', methods=['POST'])
def start_auto_trading():
    global engine_thread
    
    engine.auto_trade = True
    if engine_thread is None or not engine_thread.is_alive():
        engine_thread = threading.Thread(target=engine.run)
        engine_thread.daemon = True
        engine_thread.start()
    
    return jsonify({
        'status': 'success',
        'message': 'Auto trading started',
        'is_auto_trading': engine.auto_trade
    })

@app.route('/api/trading/stop', methods=['POST'])
def stop_auto_trading():
    engine.auto_trade = False
    return jsonify({
        'status': 'success',
        'message': 'Auto trading stopped',
        'is_auto_trading': engine.auto_trade
    })

@app.route('/api/trading/status', methods=['GET'])
def get_trading_status():
    return jsonify({
        'is_auto_trading': engine.auto_trade,
        'positions': engine.trade_executor.positions,
        'today_trades': engine.trade_executor.today_trades,
        'today_pnl': engine.trade_executor.today_pnl,
        'equity': 100000,  # Example value
        'used_margin': 25000  # Example value
    })

@app.route('/api/trading/manual', methods=['POST'])
def place_manual_trade():
    data = request.json
    action = data.get('action')
    symbol = data.get('symbol', 'NIFTY')
    quantity = int(data.get('quantity', 1))
    
    if action not in ['BUY_CALL', 'BUY_PUT']:
        return jsonify({'status': 'error', 'message': 'Invalid action'})
    
    # Create a signal for manual trading
    signal = {
        'symbol': symbol,
        'action': action,
        'last_close': 18000,  # Will be replaced with real data
        'confidence': 1.0
    }
    
    result = engine.trade_executor.place_order(signal, quantity=quantity)
    if result:
        return jsonify({'status': 'success', 'data': result})
    return jsonify({'status': 'error', 'message': 'Trade execution failed'})

@app.route('/api/trading/positions', methods=['GET'])
def get_positions():
    return jsonify({
        'positions': engine.trade_executor.positions,
        'today_trades': engine.trade_executor.today_trades,
        'today_pnl': engine.trade_executor.today_pnl
    })

@app.route('/api/trading/close', methods=['POST'])
def close_position():
    position_id = request.json.get('position_id')
    if position_id and engine.trade_executor.exit_position_by_id(position_id):
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Failed to close position'})

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status_update', {
        'is_auto_trading': engine.auto_trade,
        'time': datetime.now().isoformat()
    })

def background_updates():
    """Send periodic updates to all clients"""
    while True:
        socketio.sleep(5)
        try:
            socketio.emit('market_update', {
                'time': datetime.now().isoformat(),
                'positions': engine.trade_executor.positions,
                'today_pnl': engine.trade_executor.today_pnl,
                'signals': get_latest_signals()  # Implement this function
            })
        except Exception as e:
            print(f"Error in background updates: {e}")

# Start background thread when starting the app
socketio.start_background_task(background_updates)

if __name__ == '__main__':
    socketio.run(app, debug=True)
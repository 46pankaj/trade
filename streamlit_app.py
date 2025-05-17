# streamlit_app.py
import streamlit as st
from datetime import datetime, time
import pandas as pd
import numpy as np
from trading_engine import TradingEngine
from data_collector import DataCollector
from ai_analyzer import AIAnalyzer
import plotly.graph_objects as go

# Initialize the trading components
@st.cache_resource
def init_components():
    return {
        'data_collector': DataCollector(),
        'ai_analyzer': AIAnalyzer(),
        'trading_engine': TradingEngine(auto_trade=False)
    }

components = init_components()

# App title and config
st.set_page_config(page_title="AI Trading Platform", layout="wide")
st.title("AI Trading Platform Dashboard")

# Custom CSS to match the HTML styling
st.markdown("""
<style>
:root {
    --dark-bg: #1a1a2e;
    --darker-bg: #16213e;
    --primary: #0f3460;
    --secondary: #00b4d8;
    --success: #06d6a0;
    --danger: #ef476f;
    --warning: #ffd166;
    --text-light: #e6e6e6;
    --text-muted: #b8b8b8;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: var(--dark-bg);
    color: var(--text-light);
}

.stApp {
    background-color: var(--dark-bg);
}

.stSidebar {
    background-color: var(--darker-bg) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.stTabs [data-baseweb="tab-list"] {
    background-color: var(--darker-bg);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stTabs [aria-selected="true"] {
    background-color: var(--primary) !important;
    color: white !important;
}

.stDataFrame {
    background-color: var(--darker-bg) !important;
    color: var(--text-light) !important;
}

.stDataFrame th {
    background-color: rgba(0, 0, 0, 0.3) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

.stDataFrame td {
    border-color: rgba(255, 255, 255, 0.1) !important;
}

.profit {
    color: var(--success) !important;
    font-weight: 600 !important;
}

.loss {
    color: var(--danger) !important;
    font-weight: 600 !important;
}

.signal-buy {
    background-color: rgba(6, 214, 160, 0.2) !important;
    border-left: 3px solid var(--success) !important;
}

.signal-sell {
    background-color: rgba(239, 71, 111, 0.2) !important;
    border-left: 3px solid var(--danger) !important;
}

.signal-hold {
    background-color: rgba(255, 209, 102, 0.2) !important;
    border-left: 3px solid var(--warning) !important;
}

.status-badge {
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.status-active {
    background-color: rgba(6, 214, 160, 0.2);
    color: var(--success);
}

.status-inactive {
    background-color: rgba(239, 71, 111, 0.2);
    color: var(--danger);
}
</style>
""", unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.header("Trading Controls")
    auto_trade = st.toggle("Auto Trading", value=False)
    
    if auto_trade:
        st.success("Auto trading is ACTIVE")
    else:
        st.warning("Auto trading is INACTIVE")
    
    st.subheader("Risk Management")
    risk_per_trade = st.slider("Risk per Trade (₹)", 500, 5000, 1000, 500)
    daily_loss_limit = st.slider("Daily Loss Limit (₹)", 1000, 10000, 5000, 1000)
    
    if st.button("Emergency Stop", type="primary"):
        components['trading_engine'].auto_trade = False
        st.rerun()

# Main dashboard layout
tab1, tab2, tab3 = st.tabs(["Market Overview", "Trading Signals", "Positions"])

with tab1:
    # Market data visualization
    st.subheader("NIFTY 50 - Live Chart")
    
    # Get historical data
    nifty_data = components['data_collector'].get_historical_data('NIFTY')
    
    if nifty_data is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=nifty_data.index,
            y=nifty_data['close'],
            name='Close Price',
            line=dict(color='#00b4d8')
        ))
        
        # Add indicators
        fig.add_trace(go.Scatter(
            x=nifty_data.index,
            y=nifty_data['bollinger_upper'],
            name='Upper Bollinger',
            line=dict(color='rgba(255, 209, 102, 0.5)')
        ))
        
        fig.add_trace(go.Scatter(
            x=nifty_data.index,
            y=nifty_data['bollinger_lower'],
            name='Lower Bollinger',
            line=dict(color='rgba(255, 209, 102, 0.5)')
        ))
        
        fig.update_layout(
            height=500,
            xaxis_rangeslider_visible=False,
            margin=dict(l=20, r=20, t=30, b=20),
            plot_bgcolor='rgba(22, 33, 62, 1)',
            paper_bgcolor='rgba(22, 33, 62, 1)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Failed to load market data")

with tab2:
    # Trading signals
    st.subheader("Latest Trading Signals")
    
    # Sample signals data
    signals = pd.DataFrame([
        {
            'time': '09:15:23',
            'symbol': 'NIFTY',
            'signal': 'BUY',
            'confidence': '85%',
            'price': '18,245.30',
            'predicted': '18,320.50 (+0.4%)',
            'rsi': '62',
            'macd': '↑ Bullish',
            'sentiment': '72% Positive',
            'action': 'CALL 18200CE'
        },
        {
            'time': '09:30:45',
            'symbol': 'BANKNIFTY',
            'signal': 'SELL',
            'confidence': '78%',
            'price': '39,876.20',
            'predicted': '39,540.10 (-0.8%)',
            'rsi': '71',
            'macd': '↓ Bearish',
            'sentiment': '64% Negative',
            'action': 'PUT 39800PE'
        },
        {
            'time': '10:05:12',
            'symbol': 'NIFTY',
            'signal': 'HOLD',
            'confidence': '65%',
            'price': '18,210.75',
            'predicted': '18,195.30 (-0.1%)',
            'rsi': '55',
            'macd': '→ Neutral',
            'sentiment': '51% Neutral',
            'action': 'No Action'
        }
    ])
    
    # Apply styling based on signal type
    def color_signal(val):
        if val == 'BUY':
            return 'color: #06d6a0; font-weight: bold'
        elif val == 'SELL':
            return 'color: #ef476f; font-weight: bold'
        else:
            return 'color: #ffd166; font-weight: bold'
    
    styled_signals = signals.style.applymap(color_signal, subset=['signal'])
    st.dataframe(styled_signals, use_container_width=True, hide_index=True)
    
    if st.button("Generate New Signal"):
        with st.spinner("Analyzing market..."):
            nifty_data = components['data_collector'].get_historical_data('NIFTY')
            sentiment_data = components['data_collector'].get_market_sentiment()
            option_chain = components['data_collector'].get_option_chain('NIFTY', '2024-05-30')
            
            if nifty_data is not None:
                signal = components['ai_analyzer'].generate_signal(
                    nifty_data, 
                    sentiment_data, 
                    option_chain
                )
                
                if signal:
                    st.success("Signal generated successfully!")
                    
                    # Display signal details
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Last Close", f"₹{signal['last_close']:.2f}")
                        st.metric("Predicted Price", f"₹{signal['predicted_price']:.2f}")
                        st.metric("RSI", f"{signal['rsi']:.1f}")
                    
                    with col2:
                        st.metric("MACD Diff", f"{signal['macd_diff']:.2f}")
                        st.metric("Sentiment Score", f"{signal['sentiment_score']*100:.1f}%")
                        st.metric("Confidence", f"{signal['confidence']*100:.1f}%")
                    
                    # Action recommendation
                    if signal['action'] == 'BUY_CALL':
                        st.success(f"Recommendation: BUY CALL (Confidence: {signal['confidence']*100:.1f}%)")
                    elif signal['action'] == 'BUY_PUT':
                        st.error(f"Recommendation: BUY PUT (Confidence: {signal['confidence']*100:.1f}%)")
                    else:
                        st.warning(f"Recommendation: HOLD (Confidence: {signal['confidence']*100:.1f}%)")

with tab3:
    # Positions and trade history
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Positions")
        
        # Sample positions data
        positions = pd.DataFrame([
            {
                'symbol': 'NIFTY22SEP18200CE',
                'type': 'CE',
                'qty': 75,
                'entry': '₹120.50',
                'ltp': '₹145.75',
                'pnl': '+₹1,893.75',
                'sl': '₹95.00',
                'tp': '₹180.00',
                'action': 'Trailing'
            },
            {
                'symbol': 'BANKNIFTY22SEP39800PE',
                'type': 'PE',
                'qty': 50,
                'entry': '₹85.25',
                'ltp': '₹92.40',
                'pnl': '+₹357.50',
                'sl': '₹70.00',
                'tp': '₹120.00',
                'action': 'Active'
            },
            {
                'symbol': 'NIFTY22SEP18000PE',
                'type': 'PE',
                'qty': 25,
                'entry': '₹65.80',
                'ltp': '₹58.20',
                'pnl': '-₹190.00',
                'sl': '₹55.00',
                'tp': '₹90.00',
                'action': 'Active'
            }
        ])
        
        # Color P&L values
        def color_pnl(val):
            if val.startswith('+'):
                return 'color: #06d6a0'
            elif val.startswith('-'):
                return 'color: #ef476f'
            return ''
        
        styled_positions = positions.style.applymap(color_pnl, subset=['pnl'])
        st.dataframe(styled_positions, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Today's Trade History")
        
        # Sample trade history
        history = pd.DataFrame([
            {
                'time': '09:15:45',
                'symbol': 'NIFTY22SEP18200CE',
                'type': 'BUY CE',
                'qty': 75,
                'entry': '₹120.50',
                'exit': '',
                'pnl': ''
            },
            {
                'time': '09:20:30',
                'symbol': 'BANKNIFTY22SEP39800PE',
                'type': 'BUY PE',
                'qty': 50,
                'entry': '₹85.25',
                'exit': '',
                'pnl': ''
            },
            {
                'time': '09:45:15',
                'symbol': 'NIFTY22SEP18000PE',
                'type': 'BUY PE',
                'qty': 25,
                'entry': '₹65.80',
                'exit': '',
                'pnl': ''
            },
            {
                'time': '10:30:22',
                'symbol': 'NIFTY22SEP18100CE',
                'type': 'SELL CE',
                'qty': 50,
                'entry': '₹92.40',
                'exit': '₹105.75',
                'pnl': '+₹667.50'
            }
        ])
        
        # Color P&L values
        styled_history = history.style.applymap(color_pnl, subset=['pnl'])
        st.dataframe(styled_history, use_container_width=True, hide_index=True)

# Account summary in sidebar
with st.sidebar:
    st.subheader("Account Summary")
    st.markdown("""
    <div style="margin-bottom: 10px;">
        <span>Available Margin:</span>
        <span style="float: right; font-weight: bold;">₹78,452.00</span>
    </div>
    <div style="margin-bottom: 10px;">
        <span>Utilized Margin:</span>
        <span style="float: right; font-weight: bold;">₹21,548.00</span>
    </div>
    <div style="margin-bottom: 10px;">
        <span>Today's P&L:</span>
        <span style="float: right; font-weight: bold; color: #06d6a0;">+₹3,245.00</span>
    </div>
    <div style="margin-bottom: 10px;">
        <span>Open Positions:</span>
        <span style="float: right; font-weight: bold;">3</span>
    </div>
    <div>
        <span>Today's Trades:</span>
        <span style="float: right; font-weight: bold;">7</span>
    </div>
    """, unsafe_allow_html=True)

# Manual trading in sidebar
with st.sidebar:
    st.subheader("Manual Trading")
    symbol = st.selectbox("Symbol", ['NIFTY 50', 'BANK NIFTY', 'SENSEX'])
    option_type = st.radio("Option Type", ['Call', 'Put'])
    quantity = st.number_input("Quantity", min_value=1, value=1)
    
    if st.button("Place Trade"):
        st.success(f"Trade placed for {quantity} lots of {symbol} {option_type}")

# Run the trading engine in the background
if auto_trade:
    components['trading_engine'].auto_trade = True
    if not components['trading_engine'].running:
        import threading
        trading_thread = threading.Thread(target=components['trading_engine'].run)
        trading_thread.daemon = True
        trading_thread.start()
else:
    components['trading_engine'].auto_trade = False
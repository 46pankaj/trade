# train_model.py
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Generate some dummy data for demonstration
def generate_data():
    dates = pd.date_range(start='2020-01-01', end='2023-12-31')
    prices = np.cumsum(np.random.normal(0, 1, len(dates))) + 100
    return pd.DataFrame({'date': dates, 'close': prices})

df = generate_data()

# Prepare data for LSTM
def create_dataset(data, window_size=60):
    X, y = [], []
    for i in range(len(data)-window_size-1):
        X.append(data[i:(i+window_size)])
        y.append(data[i+window_size])
    return np.array(X), np.array(y)

X, y = create_dataset(df['close'].values)
X = X.reshape((X.shape[0], X.shape[1], 1))

# Build and train model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(60, 1)),
    LSTM(50),
    Dense(1)
])
model.compile(optimizer='adam', loss='mse')
model.fit(X, y, epochs=10, batch_size=32)

# Save model
model.save('models/price_prediction.h5')
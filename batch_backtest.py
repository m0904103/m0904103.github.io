import json
import os
import yfinance as yf
import pandas as pd
import numpy as np
import time

file_path = os.path.join('frontend', 'public', 'scan_results.json')
assets_dir = os.path.join('frontend', 'public', 'assets')
os.makedirs(assets_dir, exist_ok=True)

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def calculate_backtest_stats(df):
    if len(df) < 65: return None
    df['ma60'] = df['Close'].rolling(window=60).mean()
    df = df.dropna().reset_index()
    pos = 0
    trades = []
    entry_price = 0
    for i in range(len(df)):
        if df['Close'].iloc[i] > df['ma60'].iloc[i] and pos == 0:
            pos = 1
            entry_price = df['Close'].iloc[i]
        elif df['Close'].iloc[i] < df['ma60'].iloc[i] and pos == 1:
            pos = 0
            exit_price = df['Close'].iloc[i]
            trades.append((exit_price - entry_price) / entry_price)
    if pos == 1:
        trades.append((df['Close'].iloc[-1] - entry_price) / entry_price)
    if not trades: return {"win_rate": 0, "total_return": 0}
    win_rate = round(len([t for t in trades if t > 0]) / len(trades) * 100, 1)
    total_return = round((np.prod([1 + t for t in trades]) - 1) * 100, 1)
    return {"win_rate": win_rate, "total_return": total_return}

print(f"Starting batch update for {len(data['stocks'])} stocks...")

for i, stock in enumerate(data['stocks']):
    sym = stock['symbol']
    if 'backtest' in stock and stock['backtest'].get('win_rate', 0) > 0:
        continue # Skip already processed with data
        
    print(f"[{i+1}/{len(data['stocks'])}] Updating {sym}...")
    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period='2y')
        if df.empty or len(df) < 10:
            print(f"  No data for {sym}")
            continue
            
        # Calculate Backtest
        bt = calculate_backtest_stats(df)
        if bt:
            stock['backtest'] = bt
            
        # Save History for UI Chart
        # Only save last 120 days for UI performance
        ui_df = df.tail(120)
        history_list = []
        for index, row in ui_df.iterrows():
            history_list.append({
                "time": index.strftime('%Y-%m-%d'),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2)
            })
        history_path = os.path.join(assets_dir, f"history_{sym}.json")
        with open(history_path, 'w', encoding='utf-8') as hf:
            json.dump(history_list, hf, ensure_ascii=False)
            
    except Exception as e:
        print(f"  Error {sym}: {e}")
    
    # Simple rate limiting to avoid YF ban
    if i % 10 == 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# Final Save
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Batch update complete!")

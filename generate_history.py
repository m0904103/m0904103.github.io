import yfinance as yf
import pandas as pd
import json
import os
import time

def generate_history():
    # Read stocks from scan_results.json
    try:
        with open('scan_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            stocks = data.get('stocks', [])
    except Exception as e:
        print(f"Error reading scan_results.json: {e}")
        return

    # Create assets directory if not exists
    os.makedirs('trading/assets', exist_ok=True)

    for stock in stocks:
        symbol = stock['symbol']
        print(f"Generating history for {symbol}...")
        
        try:
            # Download 6 months of data
            df = yf.download(symbol, period="8mo", progress=False)
            if df.empty:
                print(f"  Empty data for {symbol}")
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Calculate MA60
            df['ma60'] = df['Close'].rolling(window=60).mean()

            # Format for Lightweight Charts
            history = []
            for idx, row in df.iterrows():
                history.append({
                    "time": idx.strftime('%Y-%m-%d'),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "ma60": float(row['ma60']) if not pd.isna(row['ma60']) else None
                })

            # Save to assets
            filename = f"trading/assets/history_{symbol}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False)
            
            print(f"  Success: {filename}")
            time.sleep(0.5) # Avoid rate limit
            
        except Exception as e:
            print(f"  Failed {symbol}: {e}")

if __name__ == "__main__":
    generate_history()

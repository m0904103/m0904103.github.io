import json
import os
import yfinance as yf

# US stock to add
new_symbols = {
    'MSFT': 'Microsoft (AI雲端與軟體霸主)'
}

file_path = os.path.join('frontend', 'public', 'scan_results.json')
assets_dir = os.path.join('frontend', 'public', 'assets')
os.makedirs(assets_dir, exist_ok=True)

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

existing_symbols = [s['symbol'] for s in data['stocks']]

print("Fetching data for MSFT...")
for sym, name in new_symbols.items():
    if sym in existing_symbols:
        print(f"{sym} already exists, skipping.")
        continue
        
    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period='120d')
        if df.empty or len(df) < 2:
            print(f"No data for {sym}")
            continue
            
        latest_close = round(float(df['Close'].iloc[-1]), 2)
        prev_close = float(df['Close'].iloc[-2])
        change = round(((latest_close - prev_close) / prev_close) * 100, 2)
        
        ma60 = 0
        if len(df) >= 60:
            ma60 = round(float(df['Close'].rolling(60).mean().iloc[-1]), 2)
        else:
            ma60 = latest_close
            
        is_regular = latest_close > ma60
        signal = "Strong Buy" if is_regular else "Hold"
        tactic = "「AI雲端霸主」：微軟為AI基建與軟體雙引擎，長期核心持股。" if is_regular else "「破位出局」：結構破壞！生命線之下不買弱勢股。"
        
        new_stock = {
            "symbol": sym,
            "name": name,
            "signal": signal,
            "close": latest_close,
            "ma60": ma60,
            "market": "us",
            "change": change,
            "vol_ratio": 1.2,
            "tactic": tactic,
            "is_regular": is_regular,
            "sect": "武當正規軍" if is_regular else "江湖散兵",
            "plan": {
                "entry": latest_close,
                "sl": ma60,
                "tp": round(latest_close * 1.2, 2) # 20% TP for large caps
            }
        }
        data['stocks'].append(new_stock)
        
        # Save history json
        history_list = []
        for index, row in df.iterrows():
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
            
        print(f"Added {sym} and generated history.")
    except Exception as e:
        print(f"Error processing {sym}: {e}")

# Save updated database
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Finished adding MSFT!")

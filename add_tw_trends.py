import json
import os
import yfinance as yf

# Trending Taiwan stocks to add
new_symbols = {
    # Memory
    '4967.TW': '十銓',
    '5289.TW': '宜鼎',
    # Silicon Photonics
    '3163.TW': '波若威',
    '4979.TW': '華星光',
    '4991.TW': '環宇-KY',
    '3081.TW': '聯亞',
    '4977.TW': '眾達-KY',
    # PCB
    '8358.TW': '金居',
    '3189.TW': '景碩',
    '6251.TW': '定穎投控',
    '2383.TW': '台光電',
    '1815.TW': '富喬',
    '6274.TW': '台燿',
    '2467.TW': '志聖'
}

file_path = os.path.join('frontend', 'public', 'scan_results.json')
assets_dir = os.path.join('frontend', 'public', 'assets')
os.makedirs(assets_dir, exist_ok=True)

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

existing_symbols = [s['symbol'] for s in data['stocks']]

print("Fetching data for new Taiwan trending stocks...")
for sym, name in new_symbols.items():
    if sym in existing_symbols:
        print(f"{sym} already exists, skipping.")
        continue
        
    try:
        # Note: Yahoo Finance uses .TW for Taiwan stocks, occasionally .TWO for OTC.
        # Let's try .TW first. If it fails, try .TWO.
        ticker = yf.Ticker(sym)
        df = ticker.history(period='120d')
        
        if df.empty or len(df) < 2:
            print(f"No data for {sym}, trying .TWO...")
            sym_two = sym.replace('.TW', '.TWO')
            ticker = yf.Ticker(sym_two)
            df = ticker.history(period='120d')
            if df.empty or len(df) < 2:
                print(f"Still no data for {sym_two}, skipping.")
                continue
            sym = sym_two # Use the OTC symbol
            
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
        tactic = "「趨勢輪動」：基本面增長確認，沿生命線操作。" if is_regular else "「破位出局」：結構破壞！生命線之下不買弱勢股。觀望不動是高階決策。"
        
        new_stock = {
            "symbol": sym,
            "name": name,
            "signal": signal,
            "close": latest_close,
            "ma60": ma60,
            "market": "tw",
            "change": change,
            "vol_ratio": 1.5,
            "tactic": tactic,
            "is_regular": is_regular,
            "sect": "武當正規軍" if is_regular else "江湖散兵",
            "plan": {
                "entry": latest_close,
                "sl": ma60,
                "tp": round(latest_close * 1.2, 2)
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
            
        print(f"Added {sym} ({name}) and generated history.")
    except Exception as e:
        print(f"Error processing {sym}: {e}")

# Save updated database
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Finished adding Taiwan trending stocks!")

import json
import os
import yfinance as yf

file_path = os.path.join('frontend', 'public', 'scan_results.json')
assets_dir = os.path.join('frontend', 'public', 'assets')

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find and update MSFT
for stock in data['stocks']:
    if stock['symbol'] == 'MSFT':
        ticker = yf.Ticker('MSFT')
        df = ticker.history(period='120d')
        if not df.empty and len(df) >= 2:
            latest_close = round(float(df['Close'].iloc[-1]), 2)
            prev_close = float(df['Close'].iloc[-2])
            change = round(((latest_close - prev_close) / prev_close) * 100, 2)
            
            ma60 = round(float(df['Close'].rolling(60).mean().iloc[-1]), 2) if len(df) >= 60 else latest_close
            is_regular = latest_close > ma60
            
            stock['name'] = 'Microsoft (AI雲端與軟體霸主)'
            stock['close'] = latest_close
            stock['ma60'] = ma60
            stock['change'] = change
            stock['is_regular'] = is_regular
            stock['signal'] = "Strong Buy" if is_regular else "Hold"
            stock['tactic'] = "「AI雲端霸主」：微軟為AI基建與軟體雙引擎，長期核心持股。" if is_regular else "「破位出局」：結構破壞！生命線之下不買弱勢股。"
            stock['sect'] = "武當正規軍" if is_regular else "江湖散兵"
            stock['plan'] = {
                "entry": latest_close,
                "sl": ma60,
                "tp": round(latest_close * 1.2, 2)
            }
            
            # Update history
            history_list = []
            for index, row in df.iterrows():
                history_list.append({
                    "time": index.strftime('%Y-%m-%d'),
                    "open": round(float(row['Open']), 2),
                    "high": round(float(row['High']), 2),
                    "low": round(float(row['Low']), 2),
                    "close": round(float(row['Close']), 2)
                })
            history_path = os.path.join(assets_dir, "history_MSFT.json")
            with open(history_path, 'w', encoding='utf-8') as hf:
                json.dump(history_list, hf, ensure_ascii=False)
                
            print("Successfully updated MSFT with full data and tags.")
        break

# Save updated database
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Database saved.")

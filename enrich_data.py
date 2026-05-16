import json
import os
import pandas as pd
import numpy as np

# Load database
file_path = os.path.join('frontend', 'public', 'scan_results.json')
assets_dir = os.path.join('frontend', 'public', 'assets')

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sector Mapping
sector_map = {
    # US
    'NVDA': 'AI 基建', 'AVGO': 'AI 基建', 'AMD': 'AI 基建', 'ARM': 'AI 基建', 'ASML': 'AI 基建', 
    'MU': 'AI 基建', 'DELL': 'AI 基建', 'VRT': 'AI 基建', 'PWR': 'AI 基建',
    'MSFT': 'AI 軟體', 'PLTR': 'AI 軟體', 'GOOGL': 'AI 軟體', 'ORCL': 'AI 軟體', 'SNPS': 'AI 軟體', 
    'ADBE': 'AI 軟體', 'RDDT': 'AI 軟體',
    'ASTS': '太空經濟', 'RKLB': '太空經濟', 'LUNR': '太空經濟', 'PL': '太空經濟',
    'OKLO': '核能/能源', 'GEV': '核能/能源', 'NEE': '核能/能源', 'VST': '核能/能源',
    'AAPL': '消費電子', 'TSLA': '電動車/AI', 'AMZN': '電商/雲端', 'META': '社群/AI',
    # TW (Simplified)
    '2330.TW': '台股權值', '2317.TW': '台股權值', '2454.TW': '台股權值', '2308.TW': '台股權值',
    '6442.TW': '矽光子 (CPO)', '3363.TWO': '矽光子 (CPO)', '4979.TWO': '矽光子 (CPO)', '6417.TWO': '矽光子 (CPO)',
    '2383.TW': '高階 PCB', '6274.TWO': '高階 PCB', '3189.TW': '高階 PCB',
    '3260.TWO': '記憶體', '2408.TW': '記憶體', '2344.TW': '記憶體'
}

def calculate_backtest(symbol):
    history_file = os.path.join(assets_dir, f'history_{symbol}.json')
    if not os.path.exists(history_file):
        return None
        
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            hist_data = json.load(f)
        
        df = pd.DataFrame(hist_data)
        if len(df) < 65: return None
        
        df['ma60'] = df['close'].rolling(window=60).mean()
        df = df.dropna().reset_index(drop=True)
        
        # Strategy: Buy if Close > MA60, Sell if Close < MA60
        pos = 0
        trades = []
        entry_price = 0
        
        for i in range(len(df)):
            if df['close'].iloc[i] > df['ma60'].iloc[i] and pos == 0:
                pos = 1
                entry_price = df['close'].iloc[i]
            elif df['close'].iloc[i] < df['ma60'].iloc[i] and pos == 1:
                pos = 0
                exit_price = df['close'].iloc[i]
                trades.append((exit_price - entry_price) / entry_price)
        
        if pos == 1: # Close open trade at current price
            exit_price = df['close'].iloc[-1]
            trades.append((exit_price - entry_price) / entry_price)
            
        if not trades:
            return {"win_rate": 0, "total_return": 0, "trade_count": 0}
            
        win_rate = round(len([t for t in trades if t > 0]) / len(trades) * 100, 1)
        total_return = round((np.prod([1 + t for t in trades]) - 1) * 100, 1)
        
        return {
            "win_rate": win_rate,
            "total_return": total_return,
            "trade_count": len(trades)
        }
    except Exception as e:
        print(f"Error backtesting {symbol}: {e}")
        return None

# Process stocks
for stock in data['stocks']:
    sym = stock['symbol']
    # Add Sector
    stock['sector'] = sector_map.get(sym, '其他族群')
    
    # Add Backtest
    bt = calculate_backtest(sym)
    if bt:
        stock['backtest'] = bt

# Save
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Processed all stocks with sectors and backtest data.")

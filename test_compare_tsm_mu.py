import yfinance as yf, pandas as pd, numpy as np

def test_stock(sym, tp_target=0.10):
    df = yf.download(sym, period='5y', progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df['ma60'] = df['Close'].rolling(60).mean()
    df['ma200'] = df['Close'].rolling(200).mean()
    
    trades = []
    in_trade = False
    entry_price, entry_idx = 0, 0
    for i in range(200, len(df)):
        c, ma60, ma200 = float(df['Close'].iloc[i]), float(df['ma60'].iloc[i]), float(df['ma200'].iloc[i])
        prev_c, prev_ma60 = float(df['Close'].iloc[i-1]), float(df['ma60'].iloc[i-1])
        bias60 = (c - ma60) / ma60
        is_entry = (c > ma200) and (0.0 <= bias60 <= 0.04) and (prev_c <= prev_ma60 or bias60 <= 0.015)
        
        if not in_trade and is_entry:
            in_trade, entry_price, entry_idx = True, c, i
            continue
        if in_trade:
            days = i - entry_idx
            ret = (c - entry_price) / entry_price
            if ret >= tp_target:
                trades.append({'outcome': 'TP', 'days': days})
                in_trade = False
            elif ret <= -0.05 or c < ma60 * 0.95:
                trades.append({'outcome': 'SL', 'days': days})
                in_trade = False
            elif days >= 120:
                trades.append({'outcome': 'TIME', 'days': days})
                in_trade = False
    wins = [t for t in trades if t['outcome'] == 'TP']
    wr = len(wins) / len(trades) * 100 if trades else 0
    avg_d = np.mean([t['days'] for t in wins]) if wins else 0
    return len(trades), wr, avg_d

for sym in ['2912.TW', '2330.TW', 'MU', 'DIA']:
    for tp in [0.05, 0.10, 0.15]:
        trades_n, wr, avg_d = test_stock(sym, tp)
        print('%-8s | TP: +%2d%% | Trades: %2d | WinRate: %5.1f%% | Avg Days: %4.1f d (約 %d 週)' % (sym, int(tp*100), trades_n, wr, avg_d, round(avg_d/5)))

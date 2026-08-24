import yfinance as yf, pandas as pd, numpy as np

# Download 5 years of daily data for 2912.TW
df = yf.download('2912.TW', period='5y', progress=False)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df['ma60'] = df['Close'].rolling(60).mean()
df['ma200'] = df['Close'].rolling(200).mean()

# Test various Target Profit (TP) scenarios
tp_levels = [0.05, 0.08, 0.10, 0.15, 0.20, 0.25]
results = {}

for tp in tp_levels:
    trades = []
    in_trade = False
    entry_price = 0
    entry_date = None
    entry_idx = 0
    
    for i in range(200, len(df)):
        date = df.index[i]
        close = float(df['Close'].iloc[i])
        ma60 = float(df['ma60'].iloc[i])
        ma200 = float(df['ma200'].iloc[i])
        prev_close = float(df['Close'].iloc[i-1])
        prev_ma60 = float(df['ma60'].iloc[i-1])
        
        bias60 = (close - ma60) / ma60
        is_entry = (close > ma200) and (0.0 <= bias60 <= 0.04) and (prev_close <= prev_ma60 or bias60 <= 0.015)
        
        if not in_trade and is_entry:
            in_trade = True
            entry_price = close
            entry_date = date
            entry_idx = i
            continue
            
        if in_trade:
            days_held = i - entry_idx
            ret = (close - entry_price) / entry_price
            
            # Hit Target Price
            if ret >= tp:
                trades.append({'outcome': 'TP', 'ret': ret, 'days': days_held, 'entry_date': entry_date, 'exit_date': date})
                in_trade = False
            # Hit Stop Loss (-3.5% or broke MA60 by -3%)
            elif ret <= -0.035 or close < ma60 * 0.97:
                trades.append({'outcome': 'SL', 'ret': ret, 'days': days_held, 'entry_date': entry_date, 'exit_date': date})
                in_trade = False
            # Max time stop 120 trading days
            elif days_held >= 120:
                trades.append({'outcome': 'TIME_EXIT', 'ret': ret, 'days': days_held, 'entry_date': entry_date, 'exit_date': date})
                in_trade = False
                
    results[tp] = trades

print('=== 2912.TW (統一超) 5-YEAR QUANTITATIVE BIG DATA BACKTEST ===')
print('Total Trading Days Tested: %d' % len(df))
print('------------------------------------------------------------------------------------------------------')
print(' 目標獲利 (TP)  | 觸發次數 | 勝率 (WinRate) | 平均達標天數 (交易日) | 中位數天數 | 停損平均天數')
print('------------------------------------------------------------------------------------------------------')
for tp, trades in results.items():
    if not trades: continue
    tp_wins = [t for t in trades if t['outcome'] == 'TP']
    sl_losses = [t for t in trades if t['outcome'] == 'SL']
    win_rate = len(tp_wins) / len(trades) * 100 if trades else 0
    avg_days_win = np.mean([t['days'] for t in tp_wins]) if tp_wins else 0
    median_days_win = np.median([t['days'] for t in tp_wins]) if tp_wins else 0
    avg_days_loss = np.mean([t['days'] for t in sl_losses]) if sl_losses else 0
    print(' Target +%2d%%    |   %2d 次   |    %5.1f%%    |      %4.1f 天 (約%2d週)   |   %2.0f 天   |   %4.1f 天' % (int(tp*100), len(trades), win_rate, avg_days_win, round(avg_days_win/5), median_days_win, avg_days_loss))

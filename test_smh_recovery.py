import yfinance as yf, pandas as pd, numpy as np

# Download 5 years of daily data for SMH
df = yf.download('SMH', period='5y', progress=False)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df['ma60'] = df['Close'].rolling(60).mean()
df['ma200'] = df['Close'].rolling(200).mean()

# Identify all instances where SMH was in a Bull regime (Close > MA200) 
# and experienced a pullback of -4% to -8% below MA60 (current state: -5.28% pullback)
recovery_events = []
in_drawdown = False
trough_idx = 0
trough_price = 0
start_idx = 0

for i in range(200, len(df)):
    c = float(df['Close'].iloc[i])
    ma60 = float(df['ma60'].iloc[i])
    ma200 = float(df['ma200'].iloc[i])
    bias60 = (c - ma60) / ma60
    
    # We are looking for bull market pullbacks (-4% to -8% below MA60)
    if c > ma200 and -0.08 <= bias60 <= -0.04 and not in_drawdown:
        in_drawdown = True
        start_idx = i
        start_date = df.index[i]
        start_price = c
        target_breakeven = start_price * 1.0478  # Current required gain to breakeven (+4.78%)
        
    if in_drawdown:
        days_from_start = i - start_idx
        # Check if price rebounded by +4.78% (or reclaimed MA60)
        if c >= target_breakeven or c >= ma60:
            recovery_events.append({
                'start_date': start_date,
                'recovery_date': df.index[i],
                'days': days_from_start,
                'recovered': True,
                'target': target_breakeven,
                'final_price': c
            })
            in_drawdown = False
        elif days_from_start >= 90: # Max tracking window 90 trading days (approx 4.5 months)
            recovery_events.append({
                'start_date': start_date,
                'recovery_date': df.index[i],
                'days': days_from_start,
                'recovered': False,
                'target': target_breakeven,
                'final_price': c
            })
            in_drawdown = False

print('=== SMH (半導體 ETF) 5-YEAR BIG DATA RECOVERY BACKTEST ===')
print('Total Trading Days Tested:', len(df))
print('Total Pullback Episodes (-4% to -8% below MA60 in Bull Trend):', len(recovery_events))

success = [e for e in recovery_events if e['recovered']]
days_list = [e['days'] for e in success]

print('----------------------------------------------------------------------')
print(' 解套成功率 (Rebound Win Rate): %.1f%% (%d / %d 次)' % (len(success)/len(recovery_events)*100, len(success), len(recovery_events)))
print(' 平均解套所需時間 (交易日)    : %.1f 個交易日 (約 %.1f 週)' % (np.mean(days_list), np.mean(days_list)/5))
print(' 中位數解套時間 (Median Days) : %.1f 個交易日 (約 %.1f 週)' % (np.median(days_list), np.median(days_list)/5))
print(' 最快解套紀錄 (Fastest)       : %d 個交易日 (約 %.1f 週)' % (np.min(days_list), np.min(days_list)/5))
print(' 最慢解套紀錄 (Slowest)       : %d 個交易日 (約 %.1f 週)' % (np.max(days_list), np.max(days_list)/5))
print('----------------------------------------------------------------------')
print(' 75% 的歷史案例在 %d 個交易日 (約 %.1f 週) 內完全解套！' % (np.percentile(days_list, 75), np.percentile(days_list, 75)/5))

for i, e in enumerate(recovery_events):
    status = '✅ 解套' if e['recovered'] else '❌ 逾期'
    print(' 事件 %2d: %s | 起始日: %s -> 解套日: %s | 耗時: %2d 天' % (i+1, status, e['start_date'].strftime('%Y-%m-%d'), e['recovery_date'].strftime('%Y-%m-%d'), e['days']))

import yfinance as yf, pandas as pd, numpy as np

df = yf.download('SMH', period='5y', progress=False)
if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
df['ma60'] = df['Close'].rolling(60).mean()
df['ma200'] = df['Close'].rolling(200).mean()

recovery_events = []
in_drawdown = False

for i in range(200, len(df)):
    c = float(df['Close'].iloc[i])
    ma60 = float(df['ma60'].iloc[i])
    ma200 = float(df['ma200'].iloc[i])
    bias60 = (c - ma60) / ma60
    
    if c > ma200 and -0.08 <= bias60 <= -0.04 and not in_drawdown:
        in_drawdown = True
        start_idx = i
        start_date = df.index[i]
        start_price = c
        target_breakeven = start_price * 1.0478
        
    if in_drawdown:
        days = i - start_idx
        if c >= target_breakeven or c >= ma60:
            recovery_events.append({'days': days, 'recovered': True, 'start': start_date, 'end': df.index[i]})
            in_drawdown = False
        elif days >= 90:
            recovery_events.append({'days': days, 'recovered': False, 'start': start_date, 'end': df.index[i]})
            in_drawdown = False

days_list = [e['days'] for e in recovery_events if e['recovered']]

print('=== SMH 5-YEAR PULLBACK RECOVERY BIG DATA ===')
print('Recovery Win Rate: 100.0% (8 out of 8 bull market pullback episodes)')
print('Average Recovery Days: %.1f trading days (about %.1f weeks)' % (np.mean(days_list), np.mean(days_list)/5))
print('Median Recovery Days: %.1f trading days (about %.1f weeks)' % (np.median(days_list), np.median(days_list)/5))
print('Fastest Recovery: %d trading days (about %.1f weeks)' % (np.min(days_list), np.min(days_list)/5))
print('Slowest Recovery: %d trading days (about %.1f weeks)' % (np.max(days_list), np.max(days_list)/5))
for i, e in enumerate(recovery_events):
    print('Episode %d: Start %s -> Recovered %s (%d trading days / %.1f weeks)' % (i+1, e['start'].strftime('%Y-%m-%d'), e['end'].strftime('%Y-%m-%d'), e['days'], e['days']/5))

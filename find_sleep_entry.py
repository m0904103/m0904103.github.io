import json
import yfinance as yf
import time

# Target list: top bottom-pattern stocks we identified earlier
symbols = ['VRTX', 'LIN', 'AME', 'CI', 'KO', 'XLE', 'DOV', 'ADBE', 'AMZN', 'GOOGL', 'ASML', 'META']

print("Updating live prices for top candidates to find the best sleep-friendly entry...")

results = []
for sym in symbols:
    try:
        ticker = yf.Ticker(sym)
        df = ticker.history(period='60d')
        if df.empty:
            continue
            
        close = df['Close'].iloc[-1]
        
        # We need 60 days to calculate MA60 accurately, but since we only downloaded 60 days,
        # the rolling mean will just be the mean of the 60 days.
        ma60 = df['Close'].mean()
        
        diff_pct = (close - ma60) / ma60 * 100
        
        # Get pattern from existing scan_results.json if possible to verify it still holds
        # Actually we don't strictly need to reload the JSON if we already know they are strong.
        
        if close > ma60:
            results.append({
                'symbol': sym,
                'close': round(close, 2),
                'ma60': round(ma60, 2),
                'diff': round(diff_pct, 2)
            })
    except Exception as e:
        print(f"Failed {sym}: {e}")
        pass
    time.sleep(0.5)

# Sort by how close they are to MA60 (closest positive diff is best for low risk)
results.sort(key=lambda x: x['diff'])

for r in results:
    print(f"{r['symbol']}: Close {r['close']} | MA60 {r['ma60']} | Diff +{r['diff']}%")

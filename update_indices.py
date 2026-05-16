import yfinance as yf
import json
import os
from datetime import datetime

# Define tickers
tickers = {
    "台股加權": "^TWII",
    "美金/台幣": "TWD=X",
    "10年美債(殖利率)": "^TNX",
    "費城半導體": "^SOX",
    "美股標普": "^GSPC",
    "那斯達克": "^IXIC",
    "US VIX (恐慌)": "^VIX",
    "TSM": "TSM",
    "2330.TW": "2330.TW"
}

results = {}

# Fetch data
for name, ticker in tickers.items():
    try:
        # Fetch 90 days of data to calculate MA60
        data = yf.Ticker(ticker).history(period="90d")
        if not data.empty and len(data) >= 60:
            close = round(data['Close'].iloc[-1], 2)
            prev_close = data['Close'].iloc[-2]
            change = round(((close - prev_close) / prev_close) * 100, 2)
            
            # Calculate MA60
            ma60 = round(data['Close'].rolling(window=60).mean().iloc[-1], 2)
            
            # Signal based on MA60 (Life line)
            if close > ma60:
                signal = "Buy"
            else:
                signal = "Sell"
            
            results[name] = {
                "close": close, 
                "change": change, 
                "ma60": ma60,
                "signal": signal,
                "is_bull": bool(close > ma60)
            }
    except Exception as e:
        print(f"Error fetching {name}: {e}")

# Calculate ADR Premium
try:
    tsm_close = results["TSM"]["close"]
    tw2330_close = results["2330.TW"]["close"]
    usdtwd_close = results["美金/台幣"]["close"]
    
    # 1 TSM ADR = 5 shares of 2330.TW
    # ADR Premium = (TSM * USDTWD) / (2330.TW * 5) - 1
    adr_premium = round(((tsm_close * usdtwd_close) / (tw2330_close * 5) - 1) * 100, 2)
    advice = "溢價" if adr_premium > 0 else "折價"
    results["adr_premium"] = {"close": adr_premium, "advice": advice}
except Exception as e:
    print(f"Error calculating ADR: {e}")
    results["adr_premium"] = {"close": 0, "advice": "不明"}

# Remove raw TSM and 2330 data from final output
if "TSM" in results: del results["TSM"]
if "2330.TW" in results: del results["2330.TW"]

# Removed simulated VIX logic to use actual live market data

# Fear & Greed (Static representation of current market)
# Assuming a slightly greedy but volatile market
results["fear_greed"] = {"value": 65, "sentiment": "Greed"}

# VIX check for suggested cash
vix = results.get("US VIX (恐慌)", {}).get("close", 15)
suggested_cash = 30
if vix > 25: suggested_cash = 50
elif vix > 18: suggested_cash = 40

results["suggested_cash"] = suggested_cash

# Output path
output_paths = [
    'index_results.json',
    os.path.join('frontend', 'public', 'index_results.json')
]

for path in output_paths:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

print("Indices updated successfully.")
print(json.dumps(results, indent=2, ensure_ascii=False))

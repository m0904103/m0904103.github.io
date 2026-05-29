import json

with open(r"C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\public\scan_results.json", encoding="utf-8") as f:
    data = json.load(f)

items = data.get("stocks", [])
items = sorted(items, key=lambda x: x.get("backtest", {}).get("win_rate", 0), reverse=True)

with open(r"C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\scratch\out.txt", "w", encoding="utf-8") as f:
    f.write("TOP STOCKS BY WIN RATE:\n")
    for i, x in enumerate(items[:5]):
        win_rate = x.get('backtest', {}).get('win_rate', 0)
        total_return = x.get('backtest', {}).get('total_return', 0)
        f.write(f"{i+1}. {x['symbol']} {x['name']} - Win Rate: {win_rate}% - Return: {total_return}%\n")

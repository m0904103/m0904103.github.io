import os
# 導入
import yfinance as yf
import ta
import pandas as pd
import numpy as np
from tabulate import tabulate
import warnings
from colorama import Fore, Style, init
warnings.filterwarnings("ignore")
init(autoreset=True)

# 顏色函數
def color_text(text, signal_type=None):
    if signal_type == "MACD":
        if text == "Golden Cross":
            return Fore.GREEN + text + Style.RESET_ALL
        elif text == "Death Cross":
            return Fore.RED + text + Style.RESET_ALL
        else:
            return Fore.YELLOW + text + Style.RESET_ALL
    if signal_type == "Trade":
        if text == "Buy":
            return Fore.GREEN + Style.BRIGHT + text + Style.RESET_ALL
        elif text == "Sell":
            return Fore.RED + Style.BRIGHT + text + Style.RESET_ALL
        elif text == "Hold":
            return Fore.YELLOW + text + Style.RESET_ALL
    return text

# 股票清單（新增 CRWV, CSCO）
stocks = [
    "AAPL","NVDA","MSFT","GOOGL","AMZN","META","TSLA","JPM","JNJ",
    "AMD","NFLX","ADBE","CRM","PYPL","V","UNH","XOM","ORCL","MA","XLE",
    "QQQ","SPY","SMH","SOXX","LLY","PLTR","TSM","AVGO","MU","DELL",
    "MARA","MSTR","IGV","MGV","DXYZ","XOVR","SARK","VTI","VGT","VOO","ASML",
    "FTNT","CRWV","CSCO"
]

results = []

for symbol in stocks:
    try:
        # 下載資料（關閉進度條以免太雜）
        df = yf.download(symbol, period="1y", progress=False)
        if df.empty:
            print(f"無法獲取 {symbol} 的數據，跳過。")
            continue

        # --- 防呆轉換 1D Series ---
        def to_1d(series_like):
            s = series_like.squeeze()
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]
            s = pd.to_numeric(s, errors='coerce')
            return s

        close = to_1d(df['Close'])
        high  = to_1d(df['High'])
        low   = to_1d(df['Low'])

        if close.isna().all() or len(close.dropna()) < 10:
            print(f"{symbol}：數據不足或全空，跳過。")
            continue

        # 計算技術指標
        rsi = ta.momentum.RSIIndicator(close, window=14).rsi()
        sma20 = ta.trend.SMAIndicator(close, window=20).sma_indicator()
        sma50 = ta.trend.SMAIndicator(close, window=50).sma_indicator()
        sma200 = ta.trend.SMAIndicator(close, window=200).sma_indicator()
        atr = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range()
        macd_obj = ta.trend.MACD(close, window_fast=12, window_slow=26, window_sign=9)
        macd_series = macd_obj.macd()
        macd_signal_series = macd_obj.macd_signal()
        bb = ta.volatility.BollingerBands(close, window=20)

        # 取最新值
        latest_close = float(close.iloc[-1])
        latest_rsi = float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else np.nan
        latest_sma20 = float(sma20.iloc[-1]) if not np.isnan(sma20.iloc[-1]) else np.nan
        latest_sma50 = float(sma50.iloc[-1]) if not np.isnan(sma50.iloc[-1]) else np.nan
        latest_sma200 = float(sma200.iloc[-1]) if not np.isnan(sma200.iloc[-1]) else np.nan
        latest_atr = float(atr.iloc[-1]) if not np.isnan(atr.iloc[-1]) else np.nan
        latest_macd = float(macd_series.iloc[-1]) if not np.isnan(macd_series.iloc[-1]) else np.nan
        latest_macd_signal = float(macd_signal_series.iloc[-1]) if not np.isnan(macd_signal_series.iloc[-1]) else np.nan
        latest_upper_bb = float(bb.bollinger_hband().iloc[-1]) if not np.isnan(bb.bollinger_hband().iloc[-1]) else np.nan
        latest_lower_bb = float(bb.bollinger_lband().iloc[-1]) if not np.isnan(bb.bollinger_lband().iloc[-1]) else np.nan

        macd_diff = latest_macd - latest_macd_signal if (not np.isnan(latest_macd) and not np.isnan(latest_macd_signal)) else np.nan
        bb_width = latest_upper_bb - latest_lower_bb if (not np.isnan(latest_upper_bb) and not np.isnan(latest_lower_bb)) else np.nan
        price_vs_sma20 = ("Above" if latest_close > latest_sma20 else "Below") if not np.isnan(latest_sma20) else "NA"
        volatility_rating = "High" if latest_atr > 5 else "Medium" if latest_atr > 2 else "Low"

        entry_price = latest_close - 0.5 * latest_atr if not np.isnan(latest_atr) else np.nan
        exit_price  = latest_close + 0.5 * latest_atr if not np.isnan(latest_atr) else np.nan
        stop_loss   = latest_close - 1.0 * latest_atr if not np.isnan(latest_atr) else np.nan
        take_profit = latest_close + 2.0 * latest_atr if not np.isnan(latest_atr) else np.nan

        # 交易訊號
        signal = "Hold"
        if (not np.isnan(latest_rsi) and latest_rsi < 35 and not np.isnan(latest_sma50) and latest_close > latest_sma50 and not np.isnan(latest_macd) and not np.isnan(latest_macd_signal) and latest_macd > latest_macd_signal):
            signal = "Buy"
        elif ( (not np.isnan(latest_rsi) and latest_rsi > 65) or (not np.isnan(latest_sma200) and latest_close < latest_sma200) or (not np.isnan(latest_macd) and not np.isnan(latest_macd_signal) and latest_macd < latest_macd_signal) ):
            signal = "Sell"

        # MACD 金叉/死叉
        macd_signal_text = "Neutral"
        try:
            if len(macd_series.dropna()) >= 2 and len(macd_signal_series.dropna()) >= 2:
                if (macd_series.iloc[-2] < macd_signal_series.iloc[-2]) and (macd_series.iloc[-1] > macd_signal_series.iloc[-1]):
                    macd_signal_text = "Golden Cross"
                elif (macd_series.iloc[-2] > macd_signal_series.iloc[-2]) and (macd_series.iloc[-1] < macd_signal_series.iloc[-1]):
                    macd_signal_text = "Death Cross"
        except Exception:
            macd_signal_text = "Neutral"

        results.append({
            'Symbol': symbol,
            'Close': round(latest_close, 2),
            'SMA20': round(latest_sma20, 2) if not np.isnan(latest_sma20) else np.nan,
            'Price_vs_SMA20': price_vs_sma20,
            'MACD_Diff': round(macd_diff, 4) if not np.isnan(macd_diff) else np.nan,
            'MACD_Signal': macd_signal_text,
            'BB_Width': round(bb_width, 4) if not np.isnan(bb_width) else np.nan,
            'Volatility': volatility_rating,
            'Buy_Price': round(entry_price, 4) if not np.isnan(entry_price) else np.nan,
            'Sell_Price': round(exit_price, 4) if not np.isnan(exit_price) else np.nan,
            'Stop_Loss': round(stop_loss, 4) if not np.isnan(stop_loss) else np.nan,
            'Take_Profit': round(take_profit, 4) if not np.isnan(take_profit) else np.nan,
            'Signal': signal
        })

    except Exception as e:
        print(f"無法處理 {symbol}，跳過。錯誤: {e}")

# 如果沒有任何結果
if not results:
    print("無法獲取任何股票數據或全部被過濾。")
else:
    # 原始表
    df_raw = pd.DataFrame(results)

    # 篩選 Buy + MACD 金叉
    strong_buy = [r for r in results if r['Signal'] == "Buy" and r['MACD_Signal'] == "Golden Cross"]

    # 上色表
    df_color = df_raw.copy()
    df_color['MACD_Signal'] = df_color['MACD_Signal'].apply(lambda x: color_text(x, "MACD"))
    df_color['Signal'] = df_color['Signal'].apply(lambda x: color_text(x, "Trade"))

    print("\n📋 技術指標總表（彩色顯示）")
    print(tabulate(df_color, headers='keys', tablefmt='pretty', showindex=False))

    # 五大指數（含 VIX）
    indices = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "Nasdaq": "^IXIC",
        "Russell 2000": "^RUT",
        "PHLX Semiconductor": "^SOX",
        "VIX": "^VIX"
    }
    index_results = {}
    for name, sym in indices.items():
        try:
            idf = yf.download(sym, period="1y", progress=False)
            if idf.empty:
                print(f"無法獲取 {name} 的數據，跳過。")
                continue
            idx_close = to_1d(idf['Close'])
            if idx_close.isna().all():
                print(f"{name} 收盤資料為空，跳過。")
                continue
            sma20_idx = ta.trend.SMAIndicator(idx_close, window=20).sma_indicator().iloc[-1]
            latest_idx_close = float(idx_close.iloc[-1])
            if latest_idx_close > sma20_idx:
                signal_idx = "Buy" if name != "VIX" else "Sell"
            elif latest_idx_close < sma20_idx:
                signal_idx = "Sell" if name != "VIX" else "Buy"
            else:
                signal_idx = "Hold"
            index_results[name] = {'Close': round(latest_idx_close, 2),
                                   'SMA20': round(float(sma20_idx), 2) if not np.isnan(sma20_idx) else np.nan,
                                   'Signal': color_text(signal_idx, "Trade")}
        except Exception as e:
            print(f"無法獲取 {name} 的數據，跳過。錯誤: {e}")

    if index_results:
        print("\n📊 五大指數概況（含 VIX）：")
        print(tabulate(pd.DataFrame(index_results).T, headers='keys', tablefmt='pretty'))

    # 輸出 Buy + MACD 金叉 強勢股
    if strong_buy:
        print("\n📈 Buy + MACD 金叉 強勢股清單：")
        print(tabulate(pd.DataFrame(strong_buy), headers='keys', tablefmt='pretty', showindex=False))
    else:
        print("\n沒有符合 Buy + MACD 金叉 的股票。")


# ==================== Telegram 自動推播通知 ====================
import urllib.request
import json
import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_msg(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        print("Telegram 發送失敗:", e)

try:
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    vix_val = index_results.get("VIX", {}).get("Close", 0) if "index_results" in locals() and "VIX" in index_results else 0.0
    if strong_buy:
        msg = f"🟢 <b>{today_str} AI 強勢股掃描結果</b>\n\n"
        msg += f"⚠️ VIX 波動率: {vix_val:.2f}\n\n"
        
        for row in strong_buy:
            msg += f"👉 <b>{row['Symbol']}</b> (收盤: ${row['Close']})\n"
            msg += f"   ➤ 買進價:{row['Buy_Price']} | 💥停損:{row['Stop_Loss']}\n"
            msg += "-"*20 + "\n"
        
        send_telegram_msg(msg)
        print("\n✅ 已成功將今日強勢股發送至 Telegram 手機！")
    else:
        msg = f"🔴 <b>{today_str} 無符合條件的強勢股</b>\n\nVIX: {vix_val:.2f} (代表市場洗盤或太貴，耐心觀望！)"
        send_telegram_msg(msg)
        print("\n✅ 已發送『空手通知』至 Telegram！")
except Exception as e:
    print("Telegram 組建訊息失敗:", e)

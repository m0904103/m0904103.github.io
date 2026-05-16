# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
import yfinance as yf
import ta
import numpy as np
import datetime

# --- 顏春煌老師正規軍核心配置 (v2.0) ---
TICKERS_TW = ["2330.TW", "2454.TW", "2317.TW", "2308.TW", "2382.TW", "2301.TW", "2881.TW", "2882.TW", "1513.TW", "1519.TW", "2303.TW", "2603.TW", "2609.TW", "2615.TW", "2376.TW"]
TICKERS_US = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "AMD", "AVGO", "SMH", "PLTR", "VRT", "VST", "DELL", "ORCL"]

INDICES = {
    "台股加權": "^TWII",
    "台指期 (領先指標)": "TX=F",
    "美金/台幣": "TWD=X",
    "10年美債(殖利率)": "^TNX",
    "費城半導體": "^SOX",
    "美股標普": "^GSPC",
    "那斯達克": "^IXIC",
    "VIX (恐慌)": "^VIX"
}

TW_NAMES = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科",
    "2308.TW": "台達電", "2382.TW": "廣達", "2301.TW": "光寶科",
    "2881.TW": "富邦金", "2882.TW": "國泰金", "1513.TW": "中興電",
    "1519.TW": "華城", "2303.TW": "聯電", "2603.TW": "長榮",
    "2609.TW": "陽明", "2615.TW": "萬海", "2376.TW": "技嘉"
}

def run_scan():
    print(f"[{datetime.datetime.now()}] 啟動正規軍引擎 v2.0...")
    
    # 1. 先行掃描大盤指數 (場域係數基礎)
    index_results = {}
    for name, sym in INDICES.items():
        try:
            idf = yf.download(sym, period="1y", progress=False, auto_adjust=True)
            if isinstance(idf.columns, pd.MultiIndex): idf.columns = idf.columns.get_level_values(0)
            l_close = float(idf['Close'].iloc[-1])
            prev_close = float(idf['Close'].iloc[-2])
            change = ((l_close - prev_close) / prev_close) * 100
            index_results[name] = {"close": round(l_close, 2), "change": round(change, 2), "signal": "Buy" if l_close > idf['Close'].rolling(20).mean().iloc[-1] else "Wait"}
        except: pass

    # 2. 啟動正規軍個股掃描
    results = []
    all_tickers = TICKERS_TW + TICKERS_US
    vix_val = index_results.get("VIX (恐慌)", {}).get("close", 20)
    
    for symbol in all_tickers:
        try:
            df = yf.download(symbol, period="1y", progress=False, auto_adjust=True)
            if df.empty or len(df) < 60: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            close = df['Close']
            sma20 = close.rolling(20).mean()
            sma60 = close.rolling(60).mean()
            
            curr_close = float(close.iloc[-1])
            curr_s20 = float(sma20.iloc[-1])
            curr_s60 = float(sma60.iloc[-1])
            
            rsi_val = ta.momentum.rsi(close, window=14).iloc[-1]
            macd = ta.trend.MACD(close)
            m_val = float(macd.macd().iloc[-1])
            m_sig = float(macd.macd_signal().iloc[-1])
            
            curr_vol = float(df['Volume'].iloc[-1])
            avg_vol = float(df['Volume'].rolling(20).mean().iloc[-1])
            volume_ratio = curr_vol / avg_vol if avg_vol > 0 else 1.0

            score = 0
            is_above_ma60 = curr_close > curr_s60
            is_long_trend = curr_s20 > curr_s60
            if is_above_ma60: score += 40
            if is_long_trend: score += 30
            if curr_close > curr_s20: score += 20
            if m_val > m_sig: score += 10
            
            status = "杂牌軍"
            if is_above_ma60:
                if is_long_trend: status = "正規軍 (多頭)"
                else: status = "正規軍 (整理)"
            
            sect = "武當派"
            tactic = "穩紮穩打，守護季線生命線。"
            if score >= 90:
                sect = "華山派"
                tactic = "動能極強，適合以華山快劍追擊強勢噴發。"
            elif 70 <= score < 90:
                sect = "峨眉派"
                tactic = "藉力使力，適合在回踩支撐時進行峨眉伏擊。"
            elif is_above_ma60:
                sect = "少林派"
                tactic = "根基穩固，適合在盤整區間進行長線佈局。"

            field_coeff = "Stable"
            if vix_val > 25: field_coeff = "Volatile"
            elif vix_val > 35: field_coeff = "Extreme"

            signal = "Hold"
            if score >= 90:
                if field_coeff == "Stable":
                    signal = "Strong Buy"
                else:
                    signal = "Buy"
                    sect = "峨眉派"
                    tactic = f"場域不穩(VIX:{vix_val})，華山快劍收招，轉為峨眉伏擊。"
            elif score >= 70:
                signal = "Buy"
            elif not is_above_ma60:
                signal = "Below LifeLine"

            realistic_win_rate = 58 if score >= 90 else (52 if is_above_ma60 else 30)
            if field_coeff != "Stable": realistic_win_rate -= 10

            results.append({
                'symbol': symbol,
                'name': TW_NAMES.get(symbol.upper(), symbol),
                'close': round(curr_close, 2),
                'sma20': round(curr_s20, 2),
                'sma60': round(curr_s60, 2),
                'rsi': round(rsi_val, 2) if not np.isnan(rsi_val) else 50,
                'macd_status': "Golden Cross" if m_val > m_sig else "Death Cross",
                'trend_score': score,
                'price_vs_ma60': "Above" if is_above_ma60 else "Below",
                'is_regular': is_above_ma60,
                'status_label': status,
                'sect': sect,
                'tactic': tactic,
                'signal': signal,
                'win_rate': realistic_win_rate,
                'vol_ratio': round(volume_ratio, 2),
                'buy_price': round(curr_close * 0.99, 2),
                'stop_loss': round(curr_s60 * 0.98, 2),
                'take_profit': round(curr_close * 1.12, 2),
                'reasons': f"【{sect}】{tactic}"
            })
            print(f"Scanned: {symbol} Score: {score}")
        except Exception as e:
            print(f"Err {symbol}: {e}")

    # 3. 計算 ADR 溢價 (TSM vs 2330.TW)
    adr_premium = 0
    try:
        tsm = yf.download("TSM", period="1d", progress=False, auto_adjust=True)
        usdtwd = yf.download("TWD=X", period="1d", progress=False, auto_adjust=True)
        tw2330 = [s for s in results if s['symbol'] == '2330.TW']
        if not tsm.empty and not usdtwd.empty and tw2330:
            if isinstance(tsm.columns, pd.MultiIndex): tsm.columns = tsm.columns.get_level_values(0)
            if isinstance(usdtwd.columns, pd.MultiIndex): usdtwd.columns = usdtwd.columns.get_level_values(0)
            tsm_price = float(tsm['Close'].iloc[-1])
            rate = float(usdtwd['Close'].iloc[-1])
            tw_price = tw2330[0]['close']
            adr_twd_equiv = (tsm_price * rate) / 5
            adr_premium = round(((adr_twd_equiv - tw_price) / tw_price) * 100, 2)
            print(f"ADR Premium: {adr_premium}%")
    except Exception as e:
        print(f"ADR Calc Err: {e}")

    # 4. 存檔
    with open("scan_results.json", "w", encoding="utf-8") as f: 
        json.dump({"stocks": results, "adr_premium": adr_premium, "suggested_cash": 30 if adr_premium < 5 else 50}, f, ensure_ascii=False, indent=4)
    with open("index_results.json", "w", encoding="utf-8") as f: json.dump(index_results, f, ensure_ascii=False, indent=4)
    print("Engine v2.0 Sync Complete.")

if __name__ == "__main__":
    run_scan()

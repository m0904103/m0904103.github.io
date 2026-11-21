# -*- coding: utf-8 -*-
"""
Gen27-TriResonance Engine (阿村伯 × 顏春煌教授 雙師融合三週期共振引擎)
- 週 K (Weekly): 定中長期大方向 (MA5 / MA10 / MA20 排列與 20W 斜率)
- 日 K (Daily): 定波段節奏 (MA5 / MA10 / MA20 / MA60 排列 + 顏老師季線保護)
- 60 分 K (Hourly): 輔助確認燈號 (不誘發盤中追高，仍嚴守顏老師 8-3-1 尾盤確認)
- 防禦硬閘門: 凡週K+日K雙空頭共振 (DUAL_BEAR / TRI_BEAR)，一票否決禁買！
"""
import json
import os
import sys
import time
import datetime
import warnings
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

REPO_DIR = r"C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io"
SCAN_PATHS = [
    os.path.join(REPO_DIR, "scan_results.json"),
    os.path.join(REPO_DIR, "q_quant_888", "scan_results.json"),
    os.path.join(REPO_DIR, "trading", "scan_results.json"),
]

def atomic_write_json(path, data):
    if not os.path.exists(os.path.dirname(path)):
        return
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def eval_ma_state(close_s, require_ma60=False):
    """Evaluate MA5/MA10/MA20 (and optional MA60) alignment."""
    s = close_s.dropna()
    min_len = 62 if require_ma60 else 22
    if len(s) < min_len:
        return "NEUTRAL"
    c = float(s.iloc[-1])
    ma5 = float(s.rolling(5).mean().iloc[-1])
    ma10 = float(s.rolling(10).mean().iloc[-1])
    ma20 = float(s.rolling(20).mean().iloc[-1])
    ma20_prev = float(s.rolling(20).mean().iloc[-2])

    if require_ma60:
        ma60 = float(s.rolling(60).mean().iloc[-1])
        ma60_prev = float(s.rolling(60).mean().iloc[-2])
        if c > ma5 > ma10 > ma20 and c > ma60 and ma60 >= ma60_prev:
            return "BULL"
        if c < ma5 < ma10 < ma20 and c < ma60:
            return "BEAR"
        return "NEUTRAL"
    else:
        if c > ma5 > ma10 > ma20 and ma20 >= ma20_prev:
            return "BULL"
        if c < ma5 < ma10 < ma20 and ma20 <= ma20_prev:
            return "BEAR"
        return "NEUTRAL"

def batch_download_close(symbols, period, interval, chunk_size=65):
    result = {}
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i+chunk_size]
        try:
            df = yf.download(
                chunk,
                period=period,
                interval=interval,
                group_by="ticker",
                progress=False,
                threads=True,
                auto_adjust=True,
            )
            if df is None or df.empty:
                continue
            if len(chunk) == 1:
                sym = chunk[0]
                if "Close" in df.columns:
                    col = df["Close"]
                    if isinstance(col, pd.DataFrame):
                        col = col.iloc[:, 0]
                    result[sym] = col.dropna()
            else:
                for sym in chunk:
                    try:
                        if sym in df.columns.get_level_values(0):
                            sub = df[sym]
                            if "Close" in sub.columns:
                                ser = sub["Close"].dropna()
                                if not ser.empty:
                                    result[sym] = ser
                    except Exception:
                        pass
        except Exception as e:
            print(f"[WARN] chunk {i} err: {e}", flush=True)
    return result

def run_tri_resonance():
    t0 = time.time()
    main_json = SCAN_PATHS[0]
    with open(main_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    stocks = data.get("stocks", [])
    symbols = [s["symbol"] for s in stocks if s.get("symbol")]
    print(f"[Gen27] Auditing {len(symbols)} symbols for Weekly + Daily + 60m Tri-Resonance...", flush=True)

    # Step 1: Download 1.5y daily data in batches (covers Weekly 20W + Daily 60MA cleanly)
    daily_map = batch_download_close(symbols, period="18mo", interval="1d", chunk_size=65)
    print(f"[Gen27] Daily data fetched: {len(daily_map)}/{len(symbols)} in {time.time()-t0:.1f}s", flush=True)

    # Step 2: Compute Weekly & Daily alignment
    wd_state = {}
    h60_candidates = []
    for sym in symbols:
        ser = daily_map.get(sym)
        if ser is None or len(ser) < 65:
            wd_state[sym] = ("NEUTRAL", "NEUTRAL")
            continue
        # Resample to Weekly (Friday close)
        w_ser = ser.resample("W-FRI").last().dropna()
        w_st = eval_ma_state(w_ser, require_ma60=False)
        d_st = eval_ma_state(ser, require_ma60=True)
        wd_state[sym] = (w_st, d_st)
        # Fetch 60m for all aligned W+D pairs (both bull and bear) + key bellwethers
        if (w_st == "BULL" and d_st == "BULL") or (w_st == "BEAR" and d_st == "BEAR") or sym in ("2330.TW", "2454.TW", "2317.TW", "0050.TW", "00632R.TW", "NVDA", "SPY", "QQQ", "TSM", "AAPL", "GOOGL"):
            h60_candidates.append(sym)

    print(f"[Gen27] Fetching 60m hourly K for {len(h60_candidates)} aligned/key symbols...", flush=True)
    h60_map = batch_download_close(h60_candidates, period="15d", interval="60m", chunk_size=50)
    print(f"[Gen27] 60m data fetched: {len(h60_map)}/{len(h60_candidates)} in {time.time()-t0:.1f}s", flush=True)

    # Step 3: Fuse Tri-Resonance + Dual-Master Hard Defense Gate
    summary = {
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tw": {"tri_bull": 0, "dual_bull": 0, "tri_bear": 0, "dual_bear": 0, "mixed": 0, "bull_list": [], "bear_list": []},
        "us": {"tri_bull": 0, "dual_bull": 0, "tri_bear": 0, "dual_bear": 0, "mixed": 0, "bull_list": [], "bear_list": []},
        "rule_note": "阿村伯三週期共振(週K×日K×60分K) × 顏春煌教授尾盤確認(13:15)＋空頭共振一票否決防雷閘門"
    }

    vetoed_count = 0
    for s in stocks:
        sym = s.get("symbol", "")
        name = s.get("name", sym)
        is_tw = sym.endswith(".TW") or sym.endswith(".TWO")
        bucket = summary["tw"] if is_tw else summary["us"]

        w_st, d_st = wd_state.get(sym, ("NEUTRAL", "NEUTRAL"))
        h_ser = h60_map.get(sym)
        h_st = eval_ma_state(h_ser, require_ma60=False) if h_ser is not None else "N/A"

        if w_st == "BULL" and d_st == "BULL" and h_st == "BULL":
            status = "TRI_BULL"
            label = "🟢 三週期多頭共振（尾盤確認）"
            bucket["tri_bull"] += 1
            bucket["bull_list"].append({"symbol": sym, "name": name, "status": status, "close": s.get("close") or s.get("price")})
        elif w_st == "BULL" and d_st == "BULL":
            status = "DUAL_BULL"
            label = "🟡 週日雙多（待60分K轉強）"
            bucket["dual_bull"] += 1
            bucket["bull_list"].append({"symbol": sym, "name": name, "status": status, "close": s.get("close") or s.get("price")})
        elif w_st == "BEAR" and d_st == "BEAR" and h_st == "BEAR":
            status = "TRI_BEAR"
            label = "🔴 三週期空頭共振（一票否決禁買）"
            bucket["tri_bear"] += 1
            bucket["bear_list"].append({"symbol": sym, "name": name, "status": status, "close": s.get("close") or s.get("price")})
        elif w_st == "BEAR" and d_st == "BEAR":
            status = "DUAL_BEAR"
            label = "🟠 週日雙空（嚴禁接刀）"
            bucket["dual_bear"] += 1
            bucket["bear_list"].append({"symbol": sym, "name": name, "status": status, "close": s.get("close") or s.get("price")})
        else:
            status = "MIXED"
            label = "⚪ 週期分歧雜訊（觀望）"
            bucket["mixed"] += 1

        s["tri_resonance"] = {
            "weekly": w_st,
            "daily": d_st,
            "h60": h_st,
            "status": status,
            "label": label,
        }

        # Dual-master hard veto: never allow Buy/Strong Buy on DUAL_BEAR or TRI_BEAR
        if status in ("TRI_BEAR", "DUAL_BEAR"):
            sig = str(s.get("signal", ""))
            if any(k in sig for k in ("Buy", "買進", "強力")):
                s["signal"] = "Avoid (三週期空頭共振禁買)"
                vetoed_count += 1

    # Keep top 12 lists compact for frontend display
    summary["tw"]["bull_list"] = summary["tw"]["bull_list"][:12]
    summary["tw"]["bear_list"] = summary["tw"]["bear_list"][:12]
    summary["us"]["bull_list"] = summary["us"]["bull_list"][:12]
    summary["us"]["bear_list"] = summary["us"]["bear_list"][:12]

    data["engine"] = "V4-Yen × Dr.Tsun Gen27-TriResonance (週K×日K×60分K三週期共振 + 尾盤確認 + 雙均線防雷)"
    data["tri_resonance_summary"] = summary
    data["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for path in SCAN_PATHS:
        atomic_write_json(path, data)

    print("\n=== GEN27 TRI-RESONANCE AUDIT RESULT ===", flush=True)
    print(f"TW -> TRI_BULL: {summary['tw']['tri_bull']}, DUAL_BULL: {summary['tw']['dual_bull']} | TRI_BEAR: {summary['tw']['tri_bear']}, DUAL_BEAR: {summary['tw']['dual_bear']} | MIXED: {summary['tw']['mixed']}", flush=True)
    print("TW BULLS:", [f"{x['symbol']}({x['name']})" for x in summary["tw"]["bull_list"]], flush=True)
    print("TW BEARS (sample):", [f"{x['symbol']}({x['name']})" for x in summary["tw"]["bear_list"][:10]], flush=True)
    print(f"US -> TRI_BULL: {summary['us']['tri_bull']}, DUAL_BULL: {summary['us']['dual_bull']} | TRI_BEAR: {summary['us']['tri_bear']}, DUAL_BEAR: {summary['us']['dual_bear']} | MIXED: {summary['us']['mixed']}", flush=True)
    print("US BULLS:", [f"{x['symbol']}({x['name']})" for x in summary["us"]["bull_list"]], flush=True)
    print("US BEARS (sample):", [f"{x['symbol']}({x['name']})" for x in summary["us"]["bear_list"][:10]], flush=True)
    print(f"Vetoed Buy Signals: {vetoed_count} | Elapsed: {time.time()-t0:.1f}s", flush=True)

if __name__ == "__main__":
    run_tri_resonance()

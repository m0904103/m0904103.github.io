# -*- coding: utf-8 -*-
"""
Gen28-VCP Volatility Contraction Pattern Engine (阿村伯 10/08 VCP 樞紐點 × 顏春煌教授波動率收斂)
雙師圓桌決議版：
- 【熊市自動休眠閘門】：當大盤處於 BEAR_LIQUIDITY_CRISIS 或全市場 60MA 寬度 < 30%（或台股寬度 < 25%）時，
  自動進入 HIBERNATING_BEAR_MARKET 模式，完全鎖死不發出 VCP 買進訊號！
- 【牛市自動啟動】：當大盤寬度回升 >= 30% 且脫離危機模式時，自動喚醒 ACTIVE_BULL_HUNTER，
  篩選符合「站穩60/200MA + 波動率逐步收縮 + 窒息量/布林擠壓 + 逼近樞紐點(Pivot)」之強勢波段股。
"""
import json
import os
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

def check_vcp_for_df(df):
    """
    Evaluate VCP (Volatility Contraction Pattern) on a single OHLCV DataFrame.
    Returns dict with vcp_pass, pivot_price, contraction_ratio, vol_dry_ratio, dist_to_pivot_pct.
    """
    if df is None or len(df) < 205:
        return None
    close = df["Close"].dropna()
    high = df["High"].dropna()
    low = df["Low"].dropna()
    vol = df["Volume"].dropna()
    if len(close) < 205:
        return None

    c = float(close.iloc[-1])
    ma60 = float(close.rolling(60).mean().iloc[-1])
    ma60_prev = float(close.rolling(60).mean().iloc[-6])
    ma200 = float(close.rolling(200).mean().iloc[-1])

    # Rule A: Strict Bull Stage-2 Trend (Teacher Yen MA60 rising + above MA200)
    trend_ok = (c > ma60) and (ma60 > ma200) and (ma60 >= ma60_prev)

    # Rule B: Volatility Contraction (recent 10d range < prior 20d range * 0.75, and recent range <= 12%)
    r_recent = (float(high.tail(10).max()) - float(low.tail(10).min())) / c
    r_prior = (float(high.iloc[-30:-10].max()) - float(low.iloc[-30:-10].min())) / c
    contraction_ratio = round(r_recent / r_prior, 3) if r_prior > 0 else 9.9
    vol_contract_ok = (r_recent <= 0.12) and (contraction_ratio <= 0.75)

    # Rule C: Volume Dry-Up (5d avg vol < 50d avg vol * 0.80)
    v5 = float(vol.tail(5).mean())
    v50 = float(vol.tail(50).mean())
    vol_dry_ratio = round(v5 / v50, 3) if v50 > 0 else 9.9
    vol_dry_ok = vol_dry_ratio <= 0.80

    # Rule D: Pivot Point (20-day high) proximity (-5% ~ +2%)
    pivot = float(high.tail(20).max())
    dist_pct = round((c - pivot) / pivot * 100.0, 2) if pivot > 0 else -99.0
    pivot_ok = (-5.0 <= dist_pct <= 2.5)

    vcp_pass = bool(trend_ok and vol_contract_ok and vol_dry_ok and pivot_ok)
    return {
        "vcp_pass": vcp_pass,
        "pivot_price": round(pivot, 2),
        "dist_to_pivot_pct": dist_pct,
        "contraction_ratio": contraction_ratio,
        "recent_range_pct": round(r_recent * 100.0, 2),
        "vol_dry_ratio": vol_dry_ratio,
        "trend_ok": trend_ok,
    }

def run_vcp_module():
    main_json = SCAN_PATHS[0]
    with open(main_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    mr = data.get("market_regime") or {}
    regime_code = str(mr.get("code", "BEAR_LIQUIDITY_CRISIS"))
    tw_b = float(mr.get("tw_breadth_60ma") or 0)
    us_b = float(mr.get("us_breadth_60ma") or 0)
    tot_b = float(mr.get("total_breadth_60ma") or 0)

    # Dual-Master Bear Market Auto-Hibernation Gate
    is_bear_hibernating = (
        "BEAR" in regime_code.upper()
        or "CRISIS" in regime_code.upper()
        or tot_b < 30.0
        or (tw_b < 25.0 and us_b < 35.0)
    )

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vcp_summary = {
        "engine": "Gen28-VCP (阿村伯波動收縮樞紐點 × 顏教授波動率/季線保護)",
        "updated_at": now_str,
        "status": "HIBERNATING_BEAR_MARKET" if is_bear_hibernating else "ACTIVE_BULL_HUNTER",
        "status_label": "💤 熊市自動休眠中（防三角收斂向下破底）" if is_bear_hibernating else "🚀 多頭啟動中（自動獵捕 VCP 樞紐突破股）",
        "wake_condition": "總體 60MA 寬度 ≥ 30% 且脫離 BEAR/CRISIS 模式即自動甦醒啟動",
        "candidates": [],
    }

    if is_bear_hibernating:
        print(f"[Gen28-VCP] Market Regime={regime_code}, Breadth={tot_b}% -> HIBERNATING_BEAR_MARKET (0 buy signals emitted).", flush=True)
    else:
        stocks = data.get("stocks", [])
        symbols = [s["symbol"] for s in stocks if s.get("symbol")]
        print(f"[Gen28-VCP] ACTIVE_BULL_HUNTER! Scanning {len(symbols)} symbols...", flush=True)
        for i in range(0, len(symbols), 65):
            chunk = symbols[i:i+65]
            df = yf.download(chunk, period="1y", interval="1d", group_by="ticker", progress=False, threads=True, auto_adjust=True)
            if df is None or df.empty:
                continue
            for sym in chunk:
                try:
                    sub = df if len(chunk) == 1 else df[sym]
                    res = check_vcp_for_df(sub)
                    if res and res["vcp_pass"]:
                        st_obj = next((x for x in stocks if x.get("symbol") == sym), {})
                        vcp_summary["candidates"].append({
                            "symbol": sym,
                            "name": st_obj.get("name", sym),
                            "close": st_obj.get("close") or st_obj.get("price"),
                            **res
                        })
                except Exception:
                    pass
        print(f"[Gen28-VCP] Found {len(vcp_summary['candidates'])} VCP candidates.", flush=True)

    data["vcp_module"] = vcp_summary
    data["engine"] = "V4-Yen × Dr.Tsun Gen28 (三週期共振 + VCP熊市自動休眠 + 尾盤確認 + 雙均線防雷)"
    for path in SCAN_PATHS:
        atomic_write_json(path, data)
    print(f"[Gen28-VCP] Written cleanly to scan_results.json ({vcp_summary['status']}).", flush=True)

if __name__ == "__main__":
    run_vcp_module()

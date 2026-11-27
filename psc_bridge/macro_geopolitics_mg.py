# -*- coding: utf-8 -*-
"""
================================================================================
🌍 Gen 31 全球經貿與總經地緣風險雷達 (Macro & Geopolitics Radar — MG Engine)
================================================================================
學術核心來源：國立空中大學《115上_全球經貿個案解讀(一)》（方晨教授）
淬鍊四大實戰總經與地緣模組：
  1. Ch.6 / Ch.7 / Ch.11 全球六大即時總經壓力儀表板：
     美債10年殖利率 (^TNX)、美元指數 (DX-Y.NYB)、台幣匯率 (TWD=X)、
     WTI原油 (CL=F，荷姆茲海峽封鎖雷達)、黃金 (GC=F，去美元化指標)、那斯達克/標普剪刀差。
  2. Ch.6-5 台灣大麥克 PPP 偏離度與出口匯損警戒儀：
     計算新台幣結構性低估幅度與急升匯損衝擊（避免台股出口電子股被匯率雙殺）。
  3. Ch.2-2 & Ch.5-1/5-2 川普關稅與冗餘供應鏈脆弱度矩陣：
     標註高關稅/轉口風險（如越南/中國組裝曝險）與內需防禦/關稅絕緣標的。
  4. Ch.9-1 AI 資本支出狂熱與泡沫修正指標：
     結合 2026 五大巨頭 7,000 億美元 Capex 基準與即時 NDX/SPX 20日相對強弱，判讀 AI 泡沫階段。
================================================================================
"""
import json
import math
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

MACRO_TICKERS = {
    "us10y": ("^TNX", "美國10年期公債殖利率 (%)"),
    "dxy": ("DX-Y.NYB", "美元指數 (DXY)"),
    "usdtwd": ("TWD=X", "美元兌新台幣 (USD/TWD)"),
    "wti_oil": ("CL=F", "WTI 原油期貨 (USD/桶)"),
    "gold": ("GC=F", "黃金期貨 (USD/盎司)"),
    "spx": ("^GSPC", "標普500指數 (S&P 500)"),
    "ndx": ("^NDX", "那斯達克100指數 (NDX)"),
}

# Ch.2-2 & Ch.5-2 關稅與地緣供應鏈曝險分類表 (結合 Gen 31 紅隊稽核)
SUPPLY_CHAIN_EXPOSURE: Dict[str, Dict[str, Any]] = {
    # 高關稅／轉口／地緣高曝險 (HIGH_EXPOSURE)
    "3017.TW": {"grade": "HIGH_EXPOSURE", "tag": "越南/中國散熱轉口 301 關稅曝險", "penalty": -15},
    "2317.TW": {"grade": "HIGH_EXPOSURE", "tag": "中國/墨西哥代工組裝關稅敏感", "penalty": -10},
    "2382.TW": {"grade": "HIGH_EXPOSURE", "tag": "AI 伺服器跨國供應鏈關稅敏感", "penalty": -8},
    "3231.TW": {"grade": "HIGH_EXPOSURE", "tag": "跨國組裝廠關稅與匯率雙重敏感", "penalty": -8},
    "NVDA": {"grade": "HIGH_EXPOSURE", "tag": "對中晶片出口管制＋台海地緣溢價", "penalty": -10},
    "ASML": {"grade": "HIGH_EXPOSURE", "tag": "對中設備禁令＋歐洲能源成本曝險", "penalty": -10},
    "AAPL": {"grade": "MANAGED", "tag": "中國/印度雙鏈轉移中，具高定價權", "penalty": -4},
    "2330.TW": {"grade": "MANAGED", "tag": "全球獨家先進製程定價權＋美日德冗餘設廠", "penalty": -3},
    "AVGO": {"grade": "MANAGED", "tag": "客製化 ASIC 龍頭，美國本土設計主導", "penalty": -3},
    # 關稅絕緣／地緣受惠／內需防禦 (INSULATED)
    "SGOV": {"grade": "INSULATED", "tag": "美國短債現金堡壘（零關稅、零信用風險）", "penalty": 0},
    "PGR": {"grade": "INSULATED", "tag": "純美國本土產險（零關稅、高利率受惠）", "penalty": 0},
    "JPM": {"grade": "INSULATED", "tag": "美國最大銀行（高殖利率環境淨利差受惠）", "penalty": 0},
    "LLY": {"grade": "INSULATED", "tag": "高毛利剛性醫療（專利保護＋抗景氣循環）", "penalty": 0},
    "ITA": {"grade": "INSULATED", "tag": "美國航太國防（地緣衝突直接受惠盾牌）", "penalty": 0},
    "XLE": {"grade": "INSULATED", "tag": "美國能源龍頭（荷姆茲油價飆升直接對沖）", "penalty": 0},
    "GLD": {"grade": "INSULATED", "tag": "實體黃金（去美元化＋美債赤字避險核心）", "penalty": 0},
    "VRTX": {"grade": "INSULATED", "tag": "生技孤兒藥壟斷（零關稅敏感度）", "penalty": 0},
}


def fetch_yahoo_series(ticker: str, range_str: str = "1mo") -> Optional[Dict[str, Any]]:
    """純 stdlib 抓取 Yahoo Finance 歷史收盤與即時報價，計算 1日/5日/20日變動率。"""
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(ticker)}"
        f"?interval=1d&range={range_str}"
    )
    req = urllib.request.Request(url, headers=YAHOO_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        res = data.get("chart", {}).get("result", [])
        if not res:
            return None
        meta = res[0].get("meta", {})
        closes_raw = res[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        closes = [float(c) for c in closes_raw if c is not None]
        if not closes:
            return None
        latest = float(meta.get("regularMarketPrice") or closes[-1])
        prev_1d = closes[-2] if len(closes) >= 2 else latest
        prev_5d = closes[-6] if len(closes) >= 6 else closes[0]
        prev_20d = closes[0]
        chg_1d = round((latest - prev_1d) / prev_1d * 100, 2) if prev_1d else 0.0
        chg_5d = round((latest - prev_5d) / prev_5d * 100, 2) if prev_5d else 0.0
        chg_20d = round((latest - prev_20d) / prev_20d * 100, 2) if prev_20d else 0.0
        return {
            "ticker": ticker,
            "price": round(latest, 3),
            "chg_1d_pct": chg_1d,
            "chg_5d_pct": chg_5d,
            "chg_20d_pct": chg_20d,
        }
    except Exception:
        return None


def compute_taiwan_ppp_fx_gauge(usdtwd_price: float, chg_5d_pct: float) -> Dict[str, Any]:
    """
    Ch.6-5 臺灣總體經濟與失衡的貨幣政策 — 大麥克指數 (Big Mac PPP) 模型：
      課堂基準：美國大麥克 $5.69 USD vs 台灣新台幣 75 元（折合 $2.28 USD）
      隱含 PPP 匯率 = 75 / 5.69 = 13.18 TWD/USD
    """
    us_bigmac_usd = 5.69
    tw_bigmac_twd = 75.0
    implied_ppp = round(tw_bigmac_twd / us_bigmac_usd, 2)
    undervaluation_pct = round((1.0 - (implied_ppp / usdtwd_price)) * 100, 1) if usdtwd_price > 0 else 0.0

    fx_alerts = []
    if usdtwd_price >= 32.5:
        fx_alerts.append("台幣偏弱(>32.5)，外資匯出壓力大且觸及美國匯率操縱觀察警戒線")
    if chg_5d_pct <= -1.2:
        fx_alerts.append(f"台幣 5 日急升 {abs(chg_5d_pct)}%，小心台股出口電子股毛利率與匯損雙殺！")
    elif chg_5d_pct >= 1.2:
        fx_alerts.append(f"台幣 5 日急貶 +{chg_5d_pct}%，反映外資大舉撤出提款。")

    return {
        "usdtwd": usdtwd_price,
        "big_mac_implied_ppp": implied_ppp,
        "twd_ppp_undervaluation_pct": undervaluation_pct,
        "usdtwd_5d_chg_pct": chg_5d_pct,
        "status": "ALERT" if fx_alerts else "STABLE",
        "alerts": fx_alerts or ["台幣匯率處於可控區間，無急升匯損或外資失控撤離訊號"],
    }


def evaluate_ai_bubble_cycle(ndx_20d: float, spx_20d: float, live_vix: float) -> Dict[str, Any]:
    """
    Ch.9-1 AI 投資市場狂熱與泡沫風險：
      方晨老師基準：2026 五大科技巨頭 AI Capex 達 7,000 億美元（超過全球油氣探勘 5,700 億美元），
      若生成式 AI 商業化回收跟不上算力折舊，市場會從「狂熱估值」轉為「殺估值修正」。
    """
    spread_20d = round(ndx_20d - spx_20d, 2)
    if spread_20d <= -2.0 and live_vix >= 22.0:
        phase = "DELEVERAGING_SHAKEOUT"
        verdict = "AI 權值股正經歷殺估值去槓桿（NDX 顯著弱於 SPX），嚴禁抄底高本益比無現金流 AI 股！"
    elif spread_20d >= 4.0 and live_vix < 16.0:
        phase = "EUPHORIA_OVERHEATED"
        verdict = "AI 資本狂熱過熱區，留意 Capex 回收落差與高檔背離，堅持分批停利。"
    else:
        phase = "HEALTHY_DIGESTION"
        verdict = "科技與大盤輪動消化中，以高自由現金流龍頭與防禦資產均衡配置。"

    return {
        "ndx_20d_pct": ndx_20d,
        "spx_20d_pct": spx_20d,
        "ndx_vs_spx_spread_20d_pct": spread_20d,
        "bigtech_2026_capex_usd_b": 700,
        "oil_gas_capex_benchmark_usd_b": 570,
        "phase": phase,
        "verdict": verdict,
    }


def scan_supply_chain_exposure(stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ch.2-2 & Ch.5-2 掃描掃描池中的高關稅曝險標的與關稅絕緣防禦標的。"""
    high_risk = []
    insulated = []
    seen = set()
    for s in stocks:
        sym = str(s.get("symbol", "")).upper()
        if sym in seen:
            continue
        seen.add(sym)
        info = SUPPLY_CHAIN_EXPOSURE.get(sym)
        if not info:
            continue
        entry = {
            "symbol": sym,
            "name": s.get("name", sym),
            "grade": info["grade"],
            "tag": info["tag"],
            "price": s.get("price"),
        }
        if info["grade"] == "HIGH_EXPOSURE":
            high_risk.append(entry)
        elif info["grade"] == "INSULATED":
            insulated.append(entry)
    return {
        "high_tariff_exposure_count": len(high_risk),
        "high_tariff_exposure_list": high_risk,
        "tariff_insulated_count": len(insulated),
        "tariff_insulated_list": insulated,
    }


def run_macro_geopolitics_radar(
    stocks: Optional[List[Dict[str, Any]]] = None,
    live_vix: float = 24.62,
) -> Dict[str, Any]:
    """執行完整 Gen 31 全球經貿與總經地緣風險雷達。"""
    telemetry: Dict[str, Any] = {}
    for key, (ticker, label) in MACRO_TICKERS.items():
        res = fetch_yahoo_series(ticker, range_str="1mo")
        if res:
            res["label"] = label
            telemetry[key] = res
        else:
            telemetry[key] = {"ticker": ticker, "label": label, "price": None, "chg_1d_pct": 0.0, "chg_5d_pct": 0.0, "chg_20d_pct": 0.0}

    # 計算總經地緣綜合壓力分數 (0~100，越高代表環境越險峻)
    stress = 20.0
    drivers: List[str] = []

    us10y = telemetry["us10y"]["price"]
    if us10y is not None:
        if us10y >= 4.75:
            stress += 22.0
            drivers.append(f"美債10Y殖利率飆至 {us10y:.2f}% (>4.75% 財政赤字殺估值紅線)")
        elif us10y >= 4.30:
            stress += 12.0
            drivers.append(f"美債10Y殖利率偏高 {us10y:.2f}% (壓抑長久期科技股估值)")

    wti = telemetry["wti_oil"]["price"]
    wti_20d = telemetry["wti_oil"]["chg_20d_pct"]
    if wti is not None:
        if wti >= 90.0 or wti_20d >= 15.0:
            stress += 25.0
            drivers.append(f"WTI原油警報 ${wti:.2f} (20日 {wti_20d:+.1f}%) — Ch.11 能源危機／荷姆茲海峽停滯性通膨衝擊")
        elif wti >= 78.0 or wti_20d >= 8.0:
            stress += 14.0
            drivers.append(f"WTI原油走揚 ${wti:.2f} (20日 {wti_20d:+.1f}%) — 需防能源通膨反撲")

    dxy = telemetry["dxy"]["price"]
    if dxy is not None and dxy >= 105.0:
        stress += 12.0
        drivers.append(f"強勢美元 DXY={dxy:.2f} (>=105) 抽離新興市場與台股流動性")

    gold_20d = telemetry["gold"]["chg_20d_pct"]
    if gold_20d >= 6.0:
        stress += 8.0
        drivers.append(f"黃金 20 日急漲 {gold_20d:+.1f}%，反映避險與去美元化買盤升溫")

    if live_vix >= 25.0:
        stress += 18.0
        drivers.append(f"VIX={live_vix:.2f} 進入高波動警戒區")
    elif live_vix >= 20.0:
        stress += 10.0
        drivers.append(f"VIX={live_vix:.2f} 處於震盪防禦區")

    stress = round(min(100.0, max(0.0, stress)), 1)

    if stress >= 75.0:
        regime = "RED_GEOPOLITICAL_SHOCK"
        cash_floor_pct = 70
        action_note = "總經地緣高壓紅燈！嚴守 70% 現金堡壘，僅配置關稅絕緣(SGOV/PGR/LLY)與地緣對沖(XLE/GLD/ITA)。"
    elif stress >= 55.0:
        regime = "ORANGE_STAGFLATION_RISK"
        cash_floor_pct = 55
        action_note = "停滯性通膨與關稅摩擦警戒！維持 55%~70% 高現金水位，避開高關稅轉口股與高本益比 AI 股。"
    elif stress >= 35.0:
        regime = "YELLOW_TARIFF_FRICTION"
        cash_floor_pct = 40
        action_note = "總經政策不確定區，維持 40% 以上現金底線，精選具定價權與冗餘供應鏈龍頭。"
    else:
        regime = "GREEN_EXPANSION"
        cash_floor_pct = 30
        action_note = "總經與地緣環境平穩，依 Gen 31 憲法保留至少 30% 現金底線，順勢操作多頭共振股。"

    usdtwd_price = telemetry["usdtwd"]["price"] or 32.0
    ppp_gauge = compute_taiwan_ppp_fx_gauge(usdtwd_price, telemetry["usdtwd"]["chg_5d_pct"])
    ai_cycle = evaluate_ai_bubble_cycle(
        telemetry["ndx"]["chg_20d_pct"],
        telemetry["spx"]["chg_20d_pct"],
        live_vix,
    )
    sc_scan = scan_supply_chain_exposure(stocks or [])

    return {
        "source_course": "國立空中大學《115上_全球經貿個案解讀(一)》（方晨教授）",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "macro_stress_score": stress,
        "macro_regime": regime,
        "recommended_cash_floor_pct": cash_floor_pct,
        "action_note": action_note,
        "stress_drivers": drivers or ["目前六大總經指標無極端失控訊號"],
        "live_telemetry": telemetry,
        "taiwan_ppp_fx_gauge": ppp_gauge,
        "ai_bubble_cycle": ai_cycle,
        "supply_chain_tariff_audit": sc_scan,
    }


if __name__ == "__main__":
    import sys
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rep = run_macro_geopolitics_radar()
    print(json.dumps(rep, ensure_ascii=False, indent=2))

# -*- coding: utf-8 -*-
"""
================================================================================
🏦 Gen 31 貨幣銀行與流動性週期引擎 (Monetary & Liquidity Engine — ML Engine)
================================================================================
學術核心來源：
  - 國立空中大學《貨幣銀行學》（黃昱程、楊啟均教授，392 講次）
  - 國立空中大學《總體經濟學》（IS-LM / AD-AS 貨幣傳導模型，210 講次）

淬鍊四大實戰貨幣與信用流動性模組：
  1. 利率期限結構 (Yield Curve Clock)：
     直連美債 10Y (^TNX)、5Y (^FVX)、3M (^IRX) 計算 10Y-3M 與 10Y-5Y 利差，
     辨識「倒掛警戒」、「解除倒掛陡峭化（歷史上最容易爆發衰退的窗口）」與「正常擴張」。
  2. 費雪方程式 (Fisher Equation: r = i - pi_e)：
     以 10Y 名目殖利率扣除通膨預期，量化「實質利率」對高本益比科技股之殺估值重力。
  3. 銀行信用傳導管道 (Credit Spread Proxy: HYG / IEF & KRE / XLF)：
     監控高收益債對公債比值動能與美國區域銀行體質，提早 2~6 週偵測信用緊縮。
  4. IS-LM 貨幣流動性總評 (0~100 流動性壓力分數)：
     直接輸出流動性象限，輔助 Gen 31 決定進攻或縮表防守。
================================================================================
"""
import json
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

MONETARY_TICKERS = {
    "us10y": ("^TNX", "美國10年期公債殖利率 (%)"),
    "us5y": ("^FVX", "美國5年期公債殖利率 (%)"),
    "us3m": ("^IRX", "美國3個月國庫券殖利率 (%)"),
    "hyg": ("HYG", "高收益公司債 ETF (信用風險溫度計)"),
    "ief": ("IEF", "美國7-10年中期公債 ETF (無風險基準)"),
    "kre": ("KRE", "美國區域銀行 ETF (銀行體系壓力)"),
    "xlf": ("XLF", "美國大型金融股 ETF"),
}


def _fetch_series(ticker: str, range_str: str = "1mo") -> Optional[Dict[str, Any]]:
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
        prev_5d = closes[-6] if len(closes) >= 6 else closes[0]
        prev_20d = closes[0]
        return {
            "ticker": ticker,
            "price": round(latest, 3),
            "chg_5d_pct": round((latest - prev_5d) / prev_5d * 100, 2) if prev_5d else 0.0,
            "chg_20d_pct": round((latest - prev_20d) / prev_20d * 100, 2) if prev_20d else 0.0,
        }
    except Exception:
        return None


def analyze_yield_curve(us10y: Optional[float], us5y: Optional[float], us3m: Optional[float]) -> Dict[str, Any]:
    """《貨幣銀行學》利率期限結構：計算 10Y-3M 與 10Y-5Y 利差 (bps)。"""
    if us10y is None or us3m is None:
        return {"status": "UNAVAILABLE", "spread_10y_3m_bps": None, "spread_10y_5y_bps": None}

    sp_10_3m = round((us10y - us3m) * 100, 1)
    sp_10_5y = round((us10y - us5y) * 100, 1) if us5y is not None else None

    if sp_10_3m < -10:
        curve_state = "INVERTED_RECESSION_WARNING"
        note = f"10Y-3M 倒掛 {sp_10_3m:+.1f} bps：銀行借短放長利差轉負，信用創造受阻，衰退倒數計時。"
    elif -10 <= sp_10_3m <= 35:
        curve_state = "FLAT_UNINVERSION_DANGER_ZONE"
        note = f"10Y-3M 處於 {sp_10_3m:+.1f} bps 平坦／剛解除倒掛區：歷史上股市主跌段常發生在解除倒掛前後！"
    elif us10y >= 4.75 and sp_10_3m > 35:
        curve_state = "BEAR_STEEPENING_FISCAL_STRESS"
        note = f"10Y-3M 正斜率 +{sp_10_3m:.1f} bps 但長端利率飆破 4.75%（熊市陡峭化）：債市正在懲罰通膨與財政赤字。"
    else:
        curve_state = "NORMAL_HEALTHY_SLOPE"
        note = f"10Y-3M 正常正斜率 +{sp_10_3m:.1f} bps，銀行信用中介傳導順暢。"

    return {
        "us10y_pct": us10y,
        "us5y_pct": us5y,
        "us3m_pct": us3m,
        "spread_10y_3m_bps": sp_10_3m,
        "spread_10y_5y_bps": sp_10_5y,
        "curve_state": curve_state,
        "note": note,
    }


def compute_fisher_real_rate(us10y: Optional[float], inflation_expectation_pct: float = 2.6) -> Dict[str, Any]:
    """
    《貨幣銀行學》費雪方程式 (Fisher Equation): r = i - pi_e
    實質利率 > 2.0% 時，成長股折現率壓力大增；> 2.2% 進入高壓殺估值區。
    """
    if us10y is None:
        return {"status": "UNAVAILABLE"}
    real_rate = round(us10y - inflation_expectation_pct, 2)
    # 簡化版盈餘殖利率合理本益比上限估算 (ERP 基準 3.0%)
    implied_fair_pe = round(100.0 / max(2.0, us10y + 1.5), 1)
    if real_rate >= 2.2:
        pressure = "HIGH_VALUATION_GRAVITY"
        desc = f"實質利率達 {real_rate:.2f}%（高重力區），合理市場本益比壓縮至約 {implied_fair_pe}x，高 PE 股極易殺估值。"
    elif real_rate >= 1.5:
        pressure = "MODERATE_RESTRICTIVE"
        desc = f"實質利率 {real_rate:.2f}% 維持緊縮水準，資金偏好高自由現金流與低本益比價值股。"
    else:
        pressure = "ACCOMMODATIVE"
        desc = f"實質利率 {real_rate:.2f}% 寬鬆友善，有利股市本益比擴張。"
    return {
        "nominal_10y_pct": us10y,
        "expected_inflation_pct": inflation_expectation_pct,
        "fisher_real_rate_pct": real_rate,
        "implied_fair_pe_ceiling": implied_fair_pe,
        "pressure": pressure,
        "desc": desc,
    }


def run_monetary_liquidity_engine(inflation_expectation_pct: float = 2.6) -> Dict[str, Any]:
    """執行 Gen 31 貨幣銀行與流動性週期引擎。"""
    data: Dict[str, Any] = {}
    for k, (ticker, label) in MONETARY_TICKERS.items():
        s = _fetch_series(ticker, range_str="1mo")
        if s:
            s["label"] = label
            data[k] = s
        else:
            data[k] = {"ticker": ticker, "label": label, "price": None, "chg_5d_pct": 0.0, "chg_20d_pct": 0.0}

    yc = analyze_yield_curve(data["us10y"]["price"], data["us5y"]["price"], data["us3m"]["price"])
    fisher = compute_fisher_real_rate(data["us10y"]["price"], inflation_expectation_pct)

    # 信用傳導管道：HYG 相對 IEF 20 日超額報酬 (負值擴大 = 信用利差惡化、垃圾債被拋售)
    hyg_20d = data["hyg"]["chg_20d_pct"]
    ief_20d = data["ief"]["chg_20d_pct"]
    credit_rel_20d = round(hyg_20d - ief_20d, 2)

    # 區域銀行相對大型金融股 20 日表現 (負值擴大 = 中小銀行流動性承壓)
    kre_rel_20d = round(data["kre"]["chg_20d_pct"] - data["xlf"]["chg_20d_pct"], 2)

    if credit_rel_20d <= -2.5:
        credit_status = "CREDIT_CRUNCH_WARNING"
        credit_note = f"高收益債 20 日落後美債 {credit_rel_20d:+.2f}%：企業信用利差急速擴大，防範違約傳染！"
    elif credit_rel_20d <= -1.0:
        credit_status = "CREDIT_TIGHTENING"
        credit_note = f"高收益債 20 日落後美債 {credit_rel_20d:+.2f}%：信用市場開始收緊，遠離高負債與高 CDS 公司。"
    else:
        credit_status = "CREDIT_STABLE"
        credit_note = f"高收益債相對美債 20 日 {credit_rel_20d:+.2f}%，尚未出現系統性信用凍結。"

    # 綜合流動性壓力分數 (0~100)
    liq_stress = 25.0
    if yc.get("curve_state") in ("INVERTED_RECESSION_WARNING", "BEAR_STEEPENING_FISCAL_STRESS"):
        liq_stress += 25.0
    elif yc.get("curve_state") == "FLAT_UNINVERSION_DANGER_ZONE":
        liq_stress += 18.0

    if fisher.get("pressure") == "HIGH_VALUATION_GRAVITY":
        liq_stress += 22.0
    elif fisher.get("pressure") == "MODERATE_RESTRICTIVE":
        liq_stress += 12.0

    if credit_status == "CREDIT_CRUNCH_WARNING":
        liq_stress += 25.0
    elif credit_status == "CREDIT_TIGHTENING":
        liq_stress += 12.0

    if kre_rel_20d <= -4.0:
        liq_stress += 10.0

    liq_stress = round(min(100.0, max(0.0, liq_stress)), 1)
    if liq_stress >= 70.0:
        regime = "RESTRICTIVE_LIQUIDITY_SQUEEZE"
    elif liq_stress >= 45.0:
        regime = "TIGHT_MONETARY_HEADWIND"
    else:
        regime = "ACCOMMODATIVE_LIQUIDITY"

    return {
        "source_courses": [
            "國立空中大學《貨幣銀行學》（黃昱程、楊啟均教授）",
            "國立空中大學《總體經濟學》（IS-LM / AD-AS 貨幣傳導）",
        ],
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "liquidity_stress_score": liq_stress,
        "liquidity_regime": regime,
        "yield_curve_clock": yc,
        "fisher_real_rate": fisher,
        "credit_transmission": {
            "hyg_20d_pct": hyg_20d,
            "ief_20d_pct": ief_20d,
            "hyg_vs_ief_spread_20d_pct": credit_rel_20d,
            "kre_vs_xlf_20d_pct": kre_rel_20d,
            "status": credit_status,
            "note": credit_note,
        },
    }


if __name__ == "__main__":
    import sys
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(run_monetary_liquidity_engine(), ensure_ascii=False, indent=2))

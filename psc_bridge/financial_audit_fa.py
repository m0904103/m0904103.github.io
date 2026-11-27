# -*- coding: utf-8 -*-
"""
================================================================================
📑 空大《財務資訊分析與應用》實戰防雷模組 — Gen 31 Financial Quality Auditor
================================================================================
直接蒸餾自 D:\02_Academic_Study\空大課程\財務資訊分析與應用 (72.1 萬字全 6 模組)：
  • 模組二/三：本業獲利安全邊際 (毛利率 / 營益率 / 營業槓桿健康度)
  • 模組三：杜邦獲利品質 × 阿村伯三率三升 (three_rates_rising + rev_yoy)
  • 模組四：盈餘品質勾稽 (防範「本業虧損卻靠業外灌水」與盈餘操縱)
  • 模組五：企業評價與安全邊際 (P/E、P/B、殖利率交叉辨識「高估泡沫 vs 衰退價值陷阱」)
純 Python 標準庫實作（零外部依賴）。
================================================================================
"""
from typing import Dict, List, Any


def audit_single_stock_financials(stock: Dict[str, Any]) -> Dict[str, Any]:
    fund = stock.get("fundamentals") or {}
    sym = str(stock.get("symbol", "")).strip()
    name = str(stock.get("name", sym))

    gm = fund.get("gross_margin")
    om = fund.get("op_margin")
    nm = fund.get("net_margin")
    yoy = fund.get("rev_yoy")
    pe = fund.get("pe_ratio")
    pb = fund.get("pb_ratio")
    dy = fund.get("div_yield")
    tr = bool(fund.get("three_rates_rising", False))

    # 若無財報細項欄位（例如部分美股 ETF 或未補齊個股），標記為 NA 不誤殺
    if gm is None and om is None and pe is None:
        return {"symbol": sym, "name": name, "grade": "N/A", "fa_score": None, "red_flags": [], "strengths": []}

    score = 50.0
    red_flags: List[str] = []
    strengths: List[str] = []

    # 1. 模組三：三率與本業安全邊際
    if tr:
        score += 15.0
        strengths.append("三率三升")
    if gm is not None:
        gm = float(gm)
        if gm >= 35.0:
            score += 10.0
            strengths.append(f"高毛利({gm:.1f}%)")
        elif gm < 10.0:
            score -= 10.0
            red_flags.append(f"低毛利警戒({gm:.1f}%)")

    if om is not None:
        om = float(om)
        if om >= 15.0:
            score += 10.0
            strengths.append(f"高本業營益({om:.1f}%)")
        elif om < 0:
            score -= 20.0
            red_flags.append(f"本業虧損(營益率{om:.1f}%)")

    # 2. 模組四：盈餘品質勾稽（抓本業差卻靠業外灌水的假獲利！）
    if om is not None and nm is not None:
        nm = float(nm)
        if om < 5.0 and nm > om + 6.0:
            score -= 15.0
            red_flags.append(f"盈餘品質警訊(業外灌水: 營益{om:.1f}% vs 淨利{nm:.1f}%)")
        elif nm < 0:
            score -= 12.0
            red_flags.append(f"稅後虧損({nm:.1f}%)")

    # 3. 營收動能檢核
    if yoy is not None:
        yoy = float(yoy)
        if yoy >= 20.0:
            score += 10.0
            strengths.append(f"營收強增({yoy:+.1f}%)")
        elif yoy <= -15.0:
            score -= 12.0
            red_flags.append(f"營收衰退({yoy:+.1f}%)")

    # 4. 模組五：估值安全邊際（防高估泡沫 & 防低PB衰退陷阱）
    if pe is not None and float(pe) > 0:
        pe = float(pe)
        if pe <= 16.0 and (yoy is None or yoy >= 0):
            score += 10.0
            strengths.append(f"估值安全邊際(PE {pe:.1f}x)")
        elif pe >= 45.0 and (yoy is None or yoy < 25.0):
            score -= 15.0
            red_flags.append(f"高估值泡沫警戒(PE {pe:.1f}x)")

    if pb is not None and om is not None:
        pb = float(pb)
        if pb < 1.0 and om < 5.0:
            score -= 10.0
            red_flags.append(f"低PB價值陷阱(PB {pb:.2f}x 但本業營益僅 {om:.1f}%)")

    if dy is not None and float(dy) >= 4.0 and (om is None or om >= 8.0):
        score += 5.0
        strengths.append(f"穩健殖利率({float(dy):.1f}%)")

    score = max(0.0, min(100.0, round(score, 1)))
    if score >= 80 and not red_flags:
        grade = "A+"
    elif score >= 68:
        grade = "A"
    elif score >= 52:
        grade = "B"
    elif score >= 38:
        grade = "C"
    else:
        grade = "D (財報地雷)"

    return {
        "symbol": sym,
        "name": name,
        "grade": grade,
        "fa_score": score,
        "pe": pe,
        "rev_yoy": round(float(yoy), 1) if yoy is not None else None,
        "red_flags": red_flags,
        "strengths": strengths,
    }


def audit_market_financials(stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    audited = []
    for s in stocks:
        res = audit_single_stock_financials(s)
        if res["fa_score"] is not None:
            tech = s.get("technicals") or {}
            p = float(s.get("price") or 0.0)
            ma60 = float(tech.get("ma60") or s.get("ma60") or 0.0)
            res["price"] = p
            res["above_ma60"] = (p > 0 and ma60 > 0 and p >= ma60)
            audited.append(res)

    top_quality = sorted(audited, key=lambda x: x["fa_score"], reverse=True)[:8]
    landmines = sorted([x for x in audited if x["red_flags"]], key=lambda x: x["fa_score"])[:8]

    return {
        "source_course": "國立空中大學《財務資訊分析與應用》(72.1萬字：三率安全邊際/盈餘品質勾稽/價值陷阱防雷)",
        "audited_count": len(audited),
        "grade_a_plus_count": sum(1 for x in audited if x["grade"] == "A+"),
        "red_flag_count": sum(1 for x in audited if x["red_flags"]),
        "top_quality_stocks": top_quality,
        "financial_landmines": landmines,
    }

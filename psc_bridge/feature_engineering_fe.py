# -*- coding: utf-8 -*-
"""
================================================================================
📐 空大《資料科學的特徵工程》實戰量化模組 — Gen 31 Feature Engineering Engine
================================================================================
直接蒸餾自 D:\02_Academic_Study\空大課程\資料科學的特徵工程 (12 章核心精華)：
  • 第 3 章 + 第 8 章：離散分箱 × 交互資訊 (Mutual Information, MI) 因子預測力評分
  • 第 4 章：數學轉換、特徵合成與「同市場群組式轉換」(Group-by Relative Strength)
  • 第 9 章：IQR 四分位距異常值偵測與範圍限制 (Outlier Capping / Winsorization)
  • 第 11 章：中位數與四分位距穩健縮放 (Robust Scaling，抗金融股災肥尾極端值)
純 Python 標準庫實作（零 numpy/pandas 依賴，100% 免疫 OpenBLAS 當機）。
================================================================================
"""
import math
from collections import Counter
from typing import Dict, List, Tuple, Any


def _percentile(sorted_vals: List[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    k = (n - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def compute_iqr_stats(values: List[float]) -> Dict[str, float]:
    """第 9 章 + 第 11 章：計算中位數、Q1、Q3、IQR 與上下異常值封頂界線。"""
    clean = sorted(float(v) for v in values if v is not None and not math.isnan(float(v)))
    if not clean:
        return {"median": 0.0, "q1": 0.0, "q3": 0.0, "iqr": 1.0, "lo": 0.0, "hi": 0.0}
    med = _percentile(clean, 0.50)
    q1 = _percentile(clean, 0.25)
    q3 = _percentile(clean, 0.75)
    iqr = max(q3 - q1, 1e-6)
    return {
        "median": round(med, 4),
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(iqr, 4),
        "lo": round(q1 - 1.5 * iqr, 4),
        "hi": round(q3 + 1.5 * iqr, 4),
    }


def iqr_cap(val: float, stats: Dict[str, float]) -> Tuple[float, bool]:
    """第 9 章：異常值範圍限制 (Capping)，回傳 (封頂後數值, 是否為異常值)。"""
    if val < stats["lo"]:
        return stats["lo"], True
    if val > stats["hi"]:
        return stats["hi"], True
    return val, False


def robust_scale(val: float, stats: Dict[str, float]) -> float:
    """第 11 章：Robust Scaling = (x - median) / IQR，對金融市場肥尾極端值免疫。"""
    return round((val - stats["median"]) / stats["iqr"], 4)


def compute_mutual_information(x_vals: List[float], y_vals: List[float], bins: int = 5) -> float:
    """
    第 3 章 + 第 8 章：以等頻分箱 (Quantile Discretization) 計算
    因子 X 與未來報酬 Y 之間的【交互資訊 Mutual Information (MI, 單位: nats)】。
    MI = 0 代表完全無預測力（雜訊因子）；MI 越高代表非線性預測能力越強！
    """
    pairs = [(float(x), float(y)) for x, y in zip(x_vals, y_vals) if x is not None and y is not None]
    n = len(pairs)
    if n < 10:
        return 0.0

    def discretize(arr: List[float], k: int) -> List[int]:
        s = sorted(arr)
        edges = [_percentile(s, i / k) for i in range(1, k)]
        out = []
        for v in arr:
            b = 0
            for e in edges:
                if v > e:
                    b += 1
            out.append(b)
        return out

    xs = discretize([p[0] for p in pairs], bins)
    ys = discretize([p[1] for p in pairs], bins)

    cx = Counter(xs)
    cy = Counter(ys)
    cxy = Counter(zip(xs, ys))

    mi = 0.0
    for (bx, by), cnt in cxy.items():
        pxy = cnt / n
        px = cx[bx] / n
        py = cy[by] / n
        if pxy > 0 and px > 0 and py > 0:
            mi += pxy * math.log(pxy / (px * py))
    return round(max(0.0, mi), 4)


def engineer_market_features(stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    對全站 260 檔標的執行《資料科學的特徵工程》四大實戰處理：
      1. 合成季線乖離 (bias_ma60) 與雙均線動能合成比 (trend_ratio)
      2. 群組式轉換 (台股/美股分組計算相對於同市場中位數的超額強度)
      3. IQR 異常值偵測與封頂 (防止極端妖股扭曲模型)
      4. Robust Scaling 綜合強弱排名，輸出今日前 5 強穩健領先股
    """
    enriched = []
    for s in stocks:
        sym = str(s.get("symbol", "")).strip()
        p = float(s.get("price") or 0.0)
        tech = s.get("technicals") or {}
        ma20 = float(tech.get("ma20") or s.get("ma20") or 0.0)
        ma60 = float(tech.get("ma60") or s.get("ma60") or 0.0)
        rsi = float(tech.get("rsi") or tech.get("rsi14") or 50.0)
        score = float(s.get("score") or 0.0)
        if not sym or p <= 0 or ma60 <= 0:
            continue
        mkt = "TW" if (".TW" in sym or ".TWO" in sym) else "US"
        bias60 = (p - ma60) / ma60 * 100.0
        bias20 = (p - ma20) / ma20 * 100.0 if ma20 > 0 else bias60
        enriched.append({
            "symbol": sym,
            "name": str(s.get("name", sym)),
            "market": mkt,
            "price": p,
            "ma60": ma60,
            "score": score,
            "rsi14": rsi,
            "bias_ma60": round(bias60, 2),
            "bias_ma20": round(bias20, 2),
        })

    # 第 4 章：按市場 (TW / US) 群組式計算 IQR 與 Robust Scaling
    outliers_flagged = []
    market_stats = {}
    for mkt in ("TW", "US"):
        grp = [x for x in enriched if x["market"] == mkt]
        if not grp:
            continue
        st_b60 = compute_iqr_stats([x["bias_ma60"] for x in grp])
        st_sc = compute_iqr_stats([x["score"] for x in grp])
        st_rsi = compute_iqr_stats([x["rsi14"] for x in grp])
        market_stats[mkt] = {
            "count": len(grp),
            "bias_ma60_median": st_b60["median"],
            "bias_ma60_iqr": st_b60["iqr"],
            "score_median": st_sc["median"],
        }
        for x in grp:
            cap_b60, is_out_b = iqr_cap(x["bias_ma60"], st_b60)
            cap_sc, is_out_s = iqr_cap(x["score"], st_sc)
            r_b60 = robust_scale(cap_b60, st_b60)
            r_sc = robust_scale(cap_sc, st_sc)
            r_rsi = robust_scale(x["rsi14"], st_rsi)
            # 穩健綜合相對強度 (排除極端過熱 RSI>75 與破季線標的)
            x["robust_bias60"] = r_b60
            x["robust_score"] = r_sc
            x["fe_composite_z"] = round(0.45 * r_sc + 0.35 * r_b60 + 0.20 * min(r_rsi, 1.5), 3)
            x["is_outlier"] = is_out_b or is_out_s
            if is_out_b:
                outliers_flagged.append({"symbol": x["symbol"], "market": mkt, "bias_ma60": x["bias_ma60"], "capped_to": round(cap_b60, 2)})

    # 篩選站穩季線、非過熱、Robust 綜合分數最強的各市場領先股
    top_leaders = {}
    for mkt in ("TW", "US"):
        ok = [x for x in enriched if x["market"] == mkt and x["price"] >= x["ma60"] and x["rsi14"] <= 72.0]
        ok.sort(key=lambda x: x["fe_composite_z"], reverse=True)
        top_leaders[mkt] = [
            {"symbol": x["symbol"], "name": x["name"], "price": x["price"], "bias_ma60": x["bias_ma60"], "fe_composite_z": x["fe_composite_z"]}
            for x in ok[:5]
        ]

    return {
        "source_course": "國立空中大學《資料科學的特徵工程》(Ch.3 MI / Ch.4 群組合成 / Ch.9 IQR 異常值 / Ch.11 Robust Scaling)",
        "total_processed": len(enriched),
        "outliers_capped_count": len(outliers_flagged),
        "sample_outliers": outliers_flagged[:5],
        "market_robust_stats": market_stats,
        "robust_leaders_above_ma60": top_leaders,
    }

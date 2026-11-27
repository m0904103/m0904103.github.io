# -*- coding: utf-8 -*-
"""
================================================================================
📐 Gen 31 顏春煌統計建模與防過擬合引擎 (Statistical Modeling & Overfit Guard — SM Engine)
================================================================================
學術核心來源：
  - 國立空中大學《數據分析建模的理論與實務》（顏春煌教授親授，454 講次）
  - 國立空中大學《統計學概論》（57 講次）
  - 國立空中大學《機器學習的原理與應用》（81 講次）
  - 國立空中大學《理財規劃與實務》（311 講次，退休風控與資產配置）

淬鍊四大純 Python 統計與機器學習風控護城河（零外部套件依賴）：
  1. Wilson 95% 勝率信賴區間 & 單尾 t-檢定 (A/B Test & Hypothesis Testing)：
     杜絕「小樣本全勝幻覺」，唯有在 p < 0.05 且信賴下界具正期望值時才認可進化參數。
  2. 混淆矩陣與 Precision / Recall / F1-Score (機器學習分類評估鐵律)：
     即時計算 Gen 31 買進訊號的精確率與 F1 分數，量化策略真實辨識力。
  3. 全市場橫斷面偏態 (Skewness) 與超額峰態 (Excess Kurtosis / 肥尾風險雷達)：
     掃描 260 檔台美股乖離率與動能分佈，抓出「左偏肥尾崩盤型態」（打破常態分佈幻覺）。
  4. 半凱利最佳倉位精算 (Half-Kelly Criterion, 受制於憲法層 A7 <= 25%)：
     結合勝率、賺賠比與總經壓力，算出「永不破產」的單檔最佳投資比例。
================================================================================
"""
import json
import math
from datetime import datetime
from typing import Any, Dict, List, Tuple


def wilson_confidence_interval(wins: int, total: int, z: float = 1.96) -> Dict[str, Any]:
    """
    《數據分析建模》Ch.5 A/B 測試與《統計學概論》母體比例信賴區間 (Wilson Score Interval)。
    在小樣本下遠比常態近似精準，能立刻揭穿「3 筆全勝 = 100% 勝率」的假象。
    """
    if total <= 0:
        return {"point_est_pct": 0.0, "ci95_low_pct": 0.0, "ci95_high_pct": 0.0, "sample_size": 0, "reliable": False}
    p = wins / total
    denom = 1.0 + (z * z) / total
    center = (p + (z * z) / (2.0 * total)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + (z * z) / (4.0 * total)) / total)) / denom
    low = max(0.0, center - half)
    high = min(1.0, center + half)
    return {
        "point_est_pct": round(p * 100, 1),
        "ci95_low_pct": round(low * 100, 1),
        "ci95_high_pct": round(high * 100, 1),
        "sample_size": total,
        "reliable": total >= 20 and low >= 0.45,
    }


def one_sample_t_test_positive(returns: List[float]) -> Dict[str, Any]:
    """
    《統計學概論》單樣本右尾檢定 H0: mu <= 0 vs H1: mu > 0。
    純 stdlib 透過誤差函數 math.erf 計算常態近似 p-value（檢驗策略期望值是否顯著為正）。
    """
    n = len(returns)
    if n < 5:
        return {"n": n, "mean_pct": 0.0, "t_stat": 0.0, "p_value_one_tailed": 1.0, "statistically_significant": False}
    mean = sum(returns) / n
    var = sum((x - mean) ** 2 for x in returns) / (n - 1)
    std = math.sqrt(var)
    if std <= 1e-9:
        return {"n": n, "mean_pct": round(mean, 2), "t_stat": 0.0, "p_value_one_tailed": 1.0, "statistically_significant": False}
    t_stat = mean / (std / math.sqrt(n))
    # 右尾 p-value 近似
    p_val = 0.5 * math.erfc(t_stat / math.sqrt(2.0))
    return {
        "n": n,
        "mean_pct": round(mean, 2),
        "std_pct": round(std, 2),
        "t_stat": round(t_stat, 3),
        "p_value_one_tailed": round(p_val, 4),
        "statistically_significant": (n >= 15 and p_val < 0.05 and mean > 0),
    }


def compute_confusion_metrics(eval_rows: List[Tuple[str, float]]) -> Dict[str, Any]:
    """
    《數據分析建模》Ch.6-7 & 《機器學習的原理與應用》分類器混淆矩陣評估：
      eval_rows: [(enforced_signal, realized_ret_5d), ...]
      Positive 預測 = BUY / STRONG_BUY；Positive 真實結果 = ret_5d > 0
    """
    tp = fp = fn = tn = 0
    for sig, ret in eval_rows:
        pred_pos = sig in ("BUY", "STRONG_BUY")
        actual_pos = ret > 0
        if pred_pos and actual_pos:
            tp += 1
        elif pred_pos and not actual_pos:
            fp += 1
        elif not pred_pos and actual_pos:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision_pct": round(precision * 100, 1),
        "recall_pct": round(recall * 100, 1),
        "f1_score": round(f1, 3),
    }


def compute_distribution_fat_tail_audit(stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    《統計學概論》偏態 (Skewness) 與超額峰態 (Excess Kurtosis) 橫斷面稽核：
    檢驗全市場 260 檔股票相對於季線 (MA60) 乖離率之分佈形狀。
      - Excess Kurtosis > 3.0：極端肥尾（黑天鵝風險高，常態分佈假設失效！）
      - Skewness < -0.5：顯著左偏（大盤多數個股正在破底拖累，空頭結構）
    """
    biases = []
    for s in stocks:
        p = s.get("price") or 0
        ma60 = s.get("ma60") or 0
        if p > 0 and ma60 > 0:
            biases.append((p - ma60) / ma60 * 100.0)
    n = len(biases)
    if n < 10:
        return {"sample_size": n, "status": "INSUFFICIENT_DATA"}

    mean = sum(biases) / n
    m2 = sum((x - mean) ** 2 for x in biases) / n
    std = math.sqrt(m2) if m2 > 0 else 1e-9
    m3 = sum((x - mean) ** 3 for x in biases) / n
    m4 = sum((x - mean) ** 4 for x in biases) / n

    skew = m3 / (std ** 3)
    excess_kurt = (m4 / (std ** 4)) - 3.0

    # 計算有多少比例的股票跌破季線 (MA60)
    below_ma60_pct = round(sum(1 for b in biases if b < 0) / n * 100, 1)

    if excess_kurt >= 3.0:
        tail_status = "FAT_TAIL_BLACK_SWAN_REGIME"
        note = f"超額峰態 {excess_kurt:.2f} (>=3.0 顯著肥尾)，市場存在極端暴漲暴跌尾端風險，禁止使用融資槓桿！"
    elif skew <= -0.5:
        tail_status = "LEFT_SKEWED_BEAR_BREADTH"
        note = f"市場分佈左偏 (Skew={skew:.2f})，且 {below_ma60_pct}% 個股跌破季線，屬於空頭擴散盤。"
    else:
        tail_status = "NORMAL_DISPERSION"
        note = f"市場橫斷面分佈正常 (Skew={skew:.2f}, Kurt={excess_kurt:.2f})，{below_ma60_pct}% 個股在季線下。"

    return {
        "sample_size": n,
        "mean_ma60_bias_pct": round(mean, 2),
        "std_ma60_bias_pct": round(std, 2),
        "skewness": round(skew, 3),
        "excess_kurtosis": round(excess_kurt, 3),
        "below_ma60_breadth_pct": below_ma60_pct,
        "tail_status": tail_status,
        "note": note,
    }


def compute_half_kelly_sizing(
    win_rate: float = 0.58,
    payoff_ratio: float = 1.8,
    macro_stress_score: float = 66.0,
    constitution_cap_pct: float = 25.0,
) -> Dict[str, Any]:
    """
    《理財規劃與實務》退休風控 × 凱利準則 (Half-Kelly Optimal Sizing)：
      f* = (p * b - q) / b，取半凱利 (0.5 * f*) 再依總經壓力動態折減，
      並嚴格鎖死於 Gen 31 憲法層 A7 上限 (單檔 <= 25%)。
    """
    q = 1.0 - win_rate
    full_kelly = (win_rate * payoff_ratio - q) / payoff_ratio if payoff_ratio > 0 else 0.0
    half_kelly_pct = max(0.0, full_kelly * 0.5 * 100.0)
    # 總經壓力折減係數：壓力 0 -> 1.0x；壓力 100 -> 0.35x
    stress_mult = max(0.35, 1.0 - (macro_stress_score / 100.0) * 0.65)
    adjusted_pct = min(constitution_cap_pct, round(half_kelly_pct * stress_mult, 1))
    return {
        "assumed_win_rate_pct": round(win_rate * 100, 1),
        "assumed_payoff_ratio": payoff_ratio,
        "full_kelly_pct": round(max(0.0, full_kelly * 100.0), 1),
        "half_kelly_pct": round(half_kelly_pct, 1),
        "macro_stress_multiplier": round(stress_mult, 2),
        "recommended_max_single_pos_pct": adjusted_pct,
        "constitution_a7_cap_pct": constitution_cap_pct,
        "note": f"依半凱利準則與當前總經壓力 ({macro_stress_score}/100) 折減後，單檔個股建議上限為總資金 {adjusted_pct}%（嚴守憲法 <= {constitution_cap_pct}%）。",
    }


def run_statistical_modeling_engine(
    stocks: List[Dict[str, Any]],
    eval_rows: List[Tuple[str, float]],
    macro_stress_score: float = 66.0,
) -> Dict[str, Any]:
    """執行 Gen 31 顏春煌統計建模與防過擬合引擎。"""
    buy_returns = [ret for sig, ret in eval_rows if sig in ("BUY", "STRONG_BUY")]
    wins = sum(1 for r in buy_returns if r > 0)
    wilson = wilson_confidence_interval(wins, len(buy_returns))
    t_test = one_sample_t_test_positive(buy_returns)
    conf_mat = compute_confusion_metrics(eval_rows)
    fat_tail = compute_distribution_fat_tail_audit(stocks)
    kelly = compute_half_kelly_sizing(
        win_rate=0.58,
        payoff_ratio=1.8,
        macro_stress_score=macro_stress_score,
        constitution_cap_pct=25.0,
    )

    return {
        "source_courses": [
            "國立空中大學《數據分析建模的理論與實務》（顏春煌教授）",
            "國立空中大學《統計學概論》",
            "國立空中大學《機器學習的原理與應用》",
            "國立空中大學《理財規劃與實務》",
        ],
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "oos_wilson_95ci": wilson,
        "oos_positive_expectancy_ttest": t_test,
        "classifier_confusion_matrix": conf_mat,
        "market_fat_tail_audit": fat_tail,
        "half_kelly_position_sizing": kelly,
    }


if __name__ == "__main__":
    import os, sys
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    scan_path = r"C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io\scan_results.json"
    stocks = json.load(open(scan_path, encoding="utf-8")).get("stocks", []) if os.path.exists(scan_path) else []
    print(json.dumps(run_statistical_modeling_engine(stocks, [], 66.0), ensure_ascii=False, indent=2))

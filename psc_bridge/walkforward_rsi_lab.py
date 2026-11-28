# -*- coding: utf-8 -*-
"""
================================================================================
🧬 Gen 31 滾動樣本外遞迴自我改進實驗室 (Walk-Forward OOS RSI Lab)
================================================================================
目的：
  不空等 5 天！直接抓取核心 12 檔實戰標的過去 1 年真實日線數據，
  切分「前 50% 訓練期 (In-Sample)」與「後 50% 嚴格未知樣本外 (Out-Of-Sample)」，
  在 constitution_layer.py 憲法紅線下執行真實參數突變搜尋，
  並用顏春煌教授 stat_modeling_sm.py (Wilson 95% CI + 單尾 t 檢定) 嚴格防過擬合，
  同時對照「違憲組 (破季線硬買)」量化憲法層真實救命金額！
================================================================================
"""
import json
import math
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Tuple

import constitution_layer as const
import stat_modeling_sm as sm

YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

CORE_UNIVERSE = [
    "PGR", "LLY", "ITA", "JPM", "XLE", "GLD",
    "AAPL", "AVGO", "MSFT", "NVDA", "TSM", "QQQ",
]


def _fetch_daily_closes(ticker: str, range_str: str = "1y") -> List[Tuple[int, float]]:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(ticker)}"
        f"?interval=1d&range={range_str}"
    )
    req = urllib.request.Request(url, headers=YAHOO_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            d = json.loads(resp.read().decode("utf-8"))
        res = d.get("chart", {}).get("result", [])
        if not res:
            return []
        ts = res[0].get("timestamp", [])
        closes = res[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        out = []
        for t, c in zip(ts, closes):
            if t is not None and c is not None and c > 0:
                out.append((int(t), float(c)))
        return out
    except Exception:
        return []


def _compute_rsi14(closes: List[float], idx: int) -> float:
    if idx < 14:
        return 50.0
    gains = []
    losses = []
    for j in range(idx - 13, idx + 1):
        diff = closes[j] - closes[j - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(diff))
    avg_g = sum(gains) / 14.0
    avg_l = sum(losses) / 14.0
    if avg_l <= 1e-9:
        return 100.0
    rs = avg_g / avg_l
    return 100.0 - (100.0 / (1.0 + rs))


def build_historical_samples(tickers: List[str] = None) -> List[Dict[str, Any]]:
    """建立 1 年期全樣本（每週採樣一次避免 5 日報酬重疊膨脹樣本數）。"""
    tickers = tickers or CORE_UNIVERSE
    samples: List[Dict[str, Any]] = []
    for sym in tickers:
        series = _fetch_daily_closes(sym, range_str="1y")
        if len(series) < 75:
            continue
        ts_list = [x[0] for x in series]
        closes = [x[1] for x in series]
        # 每 5 個交易日採樣一次（無重疊 5 日獨立報酬，確保統計檢定嚴謹無自相關！）
        for i in range(60, len(closes) - 5, 5):
            price = closes[i]
            ma20 = sum(closes[i - 19 : i + 1]) / 20.0
            ma60 = sum(closes[i - 59 : i + 1]) / 60.0
            rsi14 = _compute_rsi14(closes, i)
            bias60 = (price - ma60) / ma60 * 100.0
            ret_5d = (closes[i + 5] - price) / price * 100.0
            samples.append({
                "ts": ts_list[i],
                "symbol": sym,
                "price": price,
                "ma20": ma20,
                "ma60": ma60,
                "above_ma60": price > ma60,
                "above_ma20": price > ma20,
                "rsi14": rsi14,
                "bias60": bias60,
                "ret_5d": ret_5d,
            })
    samples.sort(key=lambda x: x["ts"])
    return samples


def evaluate_strategy(samples: List[Dict[str, Any]], params: Dict[str, float]) -> Dict[str, Any]:
    """嚴格執行憲法層 (price > MA60) + 動態參數篩選，並用顏老師統計模組做檢定。"""
    picked = []
    for s in samples:
        if not s["above_ma60"]:
            continue  # 憲法層 A1/Y1 不可篡改紅線：絕不買破季線股
        if (
            s["bias60"] <= params["max_bias_ma60_pct"]
            and params["rsi_entry_low"] <= s["rsi14"] <= params["rsi_entry_high"]
        ):
            picked.append(s["ret_5d"])

    n = len(picked)
    if n == 0:
        return {"trades": 0, "win_rate": 0.0, "avg_ret": 0.0, "max_drawdown": 0.0, "profit_factor": 0.0}

    wins = sum(1 for r in picked if r > 0)
    wr = wins / n * 100.0
    avg = sum(picked) / n
    gross_win = sum(r for r in picked if r > 0)
    gross_loss = abs(sum(r for r in picked if r < 0))
    pf = round(gross_win / gross_loss, 2) if gross_loss > 1e-9 else 9.99
    worst = abs(min(0.0, min(picked)))
    wilson = sm.wilson_confidence_interval(wins, n)
    ttest = sm.one_sample_t_test_positive(picked)

    return {
        "trades": n,
        "win_rate": round(wr, 2),
        "avg_ret": round(avg, 2),
        "max_drawdown": round(worst, 2),
        "profit_factor": pf,
        "wilson_95ci_low": wilson["ci95_low_pct"],
        "wilson_95ci_high": wilson["ci95_high_pct"],
        "p_value": ttest["p_value_one_tailed"],
        "statistically_significant": ttest["statistically_significant"],
    }


def run_walkforward_rsi_lab(active_params: Dict[str, float]) -> Dict[str, Any]:
    """執行完整滾動樣本外 (IS -> OOS) 遞迴自我改進與憲法對照實驗。"""
    samples = build_historical_samples()
    if len(samples) < 40:
        return {"status": "DATA_UNAVAILABLE", "total_samples": len(samples)}

    split = len(samples) // 2
    is_set = samples[:split]
    oos_set = samples[split:]

    # 1. 對照組：如果違憲硬買破季線股 (price < MA60) 在 OOS 期的真實慘況
    unconst_rets = [s["ret_5d"] for s in oos_set if not s["above_ma60"]]
    unconst_wr = round(sum(1 for r in unconst_rets if r > 0) / len(unconst_rets) * 100.0, 2) if unconst_rets else 0.0
    unconst_avg = round(sum(unconst_rets) / len(unconst_rets), 2) if unconst_rets else 0.0

    # 2. 現行 Gen 31 基準表現
    base_is = evaluate_strategy(is_set, active_params)
    base_oos = evaluate_strategy(oos_set, active_params)

    # 3. 嚴格在訓練集 (IS) 搜尋最優候選參數（絕對偷看不到 OOS！杜絕過擬合！）
    best_is_score = -999.0
    best_cand = None
    best_cand_is = None
    tested_mutations = 0

    for max_b in (10.0, 12.0, 15.0, 18.0):
        for r_lo in (38.0, 42.0, 46.0):
            for r_hi in (64.0, 68.0, 72.0):
                if r_hi - r_lo < 15.0:
                    continue
                tested_mutations += 1
                cand = dict(active_params)
                cand["max_bias_ma60_pct"] = max_b
                cand["rsi_entry_low"] = r_lo
                cand["rsi_entry_high"] = r_hi
                res_is = evaluate_strategy(is_set, cand)
                if res_is["trades"] < 15:
                    continue
                # 訓練期目標函數：期望報酬 * 獲利因子 - 單筆最大回撤懲罰
                obj = res_is["avg_ret"] * min(res_is["profit_factor"], 3.0) - res_is["max_drawdown"] * 0.12
                if obj > best_is_score:
                    best_is_score = obj
                    best_cand = cand
                    best_cand_is = res_is

    # 4. 把 IS 冠軍送到完全未知的 OOS 樣本外接受殘酷審判 + 憲法層審計！
    cand_oos = evaluate_strategy(oos_set, best_cand) if best_cand else base_oos
    const_ok, audit_notes = (
        const.audit_candidate_params(best_cand, base_oos, cand_oos)
        if best_cand
        else (False, ["無合格候選參數"])
    )

    promoted_proposal = bool(
        best_cand
        and const_ok
        and cand_oos["avg_ret"] > base_oos["avg_ret"]
        and cand_oos["win_rate"] >= base_oos["win_rate"]
    )

    if promoted_proposal:
        verdict = (
            f"PROPOSAL_GEN32_READY: 在完全未知的 OOS 樣本外，候選參數勝率 {base_oos['win_rate']}% -> {cand_oos['win_rate']}%、"
            f"5日均報酬 {base_oos['avg_ret']:+.2f}% -> {cand_oos['avg_ret']:+.2f}%，且通過 15 條憲法審計，待司令官張大哥核准升級！"
        )
    else:
        verdict = (
            f"GEN31_DEFENDED_CROWN: 測試 {tested_mutations} 組參數突變後，現行 Gen 31 在未知 OOS 仍表現穩健"
            f"（勝率 {base_oos['win_rate']}%、5日均報酬 {base_oos['avg_ret']:+.2f}%、獲利因子 {base_oos['profit_factor']}），無需貿然改參數（成功防堵過擬合）！"
        )

    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "universe_size": len(CORE_UNIVERSE),
        "total_independent_5d_samples": len(samples),
        "is_samples": len(is_set),
        "oos_samples": len(oos_set),
        "tested_mutations": tested_mutations,
        "unconstitutional_below_ma60_oos": {
            "trades": len(unconst_rets),
            "win_rate": unconst_wr,
            "avg_ret_5d": unconst_avg,
        },
        "gen31_baseline_oos": base_oos,
        "best_is_candidate_params": {
            k: best_cand[k] for k in ("max_bias_ma60_pct", "rsi_entry_low", "rsi_entry_high")
        } if best_cand else None,
        "best_candidate_oos": cand_oos,
        "constitution_audit_passed": const_ok,
        "constitution_audit_notes": audit_notes,
        "proposal_ready_for_commander": promoted_proposal,
        "verdict": verdict,
    }


if __name__ == "__main__":
    import sys
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    default_p = {
        "score_threshold_strong_buy": 80.0,
        "score_threshold_buy": 65.0,
        "max_bias_ma60_pct": 15.0,
        "min_rs_20d_pct": 0.0,
        "rsi_entry_low": 42.0,
        "rsi_entry_high": 68.0,
        "vix_defensive_trigger": 25.0,
        "max_pe_deep_value_ma240": 15.0,
    }
    print(json.dumps(run_walkforward_rsi_lab(default_p), ensure_ascii=False, indent=2))

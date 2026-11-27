# -*- coding: utf-8 -*-
"""
================================================================================
🛡️ 空大《衍生性金融商品》實戰避險防護罩 — Gen 31 Derivatives & Hedging Shield
================================================================================
直接蒸餾自 D:\02_Academic_Study\空大課程\衍生性金融商品 (27.5 萬字，聶建中/梁榮輝/謝明瑞)：
  • 第 09 講：股價指數期貨最小變異避險比率 (Optimal Hedge Ratio) ➔ 精算現貨持股需要幾張 00632R 避險
  • 第 20 講：隱含波動率 (VIX) 換算「每日 1 標準差預期震盪幅度」
  • 第 27 講：信用違約交換 (CDS) 利差換算「市場隱含 5 年累積違約機率」
  • 第 07 講/第 12 章：正2 / 反1 槓桿 ETF「年化波動率耗損 (Volatility Drag)」量化警報
  • 即時串接台灣期交所 (TAIFEX OpenAPI) 官方外資臺股期貨未平倉淨口數！
================================================================================
"""
import json
import math
import ssl
import urllib.request
from typing import Dict, Any


def fetch_taifex_foreign_txf() -> Dict[str, Any]:
    """即時抓取期交所官方 OpenAPI 外資臺股期貨 (TXF) 未平倉淨口數與契約金額。"""
    ctx = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(
            "https://openapi.taifex.com.tw/v1/MarketDataOfMajorInstitutionalTradersDetailsOfFuturesContractsBytheDate",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        data = json.loads(urllib.request.urlopen(req, context=ctx, timeout=10).read().decode("utf-8"))
        for r in data:
            if r.get("ContractCode") == "臺股期貨" and "外資" in str(r.get("Item", "")):
                net_oi = int(str(r.get("OpenInterest(Net)", "0")).replace(",", ""))
                long_oi = int(str(r.get("OpenInterest(Long)", "0")).replace(",", ""))
                short_oi = int(str(r.get("OpenInterest(Short)", "0")).replace(",", ""))
                val_yi = round(int(str(r.get("ContractValueofOpenInterest(Net)(Thousands)", "0")).replace(",", "")) / 1e5, 1)
                if net_oi <= -60000:
                    alert = "EXTREME_RED (史詩級空單警戒，嚴禁滿倉追高)"
                elif net_oi <= -30000:
                    alert = "RED (阿村伯 -3萬口紅線警戒，提高現金比)"
                elif net_oi <= -15000:
                    alert = "YELLOW (溫和避險空單)"
                else:
                    alert = "GREEN (外資期貨偏多/中性)"
                return {
                    "date": r.get("Date"),
                    "foreign_txf_net_oi": net_oi,
                    "long_oi": long_oi,
                    "short_oi": short_oi,
                    "net_value_yi_twd": val_yi,
                    "shield_status": alert,
                }
    except Exception as e:
        return {"error": str(e), "shield_status": "UNAVAILABLE"}
    return {"shield_status": "NOT_FOUND"}


def cds_implied_5y_default_prob(spread_bps: float, recovery_rate: float = 0.40) -> float:
    """
    第 27 講：信用違約交換 (CDS) 利差 (bps) 換算市場隱含 5 年累積違約機率 (%)。
    公式：hazard_rate λ ≈ (spread / 10000) / (1 - R) ; PD_5Y = 1 - exp(-5 * λ)
    """
    lam = (spread_bps / 10000.0) / max(1.0 - recovery_rate, 0.05)
    pd_5y = (1.0 - math.exp(-5.0 * lam)) * 100.0
    return round(pd_5y, 1)


def compute_optimal_inverse_etf_hedge(
    portfolio_value_twd: float,
    portfolio_beta: float = 1.0,
    inverse_etf_price: float = 11.25,
    hedge_ratio_target: float = 0.50,
) -> Dict[str, Any]:
    """
    第 09 講：最小變異避險比率實戰應用。
    計算台股現貨部位 (如 00406A) 若想做 hedge_ratio_target (如 50% 半避險)，
    精確需要買進幾張 00632R (每張 1,000 股)。
    """
    notional_to_hedge = portfolio_value_twd * portfolio_beta * hedge_ratio_target
    lot_value = inverse_etf_price * 1000.0
    exact_lots = notional_to_hedge / lot_value if lot_value > 0 else 0.0
    return {
        "portfolio_value_twd": round(portfolio_value_twd, 0),
        "hedge_ratio_target_pct": round(hedge_ratio_target * 100, 1),
        "recommended_00632R_lots": round(exact_lots, 2),
        "recommended_lots_rounded": max(1, round(exact_lots)),
    }


def compute_leveraged_etf_vol_drag(annual_vol_pct: float, leverage: float = 2.0) -> float:
    """
    第 07 講 + 第 12 章：計算正2 / 反1 槓桿 ETF 在高波動盤整下的「年化複利波動率耗損 (%)」。
    公式：Drag ≈ 0.5 * L * (L - 1) * σ^2 (對正2 L=2 為 σ^2；對反1 L=-1 同樣為 σ^2！)
    """
    sigma = annual_vol_pct / 100.0
    drag = 0.5 * abs(leverage) * abs(leverage - 1.0) * (sigma ** 2) * 100.0
    return round(drag, 2)


def run_derivatives_shield(live_vix: float = 25.0, user_tw_equity_twd: float = 46340.0) -> Dict[str, Any]:
    """整合期交所外資空單 + VIX 預期日震幅 + 槓桿扣血率 + AI 巨頭 CDS 監控。"""
    txf = fetch_taifex_foreign_txf()
    daily_expected_move_pct = round(live_vix / math.sqrt(252.0), 2)
    drag_2x = compute_leveraged_etf_vol_drag(live_vix, leverage=2.0)
    drag_inv1 = compute_leveraged_etf_vol_drag(live_vix, leverage=-1.0)
    hedge_calc = compute_optimal_inverse_etf_hedge(user_tw_equity_twd, portfolio_beta=1.1, inverse_etf_price=11.25, hedge_ratio_target=0.50)

    return {
        "source_course": "國立空中大學《衍生性金融商品》(第09講避險比率/第20講VIX波動/第27講CDS/槓桿耗損)",
        "taifex_foreign_txf": txf,
        "vix_daily_1sigma_move_pct": daily_expected_move_pct,
        "leveraged_etf_annual_vol_drag_pct": {
            "2x_long_etf_00637L": drag_2x,
            "1x_inverse_etf_00632R": drag_inv1,
            "warning": f"在 VIX={live_vix} 環境下，盤整一年單純波動耗損即吃掉 -{drag_2x}%，嚴禁長期死抱正2/反1！",
        },
        "user_00406A_50pct_hedge_plan": hedge_calc,
        "cds_reference_5y_pd_pct": {
            "CoreWeave_1314bps": cds_implied_5y_default_prob(1314),
            "SoftBank_536bps": cds_implied_5y_default_prob(536),
            "Oracle_356bps": cds_implied_5y_default_prob(356),
            "BigTech4_115bps": cds_implied_5y_default_prob(115.6),
        },
    }

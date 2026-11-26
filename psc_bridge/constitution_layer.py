# -*- coding: utf-8 -*-
"""
================================================================================
🏛️ 憲法層 (Immutable Constitution Layer) — 阿村伯 × 顏春煌教授 Gen 31
================================================================================
最高原則：
  1. 本檔案為「不可篡改憲法層」，AI 遞迴自我改進引擎 (RSI) 僅有【唯讀審計權】，
     絕對無權修改任何一條憲法紅線。
  2. 任何訊號、任何選股組合、任何 AI 自動產出的下一代參數提案，皆必須先通過
     本憲法層審計；違憲者一律強制否決 (VETO)。
================================================================================
"""
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Any

# ==============================================================================
# 🔒 憲法鐵律常數 (IMMUTABLE CONSTITUTIONAL ARTICLES)
# ==============================================================================
CONSTITUTION_VERSION = "Gen31-Constitution-v1.1"

ARTICLES = {
    # --- 阿村伯 (蔡鎮村博士) 風控與心法憲法 ---
    "A1_FORBID_DAY_TRADING": True,                  # 永遠禁止台股/美股當沖
    "A2_MIN_CASH_RATIO_BEAR": 0.70,                 # 空頭/高恐慌期 (VIX>=25 或破季線) 最低現金比 70%
    "A3_MIN_CASH_RATIO_NORMAL": 0.30,               # 正常多頭期最低現金比 30% (永遠保有選擇權 Optionality)
    "A4_FORBID_MARGIN_LEVERAGE": True,              # 永遠禁止融資與無上限槓桿
    "A5_REQUIRE_DAY2_CONFIRMATION": True,           # 大跌後必等連續 2 日不破低 (Day-2) 才准擴大進攻
    "A6_FORBID_AVERAGE_DOWN_52W_LOW": True,         # 絕不在創 52 週新低當日逆勢攤平
    "A7_SINGLE_STOCK_MAX_WEIGHT_PCT": 25.0,         # 單檔部位上限 25% (高價股改零股，絕不一把梭哈)

    # --- 顏春煌教授 技術紀律與統計檢驗憲法 ---
    "Y1_REQUIRE_ABOVE_MA60_FOR_BUY": True,          # 股價未站上 60 日季線，禁止發 Strong Buy / 追多
    "Y2_MAX_SINGLE_STOP_LOSS_PCT": 8.0,             # 單筆最大容忍虧損上限 8% (嚴禁凹單至 -20%)
    "Y3_MAX_PE_DEFENSIVE": 35.0,                    # 防禦型標的 PE > 35x 強制亮估值紅燈，改推 SGOV
    "Y4_MIN_OOS_TRADES_FOR_PROMOTION": 15,          # AI 進化提案必須累積至少 15 筆樣本外驗證才准提報
    "Y5_MIN_OOS_WINRATE_GAIN_PCT": 2.0,             # 候選演算法 OOS 勝率須優於舊版 >= 2.0% (防過度擬合)
    "Y6_MAX_OOS_DRAWDOWN_TOLERANCE_PCT": 1.0,       # 候選演算法最大回撤不得比舊版惡化超過 1.0%
    "Y7_REQUIRE_HUMAN_COMMANDER_APPROVAL": True,    # AI 永遠無權自動覆寫正式版，必須由張大哥核准
    "Y8_FORBID_CHASE_LIMIT_UP_BELOW_MA60": True,    # 破季線反彈當日急漲 >=8.5% 漲停第一根，嚴禁追高
}

# 允許 AI 遞迴進化層調整的參數安全邊界 (Bounded RSI Parameter Space)
EVOLUTION_BOUNDS = {
    "score_threshold_strong_buy": (72.0, 90.0),     # Strong Buy 分數門檻安全區間
    "score_threshold_buy": (58.0, 75.0),            # Buy 分數門檻安全區間
    "max_bias_ma60_pct": (8.0, 22.0),               # 季線最大正乖離追高上限 (%)
    "min_rs_20d_pct": (-2.0, 8.0),                  # 20 日相對大盤強弱下限 (%)
    "rsi_entry_low": (35.0, 52.0),                  # 進場 RSI 下界
    "rsi_entry_high": (62.0, 74.0),                 # 進場 RSI 上界 (防過熱)
    "vix_defensive_trigger": (22.0, 28.0),          # 觸發全面防禦模式之 VIX 門檻
    "max_pe_deep_value_ma240": (10.0, 18.0),        # 阿村伯第12柱：年線錯殺正規軍 PE 黃金折價上限
}


def get_constitution_hash() -> str:
    """計算憲法條文與參數邊界的 SHA-256 指紋，確保未被任何程式篡改。"""
    payload = json.dumps({"version": CONSTITUTION_VERSION, "articles": ARTICLES, "bounds": EVOLUTION_BOUNDS}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass
class ConstitutionalVerdict:
    passed: bool
    original_signal: str
    enforced_signal: str
    veto_reasons: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def audit_signal(stock: Dict[str, Any], market_vix: float = 20.0) -> ConstitutionalVerdict:
    """
    以雙師憲法層審計單檔股票的 AI 訊號。
    凡違反季線防守、極端弱勢或高估值紅隊閥者，強制降級/否決 (VETO)。
    """
    orig_sig = str(stock.get("signal", "Hold"))
    price = float(stock.get("price") or 0.0)
    tech = stock.get("technicals") or {}
    fund = stock.get("fundamentals") or {}

    ma60 = float(tech.get("ma60") or stock.get("ma60") or 0.0)
    rsi = float(tech.get("rsi") or tech.get("rsi14") or 50.0)
    pe = fund.get("pe") or stock.get("pe")
    symbol = str(stock.get("symbol", "")).upper()

    vetoes: List[str] = []
    enforced = orig_sig

    is_buy_like = orig_sig.lower() in ("strong buy", "buy", "強力買進", "買進")

    # 顏老師憲法 Y1：未站上 60 日季線，絕不准 Strong Buy / Buy
    if is_buy_like and ARTICLES["Y1_REQUIRE_ABOVE_MA60_FOR_BUY"]:
        if price > 0 and ma60 > 0 and price < ma60:
            vetoes.append(f"[Y1-顏老師季線憲法] 現價 {price:.2f} < 季線 {ma60:.2f}，強制駁回買進")
            enforced = "Hold (憲法駁回:破季線)"

    # 顏老師憲法 Y3：防禦股高估值紅隊閥 (PE > 35)
    defensive_set = {"WMT", "COST", "KO", "PG", "PEP", "CL", "JNJ"}
    if is_buy_like and symbol in defensive_set and pe is not None:
        try:
            pe_val = float(pe)
            if pe_val > ARTICLES["Y3_MAX_PE_DEFENSIVE"]:
                vetoes.append(f"[Y3-紅隊估值憲法] 防禦股 {symbol} PE={pe_val:.1f}x > {ARTICLES['Y3_MAX_PE_DEFENSIVE']}x，勿追高改停泊 SGOV")
                enforced = "Hold (憲法駁回:高估值)"
        except (ValueError, TypeError):
            pass

    # 阿村伯憲法 A2：恐慌期 VIX >= 25 強制收緊進攻訊號
    if is_buy_like and market_vix >= 25.0 and orig_sig.lower() in ("strong buy", "強力買進"):
        if symbol not in {"SGOV", "SHV", "XLP", "SO", "DUK", "PGR"}:
            vetoes.append(f"[A2-阿村伯恐慌憲法] VIX={market_vix:.1f} >= 25，強制降級防禦，守住 70% 現金")
            if enforced == orig_sig:
                enforced = "Watch (恐慌降級)"

    # 極端過熱保護 (RSI > 78 不追高)
    if is_buy_like and rsi > 78.0 and symbol not in {"SGOV", "SHV"}:
        vetoes.append(f"[Y1-防追高保護] RSI={rsi:.1f} > 78 過熱，待拉回再看")
        if enforced == orig_sig:
            enforced = "Hold (過熱待拉回)"

    # 顏老師 × 阿村伯第 12 柱憲法 Y8：破季線當日急漲 >= 8.5% 漲停第一根，嚴禁追高
    chg_pct = float(stock.get("change_pct") or 0.0)
    if is_buy_like and ARTICLES["Y8_FORBID_CHASE_LIMIT_UP_BELOW_MA60"]:
        if price > 0 and ma60 > 0 and price < ma60 and chg_pct >= 8.5:
            vetoes.append(f"[Y8-禁追漲停第一根] 破季線反彈單日急漲 +{chg_pct:.1f}%，等拉回 Day-2/KD金叉再零股接")
            enforced = "Hold (憲法駁回:禁追破季線漲停)"

    return ConstitutionalVerdict(
        passed=(len(vetoes) == 0),
        original_signal=orig_sig,
        enforced_signal=enforced,
        veto_reasons=vetoes,
    )


def audit_candidate_params(
    candidate_params: Dict[str, float],
    baseline_oos: Dict[str, float],
    candidate_oos: Dict[str, float],
) -> Tuple[bool, List[str]]:
    """
    審計 AI 遞迴進化引擎產出的候選參數，防止違憲與過度擬合 (Overfitting)。
    回傳 (是否允許進入司令官核准佇列, 審計理由清單)。
    """
    reasons: List[str] = []

    # 1. 檢查所有參數是否嚴格落在憲法安全邊界內
    for key, val in candidate_params.items():
        if key not in EVOLUTION_BOUNDS:
            reasons.append(f"[越權違憲] AI 試圖修改未授權參數: {key}")
            continue
        lo, hi = EVOLUTION_BOUNDS[key]
        if not (lo <= float(val) <= hi):
            reasons.append(f"[越界違憲] 參數 {key}={val} 超出憲法安全邊界 [{lo}, {hi}]")

    # 2. 檢查樣本外 (OOS) 交易樣本數是否充足
    oos_n = int(candidate_oos.get("trades", 0))
    if oos_n < ARTICLES["Y4_MIN_OOS_TRADES_FOR_PROMOTION"]:
        reasons.append(
            f"[Y4-樣本不足] OOS 驗證筆數僅 {oos_n} 筆，未達憲法門檻 {ARTICLES['Y4_MIN_OOS_TRADES_FOR_PROMOTION']} 筆（累積中，暫不升級）"
        )

    # 3. 檢查 OOS 勝率是否顯著打贏舊版
    base_wr = float(baseline_oos.get("win_rate", 0.0))
    cand_wr = float(candidate_oos.get("win_rate", 0.0))
    if oos_n >= ARTICLES["Y4_MIN_OOS_TRADES_FOR_PROMOTION"]:
        if (cand_wr - base_wr) < ARTICLES["Y5_MIN_OOS_WINRATE_GAIN_PCT"]:
            reasons.append(
                f"[Y5-未達顯著進步] 候選 OOS 勝率 {cand_wr:.1f}% vs 舊版 {base_wr:.1f}%，進步未達 +{ARTICLES['Y5_MIN_OOS_WINRATE_GAIN_PCT']}%"
            )

    # 4. 檢查最大回撤是否惡化
    base_dd = float(baseline_oos.get("max_drawdown", 0.0))
    cand_dd = float(candidate_oos.get("max_drawdown", 0.0))
    if (cand_dd - base_dd) > ARTICLES["Y6_MAX_OOS_DRAWDOWN_TOLERANCE_PCT"]:
        reasons.append(
            f"[Y6-回撤惡化否決] 候選最大回撤 {cand_dd:.1f}% 較舊版 {base_dd:.1f}% 惡化超過 {ARTICLES['Y6_MAX_OOS_DRAWDOWN_TOLERANCE_PCT']}%"
        )

    return (len(reasons) == 0), reasons


if __name__ == "__main__":
    print(f"🏛️ {CONSTITUTION_VERSION} | SHA-256 Seal: {get_constitution_hash()}")
    print(f"   • 不可篡改條文數: {len(ARTICLES)} 條")
    print(f"   • 授權 AI 進化參數: {list(EVOLUTION_BOUNDS.keys())}")

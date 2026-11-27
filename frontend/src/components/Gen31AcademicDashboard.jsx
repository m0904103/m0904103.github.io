import React, { useState, useEffect } from 'react';
import {
  ShieldAlert, Globe, Landmark, Calculator,
  Cpu, FileSearch, Lock, Eye, Layers, CheckCircle2, AlertTriangle
} from 'lucide-react';

const STATUS_URLS = [
  './gen31_rsi_status.json',
  '/q_quant_888/gen31_rsi_status.json',
];

const REGIME_ZH = {
  RED_GEOPOLITICAL_SHOCK: { label: '🔴 高度警戒：地緣衝突與總經震盪', tone: 'red' },
  ORANGE_STAGFLATION_RISK: { label: '🟠 審慎防守：停滯性通膨與關稅摩擦', tone: 'amber' },
  YELLOW_TARIFF_FRICTION: { label: '🟡 震盪觀察：政策不確定與輪動整理', tone: 'yellow' },
  GREEN_EXPANSION: { label: '🟢 順勢偏多：總經平穩可挑多頭共振', tone: 'emerald' },
};

const AI_PHASE_ZH = {
  DELEVERAGING_SHAKEOUT: '殺估值去槓桿期（嚴禁抄底高本益比 AI）',
  EUPHORIA_OVERHEATED: '資本狂熱過熱期（留意高檔分批停利）',
  HEALTHY_DIGESTION: '健康輪動消化期（聚焦高自由現金流龍頭）',
};

const CURVE_ZH = {
  BEAR_STEEPENING_FISCAL_STRESS: '熊市陡峭化（長端利率飆高懲罰赤字）',
  INVERTED_RECESSION_WARNING: '殖利率倒掛警戒（衰退倒數）',
  FLAT_UNINVERSION_DANGER_ZONE: '解除倒掛平坦區（主跌段高發窗口）',
  NORMAL_HEALTHY_SLOPE: '正常健康正斜率',
};

function MeterBar({ label, value, max = 100, statusText, tone = 'amber' }) {
  const pct = Math.max(0, Math.min(100, (Number(value) || 0) / max * 100));
  const barCls =
    tone === 'red'
      ? 'bg-gradient-to-r from-red-600 to-rose-400'
      : tone === 'emerald'
        ? 'bg-gradient-to-r from-emerald-600 to-teal-400'
        : 'bg-gradient-to-r from-amber-600 to-yellow-400';

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between gap-2 text-xs sm:text-sm">
        <span className="font-bold text-gray-200">{label}</span>
        <span className="font-mono font-black text-white">
          {value ?? '--'} <span className="text-xs font-normal text-gray-400">({statusText})</span>
        </span>
      </div>
      <div
        className="h-2.5 w-full rounded-full bg-white/10 overflow-hidden"
        role="progressbar"
        aria-label={label}
        aria-valuenow={Math.round(pct)}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className={`h-full rounded-full transition-all duration-500 ${barCls}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function Gen31AcademicDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(false);
  // 行動優先與降噪設計：支援「精簡看盤（一秒結論）」與「專業全覽（六大引擎）」雙模式，並記憶偏好
  const [viewMode, setViewMode] = useState(() => {
    try {
      const saved = localStorage.getItem('gen31_dashboard_mode');
      if (saved === 'simple' || saved === 'pro') return saved;
    } catch (_) {
      // ignore storage errors
    }
    return typeof window !== 'undefined' && window.innerWidth < 768 ? 'simple' : 'pro';
  });

  const handleModeChange = (mode) => {
    setViewMode(mode);
    try {
      localStorage.setItem('gen31_dashboard_mode', mode);
    } catch (_) {
      // ignore
    }
  };

  useEffect(() => {
    let active = true;
    const loadStatus = async () => {
      const ts = Date.now();
      for (const base of STATUS_URLS) {
        try {
          const res = await fetch(`${base}?t=${ts}`, { cache: 'no-store' });
          if (res.ok) {
            const json = await res.json();
            if (active && json && json.constitution) {
              setData(json);
              setError(false);
              return;
            }
          }
        } catch (_) {
          // try next path
        }
      }
      if (active) setError(true);
    };
    loadStatus();
    const timer = setInterval(loadStatus, 60000);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  if (error || !data) {
    return null;
  }

  const c = data.constitution || {};
  const snap = data.snapshot || {};
  const ds = data.derivatives_shield || {};
  const mg = data.macro_geopolitics || {};
  const ml = data.monetary_liquidity || {};
  const sm = data.statistical_modeling || {};
  const fa = data.financial_audit || {};
  const fe = data.feature_engineering || {};

  const txOi = ds.taifex_foreign_txf || {};
  const vixDaily1Sigma = typeof ds.vix_daily_1sigma_move_pct === 'number' ? ds.vix_daily_1sigma_move_pct : '--';
  const rawDrag = ds.leveraged_etf_annual_vol_drag_pct;
  const levAnnualDrag =
    typeof rawDrag === 'number'
      ? rawDrag
      : (rawDrag && typeof rawDrag === 'object' ? rawDrag['1x_inverse_etf_00632R'] ?? rawDrag['2x_long_etf_00637L'] ?? '--' : '--');
  const hedge = ds.user_00406A_50pct_hedge_plan || {};
  const cdsEntries = Object.entries(ds.cds_reference_5y_pd_pct || {});

  const mgTel = mg.live_telemetry || {};
  const ppp = mg.taiwan_ppp_fx_gauge || {};
  const aiCycle = mg.ai_bubble_cycle || {};
  const scAudit = mg.supply_chain_tariff_audit || {};

  const yc = ml.yield_curve_clock || {};
  const fisher = ml.fisher_real_rate || {};
  const credit = ml.credit_transmission || {};

  const fatTail = sm.market_fat_tail_audit || {};
  const kelly = sm.half_kelly_position_sizing || {};

  const feStats = fe.market_robust_stats || {};
  const feLeadersTw = fe.robust_leaders_above_ma60?.TW || [];
  const feLeadersUs = fe.robust_leaders_above_ma60?.US || [];
  const faMines = fa.financial_landmines || [];

  const oiContracts = typeof txOi.foreign_txf_net_oi === 'number' ? txOi.foreign_txf_net_oi : null;
  const oiAlert = oiContracts !== null && oiContracts <= -50000;
  const regimeInfo = REGIME_ZH[mg.macro_regime] || { label: '🟡 總經即時監控中', tone: 'amber' };
  const buyPassed = snap.constitution_buy_passed ?? 0;

  const macroTone = (mg.macro_stress_score ?? 50) >= 75 ? 'red' : (mg.macro_stress_score ?? 50) >= 55 ? 'amber' : 'emerald';
  const liqTone = (ml.liquidity_stress_score ?? 50) >= 70 ? 'red' : (ml.liquidity_stress_score ?? 50) >= 45 ? 'amber' : 'emerald';
  const breadthTone = (fatTail.below_ma60_breadth_pct ?? 50) >= 70 ? 'red' : (fatTail.below_ma60_breadth_pct ?? 50) >= 50 ? 'amber' : 'emerald';

  return (
    <section
      aria-labelledby="gen31-warroom-heading"
      className="rounded-2xl border border-amber-500/35 bg-[#12161D] shadow-2xl overflow-hidden"
    >
      {/* 頂部導覽與模式切換列（符合 WCAG >= 44px 行動觸控熱區與清晰字級） */}
      <div className="px-4 md:px-6 py-4 bg-gradient-to-r from-amber-950/35 via-[#181E29] to-slate-900 border-b border-white/10 flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 id="gen31-warroom-heading" className="text-base md:text-lg font-black text-white tracking-wide">
              🏛️ Gen {data.active_gen || 31} 空大六大聖殿戰情室
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-500/15 text-blue-200 border border-blue-400/30">
              即時更新 {data.updated_at}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-gray-300">
            {regimeInfo.label}
          </p>
        </div>

        {/* 雙模式切換按鈕組：min-h-[44px] 確保手機單手好按不誤觸 */}
        <div className="flex items-center gap-2 self-start lg:self-auto" role="group" aria-label="戰情室顯示模式">
          <button
            type="button"
            onClick={() => handleModeChange('simple')}
            aria-pressed={viewMode === 'simple'}
            className={`min-h-[44px] px-4 py-2 rounded-xl text-xs sm:text-sm font-black flex items-center gap-1.5 transition-all border focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-400 ${
              viewMode === 'simple'
                ? 'bg-amber-500 text-slate-950 border-amber-300 shadow-lg'
                : 'bg-white/5 text-gray-200 border-white/15 hover:bg-white/10'
            }`}
          >
            <Eye size={16} aria-hidden="true" />
            <span>精簡秒看</span>
          </button>
          <button
            type="button"
            onClick={() => handleModeChange('pro')}
            aria-pressed={viewMode === 'pro'}
            className={`min-h-[44px] px-4 py-2 rounded-xl text-xs sm:text-sm font-black flex items-center gap-1.5 transition-all border focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-400 ${
              viewMode === 'pro'
                ? 'bg-amber-500 text-slate-950 border-amber-300 shadow-lg'
                : 'bg-white/5 text-gray-200 border-white/15 hover:bg-white/10'
            }`}
          >
            <Layers size={16} aria-hidden="true" />
            <span>六引擎全覽</span>
          </button>
        </div>
      </div>

      {/* 【第一層：一秒總司令結論條】先給白話結論，減少認知負荷（Edward Tufte 資料墨水比原則） */}
      <div className="p-4 md:p-5 space-y-4 bg-[#10141B]">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="rounded-xl p-3.5 bg-[#171C26] border border-white/10">
            <div className="text-xs text-gray-300 font-bold">建議現金底線</div>
            <div className="text-2xl md:text-3xl font-mono font-black text-emerald-300 mt-1">
              ≥ {mg.recommended_cash_floor_pct ?? 55}%
            </div>
            <div className="text-xs text-gray-400 mt-1">保留現金就是最強防禦</div>
          </div>

          <div className="rounded-xl p-3.5 bg-[#171C26] border border-white/10">
            <div className="text-xs text-gray-300 font-bold">單檔上限（半凱利）</div>
            <div className="text-2xl md:text-3xl font-mono font-black text-cyan-300 mt-1">
              {kelly.recommended_max_single_pos_pct ?? '--'}%
            </div>
            <div className="text-xs text-gray-400 mt-1">憲法封頂 ≤ {kelly.constitution_a7_cap_pct ?? 25}%</div>
          </div>

          <div className="rounded-xl p-3.5 bg-[#171C26] border border-white/10">
            <div className="text-xs text-gray-300 font-bold">外資台指期未平倉</div>
            <div className={`text-xl md:text-2xl font-mono font-black mt-1 ${oiAlert ? 'text-rose-400' : 'text-emerald-300'}`}>
              {oiContracts !== null ? `${oiContracts.toLocaleString()} 口` : '--'}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {oiAlert ? '🔴 史詩級空單警戒' : '🟢 籌碼風險可控'}
            </div>
          </div>

          <div className="rounded-xl p-3.5 bg-[#171C26] border border-white/10">
            <div className="text-xs text-gray-300 font-bold">今日憲法放行買進</div>
            <div className={`text-2xl md:text-3xl font-mono font-black mt-1 ${buyPassed === 0 ? 'text-amber-300' : 'text-emerald-300'}`}>
              {buyPassed} 檔
            </div>
            <div className="text-xs text-gray-400 mt-1">
              {buyPassed === 0 ? '寧可空手絕不亂接刀' : '已通過15條憲法審計'}
            </div>
          </div>
        </div>

        {/* 視覺化三大壓力儀表條（取代密密麻麻文字，一眼看懂市場體溫） */}
        <div className="rounded-xl p-4 bg-[#151A23] border border-white/10 grid grid-cols-1 md:grid-cols-3 gap-4">
          <MeterBar
            label="🌍 總經與關稅壓力"
            value={mg.macro_stress_score}
            statusText={macroTone === 'red' ? '高壓紅燈' : macroTone === 'amber' ? '警戒橘燈' : '平穩綠燈'}
            tone={macroTone}
          />
          <MeterBar
            label="🏦 聯準會流動性緊縮"
            value={ml.liquidity_stress_score}
            statusText={liqTone === 'red' ? '極度抽水' : liqTone === 'amber' ? '偏緊逆風' : '寬鬆順風'}
            tone={liqTone}
          />
          <MeterBar
            label="📉 260檔跌破季線比例"
            value={fatTail.below_ma60_breadth_pct}
            statusText={`${fatTail.below_ma60_breadth_pct ?? '--'}% 走弱`}
            tone={breadthTone}
          />
        </div>

        {/* 一句話白話行動指令 */}
        <div className="rounded-xl px-4 py-3 bg-amber-500/10 border border-amber-400/30 flex items-start gap-2.5 text-xs sm:text-sm text-amber-100 leading-relaxed">
          <AlertTriangle size={18} className="text-amber-300 shrink-0 mt-0.5" aria-hidden="true" />
          <div>
            <strong className="text-amber-300">今日白話操作指令：</strong>
            {mg.action_note || '維持高現金防禦水位，嚴守季線與紀律停損。'}
          </div>
        </div>

        {/* 【第二層：專業六引擎全覽】僅在「六引擎全覽」模式展開 */}
        {viewMode === 'pro' && (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 pt-1">
            {/* ③ 衍生性避險防護罩 */}
            <article className="rounded-xl border border-rose-500/25 bg-[#151A23] p-4 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <h3 className="flex items-center gap-2 text-rose-300 font-black text-sm">
                  <ShieldAlert size={16} aria-hidden="true" />
                  <span>③ 衍生性避險防護罩</span>
                </h3>
                <span className="text-xs font-mono text-gray-300">VIX {data.live_vix ?? '--'}</span>
              </div>
              <div className="grid grid-cols-2 gap-2.5 text-xs sm:text-sm">
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">單日 1σ 正常振幅</div>
                  <div className="font-mono font-black text-amber-300 text-base mt-0.5">±{vixDaily1Sigma}%</div>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">反1/正2年複利耗損</div>
                  <div className="font-mono font-black text-rose-300 text-base mt-0.5">-{levAnnualDrag}%</div>
                </div>
              </div>
              <p className="text-xs text-gray-200 leading-relaxed">
                🛡️ 7 張 00406A 半避險配對：<strong className="text-amber-300">{hedge.recommended_lots_rounded ?? 2} 張 00632R</strong>（精算 {hedge.recommended_00632R_lots ?? 2.27} 張），反 1 限短線避險、絕不長抱。
              </p>
              {cdsEntries.length > 0 && (
                <details className="rounded-lg bg-black/25 border border-white/10 px-3 py-2 text-xs">
                  <summary className="cursor-pointer font-bold text-gray-200 select-none">
                    展開華爾街 5 年違約率 (CDS) 雷達
                  </summary>
                  <ul className="mt-2 space-y-1 text-gray-300 font-mono">
                    {cdsEntries.map(([k, v]) => (
                      <li key={k} className="flex justify-between">
                        <span>{k.replace('_', ' ')}</span>
                        <strong className="text-rose-300">{v}%</strong>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </article>

            {/* ④ 全球經貿與關稅地緣 */}
            <article className="rounded-xl border border-amber-500/25 bg-[#151A23] p-4 space-y-3">
              <h3 className="flex items-center gap-2 text-amber-300 font-black text-sm">
                <Globe size={16} aria-hidden="true" />
                <span>④ 全球經貿與關稅雷達</span>
              </h3>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-gray-400">WTI 原油</div>
                  <div className="font-mono font-black text-orange-300 text-sm mt-0.5">${mgTel.wti_oil?.price ?? '--'}</div>
                  <div className="text-gray-400">{mgTel.wti_oil?.chg_1d_pct >= 0 ? '+' : ''}{mgTel.wti_oil?.chg_1d_pct ?? 0}%</div>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-gray-400">黃金期貨</div>
                  <div className="font-mono font-black text-yellow-300 text-sm mt-0.5">${mgTel.gold?.price ?? '--'}</div>
                  <div className="text-gray-400">{mgTel.gold?.chg_1d_pct >= 0 ? '+' : ''}{mgTel.gold?.chg_1d_pct ?? 0}%</div>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-gray-400">台幣匯率</div>
                  <div className="font-mono font-black text-cyan-300 text-sm mt-0.5">{ppp.usdtwd ?? '--'}</div>
                  <div className="text-gray-400">低估 {ppp.twd_ppp_undervaluation_pct ?? '--'}%</div>
                </div>
              </div>
              <p className="text-xs text-gray-200 leading-relaxed">
                🤖 AI 週期：<strong className="text-amber-300">{AI_PHASE_ZH[aiCycle.phase] || aiCycle.phase || '--'}</strong>（那指近20日落後標普 {aiCycle.ndx_vs_spx_spread_20d_pct ?? '--'}%）
              </p>
              <div className="flex items-center justify-between text-xs text-gray-300 pt-1 border-t border-white/10">
                <span>⚠️ 高關稅曝險：<strong className="text-rose-300">{scAudit.high_tariff_exposure_count ?? 0} 檔</strong></span>
                <span>🛡️ 關稅絕緣盾：<strong className="text-emerald-300">{scAudit.tariff_insulated_count ?? 0} 檔</strong></span>
              </div>
            </article>

            {/* ⑤ 貨幣銀行與流動性 */}
            <article className="rounded-xl border border-purple-500/25 bg-[#151A23] p-4 space-y-3">
              <h3 className="flex items-center gap-2 text-purple-300 font-black text-sm">
                <Landmark size={16} aria-hidden="true" />
                <span>⑤ 貨幣銀行與流動性時鐘</span>
              </h3>
              <div className="grid grid-cols-2 gap-2.5 text-xs sm:text-sm">
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">美債 10 年殖利率</div>
                  <div className="font-mono font-black text-rose-300 text-base mt-0.5">{yc.us10y_pct ?? '--'}%</div>
                  <div className="text-xs text-gray-400">10Y-3M: {yc.spread_10y_3m_bps > 0 ? '+' : ''}{yc.spread_10y_3m_bps ?? '--'} bps</div>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">費雪實質利率</div>
                  <div className="font-mono font-black text-purple-300 text-base mt-0.5">{fisher.fisher_real_rate_pct ?? '--'}%</div>
                  <div className="text-xs text-gray-400">合理 PE 天花板 ~{fisher.implied_fair_pe_ceiling ?? '--'}x</div>
                </div>
              </div>
              <p className="text-xs text-gray-200 leading-relaxed">
                📈 曲線狀態：<strong className="text-purple-200">{CURVE_ZH[yc.curve_state] || yc.curve_state || '--'}</strong>；高收債落後美債 {credit.hyg_vs_ief_spread_20d_pct ?? '--'}%、區域銀行 {credit.kre_vs_xlf_20d_pct ?? '--'}%。
              </p>
            </article>

            {/* ⑥ 顏春煌統計建模與半凱利 */}
            <article className="rounded-xl border border-cyan-500/25 bg-[#151A23] p-4 space-y-3">
              <h3 className="flex items-center gap-2 text-cyan-300 font-black text-sm">
                <Calculator size={16} aria-hidden="true" />
                <span>⑥ 顏春煌統計與防過擬合</span>
              </h3>
              <div className="grid grid-cols-2 gap-2.5 text-xs sm:text-sm">
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">全市場平均季線乖離</div>
                  <div className="font-mono font-black text-rose-300 text-base mt-0.5">{fatTail.mean_ma60_bias_pct ?? '--'}%</div>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">半凱利建議單檔上限</div>
                  <div className="font-mono font-black text-emerald-300 text-base mt-0.5">{kelly.recommended_max_single_pos_pct ?? '--'}%</div>
                </div>
              </div>
              <p className="text-xs text-gray-300 leading-relaxed">
                內建 Wilson 95% 勝率信賴區間、單尾 t-檢定與混淆矩陣 F1-Score，防止 AI 被小樣本運氣欺騙。
              </p>
            </article>

            {/* ① 特徵工程去偏強勢 */}
            <article className="rounded-xl border border-blue-500/25 bg-[#151A23] p-4 space-y-3">
              <h3 className="flex items-center gap-2 text-blue-300 font-black text-sm">
                <Cpu size={16} aria-hidden="true" />
                <span>① 特徵工程去偏強勢股</span>
              </h3>
              <div className="grid grid-cols-2 gap-2.5 text-xs sm:text-sm">
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">台股中位數乖離</div>
                  <div className="font-mono font-black text-blue-300 text-base mt-0.5">{feStats.TW?.bias_ma60_median ?? '--'}%</div>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">美股中位數乖離</div>
                  <div className="font-mono font-black text-blue-300 text-base mt-0.5">{feStats.US?.bias_ma60_median ?? '--'}%</div>
                </div>
              </div>
              <div className="text-xs text-gray-200 space-y-1">
                <div>
                  🇹🇼 逆勢強勢：<strong className="text-emerald-300 font-mono">{feLeadersTw.slice(0, 3).map((x) => `${x.symbol.replace(/\.TWO?$/, '')}${x.name}`).join(' · ') || '--'}</strong>
                </div>
                <div>
                  🇺🇸 逆勢強勢：<strong className="text-cyan-300 font-mono">{feLeadersUs.slice(0, 3).map((x) => x.symbol).join(' · ') || '--'}</strong>
                </div>
              </div>
            </article>

            {/* ② 財報杜邦掃雷 */}
            <article className="rounded-xl border border-emerald-500/25 bg-[#151A23] p-4 space-y-3">
              <h3 className="flex items-center gap-2 text-emerald-300 font-black text-sm">
                <FileSearch size={16} aria-hidden="true" />
                <span>② 財報杜邦排雷引擎</span>
              </h3>
              <div className="grid grid-cols-2 gap-2.5 text-xs sm:text-sm">
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">財報 A+ 績優股</div>
                  <div className="font-mono font-black text-emerald-300 text-base mt-0.5">{fa.grade_a_plus_count ?? '--'} 檔</div>
                </div>
                <div className="p-2.5 rounded-lg bg-white/[0.04]">
                  <div className="text-xs text-gray-400">紅旗地雷警示</div>
                  <div className="font-mono font-black text-rose-300 text-base mt-0.5">{fa.red_flag_count ?? '--'} 檔</div>
                </div>
              </div>
              <p className="text-xs text-rose-200 leading-relaxed">
                🚨 頭號避開地雷：<strong className="font-mono">{faMines.slice(0, 3).map((x) => `${x.symbol.replace(/\.TWO?$/, '')} ${x.name}`).join(' / ') || '無'}</strong>
              </p>
            </article>
          </div>
        )}

        {/* 次要技術資訊收合於原生 <details>（符合降噪原則，不佔主視覺空間） */}
        <details className="rounded-xl bg-white/[0.03] border border-white/10 px-4 py-2.5 text-xs text-gray-300">
          <summary className="cursor-pointer font-bold text-gray-200 flex items-center gap-2 select-none">
            <Lock size={14} className="text-emerald-400 shrink-0" aria-hidden="true" />
            <span>查看 Gen {data.active_gen || 31} 憲法指紋鎖與系統稽核紀錄（15 條不可篡改規則）</span>
          </summary>
          <div className="mt-2.5 pt-2.5 border-t border-white/10 flex flex-wrap gap-x-6 gap-y-1.5 font-mono text-gray-300">
            <span><CheckCircle2 size={12} className="inline text-emerald-400 mr-1" aria-hidden="true" />SHA-256 指紋鎖: {c.sha256_seal || 'SEALED'}</span>
            <span>今日掃描: {snap.total_snapshotted ?? 260} 檔</span>
            <span>憲法攔截違憲買進: {snap.constitution_vetoed ?? 0} 檔</span>
            <span>累計追蹤訊號: {data.evaluation?.total_ledger_rows ?? 0} 筆</span>
          </div>
        </details>
      </div>
    </section>
  );
}

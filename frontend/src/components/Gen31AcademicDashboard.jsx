import React, { useState, useEffect } from 'react';
import {
  ShieldAlert, ShieldCheck, Globe, Landmark, Calculator,
  Cpu, FileSearch, ChevronDown, ChevronUp, Lock, Activity, AlertTriangle
} from 'lucide-react';

const STATUS_URLS = [
  './gen31_rsi_status.json',
  '/q_quant_888/gen31_rsi_status.json',
];

export default function Gen31AcademicDashboard() {
  const [data, setData] = useState(null);
  const [expanded, setExpanded] = useState(true);
  const [error, setError] = useState(false);

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

  const regimeColor =
    mg.macro_stress_score >= 75
      ? 'border-red-500/60 bg-red-950/30 text-red-300'
      : mg.macro_stress_score >= 55
        ? 'border-amber-500/60 bg-amber-950/30 text-amber-300'
        : 'border-emerald-500/50 bg-emerald-950/30 text-emerald-300';

  const liqColor =
    ml.liquidity_stress_score >= 70
      ? 'text-red-400'
      : ml.liquidity_stress_score >= 45
        ? 'text-amber-400'
        : 'text-emerald-400';

  const oiContracts = txOi.foreign_txf_net_oi ?? null;
  const oiAlert = oiContracts !== null && oiContracts <= -50000;

  return (
    <section className="rounded-2xl border border-amber-500/35 bg-gradient-to-br from-[#12161D] via-[#151A23] to-[#11151C] shadow-2xl overflow-hidden">
      {/* Header Bar */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="px-4 md:px-6 py-3.5 bg-gradient-to-r from-amber-950/40 via-[#181E29] to-indigo-950/40 border-b border-white/10 flex flex-wrap items-center justify-between gap-3 cursor-pointer hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-amber-500/15 border border-amber-400/30 text-amber-300">
            <Lock size={18} />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-sm md:text-base font-black text-white tracking-wide">
                🏛️ Gen {data.active_gen || 31} 空大六大聖殿即時戰情室
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                SHA-256: {c.sha256_seal || 'SEALED'} ({c.articles_count || 15}條憲法)
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/15 text-blue-300 border border-blue-500/30">
                LIVE 更新: {data.updated_at}
              </span>
            </div>
            <p className="text-[11px] text-gray-400 mt-0.5">
              特徵工程 × 財務掃雷 × 衍生性避險 × 全球經貿 × 貨幣銀行 × 顏春煌統計建模 — 六引擎即時聯防
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`px-2.5 py-1 rounded-lg text-xs font-black border ${regimeColor}`}>
            總經壓力 {mg.macro_stress_score ?? '--'}/100 · 建議現金 ≥ {mg.recommended_cash_floor_pct ?? 55}%
          </span>
          <button
            type="button"
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-300"
            aria-label="展開或收合六大引擎"
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="p-4 md:p-5 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {/* Pillar 3: Derivatives Shield */}
          <div className="rounded-xl border border-red-500/25 bg-[#0F1319]/90 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-red-300 font-black text-xs">
                <ShieldAlert size={15} />
                <span>③ 衍生性避險防護罩（期權×CDS）</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-black ${oiAlert ? 'bg-red-500/25 text-red-300' : 'bg-emerald-500/20 text-emerald-300'}`}>
                {(txOi.shield_status || 'LIVE').split(' ')[0]}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">外資台指期未平倉</div>
                <div className="font-mono font-black text-red-400 text-sm">
                  {oiContracts !== null ? `${oiContracts.toLocaleString()} 口` : '--'}
                </div>
                <div className="text-[10px] text-gray-500">
                  淨空 {txOi.net_value_yi_twd ?? '--'} 億
                </div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">VIX 單日 1σ 振幅</div>
                <div className="font-mono font-black text-amber-300 text-sm">
                  ±{vixDaily1Sigma ?? '--'}%
                </div>
                <div className="text-[10px] text-gray-500">
                  反1/正2年耗損 -{levAnnualDrag}%
                </div>
              </div>
            </div>
            <div className="text-[11px] text-gray-300 bg-white/[0.02] p-2 rounded-lg border border-white/5">
              🛡️ 最小變異半避險：7張 00406A ➔ 配對 <span className="text-amber-300 font-black">{hedge.recommended_lots_rounded ?? 2} 張 00632R</span>（精算 {hedge.recommended_00632R_lots ?? 2.27}）
            </div>
            {cdsEntries.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-0.5">
                {cdsEntries.map(([k, v]) => (
                  <span
                    key={k}
                    className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-red-500/10 text-red-300 border border-red-500/20"
                  >
                    {k.split('_')[0]} 5Y違約 {v}%
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Pillar 4: Macro & Geopolitics */}
          <div className="rounded-xl border border-amber-500/25 bg-[#0F1319]/90 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-amber-300 font-black text-xs">
                <Globe size={15} />
                <span>④ 全球經貿與關稅地緣雷達</span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-black bg-amber-500/20 text-amber-300">
                {mg.macro_regime || 'SCANNING'}
              </span>
            </div>
            <div className="grid grid-cols-3 gap-1.5 text-xs">
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">WTI 原油</div>
                <div className="font-mono font-black text-orange-300">${mgTel.wti_oil?.price ?? '--'}</div>
                <div className="text-[10px] text-gray-500">{mgTel.wti_oil?.chg_1d_pct >= 0 ? '+' : ''}{mgTel.wti_oil?.chg_1d_pct ?? 0}%</div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">黃金期貨</div>
                <div className="font-mono font-black text-yellow-300">${mgTel.gold?.price ?? '--'}</div>
                <div className="text-[10px] text-gray-500">{mgTel.gold?.chg_1d_pct >= 0 ? '+' : ''}{mgTel.gold?.chg_1d_pct ?? 0}%</div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">USD/TWD</div>
                <div className="font-mono font-black text-cyan-300">{ppp.usdtwd ?? '--'}</div>
                <div className="text-[10px] text-gray-500">PPP低估 {ppp.twd_ppp_undervaluation_pct ?? '--'}%</div>
              </div>
            </div>
            <div className="text-[11px] text-gray-300 bg-white/[0.02] p-2 rounded-lg border border-white/5">
              🤖 AI 週期：<span className="text-amber-300 font-bold">{aiCycle.phase || '--'}</span>（NDX vs SPX 20日差 <span className="font-mono text-red-400">{aiCycle.ndx_vs_spx_spread_20d_pct ?? '--'}%</span>）
            </div>
            <div className="text-[10px] text-gray-400 flex items-center justify-between">
              <span>⚠️ 高關稅曝險: <strong className="text-red-400">{scAudit.high_tariff_exposure_count ?? 0} 檔</strong></span>
              <span>🛡️ 關稅絕緣盾: <strong className="text-emerald-400">{scAudit.tariff_insulated_count ?? 0} 檔</strong></span>
            </div>
          </div>

          {/* Pillar 5: Monetary & Liquidity */}
          <div className="rounded-xl border border-purple-500/25 bg-[#0F1319]/90 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-purple-300 font-black text-xs">
                <Landmark size={15} />
                <span>⑤ 貨幣銀行與流動性時鐘</span>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-black bg-purple-500/15 ${liqColor}`}>
                壓力 {ml.liquidity_stress_score ?? '--'}/100
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">美債 10Y / 10Y-3M</div>
                <div className="font-mono font-black text-red-400 text-sm">{yc.us10y_pct ?? '--'}%</div>
                <div className="text-[10px] text-gray-500">利差 {yc.spread_10y_3m_bps > 0 ? '+' : ''}{yc.spread_10y_3m_bps ?? '--'} bps</div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">費雪實質利率 → 合理PE</div>
                <div className="font-mono font-black text-purple-300 text-sm">{fisher.fisher_real_rate_pct ?? '--'}%</div>
                <div className="text-[10px] text-gray-500">市場 PE 上限 ~{fisher.implied_fair_pe_ceiling ?? '--'}x</div>
              </div>
            </div>
            <div className="text-[11px] text-gray-300 bg-white/[0.02] p-2 rounded-lg border border-white/5">
              💳 信用傳導：高收債 HYG 落後美債 <span className="font-mono text-red-400">{credit.hyg_vs_ief_spread_20d_pct ?? '--'}%</span>｜區域銀行 KRE <span className="font-mono text-red-400">{credit.kre_vs_xlf_20d_pct ?? '--'}%</span>
            </div>
          </div>

          {/* Pillar 6: Stat Modeling & Half-Kelly */}
          <div className="rounded-xl border border-cyan-500/25 bg-[#0F1319]/90 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-300 font-black text-xs">
                <Calculator size={15} />
                <span>⑥ 顏春煌統計建模與半凱利</span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-black bg-cyan-500/15 text-cyan-300">
                防過擬合三鎖
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">260檔跌破季線比例</div>
                <div className="font-mono font-black text-red-400 text-sm">{fatTail.below_ma60_breadth_pct ?? '--'}%</div>
                <div className="text-[10px] text-gray-500">平均乖離 {fatTail.mean_ma60_bias_pct ?? '--'}%</div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">動態半凱利單檔上限</div>
                <div className="font-mono font-black text-emerald-400 text-sm">{kelly.recommended_max_single_pos_pct ?? '--'}%</div>
                <div className="text-[10px] text-gray-500">憲法封頂 ≤ {kelly.constitution_a7_cap_pct ?? 25}%</div>
              </div>
            </div>
            <div className="text-[11px] text-gray-400">
              Wilson 95% 信賴區間 ＋ 單尾 t-檢定 ＋ 混淆矩陣已就緒，杜絕小樣本過擬合幻覺。
            </div>
          </div>

          {/* Pillar 1: Feature Engineering */}
          <div className="rounded-xl border border-blue-500/25 bg-[#0F1319]/90 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-blue-300 font-black text-xs">
                <Cpu size={15} />
                <span>① 特徵工程去偏強勢篩選</span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-black bg-blue-500/15 text-blue-300">
                IQR + Robust Z
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">台股中位數乖離</div>
                <div className="font-mono font-black text-blue-300">
                  {feStats.TW?.bias_ma60_median ?? '--'}%
                </div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">美股中位數乖離</div>
                <div className="font-mono font-black text-blue-300">
                  {feStats.US?.bias_ma60_median ?? '--'}%
                </div>
              </div>
            </div>
            <div className="text-[11px] text-gray-300 space-y-0.5">
              <div>
                🇹🇼 去偏強勢：
                <span className="text-emerald-300 font-mono font-bold ml-1">
                  {feLeadersTw.slice(0, 3).map((x) => `${x.symbol.replace(/\.TWO?$/, '')}${x.name}`).join(' · ') || '--'}
                </span>
              </div>
              <div>
                🇺🇸 去偏強勢：
                <span className="text-cyan-300 font-mono font-bold ml-1">
                  {feLeadersUs.slice(0, 3).map((x) => x.symbol).join(' · ') || '--'}
                </span>
              </div>
            </div>
          </div>

          {/* Pillar 2: Financial Audit */}
          <div className="rounded-xl border border-emerald-500/25 bg-[#0F1319]/90 p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-300 font-black text-xs">
                <FileSearch size={15} />
                <span>② 財報杜邦掃雷引擎</span>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-black bg-emerald-500/15 text-emerald-300">
                三率三升＋業外稽核
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">財報 A+ 績優股</div>
                <div className="font-mono font-black text-emerald-400 text-sm">{fa.grade_a_plus_count ?? '--'} 檔</div>
              </div>
              <div className="p-2 rounded-lg bg-white/[0.03] border border-white/5">
                <div className="text-[10px] text-gray-400">紅旗地雷警示</div>
                <div className="font-mono font-black text-red-400 text-sm">{fa.red_flag_count ?? '--'} 檔</div>
              </div>
            </div>
            <div className="text-[11px] text-red-300/90">
              🚨 頭號排雷：
              <span className="font-mono font-bold ml-1">
                {faMines.slice(0, 3).map((x) => `${x.symbol.replace(/\.TWO?$/, '')} ${x.name}`).join(' / ') || '無'}
              </span>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

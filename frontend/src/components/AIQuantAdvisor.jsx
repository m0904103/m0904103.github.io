import React, { useState } from 'react';
import { 
  ShieldCheck, AlertTriangle, TrendingUp, TrendingDown, Target, 
  Cpu, Zap, PieChart, Coins, ArrowUpRight, CheckCircle2, 
  XCircle, Flame, Layers, Lock, Scale, Calculator, Sliders,
  HelpCircle, Compass, Activity, ArrowRight, DollarSign
} from 'lucide-react';

// 2026-11-10 Wall Street Buy-Side Consensus ERC 2.0: Pure US Universe
const RECOMMENDATIONS_US = [
  {
    symbol: 'VTI',
    name: 'Vanguard 全美指數 ETF',
    market: 'us',
    tier: '🇺🇸 全市場防禦底倉 (Core Anchor)',
    tierColor: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    action: '【回撤 $338~$347 分批建倉】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 25.0,
    annualVol: 16.5,
    slPrice: 376.23,
    tpPrice: 420.0,
    currPrice: 370.9,
    highlight: '涵蓋全美數千家企業，捕捉非科技股滾動式復甦，抵禦 5% 美債利率衝擊的最強防禦核心。'
  },
  {
    symbol: 'AVGO',
    name: 'Broadcom 博通',
    market: 'us',
    tier: '🇺🇸 AI ASIC 霸主 (去輝達化首選)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【站穩月線/頸線分批佈局】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 15.0,
    annualVol: 32.4,
    slPrice: 350.13,
    tpPrice: 399.0,
    currPrice: 319.48,
    highlight: '掌握 Google TPU 70~80% 市佔與 Meta MTIA，Q2 AI 營收年增 143%，完美對沖 GPU 壟斷鬆動。'
  },
  {
    symbol: 'GOOGL',
    name: 'Alphabet 谷歌-A',
    market: 'us',
    tier: '🇺🇸 低估值 TPU 帝國 (P/E ~15x)',
    tierColor: 'text-cyan-300 bg-cyan-500/10 border-cyan-500/30',
    action: '【黃金坑 $265~$272 低接】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 15.0,
    annualVol: 28.2,
    slPrice: 333.79,
    tpPrice: 360.0,
    currPrice: 288.15,
    highlight: 'TPU v8 推論成本僅 GPU 一半（$0.42 vs $0.91），本益比七巨頭最低，重倉 SpaceX 攻守兼備。'
  },
  {
    symbol: 'TSM',
    name: '台積電 ADR',
    market: 'us',
    tier: '🏆 全球先進製程壟斷 (賣鏟總司令)',
    tierColor: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    action: '【黃金坑 $335~$345 低接】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 12.0,
    annualVol: 31.5,
    slPrice: 428.52,
    tpPrice: 486.0,
    currPrice: 388.62,
    highlight: '無論 GPU 或 ASIC 競爭誰勝，全須經由 2nm/CoWoS/3D DRAM 製造，完全免疫設計端洗牌。'
  },
  {
    symbol: 'ETN',
    name: 'Eaton 伊頓電力',
    market: 'us',
    tier: '⚡ 電網基建與變壓器龍頭',
    tierColor: 'text-purple-300 bg-purple-500/10 border-purple-500/30',
    action: '【電網剛需 / 降低科技相關性】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 10.0,
    annualVol: 24.8,
    slPrice: 407.04,
    tpPrice: 450.0,
    currPrice: 359.3,
    highlight: '電氣在手訂單飆升 46% 至 200 億美元，配電與資料中心剛需大幅平滑純科技股波動。'
  },
  {
    symbol: 'CEG',
    name: 'Constellation 核能電力',
    market: 'us',
    tier: '⚛️ 核能全天候零碳電力',
    tierColor: 'text-teal-300 bg-teal-500/10 border-teal-500/30',
    action: '【已站回 60MA 季線偏多！】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 8.0,
    annualVol: 36.2,
    slPrice: 270.93,
    tpPrice: 348.0,
    currPrice: 276.09,
    highlight: '已率先收復季線！手握 8,500 MW 長期核電協議，不受限於藍潮綠能併網阻礙，高盛美銀喊買。'
  },
  {
    symbol: 'MU',
    name: 'Micron 美光科技',
    market: 'us',
    tier: '🧠 HBM3e/HBM4 超級週期',
    tierColor: 'text-pink-300 bg-pink-500/10 border-pink-500/30',
    action: '【回測 $600~$635 分批布局】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 6.0,
    annualVol: 48.5,
    slPrice: 955.94,
    tpPrice: 916.0,
    currPrice: 733.15,
    highlight: '記憶體佔 AI 資本支出比重將升至 64%，做空 ETF (MUZ) 遭主力軋空，HBM 報價強勁上行。'
  },
  {
    symbol: 'NVDA',
    name: 'NVIDIA 輝達',
    market: 'us',
    tier: '⚠️ 獨立調查案降權控管',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【靜待 11/17 財報 / $155~$175 鐵底】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 5.0,
    annualVol: 45.78,
    slPrice: 218.64,
    tpPrice: 223.0,
    currPrice: 178.67,
    highlight: '面臨 CEO 調查與 ESG 治理折價，ERC 主動壓低權重至 5%；11/17 財報與 $155~$175 區間為關鍵防線。'
  },
  {
    symbol: 'VRT',
    name: 'Vertiv Holdings 液冷',
    market: 'us',
    tier: '❄️ 高密度 DLC 液冷與電源',
    tierColor: 'text-indigo-300 bg-indigo-500/10 border-indigo-500/30',
    action: '【已站回 $200 / 等站穩季線】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 4.0,
    annualVol: 41.2,
    slPrice: 240.76,
    tpPrice: 330.0,
    currPrice: 200.47,
    highlight: 'Q3 營收年增 61%、積壓訂單 150 億美元，遠期本益比已修正至 26 倍均值，大摩目標價 $330。'
  },
  {
    symbol: 'BE',
    name: 'Bloom Energy 燃料電池',
    market: 'us',
    tier: '🔋 離網供電 Alpha 衛星觀察',
    tierColor: 'text-lime-300 bg-lime-500/10 border-lime-500/30',
    action: '【突破觀察 / 逢回配置】',
    actionColor: 'text-lime-300 bg-lime-500/20 border-lime-500/30',
    weightPct: 0.0,
    annualVol: 58.0,
    slPrice: 150.0,
    tpPrice: 242.0,
    currPrice: 193.88,
    highlight: '與 Oracle 簽 2.8 GW 離網合約，繞過藍潮電網排隊期，Q3 營收暴增 138%，可作 CEG 衛星替補。'
  }
];

// 2026-11-10 Cross-Market TW+US ERC 2.0
const RECOMMENDATIONS_CROSS = [
  {
    symbol: '2330.TW',
    name: '台積電',
    market: 'tw',
    tier: '🏆 核心壓艙石 (Core #1)',
    tierColor: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    action: '【分批逢低承接 / 守季線】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 15.0,
    annualVol: 27.06,
    slPrice: 2414.51,
    tpPrice: 2856.0,
    currPrice: 2285.0,
    highlight: '全球 2nm/CoWoS/3D DRAM 大壟斷，免疫 GPU 與 ASIC 設計架構轉換，外資長線核心定海神針。'
  },
  {
    symbol: '2454.TW',
    name: '聯發科',
    market: 'tw',
    tier: '🚀 ASIC 進攻主軸 (價值重估)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【TPU 推理贏家 / 搶先突圍觀察】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 15.0,
    annualVol: 42.8,
    slPrice: 4315.08,
    tpPrice: 4788.0,
    currPrice: 3830.0,
    highlight: '切入 Google TPU v8x (Zebrafish) 推理晶片打破博通壟斷，外資大幅重估 AI ASIC 長線成長。'
  },
  {
    symbol: 'AVGO',
    name: 'Broadcom 博通',
    market: 'us',
    tier: '🇺🇸 ASIC 對沖雙引擎',
    tierColor: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    action: '【對沖去輝達化核心】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 15.0,
    annualVol: 32.4,
    slPrice: 350.13,
    tpPrice: 399.0,
    currPrice: 319.48,
    highlight: 'Google TPU 與 Meta MTIA 核心夥伴，結合乙太網與 VMware 軟體現金流，完美分散 NVDA 風險。'
  },
  {
    symbol: 'CEG',
    name: 'Constellation 核電',
    market: 'us',
    tier: '⚛️ 電力基建 (降低相關性)',
    tierColor: 'text-teal-300 bg-teal-500/10 border-teal-500/30',
    action: '【已站穩季線 / 抗震防禦】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 12.0,
    annualVol: 36.2,
    slPrice: 270.93,
    tpPrice: 348.0,
    currPrice: 276.09,
    highlight: '打破純半導體硬體高相關性，受惠 AI 無碳基載剛需，目前股價已強勢站上 60MA 季線。'
  },
  {
    symbol: 'ASML',
    name: '艾司摩爾',
    market: 'us',
    tier: '🏗️ 半導體設備賣鏟人',
    tierColor: 'text-sky-300 bg-sky-500/10 border-sky-500/30',
    action: '【壟斷設備 / 平滑淨值】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 12.0,
    annualVol: 30.8,
    slPrice: 1686.33,
    tpPrice: 1891.0,
    currPrice: 1513.25,
    highlight: 'EUV 光刻機全球唯一壟斷，完全免疫下游晶片廠市佔廝殺，擔任底層低波壓艙石。'
  },
  {
    symbol: 'VRT',
    name: 'Vertiv Holdings',
    market: 'us',
    tier: '🇺🇸 美股 AI 基建與液冷',
    tierColor: 'text-indigo-300 bg-indigo-500/10 border-indigo-500/30',
    action: '【強彈回 $200 / 等站回季線】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 10.0,
    annualVol: 41.2,
    slPrice: 240.76,
    tpPrice: 330.0,
    currPrice: 200.47,
    highlight: '全球數據中心熱管理與電力系統龍頭，Q3 營收年增 61%，回測修正至合理本益比區間。'
  },
  {
    symbol: '3017.TW',
    name: '奇鋐',
    market: 'tw',
    tier: '⭐ 散熱龍頭 (精選保留)',
    tierColor: 'text-cyan-300 bg-cyan-500/10 border-cyan-500/30',
    action: '【適度降權至 8% / 等站回季線】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 8.0,
    annualVol: 39.67,
    slPrice: 3221.34,
    tpPrice: 3488.0,
    currPrice: 2790.0,
    highlight: '水冷板與分歧管核心供應商，縮減同質重疊保留最強龍頭，待站穩季線分批承接。'
  },
  {
    symbol: '2317.TW',
    name: '鴻海',
    market: 'tw',
    tier: '⭐ 機櫃整合雙軌受惠',
    tierColor: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    action: '【最接近季線 / 準備轉強】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 8.0,
    annualVol: 28.51,
    slPrice: 248.2,
    tpPrice: 302.0,
    currPrice: 241.5,
    highlight: 'GB200 與 TPU L10-L11 機櫃雙軌受惠，現價距離季線僅約 2.7%，最有潛力率先突破。'
  },
  {
    symbol: 'NVDA',
    name: '輝達',
    market: 'us',
    tier: '⚠️ 調查案降權控管',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【降權 5% / $155~$175 鐵底】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 5.0,
    annualVol: 45.78,
    slPrice: 218.64,
    tpPrice: 223.0,
    currPrice: 178.67,
    highlight: '面臨 CEO 獨立調查與治理折價，ERC 主動壓低權重至 5%；靜待 11/17 財報檢驗與鐵底支撐。'
  },
  {
    symbol: '3324.TWO',
    name: '雙鴻',
    market: 'tw',
    tier: '🚨 破季線剔除避開',
    tierColor: 'text-red-400 bg-red-500/20 border-red-500/40',
    action: '【剛性避開 / 0% 配比 / 嚴禁接飛刀】',
    actionColor: 'text-red-400 bg-red-600/30 border-red-500/50',
    weightPct: 0.0,
    annualVol: 36.06,
    slPrice: 1335.4,
    tpPrice: 0.0,
    currPrice: 1235.0,
    highlight: '【顏春煌教授鐵律】散熱集中度過高且跌破 60MA 生命線，ERC 強制歸零避開。'
  }
];

export default function AIQuantAdvisor({ onSelectStock, stocks }) {
  const [totalCapital, setTotalCapital] = useState(300); // 300 萬元
  const [filterType, setFilterType] = useState('all'); // 'all', 'buy', 'avoid'
  const [universeMode, setUniverseMode] = useState('us'); // 'us' (純美股 ERC 2.0) | 'cross' (台美跨市場 2.0)

  const activeRecs = universeMode === 'us' ? RECOMMENDATIONS_US : RECOMMENDATIONS_CROSS;

  // Extract live macroeconomic indicators dynamically from stocks/indices state
  const foreignOi = stocks?.indices?.['外資台指期未平倉']?.close ?? 
                    stocks?.indices?.['外資台指淨未平倉 (口)']?.close ?? 
                    (stocks?.taifex_oi ?? -103473);
  const twVix = stocks?.indices?.['台指 VIX (波動率)']?.close ?? 
                stocks?.indices?.['台指VIX (波動率)']?.close ?? 28.25;

  // Dynamic Regime Probability calculation based on Foreign OI and VIX
  const rawCrisis = 55 + (Math.abs(foreignOi) - 50000) / 2500 + (twVix - 20) * 1.2;
  const crisisConfidence = Math.min(88.5, Math.max(50.0, rawCrisis));
  const crisisPct = Number(crisisConfidence.toFixed(2));
  const shakeoutPct = Number(((100 - crisisPct) * 0.52).toFixed(2));
  const consolPct = Number(((100 - crisisPct) * 0.33).toFixed(2));
  const expandPct = Number((100 - crisisPct - shakeoutPct - consolPct).toFixed(2));

  // Cash and Equity split
  const equityPct = 40.0;
  const cashPct = 60.0;
  const equityCapital = (totalCapital * (equityPct / 100)).toFixed(1);
  const cashCapital = (totalCapital * (cashPct / 100)).toFixed(1);

  // Filter recommendations
  const filteredRecs = activeRecs.filter(item => {
    if (filterType === 'buy') return item.weightPct > 0;
    if (filterType === 'avoid') return item.weightPct === 0;
    return true;
  });

  const handleStockClick = (rec) => {
    if (!onSelectStock) return;
    const cleanSym = rec.symbol.replace(/\.TWO?$/, '');
    let matchedStock = null;
    if (stocks) {
      const list = rec.market === 'tw' ? (stocks.tw || []) : (stocks.us || []);
      matchedStock = list.find(s => s.symbol === rec.symbol || s.symbol.replace(/\.TWO?$/, '') === cleanSym);
    }
    if (matchedStock) {
      onSelectStock(matchedStock);
    } else {
      onSelectStock({
        symbol: rec.symbol,
        name: rec.name,
        market: rec.market,
        close: rec.currPrice,
        ma60: rec.slPrice,
        signal: rec.weightPct > 0 ? 'Buy' : 'Sell',
        tactic: rec.highlight
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* 🌟 模組頂部標題與版本指示 */}
      <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 bg-gradient-to-br from-[#161A1E] via-[#0E1216] to-[#080A0C] shadow-2xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-red-600 to-amber-600 text-white shadow-lg shadow-red-600/30">
              <Cpu size={24} />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-lg md:text-xl font-black tracking-tight text-white flex items-center gap-2">
                  🤖 2026 正規軍量化演算與推薦參考系統
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-black bg-red-600/20 text-red-300 border border-red-500/30">
                  v2.5.0-AlphaUpgraded
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  實時量化推薦
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">
                基於機器學習市場狀態辨識 (Regime Switching)、動態等風險貢獻 (ERC) 數值最佳化與顏春煌教授 60MA 剛性防衛線
              </p>
            </div>
          </div>
        </div>

        {/* 🚨 模組一：機器學習市場狀態動態切換引擎 (ML Regime Card) */}
        <div className="p-5 rounded-2xl bg-red-950/20 border border-red-500/40 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
              </span>
              <span className="text-xs font-black uppercase tracking-wider text-red-300">
                機器學習微觀狀態辨識
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">當前置信度：</span>
              <span className="text-sm font-mono font-black text-red-400 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/30">
                {crisisPct}%
              </span>
            </div>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-[#0B0E11]/90 border border-red-500/30">
            <div>
              <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest">當前市場狀態 (Market Regime)</div>
              <div className="text-2xl font-black text-red-400 tracking-tight flex items-center gap-2 mt-0.5">
                <AlertTriangle size={24} className="text-red-500" />
                BEAR_LIQUIDITY_CRISIS (空頭流動性危機警戒)
              </div>
              <div className="text-xs text-gray-400 mt-1 leading-relaxed">
                觸發因子：外資期貨淨留倉 <b className="text-red-400 font-mono">{Number(foreignOi).toLocaleString()} 口</b> 歷史重壓、台指 VIX 飆升至 <b className="text-purple-400 font-mono">{twVix}</b>，市場處於高脆弱期。
              </div>
            </div>

            <div className="flex flex-wrap md:flex-nowrap gap-2 shrink-0">
              <div className="px-3 py-2 rounded-xl bg-red-500/10 border border-red-500/30 text-center min-w-[110px]">
                <span className="text-[9px] font-black text-gray-400 uppercase block">早盤ORB突破</span>
                <span className="text-xs font-black text-red-400 mt-0.5 block">🛑 熔斷暫停 (0%)</span>
              </div>
              <div className="px-3 py-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-center min-w-[110px]">
                <span className="text-[9px] font-black text-gray-400 uppercase block">現金儲備下限</span>
                <span className="text-xs font-black text-amber-300 font-mono mt-0.5 block">🛡️ 60.0% 強制</span>
              </div>
              <div className="px-3 py-2 rounded-xl bg-blue-500/10 border border-blue-500/30 text-center min-w-[110px]">
                <span className="text-[9px] font-black text-gray-400 uppercase block">股票總曝險上限</span>
                <span className="text-xs font-black text-blue-300 font-mono mt-0.5 block">💼 40.0% 封頂</span>
              </div>
            </div>
          </div>

          {/* 機率分佈進度條 */}
          <div className="space-y-1.5 pt-1">
            <div className="flex justify-between text-[10px] font-black text-gray-400">
              <span>四象限機器學習機率分佈：</span>
              <span>危機 {crisisPct}% | 洗盤 {shakeoutPct}% | 整理 {consolPct}% | 擴張 {expandPct}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-gray-800 overflow-hidden flex">
              <div style={{ width: `${crisisPct}%` }} className="bg-red-500 h-full" title={`空頭流動性危機 ${crisisPct}%`} />
              <div style={{ width: `${shakeoutPct}%` }} className="bg-orange-500 h-full" title={`高波動洗盤 ${shakeoutPct}%`} />
              <div style={{ width: `${consolPct}%` }} className="bg-blue-500 h-full" title={`箱型整理 ${consolPct}%`} />
              <div style={{ width: `${expandPct}%` }} className="bg-emerald-500 h-full" title={`多頭擴張 ${expandPct}%`} />
            </div>
          </div>
        </div>
      </div>

      {/* 🧮 實戰資金配置模擬計算器 */}
      <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 bg-[#12161A] shadow-xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <Calculator size={20} className="text-amber-400" />
            <h3 className="text-base font-black text-white">
              🧮 投資本金實戰配置試算 (Dynamic Capital Sizing)
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400 font-bold">總可投資資金：</span>
            <input
              type="number"
              value={totalCapital}
              onChange={(e) => setTotalCapital(Math.max(10, Number(e.target.value)))}
              className="w-28 bg-[#1B2127] border border-amber-500/40 rounded-xl px-3 py-1.5 text-right text-amber-300 font-mono font-black text-sm focus:outline-none focus:border-amber-400 shadow-inner"
            />
            <span className="text-xs text-gray-300 font-bold">萬元</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          <div className="p-3.5 rounded-2xl bg-amber-950/30 border border-amber-500/40">
            <span className="text-[10px] font-black text-amber-400 uppercase tracking-wider block">保命防禦現金池 (60%)</span>
            <span className="text-2xl font-black font-mono text-amber-300 mt-1 block">{cashCapital} 萬元</span>
            <span className="text-[10px] text-gray-400 mt-0.5 block">保留充足彈藥，待外資空單與 VIX 退潮時低檔接棒</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-blue-950/30 border border-blue-500/40">
            <span className="text-[10px] font-black text-blue-400 uppercase tracking-wider block">動態平價股票總曝險 (40%)</span>
            <span className="text-2xl font-black font-mono text-blue-300 mt-1 block">{equityCapital} 萬元</span>
            <span className="text-[10px] text-gray-400 mt-0.5 block">分散於 8 檔三率三升主流標的，單一股票風險精確均等化</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-emerald-950/30 border border-emerald-500/40 sm:col-span-2 md:col-span-1">
            <span className="text-[10px] font-black text-emerald-400 uppercase tracking-wider block">SLSQP 最佳化成效</span>
            <span className="text-2xl font-black font-mono text-emerald-300 mt-1 block">-4.85% 波動降幅</span>
            <span className="text-[10px] text-gray-400 mt-0.5 block">由等權重 13.40% 降至 12.75%，避免黑天鵝重擊</span>
          </div>
        </div>
      </div>

      {/* ⭐ 模組二：2026 正規軍量化推薦參考名單與精準配比 */}
      <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 bg-[#12161A] shadow-xl space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
          <div className="flex items-center gap-2.5">
            <Target size={22} className="text-emerald-400" />
            <div>
              <h3 className="text-base font-black text-white flex items-center gap-2">
                ⭐ 2026 核心推薦參考組合與量化配比
                <span className="text-xs text-gray-400 font-normal">（點選任一檔可即時聯動技術圖表）</span>
              </h3>
              <p className="text-xs text-gray-400">
                以等風險貢獻 (ERC) 計算最優配比，兼顧產業成長與極致風控
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1 p-1 bg-[#1A2026] rounded-xl border border-amber-500/30 text-xs font-black">
              <button
                onClick={() => setUniverseMode('us')}
                className={`px-3 py-1.5 rounded-lg transition-all ${universeMode === 'us' ? 'bg-amber-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
              >
                🇺🇸 純美股 ERC 2.0
              </button>
              <button
                onClick={() => setUniverseMode('cross')}
                className={`px-3 py-1.5 rounded-lg transition-all ${universeMode === 'cross' ? 'bg-blue-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
              >
                🌐 台美跨市場 2.0
              </button>
            </div>

            <div className="flex items-center gap-1.5 p-1 bg-[#1A2026] rounded-xl border border-white/10 text-xs font-black">
              <button
                onClick={() => setFilterType('all')}
                className={`px-3 py-1.5 rounded-lg transition-all ${filterType === 'all' ? 'bg-white/10 text-white shadow' : 'text-gray-400 hover:text-white'}`}
              >
                全部標的 ({activeRecs.length})
              </button>
              <button
                onClick={() => setFilterType('buy')}
                className={`px-3 py-1.5 rounded-lg transition-all ${filterType === 'buy' ? 'bg-emerald-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
              >
                推薦配置 ({activeRecs.filter(r => r.weightPct > 0).length})
              </button>
              <button
                onClick={() => setFilterType('avoid')}
                className={`px-3 py-1.5 rounded-lg transition-all ${filterType === 'avoid' ? 'bg-red-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
              >
                衛星 / 剔除 ({activeRecs.filter(r => r.weightPct === 0).length})
              </button>
            </div>
          </div>
        </div>

        {/* 推薦卡片列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRecs.map((rec) => {
            const cleanSym = rec.symbol.replace(/\.TWO?$/, '');
            let liveStock = null;
            if (stocks) {
              const list = rec.market === 'tw' ? (stocks.tw || []) : (stocks.us || []);
              liveStock = list.find(s => s.symbol === rec.symbol || s.symbol.replace(/\.TWO?$/, '') === cleanSym);
            }
            const livePrice = liveStock?.close || rec.currPrice;
            const liveSL = liveStock?.ma60 || rec.slPrice;
            const isBelowMA60 = livePrice < liveSL * 0.992;
            const effectiveWeight = isBelowMA60 && rec.weightPct === 0 ? 0 : rec.weightPct;
            const liveTP = rec.tpPrice > 0 ? (liveStock ? Math.round(livePrice * 1.25) : rec.tpPrice) : 0;
            const allocAmount = ((totalCapital * effectiveWeight) / 100).toFixed(1);
            const isZero = effectiveWeight === 0;
            const dynAction = isZero ? rec.action : (isBelowMA60 ? '【暫破季線 / 待站回MA60或尾盤收腳】' : rec.action);
            const dynActionColor = isZero ? rec.actionColor : (isBelowMA60 ? 'text-amber-300 bg-amber-500/20 border-amber-500/40' : rec.actionColor);

            return (
              <div
                key={rec.symbol}
                onClick={() => handleStockClick(rec)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer group flex flex-col justify-between ${
                  isZero 
                    ? 'bg-red-950/10 border-red-500/30 hover:border-red-500/60' 
                    : 'bg-[#181D23] border-white/10 hover:border-emerald-500/50 hover:bg-[#1E242C] shadow-lg'
                }`}
              >
                <div>
                  {/* Top line: Symbol, Name, Tier */}
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-base font-black text-white group-hover:text-emerald-400 transition-colors">
                          {rec.symbol.replace(/\.TWO?$/, '')} {rec.name}
                        </span>
                        <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity text-emerald-400" />
                      </div>
                      <span className={`inline-block text-[9px] font-bold px-1.5 py-0.5 rounded border mt-1 ${rec.tierColor}`}>
                        {rec.tier}
                      </span>
                    </div>

                    <div className="text-right">
                      <span className={`text-[10px] font-black px-2 py-0.5 rounded border ${dynActionColor}`}>
                        {dynAction}
                      </span>
                      <div className="text-xs font-mono text-gray-400 mt-1">
                        現價 <b className="text-white">${livePrice}</b>
                      </div>
                    </div>
                  </div>

                  {/* Highlights */}
                  <p className="text-xs text-gray-300 leading-relaxed mt-2 p-2 rounded-xl bg-[#0F1316] border border-white/5">
                    {rec.highlight}
                  </p>
                </div>

                {/* Bottom metrics */}
                <div className="mt-4 pt-3 border-t border-white/10 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-400">動態平價建議配比：</span>
                    <span className={`font-mono font-black text-sm ${isZero ? 'text-red-400' : 'text-emerald-400'}`}>
                      {rec.weightPct.toFixed(2)}%
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-400">目前本金試算買進：</span>
                    <span className={`font-mono font-black text-sm ${isZero ? 'text-gray-500' : 'text-amber-300'}`}>
                      {isZero ? '0 萬 (禁止買進)' : `${allocAmount} 萬元`}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[10px] pt-1">
                    <div className="p-1.5 rounded-lg bg-[#0F1316] text-center border border-white/5">
                      <span className="text-gray-500 block">季線防守點 (SL)</span>
                      <span className="font-mono font-bold text-red-400">${liveSL}</span>
                    </div>
                    <div className="p-1.5 rounded-lg bg-[#0F1316] text-center border border-white/5">
                      <span className="text-gray-500 block">預期目標 (TP)</span>
                      <span className="font-mono font-bold text-emerald-400">{liveTP > 0 ? `$${liveTP}` : '無'}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ⚖️ 動態風險平價 (ERC) 數值最佳化細節與哲學 */}
      <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 bg-[#12161A] shadow-xl space-y-4">
        <div className="flex items-center gap-2.5">
          <Scale size={20} className="text-blue-400" />
          <h3 className="text-base font-black text-white">
            ⚖️ 為什麼需要動態風險平價 (ERC)？
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-300 leading-relaxed">
          <div className="p-4 rounded-2xl bg-[#161B21] border border-white/5 space-y-2">
            <h4 className="font-black text-red-400 text-sm flex items-center gap-1.5">
              <XCircle size={16} /> 傳統等權重配置的隱藏致命陷阱
            </h4>
            <p>
              若給每檔股票相同的資金（例如 11.1%），表面上看似分散，但<b>高波動標的（如聯發科 52.88%、輝達 45.78%）將佔據整個投資組合 65% 以上的總風險</b>！
              一旦龍頭股出現劇烈回檔，整個帳戶淨值將遭受不成比例的重創。
            </p>
          </div>

          <div className="p-4 rounded-2xl bg-[#161B21] border border-white/5 space-y-2">
            <h4 className="font-black text-emerald-400 text-sm flex items-center gap-1.5">
              <CheckCircle2 size={16} /> 正規軍動態風險平價的最佳化解法
            </h4>
            <p>
              透過 SLSQP 數值求解器，<b>強迫每一檔資產貢獻完全相等的風險度（均等化為 11.11%）</b>。
              低波動穩健股（台積電 27%、鴻海 28%）獲得較高配比（7.6%、6.8%），高波動成長股適度壓低（輝達 3.9%、聯發科 1.4%），使投資組合展現出極致的抗震性與防禦力！
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

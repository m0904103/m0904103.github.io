import React, { useState } from 'react';
import { 
  ShieldCheck, AlertTriangle, TrendingUp, TrendingDown, Target, 
  Cpu, Zap, PieChart, Coins, ArrowUpRight, CheckCircle2, 
  XCircle, Flame, Layers, Lock, Scale, Calculator, Sliders,
  HelpCircle, Compass, Activity, ArrowRight, DollarSign
} from 'lucide-react';

// Recommended Reference Universe calculated by SLSQP ERC & Half-Kelly optimization
const RECOMMENDATIONS = [
  {
    symbol: '2330.TW',
    name: '台積電',
    market: 'tw',
    tier: '🏆 核心首選 (Core #1)',
    tierColor: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    action: '【分批逢低承接】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 7.58,
    annualVol: 27.06,
    slPrice: 945.0,
    tpPrice: 1250.0,
    currPrice: 980.0,
    highlight: '全球 2nm/3nm 先進製程大壟斷，毛利率穩超 53%，三率三升，外資長線核心定海神針。'
  },
  {
    symbol: '2317.TW',
    name: '鴻海',
    market: 'tw',
    tier: '⭐ 穩健低波 (Low Volatility)',
    tierColor: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    action: '【守穩季線分批佈局】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 6.81,
    annualVol: 28.51,
    slPrice: 178.5,
    tpPrice: 235.0,
    currPrice: 184.0,
    highlight: 'GB200 AI 伺服器首發出貨，本益比合理，外資與投信近期波段加碼重心。'
  },
  {
    symbol: '2383.TW',
    name: '台光電',
    market: 'tw',
    tier: '⭐ 成長動能 (Growth Momentum)',
    tierColor: 'text-purple-300 bg-purple-500/10 border-purple-500/30',
    action: '【回測季線支撐逢低吸納】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 5.68,
    annualVol: 35.84,
    slPrice: 432.0,
    tpPrice: 560.0,
    currPrice: 456.0,
    highlight: 'M8/M9 高階銅箔基板 (CCL) 全球市佔率第一，受惠 AI 伺服器規格全面升級。'
  },
  {
    symbol: '3017.TW',
    name: '奇鋐',
    market: 'tw',
    tier: '⭐ 散熱龍料 (Liquid Cooling)',
    tierColor: 'text-cyan-300 bg-cyan-500/10 border-cyan-500/30',
    action: '【箱型拉回偏多操作】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 5.19,
    annualVol: 39.67,
    slPrice: 580.0,
    tpPrice: 750.0,
    currPrice: 615.0,
    highlight: '水冷板與分歧管核心供應商，獲利連三季成長，站穩季線具備強大結構支撐。'
  },
  {
    symbol: 'VRT',
    name: 'Vertiv Holdings',
    market: 'us',
    tier: '🇺🇸 美股 AI 基建 (US Infrastructure)',
    tierColor: 'text-indigo-300 bg-indigo-500/10 border-indigo-500/30',
    action: '【波段順勢抱牢 / 拉回加碼】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 5.05,
    annualVol: 39.96,
    slPrice: 88.5,
    tpPrice: 135.0,
    currPrice: 94.2,
    highlight: '全球數據中心熱管理與電力系統龍頭，微軟、Google 算力基建必選設備商。'
  },
  {
    symbol: '6669.TW',
    name: '緯穎',
    market: 'tw',
    tier: '⭐ 雲端純度最高 (Pure Cloud AI)',
    tierColor: 'text-rose-300 bg-rose-500/10 border-rose-500/30',
    action: '【高價股輕倉參與】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 4.35,
    annualVol: 43.53,
    slPrice: 1980.0,
    tpPrice: 2600.0,
    currPrice: 2090.0,
    highlight: 'ASIC 客製化伺服器大單湧入，EPS 具爆發力，但高波動依演算法縮減配置比重。'
  },
  {
    symbol: 'NVDA',
    name: '輝達',
    market: 'us',
    tier: '🇺🇸 全球算力霸主 (AI King)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【高波動適度降權 / 定額持有】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 3.94,
    annualVol: 45.78,
    slPrice: 115.0,
    tpPrice: 160.0,
    currPrice: 122.5,
    highlight: '算力無可撼動，但因年化波動度高達 45.78%，ERC 平價演算法自動減權以控制總風險。'
  },
  {
    symbol: '2454.TW',
    name: '聯發科',
    market: 'tw',
    tier: '🟡 邊緣旗艦 (Edge AI)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【極高波動輕倉防守】',
    actionColor: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
    weightPct: 1.42,
    annualVol: 52.88,
    slPrice: 1180.0,
    tpPrice: 1500.0,
    currPrice: 1215.0,
    highlight: '天璣晶片旗艦導入，但短期受宏觀手機週期影響年化波動 52.88%，系統自動壓低曝險。'
  },
  {
    symbol: '3324.TW',
    name: '雙鴻',
    market: 'tw',
    tier: '🚨 破季線避開 (Below MA60 Alert)',
    tierColor: 'text-red-400 bg-red-500/20 border-red-500/40',
    action: '【剛性避開 / 0% 配比 / 嚴禁接飛刀】',
    actionColor: 'text-red-400 bg-red-600/30 border-red-500/50',
    weightPct: 0.0,
    annualVol: 36.06,
    slPrice: 685.0,
    tpPrice: 0.0,
    currPrice: 642.0,
    highlight: '【顏春煌教授鐵律】股價跌破 60MA 生命線，嚴禁盲目低接！半凱利上限與 ERC 強制歸零！'
  }
];

export default function AIQuantAdvisor({ onSelectStock, stocks }) {
  const [totalCapital, setTotalCapital] = useState(300); // 300 萬元
  const [filterType, setFilterType] = useState('all'); // 'all', 'buy', 'avoid'

  // Cash and Equity split
  const equityPct = 40.0;
  const cashPct = 60.0;
  const equityCapital = (totalCapital * (equityPct / 100)).toFixed(1);
  const cashCapital = (totalCapital * (cashPct / 100)).toFixed(1);

  // Filter recommendations
  const filteredRecs = RECOMMENDATIONS.filter(item => {
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
      matchedStock = list.find(s => s.symbol.includes(cleanSym) || s.symbol === rec.symbol);
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
                67.51%
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
                觸發因子：外資期貨淨留倉 <b className="text-red-400 font-mono">-78,706 口</b> 歷史重壓、台指 VIX 飆升至 <b className="text-purple-400 font-mono">29.51</b>，市場處於高脆弱期。
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
              <span>危機 67.5% | 洗盤 16.7% | 整理 11.7% | 擴張 4.1%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-gray-800 overflow-hidden flex">
              <div style={{ width: '67.51%' }} className="bg-red-500 h-full" title="空頭流動性危機 67.51%" />
              <div style={{ width: '16.65%' }} className="bg-orange-500 h-full" title="高波動洗盤 16.65%" />
              <div style={{ width: '11.73%' }} className="bg-blue-500 h-full" title="箱型整理 11.73%" />
              <div style={{ width: '4.11%' }} className="bg-emerald-500 h-full" title="多頭擴張 4.11%" />
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

          <div className="flex items-center gap-1.5 p-1 bg-[#1A2026] rounded-xl border border-white/10 text-xs font-black">
            <button
              onClick={() => setFilterType('all')}
              className={`px-3 py-1.5 rounded-lg transition-all ${filterType === 'all' ? 'bg-white/10 text-white shadow' : 'text-gray-400 hover:text-white'}`}
            >
              全部標的 ({RECOMMENDATIONS.length})
            </button>
            <button
              onClick={() => setFilterType('buy')}
              className={`px-3 py-1.5 rounded-lg transition-all ${filterType === 'buy' ? 'bg-emerald-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
            >
              推薦配置 ({RECOMMENDATIONS.filter(r => r.weightPct > 0).length})
            </button>
            <button
              onClick={() => setFilterType('avoid')}
              className={`px-3 py-1.5 rounded-lg transition-all ${filterType === 'avoid' ? 'bg-red-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
            >
              破線避開 ({RECOMMENDATIONS.filter(r => r.weightPct === 0).length})
            </button>
          </div>
        </div>

        {/* 推薦卡片列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRecs.map((rec) => {
            const allocAmount = ((totalCapital * rec.weightPct) / 100).toFixed(1);
            const isZero = rec.weightPct === 0;

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
                      <span className={`text-[10px] font-black px-2 py-0.5 rounded border ${rec.actionColor}`}>
                        {rec.action}
                      </span>
                      <div className="text-xs font-mono text-gray-400 mt-1">
                        現價 <b className="text-white">${rec.currPrice}</b>
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
                      <span className="font-mono font-bold text-red-400">${rec.slPrice}</span>
                    </div>
                    <div className="p-1.5 rounded-lg bg-[#0F1316] text-center border border-white/5">
                      <span className="text-gray-500 block">預期目標 (TP)</span>
                      <span className="font-mono font-bold text-emerald-400">{rec.tpPrice > 0 ? `$${rec.tpPrice}` : '無'}</span>
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

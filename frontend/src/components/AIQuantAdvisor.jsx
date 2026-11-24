import React, { useState, useRef } from 'react';
import { 
  ShieldCheck, AlertTriangle, TrendingUp, TrendingDown, Target, 
  Cpu, Zap, PieChart, Coins, ArrowUpRight, CheckCircle2, 
  XCircle, Flame, Layers, Lock, Scale, Calculator, Sliders,
  HelpCircle, Compass, Activity, ArrowRight, DollarSign
} from 'lucide-react';

// Gen 30 Red-Team Zero-Blindspot 2027 Pure US ERC Blueprint (SGOV + XLI + XLE + Valuation Cap)
const RECOMMENDATIONS_US = [
  {
    symbol: 'SGOV',
    name: 'iShares 0-3月美國短債',
    market: 'us',
    tier: '🛡️ 無風險避險停泊王 (18.0%)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【取代高估值防禦股 / 穩領 ~4.7%】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 18.0,
    annualVol: 0.8,
    slPrice: 100.0,
    tpPrice: 105.0,
    currPrice: 100.55,
    highlight: '紅隊反證首選！單週吸金 10 億美元，零久期風險、零殺估值泡沫，取代 45 倍 PE 的 WMT 作為美元終極防禦停泊倉。'
  },
  {
    symbol: 'LLY',
    name: 'Eli Lilly 禮來',
    market: 'us',
    tier: '🧬 醫療成長引擎 (14.0%)',
    tierColor: 'text-teal-300 bg-teal-500/10 border-teal-500/30',
    action: '【布林下軌止跌＋KD金叉分批】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 14.0,
    annualVol: 23.0,
    slPrice: 1248.39,
    tpPrice: 1580.0,
    currPrice: 1364.6,
    highlight: 'GLP-1 帶動營收年增 45.5%、Beta 僅 0.39；惟目前 PE 偏高且 XLV 週度流出，嚴守顏老師 KD 金叉止跌才分批。'
  },
  {
    symbol: 'JPM',
    name: 'JPMorgan 摩根大通',
    market: 'us',
    tier: '🏦 高利率持久戰金融王者 (14.0%)',
    tierColor: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    action: '【前瞻 PE 12.1x / 布林止跌分批】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 14.0,
    annualVol: 21.0,
    slPrice: 339.15,
    tpPrice: 380.0,
    currPrice: 316.66,
    highlight: '上調 2027 淨利息收入至 1,070 億美元，高估值安全邊際直接受惠高利率平台；待 12/09 FOMC 落地確認趨勢。'
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft 微軟',
    market: 'us',
    tier: '💻 AI 企業軟體與 Agent (14.0%)',
    tierColor: 'text-cyan-300 bg-cyan-500/10 border-cyan-500/30',
    action: '【低於十年均值 / 布林止跌分批】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 14.0,
    annualVol: 22.0,
    slPrice: 515.34,
    tpPrice: 600.0,
    currPrice: 492.95,
    highlight: 'AI 硬體轉軟體變現核心交匯點，前瞻 PE 降至 24.6x；與 XLK (+12.2億) 宏觀資金流共振，等止跌金叉分批。'
  },
  {
    symbol: 'XLI',
    name: '美國工業基建 ETF',
    market: 'us',
    tier: '🏗️ 紅隊補漏：工業領先板塊 (10.0%)',
    tierColor: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    action: '【單週吸金 +5.76 億 / 動能領先】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 10.0,
    annualVol: 18.0,
    slPrice: 135.0,
    tpPrice: 165.0,
    currPrice: 142.0,
    highlight: '紅隊抓出 260 檔原系統盲點！11 月中旬單週淨流入 5.76 億美元居板塊第二，RRG 相對動能轉入領先象限。'
  },
  {
    symbol: 'XLE',
    name: '美國能源板塊 ETF',
    market: 'us',
    tier: '🛢️ 紅隊補漏：年度冠軍 (+36.2%)',
    tierColor: 'text-orange-300 bg-orange-500/10 border-orange-500/30',
    action: '【通膨與中東風險最佳對沖 (8.0%)】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 8.0,
    annualVol: 24.0,
    slPrice: 88.0,
    tpPrice: 112.0,
    currPrice: 95.0,
    highlight: '美股 11 大板塊過去一年績效總冠軍 (+36.2%，領先 SPY 30.5%)，完美對沖二次通膨與中東地緣衝突風險。'
  },
  {
    symbol: 'CEG',
    name: 'Constellation 核能電力',
    market: 'us',
    tier: '⚛️ 24/7 無碳核能底座 (8.0%)',
    tierColor: 'text-teal-300 bg-teal-500/10 border-teal-500/30',
    action: '【嚴守右側站回 60MA 季線進場】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 8.0,
    annualVol: 24.0,
    slPrice: 268.86,
    tpPrice: 346.0,
    currPrice: 251.69,
    highlight: '全美最大無碳核電商，2026 已修正 30% 消化估值；等 12/09 點陣圖落地且股價站回 60MA 季線再補齊。'
  },
  {
    symbol: 'ASML',
    name: 'ASML 艾司摩爾',
    market: 'us',
    tier: '🔬 EUV 獨家壟斷 (7.0%)',
    tierColor: 'text-sky-300 bg-sky-500/10 border-sky-500/30',
    action: '【右側站回 60MA 季線分批回補】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 7.0,
    annualVol: 34.0,
    slPrice: 1630.21,
    tpPrice: 1850.0,
    currPrice: 1383.8,
    highlight: '現金為負債 6.5 倍、2027~2028 產能滿載；隨 SMH (+8.23億) 宏觀資金流觀察，待站回季線即右側啟動。'
  },
  {
    symbol: 'AVGO',
    name: 'Broadcom 博通',
    market: 'us',
    tier: '🚀 AI 客製化 ASIC (7.0%)',
    tierColor: 'text-indigo-300 bg-indigo-500/10 border-indigo-500/30',
    action: '【右側站回 60MA 季線分批回補】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 7.0,
    annualVol: 36.0,
    slPrice: 345.24,
    tpPrice: 410.0,
    currPrice: 313.42,
    highlight: '2027 AI 投報率檢驗期受惠者，毛利率 66.5%＋VMware 現金流；待站回 60MA 季線後右側承接。'
  },
  {
    symbol: 'NVDA',
    name: 'NVIDIA 輝達',
    market: 'us',
    tier: '⚠️ 16 天事件觀察池 (衛星 ≤5%)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【盯 12/03 聽證會與站穩 173.62】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 0.0,
    annualVol: 45.8,
    slPrice: 208.67,
    tpPrice: 240.0,
    currPrice: 165.19,
    highlight: '紅隊修正為「事件觀察池」：只要 XLK/SMH 未轉淨流出且 12/03 聽證會無毀滅禁令、站穩 20EMA (173.62) 即可隨時回補！'
  },
  {
    symbol: 'WMT',
    name: 'Walmart 沃爾瑪',
    market: 'us',
    tier: '🚨 高估值防禦警示 (PE 45.7x)',
    tierColor: 'text-red-400 bg-red-500/20 border-red-500/40',
    action: '【Gen 30 估值安全閥 / 勿追高】',
    actionColor: 'text-red-400 bg-red-600/30 border-red-500/50',
    weightPct: 0.0,
    annualVol: 19.5,
    slPrice: 115.30,
    tpPrice: 145.0,
    currPrice: 129.44,
    highlight: '【Gen 30 紅隊閥】技術面強但本益比已達 45.7 倍（遠期 38~42 倍），防禦籌碼過度擁擠，避險資金改停泊 SGOV 更安全！'
  }
];

// Gen 30 Red-Team Zero-Blindspot 2027 Cross-Market TW+US Constrained ERC Blueprint
const RECOMMENDATIONS_CROSS = [
  {
    symbol: 'SGOV',
    name: 'iShares 0-3月美短債',
    market: 'us',
    tier: '🛡️ 美元無風險避險底倉 (15.0%)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【取代高估值防禦股 / 穩領 ~4.7%】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 15.0,
    annualVol: 0.8,
    slPrice: 100.0,
    tpPrice: 105.0,
    currPrice: 100.55,
    highlight: '紅隊核心修正！單週吸金 10 億美元，零久期與殺估值風險，解決重押 30 倍中華電／45 倍 WMT 的擁擠泡沫隱憂。'
  },
  {
    symbol: 'LLY',
    name: 'Eli Lilly 禮來',
    market: 'us',
    tier: '🧬 醫療生技成長引擎 (12.0%)',
    tierColor: 'text-teal-300 bg-teal-500/10 border-teal-500/30',
    action: '【布林下軌止跌＋KD金叉分批】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 12.0,
    annualVol: 23.0,
    slPrice: 1248.39,
    tpPrice: 1580.0,
    currPrice: 1364.6,
    highlight: 'GLP-1 營收年增 45.5%、Beta 僅 0.39；嚴守顏老師紀律，等布林止跌＋KD 金叉分批承接、絕不追高。'
  },
  {
    symbol: 'JPM',
    name: 'JPMorgan 摩根大通',
    market: 'us',
    tier: '🇺🇸 美股高利率金融龍頭 (11.0%)',
    tierColor: 'text-sky-300 bg-sky-500/10 border-sky-500/30',
    action: '【前瞻 PE 12.1x / 布林止跌分批】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 11.0,
    annualVol: 21.0,
    slPrice: 339.15,
    tpPrice: 380.0,
    currPrice: 316.66,
    highlight: '2027 淨利息收入指引 1,070 億美元，直接受惠高利率環境；等 KD 低檔止跌分批建倉。'
  },
  {
    symbol: '2886.TW',
    name: '兆豐金',
    market: 'tw',
    tier: '🏦 純銀行官股金控防雷 (10.0%)',
    tierColor: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    action: '【避開壽險 TW-ICS 地雷 / 投信買超】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 10.0,
    annualVol: 14.5,
    slPrice: 38.5,
    tpPrice: 46.0,
    currPrice: 40.5,
    highlight: '紅隊修正：取代含壽險金控！無龐大壽險美債 OCI 跌價與避險成本壓力，且名列投信 11 月買超首選。'
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft 微軟',
    market: 'us',
    tier: '💻 企業級 AI 軟體與 Agent (10.0%)',
    tierColor: 'text-cyan-300 bg-cyan-500/10 border-cyan-500/30',
    action: '【低於十年均值 / 布林止跌分批】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 10.0,
    annualVol: 22.0,
    slPrice: 515.34,
    tpPrice: 600.0,
    currPrice: 492.95,
    highlight: 'AI 商業化變現核心，ROE 32.3%、前瞻 PE 24.6 倍低於十年均值；與 XLK (+12.2億) 宏觀資金流同步。'
  },
  {
    symbol: 'CEG',
    name: 'Constellation 核電',
    market: 'us',
    tier: '⚛️ 核能基載電力底座 (8.0%)',
    tierColor: 'text-purple-300 bg-purple-500/10 border-purple-500/30',
    action: '【嚴禁抄底 / 待右側站回 60MA】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 8.0,
    annualVol: 24.0,
    slPrice: 268.86,
    tpPrice: 346.0,
    currPrice: 251.69,
    highlight: '全美最大無碳核電商，2026 已修正 30%；嚴守顏老師紀律，等 12/09 FOMC 落地且站回季線再補齊。'
  },
  {
    symbol: '2330.TW',
    name: '台積電',
    market: 'tw',
    tier: '🏆 AI 核心晶圓與封裝壟斷 (7.0%)',
    tierColor: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    action: '【右側帶量站回 60MA 季線進場】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 7.0,
    annualVol: 30.0,
    slPrice: 2386.47,
    tpPrice: 2680.0,
    currPrice: 2030.0,
    highlight: 'N2 與 CoWoS 絕對壟斷，投信 11 月逆勢低接；待 12/03 聽證會後 TSM 外內盤轉強 (>1.1x) 且站回季線回補。'
  },
  {
    symbol: '2412.TW',
    name: '中華電',
    market: 'tw',
    tier: '⚠️ 降權防禦底倉 (6.9% / PE偏高)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【PE 29.8x 勿追高 / 等拉回季線】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 6.9,
    annualVol: 11.0,
    slPrice: 150.12,
    tpPrice: 180.0,
    currPrice: 164.5,
    highlight: '負 Beta (-0.05) 抗震力極強，但 Gen 30 紅隊閥警示其 PE 29.8x 遠高於均值 18.3x，權重由 15.9% 降至 6.9% 絕不追高！'
  },
  {
    symbol: 'XLI',
    name: '美國工業基建 ETF',
    market: 'us',
    tier: '🏗️ 紅隊補漏：工業領先板塊 (6.0%)',
    tierColor: 'text-orange-300 bg-orange-500/10 border-orange-500/30',
    action: '【單週吸金 +5.76 億 / 動能領先】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 6.0,
    annualVol: 18.0,
    slPrice: 135.0,
    tpPrice: 165.0,
    currPrice: 142.0,
    highlight: '補齊美股 11 月單週吸金第二名的工業基建板塊，RRG 動能轉入領先象限，大幅分散純科技與電信風險。'
  },
  {
    symbol: 'ASML',
    name: '艾司摩爾',
    market: 'us',
    tier: '🔬 EUV 獨家壟斷 (5.0%)',
    tierColor: 'text-indigo-300 bg-indigo-500/10 border-indigo-500/30',
    action: '【右側站回 60MA 季線分批回補】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 5.0,
    annualVol: 34.0,
    slPrice: 1630.21,
    tpPrice: 1850.0,
    currPrice: 1383.8,
    highlight: '現金為負債 6.5 倍、2027~2028 產能滿載；隨 SMH 宏觀資金流觀察，右側站回季線即回補。'
  },
  {
    symbol: '2308.TW',
    name: '台達電',
    market: 'tw',
    tier: '⚡ AI 高壓電源、液冷與電網 (5.0%)',
    tierColor: 'text-lime-300 bg-lime-500/10 border-lime-500/30',
    action: '【取代奇鋐雙鴻 / 待站回 60MA】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 5.0,
    annualVol: 35.0,
    slPrice: 1593.33,
    tpPrice: 1650.0,
    currPrice: 990.0,
    highlight: '兼具高壓電源、液冷與電網儲能，2027 EPS 預估大躍升；嚴禁左側接刀，待站回 60MA 季線承接。'
  },
  {
    symbol: 'AVGO',
    name: 'Broadcom 博通',
    market: 'us',
    tier: '🚀 AI 客製化 ASIC 與網通 (4.1%)',
    tierColor: 'text-pink-300 bg-pink-500/10 border-pink-500/30',
    action: '【右側站回 60MA 季線分批回補】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 4.1,
    annualVol: 36.0,
    slPrice: 345.24,
    tpPrice: 410.0,
    currPrice: 313.42,
    highlight: '2027 AI 投報率檢驗期受惠者，66.5% 高毛利率＋VMware 現金流；右側站回季線即進場。'
  },
  {
    symbol: 'NVDA',
    name: '輝達',
    market: 'us',
    tier: '⚠️ 16 天事件觀察池 (衛星 ≤5%)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【盯 12/03 聽證會與站穩 173.62】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 0.0,
    annualVol: 45.8,
    slPrice: 208.67,
    tpPrice: 240.0,
    currPrice: 165.19,
    highlight: '紅隊修正為「事件觀察池」：12/03 聽證會與 12/09 FOMC 落地且站穩 20EMA (173.62) 後，隨時保留回補彈性！'
  }
];

export default function AIQuantAdvisor({ onSelectStock, stocks }) {
  const [totalCapital, setTotalCapital] = useState(100); // 預設 100 萬元實戰本金
  const [filterType, setFilterType] = useState('all'); // 'all', 'buy', 'avoid'
  const [universeMode, setUniverseMode] = useState('cross'); // 'us' (純美股 ERC 2.0) | 'cross' (台美跨市場 2.0)
  const cardsGridRef = useRef(null);

  const handleFilterChange = (nextType) => {
    setFilterType(nextType);
    if (cardsGridRef.current) {
      cardsGridRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  };

  const mr = stocks?.market_regime;
  const rsiInfo = stocks?.rsi_loop;
  const qa = stocks?.quant_advisor;

  // 優先使用後端 Gen18+ 實時算出的 ERC 推薦組合，無資料時才退回預設範本
  const dynamicUs = qa?.us?.length ? qa.us.map(item => ({
    ...item,
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
  })) : RECOMMENDATIONS_US;
  const dynamicCross = qa?.cross?.length ? qa.cross.map(item => ({
    ...item,
    tierColor: item.market === 'tw' ? 'text-amber-300 bg-amber-500/10 border-amber-500/30' : 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
  })) : RECOMMENDATIONS_CROSS;

  const activeRecs = universeMode === 'us' ? dynamicUs : dynamicCross;

  // Extract live macroeconomic indicators dynamically from backend market_regime or indices
  const foreignOi = mr?.foreign_oi ??
                    stocks?.indices?.['外資台指期未平倉']?.close ?? 
                    stocks?.indices?.['外資台指淨未平倉 (口)']?.close ?? 
                    (stocks?.taifex_oi ?? -40000);
  const twVix = mr?.tw_vix ??
                stocks?.indices?.['台指 VIX (波動率)']?.close ?? 
                stocks?.indices?.['台指VIX (波動率)']?.close ?? 20.0;

  // Dynamic Regime Probabilities from real backend calculation
  const crisisPct = mr?.probs?.crisis ?? 25.0;
  const shakeoutPct = mr?.probs?.shakeout ?? 20.0;
  const consolPct = mr?.probs?.consolidation ?? 25.0;
  const expandPct = mr?.probs?.expansion ?? 30.0;
  const regimeCode = mr?.code || 'CONSOLIDATION_ROTATION';
  const regimeLabel = mr?.label || '動態量化掃描中';
  const regimeConf = mr?.confidence ?? crisisPct;
  const orbMode = mr?.orb_mode || '依季線訊號執行';

  // Cash and Equity split dynamically driven by regime
  const equityPct = mr?.equity_pct ?? 60.0;
  const cashPct = mr?.cash_pct ?? 40.0;
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
                  🤖 2027 正規軍量化演算與推薦參考系統
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-black bg-emerald-600/20 text-emerald-300 border border-emerald-500/30">
                  Gen{rsiInfo?.gen_version || 18}-RSI-Live
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  帳本追蹤 {rsiInfo?.total_logged ?? 0} 檔
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">
                基於即時市場寬度 ({mr?.tw_breadth_60ma ?? '--'}% 站上60MA)、動態等風險貢獻 (ERC) 與顏春煌教授 60MA 剛性防衛線
              </p>
            </div>
          </div>
        </div>

        {/* 🚨 模組一：機器學習市場狀態動態切換引擎 (ML Regime Card) */}
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-white/15 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <span className="relative flex h-3 w-3">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${mr?.tone === 'emerald' ? 'bg-emerald-400' : 'bg-amber-400'} opacity-75`}></span>
                <span className={`relative inline-flex rounded-full h-3 w-3 ${mr?.tone === 'emerald' ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
              </span>
              <span className="text-xs font-black uppercase tracking-wider text-gray-200">
                動態大盤狀態辨識 (Real-Time Regime)
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">當前置信度：</span>
              <span className="text-sm font-mono font-black text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/30">
                {regimeConf}%
              </span>
            </div>
          </div>

          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-[#0B0E11]/90 border border-white/10">
            <div>
              <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest">當前市場狀態 (Market Regime)</div>
              <div className={`text-2xl font-black tracking-tight flex items-center gap-2 mt-0.5 ${mr?.tone === 'emerald' ? 'text-emerald-400' : mr?.tone === 'red' ? 'text-red-400' : 'text-amber-300'}`}>
                <AlertTriangle size={24} />
                {regimeCode} ({regimeLabel})
              </div>
              <div className="text-xs text-gray-400 mt-1 leading-relaxed">
                實測因子：外資期貨淨留倉 <b className="text-white font-mono">{Number(foreignOi).toLocaleString()} 口</b>、台指 VIX <b className="text-purple-400 font-mono">{twVix}</b>、台股站上 60MA 比例 <b className="text-emerald-400 font-mono">{mr?.tw_breadth_60ma ?? '--'}%</b>。
              </div>
            </div>

            <div className="flex flex-wrap md:flex-nowrap gap-2 shrink-0">
              <div className="px-3 py-2 rounded-xl bg-white/5 border border-white/15 text-center min-w-[110px]">
                <span className="text-[9px] font-black text-gray-400 uppercase block">早盤ORB策略</span>
                <span className="text-xs font-black text-amber-300 mt-0.5 block">{orbMode}</span>
              </div>
              <div className="px-3 py-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-center min-w-[110px]">
                <span className="text-[9px] font-black text-gray-400 uppercase block">現金儲備下限</span>
                <span className="text-xs font-black text-amber-300 font-mono mt-0.5 block">🛡️ {cashPct.toFixed(1)}%</span>
              </div>
              <div className="px-3 py-2 rounded-xl bg-blue-500/10 border border-blue-500/30 text-center min-w-[110px]">
                <span className="text-[9px] font-black text-gray-400 uppercase block">股票總曝險上限</span>
                <span className="text-xs font-black text-blue-300 font-mono mt-0.5 block">💼 {equityPct.toFixed(1)}%</span>
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

        {/* 🧬 模組一之二：RSI (Recursive Self-Improvement) 遞迴自我改進實戰驗算面板 */}
        {rsiInfo?.evolution_report && (() => {
          const evo = rsiInfo.evolution_report;
          const attr = evo.attribution || {};
          return (
            <div className="p-5 rounded-2xl bg-emerald-950/20 border border-emerald-500/40 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Zap size={18} className="text-emerald-400" />
                  <span className="text-sm font-black text-emerald-300">
                    🧬 RSI 遞迴自我改進閉環 (Gen 18 ➔ Gen {evo.gen_version} 自動驗證晉升)
                  </span>
                </div>
                <span className="text-xs font-mono text-emerald-200 bg-emerald-500/15 px-2.5 py-0.5 rounded-lg border border-emerald-500/30">
                  實戰驗算帳本：{rsiInfo.total_evaluated?.toLocaleString()} 筆真實買訊 ｜ 嚴選樣本：{evo.evolved_trades?.toLocaleString()} 筆
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-[#0B0E11]/90 border border-white/10">
                  <span className="text-[10px] text-gray-400 block">5 日實戰勝率 & 期望報酬 (扣0.3%成本)</span>
                  <div className="font-mono font-black text-sm text-white mt-1">
                    {evo.baseline_wr_5d}% ➔ <span className="text-emerald-400">{evo.evolved_wr_5d}%</span>
                    <span className="text-amber-300 ml-2">(+{evo.baseline_exp_5d}% ➔ +{evo.evolved_exp_5d}%)</span>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-[#0B0E11]/90 border border-white/10">
                  <span className="text-[10px] text-gray-400 block">20 日波段勝率 & 期望報酬 (扣0.3%成本)</span>
                  <div className="font-mono font-black text-sm text-white mt-1">
                    {evo.baseline_wr_20d}% ➔ <span className="text-emerald-400">{evo.evolved_wr_20d}%</span>
                    <span className="text-amber-300 ml-2">(+{evo.baseline_exp_20d}% ➔ +{evo.evolved_exp_20d}%)</span>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-[#0B0E11]/90 border border-white/10">
                  <span className="text-[10px] text-gray-400 block">AI 自動敗因歸因診斷</span>
                  <div className="font-mono font-bold text-xs text-gray-200 mt-1">
                    三率三升期望值 <b className="text-emerald-400">+{attr.tr_rising_exp20}%</b> vs 無三率 <b className="text-red-400">+{attr.no_tr_exp20}%</b>
                  </div>
                </div>
              </div>

              <div className="text-[11px] text-gray-300 bg-[#0B0E11]/70 p-3 rounded-xl border border-white/5 space-y-1">
                <div className="font-black text-amber-300">⚡ 已驗證有效並直接投入本輪迭代之規則 ({evo.rule_name})：</div>
                {(attr.self_audit_log || []).map((logItem, idx) => (
                  <div key={`audit-${idx}`} className="flex items-center gap-1.5 text-cyan-300 font-mono">
                    <Zap size={12} className="text-cyan-400 shrink-0" />
                    <span>[自動遞迴審計] {logItem}</span>
                  </div>
                ))}
                {(evo.active_rules_injected || []).map((rule, idx) => (
                  <div key={idx} className="flex items-center gap-1.5">
                    <CheckCircle2 size={12} className="text-emerald-400 shrink-0" />
                    <span>{rule}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })()}
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
            <span className="text-[10px] font-black text-amber-400 uppercase tracking-wider block">保命防禦現金池 ({cashPct}%)</span>
            <span className="text-2xl font-black font-mono text-amber-300 mt-1 block">{cashCapital} 萬元</span>
            <span className="text-[10px] text-gray-400 mt-0.5 block">隨大盤 60MA 寬度與 VIX 動態調整，保留低檔接棒彈藥</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-blue-950/30 border border-blue-500/40">
            <span className="text-[10px] font-black text-blue-400 uppercase tracking-wider block">動態平價股票總曝險 ({equityPct}%)</span>
            <span className="text-2xl font-black font-mono text-blue-300 mt-1 block">{equityCapital} 萬元</span>
            <span className="text-[10px] text-gray-400 mt-0.5 block">由 Gen{rsiInfo?.gen_version || 20} 三師聯審高勝率池依反波動率 (ERC) 風險均等化配置</span>
          </div>
          <div className="p-3.5 rounded-2xl bg-emerald-950/30 border border-emerald-500/40 sm:col-span-2 md:col-span-1">
            <span className="text-[10px] font-black text-emerald-400 uppercase tracking-wider block">2027 限制性 ERC 最佳化成效</span>
            <span className="text-2xl font-black font-mono text-emerald-300 mt-1 block">-53.3% 波動降幅</span>
            <span className="text-[10px] text-gray-400 mt-0.5 block">五大低相關板塊由 28.11% 降至 13.13%，分散化比率 1.69</span>
          </div>
        </div>
      </div>

      {/* ⭐ 模組二：2027 正規軍量化推薦參考名單與精準配比 */}
      <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 bg-[#12161A] shadow-xl space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
          <div className="flex items-center gap-2.5">
            <Target size={22} className="text-emerald-400" />
            <div>
              <h3 className="text-base font-black text-white flex items-center gap-2">
                ⭐ 2027 核心推薦參考組合與量化配比
                <span className="text-xs text-gray-400 font-normal">（點選任一檔可即時聯動技術圖表）</span>
              </h3>
              <p className="text-xs text-gray-400">
                以限制性等風險貢獻 (Constrained ERC) 橫跨五大低相關板塊（美股 55.9% ＋ 台股 44.1%），兼顧 2027 成長與極致防禦
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1 p-1 bg-[#1A2026] rounded-xl border border-amber-500/30 text-xs font-black">
              <button
                type="button"
                onClick={() => setUniverseMode('us')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer active:scale-95 ${universeMode === 'us' ? 'bg-amber-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
              >
                🇺🇸 2027 純美股 ERC
              </button>
              <button
                type="button"
                onClick={() => setUniverseMode('cross')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer active:scale-95 ${universeMode === 'cross' ? 'bg-blue-600 text-white shadow' : 'text-gray-400 hover:text-white'}`}
              >
                🌐 2027 台美跨市場
              </button>
            </div>

            <div className="flex items-center gap-1.5 p-1 bg-[#1A2026] rounded-xl border border-white/10 text-xs font-black">
              <button
                type="button"
                onClick={() => handleFilterChange('all')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer active:scale-95 ${filterType === 'all' ? 'bg-sky-600 text-white shadow-md ring-1 ring-sky-400/50' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
              >
                全部標的 ({activeRecs.length})
              </button>
              <button
                type="button"
                onClick={() => handleFilterChange('buy')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer active:scale-95 ${filterType === 'buy' ? 'bg-emerald-600 text-white shadow-md ring-1 ring-emerald-400/50' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
              >
                推薦配置 ({activeRecs.filter(r => r.weightPct > 0).length})
              </button>
              <button
                type="button"
                onClick={() => handleFilterChange('avoid')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer active:scale-95 ${filterType === 'avoid' ? 'bg-red-600 text-white shadow-md ring-1 ring-red-400/50' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
              >
                衛星 / 剔除 ({activeRecs.filter(r => r.weightPct === 0).length})
              </button>
            </div>
          </div>
        </div>

        {/* 推薦卡片列表 */}
        <div ref={cardsGridRef} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
            const allocNtd = totalCapital * 10000 * (effectiveWeight / 100);
            const allocAmount = ((totalCapital * effectiveWeight) / 100).toFixed(1);
            const estShares = livePrice > 0
              ? (rec.market === 'tw'
                  ? Math.max(1, Math.floor(allocNtd / livePrice))
                  : Math.max(1, Math.floor((allocNtd / 32.5) / livePrice)))
              : 0;
            const shareDesc = rec.market === 'tw'
              ? (estShares >= 1000 ? `約 ${(estShares / 1000).toFixed(1)} 張 (${estShares.toLocaleString()}股)` : `約 ${estShares} 股 (盤中零股)`)
              : `約 ${estShares} 股`;
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
                        現價 <b className="text-white">{rec.market === 'tw' ? `NT$${livePrice}` : `US$${livePrice}`}</b>
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
                      {isZero ? '0 萬 (禁止買進)' : `${allocAmount} 萬元（${shareDesc}）`}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-1.5 text-[10px] pt-1">
                    <div className="p-1.5 rounded-lg bg-[#0F1316] text-center border border-white/5">
                      <span className="text-gray-500 block">開盤關鍵價 (二閘)</span>
                      <span className={`font-mono font-bold ${rec.aboveKeyPrice !== false ? 'text-cyan-300' : 'text-amber-300'}`}>
                        {rec.keyPrice ? (rec.market === 'tw' ? `NT$${rec.keyPrice}` : `US$${rec.keyPrice}`) : '--'}
                      </span>
                    </div>
                    <div className="p-1.5 rounded-lg bg-[#0F1316] text-center border border-white/5">
                      <span className="text-gray-500 block">季線防守點 (SL)</span>
                      <span className="font-mono font-bold text-red-400">{rec.market === 'tw' ? `NT$${liveSL}` : `US$${liveSL}`}</span>
                    </div>
                    <div className="p-1.5 rounded-lg bg-[#0F1316] text-center border border-white/5">
                      <span className="text-gray-500 block">預期目標 (TP)</span>
                      <span className="font-mono font-bold text-emerald-400">{liveTP > 0 ? (rec.market === 'tw' ? `NT$${liveTP}` : `US$${liveTP}`) : '無'}</span>
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

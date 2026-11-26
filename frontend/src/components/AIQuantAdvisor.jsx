import React, { useState, useRef } from 'react';
import { 
  ShieldCheck, AlertTriangle, TrendingUp, TrendingDown, Target, 
  Cpu, Zap, PieChart, Coins, ArrowUpRight, CheckCircle2, 
  XCircle, Flame, Layers, Lock, Scale, Calculator, Sliders,
  HelpCircle, Compass, Activity, ArrowRight, DollarSign
} from 'lucide-react';

// Gen 31 Tri-Party Red-Team 2027 Pure US ERC Blueprint (阿村伯 × 顏老師 × Gemini Deep Research 紅隊定案)
const RECOMMENDATIONS_US = [
  {
    symbol: 'SGOV',
    name: 'iShares 0-3月美國短債',
    market: 'us',
    tier: '🛡️ 美元無風險短債堡壘 (28.0%)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【2027 H1 升息＋債務上限核心避風港】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 28.0,
    annualVol: 0.8,
    slPrice: 100.0,
    tpPrice: 105.0,
    currPrice: 100.68,
    highlight: 'Gen 31 紅隊大幅拉高至 28%！12 月升息機率逾 90% 且美債逼近 41.1 兆上限，無風險穩領 4%+ 高息，現金本身就是最強進攻部位。'
  },
  {
    symbol: 'LLY',
    name: 'Eli Lilly 禮來',
    market: 'us',
    tier: '🧬 醫療成長王 (14.0%)',
    tierColor: 'text-teal-300 bg-teal-500/10 border-teal-500/30',
    action: '【穩站年線 +24% / KD 金叉分批】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 14.0,
    annualVol: 23.0,
    slPrice: 1257.77,
    tpPrice: 1680.0,
    currPrice: 1392.22,
    highlight: '近 3 月狂贏納指 +30%！藥品獲美國 301 關稅豁免、完全遠離 AI 債務鏈；嚴守顏老師 KD 金叉止跌分批承接。'
  },
  {
    symbol: 'PGR',
    name: 'Progressive 前進保險',
    market: 'us',
    tier: '🛡️ Gen 31 新星：高利率產險王 (12.0%)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【逆勢大牛市 / 站穩季線與年線】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 12.0,
    annualVol: 19.0,
    slPrice: 221.86,
    tpPrice: 280.0,
    currPrice: 238.70,
    highlight: 'Gen 31 紅隊補進真牛市王者！高利率推升浮存金利息＋通膨賦予保費定價權，大盤重挫期間逆勢大漲 +9.2%、穩站年線 +12.7%。'
  },
  {
    symbol: 'JPM',
    name: 'JPMorgan 摩根大通',
    market: 'us',
    tier: '🏦 高利率大型銀行王者 (10.0%)',
    tierColor: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    action: '【受惠高利率平台 / 等 12/09 站回季線】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 10.0,
    annualVol: 21.0,
    slPrice: 338.55,
    tpPrice: 380.0,
    currPrice: 316.74,
    highlight: '短端利率穩居 4% 以上直接捍衛淨利息收益率 (NIM)，遠離中小型銀行商辦與 Neocloud 債權風險；待 12/09 FOMC 落地確認。'
  },
  {
    symbol: 'ITA',
    name: 'iShares 美國國防航太 ETF',
    market: 'us',
    tier: '✈️ Gen 31 遺珠：取代 XLI (9.0%)',
    tierColor: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    action: '【跨黨派剛性預算 / 301 關稅豁免】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 9.0,
    annualVol: 18.0,
    slPrice: 70.31,
    tpPrice: 82.0,
    currPrice: 68.77,
    highlight: 'Gen 31 紅隊取代已破年線的泛工業 XLI！中東戰事強化防空軍備剛需，航空零組件獲美國 301 關稅豁免，不受分裂國會砍預算威脅。'
  },
  {
    symbol: 'XLE',
    name: '美國能源板塊 ETF',
    market: 'us',
    tier: '🛢️ 通膨與中東戰火對沖 (7.0%)',
    tierColor: 'text-orange-300 bg-orange-500/10 border-orange-500/30',
    action: '【穩站年線 / 待站回季線 64.50】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 7.0,
    annualVol: 24.0,
    slPrice: 64.50,
    tpPrice: 76.0,
    currPrice: 60.90,
    highlight: '波斯灣油輪遇襲風險未除，高盛看 12 月布蘭特 $105（極端 $140），能源是對沖二次停滯性通膨與地緣尾部風險必備盾牌。'
  },
  {
    symbol: 'GLD',
    name: 'SPDR 黃金 ETF',
    market: 'us',
    tier: '🥇 Gen 31 遺珠：債務上限避險 (7.0%)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【清洗槓桿籌碼 / 2027 Q1 測底分批】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 7.0,
    annualVol: 16.0,
    slPrice: 300.0,
    tpPrice: 420.0,
    currPrice: 327.45,
    highlight: '11 月急跌徹底清洗追高籌碼，對比 41.1 兆債務上限與央行購金潮，高盛目標 $4,650、瑞銀看 $5,000，2027 Q1 升息測底分批低接。'
  },
  {
    symbol: 'COPX',
    name: 'Global X 全球銅礦 ETF',
    market: 'us',
    tier: '⚡ Gen 31 遺珠：免選邊站電氣化 (5.0%)',
    tierColor: 'text-orange-300 bg-orange-500/10 border-orange-500/30',
    action: '【電網升級剛需 / 避開晶片戰選邊】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 5.0,
    annualVol: 28.0,
    slPrice: 52.0,
    tpPrice: 78.0,
    currPrice: 58.66,
    highlight: '無論 2027 是 GPU 還是 ASIC 勝出，全球電網升級與變壓器擴容都無法繞開實體銅剛需，完美避開算力硬體折舊與違約風險。'
  },
  {
    symbol: 'AVGO',
    name: 'Broadcom 博通',
    market: 'us',
    tier: '🚀 AI 客製化 ASIC 收費站 (5.0%)',
    tierColor: 'text-indigo-300 bg-indigo-500/10 border-indigo-500/30',
    action: '【右側站回 60MA 季線 343.15 回補】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 5.0,
    annualVol: 36.0,
    slPrice: 343.15,
    tpPrice: 400.0,
    currPrice: 300.86,
    highlight: 'SemiAnalysis 模型中抗震度最高！鎖定雲端巨頭自研推論 ASIC 與高信用客群，待站回 60MA 季線右側承接。'
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft 微軟',
    market: 'us',
    tier: '🟡 黃牌降權：AI 軟體變現 (3.0%)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【上半年折舊與 CDS 承壓 / 下半年看 Agent】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 3.0,
    annualVol: 22.0,
    slPrice: 515.84,
    tpPrice: 600.0,
    currPrice: 489.93,
    highlight: '【Gen 31 黃牌警示】雖穩守年線且受惠推論降價，但名列 CDS 創高科技籃子且上半年折舊沉重，降權至 3%，下半年見 Agent 付費加速再加碼。'
  },
  {
    symbol: 'CEG',
    name: 'Constellation 核能電力',
    market: 'us',
    tier: '🚨 Gen 31 紅隊剔除 (55% 無長約)',
    tierColor: 'text-red-400 bg-red-500/20 border-red-500/40',
    action: '【AI 電力需求砍 34% / 深破年線 -15%】',
    actionColor: 'text-red-400 bg-red-600/30 border-red-500/50',
    weightPct: 0.0,
    annualVol: 24.0,
    slPrice: 268.01,
    tpPrice: 294.0,
    currPrice: 235.28,
    highlight: '【Gen 31 紅隊審計剔除】2032 前尚有 55% 基荷無長約、美國 5.8 GW 資料中心延後且德州喊停新建，恐引爆二次殺估值！'
  },
  {
    symbol: 'ASML',
    name: 'ASML 艾司摩爾',
    market: 'us',
    tier: '⚠️ Gen 31 降級觀察 (深破年線 -18.6%)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【近 3 月跌 -23% / 待站回季線再看】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 0.0,
    annualVol: 34.0,
    slPrice: 1619.73,
    tpPrice: 1629.0,
    currPrice: 1303.08,
    highlight: '半導體設備受關稅與總晶圓面積微調壓抑，深跌破年線為原組合最弱；嚴守 Gen 31 憲法，站回季線前不佔用核心倉位。'
  },
  {
    symbol: 'NVDA',
    name: 'NVIDIA 輝達',
    market: 'us',
    tier: '⚠️ 16 天事件觀察池 (衛星 ≤5%)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【GPU 租金腰斬 / 盯 12/03 聽證會】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 0.0,
    annualVol: 45.8,
    slPrice: 206.48,
    tpPrice: 187.0,
    currPrice: 149.30,
    highlight: '近 3 月重挫 -31%！GPU 租金下滑＋CDS 創高＋標普負面觀察，靜待 12/03 聽證會無毀滅禁令且站穩 20EMA 再評估。'
  },
  {
    symbol: 'WMT',
    name: 'Walmart 沃爾瑪',
    market: 'us',
    tier: '🚨 高估值防禦警示 (PE 45.7x)',
    tierColor: 'text-red-400 bg-red-500/20 border-red-500/40',
    action: '【Gen 31 估值安全閥 / 勿追高】',
    actionColor: 'text-red-400 bg-red-600/30 border-red-500/50',
    weightPct: 0.0,
    annualVol: 19.5,
    slPrice: 116.21,
    tpPrice: 145.0,
    currPrice: 131.94,
    highlight: '【Gen 31 紅隊閥】本益比高達 45.7 倍，防禦籌碼過度擁擠，避險資金改停泊 SGOV 與 PGR 產險更安全！'
  }
];

// Gen 31 Tri-Party Red-Team 2027 Cross-Market TW+US Constrained ERC Blueprint
const RECOMMENDATIONS_CROSS = [
  {
    symbol: 'SGOV',
    name: 'iShares 0-3月美短債',
    market: 'us',
    tier: '🛡️ 美元無風險短債堡壘 (25.0%)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【取代低成長電信與高估值消費 / 領 4%+ 息】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 25.0,
    annualVol: 0.8,
    slPrice: 100.0,
    tpPrice: 105.0,
    currPrice: 100.68,
    highlight: 'Gen 31 紅隊核心修正！當 3 個月美債穩領 4%+ 息且美元強勢，持有低成長台幣電信股機會成本遠輸 SGOV，上半年以短債穩守本金。'
  },
  {
    symbol: '2330.TW',
    name: '台積電',
    market: 'tw',
    tier: '🏆 AI 雙陣營收費站 (10.0%)',
    tierColor: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    action: '【232 零關稅豁免 / 右側站回季線加碼】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 10.0,
    annualVol: 30.0,
    slPrice: 2386.47,
    tpPrice: 2680.0,
    currPrice: 2145.0,
    highlight: '通吃 GPU 與 ASIC 兩大陣營 CoWoS 產能，2027 N2 產能翻倍且享美國 232 條款零關稅豁免，12/04 川普動工＋站回季線即右側佈局。'
  },
  {
    symbol: 'LLY',
    name: 'Eli Lilly 禮來',
    market: 'us',
    tier: '🧬 醫療生技成長引擎 (10.0%)',
    tierColor: 'text-teal-300 bg-teal-500/10 border-teal-500/30',
    action: '【穩站年線 +24% / 301 藥品豁免】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 10.0,
    annualVol: 23.0,
    slPrice: 1257.77,
    tpPrice: 1680.0,
    currPrice: 1392.22,
    highlight: '藥品名列美國 301 關稅豁免清單，完全遠離 AI 債務融資風暴，嚴守 KD 金叉分批承接。'
  },
  {
    symbol: 'PGR',
    name: 'Progressive 前進保險',
    market: 'us',
    tier: '🛡️ Gen 31 新星：高利率產險王 (10.0%)',
    tierColor: 'text-emerald-300 bg-emerald-500/10 border-emerald-500/30',
    action: '【逆勢大牛市 / 站穩季線與年線】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 10.0,
    annualVol: 19.0,
    slPrice: 221.86,
    tpPrice: 280.0,
    currPrice: 238.70,
    highlight: '高利率浮存金與通膨保費重定價雙受惠，大盤崩跌時穩站年線 +12.7% 的真多頭！'
  },
  {
    symbol: '2886.TW',
    name: '兆豐金',
    market: 'tw',
    tier: '🏦 純銀行官股金控防雷 (10.0%)',
    tierColor: 'text-blue-300 bg-blue-500/10 border-blue-500/30',
    action: '【投信大買 +3萬張 / 避壽險地雷】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 10.0,
    annualVol: 14.5,
    slPrice: 38.5,
    tpPrice: 46.0,
    currPrice: 40.5,
    highlight: '純銀行官股金控避開壽險美債跌價壓力，11/26 獲投信單日大買 +30,606 張，高利率環境淨利息收入穩健。'
  },
  {
    symbol: 'ITA',
    name: 'iShares 美國國防航太 ETF',
    market: 'us',
    tier: '✈️ Gen 31 遺珠：取代 XLI (8.0%)',
    tierColor: 'text-amber-300 bg-amber-500/10 border-amber-500/30',
    action: '【跨黨派預算 / 航空關稅豁免】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 8.0,
    annualVol: 18.0,
    slPrice: 70.31,
    tpPrice: 82.0,
    currPrice: 68.77,
    highlight: '取代已破年線的 XLI！中東戰事推升國防剛需，航空零組件獲美國 301 關稅明確豁免。'
  },
  {
    symbol: 'GLD',
    name: 'SPDR 黃金 ETF',
    market: 'us',
    tier: '🥇 Gen 31 遺珠：債務上限避險 (7.0%)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【2027 Q1 升息測底分批低接】',
    actionColor: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    weightPct: 7.0,
    annualVol: 16.0,
    slPrice: 300.0,
    tpPrice: 420.0,
    currPrice: 327.45,
    highlight: '11 月清洗槓桿籌碼後，高盛目標 $4,650、瑞銀看 $5,000，鎖定美國 41.1 兆債務上限危機的終極避險修復空間。'
  },
  {
    symbol: 'COPX',
    name: 'Global X 全球銅礦 ETF',
    market: 'us',
    tier: '⚡ Gen 31 遺珠：電網銅剛需 (5.0%)',
    tierColor: 'text-orange-300 bg-orange-500/10 border-orange-500/30',
    action: '【免選邊站電氣化 / 分批承接】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 5.0,
    annualVol: 28.0,
    slPrice: 52.0,
    tpPrice: 78.0,
    currPrice: 58.66,
    highlight: '瑞銀 2027 展望與黃金並列核心多元化資產，不論 GPU 或 ASIC 誰贏，電網升級都離不開實體銅。'
  },
  {
    symbol: 'JPM',
    name: 'JPMorgan 摩根大通',
    market: 'us',
    tier: '🇺🇸 美股高利率金融龍頭 (5.0%)',
    tierColor: 'text-sky-300 bg-sky-500/10 border-sky-500/30',
    action: '【待 12/09 FOMC 落地確認】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 5.0,
    annualVol: 21.0,
    slPrice: 338.55,
    tpPrice: 380.0,
    currPrice: 316.74,
    highlight: '2027 淨利息收入指引 1,070 億美元，直接受惠高利率平台。'
  },
  {
    symbol: 'AVGO',
    name: 'Broadcom 博通',
    market: 'us',
    tier: '🚀 AI 客製化 ASIC 收費站 (5.0%)',
    tierColor: 'text-pink-300 bg-pink-500/10 border-pink-500/30',
    action: '【右側站回 60MA 季線 343.15 回補】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 5.0,
    annualVol: 36.0,
    slPrice: 343.15,
    tpPrice: 400.0,
    currPrice: 300.86,
    highlight: '2027 客製化推論 ASIC 龍頭，66.5% 高毛利＋雲端大廠高信用客群，站回季線即右側承接。'
  },
  {
    symbol: '2308.TW',
    name: '台達電',
    market: 'tw',
    tier: '⚡ AI 高壓電源與電網儲能 (5.0%)',
    tierColor: 'text-lime-300 bg-lime-500/10 border-lime-500/30',
    action: '【避開越南關稅雷 / 待站回季線】',
    actionColor: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
    weightPct: 5.0,
    annualVol: 35.0,
    slPrice: 1593.33,
    tpPrice: 1650.0,
    currPrice: 990.0,
    highlight: '全球布局分散關稅風險，兼具電源、液冷與電網儲能，嚴禁左側接刀，待站回季線右側承接。'
  },
  {
    symbol: '3017.TW',
    name: '奇鋐',
    market: 'tw',
    tier: '🚨 Gen 31 紅隊警示：越南 35% 關稅雷',
    tierColor: 'text-red-400 bg-red-500/20 border-red-500/40',
    action: '【擴產五成在越南 / 等 1/25 聽證會】',
    actionColor: 'text-red-400 bg-red-600/30 border-red-500/50',
    weightPct: 0.0,
    annualVol: 42.0,
    slPrice: 3131.1,
    tpPrice: 3200.0,
    currPrice: 2795.0,
    highlight: '【Gen 31 紅隊抓漏】雖獲利強勁 PE 僅 12.5x，但 2027 擴產五成基地在越南，正撞 USTR 301 越南最高 35% 重稅，未獲豁免前絕不追漲停！'
  },
  {
    symbol: 'CEG',
    name: 'Constellation 核電',
    market: 'us',
    tier: '🚨 Gen 31 紅隊剔除 (55% 無長約)',
    tierColor: 'text-red-400 bg-red-500/20 border-red-500/40',
    action: '【AI 電力需求砍 34% / 深破年線】',
    actionColor: 'text-red-400 bg-red-600/30 border-red-500/50',
    weightPct: 0.0,
    annualVol: 24.0,
    slPrice: 268.01,
    tpPrice: 294.0,
    currPrice: 235.28,
    highlight: '【Gen 31 紅隊審計剔除】2032 前 55% 基荷無長約＋美國 5.8 GW 資料中心延後，恐引爆二次殺估值！'
  },
  {
    symbol: 'NVDA',
    name: '輝達',
    market: 'us',
    tier: '⚠️ 16 天事件觀察池 (衛星 ≤5%)',
    tierColor: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/30',
    action: '【盯 12/03 聽證會與 CDS 止穩】',
    actionColor: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
    weightPct: 0.0,
    annualVol: 45.8,
    slPrice: 206.48,
    tpPrice: 187.0,
    currPrice: 149.30,
    highlight: 'GPU 租金下滑＋CDS 創高，靜待 12/03 聽證會與 12/09 FOMC 落地且站穩 20EMA 再評估。'
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

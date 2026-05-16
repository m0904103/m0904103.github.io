import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Search, 
  Bell, 
  Settings, 
  BarChart3,
  ShieldAlert,
  ChevronRight,
  CheckCircle2,
  PieChart as PieIcon,
  Zap,
  Target,
  Wind,
  ShieldCheck,
  AlertTriangle,
  ArrowUpRight,
  RefreshCw,
  Info,
  Clock,
  MousePointer2,
  Quote,
  LayoutGrid
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import TradingChart from './components/TradingChart';
import InvestmentChecklist from './components/InvestmentChecklist';
import SectorHeatmap from './components/SectorHeatmap';
import StrategyBoard from './components/StrategyBoard';

const IS_PROD = window.location.hostname.includes('github.io');
const API_BASE = IS_PROD ? '.' : (import.meta.env.VITE_API_URL || "http://localhost:8000");
const RENDER_API_URL = "https://m0904103-github-io.onrender.com";

function App() {
  const [stocks, setStocks] = useState({ tw: [], us: [] });
  const [indices, setIndices] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedStock, setSelectedStock] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [systemStatus, setSystemStatus] = useState("online");
  const [activeMarket, setActiveMarket] = useState(() => {
    const hour = new Date().getHours();
    return (hour >= 8 && hour < 18) ? "tw" : "us";
  });
  const [activeTab, setActiveTab] = useState("regular"); // regular, intraday
  const [selectedSector, setSelectedSector] = useState(null);
  const [journalEntries, setJournalEntries] = useState(() => {
    const saved = localStorage.getItem('sensei_journal');
    return saved ? JSON.parse(saved) : {};
  });

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // 30s update
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setSystemStatus("connecting");
    try {
      const timestamp = new Date().getTime();
      const scanUrl = IS_PROD ? `${API_BASE}/scan_results.json?t=${timestamp}` : `${API_BASE}/scan`;
      // Always fetch indices from Render Cloud for 24/7 real-time data
      const indexUrl = `${RENDER_API_URL}/indices?t=${timestamp}`;

      const [scanRes, indexRes] = await Promise.all([
        axios.get(scanUrl),
        axios.get(indexUrl)
      ]);

      let stockData = scanRes.data;
      // Normalize data structure for Prod/Dev consistency
      if (stockData.stocks) {
        const tw = stockData.stocks.filter(s => s.market === 'tw');
        const us = stockData.stocks.filter(s => s.market === 'us');
        stockData = { tw, us };
      }

      setStocks(stockData || { tw: [], us: [] });
      setIndices(indexRes.data || {});
      setLastUpdated(new Date());
      setSystemStatus("online");
      
      // Removed auto-select AAPL logic to prevent default jumps
      // const currentMarketData = stockData[activeMarket] || [];
      // if (!selectedStock && currentMarketData.length > 0) {
      //   handleSelectStock(currentMarketData[0]);
      // }
      setLoading(false);
    } catch (err) {
      console.error("Fetch error:", err);
      setSystemStatus("error");
      setLoading(false);
    }
  };

  const handleSelectSector = (sectorName) => {
    if (!sectorName) {
      setSelectedSector(null);
      return;
    }
    
    const trimmedSector = sectorName.trim();
    setSelectedSector(trimmedSector);
    
    // Check if current market has stocks in this sector
    const currentMarketStocks = activeMarket === 'tw' ? stocks.tw : stocks.us;
    const hasInCurrent = currentMarketStocks.some(s => s.sector?.trim() === trimmedSector);
    
    if (!hasInCurrent) {
      const otherMarket = activeMarket === 'tw' ? 'us' : 'tw';
      const otherMarketStocks = otherMarket === 'tw' ? stocks.tw : stocks.us;
      const hasInOther = otherMarketStocks.some(s => s.sector?.trim() === trimmedSector);
      
      if (hasInOther) {
        setActiveMarket(otherMarket);
      }
    }
  };

  const handleSelectStock = async (stock) => {
    // Auto-switch market tab if needed
    if (stock.market && stock.market !== activeMarket) {
      setActiveMarket(stock.market);
    }
    
    setSelectedStock(stock);
    
    // Smooth scroll to chart/detail
    setTimeout(() => {
      const element = document.getElementById('trading-chart');
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);

    try {
      const historyUrl = IS_PROD 
        ? `${API_BASE}/assets/history_${stock.symbol}.json` 
        : `${API_BASE}/history/${stock.symbol}`;
      const res = await axios.get(historyUrl);
      setHistoryData(res.data);
    } catch (err) {
      setHistoryData([]); 
    }
  };

  const getSignalStyle = (signal) => {
    if (signal?.includes("Strong Buy") || signal === "Buy") return "text-red-500 bg-red-500/10 border-red-500/20";
    if (signal?.includes("Strong Sell") || signal === "Sell") return "text-green-500 bg-green-500/10 border-green-500/20";
    return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
  };

  const calculateRegularArmyScore = (stock) => {
    if (!stock) return 0;
    let score = 0;
    
    // 1. Price above MA60 (Core Principle)
    if (stock.close > stock.ma60) score += 50;
    
    // 2. Trend Score (Aggregated sentiment)
    score += (stock.trend_score || 0) / 10;
    
    // 3. RSI Health (Not overbought, not oversold)
    if (stock.rsi >= 40 && stock.rsi <= 70) score += 20;
    else if (stock.rsi > 70) score += 10; // Overbought but strong
    
    // 4. Volume Confirmation
    if (stock.vol_ratio > 1.0) score += 20;
    else score += (stock.vol_ratio || 0) * 10;
    
    return Math.min(100, Math.round(score));
  };

  const currentStocks = (activeMarket === "tw" ? stocks?.tw : stocks?.us) || [];
  
  // Filter for Regular Army (standing above MA60)
  const regularArmy = currentStocks.filter(s => s.is_regular || s.close > s.ma60);
  
  // Filter for Day Trading (high volatility/volume)
  const intradayStocks = currentStocks.filter(s => s.vol_ratio > 1.2 || s.tactical_score > 6);

  // Filter for Forbidden Zone (fallen below MA60)
  const forbiddenStocks = currentStocks.filter(s => !s.is_regular && s.close < s.ma60);

  const baseStocks = (searchTerm || selectedSector)
    ? currentStocks 
    : (activeTab === "regular" 
        ? regularArmy 
        : (activeTab === "intraday" ? intradayStocks : forbiddenStocks));

  const displayStocks = baseStocks
    .filter(s => {
      const matchSearch = s?.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          s?.name?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchSector = selectedSector ? s.sector?.trim() === selectedSector.trim() : true;
      return matchSearch && matchSector;
    })
    .sort((a, b) => {
      // 1. Strong Buy first
      const aIsStrongBuy = a.signal === 'Strong Buy' ? 1 : 0;
      const bIsStrongBuy = b.signal === 'Strong Buy' ? 1 : 0;
      if (aIsStrongBuy !== bIsStrongBuy) {
        return bIsStrongBuy - aIsStrongBuy; // Descending (1 comes before 0)
      }
      
      // 2. 最適買進做多價位的切入點 (Optimal Entry Point) - 降序排列
      // Optimal entry is when price is just above MA60. 
      // Proximity Score = (MA60 / Close). Closer to 1.0 means closer to support (safer entry).
      // Descending order of Proximity Score means the safest/most optimal entries are at the top.
      const aProximity = a.close > 0 ? (a.ma60 / a.close) : 0;
      const bProximity = b.close > 0 ? (b.ma60 / b.close) : 0;
      
      return bProximity - aProximity;
    });

  const renderWeatherStation = () => {
    const fearGreed = indices.fear_greed?.value || 50;
    const vix = indices["VIX (恐慌)"]?.close || 15;
    const twVix = indices["台指VIX (波動率)"]?.close || 15;
    const adr = indices.adr_premium?.close || 0;
    
    // Dynamic Cash Suggestion based on Dual VIX and Course Principles
    let suggestedCash = 30;
    const maxVix = Math.max(vix, twVix);
    if (maxVix > 18) suggestedCash = 40;
    if (maxVix > 25) suggestedCash = 50;
    if (maxVix > 35 || fearGreed > 90) suggestedCash = 70; // Extreme Defense Mode
    if (indices.suggested_cash) suggestedCash = indices.suggested_cash;

    // Check main indices status
    const isSPYBull = indices["美股標普"]?.is_bull;
    const isTWIIBull = indices["台股加權"]?.is_bull;

    // Sensei's Wisdom (顏老師的叮嚀)
    let wisdom = "大盤均線多頭架構尚在，保持紀律操作。";
    
    // Logic based on market trend
    if (isSPYBull === false && isTWIIBull === false) {
        wisdom = "「警告：全球多頭架構破壞」：標普與台股均跌破 MA60 生命線！進入防禦模式，嚴格執行減碼，保護本金為最高準則。";
    } else if (isTWIIBull === false) {
        wisdom = "「警報：台股均線轉弱」：台股目前跌破 MA60，美股尚在支撐上。台股部位需嚴格控管，切勿在生命線之下攤平。";
    }

    // Override with volatility/greed warnings
    if (twVix > 22) wisdom = "「警報：本土恐慌升溫」：台指 VIX 異常走高，內資情緒不穩。此時應優先檢視台股部位，守住生命線，不輕易加碼。";
    if (vix > 18 && vix <= 25) wisdom = "「盤中震盪加劇是散戶的毒藥，卻是正規軍的試金石。」：VIX 升溫，當下切勿急躁追高，建議調升現金比例，耐心等待支撐確認。";
    if (adr < -1) wisdom = "「外資的態度藏在溢價裡」：TSM ADR 呈現折價，注意開盤科技股賣壓，切勿追價，寧可錯過不可做錯。";
    if (fearGreed > 80) wisdom = "「人取我棄，鎖住人性」：市場進入極端貪婪區，切勿聽信市場喧嘩。觀望不動，本身就是一種高階決策。";
    if (maxVix > 25) wisdom = "「保命第一，留得青山在」：高度警戒區！雙 VIX 噴發！嚴禁摸底，強制執行季線停損紀律，跌破 MA60 的標的一律砍倉。";
    if (maxVix > 35) wisdom = "「最高級別紅色警戒：市場系統性崩潰風險」：台指 VIX 突破 35！這已非正常震盪，而是極端恐慌拋售。請立即執行清倉式防禦，保留 70% 現金，觀望不動是您現在最高階的決策！";

    return (
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Fear & Greed */}
          <div className="glass rounded-2xl p-4 flex flex-col justify-between border-l-4 border-l-orange-500">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">市場情緒指標</span>
              <Wind size={16} className="text-orange-500" />
            </div>
            <div className="mt-2">
              <div className="text-3xl font-black text-white">{fearGreed}</div>
              <div className="text-[10px] font-bold text-orange-400 uppercase">{indices.fear_greed?.sentiment || "Neutral"}</div>
            </div>
            <div className="w-full bg-gray-800 h-1.5 rounded-full mt-3 overflow-hidden">
              <div className="bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 h-full" style={{ width: `${fearGreed}%` }}></div>
            </div>
          </div>

          {/* VIX Risk */}
          <div className="glass rounded-2xl p-4 flex flex-col justify-between border-l-4 border-l-red-500">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">VIX 波動率監測</span>
              <ShieldAlert size={16} className={vix > 20 ? "text-red-500 animate-pulse" : "text-green-500"} />
            </div>
            <div className="mt-2">
              <div className="text-3xl font-black text-white">{vix}</div>
              <div className="text-[10px] font-bold text-gray-400">{vix > 20 ? "高風險：謹慎縮減部位" : "穩定：適合正規軍操作"}</div>
            </div>
            <div className="flex items-center mt-3 space-x-1">
               {[...Array(5)].map((_, i) => (
                  <div key={i} className={`h-1.5 flex-1 rounded-full ${i < (vix/10) ? 'bg-red-500' : 'bg-gray-800'}`}></div>
               ))}
            </div>
          </div>

          {/* TW VIX Risk */}
          <div className="glass rounded-2xl p-4 flex flex-col justify-between border-l-4 border-l-purple-500">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">台指 VIX 監測</span>
              <ShieldAlert size={16} className={twVix > 18 ? "text-purple-500 animate-pulse" : "text-green-500"} />
            </div>
            <div className="mt-2">
              <div className="text-3xl font-black text-white">{twVix}</div>
              <div className="text-[10px] font-bold text-gray-400">{twVix > 18 ? "內資恐慌中：防範本土賣壓" : "穩定：適合正規軍操作"}</div>
            </div>
            <div className="flex items-center mt-3 space-x-1">
               {[...Array(5)].map((_, i) => (
                  <div key={i} className={`h-1.5 flex-1 rounded-full ${i < (twVix/8) ? 'bg-purple-500' : 'bg-gray-800'}`}></div>
               ))}
            </div>
          </div>

          {/* ADR Premium */}
          <div className="glass rounded-2xl p-4 flex flex-col justify-between border-l-4 border-l-blue-500">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">TSM ADR 溢價</span>
              <RefreshCw size={16} className="text-blue-500" />
            </div>
            <div className="mt-2">
              <div className="text-3xl font-black text-white">{adr}%</div>
              <div className="text-[10px] font-bold text-blue-400 uppercase">{adr > 0 ? "領先溢價" : "折價收斂"}</div>
            </div>
            <p className="text-[9px] text-gray-500 mt-2 italic">台股開盤強弱關鍵指標</p>
          </div>

          {/* Suggested Cash */}
          <div className="glass rounded-2xl p-4 flex flex-col justify-between border-l-4 border-l-green-500">
            <div className="flex justify-between items-start">
              <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">建議救命錢 (Cash %)</span>
              <ShieldCheck size={16} className="text-green-500" />
            </div>
            <div className="mt-2">
              <div className="text-3xl font-black text-white">{suggestedCash}%</div>
              <div className="text-[10px] font-bold text-green-400 uppercase tracking-tighter italic">"紀律是最高階的進攻"</div>
            </div>
            <div className="flex items-center space-x-2 mt-3">
               <div className="flex-1 bg-gray-800 h-2 rounded-full relative">
                  <div className="absolute left-0 top-0 h-full bg-green-500 rounded-full" style={{ width: `${suggestedCash}%` }}></div>
               </div>
            </div>
          </div>
        </div>
        
        {/* Sensei's Wisdom Bar - Integrated into Heatmap flow or separate */}
        <div id="sensei-wisdom" className="mt-4 glass-light rounded-2xl p-4 flex items-center border border-white/5 bg-gradient-to-r from-yellow-500/5 to-transparent animate-in fade-in slide-in-from-top-4 duration-700">
          <Quote size={18} className="text-yellow-500 mr-3 flex-shrink-0" />
          <div className="flex flex-col md:flex-row md:items-center gap-2">
            <span className="text-[10px] font-black text-yellow-500 uppercase tracking-widest whitespace-nowrap">顏老師：</span>
            <span className="text-xs md:text-sm font-black text-gray-100 italic">"{wisdom}"</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#0B0E11] text-gray-200 flex flex-col font-sans selection:bg-red-500/30">
      <header className="glass border-b border-white/5 px-4 md:px-6 py-4 flex flex-col md:flex-row items-center justify-between sticky top-0 z-50 pt-[env(safe-area-inset-top)]">
        <div className="flex items-center justify-between w-full md:w-auto mb-4 md:mb-0">
          <div className="flex items-center space-x-3">
            <div className="bg-red-600 p-2 rounded-xl shadow-lg shadow-red-500/20">
              <BarChart3 className="text-white" size={20} />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-black tracking-tighter text-white italic uppercase leading-none">
                <span className="text-red-500">Regular Army</span> Command
              </h1>
              <div className="flex items-center mt-1">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                <span className="text-[9px] md:text-[10px] font-bold text-gray-500 uppercase tracking-widest">資訊工具化與量化紀律系統</span>
              </div>
            </div>
          </div>
          <div className="flex md:hidden space-x-4">
             <Bell className="text-gray-500" size={20} />
             <Settings className="text-gray-500" size={20} />
          </div>
        </div>

        <div className="flex-1 w-full max-w-2xl md:mx-12 mb-4 md:mb-0">
          <div className="relative group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-red-500 transition-colors" size={18} />
            <input 
              type="text" 
              placeholder="搜尋標的代號 (e.g. 2330, NVDA)..."
              className="w-full bg-[#1E2329] border border-white/5 rounded-2xl py-2.5 md:py-3 pl-11 pr-4 text-sm focus:ring-2 focus:ring-red-500/50 outline-none transition-all"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="hidden md:flex items-center space-x-6">
          <div className="flex bg-[#161A1E] p-1 rounded-xl border border-white/5">
            <button 
              onClick={() => setActiveMarket("tw")}
              className={`px-4 py-1.5 text-xs font-black rounded-lg transition-all ${activeMarket === 'tw' ? 'bg-red-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
            >
              🇹🇼 TAIWAN
            </button>
            <button 
              onClick={() => setActiveMarket("us")}
              className={`px-4 py-1.5 text-xs font-black rounded-lg transition-all ${activeMarket === 'us' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
            >
              🇺🇸 USA
            </button>
          </div>
          <Bell className="text-gray-500 cursor-pointer hover:text-white transition-colors" size={20} />
          <Settings className="text-gray-500 cursor-pointer hover:text-white transition-colors" size={20} />
        </div>

        {/* Mobile Market Selector */}
        <div className="flex md:hidden w-full bg-[#161A1E] p-1 rounded-xl border border-white/5">
          <button 
            onClick={() => setActiveMarket("tw")}
            className={`flex-1 py-2 text-[10px] font-black rounded-lg transition-all ${activeMarket === 'tw' ? 'bg-red-600 text-white shadow-lg' : 'text-gray-500'}`}
          >
            🇹🇼 TAIWAN
          </button>
          <button 
            onClick={() => setActiveMarket("us")}
            className={`flex-1 py-2 text-[10px] font-black rounded-lg transition-all ${activeMarket === 'us' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-500'}`}
          >
            🇺🇸 USA
          </button>
        </div>
      </header>

      <main className="flex-1 p-4 md:p-6 flex flex-col max-w-[1600px] mx-auto w-full">
        {/* Consolidated Header Dashboard */}
        <section className="mb-6 md:mb-8">
           <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-6 overflow-x-auto no-scrollbar pb-1">
                 <button 
                  onClick={() => document.getElementById('weather-station')?.scrollIntoView({ behavior: 'smooth' })}
                  className="text-[10px] md:text-[11px] font-black text-white border-b-2 border-red-500 pb-1 whitespace-nowrap hover:text-red-400 transition-colors"
                 >
                   🌟 戰情儀表板
                 </button>
                 <button 
                  onClick={() => document.getElementById('sector-heatmap')?.scrollIntoView({ behavior: 'smooth' })}
                  className="text-[10px] md:text-[11px] font-black text-gray-500 hover:text-red-500 pb-1 whitespace-nowrap transition-colors"
                 >
                   📊 產業分佈
                 </button>
                 <button 
                  onClick={() => document.getElementById('sensei-wisdom')?.scrollIntoView({ behavior: 'smooth' })}
                  className="text-[10px] md:text-[11px] font-black text-gray-500 hover:text-yellow-500 pb-1 whitespace-nowrap transition-colors"
                 >
                   🏛️ 顏師語錄
                 </button>
              </div>
              <div className="hidden md:flex items-center text-[8px] font-bold opacity-30 uppercase tracking-widest">
                 <Clock size={10} className="mr-1" /> Last Sync: {lastUpdated.toLocaleTimeString()}
                 <div className={`ml-2 w-2 h-2 rounded-full ${new Date() - lastUpdated < 120000 ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              </div>
           </div>
           
           <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
              <div id="weather-station" className="xl:col-span-8">
                 {renderWeatherStation()}
              </div>
              <div id="sector-heatmap" className="xl:col-span-4">
                 <SectorHeatmap 
                  stocks={[...stocks.tw, ...stocks.us]} 
                  onSelectSector={handleSelectSector}
                  activeSector={selectedSector}
                 />
              </div>
           </div>

           {/* 2026 Sector Strategy Board */}
           <StrategyBoard 
             stocks={[...stocks.tw, ...stocks.us]} 
             onSelectStock={handleSelectStock} 
           />
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
          {/* Section 2 & 3: Signals Column */}
          <aside className="lg:col-span-4 flex flex-col glass rounded-3xl overflow-hidden border border-white/5 h-[400px] lg:h-[calc(100vh-280px)]">
            <div className="p-3 bg-[#161A1E] border-b border-white/5 flex items-center justify-between">
              <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest">
                {selectedSector ? `族群: ${selectedSector}` : '全市場監控'}
              </span>
              {selectedSector && (
                <button 
                  onClick={() => setSelectedSector(null)}
                  className="text-[9px] font-black text-red-500 hover:text-red-400 uppercase"
                >
                  清除篩選
                </button>
              )}
            </div>

            <div className="p-1 bg-[#1E2329] flex border-b border-white/5">
              <button 
                onClick={() => setActiveTab("regular")}
                className={`flex-1 py-3 text-[10px] md:text-xs font-black flex items-center justify-center transition-all ${activeTab === 'regular' ? 'text-red-500 bg-[#161A1E]' : 'text-gray-500'}`}
              >
                <ShieldCheck size={14} className="mr-2" /> 正規軍核心
              </button>
              <button 
                onClick={() => setActiveTab("intraday")}
                className={`flex-1 py-3 text-[10px] md:text-xs font-black flex items-center justify-center transition-all border-l border-white/5 ${activeTab === 'intraday' ? 'text-orange-500 bg-[#161A1E]' : 'text-gray-500'}`}
              >
                <Zap size={14} className="mr-2" /> 動能轉強
              </button>
              <button 
                onClick={() => setActiveTab("forbidden")}
                className={`flex-1 py-3 text-[10px] md:text-xs font-black flex items-center justify-center transition-all border-l border-white/5 ${activeTab === 'forbidden' ? 'text-gray-400 bg-[#161A1E]' : 'text-gray-600'}`}
              >
                <AlertTriangle size={14} className="mr-1 md:mr-2" /> 空頭禁區
              </button>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
              {loading ? (
                <div className="p-8 text-center animate-pulse text-gray-500 italic">正在接收衛星數據...</div>
              ) : displayStocks.length === 0 ? (
                <div className="p-8 text-center text-gray-600">無符合條件之標的</div>
              ) : (
                displayStocks.map(stock => {
                  const isAboveMA60 = stock.close > stock.ma60;
                  return (
                    <div 
                      key={stock.symbol}
                      onClick={() => {
                        handleSelectStock(stock);
                        if (window.innerWidth < 1024) {
                          window.scrollTo({ top: document.querySelector('#stock-details').offsetTop - 100, behavior: 'smooth' });
                        }
                      }}
                      className={`p-4 rounded-2xl cursor-pointer transition-all border group active:scale-[0.98] ${
                        !isAboveMA60 ? 
                          selectedStock?.symbol === stock.symbol ? 'bg-[#10B981]/10 border-[#10B981]/30 ring-1 ring-[#10B981]/30' : 'bg-[#10B981]/5 border-[#10B981]/10 hover:border-[#10B981]/30'
                        : 
                          selectedStock?.symbol === stock.symbol ? 'bg-red-500/5 border-red-500/20 ring-1 ring-red-500/30' : 'bg-white/5 border-transparent hover:border-white/10'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex flex-col">
                          <span className={`text-lg md:text-xl font-black tracking-tighter transition-colors ${!isAboveMA60 ? 'text-gray-300 group-hover:text-[#10B981]' : 'text-white group-hover:text-red-500'}`}>
                            {stock.symbol.replace('.TW', '')} {stock.name}
                          </span>
                          <span className="text-[9px] md:text-[10px] text-gray-500 font-bold opacity-0 h-0">.</span>
                        </div>
                        <div className={`px-2 md:px-3 py-1 rounded-full text-[9px] md:text-[10px] font-black uppercase tracking-wider border ${
                          !isAboveMA60 ? 'text-[#10B981] border-[#10B981]/30 bg-[#10B981]/10' : getSignalStyle(stock.signal)
                        }`}>
                          {!isAboveMA60 ? '空頭禁區' : stock.signal}
                        </div>
                      </div>

                      <div className="mt-4 flex items-center justify-between">
                         <div className="flex items-center space-x-3 md:space-x-4">
                            <div className="flex flex-col">
                              <span className="text-[7px] md:text-[8px] text-gray-500 font-black uppercase">現價</span>
                              <span className={`text-xs md:text-sm font-mono font-bold ${!isAboveMA60 ? 'text-[#10B981]' : 'text-gray-100'}`}>${stock.close}</span>
                            </div>
                            <div className="flex flex-col">
                              <span className="text-[7px] md:text-[8px] text-gray-500 font-black uppercase">生命線</span>
                              <span className={`text-[9px] md:text-[10px] font-bold ${isAboveMA60 ? 'text-red-400' : 'text-gray-400'}`}>{stock.ma60 || "---"}</span>
                            </div>
                         </div>
                         <div className="flex items-center space-x-2">
                            {isAboveMA60 && stock.vol_ratio > 1.5 && <Zap size={14} className="text-orange-500" />}
                            {isAboveMA60 && <ShieldCheck size={14} className="text-red-500" />}
                            {!isAboveMA60 && <AlertTriangle size={14} className="text-[#10B981] animate-pulse" />}
                         </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </aside>

          {/* Section 4: Chart & Details */}
          <section id="stock-details" className="lg:col-span-8 space-y-6">
            {selectedStock ? (
              <>
                <div className={`glass rounded-3xl p-4 md:p-6 border transition-all ${selectedStock.close < selectedStock.ma60 ? 'border-gray-800 desaturate' : 'border-white/5'}`}>
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                    <div>
                      <div className="flex items-center space-x-3">
                        <h2 className="text-3xl md:text-4xl font-black text-white tracking-tighter italic">
                          {selectedStock.symbol.replace('.TW', '')} {selectedStock.name}
                        </h2>
                        <div className="flex flex-col">
                          <span className="px-2 py-0.5 bg-gray-800 text-gray-500 rounded-md text-[9px] font-bold uppercase">{selectedStock.market === 'tw' ? 'TWSE' : 'NASDAQ'}</span>
                          <span className="text-[8px] font-black text-red-500/80 uppercase mt-1 ml-1">{selectedStock.sector}</span>
                        </div>
                        <span className={`text-xl md:text-2xl font-black ${selectedStock.change > 0 ? 'text-red-500' : 'text-green-500'}`}>{selectedStock.change}%</span>
                        <div className="ml-auto flex items-center bg-red-600/10 border border-red-500/20 px-3 py-1 rounded-xl">
                          <div className="flex flex-col items-center">
                            <span className="text-[8px] font-black text-red-500 uppercase tracking-widest">正規軍評分</span>
                            <span className="text-xl font-black text-white">{calculateRegularArmyScore(selectedStock)}</span>
                          </div>
                        </div>
                        {selectedStock.close < selectedStock.ma60 && (
                          <span className="px-2 py-1 bg-red-600/20 text-red-500 rounded-lg text-[10px] font-black uppercase flex items-center">
                            <AlertTriangle size={12} className="mr-1" /> 空頭禁區：嚴禁摸底
                          </span>
                        )}
                      </div>
                      <div className="mt-2 flex items-center space-x-4">
                        <div className="flex items-center text-[#10B981]">
                          <TrendingUp size={14} className="mr-1" />
                          <span className="text-[10px] md:text-xs font-black">2Y 回測勝率: {selectedStock.backtest?.win_rate || "--"}%</span>
                        </div>
                        <div className="flex items-center text-red-500">
                          <Activity size={14} className="mr-1" />
                          <span className="text-[10px] md:text-xs font-black">策略總報酬: {selectedStock.backtest?.total_return || "--"}%</span>
                        </div>
                      </div>
                      <p className="text-xs md:text-sm text-gray-400 font-bold mt-1">{selectedStock.name} - {selectedStock.tactic || "大數據戰情分析中"}</p>
                      
                      {/* Tactical Score Breakdown */}
                      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2">
                        {[
                          { label: 'MA60 乖離', value: selectedStock.ma60 ? Math.max(0, Math.min(10, ((selectedStock.close / selectedStock.ma60) - 1) * 100 + 5)).toFixed(1) : 0, icon: <Activity size={10} /> },
                          { label: 'RSI 強度', value: (selectedStock.rsi || 50) / 10, icon: <Zap size={10} /> },
                          { label: '量能比例', value: Math.min(10, selectedStock.vol_ratio * 2).toFixed(1), icon: <TrendingUp size={10} /> },
                          { label: '綜合動能', value: selectedStock.tactical_score || 5, icon: <Target size={10} /> }
                        ].map((item, i) => (
                          <div key={i} className="bg-white/5 rounded-lg p-2 border border-white/5">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-[8px] font-black text-gray-500 uppercase flex items-center">{item.icon}<span className="ml-1">{item.label}</span></span>
                              <span className="text-[10px] font-bold text-red-500">{item.value}/10</span>
                            </div>
                            <div className="w-full bg-gray-800 h-1 rounded-full overflow-hidden">
                              <div className="bg-red-600 h-full" style={{ width: `${item.value * 10}%` }}></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    {selectedStock.close > selectedStock.ma60 ? (
                      <button 
                        onClick={() => document.getElementById('investment-checklist')?.scrollIntoView({ behavior: 'smooth' })}
                        className="w-full md:w-auto bg-red-600 text-white font-black px-6 md:px-8 py-3 rounded-2xl hover:bg-red-500 transition-all shadow-xl shadow-red-600/20 active:scale-95 flex items-center justify-center"
                      >
                        <Target size={18} className="mr-2" /> 進入檢核記錄模式 (CHECK)
                      </button>
                    ) : (
                      <div className="w-full md:w-auto px-6 py-3 bg-gray-800 text-gray-500 rounded-2xl font-black text-xs uppercase flex items-center justify-center">
                        <ShieldAlert size={18} className="mr-2" /> 低於生命線：拒絕交易
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4 mb-6">
                     <div className="bg-white/5 p-4 rounded-2xl border border-white/5 flex flex-col items-center md:items-start">
                        <span className="text-[8px] md:text-[9px] text-gray-500 font-black uppercase block mb-1">建議進場位</span>
                        <span className="text-xl md:text-2xl font-mono font-bold text-white">${selectedStock.plan?.entry || selectedStock.close}</span>
                     </div>
                     <div className="bg-green-500/5 p-4 rounded-2xl border border-green-500/20 flex flex-col items-center md:items-start">
                        <span className="text-[8px] md:text-[9px] text-green-400 font-black uppercase block mb-1">生命線支撐 (停損)</span>
                        <span className="text-xl md:text-2xl font-mono font-bold text-green-500">${selectedStock.ma60 || "---"}</span>
                     </div>
                     <div className="bg-red-500/5 p-4 rounded-2xl border border-red-500/20 flex flex-col items-center md:items-start">
                        <span className="text-[8px] md:text-[9px] text-red-400 font-black uppercase block mb-1">預期止盈點</span>
                        <span className="text-xl md:text-2xl font-mono font-bold text-red-500">${selectedStock.plan?.tp || "---"}</span>
                     </div>
                  </div>

                  <div className="h-[300px] md:h-[450px]">
                    <TradingChart 
                      data={historyData} 
                      symbol={selectedStock.symbol} 
                      buyPrice={selectedStock.plan?.entry}
                      stopLoss={selectedStock.ma60}
                      takeProfit={selectedStock.plan?.tp}
                    />
                  </div>
                </div>

                {/* Investment Checklist Component */}
                <div id="investment-checklist">
                  <InvestmentChecklist stock={selectedStock} />
                </div>

                {/* Sensei's Golden Quotes Section */}
                <div className="glass rounded-3xl p-4 md:p-6 border border-white/5 space-y-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-[10px] md:text-sm font-black text-white uppercase tracking-widest flex items-center">
                      <Quote size={14} className="mr-2 text-yellow-500" /> 顏老師的金句箴言 (Sensei's Wisdom)
                    </h3>
                  </div>
                  <div className="relative bg-[#161A1E] border border-white/5 rounded-2xl p-6 overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-yellow-500/50"></div>
                    <Quote size={40} className="absolute top-2 left-2 text-white/5 rotate-180" />
                    <p className="relative z-10 text-sm md:text-base text-gray-300 font-bold leading-relaxed tracking-wide italic pl-4">
                      {
                        [
                          "紀律是最高階的進攻。",
                          "跌破生命線，嚴禁摸底，強制執行資本保護。",
                          "盤中震盪加劇是散戶的毒藥，卻是正規軍的試金石。",
                          "人取我棄，鎖住人性。觀望不動，本身就是一種高階決策。",
                          "外資的態度藏在溢價裡，寧可錯過不可做錯。",
                          "季線 (MA60) 之下沒有委屈的股票，只有套牢的散戶。",
                          "量化交易的核心，就是把恐懼與貪婪交給數據。",
                          "停損不是認輸，而是為了下一次滿血復活保留實力。",
                          "買在無人問津處，賣在人聲鼎沸時。",
                          "一旦工具傳來破線訊號，絕不『腳麻』，立刻無情砍倉。",
                          "真正的高手，是透過資訊工具，將人性鎖進紀律的鐵籠。",
                          "Python 只是工具，真正的力量來自於您對量化紀律的堅持。",
                          "股市生存系統不預測未來，我們只執行客觀的事實。",
                          "投資理財都要考量風險，避免讓生計受到不好的影響。",
                          "運用系統化的方法與理性的態度，深入且快速地排除迷思。",
                          "開盤走勢往往不是想像的那樣，所以要客觀看待均線。",
                          "長線操作應保留至少 40% 資金，在重要支撐處略為加碼。",
                          "學習資訊工具的目的不是成為神算子，而是控制自己的心魔。",
                          "每一筆交易都要思考：這是擬好的 SOP，還是當下的貪婪？"
                        ][selectedStock.symbol.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % 19]
                      }
                    </p>
                  </div>
                </div>
              </>
            ) : (
              <div className="h-[400px] lg:h-full glass rounded-3xl flex flex-col items-center justify-center text-gray-600 italic p-8 md:p-12 text-center">
                <BarChart3 size={48} md:size={64} className="mb-4 opacity-20" />
                <p className="text-lg md:text-xl font-bold">請選擇標的以啟動分析系統</p>
                <p className="text-xs md:text-sm mt-2 opacity-60">系統將依據「正規軍」量化檢核標準進行自動化診斷</p>
              </div>
            )}
          </section>
        </div>
      </main>

      <footer className="h-10 border-t border-white/5 bg-[#1E2329] flex items-center px-4 md:px-6 text-[9px] md:text-[10px] text-gray-500">
        <div className="flex-1 flex space-x-4 md:space-x-8 overflow-hidden items-center">
            <div className="hidden md:flex items-center space-x-2">
              <span className="font-black text-gray-400 uppercase">System Integrity:</span>
              <span className="text-green-500 font-bold">DISCIPLINED</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-black text-gray-400 uppercase tracking-tighter">Strategy:</span>
              <span className="text-red-500 font-bold">MA60 REGULAR ARMY</span>
            </div>
            <div className="flex space-x-6 animate-marquee whitespace-nowrap opacity-60">
               {currentStocks.slice(0, 20).map(s => (
                 <span key={s.symbol} className="font-mono">
                   {s.symbol}: <span className={s.change > 0 ? 'text-red-500' : 'text-green-500'}>{s.price} ({s.change}%)</span>
                 </span>
               ))}
            </div>
        </div>
        <div className="font-black italic text-gray-400 ml-4 whitespace-nowrap">
          © 2026 REGULAR ARMY QUANT - 資訊工具化驗證系統
        </div>
      </footer>

    </div>
  );
}

export default App;

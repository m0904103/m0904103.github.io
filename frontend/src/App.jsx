import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  Cell, PieChart, Pie
} from 'recharts';
import { 
  TrendingUp, TrendingDown, AlertCircle, CheckCircle2, Search, RefreshCcw, 
  ChevronRight, BarChart3, PieChart as PieChartIcon, Activity, Wind, CloudRain,
  ShieldCheck, Zap, AlertTriangle, ShieldAlert, Navigation2, Target, Sword, Crosshair, HelpCircle,
  Menu, X, ExternalLink, Globe, LayoutDashboard, History, Settings, Info, Bell, MessageSquare,
  Lock, ArrowRight, MousePointer2, Thermometer, Droplets, Sun, Moon, Clock, Quote,
  Building2, LineChart as LineChartIcon, FileText, Coins, BookOpen
} from 'lucide-react';
import InvestmentChecklist from './components/InvestmentChecklist';
import SectorHeatmap from './components/SectorHeatmap';
import StrategyBoard from './components/StrategyBoard';
import TradingChart from './components/TradingChart';

const IS_PROD = window.location.hostname.includes('github.io');
const API_BASE = IS_PROD ? '.' : (import.meta.env.VITE_API_URL || "http://localhost:8000");
const RENDER_API_URL = "https://m0904103-github-io.onrender.com";

function App() {
  const [stocks, setStocks] = useState({ tw: [], us: [] });
  const [indices, setIndices] = useState({});
  const [taifexOi, setTaifexOi] = useState(-69847);
  const [loading, setLoading] = useState(true);
  const [selectedStock, setSelectedStock] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [dataLastUpdatedStr, setDataLastUpdatedStr] = useState("");
  const [dataAgeMinutes, setDataAgeMinutes] = useState(0);
  const [systemStatus, setSystemStatus] = useState("online");
  const [cloudStatus, setCloudStatus] = useState("connecting"); 
  const [activeMarket, setActiveMarket] = useState(() => {
    const hour = new Date().getHours();
    return (hour >= 8 && hour < 18) ? "tw" : "us";
  });
  const [activeTab, setActiveTab] = useState("regular"); 
  const [selectedSector, setSelectedSector] = useState(null);

  useEffect(() => {
    fetchData();
    checkCloudStatus();
    const interval = setInterval(fetchData, 30000);
    const cloudInterval = setInterval(checkCloudStatus, 60000);
    return () => {
      clearInterval(interval);
      clearInterval(cloudInterval);
    };
  }, []);

  const checkCloudStatus = async () => {
    try {
      await axios.get(`${RENDER_API_URL}/health`, { timeout: 5000 });
      setCloudStatus("online");
    } catch (e) {
      setCloudStatus("offline");
    }
  };

  const fetchData = async () => {
    setSystemStatus("connecting");
    try {
      const timestamp = new Date().getTime();
      const scanUrl = IS_PROD ? `${API_BASE}/scan_results.json?t=${timestamp}` : `${API_BASE}/scan`;

      const scanRes = await axios.get(scanUrl);

      let stockData = scanRes.data;
      // Calculate data age - handles both UTC ISO format ("2026-06-03T12:01:00Z") and legacy ("2026-06-03 12:01")
      if (stockData.last_updated) {
        const rawStr = stockData.last_updated;
        // Parse: if it ends with Z it's UTC ISO, otherwise assume legacy local format
        const dataTime = new Date(rawStr.includes('Z') ? rawStr : rawStr.replace(' ', 'T'));
        const ageMs = new Date() - dataTime;
        const ageMin = Math.floor(ageMs / 60000);
        setDataAgeMinutes(ageMin);
        // Display in Taiwan time (UTC+8)
        const displayStr = dataTime.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei', hour12: false });
        setDataLastUpdatedStr(displayStr);
      }
      if (stockData && stockData.stocks) {
        const tw = stockData.stocks.filter(s => s.market === 'tw');
        const us = stockData.stocks.filter(s => s.market === 'us');
        stockData = { tw, us, indices: stockData.indices };
      } else if (!stockData || !stockData.tw) {
        // Fallback to prevent TypeError in render if data is corrupted
        stockData = { tw: [], us: [], indices: {} };
      }
      setStocks(stockData);
      setIndices(stockData.indices || {});
      setTaifexOi(scanRes.data.taifex_oi || -69847);
      setLastUpdated(new Date());
      setSystemStatus("online");
    } catch (error) {
      setSystemStatus("offline");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStock = async (stock) => {
    if (stock.market && stock.market !== activeMarket) setActiveMarket(stock.market);
    setSelectedStock(stock);
    setTimeout(() => {
      const element = document.getElementById('trading-chart');
      if (element) element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);

    try {
      const historyUrl = IS_PROD ? `${API_BASE}/assets/history_${stock.symbol}.json?t=${new Date().getTime()}` : `${API_BASE}/history/${stock.symbol}`;
      const res = await axios.get(historyUrl);
      setHistoryData(res.data || []);
    } catch (e) {
      setHistoryData([]);
    }
  };

  const handleSelectSector = (sectorName) => {
    if (!sectorName) { setSelectedSector(null); return; }
    const trimmedSector = sectorName.trim();
    setSelectedSector(trimmedSector);
    const currentMarketStocks = activeMarket === 'tw' ? stocks.tw : stocks.us;
    const hasInCurrent = currentMarketStocks.some(s => s.sector?.trim() === trimmedSector);
    if (!hasInCurrent) {
      const otherMarket = activeMarket === 'tw' ? 'us' : 'tw';
      const hasInOther = (otherMarket === 'tw' ? stocks.tw : stocks.us).some(s => s.sector?.trim() === trimmedSector);
      if (hasInOther) setActiveMarket(otherMarket);
    }
  };

  const renderWeatherStation = () => {
    const usVix = indices["US VIX (恐慌)"]?.close || 16.2;
    const twVix = indices["台指 VIX (波動率)"]?.close || 39.02;
    const retailSmall = indices["散戶小台多空比"]?.close || 38.52;
    const putCall = indices["全市場 P/C Ratio"]?.close || 164.48;
    const retailMicro = indices["微台散戶多空比"]?.close || 0;
    
    let suggestedCash = indices.suggested_cash || 30;
    
    // Dynamic Cash Suggestion based on max VIX
    const maxVix = Math.max(usVix, twVix);
    if (maxVix > 25) suggestedCash = 50;
    if (maxVix > 35) suggestedCash = 70;

    let wisdom = "大格局看大勢，耐心等待屬於您的擊球區。";
    if (twVix > 35) wisdom = "【極端預警】台指 VIX 突破 38，這是一場生存遊戲。嚴格執行 70% 現金水位，保護救命錢。";

    // TAIFEX Alert Logic
    let taifexAlertText = "🟢 大盤籌碼穩定";
    let taifexAlertClass = "bg-green-600/20 text-green-400 border-green-500/30";
    if (taifexOi < -30000) {
      taifexAlertText = "🔴 【極度警戒】外資空單突破 3 萬口！切勿追高！";
      taifexAlertClass = "bg-red-600/30 text-red-400 border-red-500/50 animate-pulse";
    } else if (taifexOi < -15000) {
      taifexAlertText = "🟡 【注意】外資持續佈局空單";
      taifexAlertClass = "bg-yellow-600/20 text-yellow-400 border-yellow-500/30";
    }

    return (
      <div className="space-y-4 mb-6">
        {/* Level 3: TAIFEX Weather Radar Banner */}
        <div className={`w-full py-2 px-4 rounded-xl border flex items-center justify-between font-black text-sm transition-all shadow-lg ${taifexAlertClass}`}>
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} />
            <span>阿村伯期貨防護罩：外資台指期未平倉空單</span>
          </div>
          <div className="text-xl">{taifexOi.toLocaleString()} 口</div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="glass rounded-2xl p-4 border-l-4 border-l-blue-400">
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">美國 VIX (恐慌)</span>
            <div className="text-2xl font-black mt-1 flex items-center text-blue-400">
               {usVix}
            </div>
          </div>
          <div className={`glass rounded-2xl p-4 border-l-4 ${twVix > 35 ? 'border-l-purple-600 bg-purple-600/5' : 'border-l-red-500'}`}>
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">台指 VIX (波動率)</span>
            <div className="text-2xl font-black mt-1 flex items-center text-purple-500">
               {twVix} {twVix > 35 && <span className="ml-2 text-[10px] font-bold text-red-500">極端恐慌</span>}
            </div>
          </div>
          <div className="glass rounded-2xl p-4 border-l-4 border-l-cyan-500">
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">散戶小台多空比</span>
            <div className="text-2xl font-black mt-1 text-cyan-400">+{retailSmall}%</div>
          </div>
          <div className="glass rounded-2xl p-4 border-l-4 border-l-orange-500">
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">全市場 P/C Ratio</span>
            <div className="text-2xl font-black mt-1 text-orange-400">{putCall}%</div>
          </div>
        </div>
        <div className="bg-white/5 p-4 rounded-2xl border border-white/10 italic text-sm text-gray-300">
          <Quote size={14} className="inline mr-2 text-yellow-500" /> {wisdom}
        </div>
      </div>
    );
  };

  const signalRank = { 'Strong Buy': 0, 'Buy': 1, 'Hold': 2, 'Sell': 3, 'Strong Sell': 4 };

  const displayStocks = (activeMarket === 'tw' ? stocks.tw : stocks.us).filter(s => {
    const matchSearch = s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || s.name.includes(searchTerm);
    const matchSector = selectedSector ? s.sector === selectedSector : true;
    return matchSearch && matchSector;
  }).sort((a, b) => {
    // 1. Sort by signal strength (Strong Buy first)
    const rankDiff = (signalRank[a.signal] ?? 9) - (signalRank[b.signal] ?? 9);
    if (rankDiff !== 0) return rankDiff;
    // 2. Within same signal: sort by MA60 deviation ascending (closest to MA60 = lowest risk)
    const deviationA = a.ma60 > 0 ? Math.abs((a.close - a.ma60) / a.ma60) : 999;
    const deviationB = b.ma60 > 0 ? Math.abs((b.close - b.ma60) / b.ma60) : 999;
    return deviationA - deviationB;
  });

  return (
    <div className="min-h-screen bg-[#0B0E11] text-gray-100 font-['Inter', 'Noto Sans TC', sans-serif]">
      {/* ⚠️ 數據新鮮度警衛 - 區分盤中延遲與盤後休市 */}
      {dataAgeMinutes > 90 && dataAgeMinutes <= 180 && new Date().getDay() !== 0 && new Date().getDay() !== 6 && (
        <div className="w-full bg-red-600 text-white py-2 px-4 flex items-center justify-center gap-3 text-sm font-black z-[100] sticky top-0">
          <AlertTriangle size={18} className="animate-pulse shrink-0" />
          <span>
            ⚠️ 警告：即時報價發生延遲 {dataAgeMinutes} 分鐘！（最後更新：{dataLastUpdatedStr}）請勿依此數據下單！
          </span>
          <AlertTriangle size={18} className="animate-pulse shrink-0" />
        </div>
      )}
      {(dataAgeMinutes > 180 || new Date().getDay() === 0 || new Date().getDay() === 6) && dataAgeMinutes > 90 && (
        <div className="w-full bg-slate-700 text-slate-200 py-2 px-4 flex items-center justify-center gap-2 text-sm font-bold z-[100] sticky top-0 border-b border-white/10">
          <span>💤 盤後/假日休市：收盤數據已結算（最後更新：{dataLastUpdatedStr}）</span>
        </div>
      )}
      {dataAgeMinutes > 0 && dataAgeMinutes <= 90 && (
        <div className="w-full bg-green-700/80 text-green-100 py-1 px-4 flex items-center justify-center gap-2 text-xs font-bold">
          <span>🟢 數據新鮮度正常 — 最後同步：{dataLastUpdatedStr}（{dataAgeMinutes} 分鐘前）</span>
        </div>
      )}
      <header className="px-4 md:px-8 py-4 border-b border-white/5 bg-[#0B0E11]/80 backdrop-blur-xl sticky top-0 z-50 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="bg-red-600 p-2 rounded-xl shadow-lg shadow-red-600/20">
            <ShieldCheck className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-lg md:text-xl font-black tracking-tighter uppercase leading-none">正規軍量化交易終端</h1>
            <span className="text-[9px] font-black text-red-500 uppercase tracking-widest opacity-80">Regular Army Strategic Command</span>
          </div>
        </div>

        <div className="w-full lg:flex-1 max-w-md order-3 lg:order-none mt-2 lg:mt-0">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-red-500 transition-colors" size={16} />
            <input 
              type="text" 
              placeholder="搜尋代號或名稱..." 
              className="w-full bg-[#161A1E] border border-white/5 rounded-2xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-red-500/50 transition-all font-bold"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Cloud Signal Indicator */}
          <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border transition-all ${
            cloudStatus === 'online' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
            'bg-red-500/10 border-red-500/30 text-red-400'
          }`}>
            <div className={`w-2 h-2 rounded-full ${cloudStatus === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-[10px] font-black uppercase tracking-widest whitespace-nowrap">
              {cloudStatus === 'online' ? 'Render Cloud Active' : 'Local Backup Mode'}
            </span>
          </div>

          <div className="flex bg-[#161A1E] p-1 rounded-xl border border-white/5">
            <button onClick={() => setActiveMarket("tw")} className={`px-4 py-1.5 text-xs font-black rounded-lg ${activeMarket === 'tw' ? 'bg-red-600 text-white' : 'text-gray-500'}`}>TAIWAN</button>
            <button onClick={() => setActiveMarket("us")} className={`px-4 py-1.5 text-xs font-black rounded-lg ${activeMarket === 'us' ? 'bg-blue-600 text-white' : 'text-gray-500'}`}>USA</button>
          </div>
        </div>
      </header>

      <main className="p-4 md:p-8 max-w-[1600px] mx-auto w-full space-y-8">
        <section id="weather-station">{renderWeatherStation()}</section>
        
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-black text-gray-400 uppercase tracking-widest flex items-center">
              <LayoutDashboard size={16} className="mr-2" /> 2026 產業戰略地圖
              <span className="ml-3 px-2 py-0.5 bg-red-600/20 text-red-400 rounded-md text-[10px]">
                鎖定至 2026 年 8 月底
              </span>
            </h2>
          </div>
          <StrategyBoard 
            onSelectStock={handleSelectStock} 
            stocks={activeMarket === 'tw' ? stocks.tw : stocks.us} 
          />
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <aside className="lg:col-span-4 glass rounded-3xl overflow-hidden border border-white/5 h-[600px] flex flex-col">
             <div className="p-4 bg-[#161A1E] border-b border-white/5 flex justify-between">
                <span className="text-xs font-black text-gray-400 uppercase tracking-widest">市場診斷名單</span>
                <span className="text-[10px] text-gray-500">最後更新: {lastUpdated.toLocaleTimeString()}</span>
             </div>
             <div className="flex-1 overflow-y-auto p-2 space-y-2">
                {displayStocks.map(stock => (
                  <div key={stock.symbol} onClick={() => handleSelectStock(stock)} className={`p-3 rounded-2xl cursor-pointer transition-all border ${selectedStock?.symbol === stock.symbol ? 'bg-red-600/10 border-red-600/30' : 'bg-white/5 border-transparent hover:border-white/10'}`}>
                    <div className="flex justify-between items-start">
                      <div className="flex flex-col">
                        <div className="font-black flex items-center gap-2">
                          <span>{stock.symbol.replace(/\.TWO?$/, '')} {stock.name}</span>
                          {stock.esg_elite && <span className="px-1.5 py-0.5 rounded text-[9px] bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/30 tracking-widest">🌱 ESG護城河</span>}
                        </div>
                        {activeMarket === 'tw' && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {stock.fundamentals?.three_rates_rising && <span className="text-[9px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-400 border border-green-500/30">🟢 三率三升</span>}
                            {stock.chips?.foreign_buy && <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">🔵 外資買超</span>}
                            {stock.technicals?.bb_lower_touch && <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400 border border-purple-500/30">🔴 布林觸底</span>}
                          </div>
                        )}
                        {/* Level 2 & 3: Gap, K-Line, and Volume Surge Badges */}
                        <div className="flex flex-wrap gap-1 mt-1">
                          {stock.vol_surge && <span className="text-[9px] px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-400 border border-orange-500/30 tracking-widest font-bold">🌊 爆量突破</span>}
                          {stock.gap_up && <span className="text-[9px] px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 tracking-widest font-bold">🚀 向上缺口</span>}
                          {stock.k_pattern === 'Engulfing' && <span className="text-[9px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-400 border border-green-500/30 tracking-widest font-bold">🔄 吞噬反轉</span>}
                          {stock.k_pattern === 'Harami' && <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30 tracking-widest font-bold">🤰 母子醞釀</span>}
                        </div>
                        {/* Pattern badges for all markets */}
                        {(() => {
                          const p = stock.patterns || {};
                          const badges = [];
                          if (p.triple_bottom) badges.push({ label: '🏔️ 三重底', cls: 'bg-orange-500/20 text-orange-300 border-orange-500/30' });
                          if (p.w_bottom) badges.push({ label: '〰️ W底', cls: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' });
                          if (p.abc_wave?.pattern_en === 'ABC_BOTTOM') badges.push({ label: '🔄 ABC底完成', cls: 'bg-violet-500/20 text-violet-300 border-violet-500/30' });
                          if (p.abc_wave?.pattern_en === 'ABC_FALLING') badges.push({ label: '⚠️ C波下跌', cls: 'bg-red-500/20 text-red-400 border-red-500/30' });
                          return badges.length > 0 ? (
                            <div className="flex flex-wrap gap-1 mt-1">
                              {badges.map(b => <span key={b.label} className={`text-[9px] px-1.5 py-0.5 rounded border ${b.cls}`}>{b.label}</span>)}
                            </div>
                          ) : null;
                        })()}
                       </div>
                       <span className={`px-2 py-1 rounded-lg text-[10px] font-black ${stock.signal.includes('Buy') ? 'bg-red-600/20 text-red-500' : 'bg-gray-800 text-gray-500'}`}>{stock.signal}</span>
                    </div>
                  </div>
                ))}
             </div>
          </aside>

          <section id="trading-chart" className="lg:col-span-8 space-y-6">
            {selectedStock ? (
              <div className="glass rounded-3xl p-6 border border-white/5 space-y-6">
                 <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-3">
                        <h2 className="text-3xl font-black tracking-tighter">{selectedStock.symbol.replace(/\.TWO?$/, '')} {selectedStock.name}</h2>
                        {selectedStock.esg_elite && <span className="px-2 py-1 rounded text-xs font-black bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/30 tracking-widest">🌱 ESG護城河</span>}
                      </div>
                      <p className="text-sm text-gray-400 font-bold mt-1">{selectedStock.tactic}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-gray-500 font-black uppercase">目前股價</span>
                      <div className="text-3xl font-mono font-bold">${selectedStock.close}</div>
                    </div>
                 </div>
                 <div className="h-[400px] w-full rounded-2xl overflow-hidden">
                    {historyData && historyData.length > 0 ? (
                      <TradingChart 
                        data={historyData} 
                        symbol={selectedStock.symbol.replace(/\.TWO?$/, '')} 
                        buyPrice={selectedStock.plan?.entry}
                        stopLoss={selectedStock.plan?.sl}
                        takeProfit={selectedStock.plan?.tp}
                        currentPrice={selectedStock.close}
                        stock={selectedStock}
                      />
                    ) : (
                      <div className="w-full h-full bg-[#161A1E] border border-white/5 flex items-center justify-center text-gray-500 italic">
                        [ 圖表載入中... 正在獲取 {selectedStock.symbol.replace(/\.TWO?$/, '')} 的歷史數據 ]
                      </div>
                    )}
                 </div>
                 
                 {/* Pattern Analysis Card */}
                  {selectedStock?.patterns && Object.keys(selectedStock.patterns || {}).filter(k => k !== 'summary').length > 0 && (
                    <div className="bg-[#1a1f25] border border-white/5 rounded-2xl p-4">
                      <div className="text-xs font-black text-gray-400 uppercase tracking-widest mb-3">🧠 阿村伯型態診斷</div>
                      <div className="flex flex-wrap gap-3">
                        {selectedStock.patterns.triple_bottom && (
                          <div className="flex-1 min-w-[180px] bg-orange-500/10 border border-orange-500/20 rounded-xl p-3">
                            <div className="text-orange-300 font-black text-sm mb-1">🏔️ 三重底</div>
                            <div className="text-xs text-gray-400 space-y-0.5">
                              <div>頸線壓力：<span className="text-white font-bold">${selectedStock.patterns.triple_bottom.neckline}</span></div>
                              <div>強力支撐：<span className="text-green-400 font-bold">${selectedStock.patterns.triple_bottom.support}</span></div>
                              <div>突破目標：<span className="text-orange-300 font-bold">${selectedStock.patterns.triple_bottom.target}</span></div>
                              <div className={`mt-1 font-black ${selectedStock.patterns.triple_bottom.strength === 'strong' ? 'text-green-400' : 'text-yellow-400'}`}>
                                {selectedStock.patterns.triple_bottom.strength === 'strong' ? '✅ 已突破頸線' : '🟡 型態形成中'}
                              </div>
                            </div>
                          </div>
                        )}
                        {selectedStock.patterns.w_bottom && (
                          <div className="flex-1 min-w-[180px] bg-cyan-500/10 border border-cyan-500/20 rounded-xl p-3">
                            <div className="text-cyan-300 font-black text-sm mb-1">〰️ W底（雙底）</div>
                            <div className="text-xs text-gray-400 space-y-0.5">
                              <div>頸線壓力：<span className="text-white font-bold">${selectedStock.patterns.w_bottom.neckline}</span></div>
                              <div>強力支撐：<span className="text-green-400 font-bold">${selectedStock.patterns.w_bottom.support}</span></div>
                              <div>突破目標：<span className="text-cyan-300 font-bold">${selectedStock.patterns.w_bottom.target}</span></div>
                              <div className={`mt-1 font-black ${selectedStock.patterns.w_bottom.strength === 'strong' ? 'text-green-400' : 'text-yellow-400'}`}>
                                {selectedStock.patterns.w_bottom.strength === 'strong' ? '✅ 已突破頸線' : '🟡 型態形成中'}
                              </div>
                            </div>
                          </div>
                        )}
                        {selectedStock.patterns.abc_wave && (
                          <div className={`flex-1 min-w-[180px] border rounded-xl p-3 ${
                            selectedStock.patterns.abc_wave.pattern_en === 'ABC_FALLING'
                              ? 'bg-red-500/10 border-red-500/20'
                              : 'bg-violet-500/10 border-violet-500/20'
                          }`}>
                            <div className={`font-black text-sm mb-1 ${selectedStock.patterns.abc_wave.pattern_en === 'ABC_FALLING' ? 'text-red-400' : 'text-violet-300'}`}>
                              {selectedStock.patterns.abc_wave.pattern_en === 'ABC_FALLING' ? '⚠️ ABC下跌中（C波）' : '🔄 ABC底部完成'}
                            </div>
                            <div className="text-xs text-gray-400 space-y-0.5">
                              <div>A波頂：<span className="text-white font-bold">${selectedStock.patterns.abc_wave.wave_top}</span></div>
                              <div>A波跌幅：<span className="text-red-400 font-bold">{selectedStock.patterns.abc_wave.a_drop_pct}%</span></div>
                              <div>B波反彈：<span className="text-yellow-400 font-bold">{selectedStock.patterns.abc_wave.b_rebound_pct}%</span></div>
                              {selectedStock.patterns.abc_wave.fib_target_618 && <div>費氏目標(0.618)：<span className="text-violet-300 font-bold">${selectedStock.patterns.abc_wave.fib_target_618}</span></div>}
                              {selectedStock.patterns.abc_wave.warning && <div className="text-red-400 font-black mt-1">{selectedStock.patterns.abc_wave.warning}</div>}
                            </div>
                          </div>
                        )}
                        {selectedStock.patterns.summary && (
                          <div className="w-full bg-white/5 border border-white/10 rounded-xl p-3 flex items-center justify-between">
                            <div>
                              <div className="text-sm font-black">{selectedStock.patterns.summary.verdict}</div>
                              <div className="text-xs text-gray-400 mt-0.5">偵測訊號：{selectedStock.patterns.summary.signals.join('、')}</div>
                            </div>
                            <div className="text-2xl font-black text-white/30">#{selectedStock.patterns.summary.score}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                 {/* Restore Checklist containing the Quotes */}
                 <InvestmentChecklist stock={selectedStock} />
              </div>
            ) : (
              <div className="h-full flex items-center justify-center glass rounded-3xl border border-dashed border-white/10 text-gray-500 italic">
                請從上方地圖或左側名單選取個股進行診斷
              </div>
            )}
          </section>
        </div>

        {/* 顏老師量化武器庫 (Yen's Quant Toolbox) */}
        <section className="mt-12">
          <div className="flex items-center mb-6">
            <BookOpen size={20} className="text-blue-400 mr-3" />
            <h2 className="text-lg font-black text-white uppercase tracking-widest">
              顏老師量化武器庫 <span className="text-gray-500 text-xs ml-2">Yen's Recommended Resources</span>
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            <a href="https://mops.twse.com.tw/" target="_blank" rel="noopener noreferrer" className="glass rounded-2xl p-5 border border-white/5 hover:border-blue-500/50 hover:bg-blue-500/5 transition-all group">
              <Search className="text-blue-400 mb-3 group-hover:scale-110 transition-transform" size={28} />
              <h3 className="font-black text-lg mb-2">公開資訊觀測站 (MOPS)</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                由政府與相關機構提供，當我們需要「更及時或者是更精確的企業訊息與公告」時，這是一個最具權威性的必備網站。
              </p>
            </a>
            
            <a href="https://statementdog.com/" target="_blank" rel="noopener noreferrer" className="glass rounded-2xl p-5 border border-white/5 hover:border-green-500/50 hover:bg-green-500/5 transition-all group">
              <FileText className="text-green-400 mb-3 group-hover:scale-110 transition-transform" size={28} />
              <h3 className="font-black text-lg mb-2">財報狗 (Statementdog)</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                這個網站以「基本面選股」為主要特色，並提供「股票健診」功能。建議同學即使不付費登入，也可以嘗試使用它的健診結果來驗證自己的投資知識。
              </p>
            </a>

            <a href="https://www.cmoney.tw/" target="_blank" rel="noopener noreferrer" className="glass rounded-2xl p-5 border border-white/5 hover:border-yellow-500/50 hover:bg-yellow-500/5 transition-all group">
              <Coins className="text-yellow-400 mb-3 group-hover:scale-110 transition-transform" size={28} />
              <h3 className="font-black text-lg mb-2">CMoney 理財寶</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                提供多元的理財資訊與財經網站，裡面包含了非常多投資理財方面的軟體、籌碼分析與相關雜誌資訊。
              </p>
            </a>

            <a href="https://tw.stock.yahoo.com/" target="_blank" rel="noopener noreferrer" className="glass rounded-2xl p-5 border border-white/5 hover:border-purple-500/50 hover:bg-purple-500/5 transition-all group">
              <LineChartIcon className="text-purple-400 mb-3 group-hover:scale-110 transition-transform" size={28} />
              <h3 className="font-black text-lg mb-2">Yahoo 奇摩股市</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                除了豐富財經新聞，課程中也教導如何使用 Python 套件串接 Yahoo Finance 的 API 來下載交易資料並繪製 K 線圖。
              </p>
            </a>

            <a href="https://www.twse.com.tw/" target="_blank" rel="noopener noreferrer" className="glass rounded-2xl p-5 border border-white/5 hover:border-red-500/50 hover:bg-red-500/5 transition-all group">
              <Building2 className="text-red-400 mb-3 group-hover:scale-110 transition-transform" size={28} />
              <h3 className="font-black text-lg mb-2">台灣證券交易所</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                在進行「量化金融資料處理」時，透過 Python 去證交所抓取上市櫃公司的基本資料與每日交易數據，是量化分析的基石。
              </p>
            </a>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;

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
  Lock, ArrowRight, MousePointer2, Thermometer, Droplets, Sun, Moon, Clock, Quote
} from 'lucide-react';
import MarketStatus from './components/MarketStatus';
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
      const indexUrl = `${RENDER_API_URL}/indices?t=${timestamp}`;

      const [scanRes, indexRes] = await Promise.all([
        axios.get(scanUrl),
        axios.get(indexUrl)
      ]);

      let stockData = scanRes.data;
      if (stockData.stocks) {
        const tw = stockData.stocks.filter(s => s.market === 'tw');
        const us = stockData.stocks.filter(s => s.market === 'us');
        stockData = { tw, us };
      }

      setStocks(stockData || { tw: [], us: [] });
      setIndices(indexRes.data || {});
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
      const historyUrl = IS_PROD ? `${API_BASE}/assets/history_${stock.symbol}.json` : `${API_BASE}/history/${stock.symbol}`;
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
    const vix = indices["台指VIX (波動率)"]?.close || indices["VIX (恐慌)"]?.close || 15;
    const adr = indices.adr_premium?.close || 0;
    let suggestedCash = indices.suggested_cash || 30;
    if (vix > 35) suggestedCash = 70;

    let wisdom = "大格局看大勢，耐心等待屬於您的擊球區。";
    if (vix > 35) wisdom = "【極端預警】台指 VIX 突破 38，這是一場生存遊戲。嚴格執行 70% 現金水位，保護救命錢。";

    return (
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className={`glass rounded-2xl p-4 border-l-4 ${vix > 35 ? 'border-l-purple-600 bg-purple-600/5' : 'border-l-orange-500'}`}>
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">市場波動率 (VIX)</span>
            <div className="text-2xl font-black mt-1 flex items-center">
               {vix} <span className="ml-2 text-xs font-bold text-gray-400">極端恐慌</span>
            </div>
          </div>
          <div className="glass rounded-2xl p-4 border-l-4 border-l-blue-500">
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">建議現金水位</span>
            <div className="text-2xl font-black mt-1 text-blue-400">{suggestedCash}%</div>
          </div>
          <div className="glass rounded-2xl p-4 border-l-4 border-l-red-500">
            <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">TSM ADR 溢價</span>
            <div className="text-2xl font-black mt-1 text-red-400">{adr}%</div>
          </div>
        </div>
        <div className="bg-white/5 p-4 rounded-2xl border border-white/10 italic text-sm text-gray-300">
          <Quote size={14} className="inline mr-2 text-yellow-500" /> {wisdom}
        </div>
      </div>
    );
  };

  const displayStocks = (activeMarket === 'tw' ? stocks.tw : stocks.us).filter(s => {
    const matchSearch = s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || s.name.includes(searchTerm);
    const matchSector = selectedSector ? s.sector === selectedSector : true;
    return matchSearch && matchSector;
  });

  return (
    <div className="min-h-screen bg-[#0B0E11] text-gray-100 font-['Inter', 'Noto Sans TC', sans-serif]">
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

        <div className="flex-1 max-w-md hidden lg:block">
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
            </h2>
          </div>
          <StrategyBoard 
            onSelectStock={handleSelectStock} 
            stocks={[...stocks.tw, ...stocks.us]} 
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
                  <div key={stock.symbol} onClick={() => handleSelectStock(stock)} className={`p-4 rounded-2xl cursor-pointer transition-all border ${selectedStock?.symbol === stock.symbol ? 'bg-red-600/10 border-red-600/30' : 'bg-white/5 border-transparent hover:border-white/10'}`}>
                    <div className="flex justify-between items-center">
                      <span className="font-black">{stock.symbol} {stock.name}</span>
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
                      <h2 className="text-3xl font-black tracking-tighter">{selectedStock.symbol} {selectedStock.name}</h2>
                      <p className="text-sm text-gray-400 font-bold mt-1">{selectedStock.tactic}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-xs text-gray-500 font-black uppercase">目前股價</span>
                      <div className="text-3xl font-mono font-bold">${selectedStock.close}</div>
                    </div>
                 </div>
                 <div className="h-[400px] bg-[#161A1E] rounded-2xl border border-white/5 flex items-center justify-center text-gray-500 italic">
                    [ 圖表載入中 - 這裡將顯示 {selectedStock.symbol} 的 MA60 生命線與量化分析 ]
                 </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center glass rounded-3xl border border-dashed border-white/10 text-gray-500 italic">
                請從上方地圖或左側名單選取個股進行診斷
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;

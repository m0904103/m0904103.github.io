import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  Cell, PieChart, Pie
} from 'recharts';
import { 
  TrendingUp, TrendingDown, AlertCircle, CheckCircle2, Search, RefreshCcw, RefreshCw,
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
  const [activeMarket, setActiveMarket] = useState(() => {
    const hour = new Date().getHours();
    return (hour >= 8 && hour < 18) ? "tw" : "us";
  });
  const [activeTab, setActiveTab] = useState("regular"); // regular, intraday
  const [selectedSector, setSelectedSector] = useState(null);

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
      console.error("Fetch error:", error);
      setSystemStatus("offline");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStock = async (stock) => {
    if (stock.market && stock.market !== activeMarket) setActiveMarket(stock.market);
    setSelectedStock(stock);
    setTimeout(() => {
      const el = document.getElementById('stock-details');
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    try {
      const historyUrl = IS_PROD ? `${API_BASE}/assets/history_${stock.symbol}.json` : `${API_BASE}/history/${stock.symbol}`;
      const res = await axios.get(historyUrl);
      setHistoryData(res.data || []);
    } catch (e) {
      setHistoryData([]);
    }
  };

  const handleSelectSector = (name) => {
    setSelectedSector(name === selectedSector ? null : name);
  };

  const getSignalStyle = (signal) => {
    if (signal?.includes("Strong Buy")) return "text-red-500 bg-red-500/10 border-red-500/20";
    if (signal?.includes("Sell")) return "text-green-500 bg-green-500/10 border-green-500/20";
    return "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
  };

  const currentStocks = (activeMarket === "tw" ? stocks?.tw : stocks?.us) || [];
  const displayStocks = currentStocks.filter(s => {
    const matchSearch = s.symbol.includes(searchTerm) || s.name.includes(searchTerm);
    const matchSector = selectedSector ? s.sector === selectedSector : true;
    return matchSearch && matchSector;
  });

  const renderWeatherStation = () => {
    const vix = indices["VIX (恐慌)"]?.close || 15;
    const adr = indices.adr_premium?.close || 0;
    const suggestedCash = indices.suggested_cash || (vix > 25 ? 70 : 30);

    return (
      <div className="space-y-4 mb-6">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-black text-white tracking-tighter flex items-center gap-2">
            <Thermometer className="text-red-500" size={20} />
            市場氣象台 <span className="text-gray-500 italic text-sm">WEATHER STATION</span>
          </h2>
          
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full border text-[10px] font-bold ${
            indices.cloud_status === 'live' ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-red-500/10 border-red-500/30 text-red-400'
          }`}>
            <div className={`w-1.5 h-1.5 rounded-full ${indices.cloud_status === 'live' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            CLOUD {indices.cloud_status === 'live' ? 'LIVE' : 'OFFLINE'} {indices.cloud_time}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass rounded-2xl p-4 border-l-4 border-l-red-500">
            <span className="text-[10px] font-black text-gray-500 uppercase">台指 VIX 恐慌</span>
            <div className="text-3xl font-black text-white mt-1">{vix}</div>
          </div>
          <div className="glass rounded-2xl p-4 border-l-4 border-l-blue-500">
            <span className="text-[10px] font-black text-gray-500 uppercase">TSM ADR 溢價</span>
            <div className="text-3xl font-black text-white mt-1">{adr}%</div>
          </div>
          <div className="glass rounded-2xl p-4 border-l-4 border-l-green-500">
            <span className="text-[10px] font-black text-gray-500 uppercase">建議現金水位</span>
            <div className="text-3xl font-black text-white mt-1">{suggestedCash}%</div>
          </div>
          <div className="glass rounded-2xl p-4 border-l-4 border-l-yellow-500">
            <span className="text-[10px] font-black text-gray-500 uppercase">生命線狀態</span>
            <div className="text-xl font-black text-white mt-1">MA60 支撐中</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#0B0E11] text-gray-200 p-4 md:p-8">
      <header className="mb-8 flex justify-between items-center">
        <h1 className="text-2xl font-black italic text-white">REGULAR ARMY <span className="text-red-500">COMMAND</span></h1>
        <div className="flex gap-2 bg-gray-900 p-1 rounded-xl">
          <button onClick={() => setActiveMarket('tw')} className={`px-4 py-1 rounded-lg text-xs font-bold ${activeMarket === 'tw' ? 'bg-red-600 text-white' : 'text-gray-500'}`}>TAIWAN</button>
          <button onClick={() => setActiveMarket('us')} className={`px-4 py-1 rounded-lg text-xs font-bold ${activeMarket === 'us' ? 'bg-blue-600 text-white' : 'text-gray-500'}`}>USA</button>
        </div>
      </header>

      {renderWeatherStation()}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <aside className="lg:col-span-4 glass rounded-3xl p-4 h-[600px] overflow-y-auto">
          <div className="mb-4">
            <input 
              type="text" placeholder="搜尋股票..." 
              className="w-full bg-gray-800 border-none rounded-xl py-2 px-4 text-sm"
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            {displayStocks.map(s => (
              <div key={s.symbol} onClick={() => handleSelectStock(s)} className="p-4 bg-white/5 rounded-2xl border border-transparent hover:border-red-500/50 cursor-pointer">
                <div className="flex justify-between">
                  <span className="font-black">{s.symbol} {s.name}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full ${getSignalStyle(s.signal)}`}>{s.signal}</span>
                </div>
                <div className="mt-2 text-xs text-gray-500">價格: ${s.close} | MA60: ${s.ma60}</div>
              </div>
            ))}
          </div>
        </aside>

        <main id="stock-details" className="lg:col-span-8 space-y-6">
          {selectedStock ? (
            <div className="glass rounded-3xl p-8 border border-white/5">
              <h2 className="text-4xl font-black italic mb-4">{selectedStock.symbol} {selectedStock.name}</h2>
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="bg-white/5 p-4 rounded-2xl">
                  <span className="text-[10px] text-gray-500 uppercase">當前策略</span>
                  <p className="font-bold text-red-400">{selectedStock.tactic || "守住生命線，不摸底。"}</p>
                </div>
                <div className="bg-white/5 p-4 rounded-2xl">
                  <span className="text-[10px] text-gray-500 uppercase">趨勢分數</span>
                  <p className="text-2xl font-black">{selectedStock.trend_score}/100</p>
                </div>
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={historyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                    <XAxis dataKey="date" hide />
                    <YAxis hide domain={['auto', 'auto']} />
                    <Tooltip contentStyle={{backgroundColor: '#111', border: 'none'}} />
                    <Area type="monotone" dataKey="close" stroke="#ef4444" fill="rgba(239, 68, 68, 0.1)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-600 italic">請從左側選取股票進行量化診斷</div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;

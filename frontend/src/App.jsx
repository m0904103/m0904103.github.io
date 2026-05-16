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
  Lock, ArrowRight, MousePointer2, Thermometer, Droplets, Sun, Moon
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
    } catch (error) {
      console.error("Fetch error:", error);
      setSystemStatus("offline");
    } finally {
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
      setHistoryData(res.data || []);
    } catch (e) {
      console.error("History fetch error:", e);
      setHistoryData([]);
    }
  };

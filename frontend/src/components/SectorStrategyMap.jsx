import React, { useState } from 'react';
import { 
  Cpu, Layers, Satellite, Zap, Smartphone, Server, Brain, 
  ShieldAlert, Sparkles, ChevronRight, Activity, ArrowUpRight, CheckCircle2, AlertTriangle
} from 'lucide-react';

const SECTOR_STRATEGY_MAP = [
  {
    id: 'compute',
    title: '1. 極限算力與水冷基建',
    icon: Cpu,
    color: 'from-amber-500 to-orange-600',
    borderColor: 'border-orange-500/30',
    bgGlow: 'bg-orange-500/10',
    usLeaders: [
      { symbol: 'NVDA', name: '輝達', role: 'AI GPU 晶片霸主' },
      { symbol: 'VRT', name: 'Vertiv', role: '液冷散熱與高密度電源' }
    ],
    twSupplyChain: [
      { symbol: '3017.TW', name: '奇鋐', role: '水冷板與散熱模組' },
      { symbol: '3324.TWO', name: '雙鴻', role: '水冷散熱關鍵組件' },
      { symbol: '2308.TW', name: '台達電', role: 'AI 資料中心高壓電源' }
    ]
  },
  {
    id: 'ccl',
    title: '2. 高階 CCL 與傳輸材料',
    icon: Layers,
    color: 'from-cyan-500 to-blue-600',
    borderColor: 'border-cyan-500/30',
    bgGlow: 'bg-cyan-500/10',
    usLeaders: [
      { symbol: 'NVDA', name: '輝達', role: 'Blackwell 超高速架構' },
      { symbol: 'AVGO', name: '博通', role: '高速傳輸晶片與光通訊' }
    ],
    twSupplyChain: [
      { symbol: '2383.TW', name: '台光電', role: 'M9 高階銅箔基板霸主' },
      { symbol: '6274.TWO', name: '台燿', role: '高頻高速 CCL 供應商' }
    ]
  },
  {
    id: 'space',
    title: '3. 空間計算與低軌衛星',
    icon: Satellite,
    color: 'from-purple-500 to-indigo-600',
    borderColor: 'border-purple-500/30',
    bgGlow: 'bg-purple-500/10',
    usLeaders: [
      { symbol: 'ASTS', name: 'AST SpaceMobile', role: '手持直連衛星通訊' },
      { symbol: 'RKLB', name: 'Rocket Lab', role: '商業小型火箭發射' }
    ],
    twSupplyChain: [
      { symbol: '3491.TWO', name: '昇達科', role: 'SpaceX 毫米波元件' },
      { symbol: '2313.TW', name: '華通', role: '星鏈太空 PCB 板霸主' },
      { symbol: '6285.TW', name: '啟碁', role: '低軌衛星地面接收站' }
    ]
  },
  {
    id: 'grid',
    title: '4. 核能與智慧電網基建',
    icon: Zap,
    color: 'from-emerald-500 to-teal-600',
    borderColor: 'border-emerald-500/30',
    bgGlow: 'bg-emerald-500/10',
    usLeaders: [
      { symbol: 'CEG', name: 'Constellation', role: '核電供應巨頭' },
      { symbol: 'VST', name: 'Vistra', role: '獨立核能發電商' },
      { symbol: 'GEV', name: 'GE Vernova', role: '電網設備與綠能機組' }
    ],
    twSupplyChain: [
      { symbol: '1519.TW', name: '華城', role: '外銷美國變壓器王者' },
      { symbol: '1513.TW', name: '中興電', role: 'GIS 高壓絕緣開關' },
      { symbol: '1503.TW', name: '士電', role: '重電設備與變壓器' }
    ]
  },
  {
    id: 'edge',
    title: '5. 邊緣 AI 與終端硬體',
    icon: Smartphone,
    color: 'from-pink-500 to-rose-600',
    borderColor: 'border-pink-500/30',
    bgGlow: 'bg-pink-500/10',
    usLeaders: [
      { symbol: 'QCOM', name: '高通', role: 'Copilot+ PC 晶片' },
      { symbol: 'AAPL', name: '蘋果', role: 'Apple Intelligence 終端' }
    ],
    twSupplyChain: [
      { symbol: '2454.TW', name: '聯發科', role: '邊緣 AI 手機晶片' },
      { symbol: '2317.TW', name: '鴻海', role: 'AI 伺服器與 iPhone 代工' },
      { symbol: '2382.TW', name: '廣達', role: 'AI 筆電與伺服器組裝' }
    ]
  },
  {
    id: 'cpo',
    title: '6. 矽光子與 CPO 光電整合',
    icon: Server,
    color: 'from-sky-500 to-blue-700',
    borderColor: 'border-sky-500/30',
    bgGlow: 'bg-sky-500/10',
    usLeaders: [
      { symbol: 'AVGO', name: '博通', role: 'CPO 光電共封裝晶片' },
      { symbol: 'MRVL', name: '美滿電子', role: '高速光傳輸控制' }
    ],
    twSupplyChain: [
      { symbol: '2330.TW', name: '台積電', role: 'COUPE 矽光子封裝平台' },
      { symbol: '6451.TW', name: '訊芯-KY', role: 'CPO 光收發模組封裝' },
      { symbol: '3081.TWO', name: '聯亞', role: '矽光子外延片磊晶' }
    ]
  },
  {
    id: 'agentic',
    title: '7. 代理型 AI 軟體與 Enterprise AI',
    icon: Brain,
    color: 'from-violet-500 to-purple-700',
    borderColor: 'border-violet-500/30',
    bgGlow: 'bg-violet-500/10',
    usLeaders: [
      { symbol: 'PLTR', name: 'Palantir', role: 'AIP 企業級 AI 作業系統' },
      { symbol: 'NOW', name: 'ServiceNow', role: 'AI 工作流自動化' }
    ],
    twSupplyChain: [
      { symbol: '6811.TWO', name: '宏碁資訊', role: '雲端與 AI 解決方案' },
      { symbol: '3029.TW', name: '零壹', role: '企業代理型 AI 經銷' },
      { symbol: '6112.TW', name: '邁達特', role: '雲端系統整合與資安' }
    ]
  }
];

export default function SectorStrategyMap({ stocks, onSelectStock }) {
  const [selectedTheme, setSelectedTheme] = useState('compute');

  // Flatten all stock data for quick lookup
  const stockMap = React.useMemo(() => {
    const map = {};
    if (stocks.tw) stocks.tw.forEach(s => { map[s.symbol] = s; });
    if (stocks.us) stocks.us.forEach(s => { map[s.symbol] = s; });
    return map;
  }, [stocks]);

  const activeThemeObj = SECTOR_STRATEGY_MAP.find(t => t.id === selectedTheme) || SECTOR_STRATEGY_MAP[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-slate-900/80 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-3">
            <span className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
              <Sparkles className="w-6 h-6 animate-pulse" />
            </span>
            <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-amber-200 via-orange-300 to-amber-400">
              2026 產業戰略地圖 (美股領頭羊 ⇄ 台股供應鏈)
            </h2>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            結合華爾街投行共識與台股三大法人鎖碼，精準對照美股龍頭與台灣關鍵供應鏈。
          </p>
        </div>
      </div>

      {/* Theme Selectors */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-3">
        {SECTOR_STRATEGY_MAP.map((theme) => {
          const Icon = theme.icon;
          const isSelected = selectedTheme === theme.id;
          return (
            <button
              key={theme.id}
              onClick={() => setSelectedTheme(theme.id)}
              className={`p-3 rounded-xl border text-left transition-all duration-300 flex flex-col justify-between ${
                isSelected
                  ? `bg-slate-800 ${theme.borderColor} shadow-lg shadow-black/40 ring-1 ring-amber-500/50`
                  : 'bg-slate-900/40 border-slate-800/80 hover:bg-slate-800/60 hover:border-slate-700 text-slate-400'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`p-1.5 rounded-lg ${isSelected ? theme.bgGlow : 'bg-slate-800'}`}>
                  <Icon className={`w-4 h-4 ${isSelected ? 'text-amber-300' : 'text-slate-400'}`} />
                </span>
                {isSelected && <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />}
              </div>
              <span className={`text-xs font-semibold line-clamp-1 ${isSelected ? 'text-amber-200' : 'text-slate-300'}`}>
                {theme.title}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active Theme Strategy Panel */}
      <div className={`p-6 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border ${activeThemeObj.borderColor} backdrop-blur-xl shadow-2xl relative overflow-hidden`}>
        <div className="flex items-center gap-3 mb-6 border-b border-slate-800/80 pb-4">
          <activeThemeObj.icon className="w-7 h-7 text-amber-400" />
          <h3 className="text-xl font-bold text-slate-100">{activeThemeObj.title}</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* US Leaders */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="text-sm font-semibold text-blue-400 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-400" /> 美股戰略領頭羊 (US Leaders)
              </span>
              <span className="text-xs text-slate-500">美股點擊查看 K 線</span>
            </div>
            <div className="space-y-3">
              {activeThemeObj.usLeaders.map((item) => {
                const liveData = stockMap[item.symbol];
                const isAboveMa60 = liveData && liveData.close >= liveData.ma60;
                return (
                  <div 
                    key={item.symbol}
                    onClick={() => liveData && onSelectStock(liveData)}
                    className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-blue-500/50 hover:bg-blue-950/20 cursor-pointer transition-all flex items-center justify-between group"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-200 group-hover:text-blue-300 transition-colors">{item.symbol}</span>
                        <span className="text-xs text-slate-400">({item.name})</span>
                        {isAboveMa60 ? (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-medium flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> 季線之上
                          </span>
                        ) : liveData ? (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 font-medium flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" /> 季線下方
                          </span>
                        ) : null}
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{item.role}</p>
                    </div>

                    <div className="text-right flex items-center gap-3">
                      {liveData && (
                        <div>
                          <div className="text-sm font-bold text-slate-200">${liveData.close?.toFixed(2)}</div>
                          <div className="text-[10px] text-slate-400">季線: ${liveData.ma60?.toFixed(2)}</div>
                        </div>
                      )}
                      <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* TW Supply Chain */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="text-sm font-semibold text-emerald-400 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400" /> 台股供應鏈 (TW Supply Chain)
              </span>
              <span className="text-xs text-slate-500">台股點擊查看 K 線</span>
            </div>
            <div className="space-y-3">
              {activeThemeObj.twSupplyChain.map((item) => {
                const liveData = stockMap[item.symbol];
                const isAboveMa60 = liveData && liveData.close >= liveData.ma60;
                return (
                  <div 
                    key={item.symbol}
                    onClick={() => liveData && onSelectStock(liveData)}
                    className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-emerald-500/50 hover:bg-emerald-950/20 cursor-pointer transition-all flex items-center justify-between group"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-200 group-hover:text-emerald-300 transition-colors">{item.symbol.replace('.TW', '').replace('.TWO', '')}</span>
                        <span className="text-xs text-slate-400">({item.name})</span>
                        {isAboveMa60 ? (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-medium flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> 季線之上
                          </span>
                        ) : liveData ? (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 font-medium flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" /> 季線下方
                          </span>
                        ) : null}
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{item.role}</p>
                    </div>

                    <div className="text-right flex items-center gap-3">
                      {liveData && (
                        <div>
                          <div className="text-sm font-bold text-slate-200">{liveData.close?.toFixed(1)}元</div>
                          <div className="text-[10px] text-slate-400">季線: {liveData.ma60?.toFixed(1)}元</div>
                        </div>
                      )}
                      <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

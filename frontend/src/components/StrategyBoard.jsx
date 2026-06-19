import React from 'react';
import { Thermometer, Zap, PlugZap, BrainCircuit, Bot, Layers, ShieldCheck, Cpu, Satellite, Lock, FlaskConical } from 'lucide-react';

const StrategyBoard = ({ onSelectStock, stocks }) => {
  const baseSectors = [
    { name: "極限算力基建", rating: "🔥 超熱", count: 5, icon: <Thermometer size={16} />, color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/20", symbols: ["NVDA", "VRT", "3017", "2308", "3324"] },
    { name: "矽光子/CPO", rating: "🔥 超熱", count: 6, icon: <Zap size={16} />, color: "text-orange-400", bg: "bg-orange-400/10", border: "border-orange-400/20", symbols: ["AVGO", "MRVL", "2330", "6451", "3081", "6669"] },
    { name: "核能與智慧電網", rating: "🔥 超熱", count: 6, icon: <PlugZap size={16} />, color: "text-orange-600", bg: "bg-orange-600/10", border: "border-orange-600/20", symbols: ["CEG", "VST", "GEV", "1519", "1513", "1503"] },
    { name: "先進封裝與基板", rating: "🟢 升溫", count: 5, icon: <Layers size={16} />, color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/20", symbols: ["ASML", "AMAT", "3481", "5234", "8028"] },
    { name: "邊緣 AI 與終端", rating: "🟢 升溫", count: 5, icon: <Cpu size={16} />, color: "text-emerald-400", bg: "bg-emerald-400/10", border: "border-emerald-400/20", symbols: ["QCOM", "AAPL", "2454", "2317", "2382"] },
    { name: "空間計算與低軌衛星", rating: "🟢 升溫", count: 5, icon: <Satellite size={16} />, color: "text-emerald-600", bg: "bg-emerald-600/10", border: "border-emerald-600/20", symbols: ["ASTS", "RKLB", "6285", "3491", "2313"] },
    { name: "代理型 AI 軟體", rating: "🟡 持平", count: 6, icon: <BrainCircuit size={16} />, color: "text-yellow-500", bg: "bg-yellow-500/10", border: "border-yellow-500/20", symbols: ["PLTR", "PATH", "NOW", "6811", "3029", "6112"] },
    { name: "量子計算與密碼學", rating: "🟡 持平", count: 5, icon: <Lock size={16} />, color: "text-yellow-400", bg: "bg-yellow-400/10", border: "border-yellow-400/20", symbols: ["IONQ", "IBM", "GOOGL", "3045", "2412"] },
    { name: "生物AI與精準醫療", rating: "🟡 持平", count: 5, icon: <FlaskConical size={16} />, color: "text-yellow-600", bg: "bg-yellow-600/10", border: "border-yellow-600/20", symbols: ["VEEV", "LLY", "NVO", "2382", "2409"] },
    { name: "主權 AI 與網安", rating: "🔴 降溫", count: 5, icon: <ShieldCheck size={16} />, color: "text-gray-400", bg: "bg-gray-400/10", border: "border-gray-400/20", symbols: ["CRWD", "PANW", "3558", "6245", "8114"] },
    { name: "實體 AI 機器人", rating: "🔴 降溫", count: 5, icon: <Bot size={16} />, color: "text-gray-500", bg: "bg-gray-500/10", border: "border-gray-500/20", symbols: ["TSLA", "ARM", "2359", "2049", "2357"] }
  ];

  const findStockBySymbol = (symbol) => {
    return stocks.find(s =>
      s.symbol === symbol ||
      s.symbol === `${symbol}.TW` ||
      s.symbol === `${symbol}.TWO` ||
      s.symbol === `${symbol}O` ||
      s.symbol.replace(/\.TWO?$/, '') === symbol
    );
  };

  // Calculate dynamic changes
  const sectors = baseSectors.map(sector => {
    let totalChange = 0;
    let foundCount = 0;
    sector.symbols.forEach(sym => {
      const stock = findStockBySymbol(sym);
      if (stock && stock.change !== undefined) {
        totalChange += stock.change;
        foundCount++;
      }
    });
    const avgChange = foundCount > 0 ? (totalChange / foundCount) : 0;
    return { ...sector, avgChange };
  });

  return (
    <div className="mb-8">
      <div className="flex items-center space-x-3 mb-4">
        <div className="bg-red-600 w-1 h-6 rounded-full"></div>
        <h3 className="text-lg font-black text-white uppercase tracking-tighter italic">2026 產業戰略版 (Sector Strategy Map)</h3>
        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded-md">Real-time Analysis</span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {sectors.map((sector, idx) => (
          <div key={idx} className={`glass rounded-2xl p-4 border ${sector.border} flex flex-col justify-between hover:scale-[1.02] transition-all group`}>
            <div className="flex justify-between items-start mb-3">
              <div className={`p-2 rounded-xl ${sector.bg} ${sector.color}`}>
                {sector.icon}
              </div>
              <div className="flex flex-col items-end">
                <span className={`text-sm font-black ${sector.color}`}>{sector.rating}</span>
                <span className={`text-xs font-bold ${sector.avgChange > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {sector.avgChange > 0 ? '+' : ''}{sector.avgChange.toFixed(1)}%
                </span>
                <span className="text-[8px] text-gray-500 font-bold uppercase mt-1">{sector.count} 檔成份股</span>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-black text-gray-200 mb-2">{sector.name}</h4>
              <div className="flex flex-wrap gap-1.5">
                {sector.symbols.map(sym => {
                  const stock = findStockBySymbol(sym);
                  return (
                    <button
                      key={sym}
                      onClick={() => stock && onSelectStock(stock)}
                      className={`px-2 py-1 rounded-lg text-[9px] font-black transition-all ${
                        stock 
                          ? 'bg-white/5 text-gray-300 hover:bg-red-500 hover:text-white cursor-pointer' 
                          : 'bg-gray-900/50 text-gray-700 cursor-not-allowed border border-red-500/30'
                      }`}
                    >
                      {sym} {stock?.name || "???"}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StrategyBoard;

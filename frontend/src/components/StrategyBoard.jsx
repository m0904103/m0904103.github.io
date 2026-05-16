import React from 'react';
import { Rocket, Cpu, Zap, Database, HardDrive, LayoutGrid, TrendingUp, TrendingDown, ShieldCheck, ShoppingCart, Car, Laptop } from 'lucide-react';

const StrategyBoard = ({ onSelectStock, stocks }) => {
  const sectors = [
    { name: "太空經濟", change: "+6.4%", count: 4, icon: <Rocket size={16} />, color: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/20", symbols: ["2313", "6213", "2383", "6274"] },
    { name: "AI 基建", change: "+1.7%", count: 9, icon: <HardDrive size={16} />, color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/20", symbols: ["2317", "6669", "2382", "2308", "2345", "3167", "2376", "2301", "2357"] },
    { name: "AI 軟體", change: "+1.5%", count: 6, icon: <Database size={16} />, color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/20", symbols: ["2454", "2357", "6112", "3029", "2480", "5203"] },
    { name: "核能/能源", change: "-0.0%", count: 3, icon: <Zap size={16} />, color: "text-yellow-500", bg: "bg-yellow-500/10", border: "border-yellow-500/20", symbols: ["2308", "1513", "1519"] },
    { name: "消費電子", change: "-0.2%", count: 1, icon: <Laptop size={16} />, color: "text-gray-300", bg: "bg-gray-300/10", border: "border-gray-300/20", symbols: ["2357"] },
    { name: "電動車/AI", change: "-0.4%", count: 1, icon: <Car size={16} />, color: "text-red-400", bg: "bg-red-400/10", border: "border-red-400/20", symbols: ["2317"] },
    { name: "電商/雲端", change: "-1.1%", count: 1, icon: <ShoppingCart size={16} />, color: "text-purple-400", bg: "bg-purple-400/10", border: "border-purple-400/20", symbols: ["8454"] },
    { name: "台股權值", change: "-1.6%", count: 4, icon: <ShieldCheck size={16} />, color: "text-gray-400", bg: "bg-gray-400/10", border: "border-gray-400/20", symbols: ["2330", "2317", "2454", "2308"] },
    { name: "記憶體", change: "-6.0%", count: 2, icon: <Cpu size={16} />, color: "text-green-500", bg: "bg-green-500/10", border: "border-green-500/20", symbols: ["2344", "2408"] },
    { name: "高階 PCB", change: "-7.7%", count: 3, icon: <LayoutGrid size={16} />, color: "text-green-600", bg: "bg-green-600/10", border: "border-green-600/20", symbols: ["2383", "2368", "1815"] },
    { name: "矽光子 (CPO)", change: "-9.8%", count: 5, icon: <Zap size={16} />, color: "text-green-700", bg: "bg-green-700/10", border: "border-green-700/20", symbols: ["3363", "6451", "3163", "3443", "6442"] }
  ];

  const findStockBySymbol = (symbol) => {
    return stocks.find(s => s.symbol === symbol);
  };

  return (
    <div className="mb-8">
      <div className="flex items-center space-x-3 mb-4">
        <div className="bg-red-600 w-1 h-6 rounded-full"></div>
        <h3 className="text-lg font-black text-white uppercase tracking-tighter italic">2026 產業戰略版 (Sector Strategy Map)</h3>
        <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest bg-white/5 px-2 py-0.5 rounded-md">Real-time Analysis</span>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {sectors.map((sector, idx) => (
          <div key={idx} className={`glass rounded-2xl p-4 border ${sector.border} flex flex-col justify-between hover:scale-[1.02] transition-all group`}>
            <div className="flex justify-between items-start mb-3">
              <div className={`p-2 rounded-xl ${sector.bg} ${sector.color}`}>
                {sector.icon}
              </div>
              <div className="flex flex-col items-end">
                <span className={`text-sm font-black ${sector.color}`}>{sector.change}</span>
                <span className="text-[8px] text-gray-500 font-bold uppercase">{sector.count} 檔成份股</span>
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
                          : 'bg-gray-900/50 text-gray-700 cursor-not-allowed'
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

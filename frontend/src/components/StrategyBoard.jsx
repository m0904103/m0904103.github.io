import React from 'react';
import { Thermometer, Zap, PlugZap, BrainCircuit, Bot, Layers, ShieldCheck, Cpu } from 'lucide-react';

const StrategyBoard = ({ onSelectStock, stocks }) => {
  const sectors = [
    { name: "極限算力基建", change: "+12.4%", count: 5, icon: <Thermometer size={16} />, color: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/20", symbols: ["NVDA", "VRT", "3017", "2308", "3324"] },
    { name: "矽光子／CPO", change: "+8.7%", count: 6, icon: <Zap size={16} />, color: "text-yellow-500", bg: "bg-yellow-500/10", border: "border-yellow-500/20", symbols: ["AVGO", "MRVL", "2330", "6451", "3081", "6669"] },
    { name: "核能與智慧電網", change: "+5.2%", count: 6, icon: <PlugZap size={16} />, color: "text-green-500", bg: "bg-green-500/10", border: "border-green-500/20", symbols: ["CEG", "VST", "GEV", "1519", "1513", "1503"] },
    { name: "代理型 AI 軟體", change: "+15.1%", count: 6, icon: <BrainCircuit size={16} />, color: "text-purple-500", bg: "bg-purple-500/10", border: "border-purple-500/20", symbols: ["PLTR", "PATH", "APP", "6811", "3029", "6112"] },
    { name: "實體 AI 機器人", change: "+18.3%", count: 5, icon: <Bot size={16} />, color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/20", symbols: ["TSLA", "ARM", "2359", "2049", "8069"] },
    { name: "先進封裝與基板", change: "+9.5%", count: 5, icon: <Layers size={16} />, color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/20", symbols: ["ASML", "AMAT", "3481", "5234", "8028"] },
    { name: "主權 AI 與網安", change: "+6.8%", count: 5, icon: <ShieldCheck size={16} />, color: "text-teal-400", bg: "bg-teal-400/10", border: "border-teal-400/20", symbols: ["CRWD", "PANW", "3558", "6245", "8114"] },
    { name: "邊緣 AI 與終端", change: "+4.1%", count: 5, icon: <Cpu size={16} />, color: "text-indigo-400", bg: "bg-indigo-400/10", border: "border-indigo-400/20", symbols: ["QCOM", "AAPL", "2454", "2317", "2382"] }
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

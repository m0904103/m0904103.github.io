import React from 'react';
import { Activity, Rocket, Cpu, Zap, Database, HardDrive, LayoutGrid } from 'lucide-react';

const SectorHeatmap = ({ stocks, onSelectSector, activeSector }) => {
  if (!stocks || stocks.length === 0) return null;

  // Group stocks by sector
  const sectorGroups = stocks.reduce((acc, stock) => {
    const sector = stock.sector || '其他族群';
    if (!acc[sector]) acc[sector] = { name: sector, totalChange: 0, count: 0, stocks: [] };
    acc[sector].totalChange += stock.change || 0;
    acc[sector].count += 1;
    acc[sector].stocks.push(stock);
    return acc;
  }, {});

  const sectors = Object.values(sectorGroups).map(s => ({
    ...s,
    avgChange: s.totalChange / s.count
  })).sort((a, b) => b.avgChange - a.avgChange);

  const getSectorIcon = (name) => {
    if (name.includes('太空')) return <Rocket size={14} />;
    if (name.includes('基建')) return <HardDrive size={14} />;
    if (name.includes('軟體')) return <Database size={14} />;
    if (name.includes('半導體') || name.includes('矽光子')) return <Cpu size={14} />;
    if (name.includes('能源')) return <Zap size={14} />;
    return <LayoutGrid size={14} />;
  };

  return (
    <div className="mb-6 overflow-x-auto no-scrollbar">
      <div className="flex space-x-4 pb-2 min-w-max">
        {sectors.map((sector, idx) => (
          <div 
            key={idx}
            onClick={() => onSelectSector(sector.name === activeSector ? null : sector.name)}
            className={`glass-light p-3 rounded-2xl border transition-all hover:scale-105 cursor-pointer flex flex-col justify-between w-36 h-20 ${
              activeSector === sector.name 
                ? 'ring-2 ring-red-500 border-red-500 bg-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.3)]' 
                : sector.avgChange > 0 ? 'border-red-500/20' : 'border-[#10B981]/20'
            }`}
          >
            <div className="flex justify-between items-start">
              <span className={`text-[10px] font-black uppercase tracking-tighter truncate w-24 ${activeSector === sector.name ? 'text-white' : 'text-gray-500'}`}>
                {sector.name}
              </span>
              <span className={sector.avgChange > 0 ? 'text-red-500' : 'text-[#10B981]'}>
                {getSectorIcon(sector.name)}
              </span>
            </div>
            <div className="flex items-end justify-between">
               <span className={`text-lg font-black tracking-tighter ${sector.avgChange > 0 ? 'text-red-400' : 'text-[#10B981]'}`}>
                 {sector.avgChange > 0 ? '+' : ''}{sector.avgChange.toFixed(1)}%
               </span>
               <span className="text-[8px] text-gray-600 font-bold mb-1">
                 {sector.count} 檔
               </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SectorHeatmap;

import React from 'react';
import { Activity, Rocket, Cpu, Zap, Database, HardDrive, LayoutGrid, Satellite, FlaskConical, Lock, Wifi } from 'lucide-react';

// Gemini Deep Research Q2 2026 - Institutional Consensus Ratings
const SECTOR_META = {
  "極限算力基建":       { rating: "🔥", label: "超熱" },
  "矽光子/CPO":         { rating: "🔥", label: "超熱" },
  "核能與智慧電網":     { rating: "🔥", label: "超熱" },
  "先進封裝與基板":     { rating: "🟢", label: "升溫" },
  "邊緣 AI 與終端":     { rating: "🟢", label: "升溫" },
  "空間計算與低軌衛星": { rating: "🟢", label: "升溫" },
  "代理型 AI 軟體":     { rating: "🟡", label: "持平" },
  "量子計算與密碼學":   { rating: "🟡", label: "持平" },
  "生物AI與精準醫療":   { rating: "🟡", label: "持平" },
  "主權 AI 與網安":     { rating: "🔴", label: "降溫" },
  "實體 AI 機器人":     { rating: "🔴", label: "降溫" },
};

// Display order: hottest first
const SECTOR_ORDER = [
  "極限算力基建",
  "矽光子/CPO",
  "核能與智慧電網",
  "先進封裝與基板",
  "邊緣 AI 與終端",
  "空間計算與低軌衛星",
  "代理型 AI 軟體",
  "量子計算與密碼學",
  "生物AI與精準醫療",
  "主權 AI 與網安",
  "實體 AI 機器人",
];

const getSectorIcon = (name) => {
  if (name.includes('算力') || name.includes('基建'))   return <HardDrive size={13} />;
  if (name.includes('矽光子') || name.includes('CPO'))  return <Cpu size={13} />;
  if (name.includes('核能') || name.includes('電網'))   return <Zap size={13} />;
  if (name.includes('封裝') || name.includes('基板'))   return <Activity size={13} />;
  if (name.includes('邊緣') || name.includes('終端'))   return <Wifi size={13} />;
  if (name.includes('太空') || name.includes('衛星'))   return <Satellite size={13} />;
  if (name.includes('軟體') || name.includes('AI 軟'))  return <Database size={13} />;
  if (name.includes('量子') || name.includes('密碼'))   return <Lock size={13} />;
  if (name.includes('生物') || name.includes('醫療'))   return <FlaskConical size={13} />;
  if (name.includes('網安') || name.includes('主權'))   return <Lock size={13} />;
  if (name.includes('機器人'))                          return <Rocket size={13} />;
  return <LayoutGrid size={13} />;
};

const getRatingBorder = (rating) => {
  if (rating === "🔥") return "border-orange-500/40 bg-orange-500/5";
  if (rating === "🟢") return "border-emerald-500/40 bg-emerald-500/5";
  if (rating === "🟡") return "border-yellow-500/40 bg-yellow-500/5";
  if (rating === "🔴") return "border-gray-500/30 bg-gray-500/5";
  return "border-gray-600/20";
};

const getRatingTextColor = (rating) => {
  if (rating === "🔥") return "text-orange-400";
  if (rating === "🟢") return "text-emerald-400";
  if (rating === "🟡") return "text-yellow-400";
  if (rating === "🔴") return "text-gray-500";
  return "text-gray-500";
};

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

  // Sort by predefined order, then by avg change for unknowns
  const knownSectors = SECTOR_ORDER
    .filter(name => sectorGroups[name])
    .map(name => ({
      ...sectorGroups[name],
      avgChange: sectorGroups[name].totalChange / sectorGroups[name].count
    }));

  const otherSectors = Object.values(sectorGroups)
    .filter(s => !SECTOR_ORDER.includes(s.name) && s.name !== '其他族群')
    .map(s => ({ ...s, avgChange: s.totalChange / s.count }))
    .sort((a, b) => b.avgChange - a.avgChange);

  const sectors = [...knownSectors, ...otherSectors];

  return (
    <div className="mb-6 overflow-x-auto no-scrollbar">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[10px] font-black text-gray-500 uppercase tracking-widest">2026 產業戰略版 (Sector Strategy Map)</span>
        <span className="text-[9px] text-gray-600 font-semibold">Real-time Analysis</span>
        <span className="ml-auto flex gap-2 text-[9px] font-bold">
          <span className="text-orange-400">🔥超熱</span>
          <span className="text-emerald-400">🟢升溫</span>
          <span className="text-yellow-400">🟡持平</span>
          <span className="text-gray-500">🔴降溫</span>
        </span>
      </div>
      <div className="flex space-x-3 pb-2 min-w-max">
        {sectors.map((sector, idx) => {
          const meta = SECTOR_META[sector.name] || { rating: "", label: "" };
          const isActive = activeSector === sector.name;
          const borderClass = isActive
            ? 'ring-2 ring-red-500 border-red-500 bg-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.3)]'
            : getRatingBorder(meta.rating);
          const changeColor = sector.avgChange > 0 ? 'text-red-400' : 'text-emerald-400';

          return (
            <div
              key={idx}
              onClick={() => onSelectSector(sector.name === activeSector ? null : sector.name)}
              className={`glass-light p-3 rounded-2xl border transition-all hover:scale-105 cursor-pointer flex flex-col justify-between w-40 h-24 ${borderClass}`}
            >
              {/* Top row: icon + rating emoji */}
              <div className="flex justify-between items-start">
                <span className={`text-[9px] font-black tracking-tighter truncate w-28 leading-tight ${isActive ? 'text-white' : 'text-gray-400'}`}>
                  {sector.name}
                </span>
                <span className={isActive ? 'text-white' : getRatingTextColor(meta.rating)}>
                  {getSectorIcon(sector.name)}
                </span>
              </div>

              {/* Rating label */}
              <div className="flex items-center gap-1">
                <span className="text-[10px]">{meta.rating}</span>
                <span className={`text-[8px] font-bold ${getRatingTextColor(meta.rating)}`}>{meta.label}</span>
              </div>

              {/* Bottom row: avg change + count */}
              <div className="flex items-end justify-between">
                <span className={`text-base font-black tracking-tighter ${changeColor}`}>
                  {sector.avgChange > 0 ? '+' : ''}{sector.avgChange.toFixed(1)}%
                </span>
                <span className="text-[8px] text-gray-600 font-bold mb-1">
                  {sector.count} 檔
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SectorHeatmap;

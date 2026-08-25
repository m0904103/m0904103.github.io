import React from 'react';
import { Award, Zap, ShieldCheck, TrendingUp, AlertTriangle, Filter, CheckCircle2 } from 'lucide-react';

export const QUICK_FILTERS = [
  { id: 'all', label: '全部標的', icon: Filter, color: 'text-slate-300', bg: 'bg-slate-800' },
  { id: 'star5', label: '🏆 5星高勝率', icon: Award, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' },
  { id: 'sweet', label: '🎯 5%-12% 甜蜜區', icon: Zap, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30' },
  { id: 'foreign', label: '🔵 外資連買鎖碼', icon: ShieldCheck, color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/30' },
  { id: 'three_rates', label: '🟢 三率三升飆股', icon: TrendingUp, color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/30' },
  { id: 'below_ma60', label: '⚠️ 跌破季線警示', icon: AlertTriangle, color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/30' }
];

export default function QuickFilterBar({ activeFilter, onSelectFilter, counts = {} }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
      {QUICK_FILTERS.map(f => {
        const Icon = f.icon;
        const isSelected = activeFilter === f.id;
        const count = counts[f.id] || 0;

        return (
          <button
            key={f.id}
            onClick={() => onSelectFilter(f.id)}
            className={`px-3 py-1.5 rounded-xl border text-xs font-bold transition-all shrink-0 flex items-center gap-1.5 ${
              isSelected 
                ? 'bg-slate-800 border-amber-500 text-amber-300 shadow-md ring-1 ring-amber-500/50' 
                : 'bg-slate-900/60 border-slate-800/80 hover:bg-slate-800/60 text-slate-400'
            }`}
          >
            <Icon className={`w-3.5 h-3.5 ${f.color}`} />
            <span>{f.label}</span>
            <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${isSelected ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-800 text-slate-400'}`}>
              {count}
            </span>
          </button>
        );
      })}
    </div>
  );
}

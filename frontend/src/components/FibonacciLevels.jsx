import React from 'react';
import { Target, TrendingUp, TrendingDown, Layers, Compass, HelpCircle } from 'lucide-react';

export default function FibonacciLevels({ stock, historyData = [] }) {
  if (!stock || !stock.close) return null;

  const currentPrice = Number(stock.close);
  
  // Calculate 60-day high and low from historyData or fallback
  let high = currentPrice * 1.25;
  let low = currentPrice * 0.75;

  if (historyData && historyData.length > 5) {
    const prices = historyData.slice(-60).map(d => Number(d.close || d.price || currentPrice));
    high = Math.max(...prices);
    low = Math.min(...prices);
  }

  const diff = high - low;
  if (diff <= 0) return null;

  // Fibonacci Retracement Levels
  const fib236 = high - diff * 0.236;
  const fib382 = high - diff * 0.382;
  const fib500 = high - diff * 0.500;
  const fib618 = high - diff * 0.618;
  const fib786 = high - diff * 0.786;

  // Determine current position relative to Fibonacci levels
  const getLevelStatus = (levelPrice) => {
    const pctDiff = ((currentPrice - levelPrice) / levelPrice) * 100;
    if (Math.abs(pctDiff) < 1.5) return { text: '🎯 當前測試關卡', cls: 'text-amber-400 font-extrabold animate-pulse' };
    if (currentPrice > levelPrice) return { text: '🟢 已站上 (支撐)', cls: 'text-emerald-400' };
    return { text: '🔴 未站上 (壓力)', cls: 'text-rose-400' };
  };

  return (
    <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800 backdrop-blur-xl space-y-4 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Target className="w-5 h-5" />
          </span>
          <div>
            <h4 className="font-bold text-slate-200 text-sm">斐波那契黃金分割目標與支撐位 (Fibonacci Retracement)</h4>
            <p className="text-[10px] text-slate-400">基於 60日高點 (${high.toFixed(1)}) 與低點 (${low.toFixed(1)}) 之自動波浪推算</p>
          </div>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 font-mono font-bold">
          現價: ${currentPrice}
        </span>
      </div>

      {/* Levels Display Table */}
      <div className="grid grid-cols-1 sm:grid-cols-5 gap-2 text-xs">
        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
          <div className="text-[10px] text-slate-400 font-medium">0.236 輕微回檔</div>
          <div className="font-mono font-bold text-slate-200 text-sm">${fib236.toFixed(1)}</div>
          <div className={`text-[10px] ${getLevelStatus(fib236).cls}`}>{getLevelStatus(fib236).text}</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
          <div className="text-[10px] text-amber-300 font-medium">0.382 初步反彈目標</div>
          <div className="font-mono font-bold text-amber-200 text-sm">${fib382.toFixed(1)}</div>
          <div className={`text-[10px] ${getLevelStatus(fib382).cls}`}>{getLevelStatus(fib382).text}</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
          <div className="text-[10px] text-cyan-300 font-medium">0.500 多空強弱中軸</div>
          <div className="font-mono font-bold text-cyan-200 text-sm">${fib500.toFixed(1)}</div>
          <div className={`text-[10px] ${getLevelStatus(fib500).cls}`}>{getLevelStatus(fib500).text}</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
          <div className="text-[10px] text-emerald-300 font-medium font-bold">0.618 黃金分割主目標</div>
          <div className="font-mono font-bold text-emerald-300 text-sm">${fib618.toFixed(1)}</div>
          <div className={`text-[10px] ${getLevelStatus(fib618).cls}`}>{getLevelStatus(fib618).text}</div>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
          <div className="text-[10px] text-rose-300 font-medium">0.786 深度防守關卡</div>
          <div className="font-mono font-bold text-rose-200 text-sm">${fib786.toFixed(1)}</div>
          <div className={`text-[10px] ${getLevelStatus(fib786).cls}`}>{getLevelStatus(fib786).text}</div>
        </div>
      </div>
    </div>
  );
}

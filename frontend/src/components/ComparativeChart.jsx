import React from 'react';
import { Scale, ArrowUpRight, TrendingUp, TrendingDown, Layers, Zap } from 'lucide-react';
import { calculateWinRateScore } from './WinRateScorecard';

export default function ComparativeChart({ stock, globalIndices = {} }) {
  if (!stock || !stock.close) return null;

  const currentPrice = Number(stock.close);
  const ma60 = Number(stock.ma60 || currentPrice);
  const biasPct = (((currentPrice - ma60) / ma60) * 100).toFixed(1);

  // Market reference: S&P500 or TAIEX
  const isTwStock = stock.market === 'tw' || stock.symbol.includes('.TW');
  const marketName = isTwStock ? '台股加權指數' : '美股 S&P 500';
  const marketVix = isTwStock 
    ? (globalIndices['台指 VIX (波動率)']?.close || 20)
    : (globalIndices['US VIX (恐慌)']?.close || 16);

  // Relative Strength Status
  const isOutperforming = Number(biasPct) >= 5.0 && marketVix < 30;

  return (
    <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800 backdrop-blur-xl space-y-4 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
            <Scale className="w-5 h-5" />
          </span>
          <div>
            <h4 className="font-bold text-slate-200 text-sm">個股與整體市場相對強度對比 (Relative Strength Index)</h4>
            <p className="text-[10px] text-slate-400">對比 {stock.name} ({stock.symbol.replace(/\.TWO?$/, '')}) vs {marketName}</p>
          </div>
        </div>
        <span className={`text-xs px-2.5 py-1 rounded-full font-bold border ${isOutperforming ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>
          {isOutperforming ? '⚡ 強於大盤 (Outperform)' : '⚖️ 與大盤同步 / 整理'}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 font-medium">個股 60日季線乖離率</span>
          <div className={`text-lg font-extrabold font-mono ${Number(biasPct) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {Number(biasPct) >= 0 ? `+${biasPct}%` : `${biasPct}%`}
          </div>
          <span className="text-[9px] text-slate-500">個股多頭防守力道</span>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 font-medium">{marketName} 恐慌指數</span>
          <div className="text-lg font-extrabold font-mono text-purple-400">
            {marketVix}
          </div>
          <span className="text-[9px] text-slate-500">{marketVix > 30 ? '市場極度恐慌' : '市場波幅正常'}</span>
        </div>

        <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
          <span className="text-[10px] text-slate-400 font-medium">對比操盤指引</span>
          <div className="text-sm font-bold text-amber-300 mt-0.5">
            {isOutperforming ? '✅ 優先佈局強勢領頭羊' : '🟡 觀察季線支撐，避開弱勢股'}
          </div>
          <span className="text-[9px] text-slate-500">避開大盤拉回黑天鵝</span>
        </div>
      </div>
    </div>
  );
}

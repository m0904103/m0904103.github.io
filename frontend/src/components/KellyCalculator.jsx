import React, { useState } from 'react';
import { Calculator, ShieldCheck, DollarSign, PieChart, AlertTriangle, ArrowRight, Zap, RefreshCw } from 'lucide-react';
import { calculateWinRateScore } from './WinRateScorecard';

export default function KellyCalculator({ stock, globalIndices = {} }) {
  const [totalCapital, setTotalCapital] = useState(1000000); // Default 1,000,000 NTD or USD
  
  if (!stock || !stock.close) return null;

  const closePrice = Number(stock.close);
  const ma60 = Number(stock.ma60 || closePrice);
  
  // Calculate win rate using TINs engine
  const winRateRes = calculateWinRateScore(stock, globalIndices);
  const winRateDecimal = Math.max(0.3, Math.min(0.9, winRateRes.score / 100)); // Win probability p
  
  // Reward-to-risk ratio b (Default target 15% upside vs 5% stop loss = 3.0 ratio)
  const targetUpsidePct = 0.15;
  const stopLossPct = 0.05;
  const b = targetUpsidePct / stopLossPct; // 3.0
  
  // Kelly Fraction Formula: f* = (p(b+1) - 1) / b
  const rawKellyFraction = (winRateDecimal * (b + 1) - 1) / b;
  
  // Half-Kelly or Fractional Kelly for strict risk control (Teacher Yen Rule: Max 15% per stock)
  const isAboveMa60 = closePrice >= ma60;
  let recommendedFraction = isAboveMa60 ? Math.max(0.05, Math.min(0.15, rawKellyFraction * 0.5)) : 0;
  
  // Suggested position amount & shares
  const suggestedAmount = Math.floor(totalCapital * recommendedFraction);
  const isTwStock = stock.market === 'tw' || stock.symbol.includes('.TW');
  const suggestedShares = Math.floor(suggestedAmount / closePrice);
  
  // Stop loss price (3% to 5%)
  const stopLossPrice = isAboveMa60 ? Math.max(ma60 * 0.97, closePrice * 0.95) : closePrice * 0.97;
  const maxRiskAmount = Math.floor(suggestedAmount * 0.05);

  // Recommended Cash Buffer (Teacher Yen Rule: 20-30%, or 50% in High VIX)
  const twVix = globalIndices['台指 VIX (波動率)']?.close || 20;
  const suggestedCashBufferPct = twVix > 35 ? 50 : 30;
  const suggestedCashAmount = Math.floor(totalCapital * (suggestedCashBufferPct / 100));

  return (
    <div className="p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-slate-800 backdrop-blur-xl space-y-4 shadow-xl">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <span className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Calculator className="w-5 h-5" />
          </span>
          <div>
            <h4 className="font-bold text-slate-200 text-sm">顏老師凱利風控與部位計算器</h4>
            <p className="text-[10px] text-slate-400">基於 Kelly Criterion 與 60 日季線生命線之最佳風控下注比例</p>
          </div>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30 font-semibold">
          勝率依據: {winRateRes.score}分
        </span>
      </div>

      {/* Input Capital */}
      <div className="flex items-center justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-800">
        <label className="text-xs text-slate-400 font-medium flex items-center gap-1.5">
          <DollarSign className="w-4 h-4 text-emerald-400" />
          可運用總資本額:
        </label>
        <div className="flex items-center gap-2">
          <input 
            type="number" 
            value={totalCapital}
            onChange={(e) => setTotalCapital(Math.max(10000, Number(e.target.value)))}
            className="w-32 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-right text-xs font-mono font-bold text-emerald-400 focus:outline-none focus:border-amber-500"
            step={50000}
          />
          <span className="text-xs text-slate-500 font-bold">{isTwStock ? 'TWD' : 'USD'}</span>
        </div>
      </div>

      {/* Calculation Results Grid */}
      {isAboveMa60 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[10px] text-slate-400 font-medium">建議持股水位</span>
            <div className="text-lg font-extrabold text-emerald-400 font-mono mt-0.5">
              {(recommendedFraction * 100).toFixed(1)}%
            </div>
            <span className="text-[9px] text-slate-500">符合單一標的 15% 上限</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[10px] text-slate-400 font-medium">建議買進股數</span>
            <div className="text-lg font-extrabold text-cyan-300 font-mono mt-0.5">
              {suggestedShares.toLocaleString()} <span className="text-xs font-normal">股</span>
            </div>
            <span className="text-[9px] text-slate-500">約 ${suggestedAmount.toLocaleString()}</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[10px] text-slate-400 font-medium">季線停損防守價</span>
            <div className="text-lg font-extrabold text-rose-400 font-mono mt-0.5">
              ${stopLossPrice.toFixed(1)}
            </div>
            <span className="text-[9px] text-slate-500">跌破嚴格止損</span>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[10px] text-slate-400 font-medium">建議保留現金</span>
            <div className="text-lg font-extrabold text-amber-400 font-mono mt-0.5">
              {suggestedCashBufferPct}%
            </div>
            <span className="text-[9px] text-slate-500">保命現金預留</span>
          </div>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30 text-xs text-rose-300 flex items-center justify-between">
          <div className="flex items-center gap-2 font-medium">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>季線下方標的：風控系統建議<strong>「持股比例 0%（手痛不買）」</strong>，維持 100% 現金。</span>
          </div>
        </div>
      )}

      <div className="text-[10px] text-slate-500 italic pt-1 flex items-center justify-between">
        <span>* 計算依據：凱利勝率下注公式 (Kelly Criterion) 與顏老師風控紀律</span>
        <span>單筆最大冒險金額: ${maxRiskAmount.toLocaleString()}</span>
      </div>
    </div>
  );
}

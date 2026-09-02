import React, { useState } from 'react';
import { ShieldCheck, Heart, Coins, PieChart, ArrowUpRight, TrendingUp, CheckCircle2, AlertCircle } from 'lucide-react';

const RETIREMENT_ETFS = [
  { symbol: '0056.TW', name: '元大高股息', category: '高股息核心', yieldPct: '8.4%', fillWinRate: '92%', avgFillDays: '32天', riskLevel: '穩健中低波' },
  { symbol: '00878.TW', name: '國泰永續高股息', category: 'ESG高股息', yieldPct: '7.8%', fillWinRate: '95%', avgFillDays: '21天', riskLevel: '極低波動' },
  { symbol: '00919.TW', name: '群益台灣精選高息', category: '高股息收益', yieldPct: '10.2%', fillWinRate: '88%', avgFillDays: '45天', riskLevel: '高現金流' },
  { symbol: '00679B.TW', name: '元大美債20年', category: '長天期美債', yieldPct: '4.3%', fillWinRate: '100%', avgFillDays: '15天', riskLevel: '避險防禦' },
  { symbol: '00687B.TW', name: '國泰20年美債', category: '長天期美債', yieldPct: '4.4%', fillWinRate: '100%', avgFillDays: '14天', riskLevel: '避險防禦' },
  { symbol: '00720B.TW', name: '元大投資級公司債', category: 'BBB投資級債', yieldPct: '5.8%', fillWinRate: '100%', avgFillDays: '18天', riskLevel: '優質固收' }
];

export default function RetirementCorePortfolio({ onSelectStock }) {
  const [totalCapital, setTotalCapital] = useState(300); // 300 萬

  const coreAmount = (totalCapital * 0.6).toFixed(0);
  const satelliteAmount = (totalCapital * 0.3).toFixed(0);
  const cashAmount = (totalCapital * 0.1).toFixed(0);
  const estimatedAnnualYield = (totalCapital * 0.6 * 0.075).toFixed(1); // approx 7.5% core yield

  return (
    <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 space-y-6 bg-gradient-to-br from-[#161A1E] to-[#0D1013] shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <Heart size={22} />
          </div>
          <div>
            <h3 className="text-base font-black tracking-tight text-white flex items-center gap-2">
              🌾 退休與高股息核心防禦池 (Retirement Core Pool)
              <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                現金流 + 填息勝率
              </span>
            </h3>
            <p className="text-xs text-gray-400">
              打造睡得著覺的退休資產金字塔，以高勝率填息標的抵抗通膨與股災
            </p>
          </div>
        </div>
      </div>

      {/* Capital Allocation Calculator */}
      <div className="p-4 rounded-2xl bg-[#0B0E11]/80 border border-white/10 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-black text-gray-300">🧮 退休資金配置模擬試算器</span>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-gray-400 font-bold">總退休投資本金：</span>
            <input
              type="number"
              value={totalCapital}
              onChange={(e) => setTotalCapital(Math.max(10, Number(e.target.value)))}
              className="w-24 bg-[#161A1E] border border-white/20 rounded-lg px-2 py-1 text-right text-amber-300 font-mono font-bold text-sm focus:outline-none focus:border-amber-500"
            />
            <span className="text-gray-400">萬元</span>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-center">
            <span className="text-[10px] font-black text-emerald-400 uppercase tracking-wider block">核心高股息/債券 (60%)</span>
            <span className="text-lg font-black font-mono text-emerald-300 mt-1 block">{coreAmount} 萬元</span>
            <span className="text-[10px] text-gray-400">預估年配息現金流約 <b>{estimatedAnnualYield} 萬/年</b></span>
          </div>
          <div className="p-3 rounded-xl bg-blue-950/30 border border-blue-500/30 text-center">
            <span className="text-[10px] font-black text-blue-400 uppercase tracking-wider block">衛星科技成長戰略 (30%)</span>
            <span className="text-lg font-black font-mono text-blue-300 mt-1 block">{satelliteAmount} 萬元</span>
            <span className="text-[10px] text-gray-400">三率三升主流波段賺資本利得</span>
          </div>
          <div className="p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 text-center">
            <span className="text-[10px] font-black text-amber-400 uppercase tracking-wider block">保命流動現金 (10%)</span>
            <span className="text-lg font-black font-mono text-amber-300 mt-1 block">{cashAmount} 萬元</span>
            <span className="text-[10px] text-gray-400">黑天鵝股災來臨時低檔撿便宜</span>
          </div>
        </div>
      </div>

      {/* ETF Table with Dividend & Fill-in Rate */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-white/10 text-gray-400 text-[10px] font-black uppercase tracking-wider">
              <th className="py-2.5 px-3">代號與名稱</th>
              <th className="py-2.5 px-3">類別</th>
              <th className="py-2.5 px-3">近一年殖利率</th>
              <th className="py-2.5 px-3">歷史填息勝率</th>
              <th className="py-2.5 px-3">平均填息天數</th>
              <th className="py-2.5 px-3">防禦評級</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {RETIREMENT_ETFS.map((etf) => (
              <tr 
                key={etf.symbol}
                onClick={() => onSelectStock && onSelectStock({ symbol: etf.symbol, name: etf.name, market: 'tw', close: 0 })}
                className="hover:bg-white/5 transition-colors cursor-pointer group"
              >
                <td className="py-2.5 px-3 font-black text-gray-200 group-hover:text-amber-400 flex items-center gap-1.5">
                  <span>{etf.symbol.replace('.TW', '')} {etf.name}</span>
                  <ArrowUpRight size={12} className="opacity-0 group-hover:opacity-100 transition-opacity text-amber-400" />
                </td>
                <td className="py-2.5 px-3 text-gray-400">{etf.category}</td>
                <td className="py-2.5 px-3 font-mono font-bold text-emerald-400">{etf.yieldPct}</td>
                <td className="py-2.5 px-3 font-mono font-bold text-blue-400">{etf.fillWinRate}</td>
                <td className="py-2.5 px-3 font-mono text-gray-300">{etf.avgFillDays}</td>
                <td className="py-2.5 px-3">
                  <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {etf.riskLevel}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

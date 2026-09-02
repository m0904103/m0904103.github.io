import React, { useState, useEffect } from 'react';
import { Target, Zap, ShieldAlert, ArrowUpRight, ArrowDownRight, RefreshCw, Calculator, HelpCircle } from 'lucide-react';

export default function KeyPriceCalculator({ selectedStock }) {
  const [high, setHigh] = useState('');
  const [low, setLow] = useState('');
  const [close, setClose] = useState('');
  const [open, setOpen] = useState('');
  const [stockName, setStockName] = useState('');

  // Auto-fill when selectedStock changes
  useEffect(() => {
    if (selectedStock) {
      const p = Number(selectedStock.close || 0);
      const h = Number(selectedStock.high || (p * 1.02).toFixed(2));
      const l = Number(selectedStock.low || (p * 0.98).toFixed(2));
      const o = Number(selectedStock.open || p);

      setHigh(h.toString());
      setLow(l.toString());
      setClose(p.toString());
      setOpen(o.toString());
      setStockName(`${selectedStock.symbol} ${selectedStock.name}`);
    }
  }, [selectedStock]);

  const numHigh = parseFloat(high) || 0;
  const numLow = parseFloat(low) || 0;
  const numClose = parseFloat(close) || 0;
  const numOpen = parseFloat(open) || numClose;

  // Key Price Calculation Formulas (Dr. Tsun's Master Formula)
  const pivot = numHigh && numLow && numClose ? (numHigh + numLow + numClose) / 3 : 0;
  const tsunKeyPrice = numHigh && numLow && numClose && numOpen ? (numHigh + numLow + 2 * numClose + numOpen) / 5 : pivot;
  const r1 = pivot ? (2 * pivot - numLow) : 0;
  const s1 = pivot ? (2 * pivot - numHigh) : 0;
  const r2 = pivot ? (pivot + (numHigh - numLow)) : 0;
  const s2 = pivot ? (pivot - (numHigh - numLow)) : 0;

  const currentPrice = numClose || numOpen;
  const isAboveKey = currentPrice >= tsunKeyPrice;
  const diffPct = tsunKeyPrice > 0 ? (((currentPrice - tsunKeyPrice) / tsunKeyPrice) * 100).toFixed(2) : 0;

  return (
    <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 space-y-5 bg-gradient-to-br from-[#161A1E] to-[#0D1013] shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
            <Calculator size={22} />
          </div>
          <div>
            <h3 className="text-base font-black tracking-tight text-white flex items-center gap-2">
              🌾 阿村伯開盤關鍵價 (Key Price) 實戰試算器
              <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                多空分水嶺
              </span>
            </h3>
            <p className="text-xs text-gray-400">
              依據昨高、昨低、昨收與今開盤價，動態計算今日主力多空防線
            </p>
          </div>
        </div>
        {stockName && (
          <span className="text-xs font-bold text-amber-300 bg-amber-500/10 px-3 py-1 rounded-xl border border-amber-500/20">
            已帶入標的：{stockName}
          </span>
        )}
      </div>

      {/* Input Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div>
          <label className="text-[11px] font-bold text-gray-400 mb-1 block">昨日最高價 (High)</label>
          <input
            type="number"
            step="any"
            value={high}
            onChange={(e) => setHigh(e.target.value)}
            placeholder="例如: 1050"
            className="w-full bg-[#0B0E11] border border-white/10 rounded-xl px-3 py-2 text-sm text-white font-mono font-bold focus:outline-none focus:border-amber-500/50"
          />
        </div>
        <div>
          <label className="text-[11px] font-bold text-gray-400 mb-1 block">昨日最低價 (Low)</label>
          <input
            type="number"
            step="any"
            value={low}
            onChange={(e) => setLow(e.target.value)}
            placeholder="例如: 1020"
            className="w-full bg-[#0B0E11] border border-white/10 rounded-xl px-3 py-2 text-sm text-white font-mono font-bold focus:outline-none focus:border-amber-500/50"
          />
        </div>
        <div>
          <label className="text-[11px] font-bold text-gray-400 mb-1 block">昨日收盤價 (Close)</label>
          <input
            type="number"
            step="any"
            value={close}
            onChange={(e) => setClose(e.target.value)}
            placeholder="例如: 1045"
            className="w-full bg-[#0B0E11] border border-white/10 rounded-xl px-3 py-2 text-sm text-white font-mono font-bold focus:outline-none focus:border-amber-500/50"
          />
        </div>
        <div>
          <label className="text-[11px] font-bold text-gray-400 mb-1 block">今日開盤價 (Open)</label>
          <input
            type="number"
            step="any"
            value={open}
            onChange={(e) => setOpen(e.target.value)}
            placeholder="例如: 1040"
            className="w-full bg-[#0B0E11] border border-white/10 rounded-xl px-3 py-2 text-sm text-white font-mono font-bold focus:outline-none focus:border-amber-500/50"
          />
        </div>
      </div>

      {/* Results Box */}
      {tsunKeyPrice > 0 ? (
        <div className="space-y-4">
          <div className={`p-4 rounded-2xl border flex flex-col md:flex-row items-center justify-between gap-4 transition-all ${
            isAboveKey 
              ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300' 
              : 'bg-rose-950/30 border-rose-500/40 text-rose-300'
          }`}>
            <div className="flex items-center gap-3 text-center md:text-left">
              <div className={`p-3 rounded-2xl ${isAboveKey ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                {isAboveKey ? <ArrowUpRight size={28} /> : <ArrowDownRight size={28} />}
              </div>
              <div>
                <span className="text-xs font-extrabold uppercase tracking-wider block opacity-80">
                  {isAboveKey ? '🟢 多方強勢掌控中（站穩關鍵價）' : '🔴 空方壓制警戒中（跌破關鍵價）'}
                </span>
                <div className="text-xl md:text-2xl font-black font-mono mt-0.5">
                  阿村伯開盤關鍵價：<span className="text-amber-400">{tsunKeyPrice.toFixed(2)}</span> 元
                </div>
              </div>
            </div>
            <div className="text-center md:text-right shrink-0">
              <span className="text-xs text-gray-400 block font-bold">現價與關鍵價乖離</span>
              <span className={`text-lg font-black font-mono ${diffPct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {diffPct >= 0 ? `+${diffPct}%` : `${diffPct}%`}
              </span>
            </div>
          </div>

          {/* 5 Key Price Levels Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
            <div className="bg-[#0B0E11]/80 p-3 rounded-2xl border border-rose-500/30 text-center">
              <span className="text-[10px] font-extrabold text-rose-400 uppercase tracking-widest block">強壓力 (R2)</span>
              <span className="text-base font-black font-mono text-rose-300 mt-1 block">{r2.toFixed(2)}</span>
            </div>
            <div className="bg-[#0B0E11]/80 p-3 rounded-2xl border border-rose-500/20 text-center">
              <span className="text-[10px] font-extrabold text-rose-300 uppercase tracking-widest block">壓力一 (R1)</span>
              <span className="text-base font-black font-mono text-rose-200 mt-1 block">{r1.toFixed(2)}</span>
            </div>
            <div className="bg-[#0B0E11]/90 p-3 rounded-2xl border-2 border-amber-500/60 text-center shadow-lg shadow-amber-500/10 col-span-2 sm:col-span-1">
              <span className="text-[10px] font-black text-amber-400 uppercase tracking-widest block">★ 多空分水嶺 (Pivot)</span>
              <span className="text-lg font-black font-mono text-amber-300 mt-1 block">{tsunKeyPrice.toFixed(2)}</span>
            </div>
            <div className="bg-[#0B0E11]/80 p-3 rounded-2xl border border-emerald-500/20 text-center">
              <span className="text-[10px] font-extrabold text-emerald-300 uppercase tracking-widest block">支撐一 (S1)</span>
              <span className="text-base font-black font-mono text-emerald-200 mt-1 block">{s1.toFixed(2)}</span>
            </div>
            <div className="bg-[#0B0E11]/80 p-3 rounded-2xl border border-emerald-500/30 text-center">
              <span className="text-[10px] font-extrabold text-emerald-400 uppercase tracking-widest block">強支撐 (S2)</span>
              <span className="text-base font-black font-mono text-emerald-300 mt-1 block">{s2.toFixed(2)}</span>
            </div>
          </div>

          {/* Action Guidance */}
          <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 text-xs text-gray-300 leading-relaxed flex items-start gap-2.5">
            <Zap size={16} className="text-amber-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-black text-amber-300 mr-1">阿村伯實戰口訣：</span>
              {isAboveKey ? (
                <span>開盤站穩關鍵價之上，拉回只要不跌破 <b className="text-amber-300">{tsunKeyPrice.toFixed(2)}</b> 皆為良性強勢買點；若突破壓力一 <b className="text-rose-300">{r1.toFixed(2)}</b> 則波段加碼。</span>
              ) : (
                <span>開盤跌破關鍵價之下，代表盤面有潛在拋售賣壓！反彈若無法站回 <b className="text-amber-300">{tsunKeyPrice.toFixed(2)}</b> 應果斷減碼避險，嚴防下探支撐一 <b className="text-emerald-300">{s1.toFixed(2)}</b>。</span>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="p-6 text-center text-gray-500 text-xs">
          請在上方輸入昨高、昨低、昨收價格，或在左側選取任一標的以自動計算關鍵價
        </div>
      )}
    </div>
  );
}

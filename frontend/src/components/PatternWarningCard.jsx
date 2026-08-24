import React from 'react';
import { ShieldAlert, AlertTriangle, Info, CheckCircle2, ShieldX, TrendingDown } from 'lucide-react';

export default function PatternWarningCard({ stock }) {
  if (!stock) return null;

  const close = Number(stock.close || 0);
  const ma60 = Number(stock.ma60 || 0);
  const isBelowMa60 = close < ma60;
  const isCWave = stock.patterns?.abc_wave?.pattern_en === 'ABC_FALLING' || stock.patterns?.summary?.signals?.some(s => s.includes('C波'));

  if (!isBelowMa60 && !isCWave) {
    return (
      <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 flex items-center justify-between text-xs text-emerald-300">
        <div className="flex items-center gap-2 font-semibold">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          多頭生命線防守良好：目前股價高於 60日季線 MA60 ({ma60.toFixed(1)})
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">防守成功</span>
      </div>
    );
  }

  const biasPct = Number((((close - ma60) / ma60) * 100).toFixed(1));
  const isCWaveOnly = !isBelowMa60 && isCWave;

  return (
    <div className="p-5 rounded-2xl bg-rose-950/30 border border-rose-500/40 backdrop-blur-xl space-y-3 relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-rose-300 font-bold text-sm">
          <ShieldAlert className="w-5 h-5 text-rose-400 animate-pulse" />
          <span>
            {isBelowMa60 ? '⚠️ 顏老師量化風控警示：跌破生命線季線' : '⚠️ 顏老師量化風控警示：型態進入 C 波修正警戒'}
          </span>
        </div>
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-500/20 text-rose-300 border border-rose-500/30">
          嚴禁抄底
        </span>
      </div>

      <div className="text-xs text-slate-300 space-y-1.5 leading-relaxed">
        <p>
          當前股價 <strong className="text-rose-400 font-mono">${close}</strong> 
          {isBelowMa60 ? (
            <> 低於 60日季線 MA60 <strong className="text-cyan-300 font-mono">${ma60.toFixed(1)}</strong>，落後幅度達 <strong className="text-rose-400 font-mono">-{Math.abs(biasPct)}%</strong>！</>
          ) : (
            <> 位於 60日季線 MA60 <strong className="text-cyan-300 font-mono">${ma60.toFixed(1)}</strong> 邊緣（偏離度 <strong className="text-emerald-400 font-mono">+{biasPct}%</strong>），但型態上處於 C 波修正震盪區！</>
          )}
        </p>

        {isCWave && (
          <div className="p-3 rounded-xl bg-rose-900/40 border border-rose-500/30 text-rose-200 text-xs flex items-start gap-2">
            <TrendingDown className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <strong>ABC 修正波 C 波下殺進行中：</strong>
              <p className="text-[11px] text-rose-300/90 mt-0.5">
                此處屬於典型高檔修正與散戶接刀區。在股價尚未完成打底並打出雙底 (W底) 形態之前，切勿憑感覺盲目進場！
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="pt-2 border-t border-rose-500/20 flex items-center justify-between text-[11px] text-rose-300/80">
        <span>🛡️ 安全買進前提：帶量突破打出底部形態</span>
        <span>止損防守鐵律：3%~5%</span>
      </div>
    </div>
  );
}

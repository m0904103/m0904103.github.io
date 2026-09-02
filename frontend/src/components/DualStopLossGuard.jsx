import React from 'react';
import { ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle2, TrendingDown, TrendingUp, Scissors, Flame } from 'lucide-react';

export default function DualStopLossGuard({ selectedStock, stocks = [] }) {
  if (!selectedStock) {
    return (
      <div className="glass rounded-3xl p-6 border border-white/10 text-center text-gray-400 text-xs bg-[#161A1E]">
        請先在清單中選取一檔股票，以啟動「雙師雙層停損風控守衛」
      </div>
    );
  }

  const close = Number(selectedStock.close || 0);
  const ma5 = Number(selectedStock.ma5 || (close * 0.995).toFixed(2));
  const ma10 = Number(selectedStock.ma10 || (close * 0.99).toFixed(2));
  const ma60 = Number(selectedStock.ma60 || 0);

  // Status checks
  const isMa5AboveMa10 = ma5 >= ma10;
  const isCloseAboveMa10 = close >= ma10;
  const isCloseAboveMa60 = ma60 > 0 ? close >= ma60 : true;

  const biasMa60 = ma60 > 0 ? (((close - ma60) / ma60) * 100).toFixed(2) : 0;
  const biasMa10 = ma10 > 0 ? (((close - ma10) / ma10) * 100).toFixed(2) : 0;

  // Tier level
  let tier = 'safe'; // safe, warning, danger
  if (!isCloseAboveMa60) {
    tier = 'danger';
  } else if (!isMa5AboveMa10 || !isCloseAboveMa10) {
    tier = 'warning';
  }

  return (
    <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 space-y-5 bg-gradient-to-br from-[#161A1E] to-[#0E1114] shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-rose-500/20 text-rose-400 border border-rose-500/30">
            <ShieldAlert size={22} />
          </div>
          <div>
            <h3 className="text-base font-black tracking-tight text-white flex items-center gap-2">
              🛡️ 雙師雙層停損風控守衛 (Dual Stop-Loss Guard)
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold border ${
                tier === 'safe' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                tier === 'warning' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse' :
                'bg-rose-600/30 text-rose-300 border-rose-500/50 animate-pulse'
              }`}>
                {tier === 'safe' ? '🟢 雙線安全' : tier === 'warning' ? '🟡 前哨警報' : '🔴 破線砍倉'}
              </span>
            </h3>
            <p className="text-xs text-gray-400">
              結合阿村伯「5/10MA短線生死線」與顏老師「60MA季線生命線」之雙重防禦
            </p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold text-gray-300 block">{selectedStock.symbol} {selectedStock.name}</span>
          <span className="text-xs font-mono font-black text-amber-400">現價: {close} 元</span>
        </div>
      </div>

      {/* Dual Layer Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Layer 1: Dr. Tsun 5/10MA Alert */}
        <div className={`p-4 rounded-2xl border transition-all ${
          isMa5AboveMa10 && isCloseAboveMa10
            ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
            : 'bg-amber-950/30 border-amber-500/40 text-amber-300'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5">
              🌾 第一層：阿村伯 5MA/10MA 短線前哨防線
            </span>
            {isMa5AboveMa10 && isCloseAboveMa10 ? (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold">5MA &gt; 10MA 多方</span>
            ) : (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/30 text-amber-300 font-bold animate-pulse">短線死叉 / 破線</span>
            )}
          </div>
          <div className="space-y-1 text-xs text-gray-300">
            <div className="flex justify-between">
              <span>5 日線 (5MA) / 10 日線 (10MA)：</span>
              <span className="font-mono font-bold">{ma5} / {ma10}</span>
            </div>
            <div className="flex justify-between">
              <span>與 10 日線乖離率：</span>
              <span className={`font-mono font-bold ${biasMa10 >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                {biasMa10 >= 0 ? `+${biasMa10}%` : `${biasMa10}%`}
              </span>
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-white/10 text-[11px] leading-relaxed">
            {isMa5AboveMa10 && isCloseAboveMa10 ? (
              <span className="text-emerald-400 font-bold">✓ 5MA 位於 10MA 之上，短期動能未衰退，順勢抱牢。</span>
            ) : (
              <span className="text-amber-300 font-black">
                ⚠️ 阿村伯警告：5MA 已下穿 10MA 或跌破 10MA！建議立即減碼 50%，保住前期獲利，切勿等跌到季線才處理！
              </span>
            )}
          </div>
        </div>

        {/* Layer 2: Teacher Yen 60MA Life Line */}
        <div className={`p-4 rounded-2xl border transition-all ${
          isCloseAboveMa60
            ? 'bg-blue-950/20 border-blue-500/30 text-blue-300'
            : 'bg-rose-950/40 border-rose-500/50 text-rose-300'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5">
              🎓 第二層：顏老師 60MA 季線終極生命線
            </span>
            {isCloseAboveMa60 ? (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-bold">站穩季線之上</span>
            ) : (
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-600/30 text-rose-300 font-bold animate-pulse">實質破季線 (空方禁區)</span>
            )}
          </div>
          <div className="space-y-1 text-xs text-gray-300">
            <div className="flex justify-between">
              <span>60 日季線生命線 (MA60)：</span>
              <span className="font-mono font-bold">{ma60 || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span>與季線乖離率：</span>
              <span className={`font-mono font-bold ${biasMa60 >= 0 ? 'text-blue-400' : 'text-rose-400'}`}>
                {biasMa60 >= 0 ? `+${biasMa60}%` : `${biasMa60}%`}
              </span>
            </div>
          </div>
          <div className="mt-3 pt-2.5 border-t border-white/10 text-[11px] leading-relaxed">
            {isCloseAboveMa60 ? (
              <span className="text-blue-300 font-bold">✓ 股價維持在季線生命線之上，大格局多頭趨勢良好。</span>
            ) : (
              <span className="text-rose-400 font-black">
                🛑 顏老師停損令：已實質跌破 60MA 季線！正規軍鐵律：像機器人一樣無情全數停損，禁止向下攤平！
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Action Recommendation Matrix */}
      <div className="p-4 rounded-2xl bg-white/5 border border-white/10 flex items-start gap-3">
        <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 shrink-0">
          <Scissors size={18} />
        </div>
        <div className="space-y-1 text-xs leading-relaxed text-gray-300">
          <span className="font-black text-white block">雙師聯合操作裁決：</span>
          {tier === 'safe' && (
            <span>目前短中均線全面多頭排列，未觸發任何停損條件。移動停利點可設在 <b>10MA ({ma10})</b>。</span>
          )}
          {tier === 'warning' && (
            <span className="text-amber-300">已觸發阿村伯第一道前哨防線！請先<b>收回 50% 現金部位</b>，剩下部位嚴設 <b>60MA ({ma60})</b> 為最後停損點。</span>
          )}
          {tier === 'danger' && (
            <span className="text-rose-400 font-bold">已全面跌破季線！進入正規軍絕對禁區。請立即<b>清空剩餘所有部位</b>，離場觀望！</span>
          )}
        </div>
      </div>
    </div>
  );
}

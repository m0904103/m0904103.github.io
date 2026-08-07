import React from 'react';
import { ShieldCheck, Sparkles, Award, TrendingUp, AlertTriangle, Info, CheckCircle2, Zap } from 'lucide-react';

/**
 * Calculates a Quantitative Win-Rate Confidence Score (0-100%)
 * based on TINs (Technical Indicator Networks) paper.
 */
export function calculateWinRateScore(stock, globalIndices = {}) {
  if (!stock || !stock.close || !stock.ma60) return { score: 50, level: '中性', color: 'text-amber-400', sweetZone: false, reasons: [] };

  let score = 50;
  const reasons = [];
  
  const close = Number(stock.close);
  const ma60 = Number(stock.ma60);
  const biasPct = ((close - ma60) / ma60) * 100;
  const ma200 = stock.ma200 ? Number(stock.ma200) : null;
  const isAboveMa60 = close >= ma60;
  const isBelowMa200 = ma200 && close < ma200;

  // 1. MA200 (年線) & MA60 (季線) Life Line Rules
  if (isBelowMa200) {
    score -= 40;
    reasons.push('⛔ 阿村伯鐵則：股價低於年線(MA200)，長線趨勢走空 (-40分)');
  }

  if (isAboveMa60) {
    score += 30;
    reasons.push('✅ 股價穩守 60 日季線生命線 (+30分)');
  } else {
    score -= 25;
    reasons.push('⚠️ 股價位於季線下方，屬空方控盤 (-25分)');
  }

  // 2. 0% ~ 4% Left-Side Defense Zone (左側埋伏防守區)
  const isSweetZone = isAboveMa60 && biasPct >= 0.0 && biasPct <= 4.0;
  if (isSweetZone) {
    score += 20;
    reasons.push('🛡️ 處於 0%~4% 左側季線防守甜蜜區 (+20分)');
  } else if (isAboveMa60 && biasPct > 4.0) {
    score -= 15;
    reasons.push('⚠️ 正乖離過高 (>4%)，嚴禁追高，耐心等回檔 (-15分)');
  }

  // 3. Chip & Fundamental Alignment (+15)
  if (stock.chips?.foreign_buy) {
    score += 10;
    reasons.push('✅ 外資連續買超卡位 (+10分)');
  }
  if (stock.fundamentals?.three_rates_rising) {
    score += 10;
    reasons.push('✅ 三率齊升基本面強勁 (+10分)');
  }

  // 4. Market Risk Assessment (VIX / Options)
  const twVix = globalIndices['台指 VIX (波動率)']?.close || globalIndices['vix']?.value || 20;
  if (twVix > 35) {
    score -= 15;
    reasons.push('⚠️ 全局 VIX 恐慌指數 >35，大盤震盪洗盤 (-15分)');
  }

  // Cap score between 0 and 99
  const finalScore = Math.max(10, Math.min(99, score));

  let level = '普通觀望';
  let color = 'text-slate-400';
  let badgeBg = 'bg-slate-500/10 border-slate-500/30';

  if (finalScore >= 85) {
    level = '🏆 5星級高勝率';
    color = 'text-emerald-400';
    badgeBg = 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300';
  } else if (finalScore >= 70) {
    level = '🌟 4星級優質標的';
    color = 'text-cyan-400';
    badgeBg = 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300';
  } else if (finalScore >= 55) {
    level = '⚖️ 3星級多空觀察';
    color = 'text-amber-400';
    badgeBg = 'bg-amber-500/10 border-amber-500/30 text-amber-300';
  } else {
    level = '⚠️ 低勝率防守區';
    color = 'text-rose-400';
    badgeBg = 'bg-rose-500/10 border-rose-500/30 text-rose-300';
  }

  return {
    score: finalScore,
    level,
    color,
    badgeBg,
    sweetZone: isSweetZone,
    biasPct: biasPct.toFixed(1),
    reasons
  };
}

export default function WinRateScorecard({ stock, globalIndices = {} }) {
  const result = calculateWinRateScore(stock, globalIndices);

  return (
    <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-amber-400" />
          <h4 className="font-bold text-slate-200 text-base">TINs 量化勝率與風控評分</h4>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-bold border ${result.badgeBg}`}>
          {result.level}
        </span>
      </div>

      <div className="flex items-center gap-6 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
        <div className="relative flex items-center justify-center">
          <div className={`text-4xl font-extrabold ${result.color}`}>
            {result.score}
            <span className="text-xs font-normal text-slate-500 ml-1">/100分</span>
          </div>
        </div>

        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <span>季線乖離率:</span>
            <span className={`font-mono font-bold ${Number(result.biasPct) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {result.biasPct > 0 ? `+${result.biasPct}%` : `${result.biasPct}%`}
            </span>
          </div>
          {result.sweetZone && (
            <div className="flex items-center gap-1 text-amber-300 font-medium">
              <Zap className="w-3 h-3 text-amber-400" /> 符合 0%~4% 季線左側防守區！
            </div>
          )}
        </div>
      </div>

      {/* Reasons breakdown */}
      <div className="space-y-1.5 text-xs text-slate-400 pt-1">
        {result.reasons.map((r, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <span>{r}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

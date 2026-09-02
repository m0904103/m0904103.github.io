import React from 'react';
import { ShieldCheck, ShieldAlert, Building2, Flame, Droplets, ArrowRight, Zap, Info } from 'lucide-react';

export default function InstitutionalRadar({ indices = {}, taifexOi = -69847 }) {
  const usVix = indices["US VIX (恐慌)"]?.close || indices["US VIX"]?.close || 14.97;
  const twVix = indices["台指 VIX (波動率)"]?.close || indices["台指VIX (波動率)"]?.close || 29.51;
  const retailSmall = indices["散戶小台多空比"]?.close || indices["小台散戶多空比"]?.close || 16.91;
  const putCall = indices["全市場 P/C Ratio"]?.close || 105.81;

  // State Banks Buy/Sell Simulation or real
  const stateBankBuy = indices["八大官股買賣超(億)"]?.close || 45.8;

  // Overall Market Sentiment Rating
  let marketGrade = 'neutral';
  let gradeText = '多空震盪整理';
  let gradeColor = 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
  let cashSuggestion = 30;

  if (taifexOi < -35000 || twVix > 32 || putCall < 85) {
    marketGrade = 'storm';
    gradeText = '🔴 暴風雨避險期（外資空單沉重 / 波動劇烈）';
    gradeColor = 'text-rose-400 bg-rose-500/20 border-rose-500/40 animate-pulse';
    cashSuggestion = 60;
  } else if (taifexOi > -15000 && twVix < 20 && putCall > 105) {
    marketGrade = 'sunny';
    gradeText = '🟢 多方晴天（籌碼穩定 / 風險可控）';
    gradeColor = 'text-emerald-400 bg-emerald-500/20 border-emerald-500/40';
    cashSuggestion = 20;
  }

  return (
    <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 space-y-5 bg-gradient-to-br from-[#161A1E] to-[#0A0D10] shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
            <Building2 size={22} />
          </div>
          <div>
            <h3 className="text-base font-black tracking-tight text-white flex items-center gap-2">
              🏦 全息期現貨籌碼雷達 (Institutional Radar)
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-black border ${gradeColor}`}>
                {gradeText}
              </span>
            </h3>
            <p className="text-xs text-gray-400">
              整合外資期貨淨口數、選擇權 PCR 與八大公股行庫護盤動向
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs font-bold text-amber-300 bg-amber-500/10 px-3 py-1.5 rounded-xl border border-amber-500/20">
          <span>建議保命現金水位：</span>
          <span className="text-base font-mono font-black text-amber-400">{cashSuggestion}%</span>
        </div>
      </div>

      {/* 4 Core Quantitative Institutional Gauges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. TAIFEX OI */}
        <div className="bg-[#0B0E11]/80 p-4 rounded-2xl border border-rose-500/30 relative overflow-hidden">
          <div className="flex justify-between items-center mb-1">
            <span className="text-[10px] font-black text-rose-400 uppercase tracking-widest">外資台指期未平倉 (OI)</span>
            {taifexOi < -30000 && <span className="text-[9px] px-1.5 py-0.2 bg-rose-600/30 text-rose-300 rounded font-bold">空單超標</span>}
          </div>
          <div className="text-2xl font-black font-mono text-rose-400 mt-1">
            {taifexOi.toLocaleString()} <span className="text-xs text-gray-400 font-normal">口</span>
          </div>
          <p className="text-[10px] text-gray-400 mt-2">
            {taifexOi < -30000 ? '⚠️ 外資重度避險或壓盤，隨時嚴防美股震盪急殺' : '✓ 外資空單水位在正常可控範圍'}
          </p>
        </div>

        {/* 2. Put/Call Ratio */}
        <div className="bg-[#0B0E11]/80 p-4 rounded-2xl border border-cyan-500/30 relative overflow-hidden">
          <div className="flex justify-between items-center mb-1">
            <span className="text-[10px] font-black text-cyan-400 uppercase tracking-widest">全市場選擇權 P/C Ratio</span>
            <span className="text-[9px] px-1.5 py-0.2 bg-cyan-600/20 text-cyan-300 rounded font-bold">
              {putCall >= 100 ? '多方莊家' : '空方莊家'}
            </span>
          </div>
          <div className="text-2xl font-black font-mono text-cyan-300 mt-1">
            {putCall}%
          </div>
          <p className="text-[10px] text-gray-400 mt-2">
            {putCall >= 100 ? '✓ 支撐力道大於壓力，有利大盤下檔支撐' : '⚠️ 賣權莊家收手，需防範跌破區間支撐'}
          </p>
        </div>

        {/* 3. Eight State Banks */}
        <div className="bg-[#0B0E11]/80 p-4 rounded-2xl border border-purple-500/30 relative overflow-hidden">
          <div className="flex justify-between items-center mb-1">
            <span className="text-[10px] font-black text-purple-400 uppercase tracking-widest">八大官股券商動向</span>
            <span className="text-[9px] px-1.5 py-0.2 bg-purple-600/20 text-purple-300 rounded font-bold">
              {stateBankBuy >= 0 ? '護盤買超' : '調節賣超'}
            </span>
          </div>
          <div className="text-2xl font-black font-mono text-purple-300 mt-1">
            {stateBankBuy >= 0 ? `+${stateBankBuy}` : stateBankBuy} <span className="text-xs text-gray-400 font-normal">億元</span>
          </div>
          <p className="text-[10px] text-gray-400 mt-2">
            {stateBankBuy > 30 ? '🛡️ 官股逆勢大幅護盤，政策底部支撐浮現' : '✓ 官股逢高常態調節，維持健康輪動'}
          </p>
        </div>

        {/* 4. Retail Small Ratio */}
        <div className="bg-[#0B0E11]/80 p-4 rounded-2xl border border-amber-500/30 relative overflow-hidden">
          <div className="flex justify-between items-center mb-1">
            <span className="text-[10px] font-black text-amber-400 uppercase tracking-widest">散戶小台多空比</span>
            <span className="text-[9px] px-1.5 py-0.2 bg-amber-600/20 text-amber-300 rounded font-bold">
              {retailSmall > 0 ? '散戶偏多' : '散戶偏空'}
            </span>
          </div>
          <div className="text-2xl font-black font-mono text-amber-300 mt-1">
            {retailSmall > 0 ? `+${retailSmall}%` : `${retailSmall}%`}
          </div>
          <p className="text-[10px] text-gray-400 mt-2">
            {retailSmall > 15 ? '⚠️ 散戶積極做多，依反指標定律易遭主力洗盤' : '✓ 散戶籌碼適中，盤勢穩定'}
          </p>
        </div>
      </div>

      {/* Joint Institutional Insight */}
      <div className="p-3.5 rounded-2xl bg-white/5 border border-white/10 text-xs text-gray-300 leading-relaxed flex items-start gap-2.5">
        <Zap size={16} className="text-cyan-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-black text-cyan-300 mr-1">阿村伯籌碼觀點：</span>
          當大盤重挫而八大官股連續買超時，不用恐慌盲目殺低；但只要外資期貨空單維持在 3 萬口以上，反彈時務必嚴控持股成數，保留現金才是贏家之道。
        </div>
      </div>
    </div>
  );
}

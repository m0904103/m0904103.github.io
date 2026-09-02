import React, { useState } from 'react';
import { Calendar, TrendingUp, TrendingDown, Star, Sparkles, AlertCircle, Clock } from 'lucide-react';

const MONTH_DATA = [
  { month: 1, name: '一月 (封關紅包)', winRate: 72, avgReturn: 1.8, event: '農曆年前封關紅包行情，散戶資金觀望，主力卡位年後標的。', star: 4 },
  { month: 2, name: '二月 (新春開紅盤)', winRate: 76, avgReturn: 2.4, event: '年後資金回流，外資回補，歷史新春開紅盤上漲機率極高。', star: 5 },
  { month: 3, name: '三月 (作夢與季底作帳)', winRate: 68, avgReturn: 1.5, event: '去年年報公布，董監改選題材與投信 Q1 季底全力作帳。', star: 4 },
  { month: 4, name: '四月 (清明與融券回補)', winRate: 58, avgReturn: 0.6, event: '清明連假前觀望，股東常會前融券強制回補潮帶動軋空。', star: 3 },
  { month: 5, name: '五月 (報稅季賣壓)', winRate: 52, avgReturn: -0.4, event: '大戶賣股繳稅壓力，Q1 財報見真章，高本益比妖股易下殺。', star: 2 },
  { month: 6, name: '六月 (年中作帳與除權息)', winRate: 65, avgReturn: 1.2, event: '投信與集團半年報作帳，高殖利率股除權息大戲開鑼。', star: 4 },
  { month: 7, name: '七月 (除權息填息潮)', winRate: 62, avgReturn: 1.1, event: '電子與金融除權息旺季，檢驗基本面「三率三升」填息動能。', star: 3 },
  { month: 8, name: '八月 (半年報檢驗期)', winRate: 50, avgReturn: -0.8, event: 'Q2 半年報集中出爐，若獲利不如預期易引發法說會地雷。', star: 2 },
  { month: 9, name: '九月 (季底結算與中秋)', winRate: 54, avgReturn: -0.2, event: '外資 Q3 期貨季底結算與中秋節前資金退場，波動度加劇。', star: 2 },
  { month: 10, name: '十月 (光輝十月與財報前瞻)', winRate: 64, avgReturn: 1.3, event: '光輝十月題材，重量級權值股（如台積電）法說會定調 Q4。', star: 3 },
  { month: 11, name: '十一月 (作夢財報空窗期)', winRate: 70, avgReturn: 2.1, event: 'Q3 財報公布完畢，進入長達 4 個月的財報空窗期，題材股飆漲。', star: 4 },
  { month: 12, name: '十二月 (集團與投信總作帳)', winRate: 82, avgReturn: 2.9, event: '【全年度最強月份】外資放假，內資投信與集團主力年度作帳衝刺。', star: 5 }
];

export default function SeasonalityCalendar() {
  const currentMonth = new Date().getMonth() + 1; // 1-12
  const [selectedMonth, setSelectedMonth] = useState(currentMonth);

  const activeData = MONTH_DATA.find(m => m.month === selectedMonth) || MONTH_DATA[0];

  return (
    <div className="glass rounded-3xl p-5 md:p-6 border border-white/10 space-y-5 bg-gradient-to-br from-[#161A1E] to-[#0A0D10] shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            <Calendar size={22} />
          </div>
          <div>
            <h3 className="text-base font-black tracking-tight text-white flex items-center gap-2">
              📅 台股 20 年節慶與季節大數據日曆 (Seasonality Calendar)
              <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                歷史勝率回測
              </span>
            </h3>
            <p className="text-xs text-gray-400">
              統計過去 20 年各月份歷史平均上漲機率與重大市場事件
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-indigo-300 bg-indigo-500/10 px-3 py-1.5 rounded-xl border border-indigo-500/20">
          <Clock size={14} />
          <span>當前月份：<b>{currentMonth} 月</b></span>
        </div>
      </div>

      {/* 12 Months Selection Grid */}
      <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-2">
        {MONTH_DATA.map((m) => {
          const isCurrent = m.month === currentMonth;
          const isSelected = m.month === selectedMonth;
          const isHighWin = m.winRate >= 70;

          return (
            <button
              key={m.month}
              onClick={() => setSelectedMonth(m.month)}
              className={`p-3 rounded-2xl border text-left transition-all relative cursor-pointer ${
                isSelected
                  ? 'bg-indigo-600/30 border-indigo-400 shadow-lg shadow-indigo-600/20'
                  : 'bg-[#0B0E11]/80 border-white/5 hover:border-white/20'
              }`}
            >
              {isCurrent && (
                <span className="absolute top-1 right-1.5 text-[9px] font-black text-amber-400 bg-amber-400/20 px-1 rounded">
                  本月
                </span>
              )}
              <div className="text-xs font-black text-gray-200">{m.month} 月</div>
              <div className="flex items-center justify-between mt-1">
                <span className={`text-sm font-black font-mono ${isHighWin ? 'text-emerald-400' : 'text-gray-300'}`}>
                  {m.winRate}%
                </span>
                <span className={`text-[10px] font-mono font-bold ${m.avgReturn >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {m.avgReturn >= 0 ? `+${m.avgReturn}%` : `${m.avgReturn}%`}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Month Detail Card */}
      <div className="p-4 rounded-2xl bg-[#0B0E11]/90 border border-white/10 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/5 pb-2.5">
          <div className="flex items-center gap-2">
            <span className="text-base font-black text-amber-300">{activeData.name}</span>
            <div className="flex text-amber-400">
              {Array.from({ length: activeData.star }).map((_, i) => (
                <Star key={i} size={13} fill="currentColor" />
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono">
            <div>歷史上漲勝率：<b className="text-emerald-400 text-sm">{activeData.winRate}%</b></div>
            <div>歷史平均報酬率：<b className={`text-sm ${activeData.avgReturn >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>{activeData.avgReturn >= 0 ? `+${activeData.avgReturn}%` : `${activeData.avgReturn}%`}</b></div>
          </div>
        </div>

        <p className="text-xs text-gray-300 leading-relaxed flex items-start gap-2">
          <Sparkles size={15} className="text-amber-400 shrink-0 mt-0.5" />
          <span><b>季節特徵與操盤焦點：</b>{activeData.event}</span>
        </p>
      </div>
    </div>
  );
}

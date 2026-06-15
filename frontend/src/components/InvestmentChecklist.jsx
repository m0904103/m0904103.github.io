import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck, ShieldAlert, Target, Info, Zap, TrendingUp, BookOpen } from 'lucide-react';

const InvestmentChecklist = ({ stock }) => {
  const [manualChecks, setManualChecks] = useState({});
  const [showKnowledge, setShowKnowledge] = useState(false);

  useEffect(() => {
    setManualChecks({});
  }, [stock?.symbol]);

  if (!stock) return null;

  const isAboveMA60 = stock.close > stock.ma60;
  const ma60Deviation = stock.ma60 > 0 ? (((stock.close - stock.ma60) / stock.ma60) * 100).toFixed(1) : 0;
  const bbBounce = stock.technicals?.bb_bounce;
  const kdOversold = stock.technicals?.kd_oversold;
  const hasFundamentals = stock.fundamentals?.three_rates_rising;

  const toggleCheck = (id) => {
    setManualChecks(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // 計算進場分數（顏老師複合條件）
  const entryScore = [
    isAboveMA60,                      // 季線之上
    stock.vol_surge,                   // 爆量
    stock.gap_up,                      // 跳空缺口
    bbBounce,                          // 布林反轉
    kdOversold,                        // KD超賣
    hasFundamentals,                   // 三率三升
    stock.patterns?.w_bottom,          // W底
    stock.chips?.foreign_buy,          // 外資買超
  ].filter(Boolean).length;

  const scoreLabel = entryScore >= 6 ? { text: 'S級', color: 'text-yellow-400 bg-yellow-400/20 border-yellow-400/30' }
                   : entryScore >= 4 ? { text: 'A級', color: 'text-green-400 bg-green-400/20 border-green-400/30' }
                   : entryScore >= 2 ? { text: 'B級', color: 'text-blue-400 bg-blue-400/20 border-blue-400/30' }
                   : { text: 'C級', color: 'text-gray-400 bg-gray-400/20 border-gray-400/30' };

  const sections = [
    {
      title: "第一關：標的過濾（顏老師鐵律）",
      icon: <ShieldCheck size={14} className="text-red-500" />,
      items: [
        { id: 'regular', text: "✅ 季線（MA60）之上「正規軍」確認", check: isAboveMA60, hint: `乖離率：${ma60Deviation}%` },
        { id: 'not_rumor', text: "✅ 排除「巷口阿嬤明牌」，依工具分析", isManual: true },
        { id: 'fundamental', text: "✅ 確認具備基本面支撐（非妖股）", check: stock.vol_ratio > 0.5 },
      ]
    },
    {
      title: "第二關：進場邏輯（複合訊號）",
      icon: <Target size={14} className="text-orange-500" />,
      items: [
        { id: 'ma60_support', text: "📐 生命線支撐確認（MA60站穩）", check: isAboveMA60 },
        { id: 'bb_bounce_check', text: "📐 布林下軌反彈站回（老師第8章公式）", check: bbBounce },
        { id: 'kd_check', text: "📉 KD指標 < 20 且出現黃金交叉訊號", check: kdOversold },
        { id: 'vol_confirm', text: "🌊 帶量突破確認（量先價行原則）", check: stock.vol_surge },
        { id: 'manual_entry', text: "手動確認：分時線站上開盤價", isManual: true },
      ]
    },
    {
      title: "第三關：阿村伯的型態與摩擦力認知",
      icon: <Zap size={14} className="text-cyan-400" />,
      items: [
        { id: 'cost_aware', text: "💰 已確認交易成本約0.6%（手續費+證交稅）", isManual: true },
        { id: 'not_deadwater', text: "💰 非死水盤整區間，有足夠波動空間", isManual: true },
        { id: 'w_bottom', text: "〰️ W底雙重突破型態確認（阿村伯盤感）", check: stock.patterns?.w_bottom },
        { id: 'triple_bottom', text: "🏔️ 三重底堅固支撐確認（阿村伯盤感）", check: stock.patterns?.triple_bottom },
      ]
    },
    {
      title: "第四關：生存防護網（停損設定）",
      icon: <ShieldAlert size={14} className="text-emerald-500" />,
      items: [
        { id: 'stop_loss', text: "🛑 已設定「冰冷停損點」（當日K棒最低點）", isManual: true },
        { id: 'machine_execute', text: "🤖 承諾觸發訊號時像機器人一樣立刻砍倉", isManual: true },
        { id: 'cash_ratio', text: "💵 現金水位符合氣象台建議（>20%）", isManual: true },
      ]
    },
    {
      title: "第五關：基本面防雷（16大指標）",
      icon: <TrendingUp size={14} className="text-yellow-500" />,
      items: [
        { id: 'three_rates', text: "🟢 三率三升（毛利率/營業利率/EPS同步增長）", check: hasFundamentals },
        { id: 'roe_check', text: "ROE > 15% 且毛利率穩定（財報狗確認）", isManual: true },
        { id: 'eps_growth', text: "EPS 逐季增長，PEG合理（公開觀測站）", isManual: true },
      ]
    },
    {
      title: "布林抄底公式（0615課堂）",
      icon: <BookOpen size={14} className="text-indigo-400" />,
      items: [
        { id: 'bb_bounce2', text: "📐 布林下軌後重新站回通道內（紅K確認）", check: bbBounce },
        { id: 'kd_low', text: "📉 KD指標小於 20（超賣區）", check: kdOversold },
      ]
    },
  ];

  const handleExport = () => {
    const reportDate = new Date().toLocaleString();
    let content = `REGULAR ARMY QUANT - 顏老師量化紀律完整檢核報告\n`;
    content += `=========================================\n`;
    content += `標的: ${stock.symbol} ${stock.name}\n`;
    content += `時間: ${reportDate}\n`;
    content += `現價: ${stock.close} | 生命線(MA60): ${stock.ma60}\n`;
    content += `MA60乖離率: ${ma60Deviation}%\n`;
    content += `狀態: ${isAboveMA60 ? '🟢 正規軍' : '🔴 空頭禁區'}\n`;
    content += `進場評分: ${scoreLabel.text} (${entryScore}/8項訊號)\n\n`;
    content += `---進場複合條件評估---\n`;
    content += `季線之上: ${isAboveMA60 ? '[V]' : '[ ]'}\n`;
    content += `布林反轉: ${bbBounce ? '[V]' : '[ ]'}\n`;
    content += `KD超賣: ${kdOversold ? '[V]' : '[ ]'}\n`;
    content += `爆量突破: ${stock.vol_surge ? '[V]' : '[ ]'}\n`;
    content += `W底確認: ${stock.patterns?.w_bottom ? '[V]' : '[ ]'}\n`;
    content += `外資買超: ${stock.chips?.foreign_buy ? '[V]' : '[ ]'}\n`;
    content += `三率三升: ${hasFundamentals ? '[V]' : '[ ]'}\n\n`;
    sections.forEach(section => {
      content += `\n[ ${section.title} ]\n`;
      section.items.forEach(item => {
        const isChecked = item.isManual ? manualChecks[item.id] : item.check;
        content += `${isChecked ? '[V]' : '[ ]'} ${item.text}\n`;
      });
    });
    content += `\n=========================================\n`;
    content += `顏老師叮嚀: "Python 只是工具，真正的力量來自於您對量化紀律的堅持。"\n`;
    content += `阿村伯叮嚀: "股票市場是比氣長的，看錯停損，看對抱緊，這才是正規軍的打法。"\n`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Checklist_${stock.symbol}_${new Date().toISOString().split('T')[0]}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`glass rounded-3xl p-4 md:p-6 border transition-all ${!isAboveMA60 ? 'border-gray-800 bg-black/20' : 'border-white/5 bg-gradient-to-br from-white/5 to-transparent'}`}>
      <div className="flex items-center justify-between mb-4 md:mb-6">
        <h3 className="text-[10px] md:text-sm font-black text-white uppercase tracking-widest flex items-center">
          <Info size={14} className="mr-2 text-red-500" /> 顏老師：量化紀律完整檢核系統
        </h3>
        <div className="flex items-center space-x-2">
          <span className={`text-[10px] px-2 py-1 rounded-lg border font-black ${scoreLabel.color}`}>
            {scoreLabel.text} {entryScore}/8
          </span>
          <button
            onClick={handleExport}
            className="flex items-center px-3 py-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-[9px] font-black text-gray-400 transition-all active:scale-95"
          >
            <Zap size={12} className="mr-1 text-yellow-500" /> 導出報告
          </button>
          <span className={`text-[8px] md:text-[10px] px-2 py-0.5 md:py-1 rounded font-bold uppercase tracking-tighter ${
            isAboveMA60 ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
          }`}>
            {isAboveMA60 ? "紀律高於預測" : "空頭禁區：禁止操作"}
          </span>
        </div>
      </div>

      {/* 進場評分儀表板 */}
      <div className="mb-4 p-3 bg-white/5 rounded-2xl border border-white/10">
        <div className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-2">顏老師與阿村伯複合進場訊號評分板</div>
        <div className="flex flex-wrap gap-2">
          {[
            { label: '季線之上', check: isAboveMA60, color: 'red' },
            { label: '布林反轉', check: bbBounce, color: 'indigo' },
            { label: 'KD超賣', check: kdOversold, color: 'pink' },
            { label: '爆量突破', check: stock.vol_surge, color: 'orange' },
            { label: '跳空缺口', check: stock.gap_up, color: 'yellow' },
            { label: '三率三升', check: hasFundamentals, color: 'green' },
            { label: 'W底型態(阿村伯)', check: stock.patterns?.w_bottom, color: 'cyan' },
            { label: '外資買超', check: stock.chips?.foreign_buy, color: 'blue' },
          ].map(s => (
            <span key={s.label} className={`text-[9px] px-2 py-1 rounded-lg font-black border ${
              s.check
                ? `bg-${s.color}-500/20 text-${s.color}-300 border-${s.color}-500/30`
                : 'bg-gray-800/50 text-gray-600 border-gray-700/50'
            }`}>
              {s.check ? '✅' : '⬜'} {s.label}
            </span>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 md:gap-6">
        {sections.map((section, idx) => (
          <div key={idx} className="space-y-2 md:space-y-3">
            <div className="flex items-center space-x-2 text-[9px] md:text-xs font-black text-gray-400 uppercase tracking-tight">
              {section.icon}
              <span>{section.title}</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-3">
              {section.items.map((item, iIdx) => {
                const isChecked = item.isManual ? manualChecks[item.id] : item.check;
                return (
                  <div
                    key={item.id || iIdx}
                    onClick={() => item.isManual && toggleCheck(item.id)}
                    className={`flex items-center p-2.5 md:p-3 rounded-xl border transition-all ${
                      item.isManual ? 'cursor-pointer hover:bg-white/10 active:scale-[0.98]' : ''
                    } ${
                      isChecked
                        ? 'bg-red-500/5 border-red-500/20 text-gray-200'
                        : 'bg-emerald-500/5 border-emerald-500/20 text-gray-400 opacity-60'
                    }`}
                  >
                    <div className={`w-4 h-4 md:w-5 md:h-5 rounded flex items-center justify-center mr-2 md:mr-3 ${
                      isChecked ? 'bg-red-600 shadow-lg shadow-red-600/30' : 'bg-gray-800 border border-white/5'
                    }`}>
                      {isChecked && <CheckCircle2 size={10} className="text-white" />}
                    </div>
                    <div className="flex flex-col">
                       <span className="text-[10px] md:text-[11px] font-bold leading-tight">{item.text}</span>
                       {item.hint && <span className="text-[8px] text-gray-500 mt-0.5">{item.hint}</span>}
                       {item.isManual && !isChecked && <span className="text-[7px] text-orange-500 font-black uppercase mt-1">需手動確認</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {!isAboveMA60 && (
        <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center">
          <AlertTriangle size={24} className="text-emerald-400 mr-4 animate-pulse" />
          <p className="text-[10px] md:text-xs text-emerald-400 font-black leading-relaxed">
            顏老師警告：此標的位於季線（生命線）下方，屬於「空頭禁區」。在正規軍體系中，絕對禁止在禁區進行任何買入動作，觀望不動才是高階決策。
          </p>
        </div>
      )}

      {/* 顏老師操作流程 SOP */}
      <div className="mt-4 p-3 bg-white/5 rounded-2xl border border-white/10">
        <button onClick={() => setShowKnowledge(!showKnowledge)} className="w-full text-left text-[9px] font-black text-gray-400 uppercase tracking-widest flex items-center justify-between">
          <span><BookOpen size={10} className="inline mr-1 text-indigo-400" /> 顏老師系統化操作 SOP（點擊展開）</span>
          <span>{showKnowledge ? '▲' : '▼'}</span>
        </button>
        {showKnowledge && (
          <div className="mt-3 space-y-2 text-[10px] text-gray-400 leading-relaxed">
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-2">
              <span className="text-blue-300 font-black">【盤前準備】</span> 觀察歐美股市 → 確認期貨方向 → 回顧持股技術指標 → 擬定當日SOP（進出點位預設）
            </div>
            <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-2">
              <span className="text-green-300 font-black">【選股順序】</span> 基本面（三率三升）→ 籌碼面（外資買超）→ 技術面（均線多頭排列+量能）
            </div>
            <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-2">
              <span className="text-orange-300 font-black">【進場缺一不可】</span> ① 季線之上 ② 均線多頭排列 ③ KD黃金交叉(在20以下) ④ 布林下軌站回或帶量突破 ⑤ 先設停損再下單
            </div>
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-2">
              <span className="text-red-300 font-black">【出場條件】</span> 停損：跌破設定點立刻出場（機器人模式）｜停利：① 漲10% ② 布林上軌 ③ 趨勢反轉訊號
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 space-y-2">
         <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-2xl relative overflow-hidden">
           <div className="absolute top-0 left-0 w-1 h-full bg-yellow-500 rounded-full"></div>
           <p className="text-[10px] text-yellow-300 font-bold leading-relaxed pl-3">
             「Python 只是工具，真正的力量來自於您對量化紀律的堅持。」
           </p>
           <p className="text-[9px] text-yellow-500 font-black uppercase tracking-widest mt-1 pl-3">— 顏春煌教授</p>
         </div>
         <div className="p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-2xl relative overflow-hidden">
           <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500 rounded-full"></div>
           <p className="text-[10px] text-indigo-300 font-bold leading-relaxed pl-3">
             「布林通道的正確用法：不是『觸下軌就買』，而是等股價跌破下軌後，重新站回通道且出現紅K棒時，才是真正的居高勝率之機。」
           </p>
           <p className="text-[9px] text-indigo-400 font-black uppercase tracking-widest mt-1 pl-3">— 0615課堂精華</p>
         </div>
         <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl relative overflow-hidden">
           <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500 rounded-full"></div>
           <p className="text-[10px] text-emerald-300 font-bold leading-relaxed pl-3">
             「空手觀望也是一種極高階的交易決策，在死水盤整區間中，頻繁進出只會被手續費耗光本金。」
           </p>
           <p className="text-[9px] text-emerald-500 font-black uppercase tracking-widest mt-1 pl-3">— 顏春煌教授（語錄合集）</p>
         </div>
         <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-2xl relative overflow-hidden">
           <div className="absolute top-0 left-0 w-1 h-full bg-red-500 rounded-full"></div>
           <p className="text-[10px] text-red-300 font-bold leading-relaxed pl-3">
             「股票市場是比氣長的，看錯停損，看對抱緊，這才是正規軍的打法。」
           </p>
           <p className="text-[9px] text-red-400 font-black uppercase tracking-widest mt-1 pl-3">— 阿村伯</p>
         </div>
      </div>
    </div>
  );
};

export default InvestmentChecklist;

import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertTriangle, ShieldCheck, ShieldAlert, Target, Info, Zap } from 'lucide-react';

const InvestmentChecklist = ({ stock }) => {
  const [manualChecks, setManualChecks] = useState({});

  // Reset checks when stock changes
  useEffect(() => {
    setManualChecks({});
  }, [stock?.symbol]);

  if (!stock) return null;

  const isAboveMA60 = stock.close > stock.ma60;

  const toggleCheck = (id) => {
    setManualChecks(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const sections = [
    {
      title: "標的過濾 (Target Filter)",
      icon: <ShieldCheck size={14} className="text-red-500" />,
      items: [
        { id: 'regular', text: "確認為季線之上「正規軍」標的", check: isAboveMA60 },
        { id: 'fundamental', text: "確認具備基本面支撐 (非妖股)", check: stock.vol_ratio > 0.5 }
      ]
    },
    {
      title: "進場邏輯 (Entry Logic)",
      icon: <Target size={14} className="text-orange-500" />,
      items: [
        { id: 'ma60_support', text: "生命線支撐確認 (MA60)", check: isAboveMA60 },
        { id: 'manual_entry', text: "手動確認突破或拉回支撐點", isManual: true }
      ]
    },
    {
      title: "風險控管 (Risk & Psychology)",
      icon: <ShieldAlert size={14} className="text-[#10B981]" />,
      items: [
        { id: 'stop_loss', text: "已設定「冰冷停損點」", isManual: true },
        { id: 'cash_ratio', text: "確認現金比例符合氣象台建議", isManual: true }
      ]
    },
    {
      title: "基本面防雷 (16大指標)",
      icon: <Target size={14} className="text-yellow-500" />,
      items: [
        { id: 'roe_margin', text: "ROE > 15% 且毛利率穩定", isManual: true },
        { id: 'eps_growth', text: "EPS 逐季增長或虧損收斂 (PEG)", isManual: true }
      ]
    }
  ];

  const handleExport = () => {
    const reportDate = new Date().toLocaleString();
    let content = `REGULAR ARMY QUANT - 交易檢核報告\n`;
    content += `====================================\n`;
    content += `標的: ${stock.symbol} ${stock.name}\n`;
    content += `時間: ${reportDate}\n`;
    content += `現價: ${stock.close} | 生命線: ${stock.ma60}\n`;
    content += `狀態: ${isAboveMA60 ? '正規軍' : '空頭禁區'}\n\n`;
    content += `檢核項目:\n`;
    
    sections.forEach(section => {
      content += `\n[ ${section.title} ]\n`;
      section.items.forEach(item => {
        const isChecked = item.isManual ? manualChecks[item.id] : item.check;
        content += `${isChecked ? '[V]' : '[ ]'} ${item.text}\n`;
      });
    });
    
    content += `\n====================================\n`;
    content += `顏老師叮嚀: "Python 只是工具，真正的力量來自於您對量化紀律的堅持。"\n`;

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
          <Info size={14} className="mr-2 text-red-500" /> 顏老師：量化紀律檢核系統
        </h3>
        <div className="flex items-center space-x-2">
          <button 
            onClick={handleExport}
            className="flex items-center px-3 py-1 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-[9px] font-black text-gray-400 transition-all active:scale-95"
          >
            <Zap size={12} className="mr-1 text-yellow-500" /> 導出報告
          </button>
          <span className={`text-[8px] md:text-[10px] px-2 py-0.5 md:py-1 rounded font-bold uppercase tracking-tighter ${
            isAboveMA60 ? 'bg-red-500/20 text-red-400' : 'bg-[#10B981]/20 text-[#10B981]'
          }`}>
            {isAboveMA60 ? "紀律高於預測" : "空頭禁區：禁止操作"}
          </span>
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
                        : 'bg-[#10B981]/5 border-[#10B981]/20 text-gray-400 opacity-60'
                    }`}
                  >
                    <div className={`w-4 h-4 md:w-5 md:h-5 rounded flex items-center justify-center mr-2 md:mr-3 ${
                      isChecked ? 'bg-red-600 shadow-lg shadow-red-600/30' : 'bg-gray-800 border border-white/5'
                    }`}>
                      {isChecked && <CheckCircle2 size={10} className="text-white" />}
                    </div>
                    <div className="flex flex-col">
                       <span className="text-[10px] md:text-[11px] font-bold leading-tight">{item.text}</span>
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
        <div className="mt-6 p-4 bg-[#10B981]/10 border border-[#10B981]/20 rounded-2xl flex items-center">
          <AlertTriangle size={24} className="text-[#10B981] mr-4 animate-pulse" />
          <p className="text-[10px] md:text-xs text-[#10B981] font-black leading-relaxed">
            顏老師警告：此標的位於季線（生命線）下方，屬於「空頭禁區」。在正規軍體系中，絕對禁止在禁區進行任何買入動作，觀望不動才是高階決策。
          </p>
        </div>
      )}
      
      <div className="mt-6 md:mt-8 p-3 md:p-4 bg-[#161A1E] border border-white/5 rounded-2xl">
         <p className="text-[9px] md:text-[10px] text-gray-500 font-bold italic leading-relaxed text-center">
           "Python 只是工具，真正的力量來自於您對量化紀律的堅持。" — 顏春煌教授
         </p>
      </div>
    </div>
  );
};

export default InvestmentChecklist;

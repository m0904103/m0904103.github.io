import sys

file_path = r"c:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\frontend\src\App.jsx"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_content = """                      <div className="flex justify-between items-start">
                        <div className="flex flex-col">
                          <span className={`text-lg md:text-xl font-black tracking-tighter transition-colors ${!isAboveMA60 ? 'text-gray-300 group-hover:text-[#10B981]' : 'text-white group-hover:text-red-500'}`}>
                            {stock.symbol.replace('.TW', '')} {stock.name}
                          </span>
                          <span className="text-[9px] md:text-[10px] text-gray-500 font-bold opacity-0 h-0">.</span>
                        </div>
                        <div className={`px-2 md:px-3 py-1 rounded-full text-[9px] md:text-[10px] font-black uppercase tracking-wider border ${
                          !isAboveMA60 ? 'text-[#10B981] border-[#10B981]/30 bg-[#10B981]/10' : getSignalStyle(stock.signal)
                        }`}>
                          {!isAboveMA60 ? '空頭禁區' : stock.signal}
                        </div>
                      </div>

                      <div className="mt-4 flex items-center justify-between">
                         <div className="flex items-center space-x-3 md:space-x-4">
                            <div className="flex flex-col">
                              <span className="text-[7px] md:text-[8px] text-gray-500 font-black uppercase">現價</span>
                              <span className={`text-xs md:text-sm font-mono font-bold ${!isAboveMA60 ? 'text-[#10B981]' : 'text-gray-100'}`}>${stock.close}</span>
                            </div>
                            <div className="flex flex-col">
                              <span className="text-[7px] md:text-[8px] text-gray-500 font-black uppercase">生命線</span>
                              <span className={`text-[9px] md:text-[10px] font-bold ${isAboveMA60 ? 'text-red-400' : 'text-gray-400'}`}>{stock.ma60 || "---"}</span>
                            </div>
                         </div>
                         <div className="flex items-center space-x-2">
                            {isAboveMA60 && stock.vol_ratio > 1.5 && <Zap size={14} className="text-orange-500" />}
                            {isAboveMA60 && <ShieldCheck size={14} className="text-red-500" />}
                            {!isAboveMA60 && <AlertTriangle size={14} className="text-[#10B981] animate-pulse" />}
                         </div>
                      </div>
                    </div>
                  );
"""

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines[:394] + [new_content] + lines[424:])

print("Fixed!")

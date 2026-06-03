import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const TradingChart = ({ data, symbol, buyPrice, stopLoss, takeProfit, currentPrice, stock }) => {
  const chartContainerRef = useRef();

  useEffect(() => {
    if (!data || data.length === 0) return;

    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#1E2329' },
        textColor: '#D1D4DC',
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      grid: {
        vertLines: { color: 'rgba(70, 70, 70, 0.3)' },
        horzLines: { color: 'rgba(70, 70, 70, 0.3)' },
      },
      crosshair: { mode: 0 },
      timeScale: { borderColor: '#485c7b' },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#EF4444',
      downColor: '#10B981',
      borderVisible: false,
      wickUpColor: '#EF4444',
      wickDownColor: '#10B981',
    });

    candlestickSeries.setData(data);

    // Buy/Sell markers at MA60 crossover
    const markers = [];
    for (let i = 1; i < data.length; i++) {
      const prev = data[i-1];
      const curr = data[i];
      if (prev.ma60 && curr.ma60) {
        if (prev.close <= prev.ma60 && curr.close > curr.ma60) {
          markers.push({ time: curr.time, position: 'belowBar', color: '#EF4444', shape: 'arrowUp', text: 'BUY' });
        } else if (prev.close >= prev.ma60 && curr.close < curr.ma60) {
          markers.push({ time: curr.time, position: 'aboveBar', color: '#10B981', shape: 'arrowDown', text: 'SELL' });
        }
      }
    }
    candlestickSeries.setMarkers(markers);

    // MA60 生命線
    const ma60Points = data.filter(d => d.ma60).map(d => ({ time: d.time, value: d.ma60 }));
    if (ma60Points.length > 0) {
      const maSeries = chart.addLineSeries({
        color: '#EF4444',
        lineWidth: 2,
        priceLineVisible: false,
        title: 'MA60',
      });
      maSeries.setData(ma60Points);
    }

    // ✅ 現價線（最重要！）
    const livePrice = currentPrice || (data.length > 0 ? data[data.length - 1].close : null);
    if (livePrice) {
      candlestickSeries.createPriceLine({
        price: livePrice,
        color: '#38BDF8',   // Sky blue
        lineWidth: 2,
        lineStyle: 0,       // Solid
        axisLabelVisible: true,
        title: `NOW`,
      });
    }

    // 建議買進價
    if (buyPrice && livePrice && Math.abs(buyPrice - livePrice) > 0.01) {
      candlestickSeries.createPriceLine({
        price: buyPrice,
        color: '#EAB308',
        lineWidth: 1.5,
        lineStyle: 2,
        axisLabelVisible: true,
        title: 'BUY',
      });
    }

    // 停損線
    if (stopLoss) {
      candlestickSeries.createPriceLine({
        price: stopLoss,
        color: '#10B981',
        lineWidth: 1.5,
        lineStyle: 2,
        axisLabelVisible: true,
        title: 'STOP',
      });
    }

    // 目標獲利線
    if (takeProfit) {
      candlestickSeries.createPriceLine({
        price: takeProfit,
        color: '#F97316',
        lineWidth: 1.5,
        lineStyle: 2,
        axisLabelVisible: true,
        title: 'TARGET',
      });
    }

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, buyPrice, stopLoss, takeProfit, currentPrice]);

  const livePrice = currentPrice || (data?.length > 0 ? data[data.length - 1]?.close : null);

  return (
    <div className="relative w-full h-full bg-dark-card rounded-lg overflow-hidden border border-gray-800 shadow-xl">
      <div className="p-3 md:p-4 flex flex-col md:flex-row justify-between items-center bg-[#2B3139] gap-2">
        <h3 className="text-sm md:text-lg font-bold text-white flex items-center flex-wrap gap-2">
          {symbol} 即時戰情圖
          {stock?.market === 'tw' && stock?.fundamentals?.three_rates_rising && <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-400 border border-green-500/30">🟢 三率三升</span>}
          {stock?.market === 'tw' && stock?.chips?.foreign_buy && <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">🔵 外資連買</span>}
          {stock?.market === 'tw' && stock?.chips?.margin_surge && <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">⚠️ 融資暴增</span>}
        </h3>
        <div className="flex flex-wrap gap-2 md:gap-4 text-[10px] md:text-xs">
           {livePrice && (
             <span className="flex items-center font-black text-sky-400">
               <div className="w-2 h-2 rounded-full bg-sky-400 mr-1"></div>
               現價 ${typeof livePrice === 'number' ? livePrice.toFixed(2) : livePrice}
             </span>
           )}
           <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#EF4444] mr-1"></div> MA60 生命線</span>
           {buyPrice && <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#EAB308] mr-1"></div> 買點 ${buyPrice}</span>}
           {stopLoss && <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#10B981] mr-1"></div> 停損 ${stopLoss}</span>}
           {takeProfit && <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#F97316] mr-1"></div> 目標 ${takeProfit}</span>}
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full h-[300px] md:h-[400px]" />
    </div>
  );
};

export default TradingChart;




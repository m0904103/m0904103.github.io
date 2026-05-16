import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const TradingChart = ({ data, symbol, buyPrice, stopLoss, takeProfit }) => {
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
        vertLines: { color: 'rgba(70, 70, 70, 0.5)' },
        horzLines: { color: 'rgba(70, 70, 70, 0.5)' },
      },
      crosshair: {
        mode: 0,
      },
      timeScale: {
        borderColor: '#485c7b',
      },
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#EF4444',
      downColor: '#10B981',
      borderVisible: false,
      wickUpColor: '#EF4444',
      wickDownColor: '#10B981',
    });

    candlestickSeries.setData(data);

    // Add markers for Buy/Sell signals (Backtest Visualization)
    const markers = [];
    for (let i = 1; i < data.length; i++) {
      const prev = data[i-1];
      const curr = data[i];
      if (prev.ma60 && curr.ma60) {
        // Buy signal: Price crosses above MA60
        if (prev.close <= prev.ma60 && curr.close > curr.ma60) {
          markers.push({
            time: curr.time,
            position: 'belowBar',
            color: '#EF4444',
            shape: 'arrowUp',
            text: 'BUY',
          });
        }
        // Sell signal: Price crosses below MA60
        else if (prev.close >= prev.ma60 && curr.close < curr.ma60) {
          markers.push({
            time: curr.time,
            position: 'aboveBar',
            color: '#10B981',
            shape: 'arrowDown',
            text: 'SELL',
          });
        }
      }
    }
    candlestickSeries.setMarkers(markers);

    // Add MA60 Line (生命線)
    const ma60Points = data.filter(d => d.ma60).map(d => ({ time: d.time, value: d.ma60 }));
    if (ma60Points.length > 0) {
      const maSeries = chart.addLineSeries({
        color: '#EF4444',
        lineWidth: 1.5,
        priceLineVisible: false,
        title: 'MA60',
      });
      maSeries.setData(ma60Points);
    }

    // Add horizontal lines for Buy, Stop Loss, Take Profit
    if (buyPrice) {
      candlestickSeries.createPriceLine({
        price: buyPrice,
        color: '#EAB308',
        lineWidth: 2,
        lineStyle: 2, // Dashed
        axisLabelVisible: true,
        title: 'BUY',
      });
    }

    if (stopLoss) {
      candlestickSeries.createPriceLine({
        price: stopLoss,
        color: '#10B981',
        lineWidth: 2,
        lineStyle: 2,
        axisLabelVisible: true,
        title: 'STOP',
      });
    }

    if (takeProfit) {
      candlestickSeries.createPriceLine({
        price: takeProfit,
        color: '#EF4444',
        lineWidth: 2,
        lineStyle: 2,
        axisLabelVisible: true,
        title: 'PROFIT',
      });
    }

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, buyPrice, stopLoss, takeProfit]);

  return (
    <div className="relative w-full h-full bg-dark-card rounded-lg overflow-hidden border border-gray-800 shadow-xl">
      <div className="p-3 md:p-4 flex flex-col md:flex-row justify-between items-center bg-[#2B3139] gap-2">
        <h3 className="text-sm md:text-lg font-bold text-white">{symbol} 即時戰情圖</h3>
        <div className="flex space-x-3 md:space-x-4 text-[10px] md:text-xs">
           <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#EF4444] mr-1"></div> MA60 生命線</span>
           <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#EAB308] mr-1"></div> Buy</span>
           <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#10B981] mr-1"></div> Stop</span>
           <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#EF4444] mr-1"></div> Profit</span>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full h-[300px] md:h-[400px]" />
    </div>
  );
};

export default TradingChart;

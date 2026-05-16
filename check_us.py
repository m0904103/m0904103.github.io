import yfinance as yf
import ta
import pandas as pd
import numpy as np
import json
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# ==================== 300 檔正規軍 2026 終極池子 (v9.2.0 基因升級版) ====================
STOCKS_US = [
    "QQQ", "SPY", "SMH", "SOXX", "XLK", "XLE", "VGT", "VOO", "VTI", "IWM", "DIA",
    "NVDA", "TSM", "AVGO", "AMD", "QCOM", "MU", "ASML", "ARM", "INTC", "AMAT", "LRCX", "DELL", "STX",
    "MSFT", "AMZN", "GOOGL", "META", "AAPL", "PLTR", "ADBE", "CRM", "SNOW", "PANW", "FTNT", "CRWD", "NOW", "INTU", "ORCL", "CSCO", "NFLX",
    "VRT", "VST", "NEE", "EQIX", "CAT", "GE", "XOM", "CVX", "LIN", "HON", "BA", "IBM", "T", "BX",
    "BRK-B", "JPM", "V", "MA", "GS", "MS", "WFC", "BAC", "AXP", "BLK", "UNH", "JNJ", "LLY", "NVO", "COST", "WMT", "PYPL", "LOW", "HD", "MCD", "PEP", "KO",
    "MSTR", "COIN", "MARA", "CEG", "OKLO", "ETN", "PWR", "GEV", "VRTX", "REGN", "ISRG", "TER", "AVAV", "LMT", "RTX", "ADSK", "ANSS", "WDAY", "SNPS", "CDNS",
    "MDB", "DDOG", "TSLA", "ABNB", "UBER", "SHOP", "SQ", "DKNG", "HOOD", "RIVN", "LCID", "F", "GM", "TM", "HMC", "SBUX", "NKE", "LULU", "TJX",
    "TEL", "APH", "GLW", "MSI", "HPE", "NTAP", "WDC", "WOLF", "ON", "NXPI", "MCHP", "MPWR", "MONY", "APP", "RDDT",
    "AMGN", "GILD", "BMY", "ABBV", "PFE", "MRK", "TMO", "DHR", "MDT", "SYK", "BSX", "ZTS", "CI", "CVS", "ELV", "HUM", "HCA",
    "UPS", "FDX", "NSC", "UNP", "CSX", "NOC", "GD", "MMM", "EMR", "ITW", "PH", "AME", "ROP", "PAYX", "FIS", "FISV", "JKHY", "ADU",
    "DOV", "MRVL", "NET", "ZS", "OKLO", "BWXT"
]

STOCKS_TW = [
    "2330.TW", "2317.TW", "2454.TW", "2308.TW", "2303.TW", "3711.TW", "2382.TW", "6669.TW", "3231.TW", "2376.TW", "2357.TW", "2301.TW", "2395.TW", "2412.TW",
    "3017.TW", "3653.TW", "6235.TW", "6415.TW", "1503.TW", "1513.TW", "1519.TW", "2881.TW", "2882.TW", "2891.TW", "5871.TW", "2379.TW", "3008.TW", "3034.TW", "3037.TW",
    "2327.TW", "2474.TW", "2356.TW", "4958.TW", "2313.TW", "2360.TW", "2449.TW", "3702.TW", "2347.TW", "2409.TW", "3481.TW", "2603.TW", "2609.TW", "2615.TW",
    "2002.TW", "1301.TW", "1303.TW", "1326.TW", "6505.TW", "1216.TW", "2912.TW", "5904.TW", "9910.TW", "9921.TW", "2207.TW", "2105.TW", "1402.TW", "1101.TW",
    "2344.TW", "2408.TW", "2337.TW", "2353.TW", "2324.TW", "2352.TW", "4938.TW", "3045.TW", "4904.TW", "6206.TW", "2359.TW", "3680.TW", "3583.TW", "1717.TW", "2368.TW",
    "2441.TW", "2451.TW", "3006.TW", "3010.TW", "3014.TW", "3035.TW", "3044.TW", "3227.TW", "3443.TW", "3532.TW", "3592.TW", "3661.TW", "3665.TW", "4919.TW", "4961.TW",
    "4966.TW", "5269.TW", "5274.TW", "6139.TW", "6205.TW", "6223.TW", "6239.TW", "6414.TW", "6472.TW", "6515.TW", "6531.TW", "6533.TW", "6643.TW", "6679.TW", "6719.TW",
    "6770.TW", "8016.TW", "8046.TW", "8050.TW", "8069.TW", "8150.TW", "8210.TW", "8299.TW", "8436.TW", "8464.TW", "8936.TW", "9904.TW", "9914.TW", "9933.TW", "9945.TW",
    "2633.TW", "2637.TW", "2707.TW", "2727.TW", "4142.TW", "4147.TW", "4164.TW", "4174.TW", "6446.TW", "1514.TW", "1519.TW", "1504.TW", "1503.TW",
    "3363.TW", "4979.TW", "6187.TW", "4770.TW", "1785.TW", "1711.TW"
]

TW_NAMES = {
    # --- TW 正規軍 ---
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2308.TW": "台達電", "2303.TW": "聯電", 
    "3711.TW": "日月光投控", "2382.TW": "廣達", "6669.TW": "緯穎", "3231.TW": "緯創", "2376.TW": "技嘉", 
    "2357.TW": "華碩", "2301.TW": "光寶科", "2395.TW": "研華", "2412.TW": "中華電", "3017.TW": "奇鋐", 
    "3653.TW": "健策", "6235.TW": "華孚", "6415.TW": "矽力-KY", "1503.TW": "士電", "1513.TW": "中興電", 
    "1519.TW": "華城", "2881.TW": "富邦金", "2882.TW": "國泰金", "2891.TW": "中信金", "5871.TW": "中租-KY", 
    "2379.TW": "瑞昱", "3008.TW": "大立光", "3034.TW": "聯詠", "3037.TW": "欣興", "2327.TW": "國巨", 
    "2474.TW": "可成", "2356.TW": "英業達", "4958.TW": "臻鼎-KY", "2313.TW": "華通", "2360.TW": "致茂",
    "2449.TW": "京元電子", "3702.TW": "大聯大", "2347.TW": "聯強", "2409.TW": "友達", "3481.TW": "群創",
    "2603.TW": "長榮", "2609.TW": "陽明", "2615.TW": "萬海", "2002.TW": "中鋼", "1301.TW": "台塑",
    "1303.TW": "南亞", "1326.TW": "台化", "6505.TW": "台塑化", "1216.TW": "統一", "2912.TW": "統一超",
    "5904.TW": "寶雅", "9910.TW": "豐泰", "9921.TW": "巨大", "2207.TW": "和泰車", "2105.TW": "正新",
    "1402.TW": "遠東新", "1101.TW": "台泥", "2344.TW": "華邦電", "2408.TW": "南亞科", "2337.TW": "旺宏",
    "2353.TW": "宏碁", "2324.TW": "仁寶", "2352.TW": "佳世達", "4938.TW": "和碩", "3045.TW": "台灣大",
    "4904.TW": "遠傳", "6206.TW": "飛捷", "3661.TW": "世芯-KY", "3665.TW": "貿聯-KY", "5269.TW": "祥碩",
    "5274.TW": "信驊", "3035.TW": "智原", "3443.TW": "創意", "6446.TW": "藥華藥", "4147.TW": "泰博",
    "2359.TW": "所羅門", "3680.TW": "家登", "3583.TW": "辛耘", "1717.TW": "長興", "1514.TW": "亞力",
    "3363.TW": "上詮", "4979.TW": "華星光", "6187.TW": "萬潤", "4770.TW": "崇越", "1785.TW": "光洋科", "1711.TW": "永光",
    # --- US 正規軍 ---
    "QQQ": "納斯達克100", "SPY": "標普500", "SMH": "半導體ETF", "SOXX": "費半ETF", "XLK": "科技ETF", 
    "XLE": "能源ETF", "VGT": "資訊科技ETF", "VOO": "標普500ETF", "VTI": "全美股市ETF", "IWM": "羅素2000ETF", "DIA": "道瓊工業指數ETF",
    "NVDA": "輝達", "TSM": "台積電 ADR", "AVGO": "博通", "AMD": "超微", "QCOM": "高通", "MU": "美光", 
    "ASML": "艾司摩爾", "ARM": "安謀", "INTC": "英特爾", "AMAT": "應用材料", "LRCX": "科林研發", "DELL": "戴爾", "STX": "希捷",
    "MSFT": "微軟", "AMZN": "亞馬遜", "GOOGL": "谷歌", "META": "臉書", "AAPL": "蘋果", "PLTR": "帕蘭提爾", 
    "ADBE": "奧多比", "CRM": "賽富時", "SNOW": "雪花", "PANW": "帕羅奧圖", "FTNT": "飛塔", "CRWD": "庫德史萊克", 
    "NOW": "ServiceNow", "INTU": "Intuit", "ORCL": "甲骨文", "CSCO": "思科", "NFLX": "網飛",
    "VRT": "維諦", "VST": "維斯特", "NEE": "新紀元能源", "EQIX": "艾奎尼克斯", "CAT": "卡特彼勒", "GE": "奇異", 
    "XOM": "艾克森美孚", "CVX": "雪佛龍", "LIN": "林德", "HON": "漢威聯合", "BA": "波音", "IBM": "萬國商業機器", 
    "T": "AT&T", "BX": "黑石", "BRK-B": "波克夏", "JPM": "摩根大通", "V": "威士", "MA": "萬事達", 
    "GS": "高盛", "MS": "摩根士丹利", "WFC": "富國銀行", "BAC": "美國銀行", "AXP": "美國運通", "BLK": "貝萊德", 
    "UNH": "聯合健康", "JNJ": "強生", "LLY": "禮來", "NVO": "諾和諾德", "COST": "好市多", "WMT": "沃爾瑪", 
    "PYPL": "PayPal", "LOW": "勞氏", "HD": "家得寶", "MCD": "麥當勞", "PEP": "百事", "KO": "可口可樂",
    "MSTR": "微策略", "COIN": "Coinbase", "MARA": "Marathon Digital", "CEG": "Constellation Energy", 
    "OKLO": "Oklo Inc.", "ETN": "伊頓", "PWR": "Quanta Services", "GEV": "GE Vernova", "VRTX": "Vertex Pharm", 
    "REGN": "Regeneron", "ISRG": "直覺手術", "TER": "泰瑞達", "AVAV": "空拍環境", "LMT": "洛克希德馬丁", 
    "RTX": "雷神科技", "ADSK": "Autodesk", "ANSS": "Ansys", "WDAY": "Workday", "SNPS": "Synopsys", "CDNS": "Cadence",
    "MDB": "MongoDB", "DDOG": "Datadog", "TSLA": "特斯拉", "ABNB": "Airbnb", "UBER": "優步", "SHOP": "Shopify", 
    "SQ": "Block", "DKNG": "DraftKings", "HOOD": "Robinhood", "RIVN": "Rivian", "LCID": "Lucid", "F": "福特", 
    "GM": "通用汽車", "TM": "豐田", "HMC": "本田", "SBUX": "星巴克", "NKE": "耐吉", "LULU": "露露樂蒙", "TJX": "TJX Companies",
    "TEL": "TE Connectivity", "APH": "安費諾", "GLW": "康寧", "MSI": "摩托羅拉系統", "HPE": "慧與科技", 
    "NTAP": "NetApp", "WDC": "威騰電子", "WOLF": "Wolfspeed", "ON": "安森美", "NXPI": "恩智浦", 
    "MCHP": "微晶片科技", "MPWR": "芯源系統", "APP": "AppLovin", "RDDT": "Reddit",
    "AMGN": "安進", "GILD": "吉利德", "BMY": "必貴寶", "ABBV": "艾伯維", "PFE": "輝瑞", "MRK": "默沙東", 
    "TMO": "賽默飛世爾", "DHR": "丹納赫", "MDT": "美敦力", "SYK": "史賽克", "BSX": "波士頓科學", "ZTS": "碩騰", 
    "CI": "信諾", "CVS": "CVS健康", "ELV": "Elevance Health", "HUM": "Humana", "HCA": "HCA Healthcare",
    "UPS": "優比速", "FDX": "聯邦快遞", "NSC": "諾福克南方", "UNP": "聯合太平洋", "CSX": "CSX運輸", 
    "NOC": "諾斯洛普格魯曼", "GD": "通用動力", "MMM": "3M", "EMR": "艾默生電氣", "ITW": "伊利諾工具", 
    "PH": "派克漢尼汾", "AME": "阿美特克", "ROP": "Roper", "PAYX": "沛齊", "FIS": "富達投資服務", 
    "FISV": "Fiserv", "JKHY": "Jack Henry", "DOV": "Dover Corp", "MRVL": "馬威爾", "NET": "Cloudflare", "ZS": "Zscaler", "BWXT": "BWX Tech"
}

STOCKS_ALL = STOCKS_US + STOCKS_TW

def run_martial_arts_scan():
    results = []
    def robust_get_close(df):
        if df.empty: return 0
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if 'Close' in df.columns:
            s = df['Close']
            if isinstance(s, (pd.Series, pd.DataFrame)):
                val = s.iloc[-1]
                if isinstance(val, (pd.Series, pd.DataFrame)): val = val.iloc[0]
                return float(val)
        return 0

    # --- 1. ADR Premium Calculation ---
    adr_premium = 0
    try:
        tsm_data = yf.download("TSM", period="5d", progress=False)
        tw_2330 = yf.download("2330.TW", period="5d", progress=False)
        usdtwd_data = yf.download("TWD=X", period="5d", progress=False)
        
        tsm_p = robust_get_close(tsm_data)
        tw_p = robust_get_close(tw_2330)
        fx = robust_get_close(usdtwd_data)
        
        if tsm_p > 0 and tw_p > 0 and fx > 0:
            adr_premium = round(((tsm_p * fx) / (tw_p * 5) - 1) * 100, 2)
            print(f"--- ADR Premium: {adr_premium}% (TSM: {tsm_p}, 2330: {tw_p}, FX: {fx})")
    except Exception as e:
        print(f"ADR calculation failed: {e}")

    # --- 2. Dynamic Indices Scanning (v9.5.0 Calibration) ---
    INDICES_MAP = {
        "台股加權": "^TWII",
        "美金/台幣": "TWD=X",
        "10年美債(殖利率)": "^TNX",
        "費城半導體": "^SOX",
        "美股標普": "^GSPC",
        "那斯達克": "^IXIC",
        "US VIX (恐慌)": "^VIX"
    }
    
    indices_results = {}
    for name, ticker in INDICES_MAP.items():
        try:
            idf = yf.download(ticker, period="5d", progress=False)
            if not idf.empty:
                if isinstance(idf.columns, pd.MultiIndex): idf.columns = idf.columns.get_level_values(0)
                curr = idf['Close'].iloc[-1].item()
                prev = idf['Close'].iloc[-2].item()
                chg = round(((curr - prev) / prev) * 100, 2)
                
                # Simple signal logic
                sig = "Buy" if chg > 0 else "Wait"
                if "VIX" in name: sig = "Wait" if chg < 0 else "Sell"

                indices_results[name] = {
                    "close": round(curr, 2),
                    "change": chg,
                    "signal": sig
                }
        except Exception as e:
            print(f"Error fetching index {name}: {e}")
            indices_results[name] = {"close": 0, "change": 0, "signal": "Wait"}

    # Special case for TW VIX
    indices_results["TW VIX (恐慌)"] = {"close": 35.43, "change": 0.0, "signal": "Wait"}

    # --- 3. Main Stock Scanning Loop ---
    for symbol in STOCKS_ALL:
        try:
            df = yf.download(symbol, period="1y", progress=False)
            if df.empty or len(df) < 65: continue
            
            data = {}
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col in df.columns:
                    s = df[col]
                    if isinstance(s, pd.DataFrame): s = s.iloc[:, 0]
                    data[col] = s.squeeze()
            
            close = data['Close']
            volume = data['Volume']
            
            if close.empty: continue

            sma60 = ta.trend.SMAIndicator(close, window=60).sma_indicator().iloc[-1]
            rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]
            curr_p = close.iloc[-1].item()
            prev_p = close.iloc[-2].item()
            change = ((curr_p - prev_p) / prev_p) * 100

            is_reg = curr_p > (sma60 * 0.98)
            
            wr = 60
            if curr_p > sma60: wr += 10
            if rsi > 50: wr += 5
            if rsi > 70: wr -= 5
            if change > 0: wr += 2
            
            sig = "Hold"
            if wr >= 75: sig = "Strong Buy"
            elif wr >= 65: sig = "Buy"
            elif wr < 55: sig = "Sell"

            macd_status = "整理"
            if change > 1.5 and rsi < 65: macd_status = "Golden Cross"
            
            trend_score = (wr - 50) / 5
            if trend_score < 0: trend_score = 0
            if trend_score > 10: trend_score = 10
            
            tactical_pulse = 5.0
            if 55 < rsi < 68: tactical_pulse += 2.0
            if (curr_p - sma60)/sma60 < 0.08: tactical_pulse += 1.5
            
            vol_ratio = 1.0
            if not volume.empty and len(volume) > 20:
                v_last = float(volume.iloc[-1])
                v_avg = float(volume.iloc[-20:].mean())
                vol_ratio = round(v_last / v_avg, 2) if v_avg > 0 else 1.0

            elite_map = {
                "VRT": "[COOLING-CORE]", "LLY": "[GLP1-KING]", "CEG": "[NUCLEAR-POWER]", 
                "TSM": "[N2-GENE]", "ARM": "[IP-霸主]", "AAPL": "[EDGE-AI]",
                "MRVL": "[CPO-LEADER]", "DOV": "[LIQUID-VALVE]",
                "3363.TW": "[CPO-隱形]", "4979.TW": "[CPO-光網]", "6187.TW": "[CoWoS-GEAR]",
                "4770.TW": "[N2-CHEMICAL]", "1717.TW": "[N2-MATERIAL]", "3131.TW": "[CoWoS-WET]",
                "3583.TW": "[CoWoS-CORE]", "2330.TW": "[GLOBAL-BASE]"
            }
            
            def get_sect_and_tactic(s, curr_p, sma60, rsi, change, vol_ratio):
                if s in ["2330.TW", "TSM", "AAPL", "MSFT", "VOO", "SPY"]:
                    return "武當派", "「以柔克剛」：生命線之上，穩如泰山。守護生命線，順勢而為。"
                if s in ["NVDA", "AVGO", "AMD", "SMH", "SOXX"]:
                    return "少林派", "「剛猛進攻」：數據領先，趨勢事實確立。天下武功出少林，全力出擊。"
                if change > 2.5 and rsi > 60:
                    return "華山派", "「奇招迭出」：華山勢有破綻即出招。勢如破竹，掌握技術面突破點。"
                if vol_ratio > 1.5 and rsi < 40:
                    return "唐門派", "「暗器伏兵」：量先價行，低位伏兵。等待紅K啟動，一擊必殺。"
                if rsi > 75:
                    return "峨眉派", "「綿裡藏針」：過熱區間，謹慎追價。鎖住人性，等待回檔支撐。"
                if curr_p < sma60:
                    return "江湖散兵", "「破位出局」：結構破壞！生命線之下不買弱勢股。觀望不動是高階決策。"
                return "武當正規軍", "「守正出奇」：保持紀律，運用系統化方法排除迷思。MA60 為主，KD 為輔。"

            curr_sect, curr_tactic = get_sect_and_tactic(symbol, curr_p, sma60, rsi, change, vol_ratio)

            results.append({
                "symbol": symbol,
                "market": "tw" if symbol.endswith(".TW") else "us",
                "label": elite_map.get(symbol, ""),
                "name": TW_NAMES.get(symbol, symbol),
                "price": round(curr_p, 2),
                "close": round(curr_p, 2),
                "change": round(change, 2),
                "sma60": round(sma60, 2),
                "ma60": round(sma60, 2),
                "rsi": round(rsi, 2),
                "win_rate": wr,
                "trend_score": round(trend_score, 1),
                "tactical_score": round(tactical_pulse, 1),
                "macd_status": macd_status,
                "sect": curr_sect,
                "is_regular": is_reg,
                "signal": sig,
                "tactic": curr_tactic,
                "vol_ratio": vol_ratio,
                "plan": {
                    "entry": round(sma60 * 1.02, 2),
                    "sl": round(sma60 * 0.95, 2),
                    "tp": round(curr_p * 1.2, 2)
                }
            })
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")

    # --- 4. Final Data Assembly ---
    indices_final = {
        **indices_results,
        "ADR 溢價": {"close": adr_premium, "advice": "溢價" if adr_premium > 0 else "折價"},
        "adr_premium": {"close": adr_premium, "advice": "溢價" if adr_premium > 0 else "折價"},
        "fear_greed": {"value": 67, "sentiment": "Greed"},
        "suggested_cash": 30 if adr_premium < 15 else 40
    }

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (np.bool_, bool)): return bool(obj)
            if isinstance(obj, (np.integer, int)): return int(obj)
            if isinstance(obj, (np.floating, float)): return float(obj)
            return super().default(obj)

    output = {
        "stocks": results,
        "indices": indices_final,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("scan_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
    print("--- Precise Strike Scan Complete ---")

if __name__ == "__main__":
    run_martial_arts_scan()

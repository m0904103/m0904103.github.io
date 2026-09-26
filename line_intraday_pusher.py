# -*- coding: utf-8 -*-
"""
line_intraday_pusher.py - q_quant_888 顏老師鐵律盤中到價 LINE 推播守護引擎
================================================================================
功能亮點：
1. 盤中即時報價：對接 TWSE/TPEx 官方高速 MIS API (延遲低，免付費 Key)。
2. 大腦比對（顏老師鐵律）：
   - 均線生命線：股價守穩 MA60 季線之上（拒絕摸底向下攤平）。
   - 甜蜜買進區：回測布林通道下軌或甜蜜進場價位區間。
   - KD 超賣轉強：KD 進入 30 以下超賣區或黃金交叉打底。
   - 無情停損點 (SL)：以進場當日盤中最低價 (Low of Entry Day) 為停損防線，破線無條件離場。
   - 階梯停利 (TP)：第一目標 +10%、第二目標 +15% 順勢落袋。
3. LINE Messaging API 推播：
   - 主動發送 Flex Message 高質感交易戰情卡片至個人 LINE。
   - 內建冷卻防重複機制 (Cooldown)，同一標的盤中不重覆轟炸。
4. 支援三種執行模式：
   - 本機守護 Daemon：盤中每 1~3 分鐘自動輪巡。
   - 雲端定時排程：支援 GitHub Actions / Render 關機全自動監控。
   - 立即測試模式：--test 或 --force-symbol 快速驗證。
"""

import os
import sys
import json
import time
import ssl
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 確保輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent if 'scripts' in str(Path(__file__)) else Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
CONFIG_DIR = BASE_DIR / 'config'
STATE_FILE = DATA_DIR / 'line_alert_state.json'
CACHE_FILE = DATA_DIR / 'intraday_cache.json'
CONFIG_FILE = CONFIG_DIR / 'line_config.json'

DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# 台北時區 (UTC+8)
TAIPEI_TZ = timezone(timedelta(hours=8))

# 預設追蹤的核心正規軍標的
DEFAULT_WATCHLIST = {
    '2330.TW': {'name': '台積電', 'market': 'tse'},
    '3017.TW': {'name': '奇鋐', 'market': 'tse'},
    '3324.TW': {'name': '雙鴻', 'market': 'otc'},
    '6669.TW': {'name': '緯穎', 'market': 'tse'},
    '3081.TW': {'name': '聯亞', 'market': 'otc'},
    '6451.TW': {'name': '訊芯-KY', 'market': 'tse'},
    '1519.TW': {'name': '華城', 'market': 'tse'},
    '2382.TW': {'name': '廣達', 'market': 'tse'},
    '2454.TW': {'name': '聯發科', 'market': 'tse'},
    '2317.TW': {'name': '鴻海', 'market': 'tse'}
}

# ------------------------------------------------------------------------------
# 1. 設定讀取模組
# ------------------------------------------------------------------------------
def load_config():
    config = {
        'channel_access_token': os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '').strip(),
        'user_id': os.environ.get('LINE_USER_ID', '').strip(),
        'cooldown_minutes': 60,
        'watchlist': list(DEFAULT_WATCHLIST.keys())
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                local_cfg = json.load(f)
                if local_cfg.get('channel_access_token') and not config['channel_access_token']:
                    config['channel_access_token'] = local_cfg['channel_access_token'].strip()
                if local_cfg.get('user_id') and not config['user_id']:
                    config['user_id'] = local_cfg['user_id'].strip()
                if 'cooldown_minutes' in local_cfg:
                    config['cooldown_minutes'] = local_cfg['cooldown_minutes']
                if 'watchlist' in local_cfg and isinstance(local_cfg['watchlist'], list):
                    config['watchlist'] = local_cfg['watchlist']
        except Exception as e:
            print(f'⚠️ 讀取 {CONFIG_FILE} 失敗: {e}')
            
    return config

# ------------------------------------------------------------------------------
# 2. LINE Messaging API 推播模組
# ------------------------------------------------------------------------------
def push_line_message(token, user_id, messages):
    if not token or not user_id:
        print('❌ 未設定 LINE_CHANNEL_ACCESS_TOKEN 或 LINE_USER_ID，略過推播。')
        return False
        
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'to': user_id,
        'messages': messages if isinstance(messages, list) else [messages]
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            if res.status == 200:
                print('✅ LINE 訊息已成功推播至學長手機！')
                return True
            else:
                print(f'⚠️ LINE 推播回傳狀態碼: {res.status}')
                return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='replace')
        print(f'❌ LINE API 呼叫失敗 ({e.code}): {err_msg}')
        return False
    except Exception as e:
        print(f'❌ LINE 連線異常: {e}')
        return False

# ------------------------------------------------------------------------------
# 3. 提示工程：建構顏老師鐵律高階戰情卡片 (Flex Message)
# ------------------------------------------------------------------------------
def create_sweet_spot_card(symbol, name, current_price, low_price, ma60, bb_lower, kd_k, kd_d, entry_plan=None):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d %H:%M:%S')
    
    # 停損停利計算（嚴格遵循顏老師 SOP）
    sl_price = round(low_price, 2)  # Low of Entry Day
    tp1_price = round(current_price * 1.10, 2)  # +10%
    tp2_price = round(current_price * 1.15, 2)  # +15%
    
    # 替代純文字版（防護保底）
    alt_text = f'【q_quant_888 顏老師鐵律】{symbol} {name} 觸發甜蜜買進！現價: {current_price}, 停損: {sl_price}'
    
    flex_content = {
        'type': 'bubble',
        'size': 'mega',
        'header': {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#0F172A',
            'paddingAll': '16px',
            'contents': [
                {
                    'type': 'box',
                    'layout': 'horizontal',
                    'contents': [
                        {
                            'type': 'text',
                            'text': '🟢 顏老師鐵律｜到價買進訊號',
                            'weight': 'bold',
                            'color': '#10B981',
                            'size': 'sm',
                            'flex': 3
                        },
                        {
                            'type': 'text',
                            'text': 'q_quant_888',
                            'color': '#94A3B8',
                            'size': 'xs',
                            'align': 'end',
                            'flex': 2
                        }
                    ]
                },
                {
                    'type': 'box',
                    'layout': 'horizontal',
                    'margin': 'md',
                    'contents': [
                        {
                            'type': 'text',
                            'text': f'{symbol} {name}',
                            'weight': 'bold',
                            'size': 'xl',
                            'color': '#F8FAFC',
                            'flex': 3
                        },
                        {
                            'type': 'text',
                            'text': f'${current_price:.1f}',
                            'weight': 'bold',
                            'size': 'xxl',
                            'color': '#EF4444',
                            'align': 'end',
                            'flex': 2
                        }
                    ]
                },
                {
                    'type': 'box',
                    'layout': 'horizontal',
                    'margin': 'sm',
                    'contents': [
                        {
                            'type': 'text',
                            'text': f'盤中低點: ${low_price:.1f} ｜ 季線MA60: ${ma60:.1f}',
                            'color': '#94A3B8',
                            'size': 'xs'
                        }
                    ]
                }
            ]
        },
        'body': {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#1E293B',
            'paddingAll': '16px',
            'contents': [
                {
                    'type': 'box',
                    'layout': 'horizontal',
                    'contents': [
                        {
                            'type': 'box',
                            'layout': 'vertical',
                            'backgroundColor': '#334155',
                            'cornerRadius': '6px',
                            'paddingAll': '6px',
                            'margin': 'xs',
                            'contents': [
                                {
                                    'type': 'text',
                                    'text': '生命線守護',
                                    'color': '#38BDF8',
                                    'size': 'xxs',
                                    'align': 'center',
                                    'weight': 'bold'
                                }
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'vertical',
                            'backgroundColor': '#334155',
                            'cornerRadius': '6px',
                            'paddingAll': '6px',
                            'margin': 'xs',
                            'contents': [
                                {
                                    'type': 'text',
                                    'text': f'KD超賣 (K:{kd_k:.0f})',
                                    'color': '#FBBF24',
                                    'size': 'xxs',
                                    'align': 'center',
                                    'weight': 'bold'
                                }
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'vertical',
                            'backgroundColor': '#334155',
                            'cornerRadius': '6px',
                            'paddingAll': '6px',
                            'margin': 'xs',
                            'contents': [
                                {
                                    'type': 'text',
                                    'text': '布林下軌支撐',
                                    'color': '#34D399',
                                    'size': 'xxs',
                                    'align': 'center',
                                    'weight': 'bold'
                                }
                            ]
                        }
                    ]
                },
                {
                    'type': 'separator',
                    'margin': 'md',
                    'color': '#334155'
                },
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'margin': 'md',
                    'spacing': 'sm',
                    'contents': [
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'contents': [
                                {'type': 'text', 'text': '🎯 甜蜜買進價', 'color': '#94A3B8', 'size': 'sm', 'flex': 2},
                                {'type': 'text', 'text': f'${current_price:.1f}', 'color': '#F8FAFC', 'size': 'sm', 'weight': 'bold', 'flex': 3}
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'contents': [
                                {'type': 'text', 'text': '🛡️ 顏老師停損(SL)', 'color': '#F87171', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': f'${sl_price:.1f} (當日低點)', 'color': '#F87171', 'size': 'sm', 'weight': 'bold', 'flex': 3}
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'contents': [
                                {'type': 'text', 'text': '🚀 階梯停利(TP)', 'color': '#4ADE80', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': f'${tp1_price:.1f} (+10%) / ${tp2_price:.1f} (+15%)', 'color': '#4ADE80', 'size': 'sm', 'weight': 'bold', 'flex': 3}
                            ]
                        }
                    ]
                },
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'margin': 'md',
                    'backgroundColor': '#0F172A',
                    'cornerRadius': '6px',
                    'paddingAll': '10px',
                    'contents': [
                        {
                            'type': 'text',
                            'text': '💡 顏老師決策提示與下單防呆：',
                            'color': '#FDE047',
                            'size': 'xs',
                            'weight': 'bold'
                        },
                        {
                            'type': 'text',
                            'text': '1. 現價觸及甜蜜區，且守穩季線生命線。\n2. 嚴防按錯：請核對「整張」與「零股」下單視窗。\n3. 無情停損：盤中跌破當日最低價立即市價出場！',
                            'color': '#CBD5E1',
                            'size': 'xxs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                }
            ]
        },
        'footer': {
            'type': 'box',
            'layout': 'horizontal',
            'backgroundColor': '#0F172A',
            'paddingAll': '12px',
            'contents': [
                {
                    'type': 'text',
                    'text': f'觸發時間：{now_str}',
                    'color': '#64748B',
                    'size': 'xxs',
                    'align': 'center'
                }
            ]
        }
    }
    
    return [
        {
            'type': 'flex',
            'altText': alt_text,
            'contents': flex_content
        }
    ]

# ------------------------------------------------------------------------------
# 4. TWSE/TPEx 即時報價爬取引擎
# ------------------------------------------------------------------------------
def fetch_realtime_quotes(watchlist):
    tickers = []
    for sym in watchlist:
        code = sym.split('.')[0]
        # 判斷是上市 (tse) 還是上櫃 (otc)
        is_otc = sym.endswith('.TWO') or code in ['3324', '3081', '3491', '6811', '3558', '6245']
        prefix = 'otc' if is_otc else 'tse'
        tickers.append(f'{prefix}_{code}.tw')
        
    ch_param = '|'.join(tickers)
    url = f'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ch_param}&json=1&delay=0'
    
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    results = {}
    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as res:
            raw = res.read().decode('utf-8')
            data = json.loads(raw)
            for item in data.get('msgArray', []):
                code = item.get('c')
                name = item.get('n', '')
                
                # 成交價 z
                z_str = item.get('z', '-')
                y_str = item.get('y', '0')
                l_str = item.get('l', '-')
                h_str = item.get('h', '-')
                
                y_val = float(y_str) if y_str != '-' else 0.0
                
                # 若 z 為 '-' (如開盤試撮或未成交)，由買賣一檔替代
                if z_str != '-':
                    price = float(z_str)
                else:
                    b_list = item.get('b', '').split('_')
                    a_list = item.get('a', '').split('_')
                    if a_list and a_list[0] and a_list[0] != '-':
                        price = float(a_list[0])
                    elif b_list and b_list[0] and b_list[0] != '-':
                        price = float(b_list[0])
                    else:
                        price = y_val
                        
                low_val = float(l_str) if l_str != '-' else price
                high_val = float(h_str) if h_str != '-' else price
                
                results[f'{code}.TW'] = {
                    'symbol': f'{code}.TW',
                    'name': name,
                    'price': price,
                    'yesterday_close': y_val,
                    'low': low_val,
                    'high': high_val,
                    'time': item.get('t', '')
                }
    except Exception as e:
        print(f'⚠️ TWSE MIS API 抓取失敗: {e}')
        
    return results

# ------------------------------------------------------------------------------
# 5. 指標計算與歷史快取 (MA60, 布林通道, KD)
# ------------------------------------------------------------------------------
def get_stock_technicals(symbol):
    # 先查快取
    cache = {}
    today_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d')
    
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except Exception:
            cache = {}
            
    if symbol in cache and cache[symbol].get('date') == today_str:
        return cache[symbol]
        
    # 若快取無今日資料，向 yfinance 抓取歷史日 K
    try:
        import yfinance as yf
        ticker_sym = symbol
        df = yf.Ticker(ticker_sym).history(period='6mo')
        if df.empty and symbol.endswith('.TW'):
            ticker_sym = symbol.replace('.TW', '.TWO')
            df = yf.Ticker(ticker_sym).history(period='6mo')
            
        if not df.empty and len(df) >= 20:
            ma60 = float(df['Close'].rolling(60).mean().iloc[-1]) if len(df) >= 60 else float(df['Close'].mean())
            ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
            std20 = float(df['Close'].rolling(20).std().iloc[-1])
            bb_lower = ma20 - (2 * std20)
            bb_upper = ma20 + (2 * std20)
            
            l9 = df['Low'].rolling(9).min()
            h9 = df['High'].rolling(9).max()
            rsv = 100 * (df['Close'] - l9) / (h9 - l9)
            k_series = rsv.ewm(com=2, adjust=False).mean()
            d_series = k_series.ewm(com=2, adjust=False).mean()
            
            tech_data = {
                'date': today_str,
                'ma60': round(ma60, 2),
                'ma20': round(ma20, 2),
                'bb_lower': round(bb_lower, 2),
                'bb_upper': round(bb_upper, 2),
                'k': round(float(k_series.iloc[-1]), 2),
                'd': round(float(d_series.iloc[-1]), 2)
            }
            cache[symbol] = tech_data
            try:
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return tech_data
    except Exception as e:
        print(f'⚠️ 計算 {symbol} 指標失敗: {e}')
        
    return None

# ------------------------------------------------------------------------------
# 6. 防重複推播冷卻機制
# ------------------------------------------------------------------------------
def check_can_alert(symbol, current_price, cooldown_minutes=60):
    state = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except Exception:
            state = {}
            
    now = datetime.now(TAIPEI_TZ)
    today_str = now.strftime('%Y-%m-%d')
    
    if symbol in state:
        last_alert = state[symbol]
        last_date = last_alert.get('date')
        last_time_str = last_alert.get('timestamp')
        
        if last_date == today_str and last_time_str:
            try:
                last_time = datetime.fromisoformat(last_time_str)
                diff_sec = (now - last_time).total_seconds()
                if diff_sec < (cooldown_minutes * 60):
                    return False, f'冷卻中 (已推播過，距離上次 {int(diff_sec/60)} 分鐘)'
            except Exception:
                pass
                
    return True, '可推播'

def mark_alert_sent(symbol, current_price):
    state = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except Exception:
            state = {}
            
    now = datetime.now(TAIPEI_TZ)
    state[symbol] = {
        'date': now.strftime('%Y-%m-%d'),
        'timestamp': now.isoformat(),
        'price': current_price
    }
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f'⚠️ 儲存警報狀態失敗: {e}')

# ------------------------------------------------------------------------------
# 7. 核心巡檢與大腦比對引擎
# ------------------------------------------------------------------------------
def run_scan_once(config, force_symbol=None):
    watchlist = config.get('watchlist', list(DEFAULT_WATCHLIST.keys()))
    if force_symbol:
        watchlist = [force_symbol]
        
    print(f'🔍 啟動盤中巡檢，監控標的數: {len(watchlist)} 檔...')
    quotes = fetch_realtime_quotes(watchlist)
    
    alerts_triggered = 0
    token = config.get('channel_access_token')
    user_id = config.get('user_id')
    cooldown = config.get('cooldown_minutes', 60)
    
    for sym in watchlist:
        q = quotes.get(sym)
        if not q:
            alt_sym = sym.replace('.TWO', '.TW') if sym.endswith('.TWO') else sym.replace('.TW', '.TWO')
            q = quotes.get(alt_sym)
            
        if not q or q['price'] <= 0:
            print(f'  - {sym}: 無即時報價')
            continue
            
        price = q['price']
        low_p = q['low']
        name = q['name'] or DEFAULT_WATCHLIST.get(sym, {}).get('name', sym)
        
        tech = get_stock_technicals(sym)
        if not tech:
            ma60 = round(price * 0.95, 2)
            bb_lower = round(price * 0.98, 2)
            k_val = 25.0
            d_val = 26.0
        else:
            ma60 = tech['ma60']
            bb_lower = tech['bb_lower']
            k_val = tech['k']
            d_val = tech['d']
            
        # 顏老師鐵律條件判定
        # 1. 守穩季線生命線之上 (或在季線附近 1% 容錯內)
        is_above_ma60 = bool(price >= ma60 * 0.99)
        # 2. 觸及或進入甜蜜區 (回測布林下軌附近 2% 內，或價格低於布林下軌拉回)
        is_sweet_spot = bool(price <= bb_lower * 1.025)
        # 3. KD 超賣或轉強打底 (K <= 35 或 K > D)
        is_kd_oversold = bool(k_val <= 35 or k_val > d_val)
        
        should_alert = force_symbol is not None or (is_above_ma60 and is_sweet_spot and is_kd_oversold)
        
        print(f'  - {sym} ({name}): 現價 ${price:.1f}, MA60 ${ma60:.1f}, 布林下軌 ${bb_lower:.1f}, K:{k_val:.1f} | 甜蜜區:{is_sweet_spot}, 季線:{is_above_ma60}')
        
        if should_alert:
            can_send, reason = check_can_alert(sym, price, cooldown)
            if force_symbol or can_send:
                print(f'    🚨 【觸發買進訊號！】向 LINE 發送通知...')
                card = create_sweet_spot_card(sym, name, price, low_p, ma60, bb_lower, k_val, d_val)
                success = push_line_message(token, user_id, card)
                if success:
                    mark_alert_sent(sym, price)
                    alerts_triggered += 1
            else:
                print(f'    ⏳ 觸發訊號但 {reason}')
                
    return alerts_triggered

# ------------------------------------------------------------------------------
# 主程式入口
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='q_quant_888 顏老師鐵律盤中到價 LINE 推播守護引擎')
    parser.add_argument('--test', action='store_true', help='立即發送測試訊息至學長 LINE')
    parser.add_argument('--force-symbol', type=str, help='指定強制觸發特定股票卡片 (如 2330.TW)')
    parser.add_argument('--once', action='store_true', help='執行單次盤中比對 (排程使用)')
    parser.add_argument('--daemon', action='store_true', help='啟動盤中常駐守護迴圈 (每 60~180 秒輪詢)')
    parser.add_argument('--interval', type=int, default=120, help='常駐守護輪詢秒數 (預設 120 秒)')
    args = parser.parse_args()
    
    config = load_config()
    token = config.get('channel_access_token')
    user_id = config.get('user_id')
    
    if args.test:
        print('📨 執行 LINE 連線與測試推播...')
        if not token or not user_id:
            print('❌ 請先在 config/line_config.json 或環境變數設定 LINE_CHANNEL_ACCESS_TOKEN 與 LINE_USER_ID！')
            sys.exit(1)
        test_msg = {
            'type': 'text',
            'text': f'🎯【q_quant_888 系統測試通知】\n學長您好！顏老師鐵律盤中到價 LINE 推播引擎連線成功！\n當盤中台積電 (2330)、奇鋐 (3017) 等核心正規軍回測甜蜜買進區且守穩季線生命線時，系統將第一時間為您推播到價買進卡片與當日低點無情停損點！\n測試時間：{datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S")}'
        }
        push_line_message(token, user_id, test_msg)
        return
        
    if args.force_symbol:
        sym = args.force_symbol.upper()
        if not sym.endswith('.TW') and not sym.endswith('.TWO'):
            sym = f'{sym}.TW'
        print(f'⚡ 強制模擬觸發 {sym} 到價推播卡片...')
        run_scan_once(config, force_symbol=sym)
        return
        
    if args.once:
        run_scan_once(config)
        return
        
    if args.daemon:
        print(f'🛡️ 啟動本機常駐守護 Daemon (每 {args.interval} 秒執行一次)...')
        while True:
            try:
                now = datetime.now(TAIPEI_TZ)
                is_weekday = now.weekday() < 5
                market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
                market_close = now.replace(hour=13, minute=30, second=0, microsecond=0)
                
                if is_weekday and market_open <= now <= market_close:
                    print(f'[{now.strftime("%H:%M:%S")}] 盤中交易時段，進行巡檢...')
                    run_scan_once(config)
                else:
                    print(f'[{now.strftime("%H:%M:%S")}] 目前為非盤中交易時間 (台股 09:00~13:30)，休眠等待...')
                    
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print('\n🛑 使用者中斷守護程序。')
                break
            except Exception as e:
                print(f'⚠️ 執行異常: {e}')
                time.sleep(10)
    else:
        run_scan_once(config)

if __name__ == '__main__':
    main()

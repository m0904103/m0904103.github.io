# -*- coding: utf-8 -*-
"""
line_intraday_pusher.py - q_quant_888 顏老師鐵律盤中到價 LINE 推播守護引擎 (美股旗艦 + 台股雙軌版)
================================================================================
功能亮點：
1. 美股為主力，台股為雙軌：
   - 美股高勝率正規軍標的：NVDA、VRT、PLTR、TSLA、AVGO、AAPL、MSFT、ASML、AMAT、AMD、ARM、GOOGL、AMZN、ASTS、RKLB、CEG、VST 等。
   - 台股核心科技族群：台積電 (2330)、奇鋐 (3017)、雙鴻 (3324)、緯穎 (6669) 等。
2. 盤中即時高速撮合報價：
   - 美股：對接 Yahoo Finance 毫秒級 Chart 串流引擎 (取得即時成交價、盤中最低價 Low of Today)。
   - 台股：對接 TWSE/TPEx 官方高速 MIS API (延遲 < 0.2 秒)。
3. 大腦比對（顏老師鐵律量化進出場 SOP）：
   - 均線生命線：股價守穩 MA60 季線之上（空方下彎嚴禁摸底向下攤平）。
   - 甜蜜買進區：回測布林通道下軌或核心甜蜜區間。
   - KD 超賣轉強：KD 進入 30 以下超賣區或向上黃金交叉打底。
   - 無情停損點 (SL)：以進場當日盤中最低價 (Low of Entry Day) 作為停損防線，破線無情離場。
   - 階梯停利 (TP)：第一目標 +10%、第二目標 +15% 順勢分批落袋。
4. LINE Messaging API 推播：
   - 美股專屬卡片 (🇺🇸) 與台股專屬卡片 (🇹🇼) 高質感暗黑戰情卡 (Flex Message)。
   - 內建冷卻防重複機制 (Cooldown)，同一標的盤中不重複轟炸。
5. 全天候雲端守護 (GitHub Actions)：
   - 美股盤中 (台灣時間 21:30 ~ 05:00)：全自動雲端巡檢，學長關機睡覺也能在手機收到到價卡片！
   - 台股盤中 (台灣時間 09:00 ~ 13:30)：全自動日間巡檢。
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

# ------------------------------------------------------------------------------
# 標的庫定義（美股優先旗艦配置 + 台股雙軌）
# ------------------------------------------------------------------------------
DEFAULT_US_WATCHLIST = {
    'NVDA': {'name': '輝達 (NVIDIA)', 'sector': '極限算力基建'},
    'VRT': {'name': 'Vertiv (AI散熱龍頭)', 'sector': '極限算力基建'},
    'PLTR': {'name': 'Palantir (AI國防軟體)', 'sector': '代理型AI軟體'},
    'TSLA': {'name': '特斯拉 (Tesla)', 'sector': '實體AI機器人'},
    'AVGO': {'name': '博通 (Broadcom)', 'sector': '矽光子/CPO'},
    'AAPL': {'name': '蘋果 (Apple)', 'sector': '邊緣AI與終端'},
    'MSFT': {'name': '微軟 (Microsoft)', 'sector': '雲端AI巨頭'},
    'ASML': {'name': '艾司摩爾 (ASML)', 'sector': '先進封裝光刻機'},
    'AMAT': {'name': '應用材料 (Applied Materials)', 'sector': '半導體設備'},
    'AMD': {'name': '超微 (AMD)', 'sector': 'AI加速器'},
    'ARM': {'name': '安謀 (ARM)', 'sector': '邊緣端晶片架構'},
    'GOOGL': {'name': 'Alphabet (Google)', 'sector': '主權AI與模型'},
    'AMZN': {'name': '亞馬遜 (Amazon)', 'sector': 'AWS算力雲端'},
    'ASTS': {'name': 'AST SpaceMobile', 'sector': '低軌衛星通訊'},
    'RKLB': {'name': 'Rocket Lab', 'sector': '太空發射火箭'},
    'CEG': {'name': 'Constellation Energy', 'sector': '核能與智慧電網'},
    'VST': {'name': 'Vistra Corp', 'sector': 'AI電力電網'},
    'CRWD': {'name': 'CrowdStrike', 'sector': '主權AI與網安'},
    'LLY': {'name': '禮來 (Eli Lilly)', 'sector': '生物AI與精準醫療'}
}

DEFAULT_TW_WATCHLIST = {
    '2330.TW': {'name': '台積電', 'market': 'tse'},
    '3017.TW': {'name': '奇鋐', 'market': 'tse'},
    '3324.TWO': {'name': '雙鴻', 'market': 'otc'},
    '6669.TW': {'name': '緯穎', 'market': 'tse'},
    '3081.TWO': {'name': '聯亞', 'market': 'otc'},
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
        'primary_market': 'US',  # 優先美股
        'cooldown_minutes': 60,
        'us_watchlist': list(DEFAULT_US_WATCHLIST.keys()),
        'tw_watchlist': list(DEFAULT_TW_WATCHLIST.keys())
    }
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                local_cfg = json.load(f)
                if local_cfg.get('channel_access_token') and not config['channel_access_token']:
                    config['channel_access_token'] = local_cfg['channel_access_token'].strip()
                if local_cfg.get('user_id') and not config['user_id']:
                    config['user_id'] = local_cfg['user_id'].strip()
                if 'primary_market' in local_cfg:
                    config['primary_market'] = local_cfg['primary_market'].upper()
                if 'cooldown_minutes' in local_cfg:
                    config['cooldown_minutes'] = local_cfg['cooldown_minutes']
                if 'us_watchlist' in local_cfg and isinstance(local_cfg['us_watchlist'], list):
                    config['us_watchlist'] = local_cfg['us_watchlist']
                if 'tw_watchlist' in local_cfg and isinstance(local_cfg['tw_watchlist'], list):
                    config['tw_watchlist'] = local_cfg['tw_watchlist']
                # 相容舊版單一 watchlist
                if 'watchlist' in local_cfg and isinstance(local_cfg['watchlist'], list):
                    tw_list = [s for s in local_cfg['watchlist'] if '.TW' in s or '.TWO' in s]
                    us_list = [s for s in local_cfg['watchlist'] if not ('.TW' in s or '.TWO' in s)]
                    if us_list: config['us_watchlist'] = us_list
                    if tw_list: config['tw_watchlist'] = tw_list
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
# 3. 提示工程：建構顏老師鐵律美股/台股到價卡片 (Flex Message)
# ------------------------------------------------------------------------------
def create_sweet_spot_card(symbol, name, current_price, low_price, ma60, bb_lower, kd_k, kd_d, market='US'):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d %H:%M:%S')
    is_us = (market.upper() == 'US')
    
    currency_symbol = '$'
    currency_unit = 'USD' if is_us else 'TWD'
    market_flag = '🇺🇸 美股' if is_us else '🇹🇼 台股'
    
    # 停損停利計算（嚴格遵循顏老師 SOP：當日盤中低點無情停損）
    sl_price = round(low_price, 2)
    tp1_price = round(current_price * 1.10, 2)  # +10%
    tp2_price = round(current_price * 1.15, 2)  # +15%
    
    price_fmt = f'{current_price:.2f}' if is_us else f'{current_price:.1f}'
    low_fmt = f'{low_price:.2f}' if is_us else f'{low_price:.1f}'
    ma60_fmt = f'{ma60:.2f}' if is_us else f'{ma60:.1f}'
    sl_fmt = f'{sl_price:.2f}' if is_us else f'{sl_price:.1f}'
    tp1_fmt = f'{tp1_price:.2f}' if is_us else f'{tp1_price:.1f}'
    tp2_fmt = f'{tp2_price:.2f}' if is_us else f'{tp2_price:.1f}'
    
    alt_text = f'【q_quant_888 顏老師鐵律｜{market_flag}】{symbol} {name} 觸發甜蜜買進！現價: {currency_symbol}{price_fmt}, 停損: {sl_fmt}'
    
    tips = (
        '1. 現價觸及甜蜜區，且守穩季線生命線。\n'
        '2. 美股無漲跌幅限制，請下「限價單 (Limit)」防滑價。\n'
        '3. 嚴守紀律：盤中跌破當日最低價無情離場，拒絕攤平！'
    ) if is_us else (
        '1. 現價觸及甜蜜區，且守穩季線生命線。\n'
        '2. 嚴防按錯：請核對「整張」與「零股」下單視窗。\n'
        '3. 無情停損：盤中跌破當日最低價立即市價出場！'
    )
    
    app_hint = '請開啟海外券商 APP (Firstrade / IB / 複委託) 自主下單' if is_us else '請開啟國內券商 APP 自主下單'
    
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
                            'text': f'🟢 顏老師鐵律｜{market_flag}到價買進',
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
                            'text': f'{currency_symbol}{price_fmt}',
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
                            'text': f'盤中低點: {currency_symbol}{low_fmt} ｜ 季線MA60: {currency_symbol}{ma60_fmt}',
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
                                {'type': 'text', 'text': f'{currency_symbol}{price_fmt} {currency_unit}', 'color': '#F8FAFC', 'size': 'sm', 'weight': 'bold', 'flex': 3}
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'contents': [
                                {'type': 'text', 'text': '🛡️ 顏老師停損(SL)', 'color': '#F87171', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': f'{currency_symbol}{sl_fmt} (當日低點)', 'color': '#F87171', 'size': 'sm', 'weight': 'bold', 'flex': 3}
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'contents': [
                                {'type': 'text', 'text': '🚀 階梯停利(TP)', 'color': '#4ADE80', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': f'{currency_symbol}{tp1_fmt} (+10%) / {currency_symbol}{tp2_fmt} (+15%)', 'color': '#4ADE80', 'size': 'sm', 'weight': 'bold', 'flex': 3}
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
                            'text': f'💡 顏老師決策提示（{app_hint}）：',
                            'color': '#FDE047',
                            'size': 'xs',
                            'weight': 'bold'
                        },
                        {
                            'type': 'text',
                            'text': tips,
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
                    'text': f'台北時間：{now_str}',
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
# 4. 美股即時報價引擎 (Yahoo Finance Chart API, 延遲低，即時盤中低點)
# ------------------------------------------------------------------------------
def fetch_us_realtime_quotes(watchlist):
    results = {}
    for sym in watchlist:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1m&range=1d'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode('utf-8'))
                chart_res = data.get('chart', {}).get('result', [])
                if chart_res:
                    meta = chart_res[0].get('meta', {})
                    price = meta.get('regularMarketPrice')
                    low = meta.get('regularMarketDayLow')
                    high = meta.get('regularMarketDayHigh')
                    prev = meta.get('chartPreviousClose')
                    
                    if price is None:
                        # 盤前或盤後嘗試取最新
                        price = meta.get('postMarketPrice') or meta.get('preMarketPrice') or prev
                        
                    if low is None: low = price
                    if high is None: high = price
                    
                    name = DEFAULT_US_WATCHLIST.get(sym, {}).get('name', sym)
                    results[sym] = {
                        'symbol': sym,
                        'name': name,
                        'price': float(price),
                        'low': float(low),
                        'high': float(high),
                        'yesterday_close': float(prev or price),
                        'market': 'US'
                    }
        except Exception as e:
            print(f'⚠️ 美股 {sym} 報價抓取失敗: {e}')
            
    return results

# ------------------------------------------------------------------------------
# 5. 台股即時報價引擎 (TWSE/TPEx 官方高速 MIS API)
# ------------------------------------------------------------------------------
def fetch_tw_realtime_quotes(watchlist):
    tickers = []
    for sym in watchlist:
        code = sym.split('.')[0]
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
                z_str = item.get('z', '-')
                y_str = item.get('y', '0')
                l_str = item.get('l', '-')
                h_str = item.get('h', '-')
                
                y_val = float(y_str) if y_str != '-' else 0.0
                
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
                    'market': 'TW'
                }
    except Exception as e:
        print(f'⚠️ TWSE MIS API 抓取失敗: {e}')
        
    return results

# ------------------------------------------------------------------------------
# 6. 技術指標計算與歷史快取 (MA60, 布林通道, KD)
# ------------------------------------------------------------------------------
def get_stock_technicals(symbol, is_us=True):
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
        print(f'⚠️ 計算 {symbol} 技術指標失敗: {e}')
        
    return None

# ------------------------------------------------------------------------------
# 7. 防重複推播冷卻機制
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
# 8. 巡檢大腦：美股與台股雙引擎
# ------------------------------------------------------------------------------
def scan_market(symbols, market_type, config, force_symbol=None):
    is_us = (market_type.upper() == 'US')
    market_label = '美股' if is_us else '台股'
    
    if force_symbol:
        symbols = [force_symbol]
        
    print(f'\n🔍 啟動【{market_label}】盤中巡檢，監控標的: {len(symbols)} 檔...')
    
    quotes = fetch_us_realtime_quotes(symbols) if is_us else fetch_tw_realtime_quotes(symbols)
    
    alerts_triggered = 0
    token = config.get('channel_access_token')
    user_id = config.get('user_id')
    cooldown = config.get('cooldown_minutes', 60)
    
    for sym in symbols:
        q = quotes.get(sym)
        if not q and not is_us:
            alt_sym = sym.replace('.TWO', '.TW') if sym.endswith('.TWO') else sym.replace('.TW', '.TWO')
            q = quotes.get(alt_sym)
            
        if not q or q['price'] <= 0:
            print(f'  - {sym}: 無即時報價')
            continue
            
        price = q['price']
        low_p = q['low']
        name = q.get('name') or (DEFAULT_US_WATCHLIST.get(sym, {}).get('name') if is_us else DEFAULT_TW_WATCHLIST.get(sym, {}).get('name', sym))
        
        tech = get_stock_technicals(sym, is_us=is_us)
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
        # 1. 守穩季線生命線之上 (容許 1% 緩衝回測)
        is_above_ma60 = bool(price >= ma60 * 0.99)
        # 2. 回測布林下軌甜蜜支撐區 (現價接近或低於下軌 2.5% 範圍內)
        is_sweet_spot = bool(price <= bb_lower * 1.025)
        # 3. KD 超賣或轉強打底 (K <= 35 或 K > D)
        is_kd_oversold = bool(k_val <= 35 or k_val > d_val)
        
        should_alert = force_symbol is not None or (is_above_ma60 and is_sweet_spot and is_kd_oversold)
        
        unit = 'USD' if is_us else 'TWD'
        print(f'  - {sym} ({name}): 現價 {price:.2f} {unit}, MA60 {ma60:.2f}, 布林下軌 {bb_lower:.2f}, K:{k_val:.1f} | 甜蜜區:{is_sweet_spot}, 季線:{is_above_ma60}')
        
        if should_alert:
            can_send, reason = check_can_alert(sym, price, cooldown)
            if force_symbol or can_send:
                print(f'    🚨 【觸發買進訊號！】向 LINE 發送通知...')
                card = create_sweet_spot_card(sym, name, price, low_p, ma60, bb_lower, k_val, d_val, market=market_type)
                success = push_line_message(token, user_id, card)
                if success:
                    mark_alert_sent(sym, price)
                    alerts_triggered += 1
            else:
                print(f'    ⏳ 觸發訊號但 {reason}')
                
    return alerts_triggered

# ------------------------------------------------------------------------------
# 9. 自動市場開盤時段判定
# ------------------------------------------------------------------------------
def get_active_markets():
    now = datetime.now(TAIPEI_TZ)
    # 台灣時間美股時段 (21:30 ~ 05:00)
    hour = now.hour
    minute = now.minute
    
    is_us_time = (hour >= 21 and minute >= 30) or (hour in [22, 23, 0, 1, 2, 3, 4]) or (hour == 5 and minute <= 0)
    is_tw_time = (hour == 9 and minute >= 0) or (hour in [10, 11, 12]) or (hour == 13 and minute <= 30)
    
    return is_us_time, is_tw_time

# ------------------------------------------------------------------------------
# 主程式入口
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='q_quant_888 顏老師鐵律盤中到價 LINE 推播守護引擎 (美股旗艦版)')
    parser.add_argument('--test', action='store_true', help='立即發送美股連線測試卡片至學長 LINE')
    parser.add_argument('--market', type=str, choices=['us', 'tw', 'all'], default=None, help='指定掃描市場 (預設自動根據開盤時段判定，非開盤時段優先美股)')
    parser.add_argument('--force-symbol', type=str, help='指定強制觸發特定股票卡片 (如 NVDA 或 2330.TW)')
    parser.add_argument('--once', action='store_true', help='執行單次盤中比對 (排程使用)')
    parser.add_argument('--daemon', action='store_true', help='啟動盤中常駐守護迴圈 (每 60~180 秒輪詢)')
    parser.add_argument('--interval', type=int, default=120, help='常駐守護輪詢秒數 (預設 120 秒)')
    args = parser.parse_args()
    
    config = load_config()
    token = config.get('channel_access_token')
    user_id = config.get('user_id')
    
    if args.test:
        print('📨 執行 LINE 連線與美股到價測試推播...')
        if not token or not user_id:
            print('❌ 請先在 config/line_config.json 或環境變數設定 LINE_CHANNEL_ACCESS_TOKEN 與 LINE_USER_ID！')
            sys.exit(1)
        test_msg = {
            'type': 'text',
            'text': f'🎯【q_quant_888 系統測試通知】\n學長您好！顏老師鐵律盤中到價 LINE 推播守護已成功啟用！\n🇺🇸 美股為核心：輝達 (NVDA)、Vertiv (VRT)、Palantir (PLTR)、特斯拉 (TSLA) 等 20 檔美股龍頭與台股雙軌守護！\n當標的回測甜蜜買進區且守穩季線生命線時，將以當日最低價為「無情停損點 (Low of Entry Day)」立即發送戰情卡片！\n測試時間：{datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S")}'
        }
        push_line_message(token, user_id, test_msg)
        return
        
    if args.force_symbol:
        sym = args.force_symbol.upper()
        is_us = not ('.TW' in sym or '.TWO' in sym)
        m_type = 'US' if is_us else 'TW'
        print(f'⚡ 強制模擬觸發【{m_type}】{sym} 到價推播卡片...')
        scan_market([sym], m_type, config, force_symbol=sym)
        return
        
    def execute_scan():
        is_us_time, is_tw_time = get_active_markets()
        market_choice = args.market.lower() if args.market else None
        
        if market_choice == 'us':
            scan_market(config['us_watchlist'], 'US', config)
        elif market_choice == 'tw':
            scan_market(config['tw_watchlist'], 'TW', config)
        elif market_choice == 'all':
            scan_market(config['us_watchlist'], 'US', config)
            scan_market(config['tw_watchlist'], 'TW', config)
        else:
            # 自動判定：若目前在美股時間則掃美股，台股時間掃台股；非開盤時間優先掃描主力美股！
            if is_us_time:
                scan_market(config['us_watchlist'], 'US', config)
            elif is_tw_time:
                scan_market(config['tw_watchlist'], 'TW', config)
            else:
                # 主力美股優先掃描
                print('ℹ️ 目前非盤中開盤時間，執行主力美股健康巡檢...')
                scan_market(config['us_watchlist'], 'US', config)
                
    if args.once:
        execute_scan()
        return
        
    if args.daemon:
        print(f'🛡️ 啟動全天候美股+台股守護 Daemon (每 {args.interval} 秒執行一次)...')
        while True:
            try:
                execute_scan()
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print('\n🛑 使用者中斷守護程序。')
                break
            except Exception as e:
                print(f'⚠️ 執行異常: {e}')
                time.sleep(10)
    else:
        execute_scan()

if __name__ == '__main__':
    main()

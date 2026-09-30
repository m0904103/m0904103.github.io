# -*- coding: utf-8 -*-
"""
line_intraday_pusher.py - q_quant_888 顏老師鐵律波段到價 LINE 推播守護引擎 (美股旗艦 + 台股雙軌版)
================================================================================
【顏春煌教授 8-3-1、8-3-2、8-4-2 原音心法深度實踐】
1. 波段為王，拒絕當沖：
   - 當沖手續費與交易稅吃掉獲利，振幅受限；優質成長股波段能賺取 50% 甚至 100% 以上大行情！
2. 尾盤確認進場法 (Tail-End Entry Confirmation)：
   - 盤中回測布林下軌、KD < 20~30 超賣區時「先列入重點關注，不毛躁追價」。
   - 於收盤前 15~30 分鐘（台股 13:15 / 美股收盤前半小時）確認 K 線收腳站回布林通道內、KD 金叉打底，才正式進場買進。
3. 買進日低點波段守護防線 (Low of Entry Day)：
   - 買進當天絕不自我停損（當天收盤進場，低點已確立）。
   - 當天最低價即為這筆波段交易未來數週的「基準防守線」。
   - 進入持有期 (Holding Period)：只要每日不跌破買進日最低價，安心抱牢！若未來某日不幸跌破，才無情停損！
4. 長短雙軌部位管理 (Dual-Track Allocation)：
   - 短期部位 (50%)：+5% ~ +10% 價差先獲利了結，落袋為安。
   - 波段部位 (50%)：一路抱牢，直到衝過布林通道上軌、跌回通道內部時才賣出，享受最大主升段！
5. 季線生命線 (MA60) 向上保護原則：
   - 季線向上且站穩生命線之標的才具備做多高勝率（京元電獲利 vs 中興電虧損的經典對比）。
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
    'LLY': {'name': '禮來 (Eli Lilly)', 'sector': '生物AI與精準醫療'},
    'V': {'name': '威士 (Visa)', 'sector': '防禦對沖/ESG龍頭'}
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
# 🌾 阿村伯（蔡鎮村博士） 30年操盤大數據與風控名言庫 (動態輪動)
# ------------------------------------------------------------------------------
DR_TSUN_QUOTES = [
    {
        'category': '盤前沉著',
        'title': '🌾 阿村伯 30年實戰操盤心法：',
        'quote': '「開盤前 15 分鐘是機構法人洗盤誘空的時刻，聰明操盤手冷眼旁觀莫急躁！到價才開槍，沒到價就安心喝茶。只要部位抱得住、風控守得牢，今晚才能睡得著香！」'
    },
    {
        'category': '盤前沉著',
        'title': '🌾 阿村伯 開盤觀潮銘言：',
        'quote': '「開盤爆量莫盲追，盤中衝高多洗盤！大數據顯示真正的安全買點，往往隱藏在收盤前趨勢確立的冷靜落腳處。讓子彈飛一會兒，本金安全第一！」'
    },
    {
        'category': '風控鐵律',
        'title': '🌾 阿村伯 兩度歸零血淚警言：',
        'quote': '「阿村伯年輕時曾兩度賠光身家，深刻領悟：只要一次致命重傷，前面賺 100 次都是白費！不要急著發大財，先學會不虧大錢，保護本金是生存第一法則！」'
    },
    {
        'category': '無情停損',
        'title': '🌾 阿村伯 機器人停損紀律：',
        'quote': '「進場前先算好虧損上限，觸發停損時要像機器人一樣執行！向下攤平只會越攤越貧，股票下跌必有法人知道而散戶不知道的理由，切勿護短！」'
    },
    {
        'category': '大數據勝率',
        'title': '🌾 阿村伯 大數據觀察心法：',
        'quote': '「不識多空真面目，只緣身在波浪中！傳統技術分析看的是『點』，大數據分析看的是『面』。讓歷史統計勝率告訴你何時該進、何時該縮，勝率大於 70% 才能重兵出擊！」'
    },
    {
        'category': '大數據勝率',
        'title': '🌾 阿村伯 節慶勝率法則：',
        'quote': '「股市也有四季輪動與節慶效應！不聽信市場小道消息，完全依據當前籌碼與大數據數據行動。數據說話最客觀，勝率未達標準前寧可空倉等待！」'
    },
    {
        'category': '選股護城河',
        'title': '🌾 阿村伯 三率三升選股鐵律：',
        'quote': '「毛利率、營業利益率、稅後純益率『三率三升』才是企業真正的護城河！徹底淘汰三率衰退的落水狗，跟著法人與千張大戶站在買方，波段才能抱得穩如泰山！」'
    },
    {
        'category': '選股護城河',
        'title': '🌾 阿村伯 籌碼深度解密：',
        'quote': '「看盤先看主力底牌！外資期貨空單、八大官股庫藏、千張大戶持股比例，籌碼沉澱且大戶集中度上升的地方，才是下一波飆股的誕生地！」'
    },
    {
        'category': '持盈保泰',
        'title': '🌾 阿村伯 退休資產防禦觀念：',
        'quote': '「留得青山在，不怕沒柴燒！保留 20%~30% 以上的現金流動性，拒絕高槓桿押注。高現金就是最堅固的戰略堡壘，手中有糧，心中不慌！」'
    },
    {
        'category': '均線順勢流',
        'title': '🌾 阿村伯 均線順勢法則：',
        'quote': '「5 日線跌破 10 日線，短線亮紅燈；60MA 季線向上，才是真正的波段生命線！均線下彎的弱勢股，反彈都是逃命波，絕不搶反彈！」'
    }
]

# ------------------------------------------------------------------------------
# 🎓 顏春煌教授 12講117單元計量與波段鐵律庫 (源自顏老師語錄合集.md 動態輪動)
# ------------------------------------------------------------------------------
PROF_YEN_QUOTES = [
    {
        'category': '理性與迷思',
        'title': '🎓 顏春煌教授 投資理性與排除迷思：',
        'quote': '「我們不會像投顧老師帶著同學做暴利股票，而是讓大家深入且快速排除投資迷思！運用系統化的方法與保持理性的態度進行投資，脫離新手階段，讓財富穩健累積。」'
    },
    {
        'category': '計量鐵律',
        'title': '🎓 顏春煌教授 數位學習與計量鐵律：',
        'quote': '「不求次次暴利，但求筆筆合規！開盤前 15 分鐘市場常有機構情緒性激烈洗盤。恪守 60MA 季線生命線與正期望值 E[R] > 0，切勿在洗盤中盲目追高或恐慌拋售！」'
    },
    {
        'category': '波段為王',
        'title': '🎓 顏春煌教授 8-3-1 波段為王心法：',
        'quote': '「波段為王，拒絕當沖！當沖手續費與交易稅吃掉大部分利潤，且振幅受限。優質成長股站在季線生命線上，能為你賺取 50% 甚至 100% 以上大波段利潤！」'
    },
    {
        'category': '尾盤進場',
        'title': '🎓 顏春煌教授 8-3-2 尾盤進場確認法：',
        'quote': '「盤中回測布林下軌與 KD 低檔時先冷靜觀察，不毛躁追價！收盤前 15~30 分鐘確認 K 線收腳站回布林通道內、KD 金叉打底，才正式下單建倉！」'
    },
    {
        'category': '守護防線',
        'title': '🎓 顏春煌教授 8-4-2 買進日低點防線：',
        'quote': '「買進當天絕不停損！當天最低價即為這筆波段未來數週的基準防守線。進入持有期後，只要每日收盤未跌破買進日低點，安心抱牢，讓獲利奔跑！」'
    },
    {
        'category': '雙軌配置',
        'title': '🎓 顏春煌教授 長短雙軌部位管理：',
        'quote': '「50% 短期部位：達 +5%~+10% 價差先行落袋為安；50% 波段部位：一路抱牢直到衝過布林通道上軌且折回時才賣出，享受主升段最大獲利！」'
    },
    {
        'category': '布林常態分佈',
        'title': '🎓 顏春煌教授 布林通道統計學：',
        'quote': '「股價分佈符合統計常態分佈，正負 2 個標準差涵蓋 95.4% 的價格變動。當股價觸及下軌反彈才是安全進場點，突破上軌折回則是停利訊號！」'
    },
    {
        'category': '量先價行',
        'title': '🎓 顏春煌教授 OBV 能量潮法則：',
        'quote': '「量先價行！成交量往往先於股價變化。當股價在低檔盤整、OBV 能量潮率先向上突破時，代表主力正在沉澱吸籌，是趨勢反轉的前兆！」'
    },
    {
        'category': '排除心理偏見',
        'title': '🎓 顏春煌教授 克服追高殺低陷阱：',
        'quote': '「散戶最常陷入追高殺低的情緒陷阱。技術分析指標能幫我們排除主觀心理偏見，客觀判斷高低點。我們無法買在最低賣在最高，但能避開相對高點追價與低點恐慌殺低！」'
    },
    {
        'category': '程式回測實證',
        'title': '🎓 顏春煌教授 Python 量化回測：',
        'quote': '「透過 Python 程式與歷史數據回測，用客觀驗證替代主觀猜測！只有經得起歷史數據考驗的策略，才能在充滿不確定性的金融市場中帶你穩健前行。」'
    }
]

import random

def get_rotating_dr_tsun_quote(seed=None):
    if seed is not None:
        return DR_TSUN_QUOTES[seed % len(DR_TSUN_QUOTES)]
    return random.choice(DR_TSUN_QUOTES)

def get_rotating_prof_yen_quote(seed=None):
    if seed is not None:
        return PROF_YEN_QUOTES[seed % len(PROF_YEN_QUOTES)]
    return random.choice(PROF_YEN_QUOTES)

# ------------------------------------------------------------------------------
# 1. 設定讀取模組
# ------------------------------------------------------------------------------
def load_config():
    config = {
        'channel_access_token': os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '').strip(),
        'user_id': os.environ.get('LINE_USER_ID', '').strip(),
        'primary_market': 'US',
        'cooldown_minutes': 20,
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
def push_line_message(token, user_id, messages, mode='broadcast'):
    if not token:
        print('❌ 未設定 LINE_CHANNEL_ACCESS_TOKEN，略過推播。')
        return False

    messages_list = messages if isinstance(messages, list) else [messages]
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    if mode == 'broadcast' or not user_id:
        url = 'https://api.line.me/v2/bot/message/broadcast'
        payload = {'messages': messages_list}
    else:
        url = 'https://api.line.me/v2/bot/message/push'
        payload = {'to': user_id, 'messages': messages_list}
    
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            if res.status == 200:
                print('✅ LINE 戰情卡片已成功廣播推播至所有好友/成員手機！')
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
# 3. 提示工程：建構顏老師正統波段交易戰情卡片 (Flex Message)
# ------------------------------------------------------------------------------
def create_sweet_spot_card(symbol, name, current_price, low_price, ma60, bb_lower, kd_k, kd_d, market='US'):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d %H:%M:%S')
    is_us = (market.upper() == 'US')
    
    currency_symbol = '$'
    currency_unit = 'USD' if is_us else 'TWD'
    market_flag = '🇺🇸 美股' if is_us else '🇹🇼 台股'
    
    # 顏老師正統 SOP：以買進當日盤中低點作為未來持有期間的波段防守點 (Low of Entry Day)
    sl_price = round(low_price, 2)
    # 顏老師雙軌部位獲利目標：短期部位 +5%~+10%，波段部位抱到突破布林上軌折回
    tp1_price = round(current_price * 1.05, 2)  # 短期第一目標 +5%
    tp2_price = round(current_price * 1.10, 2)  # 短期第二目標 +10%
    
    price_fmt = f'{current_price:.2f}' if is_us else f'{current_price:.1f}'
    low_fmt = f'{low_price:.2f}' if is_us else f'{low_price:.1f}'
    ma60_fmt = f'{ma60:.2f}' if is_us else f'{ma60:.1f}'
    sl_fmt = f'{sl_price:.2f}' if is_us else f'{sl_price:.1f}'
    tp1_fmt = f'{tp1_price:.2f}' if is_us else f'{tp1_price:.1f}'
    tp2_fmt = f'{tp2_price:.2f}' if is_us else f'{tp2_price:.1f}'
    
    alt_text = f'【q_quant_888 顏老師鐵律｜{market_flag}波段預警】{symbol} {name} 觸發甜蜜買進！現價: {currency_symbol}{price_fmt}'
    
    entry_timing = (
        '現價已回測進入布林下軌超賣區！請於【收盤前半小時 (美東 15:30 左右)】確認 K 線收腳站回通道內再行進場。'
        if is_us else
        '現價已回測進入布林下軌超賣區！請於【收盤前 15 分鐘 (13:15 左右)】確認 K 線紅棒站回底線再行進場。'
    )
    
    tips = (
        '1. 【拒絕當沖】顏老師強調波段賺取 50%~100% 大行情，反對頻繁當沖耗損成本。\n'
        '2. 【進場當日不停損】今日低點為「未來波段防守線」；持有期只要每日收盤不破此低點，安心續抱！\n'
        '3. 【長短雙軌配置】50% 部位達 +5%~+10% 先行落袋；50% 波段部位抱到衝出布林上軌折回才賣！'
    )
    
    app_hint = '美股無漲跌幅限制，請採「限價單 (Limit Order)」掛單防滑價' if is_us else '下單前請務必核對「整張(1,000股)」與「零股(100股)」視窗防呆'
    
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
                            'text': f'🟢 顏老師鐵律｜{market_flag}波段買進預警',
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
                            'text': symbol if (not name or name == symbol) else (name if symbol in name else f'{symbol} {name}'),
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
                            'text': f'今日盤中低點: {currency_symbol}{low_fmt} ｜ 季線MA60: {currency_symbol}{ma60_fmt}',
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
                                    'text': '季線生命線守護',
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
                                    'text': f'KD超賣打底 (K:{kd_k:.0f})',
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
                                    'text': '布林下軌甜蜜支撐',
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
                                {'type': 'text', 'text': '🛡️ 未來波段停損線', 'color': '#F87171', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': f'{currency_symbol}{sl_fmt} (買進日低點防線)', 'color': '#F87171', 'size': 'sm', 'weight': 'bold', 'flex': 3}
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'contents': [
                                {'type': 'text', 'text': '🚀 短期價差目標', 'color': '#4ADE80', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': f'{currency_symbol}{tp1_fmt} (+5%) ~ {currency_symbol}{tp2_fmt} (+10%)', 'color': '#4ADE80', 'size': 'sm', 'weight': 'bold', 'flex': 3}
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'contents': [
                                {'type': 'text', 'text': '🌊 波段抱牢目標', 'color': '#38BDF8', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': '衝出布林上軌折回才賣', 'color': '#38BDF8', 'size': 'sm', 'weight': 'bold', 'flex': 3}
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
                            'text': f'💡 顏老師實務進出場心法與防呆：',
                            'color': '#FDE047',
                            'size': 'xs',
                            'weight': 'bold'
                        },
                        {
                            'type': 'text',
                            'text': f'【進場確認】{entry_timing}\n{tips}\n⚠️ 注意：{app_hint}。',
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
                    'text': f'台北時間：{now_str} ｜ 波段守護系統',
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
# 4. 美股即時報價引擎 (Yahoo Finance Chart API)
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
        
    print(f'\n🔍 啟動【{market_label}】波段巡檢，監控標的: {len(symbols)} 檔...')
    
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
                print(f'    🚨 【觸發波段買進預警！】向 LINE 發送通知...')
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
    hour = now.hour
    minute = now.minute
    
    is_us_time = (hour >= 21 and minute >= 30) or (hour in [22, 23, 0, 1, 2, 3, 4]) or (hour == 5 and minute <= 0)
    is_tw_time = (hour == 8 and minute >= 30) or (hour in [9, 10, 11, 12]) or (hour == 13 and minute <= 30)
    
    return is_us_time, is_tw_time

def create_premarket_guidance_card(market='US'):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d %H:%M:%S')
    is_us = (market.upper() == 'US')
    market_flag = '🇺🇸 美股' if is_us else '🇹🇼 台股'
    open_time_str = '21:30' if is_us else '09:00'
    
    dr_tsun_item = get_rotating_dr_tsun_quote()
    prof_yen_item = get_rotating_prof_yen_quote()
    
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
                    'type': 'text',
                    'text': f'🛡️ 盤前安定軍心卡 ｜ {market_flag}',
                    'weight': 'bold',
                    'color': '#38BDF8',
                    'size': 'sm'
                },
                {
                    'type': 'text',
                    'text': f'開盤前夕 ｜ 雙師學術與實戰指導',
                    'weight': 'bold',
                    'size': 'xl',
                    'color': '#F8FAFC',
                    'margin': 'xs'
                },
                {
                    'type': 'text',
                    'text': f'開盤時間：今晚 {open_time_str} ｜ 守護時間：{now_str}',
                    'color': '#94A3B8',
                    'size': 'xs',
                    'margin': 'xs'
                }
            ]
        },
        'body': {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#1E293B',
            'paddingAll': '16px',
            'contents': [
                # 🎓 顏春煌教授 語錄 (動態輪動)
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#0F172A',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'none',
                    'contents': [
                        {
                            'type': 'text',
                            'text': prof_yen_item['title'],
                            'weight': 'bold',
                            'color': '#60A5FA',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': prof_yen_item['quote'],
                            'color': '#E2E8F0',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                },
                # 🌾 阿村伯 語錄 (動態輪動)
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#0F172A',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'md',
                    'contents': [
                        {
                            'type': 'text',
                            'text': dr_tsun_item['title'],
                            'weight': 'bold',
                            'color': '#FBBF24',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': dr_tsun_item['quote'],
                            'color': '#E2E8F0',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                },
                # 三不原則
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#334155',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'md',
                    'contents': [
                        {
                            'type': 'text',
                            'text': '🛡️ 盤前開槍三大紀律公約：',
                            'weight': 'bold',
                            'color': '#34D399',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': '1. ❌【不急追高】開盤 15 分鐘靜觀其變，不搶掛市價追高。\n2. ❌【不恐慌殺低】只要收盤未跌破 60MA 季線生命線，絕不被洗盤嚇退。\n3. 🟢【只在甜美區開槍】靜待開盤後若出現 99分 + 甜美區（+0.5%~+5.0%）到價圖卡，再從容限價掛單建倉！',
                            'color': '#F8FAFC',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                }
            ]
        },
        'footer': {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#0F172A',
            'contents': [
                {
                    'type': 'text',
                    'text': '正規軍 4.0 安定軍心系統 ｜ 守護全體學員資產',
                    'color': '#64748B',
                    'size': 'xs',
                    'align': 'center'
                }
            ]
        }
    }
    
    return {
        'type': 'flex',
        'altText': f'🛡️【q_quant_888 盤前安定軍心卡】{market_flag} 雙師輪動紀律與實戰心法！',
        'contents': flex_content
    }

def create_intraday_noon_card():
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d %H:%M:%S')
    dr_tsun_item = get_rotating_dr_tsun_quote()
    prof_yen_item = get_rotating_prof_yen_quote()
    
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
                    'type': 'text',
                    'text': '🛡️ 12:30 盤中定心丸 ｜ 🇹🇼 台股持盈保泰',
                    'weight': 'bold',
                    'color': '#38BDF8',
                    'size': 'sm'
                },
                {
                    'type': 'text',
                    'text': '距 13:30 收盤倒數 1 小時 ｜ 雙師指導',
                    'weight': 'bold',
                    'size': 'xl',
                    'color': '#F8FAFC',
                    'margin': 'xs'
                },
                {
                    'type': 'text',
                    'text': f'巡檢時間：{now_str} ｜ 離收盤剩餘 60 分鐘',
                    'color': '#94A3B8',
                    'size': 'xs',
                    'margin': 'xs'
                }
            ]
        },
        'body': {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#1E293B',
            'paddingAll': '16px',
            'contents': [
                # 🎓 顏春煌教授 語錄 (動態輪動)
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#0F172A',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'none',
                    'contents': [
                        {
                            'type': 'text',
                            'text': prof_yen_item['title'],
                            'weight': 'bold',
                            'color': '#60A5FA',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': prof_yen_item['quote'],
                            'color': '#E2E8F0',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                },
                # 🌾 阿村伯 語錄 (動態輪動)
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#0F172A',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'md',
                    'contents': [
                        {
                            'type': 'text',
                            'text': dr_tsun_item['title'],
                            'weight': 'bold',
                            'color': '#FBBF24',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': dr_tsun_item['quote'],
                            'color': '#E2E8F0',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                },
                # 焦點標的表
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#334155',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'md',
                    'contents': [
                        {
                            'type': 'text',
                            'text': '📊 焦點標的收盤前防守點參考：',
                            'weight': 'bold',
                            'color': '#34D399',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': '• 2474 可成：現價 $206.0 ｜ 季線硬防守 $199.13 (100%勝率)\n• 6669 緯穎：現價 $2,105 ｜ 季線硬防守 $2,056 (KD K=11.7超賣)\n• 1519 華城：現價 $699.0 ｜ 季線硬防守 $683.37 (乖離 +2.29%)',
                            'color': '#F8FAFC',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                }
            ]
        },
        'footer': {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#0F172A',
            'contents': [
                {
                    'type': 'text',
                    'text': '正規軍 4.0 戰情室 ｜ 13:15 發送收盤前終極確認卡',
                    'color': '#64748B',
                    'size': 'xs',
                    'align': 'center'
                }
            ]
        }
    }
    
    return {
        'type': 'flex',
        'altText': '🛡️【q_quant_888 12:30 盤中定心丸】距收盤倒數 1 小時雙師持盈保泰戰術指南！',
        'contents': flex_content
    }

def create_postmarket_summary_card(market='US'):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d %H:%M:%S')
    is_us = (market.upper() == 'US')
    market_flag = '🇺🇸 美股' if is_us else '🇹🇼 台股'
    
    dr_tsun_item = get_rotating_dr_tsun_quote()
    prof_yen_item = get_rotating_prof_yen_quote()
    
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
                    'type': 'text',
                    'text': f'🌅 盤後總結與戰果檢核卡 ｜ {market_flag}',
                    'weight': 'bold',
                    'color': '#10B981',
                    'size': 'sm'
                },
                {
                    'type': 'text',
                    'text': f'收盤結算 ｜ 雙師總結與持盈保泰戰報',
                    'weight': 'bold',
                    'size': 'xl',
                    'color': '#F8FAFC',
                    'margin': 'xs'
                },
                {
                    'type': 'text',
                    'text': f'結算時間：{now_str} ｜ 全單元點燈完成',
                    'color': '#94A3B8',
                    'size': 'xs',
                    'margin': 'xs'
                }
            ]
        },
        'body': {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#1E293B',
            'paddingAll': '16px',
            'contents': [
                # 🎓 顏春煌教授 語錄 (動態輪動)
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#0F172A',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'none',
                    'contents': [
                        {
                            'type': 'text',
                            'text': prof_yen_item['title'],
                            'weight': 'bold',
                            'color': '#60A5FA',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': prof_yen_item['quote'],
                            'color': '#E2E8F0',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                },
                # 🌾 阿村伯 語錄 (動態輪動)
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#0F172A',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'md',
                    'contents': [
                        {
                            'type': 'text',
                            'text': dr_tsun_item['title'],
                            'weight': 'bold',
                            'color': '#FBBF24',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': dr_tsun_item['quote'],
                            'color': '#E2E8F0',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                },
                # 盤後檢核三步驟
                {
                    'type': 'box',
                    'layout': 'vertical',
                    'backgroundColor': '#334155',
                    'cornerRadius': '8px',
                    'paddingAll': '12px',
                    'margin': 'md',
                    'contents': [
                        {
                            'type': 'text',
                            'text': '📊 盤後資產檢核三步驟：',
                            'weight': 'bold',
                            'color': '#34D399',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': '1. 🟢【波段防守線檢查】：確認持股（如 V, AMZN, 2474 等）收盤價是否守穩「買進日低點防線」與 60MA 生命線。\n2. 🟢【綠燈100%過關】：學習單元與系統數據已發送全綠燈點燈，合規滿分。\n3. 🔴【心態平靜安心】：今日無過度當沖與衝動操作，保留資金實力迎接明日戰局！',
                            'color': '#F8FAFC',
                            'size': 'xs',
                            'wrap': True,
                            'margin': 'xs'
                        }
                    ]
                }
            ]
        },
        'footer': {
            'type': 'box',
            'layout': 'vertical',
            'backgroundColor': '#0F172A',
            'contents': [
                {
                    'type': 'text',
                    'text': '正規軍 4.0 持盈保泰系統 ｜ 感謝學員每日嚴守紀律',
                    'color': '#64748B',
                    'size': 'xs',
                    'align': 'center'
                }
            ]
        }
    }
    
    return {
        'type': 'flex',
        'altText': f'🌅【q_quant_888 盤後總結卡】{market_flag} 雙師盤後戰報與結算指導！',
        'contents': flex_content
    }

# ------------------------------------------------------------------------------
# 主程式入口
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='q_quant_888 顏老師鐵律波段到價 LINE 推播守護引擎')
    parser.add_argument('--noon', action='store_true', help='立即推播 12:30 盤中定心丸與持盈保泰戰術卡片')
    parser.add_argument('--premarket', action='store_true', help='立即推播美股/台股盤前安定軍心與雙師教育指導卡片')
    parser.add_argument('--postmarket', action='store_true', help='立即推播美股/台股盤後總結與戰果檢核卡片')
    parser.add_argument('--test', action='store_true', help='立即發送波段連線測試卡片至學長 LINE')
    parser.add_argument('--market', type=str, choices=['us', 'tw', 'all'], default=None, help='指定掃描市場 (預設自動根據開盤時段判定，非開盤時段優先美股)')
    parser.add_argument('--force-symbol', type=str, help='指定強制觸發特定股票卡片 (如 NVDA 或 2330.TW)')
    parser.add_argument('--once', action='store_true', help='執行單次盤中比對 (排程使用)')
    parser.add_argument('--daemon', action='store_true', help='啟動常駐守護迴圈 (每 60~180 秒輪詢)')
    parser.add_argument('--interval', type=int, default=120, help='常駐守護輪詢秒數 (預設 120 秒)')
    args = parser.parse_args()
    
    config = load_config()
    token = config.get('channel_access_token')
    user_id = config.get('user_id')
    
    if args.noon:
        print('🛡️ 執行 LINE 12:30 盤中定心丸與持盈保泰戰術廣播推播...')
        card = create_intraday_noon_card()
        push_line_message(token, user_id, card, mode='broadcast')
        return
    
    if args.premarket:
        print('🛡️ 執行 LINE 盤前安定軍心與雙師教育指導廣播推播...')
        m_type = args.market.upper() if args.market else 'US'
        card = create_premarket_guidance_card(market=m_type)
        push_line_message(token, user_id, card, mode='broadcast')
        return

    if args.postmarket:
        print('🌅 執行 LINE 盤後總結與戰果檢核廣播推播...')
        m_type = args.market.upper() if args.market else 'US'
        card = create_postmarket_summary_card(market=m_type)
        push_line_message(token, user_id, card, mode='broadcast')
        return
    
    if args.test:
        print('📨 執行 LINE 連線與顏老師波段心法測試推播...')
        if not token or not user_id:
            print('❌ 請先在 config/line_config.json 或環境變數設定 LINE_CHANNEL_ACCESS_TOKEN 與 LINE_USER_ID！')
            sys.exit(1)
        test_msg = {
            'type': 'text',
            'text': f'🎯【q_quant_888 顏老師波段心法測試通知】\n學長您好！顏老師鐵律波段到價守護引擎連線成功！\n🌟 核心心法：\n1. 波段為王，堅決反對沉迷當沖！\n2. 盤中到價只作監控，收盤前半小時確認站穩布林下軌才進場！\n3. 買進當天絕不停損，今日最低價為未來持有期的「基準防守線」！\n4. 50% 部位賺 5%~10% 先行落袋，50% 波段部位抱牢主升段！\n測試時間：{datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S")}'
        }
        push_line_message(token, user_id, test_msg)
        return
        
    if args.force_symbol:
        sym = args.force_symbol.upper()
        is_us = not ('.TW' in sym or '.TWO' in sym)
        m_type = 'US' if is_us else 'TW'
        print(f'⚡ 強制模擬觸發【{m_type}】{sym} 顏老師波段到價卡片...')
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
            if is_us_time:
                scan_market(config['us_watchlist'], 'US', config)
            elif is_tw_time:
                scan_market(config['tw_watchlist'], 'TW', config)
            else:
                print('ℹ️ 目前非盤中開盤時間，執行主力美股健康巡檢...')
                scan_market(config['us_watchlist'], 'US', config)
                
    if args.once:
        execute_scan()
        return
        
    if args.daemon:
        print(f'🛡️ 啟動全天候美股+台股波段守護 Daemon (每 {args.interval} 秒執行一次)...')
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

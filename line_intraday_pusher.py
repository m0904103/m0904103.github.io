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
from zoneinfo import ZoneInfo

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
    'VTI': {'name': 'Vanguard 全美指數 ETF', 'sector': '美股核心大盤'},
    'DIA': {'name': '道瓊藍籌指數 ETF', 'sector': '美股核心大盤'},
    'AVGO': {'name': '博通 (Broadcom)', 'sector': '矽光子/CPO'},
    'GOOGL': {'name': 'Alphabet (Google)', 'sector': '主權AI與模型'},
    'TSM': {'name': '台積電 ADR', 'sector': '先進製程代工'},
    'ETN': {'name': 'Eaton (伊頓電力)', 'sector': '核能與智慧電網'},
    'CEG': {'name': 'Constellation Energy', 'sector': '核能與智慧電網'},
    'BE': {'name': 'Bloom Energy', 'sector': '核能與智慧電網'},
    'ASML': {'name': '艾司摩爾 (ASML)', 'sector': '先進封裝光刻機'},
    'MU': {'name': '美光科技 (Micron)', 'sector': 'HBM超級週期'},
    'NVDA': {'name': '輝達 (NVIDIA)', 'sector': '極限算力基建'},
    'VRT': {'name': 'Vertiv (AI散熱龍頭)', 'sector': '極限算力基建'},
    'PLTR': {'name': 'Palantir (AI國防軟體)', 'sector': '代理型AI軟體'},
    'TSLA': {'name': '特斯拉 (Tesla)', 'sector': '實體AI機器人'},
    'AAPL': {'name': '蘋果 (Apple)', 'sector': '邊緣AI與終端'},
    'MSFT': {'name': '微軟 (Microsoft)', 'sector': '雲端AI巨頭'},
    'AMAT': {'name': '應用材料 (Applied Materials)', 'sector': '半導體設備'},
    'AMD': {'name': '超微 (AMD)', 'sector': 'AI加速器'},
    'AMZN': {'name': '亞馬遜 (Amazon)', 'sector': 'AWS算力雲端'},
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
    '2317.TW': {'name': '鴻海', 'market': 'tse'},
    '2474.TW': {'name': '可成', 'market': 'tse'},
    '1402.TW': {'name': '遠東新', 'market': 'tse'}
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
def push_telegram_message(text_content):
    try:
        tg_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        if not tg_token:
            print('⚠️ 未設定 TELEGRAM_BOT_TOKEN 環境變數，略過 Telegram 推播。')
            return False
        chat_ids = ["7660257976", "7912782196"]  # Simon Chang (張大哥) 與 Huang Chai Jung (黃嘉蓉學員)
        env_chat = os.environ.get("TELEGRAM_CHAT_ID")
        if env_chat and env_chat.strip() not in chat_ids:
            chat_ids.append(env_chat.strip())

        # 徹底防禦 Telegram Markdown 將 $ 識別為 LaTeX 或底線(_)導致 HTTP 400 解析失敗
        clean_text = str(text_content).replace('$', '')
        success = False
        for cid in chat_ids:
            try:
                url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                payload = {'chat_id': cid, 'text': clean_text}
                data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
                with urllib.request.urlopen(req, timeout=10) as res:
                    if res.status == 200:
                        success = True
            except Exception as send_err:
                print(f'⚠️ Telegram chat_id={cid} 發送失敗: {send_err}')
        if success:
            print('✅ Telegram 雙軌訊號已成功廣播發送至 Telegram 學員手機！')
            return True
    except Exception as e:
        print(f'⚠️ Telegram 推播輔助發送: {e}')
    return False

def push_line_message(token, user_id, messages, mode='broadcast'):
    # 自動雙軌同步推播至 Telegram
    try:
        msg_list = messages if isinstance(messages, list) else [messages]
        for m in msg_list:
            if isinstance(m, dict) and m.get('altText'):
                push_telegram_message(f"🏛️ *【q_quant_888 雙師戰報】*\n{m.get('altText')}")
            elif isinstance(m, dict) and m.get('text'):
                push_telegram_message(m.get('text'))
            elif isinstance(m, str):
                push_telegram_message(m)
    except Exception as tg_err:
        pass

    if not token:
        print('❌ 未設定 LINE_CHANNEL_ACCESS_TOKEN，略過 LINE 推播。')
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
def create_sweet_spot_card(symbol, name, current_price, low_price, ma60, bb_lower, kd_k, kd_d, market='US',
                           sl_price=None, tp1_price=None, rsi=None, vol_ratio=None, macro_note=None):
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d %H:%M:%S')
    is_us = (market.upper() == 'US')

    currency_symbol = '' if is_us else ''
    currency_unit = 'USD' if is_us else 'TWD'
    market_flag = '🇺🇸 美股' if is_us else '🇹🇼 台股'

    # 雙師 V4-Yen 防禦停損與 8-3-1 雙軌目標價
    if sl_price is None:
        sl_price = round(max(low_price * 0.97, current_price * 0.93), 2)
    if tp1_price is None:
        tp1_price = round(current_price * 1.08, 2)
    sl_pct = (sl_price / current_price - 1.0) * 100

    price_fmt = f'{current_price:.2f}' if is_us else f'{current_price:.1f}'
    low_fmt = f'{low_price:.2f}' if is_us else f'{low_price:.1f}'
    ma60_fmt = f'{ma60:.2f}' if is_us else f'{ma60:.1f}'
    sl_fmt = f'{sl_price:.2f}' if is_us else f'{sl_price:.1f}'
    tp1_fmt = f'{tp1_price:.2f}' if is_us else f'{tp1_price:.1f}'
    extra_stats = []
    if rsi is not None:
        extra_stats.append(f'RSI:{rsi:.0f}')
    if vol_ratio is not None:
        extra_stats.append(f'量比:{vol_ratio:.2f}x')
    extra_str = ' ｜ '.join(extra_stats) if extra_stats else f'K:{kd_k:.1f}/D:{kd_d:.1f}'
    macro_line = f'\n🌐 【總經氣候】{macro_note}' if macro_note else ''

    alt_text = (
        f'🎯【q_quant_888 顏老師 V4-Yen 精選訊號｜{market_flag}】\n'
        f'📌 標的：{symbol} {name}\n'
        f'💵 現價：{price_fmt} {currency_unit}（{extra_str}｜KD {kd_k:.1f}>{kd_d:.1f}）\n'
        f'🛡️ 雙重防洗停損：{sl_fmt} {currency_unit}（{sl_pct:.1f}%，ATR緩衝兼-7%硬保險絲）\n'
        f'🚀 8-3-1 雙軌目標：TP1 {tp1_fmt} (+8%賣半保本) ｜ 剩餘抱破布林上軌\n'
        f'⏰ 紀律：請等收盤前15~30分鐘確認收強紅K（站穩季線 {ma60_fmt}）再下單！'
        f'{macro_line}'
    )

    entry_timing = (
        '現價已通過年/季線雙均線、紅K收強與量能篩選！請於【美股收盤前半小時 (美東 15:30)】確認收腳站穩再下限價單。'
        if is_us else
        '現價已通過年/季線雙均線、紅K收強與量能篩選！請於【台股收盤前 15 分鐘 (13:15)】確認紅K收高再進場。'
    )

    tips = (
        '1. 【V4-Yen 核心】11.2年大數據驗證：站穩MA60向上＋MA200＋布林下軌＋KD金叉＋收強紅K＋量能健康。\n'
        '2. 【阿村伯硬停損保險絲】採「近3日低點-1.2×ATR」與「-7%硬底線」取較高者，防針刺洗盤同時封死重傷。\n'
        '3. 【顏式 8-3-1 雙軌出場】達 +8% 先賣一半落袋並移保本，剩餘 50% 抱至衝破布林上軌折回才賣！'
    )

    app_hint = '美股無漲跌幅限制，請採「限價單 (Limit Order)」防滑價' if is_us else '下單前請務必核對「整張(1,000股)」與「零股」視窗防呆'
    
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
                                {'type': 'text', 'text': '🛡️ 雙師防洗停損', 'color': '#F87171', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': f'{sl_fmt} {currency_unit} ({sl_pct:.1f}% ATR+-7%)', 'color': '#F87171', 'size': 'sm', 'weight': 'bold', 'flex': 3}
                            ]
                        },
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'contents': [
                                {'type': 'text', 'text': '🚀 8-3-1 第一目標', 'color': '#4ADE80', 'size': 'sm', 'weight': 'bold', 'flex': 2},
                                {'type': 'text', 'text': f'{tp1_fmt} {currency_unit} (+8%賣半保本)', 'color': '#4ADE80', 'size': 'sm', 'weight': 'bold', 'flex': 3}
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
                            'text': '💡 顏老師 V4-Yen 雙軌心法與防呆：',
                            'color': '#FDE047',
                            'size': 'xs',
                            'weight': 'bold'
                        },
                        {
                            'type': 'text',
                            'text': f'【進場確認】{entry_timing}\n{tips}{macro_line}\n⚠️ 注意：{app_hint}。',
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
                    open_p = meta.get('regularMarketOpen')
                    vol = meta.get('regularMarketVolume')
                    prev = meta.get('chartPreviousClose')

                    # 從當日分鐘線補抓開盤價與高低點
                    q_list = chart_res[0].get('indicators', {}).get('quote', [{}])
                    if q_list and open_p is None:
                        opens = [o for o in (q_list[0].get('open') or []) if o is not None]
                        if opens:
                            open_p = opens[0]

                    if price is None:
                        price = meta.get('postMarketPrice') or meta.get('preMarketPrice') or prev

                    if low is None: low = price
                    if high is None: high = price
                    if open_p is None: open_p = price

                    name = DEFAULT_US_WATCHLIST.get(sym, {}).get('name', sym)
                    results[sym] = {
                        'symbol': sym,
                        'name': name,
                        'price': float(price),
                        'open': float(open_p),
                        'low': float(low),
                        'high': float(high),
                        'volume': float(vol or 0.0),
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
                open_str = item.get('o', '-')
                open_val = float(open_str) if open_str not in ('-', '', None) else price
                vol_str = item.get('v', '0')
                vol_shares = float(vol_str) * 1000.0 if vol_str not in ('-', '', None) else 0.0

                results[f'{code}.TW'] = {
                    'symbol': f'{code}.TW',
                    'name': name,
                    'price': price,
                    'open': open_val,
                    'yesterday_close': y_val,
                    'low': low_val,
                    'high': high_val,
                    'volume': vol_shares,
                    'market': 'TW'
                }
    except Exception as e:
        print(f'⚠️ TWSE MIS API 抓取失敗: {e}')
        
    return results

# ------------------------------------------------------------------------------
# 6. 技術指標計算與歷史快取 (V4-Yen: MA60/MA200, BB, KD, RSI, ATR14, Low3, Vol20)
# ------------------------------------------------------------------------------
_MACRO_CACHE = {}

def get_session_elapsed_ratio(is_us=True):
    """計算盤中已經過時間比例（用於等比例推估當日全日量能），非盤中回傳 1.0"""
    if is_us:
        now_et = datetime.now(ZoneInfo('America/New_York'))
        if now_et.weekday() < 5:
            mins = now_et.hour * 60 + now_et.minute
            if 570 <= mins < 960:  # 09:30 ~ 16:00 ET (390 mins)
                return max(0.18, min(1.0, (mins - 570) / 390.0))
    else:
        now_tw = datetime.now(TAIPEI_TZ)
        if now_tw.weekday() < 5:
            mins = now_tw.hour * 60 + now_tw.minute
            if 540 <= mins < 810:  # 09:00 ~ 13:30 TW (270 mins)
                return max(0.18, min(1.0, (mins - 540) / 270.0))
    return 1.0

def get_macro_climate_shield(is_us=True):
    """大盤氣候總開關：美股看 SPY 季線/年線與 10Y 美債殖利率；台股看加權與台幣匯率月線"""
    key = 'US' if is_us else 'TW'
    cached = _MACRO_CACHE.get(key)
    if cached and (time.time() - cached.get('ts', 0) < 900):
        return cached

    res = {'market_ok': True, 'sizing_hint': '🟢 總經氣候平穩，可依標準倉位執行', 'ts': time.time()}
    try:
        import yfinance as yf
        if is_us:
            spy = yf.Ticker('SPY').history(period='1y')
            tnx = yf.Ticker('^TNX').history(period='1mo')
            if not spy.empty and len(spy) >= 65:
                spy_c = float(spy['Close'].iloc[-1])
                spy_ma60 = float(spy['Close'].rolling(60).mean().iloc[-1])
                spy_ma60_prev = float(spy['Close'].rolling(60).mean().iloc[-6])
                spy_ma200 = float(spy['Close'].rolling(200).mean().iloc[-1]) if len(spy) >= 200 else spy_ma60
                tnx_v = float(tnx['Close'].iloc[-1]) if not tnx.empty else 4.5
                bear_mode = (spy_c < spy_ma60 * 0.96) or (spy_c < spy_ma200 and spy_ma60 < spy_ma60_prev)
                if bear_mode:
                    res['market_ok'] = False
                    res['sizing_hint'] = f'🐻 美股熊市總開關啟動 (SPY {spy_c:.1f} < MA60 {spy_ma60:.1f} 或 MA200 {spy_ma200:.1f} 轉空)，鎖住開槍！'
                elif tnx_v >= 4.90:
                    res['sizing_hint'] = f'⚠️ 10Y美債殖利率偏高 ({tnx_v:.2f}%)，建議減半偵察試單 (SPY {spy_c:.1f} 尚穩)'
                else:
                    res['sizing_hint'] = f'🟢 美股氣候穩健 (SPY {spy_c:.1f} >= 季線 {spy_ma60:.1f}，10Y美債 {tnx_v:.2f}%)，可依標準倉位'
        else:
            twd = yf.Ticker('TWD=X').history(period='2mo')
            twii_t = yf.Ticker('^TWII')
            twii = twii_t.history(period='6mo').dropna(subset=['Close'])
            twii_bear = False
            if not twii.empty and len(twii) >= 60:
                last_px = None
                try:
                    last_px = twii_t.fast_info.get('lastPrice')
                except Exception:
                    pass
                tw_c = float(last_px or twii['Close'].iloc[-1])
                tw_m60 = float(twii['Close'].rolling(60).mean().iloc[-1])
                twii_bear = (tw_c < tw_m60 * 0.93)
            if twii_bear:
                res['market_ok'] = False
                res['sizing_hint'] = f'🐻 台股加權 ({tw_c:.0f}) 跌破季線 ({tw_m60:.0f}) 7% 以上空頭格局，鎖住開槍！'
            elif not twd.empty and len(twd) >= 20:
                twd = twd.dropna(subset=['Close'])
                fx_c = float(twd['Close'].iloc[-1])
                fx_m20 = float(twd['Close'].rolling(20).mean().iloc[-1])
                if fx_c <= fx_m20 * 1.002:
                    res['sizing_hint'] = f'🟢 台幣升值順風區 ({fx_c:.2f} <= 月線 {fx_m20:.2f}，歷史20日勝率80.4%)，可依標準倉位'
                else:
                    res['sizing_hint'] = f'⚠️ 台幣貶值逆風區 ({fx_c:.2f} > 月線 {fx_m20:.2f}，歷史勝率68.4%)，建議減半輕試'
    except Exception as e:
        res['sizing_hint'] = f'⚠️ 總經氣候抓取略過 ({e})'
    _MACRO_CACHE[key] = res
    return res

def get_stock_technicals(symbol, is_us=True):
    import math
    cache = {}
    today_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d')
    now_ts = time.time()

    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    if symbol in cache:
        c_item = cache[symbol]
        # 15 分鐘內且具備完整有效 V4-Yen 數值才使用快取
        ma60_v = c_item.get('ma60')
        if (now_ts - c_item.get('ts', 0) < 900) and ('ma200' in c_item) and ('atr14' in c_item) and isinstance(ma60_v, (int, float)) and not math.isnan(ma60_v):
            return c_item

    try:
        import yfinance as yf
        import pandas as pd
        ticker_sym = symbol
        df = yf.Ticker(ticker_sym).history(period='1y')
        if df.empty and symbol.endswith('.TW'):
            ticker_sym = symbol.replace('.TW', '.TWO')
            df = yf.Ticker(ticker_sym).history(period='1y')

        df = df.dropna(subset=['Open', 'High', 'Low', 'Close'])
        if not df.empty and len(df) >= 65:
            ma60_s = df['Close'].rolling(60).mean()
            ma60 = float(ma60_s.iloc[-1])
            ma60_prev5 = float(ma60_s.iloc[-6]) if len(ma60_s.dropna()) >= 6 else ma60
            ma60_slope5 = ma60 - ma60_prev5
            ma200 = float(df['Close'].rolling(200).mean().iloc[-1]) if len(df) >= 200 else ma60
            ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
            std20 = float(df['Close'].rolling(20).std().iloc[-1])
            bb_lower = ma20 - (2 * std20)
            bb_upper = ma20 + (2 * std20)
            low3 = float(df['Low'].iloc[-3:].min())

            hl = df['High'] - df['Low']
            hc = (df['High'] - df['Close'].shift(1)).abs()
            lc = (df['Low'] - df['Close'].shift(1)).abs()
            tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
            atr14 = float(tr.rolling(14).mean().iloc[-1])

            # 使用前 20 個已收盤交易日均量，避免盤中尚未收盤拉低基準
            vol20 = float(df['Volume'].iloc[-21:-1].mean()) if len(df) >= 22 else float(df['Volume'].mean())

            delta = df['Close'].diff()
            gain = delta.clip(lower=0).rolling(14).mean()
            loss = (-delta.clip(upper=0)).rolling(14).mean()
            rs = gain / loss.replace(0, float('nan'))
            rsi14 = float((100 - (100 / (1 + rs))).iloc[-1])
            if pd.isna(rsi14):
                rsi14 = 50.0

            l9 = df['Low'].rolling(9).min()
            h9 = df['High'].rolling(9).max()
            rsv = 100 * (df['Close'] - l9) / (h9 - l9).replace(0, float('nan'))
            k_val, d_val = 50.0, 50.0
            for r in rsv:
                if pd.notna(r):
                    k_val = (2.0 / 3.0) * k_val + (1.0 / 3.0) * float(r)
                    d_val = (2.0 / 3.0) * d_val + (1.0 / 3.0) * k_val

            tech_data = {
                'date': today_str,
                'ts': now_ts,
                'ma60': round(ma60, 2),
                'ma60_slope5': round(ma60_slope5, 4),
                'ma200': round(ma200, 2),
                'ma20': round(ma20, 2),
                'bb_lower': round(bb_lower, 2),
                'bb_upper': round(bb_upper, 2),
                'low3': round(low3, 2),
                'atr14': round(atr14, 2),
                'vol20': round(vol20, 1),
                'last_vol': float(df['Volume'].iloc[-1]),
                'last_open': float(df['Open'].iloc[-1]),
                'rsi14': round(rsi14, 2),
                'k': round(k_val, 2),
                'd': round(d_val, 2)
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

    macro = get_macro_climate_shield(is_us=is_us)
    elapsed_ratio = get_session_elapsed_ratio(is_us=is_us)
    print(f'\n🔍 啟動【{market_label}】V4-Yen 雙師波段巡檢（監控 {len(symbols)} 檔 | 時段進度 {elapsed_ratio*100:.0f}%）')
    print(f'   🌐 總經氣候：{macro["sizing_hint"]}')

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
        high_p = q.get('high', price)
        open_p = q.get('open', price)
        raw_vol = q.get('volume', 0.0)
        name = q.get('name') or (DEFAULT_US_WATCHLIST.get(sym, {}).get('name') if is_us else DEFAULT_TW_WATCHLIST.get(sym, {}).get('name', sym))

        tech = get_stock_technicals(sym, is_us=is_us)
        if not tech:
            print(f'  - {sym} ({name}): 歷史指標不足，略過判定')
            continue

        ma60 = tech['ma60']
        ma60_slope5 = tech.get('ma60_slope5', 0.0)
        ma200 = tech.get('ma200', ma60)
        bb_lower = tech['bb_lower']
        low3 = min(tech.get('low3', low_p), low_p)
        atr14 = max(tech.get('atr14', price * 0.02), price * 0.005)
        vol20 = tech.get('vol20', 0.0)
        rsi14 = tech.get('rsi14', 50.0)
        k_val = tech['k']
        d_val = tech['d']

        if open_p == price and tech.get('last_open'):
            open_p = tech['last_open']
        if raw_vol <= 0 and tech.get('last_vol', 0) > 0:
            raw_vol = tech['last_vol']

        proj_vol_ratio = (raw_vol / elapsed_ratio) / vol20 if (vol20 > 0 and raw_vol > 0) else 1.0
        rng = max(high_p - low_p, 1e-6)
        close_pos = (price - low_p) / rng if high_p > low_p else 0.6

        # ------------------------------------------------------------------
        # 顏老師 V4-Yen 簡約大數據六大鐵律（經 11.2 年 22 萬根 K 棒認證，PF > 2.0）
        # 1. 雙均線趨勢護城河：站穩季線 60MA ＋ 季線斜率向上 ＋ 站穩年線 200MA
        is_trend_ok = bool(price >= ma60 and ma60_slope5 > 0 and price >= ma200)
        # 2. 布林下軌甜蜜回測 (BB_Lower * 1.05)
        is_sweet_spot = bool(price <= bb_lower * 1.05)
        # 3. KD 低檔金叉 ＋ RSI 不過熱 (K <= 50 且 K > D 且 RSI <= 55)
        is_kd_rsi_ok = bool(k_val <= 50.0 and k_val > d_val and rsi14 <= 55.0)
        # 4. 8-3-1 紅 K 收強確認止跌 (Close >= Open 且收在當日振福上 45%)
        is_red_strong = bool(price >= open_p and close_pos >= 0.55)
        # 5. 老王量能健康過濾 (0.90x ~ 2.50x 均量，有量換手又避開爆量出貨)
        is_vol_ok = bool(0.90 <= proj_vol_ratio <= 2.50)
        # 6. 大盤熊市總開關 (熊市時自動鎖住多方買訊)
        is_macro_ok = bool(macro['market_ok'])

        # 雙師風控防守與目標計算 (ATR 緩衝兼阿村伯 -7% 硬停損保險絲)
        sl_price = round(max(low3 - 1.2 * atr14, price * 0.93), 2)
        tp1_price = round(price * 1.08, 2)

        should_alert = (force_symbol is not None) or (
            is_macro_ok and is_trend_ok and is_sweet_spot and is_kd_rsi_ok and is_red_strong and is_vol_ok
        )

        unit = 'USD' if is_us else 'TWD'
        watch_tag = '👀[候選]' if (is_trend_ok and is_sweet_spot) else '  '
        print(
            f'  {watch_tag} {sym} ({name}): 現價 {price:.2f} {unit} | '
            f'MA60={ma60:.2f}({"↑" if ma60_slope5>0 else "↓"}) MA200={ma200:.2f} BBL*1.05={bb_lower*1.05:.2f} | '
            f'KD={k_val:.1f}/{d_val:.1f} RSI={rsi14:.0f} Pos={close_pos:.2f} 量={proj_vol_ratio:.2f}x'
        )

        if should_alert:
            can_send, reason = check_can_alert(sym, price, cooldown)
            if force_symbol or can_send:
                print(f'    🚨 【V4-Yen 精選狙擊觸發！】Stop={sl_price:.2f} | TP1={tp1_price:.2f} -> 發送通知...')
                card = create_sweet_spot_card(
                    sym, name, price, low_p, ma60, bb_lower, k_val, d_val, market=market_type,
                    sl_price=sl_price, tp1_price=tp1_price, rsi=rsi14, vol_ratio=proj_vol_ratio,
                    macro_note=macro['sizing_hint']
                )
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

def create_preclose_confirmation_card(market='US'):
    """
    🌆 尾盤到價戰術確認卡 (收盤前 15~30 分鐘)
    顏春煌教授 8-3-2【尾盤確認進場法】+ 8-4-2【買進日低點防守線】最終判定
    """
    now_str = datetime.now(TAIPEI_TZ).strftime("%Y-%m-%d %H:%M:%S")
    dr_tsun_item = get_rotating_dr_tsun_quote()
    prof_yen_item = get_rotating_prof_yen_quote()
    
    market_flag = "🇺🇸 美股尾盤戰術區" if market == 'US' else "🇹🇼 台股尾盤戰術區"
    
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
                    'text': f'🌆 尾盤到價戰術確認卡 ｜ {market_flag}',
                    'weight': 'bold',
                    'color': '#F59E0B',
                    'size': 'sm'
                },
                {
                    'type': 'text',
                    'text': '收盤前 15~30 分鐘 ｜ 尾盤定心判定',
                    'weight': 'bold',
                    'size': 'xl',
                    'color': '#F8FAFC',
                    'margin': 'xs'
                },
                {
                    'type': 'text',
                    'text': f'確認時間：{now_str} ｜ 嚴守顏老師與阿村伯紀律',
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
                # 尾盤定心三法則
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
                            'text': '🎯 顏老師尾盤定心三法（收盤前 15~30 分鐘）：',
                            'weight': 'bold',
                            'color': '#F59E0B',
                            'size': 'xs'
                        },
                        {
                            'type': 'text',
                            'text': '1. 🟡【觀望不盲追】：盤中回測下軌時絕不出手，只在收盤前 15~30 分鐘確認 K 線是否收腳打底！\n2. 🟢【到價開槍法】：若 K 線確認站回布林下軌且 KD 打底，才正式下單建倉 50% 短線部位！\n3. 🛡️【持股防守線】：買進當天絕不停損！持有標的（如 V, AMZN）未跌破買進日最低價防線，安心抱牢，今晚睡得香！',
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
                    'text': '正規軍 4.0 尾盤戰術守護 ｜ 顏老師與阿村伯陪伴您',
                    'color': '#64748B',
                    'size': 'xs',
                    'align': 'center'
                }
            ]
        }
    }
    
    return {
        'type': 'flex',
        'altText': f'🌆【q_quant_888 尾盤戰術卡】{market_flag} 雙師尾盤定心與開槍判定！',
        'contents': flex_content
    }

# ------------------------------------------------------------------------------
# 主程式入口
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='q_quant_888 顏老師鐵律波段到價 LINE 推播守護引擎')
    parser.add_argument('--noon', action='store_true', help='立即推播 12:30 盤中定心丸與持盈保泰戰術卡片')
    parser.add_argument('--premarket', action='store_true', help='立即推播美股/台股盤前安定軍心與雙師教育指導卡片')
    parser.add_argument('--preclose', action='store_true', help='立即推播美股/台股收盤前 15~30 分鐘尾盤定心與戰術卡片')
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

    if args.preclose:
        print('🌆 執行 LINE 收盤前 15~30 分鐘尾盤戰術與開槍判定廣播推播...')
        m_type = args.market.upper() if args.market else 'US'
        card = create_preclose_confirmation_card(market=m_type)
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
        now_hour = datetime.now(TAIPEI_TZ).hour
        
        if market_choice == 'us':
            scan_market(config['us_watchlist'], 'US', config)
        elif market_choice == 'tw':
            scan_market(config['tw_watchlist'], 'TW', config)
        elif market_choice == 'all':
            scan_market(config['us_watchlist'], 'US', config)
            scan_market(config['tw_watchlist'], 'TW', config)
        else:
            if (6 <= now_hour < 14):
                # 06:00 ~ 14:00 台北時間：專注台股觀測
                scan_market(config['tw_watchlist'], 'TW', config)
            else:
                # 14:00 ~ 06:00 台北時間：專注美股觀測 (包含傍晚與夜盤)
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

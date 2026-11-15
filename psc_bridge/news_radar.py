# -*- coding: utf-8 -*-
r"""
全自動財經新聞與事件雷達 (cnyes 鉅亨網頭條 / 台股 / 美股)
將即時快訊寫入 D:\PSC_Quant_DB\news_feed.db 並輸出 q_quant_888/news_radar.json，
自動比對全站 260 檔標的與利多/利空情緒標籤，供 psc_qquant_bridge.py 與網頁前端連動。
"""
import json
import os
import shutil
import sqlite3
import ssl
import sys
import urllib.request
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = r'C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io'
SCAN_FILE = os.path.join(BASE_DIR, 'scan_results.json')
WEB_DIR = os.path.join(BASE_DIR, 'q_quant_888')
DB_DIR = r'D:\PSC_Quant_DB'
NEWS_DB = os.path.join(DB_DIR, 'news_feed.db')
NEWS_JSON = os.path.join(BASE_DIR, 'news_radar.json')

BULL_KW = (
    '買超', '增持', '加碼', '創新高', '突破', '上調', '受惠', '成長', '擴產',
    '搶市', '大漲', '飆', '看多', '力挺', '回溫', '訂單', '營收創', '優於預期',
    '降息', '護盤', '反彈', '復職',
)
BEAR_KW = (
    '調查', '停飛', '故障', '空單', '賣超', '下修', '重挫', '跌破', '虧損',
    '制裁', '戰爭', '緊縮', '恐慌', '警示', '停擺', '取消', '裁員', '升息',
    '違約', '暴跌', '請辭', '危機',
)

ALIAS_MAP = {
    '輝達': 'NVDA', '英偉達': 'NVDA', '黃仁勳': 'NVDA',
    '台積電': '2330.TW', '鴻海': '2317.TW', '聯發科': '2454.TW',
    '廣達': '2382.TW', '緯創': '3231.TW', '華碩': '2357.TW',
    '技嘉': '2376.TW', '微星': '2377.TW', '日月光': '3711.TW',
    '谷歌': 'GOOGL', '蘋果': 'AAPL', '微軟': 'MSFT',
    '博通': 'AVGO', '超微': 'AMD', '美光': 'MU',
    '特斯拉': 'TSLA', '亞馬遜': 'AMZN', '高通': 'QCOM',
}


def _load_symbol_matchers():
    """從 scan_results.json 建立標的關鍵字對照表"""
    matchers = dict(ALIAS_MAP)
    if not os.path.exists(SCAN_FILE):
        return matchers
    try:
        with open(SCAN_FILE, 'r', encoding='utf-8') as f:
            stocks = json.load(f).get('stocks', [])
        for s in stocks:
            sym = str(s.get('symbol', '')).strip()
            name = str(s.get('name', '')).strip()
            if not sym:
                continue
            code = sym.split('.')[0]
            if len(code) >= 2 and not code.isdigit():
                matchers[code] = sym
            elif code.isdigit():
                matchers[code] = sym
            clean_name = name.split('(')[0].split(' ')[0].strip()
            if len(clean_name) >= 2:
                matchers[clean_name] = sym
    except Exception:
        pass
    return matchers


def _classify_sentiment(text):
    b_hits = sum(1 for kw in BULL_KW if kw in text)
    s_hits = sum(1 for kw in BEAR_KW if kw in text)
    if b_hits > s_hits:
        return 'bullish'
    if s_hits > b_hits:
        return 'bearish'
    return 'neutral'


def _match_symbols(text, matchers):
    found = []
    for kw, sym in matchers.items():
        if kw in text and sym not in found:
            found.append(sym)
    return found[:5]


def fetch_cnyes_category(cat, limit=25):
    url = f'https://api.cnyes.com/media/api/v1/newslist/category/{cat}?limit={limit}'
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=12) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    return data.get('items', {}).get('data', [])


def update_news_radar(max_age_minutes=15, force=False):
    """抓最新鉅亨網新聞入庫並產生 news_radar.json；若距離上次更新未滿 max_age_minutes 則跳過網路請求"""
    if not force and os.path.exists(NEWS_JSON):
        age_sec = datetime.now().timestamp() - os.path.getmtime(NEWS_JSON)
        if age_sec < max_age_minutes * 60:
            try:
                with open(NEWS_JSON, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(NEWS_DB, timeout=10)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news_items (
            news_id TEXT PRIMARY KEY,
            category TEXT,
            title TEXT,
            summary TEXT,
            published_at TEXT,
            sentiment TEXT,
            matched_symbols TEXT,
            url TEXT,
            fetched_at TEXT
        )
    """)

    matchers = _load_symbol_matchers()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rows_to_insert = []
    seen_ids = set()

    for cat in ('headline', 'tw_stock', 'us_stock'):
        try:
            items = fetch_cnyes_category(cat, limit=25)
        except Exception as e:
            print(f"[News] 抓取 {cat} 失敗: {e}")
            continue

        for it in items:
            nid = str(it.get('newsId', '')).strip()
            if not nid or nid in seen_ids:
                continue
            seen_ids.add(nid)
            title = str(it.get('title', '')).strip()
            summary = str(it.get('summary', '')).strip()
            pub_ts = it.get('publishAt', 0)
            pub_str = datetime.fromtimestamp(pub_ts).strftime('%Y-%m-%d %H:%M:%S') if pub_ts else now_str
            full_text = f"{title} {summary}"
            sentiment = _classify_sentiment(full_text)
            matched = _match_symbols(full_text, matchers)
            url = f"https://news.cnyes.com/news/id/{nid}"
            rows_to_insert.append((
                nid, cat, title, summary, pub_str, sentiment,
                ','.join(matched), url, now_str
            ))

    if rows_to_insert:
        cur.executemany(
            "INSERT OR REPLACE INTO news_items VALUES (?,?,?,?,?,?,?,?,?)",
            rows_to_insert
        )
        conn.commit()

    cur.execute("""
        SELECT news_id, category, title, published_at, sentiment, matched_symbols, url
        FROM news_items
        ORDER BY published_at DESC
        LIMIT 40
    """)
    recent = []
    bull_cnt = bear_cnt = neu_cnt = 0
    for nid, cat, title, pub_str, sent, syms, url in cur.fetchall():
        if sent == 'bullish':
            bull_cnt += 1
        elif sent == 'bearish':
            bear_cnt += 1
        else:
            neu_cnt += 1
        recent.append({
            'id': nid,
            'category': cat,
            'title': title,
            'published_at': pub_str,
            'sentiment': sent,
            'symbols': [x for x in syms.split(',') if x],
            'url': url,
        })
    total_db = cur.execute("SELECT COUNT(*) FROM news_items").fetchone()[0]
    conn.close()

    payload = {
        'updated_at': now_str,
        'source': 'cnyes_api',
        'db_total': total_db,
        'summary': {
            'bullish': bull_cnt,
            'bearish': bear_cnt,
            'neutral': neu_cnt,
        },
        'items': recent,
    }
    with open(NEWS_JSON, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    if os.path.exists(WEB_DIR):
        shutil.copy2(NEWS_JSON, os.path.join(WEB_DIR, 'news_radar.json'))
    return payload


def get_news_digest_lines(limit=5, force=False):
    payload = update_news_radar(max_age_minutes=15, force=force)
    items = payload.get('items', [])
    # 優先顯示有匹配到 260 檔標的或帶明確多空情緒的新聞
    prioritized = sorted(
        items,
        key=lambda x: (1 if x.get('symbols') else 0, 1 if x.get('sentiment') != 'neutral' else 0, x.get('published_at', '')),
        reverse=True,
    )[:limit]
    lines = ["\n📰 【三、即時財經新聞與事件雷達（鉅亨網）】"]
    for it in prioritized:
        icon = '🟢' if it['sentiment'] == 'bullish' else ('🔴' if it['sentiment'] == 'bearish' else '⚪')
        tag = f" [{','.join(it['symbols'])}]" if it.get('symbols') else ""
        hhmm = it.get('published_at', '')[11:16]
        lines.append(f"• {icon} {hhmm}{tag} {it['title']}")
    return lines


if __name__ == '__main__':
    force_flag = '--force' in sys.argv
    res = update_news_radar(force=force_flag)
    print(f"新聞雷達更新完成: 共收錄 {res['db_total']} 則，最新 40 則情緒分布 {res['summary']}")
    for line in get_news_digest_lines(limit=6, force=False):
        print(line)

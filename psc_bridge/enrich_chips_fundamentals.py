# -*- coding: utf-8 -*-
r"""
全站 260 檔「真實三大法人籌碼 ＋ 真實三率/月營收/本益比 ＋ Gen 18 Ultimate 回測與訊號」整合引擎
資料來源：
1. 證交所 TWSE T86 (三大法人買賣超) & 櫃買中心 TPEx 三大法人買賣超
2. 證交所 OpenAPI MI_MARGN (真實融資融券餘額與增減)
3. 證交所 OpenAPI t187ap17_L (真實毛利率、營業利益率、稅後純益率)
4. 證交所 OpenAPI t187ap05_L & 櫃買 mopsfin_t187ap05_O (真實月營收 YoY / MoM)
5. 證交所 OpenAPI BWIBBU_ALL & 櫃買 peratio_analysis (真實本益比 PE、殖利率 Yield、股價淨值比 PB)
6. D:\PSC_Quant_DB\market_history.db (Gen 18 Ultimate 雙師×華爾街波段回測)
"""
import json
import os
import shutil
import sqlite3
import ssl
import sys
import urllib.request
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = r'C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io'
SCAN_FILE = os.path.join(BASE_DIR, 'scan_results.json')
WEB_DIR = os.path.join(BASE_DIR, 'q_quant_888')
DB_DIR = r'D:\PSC_Quant_DB'
HIST_DB = os.path.join(DB_DIR, 'market_history.db')
COST = 0.003


def _http_json(url, timeout=15):
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _to_float(val, default=None):
    if val is None:
        return default
    s = str(val).replace(',', '').replace('%', '').strip()
    if not s or s in ('-', '--', 'N/A', 'null'):
        return default
    try:
        return float(s)
    except Exception:
        return default


def _to_int(val, default=0):
    f = _to_float(val, None)
    return int(round(f)) if f is not None else default


def fetch_tw_chips():
    """抓取最新一個交易日的上市 (TWSE T86 + MI_MARGN) 與上櫃 (TPEx) 真實法人與融資券籌碼"""
    chips_map = {}
    trade_date_str = ''

    # 往回找最近 5 天內有開盤的日期
    for delta in range(0, 6):
        dt = datetime.now() - timedelta(days=delta)
        if dt.weekday() >= 5:
            continue
        ymd = dt.strftime('%Y%m%d')
        try:
            url = f'https://www.twse.com.tw/rwd/zh/fund/T86?date={ymd}&selectType=ALLBUT0999&response=json'
            data = _http_json(url)
            if data.get('stat') == 'OK' and data.get('data'):
                trade_date_str = dt.strftime('%Y-%m-%d')
                for r in data['data']:
                    code = str(r[0]).strip()
                    f_net = _to_int(r[4]) + _to_int(r[7])  # 外資及陸資 + 外資自營商 (股)
                    t_net = _to_int(r[10])                 # 投信買賣超 (股)
                    d_net = _to_int(r[11])                 # 自營商合計 (股)
                    tot_net = _to_int(r[18])               # 三大法人合計 (股)
                    chips_map[code] = {
                        'date': trade_date_str,
                        'foreign_net_shares': f_net,
                        'trust_net_shares': t_net,
                        'dealer_net_shares': d_net,
                        'total_inst_shares': tot_net,
                        'foreign_lots': round(f_net / 1000.0, 1),
                        'trust_lots': round(t_net / 1000.0, 1),
                        'total_inst_lots': round(tot_net / 1000.0, 1),
                    }
                # 同步抓同日上櫃 TPEx 三大法人
                roc_y = dt.year - 1911
                roc_date = f"{roc_y}/{dt.strftime('%m/%d')}"
                tpex_url = f'https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php?l=zh-tw&se=EW&t=D&d={roc_date}&o=json'
                try:
                    tdata = _http_json(tpex_url)
                    tables = tdata.get('tables', [])
                    trows = tables[0].get('data', []) if tables else tdata.get('aaData', [])
                    for r in trows:
                        code = str(r[0]).strip()
                        f_net = _to_int(r[10])
                        t_net = _to_int(r[13])
                        d_net = _to_int(r[22])
                        tot_net = _to_int(r[23])
                        chips_map[code] = {
                            'date': trade_date_str,
                            'foreign_net_shares': f_net,
                            'trust_net_shares': t_net,
                            'dealer_net_shares': d_net,
                            'total_inst_shares': tot_net,
                            'foreign_lots': round(f_net / 1000.0, 1),
                            'trust_lots': round(t_net / 1000.0, 1),
                            'total_inst_lots': round(tot_net / 1000.0, 1),
                        }
                except Exception as te:
                    print(f"[TPEx 3insti] 略過: {te}")
                break
        except Exception:
            continue

    # 抓上市真實融資融券 MI_MARGN
    try:
        mdata = _http_json('https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN')
        for r in mdata:
            code = str(r.get('股票代號', '')).strip()
            if not code:
                continue
            m_prev = _to_int(r.get('融資前日餘額'))
            m_curr = _to_int(r.get('融資今日餘額'))
            s_prev = _to_int(r.get('融券前日餘額'))
            s_curr = _to_int(r.get('融券今日餘額'))
            entry = chips_map.setdefault(code, {
                'date': trade_date_str or datetime.now().strftime('%Y-%m-%d'),
                'foreign_net_shares': 0, 'trust_net_shares': 0,
                'dealer_net_shares': 0, 'total_inst_shares': 0,
                'foreign_lots': 0.0, 'trust_lots': 0.0, 'total_inst_lots': 0.0,
            })
            entry['margin_diff'] = m_curr - m_prev
            entry['margin_bal'] = m_curr
            entry['short_diff'] = s_curr - s_prev
            entry['short_bal'] = s_curr
    except Exception as me:
        print(f"[TWSE MI_MARGN] 略過: {me}")

    # 4. 集保中心 (TDCC) 最新千張大戶與400張大戶持股比例 (getOD.ashx?id=1-5)
    try:
        ctx = ssl._create_unverified_context()
        req = urllib.request.Request('https://smart.tdcc.com.tw/opendata/getOD.ashx?id=1-5', headers={'User-Agent': 'Mozilla/5.0'})
        raw_csv = urllib.request.urlopen(req, context=ctx, timeout=20).read().decode('utf-8-sig', errors='replace')
        for line in raw_csv.splitlines()[1:]:
            parts = line.split(',')
            if len(parts) < 6:
                continue
            code = parts[1].strip()
            lvl = _to_int(parts[2], 0)
            cnt = _to_int(parts[3], 0)
            pct = _to_float(parts[5], 0.0) or 0.0
            if not code:
                continue
            entry = chips_map.setdefault(code, {
                'date': trade_date_str or datetime.now().strftime('%Y-%m-%d'),
                'foreign_net_shares': 0, 'trust_net_shares': 0,
                'dealer_net_shares': 0, 'total_inst_shares': 0,
                'foreign_lots': 0.0, 'trust_lots': 0.0, 'total_inst_lots': 0.0,
            })
            if lvl in (12, 13, 14, 15):
                entry['tdcc_400_pct'] = round(entry.get('tdcc_400_pct', 0.0) + pct, 2)
            if lvl == 15:
                entry['tdcc_1000_pct'] = round(pct, 2)
                entry['tdcc_1000_holders'] = cnt
            elif lvl == 17:
                entry['tdcc_total_holders'] = cnt
    except Exception as tde:
        print(f"[TDCC 1-5] 略過: {tde}")

    return chips_map, trade_date_str


def fetch_tw_fundamentals():
    """從證交所與櫃買中心 OpenAPI 抓取真實毛利率/營益率/純益率、月營收 YoY、PE/PB/殖利率"""
    fund_map = {}

    # 1. 上市營益分析表 t187ap17_L
    try:
        rows = _http_json('https://openapi.twse.com.tw/v1/opendata/t187ap17_L')
        for r in rows:
            code = str(r.get('公司代號', '')).strip()
            if not code:
                continue
            gm = _to_float(r.get('毛利率(%)(營業毛利)/(營業收入)'))
            om = _to_float(r.get('營業利益率(%)(營業利益)/(營業收入)'))
            nm = _to_float(r.get('稅後純益率(%)(稅後純益)/(營業收入)'))
            fund_map.setdefault(code, {})['gross_margin'] = gm
            fund_map[code]['op_margin'] = om
            fund_map[code]['net_margin'] = nm
    except Exception as e:
        print(f"[t187ap17_L] 略過: {e}")

    # 2. 上市與上櫃每月營收 (t187ap05_L + mopsfin_t187ap05_O)
    for ep in ('https://openapi.twse.com.tw/v1/opendata/t187ap05_L',
               'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O'):
        try:
            rows = _http_json(ep)
            for r in rows:
                code = str(r.get('公司代號', '')).strip()
                if not code:
                    continue
                yoy = _to_float(r.get('營業收入-去年同月增減(%)'))
                mom = _to_float(r.get('營業收入-上月比較增減(%)'))
                cum_yoy = _to_float(r.get('累計營業收入-前期比較增減(%)'))
                d = fund_map.setdefault(code, {})
                d['rev_yoy'] = yoy
                d['rev_mom'] = mom
                d['rev_cum_yoy'] = cum_yoy
        except Exception as e:
            print(f"[Revenue API] 略過: {e}")

    # 3. 上市與上櫃本益比、殖利率、淨值比
    try:
        rows = _http_json('https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL')
        for r in rows:
            code = str(r.get('Code', '')).strip()
            if not code:
                continue
            d = fund_map.setdefault(code, {})
            d['pe_ratio'] = _to_float(r.get('PEratio'))
            d['div_yield'] = _to_float(r.get('DividendYield'))
            d['pb_ratio'] = _to_float(r.get('PBratio'))
    except Exception as e:
        print(f"[BWIBBU_ALL] 略過: {e}")

    try:
        rows = _http_json('https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis')
        for r in rows:
            code = str(r.get('SecuritiesCompanyCode', '')).strip()
            if not code:
                continue
            d = fund_map.setdefault(code, {})
            d['pe_ratio'] = _to_float(r.get('PriceEarningRatio'))
            d['div_yield'] = _to_float(r.get('YieldRatio'))
            d['pb_ratio'] = _to_float(r.get('PriceBookRatio'))
    except Exception as e:
        print(f"[TPEx PE] 略過: {e}")

    return fund_map


def run_gen18_backtest(g, regime_map, bench_r60, years_limit=None):
    """Gen 18 Ultimate 雙師×華爾街波段引擎 (扣 0.3% 成本)"""
    sub = g.copy()
    if years_limit is not None:
        cutoff = (datetime.now() - timedelta(days=int(years_limit * 365.25))).strftime('%Y-%m-%d')
        # 保留前 200 根供均線暖機
        idx_cut = np.searchsorted(sub['date'].values, cutoff)
        start_idx = max(0, idx_cut - 200)
        sub = sub.iloc[start_idx:].copy()
    else:
        cutoff = '1990-01-01'

    if len(sub) < 120:
        return {'win_rate': 0.0, 'total_return': 0.0, 'trade_count': 0}

    c = sub['close'].values
    o = sub['open'].values
    l = sub['low'].values
    h = sub['high'].values
    v = sub['volume'].values
    ma20 = sub['ma20'].values
    ma60 = sub['ma60'].values
    ma200 = sub['ma200'].values
    dates = sub['date'].values

    vol_ma5 = pd.Series(v).rolling(5).mean().values
    std20 = pd.Series(c).rolling(20).std().values
    bb_dn = ma20 - 2 * std20
    bb_up = ma20 + 2 * std20

    low9 = pd.Series(l).rolling(9).min().values
    high9 = pd.Series(h).rolling(9).max().values
    denom = np.where(high9 - low9 == 0, np.nan, high9 - low9)
    rsv = (c - low9) / denom * 100
    k = d = 50.0
    ks = np.zeros(len(c))
    ds = np.zeros(len(c))
    for i, val in enumerate(rsv):
        k = (2 / 3) * k + (1 / 3) * val if not np.isnan(val) else k
        d = (2 / 3) * d + (1 / 3) * k
        ks[i] = k
        ds[i] = d

    trades = []
    in_pos = False
    entry_p = stop_p = half_ret = 0.0
    half_sold = hit_up = False
    hold = 0
    entry_dt = ''

    start_bar = 60
    for i in range(start_bar, len(c)):
        if np.isnan(ma60[i]) or np.isnan(bb_dn[i]):
            continue
        m200 = ma200[i] if not np.isnan(ma200[i]) else ma60[i] * 0.98

        if not in_pos:
            mkt_ok = regime_map.get(dates[i], True)
            pullback_ok = (l[i] <= ma20[i] * 1.005 or l[i - 1] <= ma20[i - 1] * 1.005 or l[i] <= bb_dn[i] * 1.02) and c[i] > ma60[i]
            kd_turn = (ks[i] < 45 and ks[i] > ks[i - 1]) or (ks[i] > ds[i] and ks[i - 1] <= ds[i - 1] and ks[i] < 50)
            strong_trend = ma20[i] >= ma60[i] and ma60[i] > m200 and ma60[i] > ma60[max(0, i - 10)]
            sr60 = (c[i] - c[i - 60]) / c[i - 60] if c[i - 60] > 0 else 0.0
            b60 = bench_r60.get(dates[i], 0.0)
            if np.isnan(b60):
                b60 = 0.0
            vol_ok = v[i] >= vol_ma5[i] * 0.85 if vol_ma5[i] > 0 else True

            if mkt_ok and strong_trend and pullback_ok and kd_turn and (sr60 >= b60 - 0.02) and vol_ok and c[i] > o[i]:
                in_pos = True
                entry_p = c[i]
                stop_p = max(min(l[i], l[i - 1]) * 0.985, ma60[i] * 0.97)
                half_sold = hit_up = False
                hold = 0
                entry_dt = dates[i]
        else:
            hold += 1
            if not half_sold and h[i] >= entry_p * 1.055:
                half_sold = True
                half_ret = 0.055 - COST
                stop_p = max(stop_p, entry_p * 0.985)
            if h[i] >= bb_up[i]:
                hit_up = True
            if c[i] < stop_p or (hit_up and c[i] < ma20[i] and c[i] < bb_up[i]) or hold >= 80:
                rem_ret = ((c[i] - entry_p) / entry_p) - COST
                net_ret = (0.5 * half_ret + 0.5 * rem_ret) if half_sold else rem_ret
                if entry_dt >= cutoff:
                    trades.append(net_ret)
                in_pos = False

    if not trades:
        return {'win_rate': 0.0, 'total_return': 0.0, 'trade_count': 0}

    wins = sum(1 for r in trades if r > 0)
    tot_ret = float((np.prod([1.0 + r for r in trades]) - 1.0) * 100.0)
    return {
        'win_rate': round((wins / len(trades)) * 100.0, 1),
        'total_return': round(tot_ret, 1),
        'trade_count': len(trades),
    }


def main():
    print("1. 正在連線台灣證交所 (TWSE) 與櫃買中心 (TPEx) 抓取真實三大法人、融資融券與三率/月營收...")
    chips_map, chip_date = fetch_tw_chips()
    fund_map = fetch_tw_fundamentals()
    print(f"   ✅ 抓回真實法人籌碼 {len(chips_map)} 檔 (交易日 {chip_date})、真實基本面 {len(fund_map)} 檔")

    conn = sqlite3.connect(HIST_DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chips_daily (
            symbol TEXT,
            date TEXT,
            foreign_lots REAL,
            trust_lots REAL,
            total_inst_lots REAL,
            margin_diff INTEGER,
            margin_bal INTEGER,
            short_diff INTEGER,
            short_bal INTEGER,
            PRIMARY KEY (symbol, date)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fundamentals_snapshot (
            symbol TEXT PRIMARY KEY,
            updated_at TEXT,
            gross_margin REAL,
            op_margin REAL,
            net_margin REAL,
            three_rates_rising INTEGER,
            rev_yoy REAL,
            rev_mom REAL,
            pe_ratio REAL,
            pb_ratio REAL,
            div_yield REAL
        )
    """)

    df_all = pd.read_sql_query(
        "SELECT symbol, date, open, high, low, close, volume, ma20, ma60, ma200 "
        "FROM daily_bars ORDER BY symbol, date",
        conn,
    )
    vti = df_all[df_all['symbol'] == 'VTI'].set_index('date')
    tsm = df_all[df_all['symbol'] == '2330.TW'].set_index('date')
    us_bull = (vti['close'] > vti['ma60']).to_dict()
    tw_bull = (tsm['close'] > tsm['ma60']).to_dict()
    us_r60 = vti['close'].pct_change(60).to_dict()
    tw_r60 = tsm['close'].pct_change(60).to_dict()
    grouped = {sym: g for sym, g in df_all.groupby('symbol')}

    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        scan_data = json.load(f)

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    strong_buy_cnt = buy_cnt = high_wr_cnt = 0

    for s in scan_data.get('stocks', []):
        sym = s['symbol']
        is_tw = '.TW' in sym
        code = sym.split('.')[0]

        # A. 更新真實籌碼面 (取代原本的 Mock Chips)
        if is_tw and code in chips_map:
            ci = chips_map[code]
            f_lots = ci.get('foreign_lots', 0.0)
            t_lots = ci.get('trust_lots', 0.0)
            tot_lots = ci.get('total_inst_lots', 0.0)
            m_diff = ci.get('margin_diff', 0)
            # 嚴格定義：三大法人合計買賣超必須 > 0 才算法人偏多，杜絕外資大賣、投信小買卻標示買超的假陽性
            is_inst_buy = bool(tot_lots > 0)
            is_margin_surge = bool(m_diff > 500 and tot_lots < 0)
            s['chips'] = {
                'foreign_buy': is_inst_buy,
                'margin_surge': is_margin_surge,
                'foreign_lots': f_lots,
                'trust_lots': t_lots,
                'total_inst_lots': tot_lots,
                'margin_diff': m_diff,
                'tdcc_1000_pct': ci.get('tdcc_1000_pct'),
                'tdcc_400_pct': ci.get('tdcc_400_pct'),
                'tdcc_total_holders': ci.get('tdcc_total_holders'),
                'date': ci.get('date', chip_date),
                'source': 'TWSE/TPEx/TDCC Official',
            }
            cur.execute(
                "INSERT OR REPLACE INTO chips_daily VALUES (?,?,?,?,?,?,?,?,?)",
                (sym, ci.get('date', chip_date), f_lots, t_lots, tot_lots,
                 m_diff, ci.get('margin_bal', 0), ci.get('short_diff', 0), ci.get('short_bal', 0))
            )

        # B. 更新真實基本面 (證交所/櫃買三率、月營收 YoY、本益比、殖利率)
        if is_tw and code in fund_map:
            fi = fund_map[code]
            gm = fi.get('gross_margin')
            om = fi.get('op_margin')
            nm = fi.get('net_margin')
            yoy = fi.get('rev_yoy')
            mom = fi.get('rev_mom')
            pe = fi.get('pe_ratio')
            pb = fi.get('pb_ratio')
            dy = fi.get('div_yield')
            old_tr = (s.get('fundamentals') or {}).get('three_rates_rising', False)
            # 若有真實正營益率且月營收 YoY 正成長 (或原本季報三率三升為 True 且本業獲利 > 0)
            real_tr = bool(old_tr or ((om is not None and om > 10.0) and (nm is not None and nm > 8.0) and (yoy is not None and yoy > 10.0)))
            s['fundamentals'] = {
                'three_rates_rising': real_tr,
                'gross_margin': gm,
                'op_margin': om,
                'net_margin': nm,
                'rev_yoy': yoy,
                'rev_mom': mom,
                'pe_ratio': pe,
                'pb_ratio': pb,
                'div_yield': dy,
                'source': 'TWSE/TPEx OpenAPI',
            }
            cur.execute(
                "INSERT OR REPLACE INTO fundamentals_snapshot VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (sym, now_str, gm, om, nm, 1 if real_tr else 0, yoy, mom, pe, pb, dy)
            )

        # C. 執行 Gen 18 Ultimate 回測並對齊訊號門檻
        if sym in grouped:
            g = grouped[sym]
            regime = tw_bull if is_tw else us_bull
            br60 = tw_r60 if is_tw else us_r60
            bt5 = run_gen18_backtest(g, regime, br60, years_limit=5)
            bt20 = run_gen18_backtest(g, regime, br60, years_limit=20)
            chosen = bt5 if bt5['trade_count'] >= 3 else bt20

            s['backtest'] = {
                'win_rate': chosen['win_rate'],
                'total_return': chosen['total_return'],
                'trade_count': chosen['trade_count'],
                'win_rate_20y': bt20['win_rate'],
                'total_return_20y': bt20['total_return'],
                'trade_count_20y': bt20['trade_count'],
                'history_years': round(len(g) / 252.0, 1),
                'engine': 'Gen18-Ultimate',
            }
            cur.execute(
                "INSERT OR REPLACE INTO backtest_summary VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (sym, len(g), str(g['date'].iloc[0]), str(g['date'].iloc[-1]),
                 bt5['win_rate'], bt5['total_return'], bt5['trade_count'],
                 bt20['win_rate'], bt20['total_return'], bt20['trade_count'], now_str)
            )

            wr = chosen['win_rate']
            if wr >= 65.0:
                high_wr_cnt += 1

            # 嚴格訊號分級：拒絕給低勝率或破季線或法人大砍的股票貼 Strong Buy！
            close_p = float(s.get('close', 0) or 0)
            ma60_p = float(s.get('ma60', 0) or 0)
            ma200_p = float(s.get('ma200', 0) or 0)
            above_ma60 = close_p > ma60_p > 0
            inst_ok = (s.get('chips') or {}).get('foreign_buy', False)
            tr_ok = (s.get('fundamentals') or {}).get('three_rates_rising', False)

            if not above_ma60:
                s['signal'] = 'Avoid'
                s['score'] = min(int(s.get('score', 50)), 58)
            else:
                # 站上季線
                base_score = 65
                if wr >= 65.0:
                    base_score += 15
                elif wr >= 55.0:
                    base_score += 8
                if inst_ok:
                    base_score += 8
                if tr_ok:
                    base_score += 7
                if ma200_p > 0 and ma60_p >= ma200_p:
                    base_score += 4
                s['score'] = min(99, base_score)

                if wr >= 65.0 and inst_ok and s['score'] >= 85:
                    s['signal'] = 'Strong Buy'
                    strong_buy_cnt += 1
                elif wr >= 60.0 and s['score'] >= 78:
                    s['signal'] = 'Buy'
                    buy_cnt += 1
                else:
                    s['signal'] = 'Hold'

    conn.commit()
    conn.close()

    scan_data['last_updated'] = now_str
    scan_data['updated_at'] = now_str
    scan_data['engine'] = 'V4-Yen × Gen18-Ultimate (TWSE/TPEx/TDCC Real Chips & Fundamentals)'
    with open(SCAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, ensure_ascii=False, indent=2)
    for rel_target in (
        'live_portfolio.json',
        os.path.join('q_quant_888', 'scan_results.json'),
        os.path.join('q_quant_888', 'live_portfolio.json'),
        os.path.join('frontend', 'public', 'scan_results.json'),
        os.path.join('frontend', 'public', 'live_portfolio.json'),
        os.path.join('trading', 'scan_results.json'),
        os.path.join('trading', 'live_portfolio.json'),
    ):
        full_t = os.path.join(BASE_DIR, rel_target)
        if os.path.exists(os.path.dirname(full_t)):
            shutil.copy2(SCAN_FILE, full_t)

    print(f"2. ✅ 升級完成！全站勝率 >= 65% 共 {high_wr_cnt} 檔 | 嚴選 Strong Buy: {strong_buy_cnt} 檔 | Buy: {buy_cnt} 檔")


if __name__ == '__main__':
    main()

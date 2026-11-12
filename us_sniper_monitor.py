# -*- coding: utf-8 -*-
"""
GitHub Cloud US Sniper Monitor (24/7 Cloud Watch for AMD / AVGO / SOXX / NVDA)
Runs every 5 minutes during US market hours via GitHub Actions.
"""
import argparse
import json
import os
import ssl
import urllib.request
from datetime import datetime, timedelta, timezone

import yfinance as yf

TAIPEI_TZ = timezone(timedelta(hours=8))
US_EST_TZ = timezone(timedelta(hours=-5))
STATE_FILE = os.path.join("data", "us_sniper_state.json")


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"date": "", "sent": []}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def send_telegram(token, chat_id, text):
    if not token or not chat_id:
        print("Telegram credentials missing; skipping send.")
        return False
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps(
            {"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            ensure_ascii=False,
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, context=ctx, timeout=12) as res:
        body = json.loads(res.read().decode("utf-8"))
        print(f"Telegram sent: ok={body.get('ok')}, msg_id={body.get('result', {}).get('message_id')}")
        return bool(body.get("ok"))


def get_intraday_snapshot(ticker):
    tk = yf.Ticker(ticker)
    daily = tk.history(period="4mo")
    if daily.empty:
        return None
    prev_close = float(daily["Close"].iloc[-1])
    ma5 = float(daily["Close"].rolling(5).mean().iloc[-1])
    ma10 = float(daily["Close"].rolling(10).mean().iloc[-1])
    ma20 = float(daily["Close"].rolling(20).mean().iloc[-1])
    ma60 = float(daily["Close"].rolling(60).mean().iloc[-1])

    intra = tk.history(period="1d", interval="1m", prepost=False)
    if intra.empty:
        # Fallback to prepost if before regular open
        intra = tk.history(period="1d", interval="1m", prepost=True)
        is_regular = False
    else:
        is_regular = True

    if intra.empty:
        return None

    last_price = float(intra["Close"].iloc[-1])
    last_open = float(intra["Open"].iloc[-1])
    last_time = intra.index[-1]
    day_high = float(intra["High"].max())
    day_low = float(intra["Low"].min())

    vol = intra["Volume"].fillna(0)
    tp = (intra["High"] + intra["Low"] + intra["Close"]) / 3.0
    cum_vol = float(vol.sum())
    vwap = float((tp * vol).sum() / cum_vol) if cum_vol > 0 else last_price

    return {
        "ticker": ticker,
        "price": last_price,
        "open": last_open,
        "prev_close": prev_close,
        "chg_pct": (last_price / prev_close - 1) * 100,
        "vwap": vwap,
        "day_high": day_high,
        "day_low": day_low,
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "ma60": ma60,
        "is_regular": is_regular,
        "bar_time": str(last_time),
    }


def evaluate_signals(snapshots, est_now):
    alerts = []
    hhmm = est_now.hour * 100 + est_now.minute
    after_1000 = hhmm >= 1000  # 23:00 TW time (after first 30m washout)
    after_1015 = hhmm >= 1015

    avgo = snapshots.get("AVGO")
    if avgo and avgo["is_regular"] and after_1000:
        p, v, ma60 = avgo["price"], avgo["vwap"], avgo["ma60"]
        if p >= ma60 and p >= v:
            alerts.append((
                "AVGO_BUY_BREAKOUT",
                f"🎯 <b>【開槍訊號｜AVGO 博通】站穩季線＋日內 VWAP</b>\n"
                f"• 現價：<b>{p:.2f}</b> ({avgo['chg_pct']:+.2f}%) ｜ VWAP：{v:.2f}\n"
                f"• 季線 MA60：{ma60:.2f} ｜ 月線 MA20：{avgo['ma20']:.2f}\n"
                f"• 戰術：確認不被 NVDA 拖累，可分批 20%~30% 試單，防守 10 日線 {avgo['ma10']:.2f}。"
            ))
        elif 343.0 <= p < ma60 and p >= v and p > avgo["open"]:
            alerts.append((
                "AVGO_BUY_SUPPORT",
                f"🎯 <b>【開槍訊號｜AVGO 博通】回測季線區止跌站上 VWAP</b>\n"
                f"• 現價：<b>{p:.2f}</b> ({avgo['chg_pct']:+.2f}%) ｜ VWAP：{v:.2f}\n"
                f"• 戰術：回測有撐，可小倉位試單，防守 {avgo['ma10']:.2f}。"
            ))

    amd = snapshots.get("AMD")
    if amd and amd["is_regular"] and after_1000:
        p, v = amd["price"], amd["vwap"]
        if 545.0 <= p <= 562.0 and p >= v:
            alerts.append((
                "AMD_BUY_PULLBACK",
                f"🎯 <b>【開槍訊號｜AMD 超微】回測支撐守穩＋站上 VWAP</b>\n"
                f"• 現價：<b>{p:.2f}</b> ({amd['chg_pct']:+.2f}%) ｜ VWAP：{v:.2f}\n"
                f"• 月線 MA20：{amd['ma20']:.2f} ｜ 季線 MA60：{amd['ma60']:.2f}\n"
                f"• 戰術：未追高、回踩支撐轉強，可分批 20%~30% 試單，防守月線 {amd['ma20']:.2f}。"
            ))
        elif p > 562.0 and p >= v and after_1015:
            alerts.append((
                "AMD_BUY_STRENGTH",
                f"🚀 <b>【強勢狙擊｜AMD 超微】盤中強勢站穩 VWAP 續攻</b>\n"
                f"• 現價：<b>{p:.2f}</b> ({amd['chg_pct']:+.2f}%) ｜ VWAP：{v:.2f}\n"
                f"• 戰術：逆勢領漲確認，切勿一次滿倉，分批介入並嚴設停損 {amd['ma60']:.2f}。"
            ))

    soxx = snapshots.get("SOXX")
    if soxx and soxx["is_regular"] and after_1000:
        p, v, ma10 = soxx["price"], soxx["vwap"], soxx["ma10"]
        if p >= ma10 and p >= v:
            alerts.append((
                "SOXX_STABILIZE",
                f"🛡️ <b>【指數止穩｜SOXX 費半ETF】守穩十日線＋站上 VWAP</b>\n"
                f"• 現價：<b>{p:.2f}</b> ({soxx['chg_pct']:+.2f}%) ｜ VWAP：{v:.2f} ｜ MA10：{ma10:.2f}\n"
                f"• 戰術：半導體板塊整體恐慌消化中，穩健型可留意分批佈局。"
            ))

    nvda = snapshots.get("NVDA")
    if nvda and nvda["is_regular"]:
        p, v = nvda["price"], nvda["vwap"]
        if p < 150.0:
            alerts.append((
                "NVDA_BREAK_150",
                f"⚠️ <b>【風險警訊｜NVDA】跌破 150 整數大關！</b>\n"
                f"• 現價：<b>{p:.2f}</b> ({nvda['chg_pct']:+.2f}%) ｜ 日低：{nvda['day_low']:.2f}\n"
                f"• 戰術：賣壓尚未出盡，<b>嚴禁接刀！</b>繼續空手觀望。"
            ))
        elif p >= 169.60 and p >= v and hhmm >= 1030:
            alerts.append((
                "NVDA_RECLAIM_169",
                f"🟢 <b>【止跌觀察｜NVDA】放量收復 169.60 籌碼支撐＋VWAP</b>\n"
                f"• 現價：<b>{p:.2f}</b> ({nvda['chg_pct']:+.2f}%) ｜ VWAP：{v:.2f}\n"
                f"• 戰術：恐慌盤洗出右腳訊號浮現，可小倉位觀察右側機會。"
            ))

    return alerts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print status without sending Telegram")
    args = parser.parse_args()

    tw_now = datetime.now(TAIPEI_TZ)
    est_now = datetime.now(US_EST_TZ)
    today_key = est_now.strftime("%Y-%m-%d")

    state = load_state()
    if state.get("date") != today_key:
        state = {"date": today_key, "sent": []}

    tickers = ["AMD", "AVGO", "SOXX", "NVDA"]
    snapshots = {}
    for t in tickers:
        snap = get_intraday_snapshot(t)
        if snap:
            snapshots[t] = snap
            print(
                f"{t:5s} | reg={snap['is_regular']} | price={snap['price']:.2f} ({snap['chg_pct']:+.2f}%) "
                f"| vwap={snap['vwap']:.2f} | ma10={snap['ma10']:.2f} | ma60={snap['ma60']:.2f}"
            )

    alerts = evaluate_signals(snapshots, est_now)
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "7660257976").strip()

    new_msgs = []
    for code, msg in alerts:
        if code not in state["sent"]:
            new_msgs.append((code, msg))

    if new_msgs:
        header = f"🇺🇸 <b>【GitHub 雲端美股狙擊哨兵｜{tw_now.strftime('%m/%d %H:%M')} 台北時間】</b>\n\n"
        full_text = header + "\n\n".join(m for _, m in new_msgs)
        if args.dry_run:
            print("--- DRY RUN ALERT ---\n" + full_text)
        else:
            if send_telegram(token, chat_id, full_text):
                for code, _ in new_msgs:
                    state["sent"].append(code)
                save_state(state)
    else:
        print(f"No new sniper alerts triggered at EST {est_now.strftime('%H:%M')} (already sent: {state['sent']}).")


if __name__ == "__main__":
    main()

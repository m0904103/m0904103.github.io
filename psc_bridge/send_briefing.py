# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.error
import ssl

CONFIG_PATH = r"C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io\config\line_config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

MESSAGE_TEXT = """【雙師實戰學院】2026/11/17 美股開盤前瞻：AI擠泡沫與全球資金大挪移！

各位學員晚安，我是阿村伯（蔡鎮村博士）與顏春煌教授。

今晚美股開盤前夕，全球金融市場正經歷一場「歷史級別的資金大轉向」。在進場前，請全體學員務必牢記以下四大核心紀律：

━━━━━━━━━━━━━━━━━━━━
📊 一、 今日台股盤後籌碼震撼警訊（借鏡美股）
━━━━━━━━━━━━━━━━━━━━
今日台股上下劇烈震盪 1,747 點，三大法人單日狂賣 -576 億元！
1. 提款重災區：外資狂砍台積電 -14,606 張、指數 ETF 遭自營避險血洗。
2. 資金唯一避風港：三大法人狂掃 00632R（台灣50反1）高達 9.96 萬張！其餘資金全面躲入非科技防禦股（中鼎、中信金、長榮航、統一）。
👉 結論：外資與本土主力正在大規模從 AI 科技股去槓桿，這股避險潮今晚將直撲美股！

━━━━━━━━━━━━━━━━━━━━
🌐 二、 美股盤前重磅情報解讀
━━━━━━━━━━━━━━━━━━━━
1. 華爾街 13F 巨頭分道揚鑣：
   • 橋水大砍英偉達 (NVDA) -30.5%、索羅斯與德魯肯米勒同步削倉。
   • 唯有散戶指標木頭姐 (ARK) 逆勢大買 NVDA +85.4%（典型的法人出貨給散戶接刀模式）。
   • 巴菲特團隊加碼萊納建築 (LEN) 與達美航空 (DAL)，資金大幅流向「實體剛需與現金流母牛」。
2. 歐洲大銀行「甩賣 8 億美元數據中心債務」：
   • ING 與法興銀行折價掛牌出售 AI 機房貸款，顯示金融體系開始對 AI 投入產出比 (ROI) 產生警惕，去槓桿骨牌正在成形。
3. NVDA 國會調查與成立安全委員會：
   • 英偉達正式從「純算力成長股」被推入「地緣政治與國防審查」的暴風圈，本益比將面臨殘酷重估。

━━━━━━━━━━━━━━━━━━━━
🎯 三、 雙師實戰操盤準則（今晚策略）
━━━━━━━━━━━━━━━━━━━━
1. 【嚴禁盲目抄底科技股】：
   • 顏春煌教授走圖鐵律：均線空頭排列＋機構法人去槓桿時，切忌「左側接刀」。任何盤中急彈皆視為逃命波，不可將反彈當回升。
2. 【現金為王，防守第一】：
   • 建議整體投資組合維持 60%～70% 現金儲備。在市場滿天鬼故事、恐慌性多殺多尚未見底前，空手就是最好的獲利！
3. 【關注實體剛需與醫療防禦】：
   • 若欲布局，僅關注具備「真金白銀 CMF 資金淨流入、月線翻揚、三閘全過」之防禦型標的（如系統精選之醫療龍頭 UNH，關鍵防線 404.69 美元）。

「多頭市場比誰賺得快，空頭市場比誰活得久！」
守住本金，等待大戶殺出帶血的籌碼，那才是我們進場撿黃金的世紀時刻！

—— 阿村伯 (蔡鎮村博士) × 顏春煌教授 敬上"""

def send_telegram(cfg, text):
    token = cfg.get("telegram_bot_token")
    chat_id = cfg.get("telegram_chat_id")
    if not token or not chat_id:
        print("[Telegram] Config missing token or chat_id")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            print("[Telegram] Broadcast success! Status:", resp.getcode())
            return True
    except Exception as e:
        print("[Telegram] Failed to send:", e)
        return False

def send_line(cfg, text):
    token = cfg.get("channel_access_token")
    user_id = cfg.get("user_id")
    if not token or not user_id:
        print("[LINE] Config missing token or user_id")
        return False
    url = "https://api.line.me/v2/bot/message/push"
    payload = json.dumps({
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    })
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            print("[LINE] Broadcast success! Status:", resp.getcode())
            return True
    except Exception as e:
        print("[LINE] Failed to send:", e)
        return False

if __name__ == "__main__":
    cfg = load_config()
    print("Sending to Telegram...")
    send_telegram(cfg, MESSAGE_TEXT)
    print("Sending to LINE...")
    send_line(cfg, MESSAGE_TEXT)

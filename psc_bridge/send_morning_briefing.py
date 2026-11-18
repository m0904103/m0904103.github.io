# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.error
import ssl

CONFIG_PATH = r"C:\Users\manpo\.gemini\antigravity\scratch\m0904103.github.io\config\line_config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

MESSAGE_TEXT = """【雙師實戰學院】2026/11/18 台股開盤前瞻：英偉達財報解壓與今日三大紀律！

各位學員早安！我是阿村伯（蔡鎮村博士）與顏春煌教授。

昨夜美股盤後迎來歷史級別的重頭戲，英偉達 (NVDA) 公布 Q3 財報，營收 1,158 億美元（年增 103% 翻倍）、Q4 展望上調至 1,300 億美元，盤後擴大上漲近 +5%！台積電 ADR (TSM) 更狂飆 +5.45% 衝上 379.28 美元！

台股早盤即將迎來報復性「解壓反彈」，預估加權指數開盤將大漲 +850 ~ +1,050 點！但在全體市場歡呼之際，請全體學員務必保持專業清醒，牢記今日三大實戰指令：

━━━━━━━━━━━━━━━━━━━━
🎯 一、 今日開盤關鍵：開高絕不「市價盲追」！
━━━━━━━━━━━━━━━━━━━━
1. 【解壓反彈 vs 多頭回升】：
   • 顏春煌教授走圖 SOP：空頭格局中的第一根大反彈，通常是主力用來「解套」與「換手」的震盪波。
   • 昨天在 22.50 套牢 00981A 或在 2,270 套牢台積電的短線客，今天開高第一盤都在等著解套倒貨！
   • 嚴禁掛「市價單」盲目追高，容易直接買在全天最高點！
2. 【若要做短衝，只等回踩關鍵價】：
   • 00981A 昨天收 21.53，今日阿村伯開盤關鍵防守中軸在 22.10 ~ 22.15 元。
   • 寧可等開盤 15 分鐘衝高回踩 22.15 ~ 22.25 有撐再掛限價，絕不在開盤第一秒追高！

━━━━━━━━━━━━━━━━━━━━
🏛️ 二、 英偉達電話會議官方明牌：台廠誰受惠？
━━━━━━━━━━━━━━━━━━━━
臨時 CEO 克雷斯今晨親自宣布：
1. 【台積電 (2330)】：
   • 下一代旗艦 Vera Rubin NVL72 與 Vera CPU 全面採用台積電先進技術量產！克雷斯更透露「台積電高層領導本週就在英偉達總部坐鎮」！
   • 昨日有低接台積電零股的學員，今早逢高衝上 2,275 ~ 2,285 元以上，正是分批獲利、開心數錢的絕佳檔位！
2. 【先進封裝與載板新夥伴】：
   • 正式點名與「日月光投控/矽品精密 (3711)」在先進封裝達成新協議；
   • 與「景碩科技 (3189)」在基板擴產達成新協議，今日盤中可列入強勢關注。

━━━━━━━━━━━━━━━━━━━━
🛡️ 三、 雙師整體風控與盤中觀察指標
━━━━━━━━━━━━━━━━━━━━
1. 【緊盯外資 9.7 萬口期貨空單】：
   • 昨天外資買超第一名是 00632R（台灣50反1，狂掃近 10 萬張）。
   • 今天大盤開高反彈，必須檢視外資是否「真金白銀大幅回補期貨空單與反1」；若外資空單不退、現貨趁拉高倒貨，中午後容易衝高回落。
2. 【手握現金，大賺不貪】：
   • 投資組合建議維持高現金水位（60% 以上）。
   • 「買在無人問津處，賣在人聲鼎沸時！」有獲利的短線部位逢高開心收割，守住利潤才是真贏家！

祝全體學員今日操盤順利，穩健大豐收！

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

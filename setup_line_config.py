# -*- coding: utf-8 -*-
"""
setup_line_config.py - q_quant_888 LINE 推播快速設定與實機連線檢驗工具
================================================================================
本腳本引導您在 1 分鐘內完成 LINE 官方帳號 (Messaging API) 的串接設定，
並立即發送一則「顏老師鐵律到價通知卡片」至您的手機 LINE，確保推播鏈路 100% 暢通！
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 確保輸出編碼為 UTF-8
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / 'config'
CONFIG_FILE = CONFIG_DIR / 'line_config.json'
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

TAIPEI_TZ = timezone(timedelta(hours=8))

def test_line_credentials(token, user_id):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    now_str = datetime.now(TAIPEI_TZ).strftime('%Y-%m-%d %H:%M:%S')
    test_message = {
        'type': 'flex',
        'altText': '🎯【q_quant_888 顏老師鐵律】LINE 推播連線成功！',
        'contents': {
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
                        'text': '🟢 系統連線成功 ｜ q_quant_888',
                        'weight': 'bold',
                        'color': '#10B981',
                        'size': 'sm'
                    },
                    {
                        'type': 'text',
                        'text': '顏老師鐵律盤中決策輔助',
                        'weight': 'bold',
                        'size': 'xl',
                        'color': '#F8FAFC',
                        'margin': 'sm'
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
                        'type': 'text',
                        'text': '🎉 恭喜學長！LINE 到價推播守護已成功啟用！',
                        'color': '#38BDF8',
                        'weight': 'bold',
                        'size': 'md'
                    },
                    {
                        'type': 'text',
                        'text': '盤中當標的回測「甜蜜買進區」且守穩「MA60生命線」時，系統將第一時間推送即時卡片至您的 LINE。',
                        'color': '#CBD5E1',
                        'size': 'xs',
                        'wrap': True,
                        'margin': 'md'
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
                        'contents': [
                            {'type': 'text', 'text': '🛡️ 守護機制：當日最低價無情停損 (Low of Entry Day)', 'color': '#F87171', 'size': 'xs'},
                            {'type': 'text', 'text': '🚀 獲利目標：+10% ~ +15% 階梯分批落袋', 'color': '#4ADE80', 'size': 'xs', 'margin': 'xs'},
                            {'type': 'text', 'text': '📱 下單執行：由您手動開啟券商 APP 自主下單', 'color': '#FDE047', 'size': 'xs', 'margin': 'xs'}
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
                    {'type': 'text', 'text': f'測試驗證時間：{now_str}', 'color': '#64748B', 'size': 'xxs', 'align': 'center'}
                ]
            }
        }
    }
    
    payload = {
        'to': user_id,
        'messages': [test_message]
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status == 200, '連線成功'
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8', errors='replace')
        return False, f'HTTP {e.code}: {err}'
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print(" 🎯 q_quant_888 顏老師鐵律 LINE Messaging API 快速設定精靈")
    print("=" * 70)
    print("提示：若您尚未建立 LINE Bot，請至 LINE Developers (https://developers.line.biz/zh-hant/)")
    print("  1. 建立 Messaging API Channel (免費官方帳號)")
    print("  2. 在 [Messaging API] 分頁取得 Channel Access Token (long-lived)")
    print("  3. 在 [Basic settings] 分頁取得 Your user ID (以 U 開頭的一串碼)")
    print("  4. 掃描 QR code 將該官方帳號加入好友！")
    print("=" * 70)
    
    existing_token = ""
    existing_user = ""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                c = json.load(f)
                existing_token = c.get('channel_access_token', '')
                existing_user = c.get('user_id', '')
        except Exception:
            pass
            
    token = input(f"\n請輸入 Channel Access Token [{existing_token[:15]}...]: ").strip() or existing_token
    user_id = input(f"請輸入 Your user ID [{existing_user}]: ").strip() or existing_user
    
    if not token or not user_id:
        print("❌ Token 與 User ID 不能為空！")
        return
        
    print("\n🚀 正在向您的 LINE 發送連線測試卡片...")
    success, msg = test_line_credentials(token, user_id)
    
    if success:
        print("✅ 測試卡片已發送成功！請查看手機 LINE 聊天室！")
        config = {
            'channel_access_token': token,
            'user_id': user_id,
            'cooldown_minutes': 60,
            'watchlist': [
                '2330.TW', '3017.TW', '3324.TWO', '6669.TW', '3081.TWO',
                '6451.TW', '1519.TW', '2382.TW', '2454.TW', '2317.TW'
            ]
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"💾 設定已安全儲存至 {CONFIG_FILE} (本檔案已被 .gitignore 守護，絕不外流)！")
        print("\n💡 若要讓 GitHub Actions 在您電腦關機時也能自動推播，請將以下兩組密鑰填入 GitHub 儲存庫：")
        print("   前往 GitHub Repository -> Settings -> Secrets and variables -> Actions")
        print("   1. LINE_CHANNEL_ACCESS_TOKEN")
        print("   2. LINE_USER_ID")
    else:
        print(f"❌ 測試失敗: {msg}")

if __name__ == '__main__':
    main()

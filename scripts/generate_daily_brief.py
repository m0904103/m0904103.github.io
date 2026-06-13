import os
import requests
from bs4 import BeautifulSoup
import datetime
import json
import re

# 嘗試載入 google-genai (支援最新的 Gemini 1.5 系列)
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Please install google-genai: pip install google-genai")
    exit(1)

def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    # 移除 script 與 style
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text(separator='\n')
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        exit(1)

    print("Fetching data from sources...")
    
    # 來源 1: youtube-stock-tracker (HTML 靜態內容)
    tracker_html = fetch_content("https://m0904103.github.io/youtube-stock-tracker/")
    tracker_text = clean_html(tracker_html)
    
    # 來源 2: trump-advisory (取得 React Component 內的假資料或原始碼作為代表)
    trump_jsx = fetch_content("https://raw.githubusercontent.com/m0904103/trump-advisory/main/src/components/LiveFeed.jsx")
    
    # 來源 3: trading (正規軍量化數據，嘗試從本地讀取 scan_results.json 或是從網頁抓)
    trading_text = ""
    local_scan_path = "../trading/assets/scan_results.json"
    if os.path.exists(local_scan_path):
        with open(local_scan_path, "r", encoding="utf-8") as f:
            trading_text = f.read()[:5000] # 只取前 5000 字元避免 token 過長
    else:
        # Fallback to fetching HTML
        trading_html = fetch_content("https://m0904103.github.io/trading/")
        trading_text = clean_html(trading_html)

    print("Data fetched. Calling Gemini API...")
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    你現在是一位金融分析師，需要根據以下三個資料來源，產出一份每日盤前戰略預報。
    請分別以「顏老師（注重 MA60 季線、量化紀律、正規軍藍籌股）」與「阿村伯（注重總經輿情、地緣政治、散戶動向）」的口吻來撰寫。
    
    【資料來源 1：股市輿情追蹤】
    {tracker_text[:3000]}
    
    【資料來源 2：川普投顧即時矩陣】
    {trump_jsx[:2000]}
    
    【資料來源 3：正規軍量化數據】
    {trading_text[:3000]}
    
    【輸出格式要求】
    請回傳一個 JSON 格式的字串，包含三個欄位 (請使用純 JSON，不要包含 Markdown backticks 如 ```json)：
    {{
        "teacher_yen": "顏老師的分析內容（使用 HTML 標籤排版，如 <p>, <ul>, <li>, <strong>）",
        "uncle_tsun": "阿村伯的分析內容（使用 HTML 標籤排版，如 <p>, <ul>, <li>, <strong>）",
        "strategy": "綜合行動建議（使用 HTML 標籤排版，如 <p>, <ul>, <li>, <strong>）"
    }}
    
    注意：
    1. 內容要夠專業、具備實戰感。
    2. 顏老師要提到 MA60、預期利潤大於摩擦力、多方事實等專有名詞。
    3. 阿村伯要提到大戶動向、地緣政治影響（如原油、軍工）或台股外溢效應。
    4. 回傳必須是合法的 JSON。
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
            )
        )
        
        result_text = response.text.strip()
        # Clean up if markdown backticks were added
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        data = json.loads(result_text)
    except Exception as e:
        print(f"Error calling Gemini API or parsing JSON: {e}")
        print("Raw response:", response.text if 'response' in locals() else "None")
        exit(1)

    print("Generating HTML...")
    
    # 讀取模板
    template_path = os.path.join(os.path.dirname(__file__), "..", "daily-brief", "template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 替換變數
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    html_output = template.replace("{{DATE_TIME}}", now_str)
    html_output = html_output.replace("{{TEACHER_YEN_CONTENT}}", data.get("teacher_yen", "<p>暫無數據</p>"))
    html_output = html_output.replace("{{UNCLE_TSUN_CONTENT}}", data.get("uncle_tsun", "<p>暫無數據</p>"))
    html_output = html_output.replace("{{STRATEGY_CONTENT}}", data.get("strategy", "<p>暫無數據</p>"))

    # 寫入結果
    output_path = os.path.join(os.path.dirname(__file__), "..", "daily-brief", "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()

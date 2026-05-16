import os
with open(r'C:\Users\manpo\OneDrive\桌面\AI投資分析\daily_scanner.py', encoding='utf-8') as f:
    lines = f.readlines()

# Extract from line 155 (index 154) onwards
new_content = "".join(lines[154:])
new_content = new_content.replace('"8711776249:AAFGdZh-k58nsGyBeUWYN7YskfxygPVctvE"', 'os.environ.get("TELEGRAM_TOKEN")')
new_content = new_content.replace('"7660257976"', 'os.environ.get("CHAT_ID")')

new_content = "import os\n" + new_content

with open(r'C:\Users\manpo\OneDrive\桌面\AI_Stock_Scanner_Cloud\main.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

import json
import os
import re

data_text = """
1503 士電
.
Strong Buy
現價
$201
生命線
200.27
1519 華城
.
Strong Buy
現價
$907
生命線
902.63
QQQ 納斯達克100
.
Buy
現價
$707.24
生命線
621.71
SPY 標普500
.
Buy
現價
$738.18
生命線
685.74
SMH 半導體ETF
.
Buy
現價
$561.25
生命線
436.35
SOXX 費半ETF
.
Buy
現價
$515.99
生命線
384.51
XLK 科技ETF
.
Buy
現價
$175.2
生命線
146.18
XLE 能源ETF
.
Strong Buy
現價
$57.57
生命線
57.35
VGT 資訊科技ETF
.
Buy
現價
$112.3
生命線
95.3
VOO 標普500ETF
.
Buy
現價
$678.67
生命線
630.39
VTI 全美股市ETF
.
Buy
現價
$362.79
生命線
338.14
IWM 羅素2000ETF
.
Strong Buy
現價
$282.57
生命線
262.52
DIA 道瓊工業指數ETF
.
Strong Buy
現價
$497.89
生命線
480.97
NVDA 輝達
.
Strong Buy
現價
$220.78
生命線
189.8
TSM 台積電 ADR
.
Strong Buy
現價
$397.28
生命線
365.39
AVGO 博通
.
Strong Buy
現價
$419.3
生命線
356.95
AMD 超微
.
Buy
現價
$448.29
生命線
254.41
QCOM 高通
.
Strong Buy
現價
$210.31
生命線
144.47
MU 美光
.
Buy
現價
$766.58
生命線
455.92
ASML 艾司摩爾
.
Strong Buy
現價
$1520.94
生命線
1414.09
ARM 安謀
.
Strong Buy
現價
$207.92
生命線
156.16
INTC 英特爾
.
Buy
現價
$120.61
生命線
61.97
AMAT 應用材料
.
Strong Buy
現價
$431.2
生命線
375.36
LRCX 科林研發
.
Strong Buy
現價
$289.24
生命線
242.73
DELL 戴爾
.
Strong Buy
現價
$238.94
生命線
174.47
STX 希捷
.
Buy
現價
$808.79
生命線
495.46
MSFT 微軟
.
Buy
現價
$407.77
生命線
398.23
AMZN 亞馬遜
.
Strong Buy
現價
$265.82
生命線
229.17
GOOGL 谷歌
.
Buy
現價
$387.35
生命線
323.75
AAPL 蘋果
.
Buy
現價
$294.8
生命線
264.21
PANW 帕羅奧圖
.
Buy
現價
$215.6
生命線
167.39
FTNT 飛塔
.
Buy
現價
$113.87
生命線
84.33
CRWD 庫德史萊克
.
Buy
現價
$546.18
生命線
424.3
ORCL 甲骨文
.
Strong Buy
現價
$186.83
生命線
159.21
CSCO 思科
.
Buy
現價
$99.29
生命線
82.85
VRT 維諦
.
Strong Buy
現價
$367.13
生命線
282.76
NEE 新紀元能源
.
Strong Buy
現價
$94.59
生命線
92.89
EQIX 艾奎尼克斯
.
Strong Buy
現價
$1080.63
生命線
1010.86
CAT 卡特彼勒
.
Strong Buy
現價
$912.14
生命線
767.88
LIN 林德
.
Strong Buy
現價
$503.87
生命線
496.23
BA 波音
.
Strong Buy
現價
$236.87
生命線
220.15
BX 黑石
.
Strong Buy
現價
$122.76
生命線
116.78
BRK-B 波克夏
.
Strong Buy
現價
$484.96
生命線
482.38
JPM 摩根大通
.
Buy
現價
$304.88
生命線
299.94
V 威士
.
Strong Buy
現價
$326.42
生命線
312.48
MA 萬事達
.
禁區
現價
$499.81
生命線
506.09
GS 高盛
.
Strong Buy
現價
$945.9
生命線
879.4
MS 摩根士丹利
.
Strong Buy
現價
$191.88
生命線
173.6
BAC 美國銀行
.
Buy
現價
$50.78
生命線
50.68
AXP 美國運通
.
Buy
現價
$314.31
生命線
313.79
BLK 貝萊德
.
Strong Buy
現價
$1092.5
生命線
1019.35
UNH 聯合健康
.
Buy
現價
$396.39
生命線
308.85
LLY 禮來
.
Strong Buy
現價
$989.87
生命線
954.78
NVO 諾和諾德
.
Buy
現價
$47
生命線
39.32
COST 好市多
.
Strong Buy
現價
$1021.88
生命線
997.2
WMT 沃爾瑪
.
Strong Buy
現價
$130.35
生命線
125.94
KO 可口可樂
.
Strong Buy
現價
$80.03
生命線
77.3
MSTR 微策略
.
Strong Buy
現價
$184.42
生命線
146.37
COIN Coinbase
.
Strong Buy
現價
$207.64
生命線
188.17
MARA Marathon Digital
.
Strong Buy
現價
$12.72
生命線
9.75
OKLO Oklo Inc.
.
Strong Buy
現價
$73.63
生命線
62.05
ETN 伊頓
.
Buy
現價
$401.53
生命線
381.67
PWR Quanta Services
.
Buy
現價
$765.81
生命線
601.32
GEV GE Vernova
.
Strong Buy
現價
$1071.98
生命線
935.5
VRTX Vertex Pharm
.
禁區
現價
$448.29
生命線
451.88
TER 泰瑞達
.
Strong Buy
現價
$358.45
生命線
332.37
SNPS Synopsys
.
Strong Buy
現價
$513.21
生命線
440.98
CDNS Cadence
.
Strong Buy
現價
$358.04
生命線
304.51
MDB MongoDB
.
Strong Buy
現價
$308.72
生命線
272
DDOG Datadog
.
Buy
現價
$199.94
生命線
127.96
TSLA 特斯拉
.
Strong Buy
現價
$433.45
生命線
388.64
ABNB Airbnb
.
Buy
現價
$135.48
生命線
133.18
UBER 優步
.
Strong Buy
現價
$76.36
生命線
74.1
DKNG DraftKings
.
Strong Buy
現價
$24.61
生命線
23.51
HOOD Robinhood
.
Buy
現價
$78.27
生命線
76.45
GM 通用汽車
.
禁區
現價
$76.44
生命線
76.89
SBUX 星巴克
.
Strong Buy
現價
$106.58
生命線
97.78
TEL TE Connectivity
.
禁區
現價
$213.73
生命線
215.95
GLW 康寧
.
Strong Buy
現價
$198.24
生命線
151.91
HPE 慧與科技
.
Strong Buy
現價
$30.21
生命線
24.52
NTAP NetApp
.
Strong Buy
現價
$116.23
生命線
103.52
WDC 威騰電子
.
Buy
現價
$488.74
生命線
334.27
WOLF Wolfspeed
.
Buy
現價
$53.72
生命線
23.67
ON 安森美
.
Strong Buy
現價
$104.11
生命線
74.38
NXPI 恩智浦
.
Strong Buy
現價
$294.23
生命線
224.79
MCHP 微晶片科技
.
Strong Buy
現價
$97.7
生命線
75.78
MPWR 芯源系統
.
Strong Buy
現價
$1599.52
生命線
1276.89
APP AppLovin
.
Strong Buy
現價
$490.69
生命線
441.89
RDDT Reddit
.
Buy
現價
$152.35
生命線
146.83
CI 信諾
.
Strong Buy
現價
$298.49
生命線
276.28
CVS CVS健康
.
Buy
現價
$95.15
生命線
77.38
ELV Elevance Health
.
Buy
現價
$393.3
生命線
321
HUM Humana
.
Buy
現價
$295.35
生命線
197.11
FDX 聯邦快遞
.
Buy
現價
$376.42
生命線
371.89
NSC 諾福克南方
.
Strong Buy
現價
$312.35
生命線
301.2
UNP 聯合太平洋
.
Strong Buy
現價
$265.6
生命線
254.39
CSX CSX運輸
.
Strong Buy
現價
$44.53
生命線
42.14
GD 通用動力
.
Strong Buy
現價
$346.46
生命線
344.88
EMR 艾默生電氣
.
禁區
現價
$137.28
生命線
139.67
AME 阿美特克
.
Strong Buy
現價
$231.2
生命線
227.03
PAYX 沛齊
.
Strong Buy
現價
$93.71
生命線
92.45
DOV Dover Corp
.
禁區
現價
$216.71
生命線
217.94
MRVL 馬威爾
.
Strong Buy
現價
$164.5
生命線
114.97
ZS Zscaler
.
Strong Buy
現價
$146.17
生命線
145.32
"""

lines = [l.strip() for l in data_text.strip().split('\n') if l.strip()]
stocks = []
i = 0
while i < len(lines):
    header = lines[i] # "1503 士電" or "QQQ 納斯達克100"
    # Skip "." line
    signal = lines[i+2]
    # Skip "現價"
    price_str = lines[i+4].replace('$', '').replace(',', '')
    # Skip "生命線"
    ma60_str = lines[i+6].replace(',', '')
    
    parts = header.split(' ', 1)
    symbol = parts[0]
    name = parts[1] if len(parts) > 1 else symbol
    
    # Logic to fix market segregation
    market = 'us'
    if symbol.isdigit() and len(symbol) >= 4:
        market = 'tw'
        if not symbol.endswith('.TW'):
            symbol += '.TW'
    elif symbol.endswith('.TW'):
        market = 'tw'
        
    stocks.append({
        "symbol": symbol,
        "name": name,
        "signal": signal,
        "close": float(price_str),
        "ma60": float(ma60_str),
        "market": market,
        "change": 0.0,
        "vol_ratio": 1.2,
        "tactic": "正規軍穩健架構" if signal != "禁區" else "空頭禁區：建議觀望",
        "plan": {
            "entry": float(price_str),
            "sl": float(ma60_str),
            "tp": round(float(price_str) * 1.2, 2)
        }
    })
    i += 7

# Load existing TW stocks to merge or just use this new list
# Given the user's input, they probably want to REPLACE the US list but KEEP the TW list
# I'll read current scan_results.json and merge

try:
    with open('scan_results.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
        existing_stocks = existing_data.get('stocks', [])
except:
    existing_stocks = []

# Filter out old US stocks and the specific TW stocks in the new list to avoid duplicates
new_symbols = {s['symbol'] for s in stocks}
merged_stocks = stocks + [s for s in existing_stocks if s['symbol'] not in new_symbols]

# Sort
merged_stocks.sort(key=lambda x: (x['market'] != 'us', x['symbol']))

scan_results = {
    "stocks": merged_stocks,
    "last_updated": "2026-05-15 08:38"
}

# Write to frontend/public so it gets built and deployed
output_path = os.path.join('frontend', 'public', 'scan_results.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(scan_results, f, ensure_ascii=False, indent=2)

print(f"Successfully updated {output_path} with {len(merged_stocks)} stocks.")


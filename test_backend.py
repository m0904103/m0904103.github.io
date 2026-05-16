# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'c:\Users\manpo\OneDrive\桌面\m0904103_github_io')
from app import fetch_stock, fetch_index

# Test TW
r = fetch_stock('2330.TW')
print(f"2330 name={r['name']} price={r['price']} ma60={r['ma60']} rsi={r['rsi']}")
print(f"     entry={r['entry']} stop={r['stop']} target={r['target']}")
print(f"     is_regular={r['is_regular']} advice={r['advice']}")

r2 = fetch_stock('NVDA')
print(f"NVDA name={r2['name']} price={r2['price']} rvol={r2['rvol']} rsi={r2['rsi']}")
print(f"     entry={r2['entry']} stop={r2['stop']} target={r2['target']}")

# Test index
idx = fetch_index('^TWII')
print(f"TWII: {idx}")

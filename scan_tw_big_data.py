import json
import os
import yfinance as yf
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

DATA_FILE = os.path.join('frontend', 'public', 'scan_results.json')

def check_three_rates(ticker_obj):
    # Try to get quarterly financials
    # We need Gross Margin, Operating Margin, Net Margin YoY
    try:
        q_fin = ticker_obj.quarterly_financials
        if q_fin is None or q_fin.empty or len(q_fin.columns) < 5:
            return False
            
        latest = q_fin.iloc[:, 0]
        last_yr = q_fin.iloc[:, 4]
        
        def get_margin(fin_col):
            rev = fin_col.get('Total Revenue') or fin_col.get('Operating Revenue')
            if not rev: return None, None, None
            gross = fin_col.get('Gross Profit')
            op = fin_col.get('Operating Income')
            net = fin_col.get('Net Income')
            
            gm = gross / rev if gross else 0
            om = op / rev if op else 0
            nm = net / rev if net else 0
            return gm, om, nm

        gm0, om0, nm0 = get_margin(latest)
        gm1, om1, nm1 = get_margin(last_yr)
        
        if None in (gm0, gm1): return False
        
        # Check if three rates are rising YoY
        return bool((gm0 > gm1) and (om0 > om1) and (nm0 > nm1))
    except Exception as e:
        return False

def check_technicals(df):
    try:
        if len(df) < 20:
            return False, False
            
        # Bollinger Bands
        df['MA20'] = df['Close'].rolling(20).mean()
        df['STD20'] = df['Close'].rolling(20).std()
        df['LowerBand'] = df['MA20'] - (2 * df['STD20'])
        
        # KD Stochastic
        df['L9'] = df['Low'].rolling(9).min()
        df['H9'] = df['High'].rolling(9).max()
        df['RSV'] = 100 * (df['Close'] - df['L9']) / (df['H9'] - df['L9'])
        df['K'] = df['RSV'].ewm(com=2, adjust=False).mean()
        df['D'] = df['K'].ewm(com=2, adjust=False).mean()
        
        latest = df.iloc[-1]
        
        # Check if touching lower band
        bb_lower_touch = bool(latest['Low'] <= latest['LowerBand'] * 1.01)
        # Check if KD < 30 and K > D (golden cross approaching or happened)
        kd_cross_up = bool(latest['K'] < 30 and latest['K'] > latest['D'])
        
        return bb_lower_touch, kd_cross_up
    except Exception:
        return False, False

import sys
sys.stdout.reconfigure(encoding='utf-8')

def run_scan():
    print("Starting Uncle Tsun's Big Data Engine for TW Stocks...")
    
    if not os.path.exists(DATA_FILE):
        print("Error: scan_results.json not found!")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    updated_count = 0
    for stock in data.get('stocks', []):
        if stock.get('market') != 'tw':
            continue
            
        sym = stock['symbol']
        print(f"  - Scanning {sym} ({stock.get('name')})...", end="", flush=True)
        
        ticker = yf.Ticker(sym)
        df = ticker.history(period='6mo')
        
        if df.empty:
            if sym.endswith('.TW'):
                sym_two = sym.replace('.TW', '.TWO')
                ticker = yf.Ticker(sym_two)
                df = ticker.history(period='6mo')
            if df.empty:
                print(" [FAILED: No Data]")
                continue
            
        # 1. Fundamentals (Three Rates)
        three_rates = check_three_rates(ticker)
        
        # 2. Technicals (BB & KD)
        bb_lower, kd_cross = check_technicals(df)
        
        # 3. Mock Chips (Since TWSE API blocked, mock based on volume momentum)
        try:
            df['Vol_MA5'] = df['Volume'].rolling(5).mean()
            is_foreign_buying = bool(df['Close'].iloc[-1] > df['Close'].rolling(5).mean().iloc[-1] and df['Volume'].iloc[-1] > df['Vol_MA5'].iloc[-1])
            margin_surge = bool(df['Volume'].iloc[-1] > df['Vol_MA5'].iloc[-1] * 2 and df['Close'].iloc[-1] < df['Close'].iloc[-2])
        except Exception:
            is_foreign_buying = False
            margin_surge = False
            
        stock['fundamentals'] = {
            "three_rates_rising": three_rates
        }
        stock['technicals'] = {
            "bb_lower_touch": bb_lower,
            "kd_cross_up": kd_cross
        }
        stock['chips'] = {
            "foreign_buy": is_foreign_buying,
            "margin_surge": margin_surge
        }
        
        updated_count += 1
        print(" [OK]")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nBig Data Scan Complete! Processed {updated_count} TW stocks.")

if __name__ == "__main__":
    run_scan()

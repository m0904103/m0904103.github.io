"""
阿村伯底部型態偵測引擎 — Pattern Detector
偵測：W底（雙底）、三重底、ABC修正浪
作者：正規軍量化終端
"""
import numpy as np

def find_local_lows(closes, window=5):
    lows = []
    for i in range(window, len(closes) - window):
        window_slice = closes[i - window:i + window + 1]
        if closes[i] == min(window_slice):
            lows.append((i, closes[i]))
    return lows

def find_local_highs(closes, window=5):
    highs = []
    for i in range(window, len(closes) - window):
        window_slice = closes[i - window:i + window + 1]
        if closes[i] == max(window_slice):
            highs.append((i, closes[i]))
    return highs

def detect_w_bottom(closes, tolerance=0.03):
    if len(closes) < 30: return None
    lows = find_local_lows(closes, window=5)
    highs = find_local_highs(closes, window=5)
    if len(lows) < 2: return None
    recent_lows = [(i, p) for i, p in lows if i > len(closes) - 80]
    for j in range(len(recent_lows) - 1):
        idx1, price1 = recent_lows[j]
        idx2, price2 = recent_lows[j + 1]
        if idx2 - idx1 < 10: continue
        if abs(price1 - price2) / price1 > tolerance: continue
        if price2 < price1 * (1 - tolerance): continue
        between_highs = [(i, p) for i, p in highs if idx1 < i < idx2]
        if not between_highs: continue
        neckline = max(p for _, p in between_highs)
        current_price = closes[-1]
        if current_price >= neckline * 0.98:
            breakthrough_pct = (current_price - neckline) / neckline * 100
            low_price = min(price1, price2)
            target = neckline + (neckline - low_price)
            return {
                "pattern": "W底",
                "pattern_en": "W_BOTTOM",
                "neckline": round(neckline, 2),
                "support": round(low_price, 2),
                "target": round(target, 2),
                "breakthrough_pct": round(breakthrough_pct, 2),
                "bottom1_price": round(price1, 2),
                "bottom2_price": round(price2, 2),
                "days_formed": len(closes) - idx1,
                "strength": "strong" if current_price > neckline else "forming"
            }
    return None

def detect_triple_bottom(closes, tolerance=0.04):
    if len(closes) < 40: return None
    lows = find_local_lows(closes, window=5)
    recent_lows = [(i, p) for i, p in lows if i > len(closes) - 100]
    if len(recent_lows) < 3: return None
    for k in range(len(recent_lows) - 2):
        idx1, price1 = recent_lows[k]
        idx2, price2 = recent_lows[k + 1]
        idx3, price3 = recent_lows[k + 2]
        if idx2 - idx1 < 8 or idx3 - idx2 < 8: continue
        avg_bottom = (price1 + price2 + price3) / 3
        if any(abs(p - avg_bottom) / avg_bottom > tolerance for p in [price1, price2, price3]): continue
        highs = find_local_highs(closes, window=5)
        between_highs = [(i, p) for i, p in highs if idx1 < i < idx3]
        if not between_highs: continue
        neckline = max(p for _, p in between_highs)
        current_price = closes[-1]
        if current_price >= avg_bottom and idx3 > len(closes) - 30:
            support = min(price1, price2, price3)
            target = neckline + (neckline - support)
            return {
                "pattern": "三重底",
                "pattern_en": "TRIPLE_BOTTOM",
                "neckline": round(neckline, 2),
                "support": round(support, 2),
                "target": round(target, 2),
                "avg_bottom": round(avg_bottom, 2),
                "days_formed": len(closes) - idx1,
                "strength": "strong" if current_price > neckline else "forming"
            }
    return None

def detect_abc_wave(closes, highs_prices=None, lows_prices=None, tolerance=0.05):
    if len(closes) < 50: return None
    highs = find_local_highs(closes, window=7)
    lows = find_local_lows(closes, window=7)
    recent_highs = [(i, p) for i, p in highs if i > len(closes) - 100]
    recent_lows = [(i, p) for i, p in lows if i > len(closes) - 100]
    if not recent_highs or len(recent_lows) < 2: return None
    wave_top_idx, wave_top_price = max(recent_highs, key=lambda x: x[1])
    a_lows = [(i, p) for i, p in recent_lows if i > wave_top_idx]
    if not a_lows: return None
    a_bottom_idx, a_bottom_price = min(a_lows, key=lambda x: x[1])
    a_wave_drop = (wave_top_price - a_bottom_price) / wave_top_price
    if a_wave_drop < 0.15: return None
    b_highs = [(i, p) for i, p in recent_highs if i > a_bottom_idx]
    if not b_highs: return None
    b_top_idx, b_top_price = max(b_highs, key=lambda x: x[1])
    b_rebound_pct = (b_top_price - a_bottom_price) / (wave_top_price - a_bottom_price)
    if not (0.30 <= b_rebound_pct <= 0.70): return None
    c_lows = [(i, p) for i, p in recent_lows if i > b_top_idx]
    current_price = closes[-1]
    if c_lows:
        c_bottom_idx, c_bottom_price = min(c_lows, key=lambda x: x[1])
        c_wave_drop = (b_top_price - c_bottom_price) / b_top_price
        is_near_bottom = (c_wave_drop >= 0.10 and c_bottom_idx > len(closes) - 20 and current_price <= c_bottom_price * 1.05)
        if is_near_bottom:
            fib_target_50 = round(a_bottom_price + (wave_top_price - a_bottom_price) * 0.50, 2)
            fib_target_618 = round(a_bottom_price + (wave_top_price - a_bottom_price) * 0.618, 2)
            return {
                "pattern": "ABC底部",
                "pattern_en": "ABC_BOTTOM",
                "wave_top": round(wave_top_price, 2),
                "a_bottom": round(a_bottom_price, 2),
                "b_top": round(b_top_price, 2),
                "c_bottom": round(c_bottom_price, 2),
                "a_drop_pct": round(a_wave_drop * 100, 1),
                "b_rebound_pct": round(b_rebound_pct * 100, 1),
                "fib_target_50": fib_target_50,
                "fib_target_618": fib_target_618,
                "support": round(c_bottom_price, 2),
                "days_formed": len(closes) - wave_top_idx,
                "strength": "strong"
            }
    else:
        c_current_drop = (b_top_price - current_price) / b_top_price
        if c_current_drop >= 0.05:
            est_c_bottom = round(a_bottom_price * (1 - 0.02), 2)
            return {
                "pattern": "ABC下跌中",
                "pattern_en": "ABC_FALLING",
                "wave_top": round(wave_top_price, 2),
                "a_bottom": round(a_bottom_price, 2),
                "b_top": round(b_top_price, 2),
                "a_drop_pct": round(a_wave_drop * 100, 1),
                "b_rebound_pct": round(b_rebound_pct * 100, 1),
                "estimated_c_bottom": est_c_bottom,
                "warning": "C波進行中，尚未見底，請勿抄底！",
                "days_formed": len(closes) - wave_top_idx,
                "strength": "warning"
            }
    return None

def analyze_patterns(df):
    if df is None or len(df) < 30: return {}
    closes = list(df['Close'].astype(float))
    results = {}
    w_bottom = detect_w_bottom(closes)
    if w_bottom: results['w_bottom'] = w_bottom
    triple = detect_triple_bottom(closes)
    if triple: results['triple_bottom'] = triple
    abc = detect_abc_wave(closes)
    if abc: results['abc_wave'] = abc
    
    strength_score = 0
    signals = []
    if 'w_bottom' in results:
        if results['w_bottom']['strength'] == 'strong':
            strength_score += 3
            signals.append('W底突破')
        else:
            strength_score += 1
            signals.append('W底形成中')
    if 'triple_bottom' in results:
        if results['triple_bottom']['strength'] == 'strong':
            strength_score += 4
            signals.append('三重底突破')
        else:
            strength_score += 2
            signals.append('三重底形成中')
    if 'abc_wave' in results:
        if results['abc_wave']['pattern_en'] == 'ABC_BOTTOM':
            strength_score += 3
            signals.append('ABC底部完成')
        elif results['abc_wave']['pattern_en'] == 'ABC_FALLING':
            strength_score -= 2
            signals.append('⚠️C波下跌中')
            
    if signals:
        results['summary'] = {
            'score': strength_score,
            'signals': signals,
            'verdict': (
                '🔥 強力底部訊號' if strength_score >= 5 else
                '✅ 底部型態確認' if strength_score >= 3 else
                '🟡 底部形成中' if strength_score >= 1 else
                '⚠️ 下跌未止'
            )
        }
    return results

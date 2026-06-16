import json

def analyze():
    try:
        with open('trading/scan_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print("Error reading json")
        return

    indices = data.get('indices', {})
    oi = data.get('taifex_oi', 0)
    
    print("=== 盤勢數據 ===")
    print(f"外資未平倉 (OI): {oi}")
    for k, v in indices.items():
        print(f"{k}: {v.get('close')}")
        
    stocks = data.get('stocks', [])
    
    tw_candidates = []
    us_candidates = []
    
    for s in stocks:
        if not s.get('is_regular'): continue
        if s.get('signal') not in ['Strong Buy', 'Buy']: continue
        
        score = 0
        reasons = []
        
        # 顏老師 (Fundamentals / MA)
        if s.get('fundamentals', {}).get('three_rates_rising'):
            score += 2
            reasons.append("三率三升")
        if s.get('vol_surge'):
            score += 1
            reasons.append("爆量突破")
            
        # 阿村伯 (Patterns)
        patterns = s.get('patterns', {})
        if patterns.get('w_bottom'):
            score += 3
            reasons.append("W底型態")
        if patterns.get('triple_bottom'):
            score += 3
            reasons.append("三重底")
        if s.get('k_pattern'):
            score += 1
            reasons.append(s.get('k_pattern'))
            
        if score >= 2:
            info = f"{s.get('symbol')} {s.get('name')} (價:{s.get('close')} | {s.get('sector')}) - 理由: {', '.join(reasons)}"
            if s.get('market') == 'tw':
                tw_candidates.append((score, info))
            else:
                us_candidates.append((score, info))
                
    tw_candidates.sort(reverse=True)
    us_candidates.sort(reverse=True)
    
    print("\n=== 台股推薦 (前5名) ===")
    for score, info in tw_candidates[:5]:
        print(info)
        
    print("\n=== 美股推薦 (前5名) ===")
    for score, info in us_candidates[:5]:
        print(info)

if __name__ == '__main__':
    analyze()

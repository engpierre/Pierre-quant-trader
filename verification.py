import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')

def calculate_validity_score(candidate):
    score = 0
    reasoning = []
    breakdown = {"Scout": 0, "Sentiment": 0, "Insider": 0, "Mechanics": 0, "NVIDIA AI-Q": 0}

    # 1. Scout Baseline
    score += 15
    breakdown["Scout"] = 15
    reasoning.append("Scout Protocol: +15% (Baseline Liquidity & 200-MA Structure Met)")

    # 2. Sentiment Context
    sent = candidate.get('sentiment', {})
    if sent.get('runner_potential'):
        score += 20
        breakdown["Sentiment"] += 20
        reasoning.append("[+] Sentiment: Identified as a high-velocity 'Runner' (+20%)")
    if sent.get('exhaustion_risk'):
        score -= 20
        breakdown["Sentiment"] -= 20
        reasoning.append("[-] Sentiment: Heavy exhaustion risk / Retail fatigue (-20%)")
        
    hype_addition = min(int(sent.get('hype_score', 0)), 15)
    if hype_addition > 0:
        score += hype_addition
        breakdown["Sentiment"] += hype_addition
        reasoning.append(f"[+] Sentiment: Favorable retail engagement allocation relative to technical base (+{hype_addition}%)")
        
    # Phase 1.5: Technical
    if candidate.get('technical_audit', {}).get('obv_trend') == 'Accumulation':
        score += 15
        breakdown["Mechanics"] += 15
        reasoning.append("OBV Structure: +15% (Institutional Accumulation)")
        
    # Phase 1.8: Market Intelligence
    aiq_mod = candidate.get('intelligence_audit', {}).get('aiq_conviction_modifier', 0)
    score += aiq_mod
    breakdown["NVIDIA AI-Q"] += aiq_mod
    if aiq_mod > 0:
        reasoning.append(f"AI-Q Fundament (NVIDIA RAG Bridge): +{aiq_mod}% (Strong Context)")
    elif aiq_mod < 0:
        reasoning.append(f"AI-Q Fundament (NVIDIA RAG Bridge): {aiq_mod}% (Weak Context)")
        
    # 3. Insider Integrity
    insider = candidate.get('insider_audit', {})
    if insider.get('red_flag'):
        score -= 30
        breakdown["Insider"] -= 30
        reasoning.append("[-] Insider Risk: Major executive sell-off divergence detected (-30%)")
    elif insider.get('recent_ceo_cfo_buy'):
        score += 15
        breakdown["Insider"] += 15
        reasoning.append("[+] Insider Integrity: Net cluster purchases by CEO/CFO (+15%)")
    else:
        score += 10
        breakdown["Insider"] += 10
        reasoning.append("[~] Insider Baseline: +10% (Neutral stance. No critical executive dumping detected)")
        
    final_score = min(max(score, 0), 100)
    return final_score, reasoning, breakdown

def generate_verification_report():
    input_file = 'intelligence_candidates.json'
    try:
        with open(input_file, 'r') as f:
            candidates = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load {input_file}. Ensure previous Agent executed successfully.")
        return
        
    verified_candidates = []
    
    logging.info(f"Verification Agent analyzing {len(candidates)} fully mapped candidates...")
    
    for c in candidates:
        score, reasons, breakdown = calculate_validity_score(c)
        c['verification_audit'] = {
            'validity_score': score,
            'reasoning': reasons,
            'breakdown': breakdown
        }
        
        logging.info(f"\n➔ Diagnostics Breakdown for {c['symbol']} | Validity FCS: {score}%")
        for r in reasons:
            logging.info(f"    {r}")

        verified_candidates.append(c)
        
    # Order candidates analytically by strongest score
    verified_candidates = sorted(verified_candidates, key=lambda x: x.get('verification_audit', {}).get('validity_score', 0), reverse=True)

    report_lines = []
    report_lines.append("# Final Pipeline Signal Matrix\n")
    report_lines.append(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append("---\n")
    
    top_tier = [c for c in verified_candidates if c['verification_audit']['validity_score'] >= 75]
    watchlist = [c for c in verified_candidates if 60 <= c['verification_audit']['validity_score'] < 75]
    
    report_lines.append("## 🏆 Executable Top Tier (FCS > 75%)")
    if not top_tier:
         report_lines.append("*No assets met the strict conviction criteria.*")
    else:
         for c in top_tier:
             score = c['verification_audit']['validity_score']
             ticker = c['symbol']
             price = c['price']
             report_lines.append(f"### 🟩 {ticker} | Validity Score: {score}% | Market Price: ${price}")
             for r in c['verification_audit']['reasoning']:
                 report_lines.append(f"- {r}")
             report_lines.append("")

    report_lines.append("## 🔎 Secondary Watchlist (FCS 60% - 74%)")
    if not watchlist:
        report_lines.append("*No secondary watchlist candidates.*")
    else:
        for c in watchlist:
            score = c['verification_audit']['validity_score']
            ticker = c['symbol']
            report_lines.append(f"- **{ticker}** ({score}%) - Sentiment Catalyst: {c.get('sentiment', {}).get('narrative', 'N/A')}")
            
    with open('Signal_Report.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))

    with open('verified_candidates.json', 'w') as f:
        json.dump(verified_candidates, f, indent=4)

    logging.info("\n--- VERIFICATION AUDIT COMPLETE ---")
    logging.info(f"Signal_Report.md generated seamlessly. Executable Top Tiers (FCS > 75%): {len(top_tier)}")

if __name__ == "__main__":
    generate_verification_report()

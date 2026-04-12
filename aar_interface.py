import sqlite3

def get_agent_performance():
    """
    Queries the AAR Ledger to calculate win-rates per agent.
    Formula: T_c = (Successes / Total_Trials) * Regime_Stability_Factor
    """
    conn = sqlite3.connect('antigravity_aar.db')
    cursor = conn.cursor()
    
    # Extracting the last 50 outcomes to weight recent performance higher
    cursor.execute("""
        SELECT agent_name, status, regime 
        FROM mission_logs 
        ORDER BY timestamp DESC LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()

    performance_map = {}
    for agent, status, regime in rows:
        if agent not in performance_map:
            performance_map[agent] = {"wins": 0, "total": 0}
        performance_map[agent]["total"] += 1
        if status == "SUCCESS":
            performance_map[agent]["wins"] += 1
            
    # Calculate Trust Coefficient
    trust_scores = {k: v["wins"]/v["total"] for k, v in performance_map.items() if v["total"] > 0}
    return trust_scores

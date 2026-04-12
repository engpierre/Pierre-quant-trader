import sqlite3
from datetime import datetime, timedelta

def seed_database():
    conn = sqlite3.connect('antigravity_aar.db')
    cursor = conn.cursor()

    # Drop existing out-dated schema table if it conflicts with Phase 5
    cursor.execute('DROP TABLE IF EXISTS mission_logs')

    # Create table if it doesn't exist (matching your AAR Interface logic)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mission_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT,
            status TEXT,
            regime TEXT,
            timestamp DATETIME
        )
    ''')

    # Scenario Data: 
    # We want the 'Technical' agent to be reliable in Bull markets 
    # but 'Whale' and 'Geopolitical' to have some failures in Volatile regimes.
    scenarios = [
        # Technical Agent: Reliable Bullish Performer
        ("Technical", "SUCCESS", "Trending-Bull"),
        ("Technical", "SUCCESS", "Trending-Bull"),
        ("Technical", "FAILURE", "Volatile-Bear"),
        
        # Whale Agent: Heavy hitter, but prone to false flags
        ("Whale", "SUCCESS", "Trending-Bull"),
        ("Whale", "FAILURE", "Volatile-Bear"),
        ("Whale", "FAILURE", "Volatile-Bear"),

        # Geopolitical Agent: High-Value but High-Variance
        ("Geopolitical", "SUCCESS", "Volatile-Bear"),
        ("Geopolitical", "FAILURE", "Trending-Bull"),
        
        # Blackwell Critic: The baseline for your Red Team
        ("Critic", "SUCCESS", "Volatile-Bear"),
        ("Critic", "SUCCESS", "Trending-Bull")
    ]

    print("Seeding AAR Ledger with historical ground truth...")
    
    for i in range(5):  # Loop to create 50 randomized entries based on scenarios
        for agent, status, regime in scenarios:
            timestamp = datetime.now() - timedelta(days=i, hours=i)
            cursor.execute('''
                INSERT INTO mission_logs (agent_name, status, regime, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (agent, status, regime, timestamp))

    conn.commit()
    conn.close()
    print("Database seeding complete. Trust Coefficients are now calculable.")

if __name__ == "__main__":
    seed_database()

# CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
import os
from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
DB_PATH = "pierre_quant.db"

def init_db():
    """Initializes the local database to store multi-asset matrix structures."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_matrices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            timestamp TEXT,
            window_size INTEGER,
            prices TEXT,
            volumes TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/matrix-webhook', methods=['POST'])
def webhook_receiver():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "ERROR", "message": "Empty payload"}), 400
        
        ticker = data.get("ticker")
        window_size = data.get("window_size")
        # Store arrays as compressed JSON text strings in SQLite
        prices_str = json.dumps(data.get("prices", []))
        volumes_str = json.dumps(data.get("volumes", []))
        timestamp = datetime.now().isoformat()

        # Insert matrix row into the local database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO market_matrices (ticker, timestamp, window_size, prices, volumes)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticker, timestamp, window_size, prices_str, volumes_str))
        conn.commit()
        conn.close()

        print(f"[CATCH] Successfully archived 4H matrix for {ticker} into database.")
        return jsonify({"status": "SUCCESS"}), 200

    except Exception as e:
        print(f"[ERROR] Failed to ingest matrix: {str(e)}")
        return jsonify({"status": "ERROR", "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    # Runs locally on port 5000
    print("Starting Matrix Webhook Receiver on Port 5000...")
    app.run(host='0.0.0.0', port=5000)

import sqlite3
import json
import os

def export():
    conn = sqlite3.connect("data/markets.db")
    conn.row_factory = sqlite3.Row
    
    # 1. Export Markets Summary (those with metrics)
    markets = conn.execute("""
        SELECT question, outcome_name, smart_money_win_rate, volume_usd, condition_id 
        FROM active_market_outcomes 
        WHERE smart_money_win_rate IS NOT NULL
        ORDER BY smart_money_win_rate DESC
    """).fetchall()
    
    with open("test_data/markets_summary.json", "w") as f:
        json.dump([dict(m) for m in markets], f, indent=2)
        
    # 2. Export Holders for the Top market
    if markets:
        top_cid = markets[0]["condition_id"]
        holders = conn.execute("""
            SELECT h.wallet_address, h.position_size, h.outcome_index, ws.total_pnl
            FROM holders h
            LEFT JOIN wallets_stats ws ON h.wallet_address = ws.wallet_address
            WHERE h.market_id = ?
            ORDER BY h.position_size DESC
        """, (top_cid,)).fetchall()
        
        with open("test_data/top_market_holders.json", "w") as f:
            json.dump({
                "market_question": markets[0]["question"],
                "holders": [dict(h) for h in holders]
            }, f, indent=2)

    conn.close()
    print("Export complete. Files in test_data/")

if __name__ == "__main__":
    export()

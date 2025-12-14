import sqlite3
import os
import sys
import time
import datetime
import ast
from typing import Dict, Any

# Import local client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gamma_client import MarketFetcher

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "markets.db")

def setup_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    # Enable WAL mode for better concurrency (Reader doesn't block Writer)
    conn.execute("PRAGMA journal_mode=WAL;")
    
    cursor = conn.cursor()
    
    # Drop tables for clean snapshot
    cursor.execute('DROP TABLE IF EXISTS active_market_outcomes')
    cursor.execute('DROP TABLE IF EXISTS market_tags')
    
    # Create Tables
    cursor.execute('''
        CREATE TABLE active_market_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_at TEXT,
            market_id TEXT,
            event_slug TEXT,
            question TEXT,
            url TEXT,
            outcome_name TEXT,
            price REAL,
            apr REAL,
            spread REAL,
            volume_usd REAL,
            liquidity_usd REAL,
            start_date TEXT,
            end_date TEXT,
            category TEXT,
            icon_url TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE market_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_at TEXT,
            market_id TEXT,
            tag_label TEXT
        )
    ''')
    
    conn.commit()
    return conn

def run_scrape():
    start_total = time.time()
    print(f"[{datetime.datetime.now()}] Starting Scrape...")
    
    fetcher = MarketFetcher()
    
    # 1. Fetch Events (for Tags & Icons)
    t0 = time.time()
    raw_events = fetcher.fetch_all_events()
    
    # Build Map
    events_map = {}
    for ev in raw_events:
        e_id = str(ev.get("id"))
        slug = ev.get("slug") or ""
        icon = ev.get("icon") or ev.get("image") or ""
        
        tags = []
        if isinstance(ev.get("tags"), list):
            tags = [t.get("label") for t in ev.get("tags") if t.get("label")]
            
        events_map[e_id] = {"slug": slug, "tags": tags, "icon": icon}
        
    print(f"Events: {len(raw_events)} (took {time.time()-t0:.2f}s)")
    
    # 2. Fetch Markets
    t0 = time.time()
    raw_markets = fetcher.fetch_all_markets()
    print(f"Markets: {len(raw_markets)} (took {time.time()-t0:.2f}s)")
    
    # 3. Process & Store
    conn = setup_db()
    cursor = conn.cursor()
    snapshot_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    count_outcomes = 0
    count_tags = 0
    
    for m in raw_markets:
        m_id = str(m.get("id"))
        question = m.get("question") or ""
        
        # Resolve Event Info
        event_slug = ""
        icon_url = ""
        tag_labels = []
        
        # Find Event ID from nested events list
        m_events = m.get("events")
        if m_events and isinstance(m_events, list) and len(m_events) > 0:
            e_id = str(m_events[0].get("id"))
            if e_id in events_map:
                info = events_map[e_id]
                event_slug = info["slug"]
                icon_url = info["icon"]
                tag_labels = info["tags"]
            else:
                # Fallback to nested data
                event_slug = m_events[0].get("slug") or ""
                icon_url = m_events[0].get("icon") or m_events[0].get("image") or ""
        
        # Fallback 2
        if not event_slug: event_slug = m.get("slug") or ""
        if not icon_url: icon_url = m.get("icon") or m.get("image") or ""
        
        url = f"https://polymarket.com/event/{event_slug}" if event_slug else ""
        primary_category = tag_labels[0] if tag_labels else ""
        
        # Save Tags
        for t in tag_labels:
            cursor.execute("INSERT INTO market_tags (snapshot_at, market_id, tag_label) VALUES (?,?,?)", 
                           (snapshot_at, m_id, t))
            count_tags += 1
            
        # Outcomes
        outcomes = m.get("outcomes")
        prices = m.get("outcomePrices")
        
        # Parsing stringified JSON if needed (sometimes API returns strings)
        if isinstance(outcomes, str):
            try: outcomes = ast.literal_eval(outcomes)
            except: outcomes = [outcomes]
        if isinstance(prices, str):
            try: prices = ast.literal_eval(prices)
            except: prices = []
            
        if not isinstance(outcomes, list): outcomes = []
        if not isinstance(prices, list): prices = []
        
        for i, outcome_name in enumerate(outcomes):
            price = 0.0
            if i < len(prices):
                try: price = float(prices[i])
                except: pass

            apr = None
            try:
                end_s = (m.get("endDate") or "").strip()
                if end_s.endswith("Z"):
                    end_s = end_s[:-1] + "+00:00"
                end_dt = datetime.datetime.fromisoformat(end_s) if end_s else None
                snap_dt = datetime.datetime.fromisoformat(snapshot_at)
                if (
                    end_dt is not None
                    and end_dt.tzinfo is not None
                    and snap_dt.tzinfo is not None
                    and price is not None
                    and price > 0.0
                    and price < 1.0
                ):
                    days = (end_dt - snap_dt).total_seconds() / 86400.0
                    if days > 0.0:
                        roi = (1.0 / float(price)) - 1.0
                        apr_val = roi * (365.0 / days)
                        if apr_val > 0.0 and apr_val != float("inf"):
                            apr = float(apr_val)
            except Exception:
                apr = None
            
            cursor.execute('''
                INSERT INTO active_market_outcomes (
                    snapshot_at, market_id, event_slug, question, url, outcome_name, 
                    price, apr, spread, volume_usd, liquidity_usd, start_date, end_date, 
                    category, icon_url
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                snapshot_at, m_id, event_slug, question, url, str(outcome_name),
                price, apr, float(m.get("spread") or 0), float(m.get("volume") or 0), float(m.get("liquidity") or 0),
                m.get("startDate"), m.get("endDate"), primary_category, icon_url
            ))
            count_outcomes += 1
            
    conn.commit()

    # Re-create indices after refresh (tables are dropped each run)
    conn.executescript("""
        CREATE INDEX IF NOT EXISTS idx_market_tags_label ON market_tags(tag_label);
        CREATE INDEX IF NOT EXISTS idx_market_tags_market_id ON market_tags(market_id);
        CREATE INDEX IF NOT EXISTS idx_amo_market_id ON active_market_outcomes(market_id);
        CREATE INDEX IF NOT EXISTS idx_amo_volume ON active_market_outcomes(volume_usd DESC);
        CREATE INDEX IF NOT EXISTS idx_amo_end_date ON active_market_outcomes(end_date);
        CREATE INDEX IF NOT EXISTS idx_amo_price ON active_market_outcomes(price);
        CREATE INDEX IF NOT EXISTS idx_amo_spread ON active_market_outcomes(spread);
        CREATE INDEX IF NOT EXISTS idx_amo_liquidity ON active_market_outcomes(liquidity_usd);
        CREATE INDEX IF NOT EXISTS idx_amo_apr ON active_market_outcomes(apr);
        CREATE INDEX IF NOT EXISTS idx_amo_question ON active_market_outcomes(question);
        CREATE INDEX IF NOT EXISTS idx_amo_outcome ON active_market_outcomes(outcome_name);
        ANALYZE;
    """)
    conn.commit()
    conn.close()
    
    print(f"Saved: {count_outcomes} outcomes, {count_tags} tags.")
    print(f"Total Time: {time.time() - start_total:.2f}s")

if __name__ == "__main__":
    run_scrape()

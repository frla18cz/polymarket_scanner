import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:3000",
    "https://your-vercel-app.vercel.app",  # Add your Vercel domain here
    "*" # Allow all for development convenience
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "markets.db")

class TagStats(BaseModel):
    tag_label: str
    count: int

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_indices():
    """Create indices and enable WAL mode for performance."""
    conn = get_db_connection()
    try:
        # Enable Write-Ahead Logging (allows simultaneous read/write)
        conn.execute("PRAGMA journal_mode=WAL;")
        
        conn.executescript("""
            CREATE INDEX IF NOT EXISTS idx_market_tags_label ON market_tags(tag_label);
            CREATE INDEX IF NOT EXISTS idx_market_tags_market_id ON market_tags(market_id);
            CREATE INDEX IF NOT EXISTS idx_amo_market_id ON active_market_outcomes(market_id);
            CREATE INDEX IF NOT EXISTS idx_amo_volume ON active_market_outcomes(volume_usd DESC);
            CREATE INDEX IF NOT EXISTS idx_amo_end_date ON active_market_outcomes(end_date);
            
            -- Missing indices for sliders (Critical for performance)
            CREATE INDEX IF NOT EXISTS idx_amo_price ON active_market_outcomes(price);
            CREATE INDEX IF NOT EXISTS idx_amo_spread ON active_market_outcomes(spread);
            CREATE INDEX IF NOT EXISTS idx_amo_liquidity ON active_market_outcomes(liquidity_usd);
            
            ANALYZE;
        """)
        conn.commit()
        print("DEBUG: Database WAL mode enabled and indices verified.")
    except Exception as e:
        print(f"WARNING: Failed to optimize DB: {e}")
    finally:
        conn.close()

@app.get("/api/tags", response_model=List[TagStats])
def get_tags():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT tag_label, COUNT(*) as count FROM market_tags GROUP BY tag_label ORDER BY count DESC"
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [{"tag_label": r["tag_label"], "count": r["count"]} for r in rows]

@app.get("/api/status")
def get_status(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        row = cursor.execute("SELECT MAX(snapshot_at) as last_updated FROM active_market_outcomes").fetchone()
        last_updated = row["last_updated"] if row else None
    except:
        last_updated = None
    conn.close()
    return {"last_updated": last_updated}

@app.get("/api/markets")
def get_markets(
    response: Response,
    included_tags: Optional[List[str]] = Query(None),
    excluded_tags: Optional[List[str]] = Query(None),
    sort_by: str = "volume_usd",
    sort_dir: str = "desc",
    limit: int = 100,
    offset: int = 0,
    min_volume: Optional[float] = 0,
        min_liquidity: Optional[float] = 0,
    min_price: Optional[float] = 0.0,
    max_price: Optional[float] = 1.0,
    max_spread: Optional[float] = None,
    max_hours_to_expire: Optional[int] = None,
    include_expired: bool = True,
    search: Optional[str] = None
):
    print(f"DEBUG: get_markets called with included_tags={included_tags}, excluded_tags={excluded_tags}")
    
    # Handle comma-separated tags (proxy fix)
    if included_tags and len(included_tags) == 1 and "," in included_tags[0]:
        included_tags = included_tags[0].split(",")
        print(f"DEBUG: Parsed comma-separated included_tags: {included_tags}")

    if excluded_tags and len(excluded_tags) == 1 and "," in excluded_tags[0]:
        excluded_tags = excluded_tags[0].split(",")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Disable caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    where_clauses = ["1=1"]
    params = []
    
    if min_volume:
        where_clauses.append("volume_usd >= ?")
        params.append(min_volume)
        
    if min_liquidity:
        where_clauses.append("liquidity_usd >= ?")
        params.append(min_liquidity)

    if min_price is not None:
        where_clauses.append("price >= ?")
        params.append(min_price)
    
    if max_price is not None:
        where_clauses.append("price <= ?")
        params.append(max_price)

    if max_spread is not None:
        where_clauses.append("spread <= ?")
        params.append(max_spread)

    if search:
        where_clauses.append("(question LIKE ? OR outcome_name LIKE ?)")
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    if max_hours_to_expire is not None:
        cutoff_dt = datetime.utcnow() + timedelta(hours=max_hours_to_expire)
        cutoff_str = cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        where_clauses.append("datetime(end_date) <= datetime(?)")
        params.append(cutoff_str)
        
        if not include_expired:
            now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            where_clauses.append("datetime(end_date) >= datetime(?)")
            params.append(now_str)

    # Tag Logic
    if included_tags:
        placeholders = ",".join("?" * len(included_tags))
        where_clauses.append(f"EXISTS (SELECT 1 FROM market_tags t WHERE t.market_id = active_market_outcomes.market_id AND t.tag_label IN ({placeholders}))")
        params.extend(included_tags)

    if excluded_tags:
        placeholders = ",".join("?" * len(excluded_tags))
        where_clauses.append(f"NOT EXISTS (SELECT 1 FROM market_tags t WHERE t.market_id = active_market_outcomes.market_id AND t.tag_label IN ({placeholders}))")
        params.extend(excluded_tags)

    where_str = " AND ".join(where_clauses)
    
    # Sorting
    valid_sorts = ["volume_usd", "liquidity_usd", "end_date", "price", "spread"]
    if sort_by not in valid_sorts: sort_by = "volume_usd"
    
    sql = f"""
        SELECT * FROM active_market_outcomes
        WHERE {where_str}
        ORDER BY {sort_by} {'ASC' if sort_dir == 'asc' else 'DESC'}
        LIMIT {limit} OFFSET {offset}
    """
    
    rows = cursor.execute(sql, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

    
    # Sorting
    valid_sorts = ["volume_usd", "liquidity_usd", "end_date", "price", "spread"]
    if sort_by not in valid_sorts: sort_by = "volume_usd"
    
    sql = f"""
        SELECT * FROM active_market_outcomes
        WHERE {where_str}
        ORDER BY {sort_by} {'ASC' if sort_dir == 'asc' else 'DESC'}
        LIMIT {limit} OFFSET {offset}
    """
    
    rows = cursor.execute(sql, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

    if os.path.exists(STATIC_PATH):
        with open(STATIC_PATH, "r") as f: return f.read()
    return "Dashboard HTML not found in static/"

if __name__ == "__main__":
    ensure_indices()
    uvicorn.run(app, host="0.0.0.0", port=8000)

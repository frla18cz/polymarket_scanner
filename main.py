import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "markets.db")
STATIC_PATH = os.path.join(BASE_DIR, "static", "index.html")

class TagStats(BaseModel):
    tag_label: str
    count: int

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/tags", response_model=List[TagStats])
def get_tags():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT tag_label, COUNT(*) as count FROM market_tags GROUP BY tag_label ORDER BY count DESC LIMIT 50"
    rows = cursor.execute(query).fetchall()
    conn.close()
    return [{"tag_label": r["tag_label"], "count": r["count"]} for r in rows]

@app.get("/api/markets")
def get_markets(
    tag: Optional[str] = None,
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    if tag:
        where_clauses.append("EXISTS (SELECT 1 FROM market_tags t WHERE t.market_id = active_market_outcomes.market_id AND t.tag_label = ?)")
        params.append(tag)

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

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists(STATIC_PATH):
        with open(STATIC_PATH, "r") as f: return f.read()
    return "Dashboard HTML not found in static/"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

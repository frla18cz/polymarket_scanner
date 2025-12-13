import os
import sqlite3
import time
import json
from datetime import datetime, timedelta
from typing import Optional, List, Any
from fastapi import FastAPI, Query, Response, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from pathlib import Path

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def _repo_root() -> Path:
    # .../.worktrees/<name>/main.py -> repo root is parents[2]
    here = Path(__file__).resolve()
    if len(here.parents) >= 3:
        return here.parents[2]
    return here.parent


def _default_db_path() -> Path:
    here = Path(__file__).resolve()
    if ".worktrees" in here.parts:
        return _repo_root() / "data" / "markets.db"
    return Path(BASE_DIR) / "data" / "markets.db"


def _default_metrics_db_path() -> Path:
    here = Path(__file__).resolve()
    if ".worktrees" in here.parts:
        return _repo_root() / "data" / "metrics.db"
    return Path(BASE_DIR) / "data" / "metrics.db"


def get_db_path() -> str:
    return os.environ.get("MARKETS_DB_PATH") or str(_default_db_path())


def get_metrics_db_path() -> str:
    return os.environ.get("METRICS_DB_PATH") or str(_default_metrics_db_path())


DB_PATH = get_db_path()
METRICS_DB_PATH = get_metrics_db_path()
FRONTEND_INDEX_PATH = Path(BASE_DIR) / "frontend_deploy" / "index.html"

class TagStats(BaseModel):
    tag_label: str
    count: int


class PerfScenarioResult(BaseModel):
    name: str
    seconds: float
    rows: int
    params: dict[str, Any]


class PerfDiagnosticsResponse(BaseModel):
    db_path: str
    generated_at: str
    scenarios: List[PerfScenarioResult]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_metrics_connection():
    conn = sqlite3.connect(METRICS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_metrics_db():
    conn = get_metrics_connection()
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            method TEXT,
            path TEXT,
            query_params TEXT,
            duration_ms REAL,
            status_code INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def ensure_indices():
    """Create indices and enable WAL mode for performance on startup."""
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
            
            -- Text Search Indices (helps with sorting/exact match)
            CREATE INDEX IF NOT EXISTS idx_amo_question ON active_market_outcomes(question);
            CREATE INDEX IF NOT EXISTS idx_amo_outcome ON active_market_outcomes(outcome_name);
            
            ANALYZE;
        """)
        conn.commit()
        print("DEBUG: Database WAL mode enabled and indices verified.")
    except Exception as e:
        print(f"WARNING: Failed to optimize DB: {e}")
    finally:
        conn.close()


def _top_tags(limit: int = 5) -> list[str]:
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT tag_label FROM market_tags GROUP BY tag_label ORDER BY COUNT(*) DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [r["tag_label"] for r in rows if r and r["tag_label"]]
    finally:
        conn.close()


def _percentile_value(column: str, quantile: float) -> Optional[float]:
    conn = get_db_connection()
    try:
        row = conn.execute(
            f"SELECT COUNT(*) AS n FROM active_market_outcomes WHERE {column} IS NOT NULL"
        ).fetchone()
        total = int(row["n"]) if row and row["n"] is not None else 0
        if total <= 0:
            return None
        offset = int(total * quantile)
        row2 = conn.execute(
            f"SELECT {column} AS v FROM active_market_outcomes WHERE {column} IS NOT NULL ORDER BY {column} ASC LIMIT 1 OFFSET ?",
            (offset,),
        ).fetchone()
        if not row2 or row2["v"] is None:
            return None
        return float(row2["v"])
    finally:
        conn.close()


def _compute_hours_to_expire_default() -> int:
    conn = get_db_connection()
    try:
        row = conn.execute(
            """
            SELECT end_date FROM active_market_outcomes
            WHERE end_date IS NOT NULL AND datetime(end_date) > datetime('now')
            ORDER BY datetime(end_date) ASC
            LIMIT 1
            """
        ).fetchone()
        if not row or not row["end_date"]:
            return 72
        end_s = str(row["end_date"]).strip()
        if end_s.endswith("Z"):
            end_s = end_s[:-1] + "+00:00"
        try:
            end_dt = datetime.fromisoformat(end_s)
        except Exception:
            return 72
        if end_dt.tzinfo is None:
            from datetime import timezone

            end_dt = end_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(end_dt.tzinfo)
        hours = int(((end_dt - now).total_seconds() / 3600.0) + 1.0)
        return max(1, min(hours, 24 * 14))
    finally:
        conn.close()

# Initialize App
app = FastAPI()

# Run startup optimization
ensure_indices()
init_metrics_db()

# CORS Configuration
origins = [
    "http://localhost:3000",
    "https://your-vercel-app.vercel.app",  
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def measure_execution_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Log to Metrics DB (Async to not block main thread too much? SQLite is fast enough for now)
    try:
        if request.url.path.startswith("/api"): # Only log API requests
            conn = get_metrics_connection()
            conn.execute(
                "INSERT INTO request_logs (method, path, query_params, duration_ms, status_code) VALUES (?, ?, ?, ?, ?)",
                (
                    request.method, 
                    request.url.path, 
                    json.dumps(dict(request.query_params)), 
                    process_time, 
                    response.status_code
                )
            )
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Error logging metric: {e}")
        
    return response

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
        uniq_included = list(dict.fromkeys(included_tags))
        placeholders = ",".join("?" * len(uniq_included))
        # ANY: at least one of selected tags
        where_clauses.append(f"market_id IN (SELECT market_id FROM market_tags WHERE tag_label IN ({placeholders}))")
        params.extend(uniq_included)

    if excluded_tags:
        placeholders = ",".join("?" * len(excluded_tags))
        # Optimized: Use NOT IN (SELECT...) instead of correlated NOT EXISTS.
        where_clauses.append(f"market_id NOT IN (SELECT market_id FROM market_tags WHERE tag_label IN ({placeholders}))")
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
    
    # --- PERFORMANCE LOGGING ---
    t_start = time.time()
    try:
        rows = cursor.execute(sql, params).fetchall()
    except Exception as e:
        print(f"ERROR executing SQL: {e}")
        conn.close()
        return []
        
    t_end = time.time()
    duration = t_end - t_start
    
    print(f"PERF: SQL Query took {duration:.4f} seconds. Rows returned: {len(rows)}")
    
    if duration > 0.5: # Log anything over 500ms
        print(f"SLOW QUERY DETECTED! SQL: {sql} PARAMS: {params}")
        try:
            explain_sql = f"EXPLAIN QUERY PLAN {sql}"
            plan = cursor.execute(explain_sql, params).fetchall()
            print("QUERY PLAN:")
            for p in plan:
                print(dict(p))
        except:
            pass

    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/admin/stats")
def get_admin_stats(request: Request, days: int = 1):
    """Internal endpoint to view performance metrics"""
    conn = get_metrics_connection()
    cursor = conn.cursor()
    
    # Average latency
    avg_latency = cursor.execute(
        "SELECT AVG(duration_ms) FROM request_logs WHERE timestamp >= datetime('now', ?)", 
        (f"-{days} days",)
    ).fetchone()[0]
    
    # Slowest queries
    slow_queries = cursor.execute(
        "SELECT * FROM request_logs ORDER BY duration_ms DESC LIMIT 10"
    ).fetchall()
    
    # Request count
    count = cursor.execute(
        "SELECT COUNT(*) FROM request_logs WHERE timestamp >= datetime('now', ?)",
        (f"-{days} days",)
    ).fetchone()[0]
    
    conn.close()
    
    return {
        "period": f"Last {days} days",
        "total_requests": count,
        "avg_latency_ms": round(avg_latency or 0, 2),
        "slowest_queries": [dict(r) for r in slow_queries]
    }


@app.get("/api/diagnostics/perf", response_model=PerfDiagnosticsResponse)
def diagnostics_perf(request: Request, mode: str = "fast"):
    """
    Dev-only: spustí sadu reprezentativních dotazů a vrátí timingy pro frontend.
    """

    tags = _top_tags(limit=5)
    if len(tags) < 2:
        raise HTTPException(status_code=500, detail="Nedostatek tagů v DB.")
    tag_a, tag_b = tags[0], tags[1]

    if mode == "auto":
        median_price = _percentile_value("price", 0.5) or 0.5
        p25_spread = _percentile_value("spread", 0.25) or 0.05
        p75_volume = _percentile_value("volume_usd", 0.75) or 1000.0
        p75_liquidity = _percentile_value("liquidity_usd", 0.75) or 100.0
        min_price = max(0.0, median_price - 0.05)
        max_price = min(1.0, median_price + 0.05)
        max_spread = float(p25_spread)
        min_volume = float(p75_volume)
        min_liquidity = float(p75_liquidity)
        hours_to_expire = _compute_hours_to_expire_default()
    else:
        min_price, max_price = 0.45, 0.55
        max_spread = 0.05
        min_volume = 1000.0
        min_liquidity = 100.0
        hours_to_expire = 72

    scenarios: list[tuple[str, dict[str, Any]]] = [
        ("excluded_single", {"included_tags": None, "excluded_tags": [tag_a], "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("excluded_multi", {"included_tags": None, "excluded_tags": [tag_a, tag_b], "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("included_single", {"included_tags": [tag_a], "excluded_tags": None, "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("included_multi", {"included_tags": [tag_a, tag_b], "excluded_tags": None, "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("included_csv", {"included_tags": [f"{tag_a},{tag_b}"], "excluded_tags": None, "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("included_excluded_conflict", {"included_tags": [tag_a, tag_b], "excluded_tags": [tag_a], "min_volume": min_volume, "max_spread": max_spread, "limit": 100}),
        ("price_probability_range", {"included_tags": None, "excluded_tags": None, "min_price": min_price, "max_price": max_price, "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("spread_max", {"included_tags": None, "excluded_tags": None, "max_spread": max_spread, "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("volume_liquidity_min", {"included_tags": None, "excluded_tags": None, "min_volume": min_volume, "min_liquidity": min_liquidity, "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("expiring_soon", {"included_tags": None, "excluded_tags": None, "max_hours_to_expire": hours_to_expire, "include_expired": False, "sort_by": "end_date", "sort_dir": "asc", "limit": 100}),
    ]

    results: list[PerfScenarioResult] = []
    for name, params in scenarios:
        t0 = time.perf_counter()
        rows = get_markets(Response(), **params)
        t1 = time.perf_counter()
        results.append(
            PerfScenarioResult(
                name=name,
                seconds=(t1 - t0),
                rows=len(rows),
                params=params,
            )
        )

    return PerfDiagnosticsResponse(
        db_path=DB_PATH,
        generated_at=datetime.utcnow().isoformat() + "Z",
        scenarios=results,
    )


def _frontend_enabled() -> bool:
    return os.environ.get("SERVE_FRONTEND") == "1"


@app.get("/", include_in_schema=False)
def frontend_root():
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not FRONTEND_INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/index.html not found")
    return FileResponse(FRONTEND_INDEX_PATH)


@app.get("/{path:path}", include_in_schema=False)
def frontend_catchall(path: str):
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    if not FRONTEND_INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/index.html not found")
    return FileResponse(FRONTEND_INDEX_PATH)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

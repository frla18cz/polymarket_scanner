import os
import sqlite3
import time
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Any
from fastapi import FastAPI, Query, Response, Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path

from bootstrap_snapshots import (
    BOOTSTRAP_CACHE_CONTROL,
    build_app_bootstrap_payload,
    build_homepage_bootstrap_payload,
    ensure_precomputed_snapshots_schema,
    load_precomputed_snapshot,
    refresh_precomputed_snapshots,
)
from logging_setup import setup_logging
from market_queries import get_status_timestamps, get_tag_stats, query_markets
from smart_money_materialized import (
    ensure_market_smart_money_stats_schema,
    rebuild_market_smart_money_stats,
)

setup_logging("web")
logger = logging.getLogger("polylab")

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
HOME_INDEX_PATH = Path(BASE_DIR) / "frontend_deploy" / "index.html"
APP_INDEX_PATH = Path(BASE_DIR) / "frontend_deploy" / "app" / "index.html"
DOCS_DIR = Path(BASE_DIR) / "frontend_deploy" / "docs"
DOCS_INDEX_PATH = Path(BASE_DIR) / "frontend_deploy" / "docs" / "index.html"
LANDING_INDEX_PATH = Path(BASE_DIR) / "frontend_deploy" / "landing" / "index.html"
CUSTOM_DATA_INDEX_PATH = Path(BASE_DIR) / "frontend_deploy" / "custom-data" / "index.html"
ROBOTS_TXT_PATH = Path(BASE_DIR) / "frontend_deploy" / "robots.txt"
SITEMAP_XML_PATH = Path(BASE_DIR) / "frontend_deploy" / "sitemap.xml"

class TagStats(BaseModel):
    tag_label: str
    count: int

class Holder(BaseModel):
    market_id: str
    outcome_index: int
    wallet_address: str
    position_size: float
    snapshot_at: str
    alias: Optional[str] = None

class WalletStats(BaseModel):
    wallet_address: str
    total_pnl: float
    last_updated: str
    alias: Optional[str] = None

class HolderDetail(BaseModel):

    wallet_address: str

    position_size: float

    outcome_index: int

    total_pnl: Optional[float] = None

    alias: Optional[str] = None

    wallet_tag: Optional[str] = None







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

        # Schema migration (idempotent): add + backfill APR for outcome-level rows
        try:
            # Check if wallets_stats exists and needs 'alias' column
            ws_exists = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='wallets_stats'").fetchone()[0]
            if ws_exists:
                cols = [r["name"] for r in conn.execute("PRAGMA table_info(wallets_stats)").fetchall()]
                if "alias" not in cols:
                    conn.execute("ALTER TABLE wallets_stats ADD COLUMN alias TEXT;")
                    conn.commit()
                if "wallet_tag" not in cols:
                    conn.execute("ALTER TABLE wallets_stats ADD COLUMN wallet_tag TEXT;")
                    conn.commit()
            
            # Identify known system/rewards wallet
            REWARDS_WALLET = "0xa5ef39c3d3e10d0b270233af41cac69796b12966"
            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute("INSERT OR IGNORE INTO wallets_stats (wallet_address, total_pnl, last_updated) VALUES (?, 0, ?)", (REWARDS_WALLET, now_iso))
            conn.execute("UPDATE wallets_stats SET wallet_tag = 'SYSTEM' WHERE wallet_address = ?", (REWARDS_WALLET,))
            conn.commit()

            cols = [r["name"] for r in conn.execute("PRAGMA table_info(active_market_outcomes)").fetchall()]
            if "apr" not in cols:
                conn.execute("ALTER TABLE active_market_outcomes ADD COLUMN apr REAL;")
                conn.commit()
            
            if "condition_id" not in cols:
                conn.execute("ALTER TABLE active_market_outcomes ADD COLUMN condition_id TEXT;")
                conn.commit()

            if "outcome_index" not in cols:
                conn.execute("ALTER TABLE active_market_outcomes ADD COLUMN outcome_index INTEGER;")
                conn.commit()
            
            # Always ensure outcome_index is backfilled for Yes/No if it is NULL
            conn.execute("UPDATE active_market_outcomes SET outcome_index = 0 WHERE (outcome_index IS NULL) AND (outcome_name = 'Yes' OR outcome_name = 'YES');")
            conn.execute("UPDATE active_market_outcomes SET outcome_index = 1 WHERE (outcome_index IS NULL) AND (outcome_name = 'No' OR outcome_name = 'NO');")
            conn.commit()

            conn.execute(
                """
                UPDATE active_market_outcomes
                SET apr = (
                    CASE
                        WHEN price IS NOT NULL
                             AND price > 0.0
                             AND price < 1.0
                             AND end_date IS NOT NULL
                             AND snapshot_at IS NOT NULL
                             AND julianday(datetime(end_date)) > julianday(datetime(snapshot_at))
                        THEN ((1.0 / price) - 1.0) * (365.0 / (julianday(datetime(end_date)) - julianday(datetime(snapshot_at))))
                        ELSE NULL
                    END
                )
                WHERE apr IS NULL
                """
            )
            conn.commit()
        except Exception as e:
            logger.warning("Failed to ensure APR column/index readiness: %s", e)
        
        ensure_market_smart_money_stats_schema(conn)
        ensure_precomputed_snapshots_schema(conn)

        conn.executescript("""
            CREATE TABLE IF NOT EXISTS holders (
                market_id TEXT,
                outcome_index INTEGER,
                wallet_address TEXT,
                position_size REAL,
                snapshot_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS wallets_stats (
                wallet_address TEXT PRIMARY KEY,
                total_pnl REAL,
                last_updated TEXT,
                alias TEXT,
                wallet_tag TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_holders_market ON holders(market_id);
            CREATE INDEX IF NOT EXISTS idx_holders_wallet ON holders(wallet_address);
            CREATE INDEX IF NOT EXISTS idx_holders_market_outcome ON holders(market_id, outcome_index);
            CREATE INDEX IF NOT EXISTS idx_holders_market_outcome_wallet ON holders(market_id, outcome_index, wallet_address);
            CREATE INDEX IF NOT EXISTS idx_wallets_stats_address ON wallets_stats(wallet_address);

            CREATE INDEX IF NOT EXISTS idx_market_tags_label ON market_tags(tag_label);
            CREATE INDEX IF NOT EXISTS idx_market_tags_market_id ON market_tags(market_id);
            CREATE INDEX IF NOT EXISTS idx_amo_market_id ON active_market_outcomes(market_id);
            CREATE INDEX IF NOT EXISTS idx_amo_condition_id ON active_market_outcomes(condition_id);
            CREATE INDEX IF NOT EXISTS idx_amo_outcome_index ON active_market_outcomes(outcome_index);
            CREATE INDEX IF NOT EXISTS idx_amo_volume ON active_market_outcomes(volume_usd DESC);
            CREATE INDEX IF NOT EXISTS idx_amo_liquidity ON active_market_outcomes(liquidity_usd DESC);
            CREATE INDEX IF NOT EXISTS idx_amo_end_date ON active_market_outcomes(end_date);
            
            -- Missing indices for sliders (Critical for performance)
            CREATE INDEX IF NOT EXISTS idx_amo_price ON active_market_outcomes(price);
            CREATE INDEX IF NOT EXISTS idx_amo_spread ON active_market_outcomes(spread);
            CREATE INDEX IF NOT EXISTS idx_amo_apr ON active_market_outcomes(apr);
            
            -- Text Search Indices (helps with sorting/exact match)
            CREATE INDEX IF NOT EXISTS idx_amo_question ON active_market_outcomes(question);
            CREATE INDEX IF NOT EXISTS idx_amo_outcome ON active_market_outcomes(outcome_name);
            
            ANALYZE;
        """)
        conn.commit()
        logger.info("Database WAL mode enabled and indices verified.")
    except Exception as e:
        logger.warning("Failed to optimize DB: %s", e)
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


def refresh_materialized_smart_money_stats() -> str:
    conn = get_db_connection()
    try:
        updated_at = rebuild_market_smart_money_stats(conn)
        conn.commit()
        return updated_at
    finally:
        conn.close()


def refresh_bootstrap_snapshots() -> None:
    conn = get_db_connection()
    try:
        refresh_precomputed_snapshots(conn)
        conn.commit()
    finally:
        conn.close()


def _load_or_build_snapshot(snapshot_key: str, builder):
    conn = get_db_connection()
    try:
        payload = load_precomputed_snapshot(conn, snapshot_key)
        if payload is not None:
            return payload
        payload = builder(conn)
        ensure_precomputed_snapshots_schema(conn)
        refresh_precomputed_snapshots(conn)
        conn.commit()
        return payload
    finally:
        conn.close()

# Initialize App
app = FastAPI(title="PolyLab", docs_url="/api/docs", redoc_url="/api/redoc")

# Serve static assets for the frontend (e.g. logo under /assets/*)
ASSETS_DIR = Path(BASE_DIR) / "frontend_deploy" / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Run startup optimization
ensure_indices()
init_metrics_db()

app.add_middleware(
    CORSMiddleware,
    # We don't use cookies/auth for the API, so keep CORS permissive.
    # This also avoids the invalid combination of `allow_credentials=True` with `allow_origins=["*"]`.
    allow_origins=["*"],
    allow_credentials=False,
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
        logger.warning("Error logging metric: %s", e)
        
    return response

@app.get("/api/markets/{market_id}/holders", response_model=List[HolderDetail])
def get_market_holders(market_id: str):
    conn = get_db_connection()
    try:
        # Join holders with wallets_stats to get PnL, alias and wallet_tag
        sql = """
            SELECT 
                h.wallet_address, 
                h.position_size, 
                h.outcome_index,
                ws.total_pnl,
                ws.alias,
                ws.wallet_tag
            FROM holders h
            LEFT JOIN wallets_stats ws ON h.wallet_address = ws.wallet_address
            WHERE h.market_id = ?
            ORDER BY h.outcome_index ASC, h.position_size DESC
        """
        rows = conn.execute(sql, (market_id,)).fetchall()
        return [
            HolderDetail(
                wallet_address=r["wallet_address"],
                position_size=r["position_size"],
                outcome_index=r["outcome_index"],
                total_pnl=r["total_pnl"],
                alias=r["alias"],
                wallet_tag=r["wallet_tag"]
            )
            for r in rows
        ]
    finally:
        conn.close()

@app.get("/api/tags", response_model=List[TagStats])


def get_tags():
    conn = get_db_connection()
    try:
        return get_tag_stats(conn)
    finally:
        conn.close()

@app.get("/api/status")
def get_status(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    conn = get_db_connection()
    try:
        return get_status_timestamps(conn)
    finally:
        conn.close()

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
    min_apr: Optional[float] = None,
    min_hours_to_expire: Optional[int] = None,
    max_hours_to_expire: Optional[int] = None,
    include_expired: bool = True,
    search: Optional[str] = None,
    profit_threshold: float = 1000.0,
    min_profitable: int = 0,
    min_losing_opposite: int = 0
):
    # When calling endpoint functions directly (tests/tools), FastAPI's `Query(...)` defaults
    # are not resolved and can show up as `fastapi.params.Query` instances.
    try:
        from fastapi.params import Query as _QueryParam  # type: ignore
    except Exception:
        _QueryParam = None
    if _QueryParam is not None:
        if isinstance(included_tags, _QueryParam):
            included_tags = None
        if isinstance(excluded_tags, _QueryParam):
            excluded_tags = None

    logger.debug("get_markets called with included_tags=%s, excluded_tags=%s", included_tags, excluded_tags)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    conn = get_db_connection()
    try:
        return query_markets(
            conn,
            included_tags=included_tags,
            excluded_tags=excluded_tags,
            sort_by=sort_by,
            sort_dir=sort_dir,
            limit=limit,
            offset=offset,
            min_volume=min_volume,
            min_liquidity=min_liquidity,
            min_price=min_price,
            max_price=max_price,
            max_spread=max_spread,
            min_apr=min_apr,
            min_hours_to_expire=min_hours_to_expire,
            max_hours_to_expire=max_hours_to_expire,
            include_expired=include_expired,
            search=search,
            profit_threshold=profit_threshold,
            min_profitable=min_profitable,
            min_losing_opposite=min_losing_opposite,
        )
    finally:
        conn.close()


@app.get("/api/homepage-bootstrap")
def get_homepage_bootstrap(response: Response):
    response.headers["Cache-Control"] = BOOTSTRAP_CACHE_CONTROL
    return _load_or_build_snapshot("homepage", build_homepage_bootstrap_payload)


@app.get("/api/app-bootstrap")
def get_app_bootstrap(response: Response, view: str = "scanner", preset: Optional[str] = None):
    response.headers["Cache-Control"] = BOOTSTRAP_CACHE_CONTROL
    normalized_view = "smart" if view == "smart" else "scanner"
    snapshot_key = f"app_preset_{preset}" if preset else f"app_default_{normalized_view}"
    return _load_or_build_snapshot(
        snapshot_key,
        lambda conn: build_app_bootstrap_payload(conn, view=normalized_view, preset_id=preset),
    )

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
        ("text_search_like", {"search": "Trump", "sort_by": "volume_usd", "sort_dir": "desc", "limit": 100}),
        ("sort_by_apr", {"min_apr": 0.05, "sort_by": "apr", "sort_dir": "desc", "limit": 100}),
        ("deep_pagination", {"sort_by": "volume_usd", "limit": 100, "offset": 5000}),
        ("kitchen_sink_complex", {"search": "a", "min_volume": 1000, "max_spread": 0.1, "min_price": 0.1, "max_price": 0.9, "sort_by": "liquidity_usd", "limit": 50}),
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

def _frontend_no_cache_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }


def _resolve_docs_page_path(path: str | None = None) -> Path:
    if path is None or path == "":
        target = DOCS_DIR / "index.html"
    else:
        parts = [part for part in Path(path).parts if part not in ("", ".")]
        if not parts or any(part == ".." for part in parts):
            raise HTTPException(status_code=404, detail="Not Found")
        target = DOCS_DIR.joinpath(*parts) / "index.html"
    if not target.exists():
        raise HTTPException(status_code=404, detail="Not Found")
    return target


@app.get("/", include_in_schema=False)
def frontend_root(request: Request):
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if "market_id" in request.query_params:
        redirect_target = f"/app?{request.query_params}"
        return RedirectResponse(url=redirect_target, status_code=307, headers=_frontend_no_cache_headers())
    if not HOME_INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/index.html not found")
    return FileResponse(HOME_INDEX_PATH, headers=_frontend_no_cache_headers())


@app.get("/app", include_in_schema=False)
@app.get("/app/", include_in_schema=False)
def frontend_app():
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not APP_INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/app/index.html not found")
    return FileResponse(APP_INDEX_PATH, headers=_frontend_no_cache_headers())


@app.get("/docs", include_in_schema=False)
@app.get("/docs/", include_in_schema=False)
def frontend_docs():
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(_resolve_docs_page_path(), headers=_frontend_no_cache_headers())


@app.get("/docs/{path:path}", include_in_schema=False)
def frontend_docs_page(path: str):
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(_resolve_docs_page_path(path), headers=_frontend_no_cache_headers())


@app.get("/landing", include_in_schema=False)
@app.get("/landing/", include_in_schema=False)
def frontend_landing():
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not LANDING_INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/landing/index.html not found")
    return FileResponse(LANDING_INDEX_PATH, headers=_frontend_no_cache_headers())


@app.get("/custom-data", include_in_schema=False)
@app.get("/custom-data/", include_in_schema=False)
def frontend_custom_data():
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not CUSTOM_DATA_INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/custom-data/index.html not found")
    return FileResponse(CUSTOM_DATA_INDEX_PATH, headers=_frontend_no_cache_headers())


@app.get("/robots.txt", include_in_schema=False)
def frontend_robots():
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not ROBOTS_TXT_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/robots.txt not found")
    return FileResponse(ROBOTS_TXT_PATH, headers=_frontend_no_cache_headers())


@app.get("/sitemap.xml", include_in_schema=False)
def frontend_sitemap():
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if not SITEMAP_XML_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/sitemap.xml not found")
    return FileResponse(SITEMAP_XML_PATH, headers=_frontend_no_cache_headers())


@app.get("/app/{path:path}", include_in_schema=False)
def frontend_app_catchall(path: str):
    if not _frontend_enabled():
        raise HTTPException(status_code=404, detail="Not Found")
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not Found")
    if not APP_INDEX_PATH.exists():
        raise HTTPException(status_code=500, detail="frontend_deploy/app/index.html not found")
    return FileResponse(APP_INDEX_PATH, headers=_frontend_no_cache_headers())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

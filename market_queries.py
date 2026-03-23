from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional


logger = logging.getLogger("polylab.market_queries")


VALID_SORTS = {
    "volume_usd": "amo.volume_usd",
    "liquidity_usd": "amo.liquidity_usd",
    "end_date": "amo.end_date",
    "price": "amo.price",
    "spread": "amo.spread",
    "apr": "apr",
    "question": "amo.question COLLATE NOCASE",
    "yes_profitable_count": "COALESCE(msm.yes_profitable_count, 0)",
    "yes_losing_count": "COALESCE(msm.yes_losing_count, 0)",
    "yes_total": "COALESCE(msm.yes_total, 0)",
    "no_profitable_count": "COALESCE(msm.no_profitable_count, 0)",
    "no_losing_count": "COALESCE(msm.no_losing_count, 0)",
    "no_total": "COALESCE(msm.no_total, 0)",
}


def _pragma_column_name(row):
    try:
        if hasattr(row, "keys") and "name" in row.keys():
            return row["name"]
    except Exception:
        pass
    try:
        return row[1]
    except Exception:
        return None


def table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    return bool(row)


def normalize_tag_filters(values: Optional[list[str]]) -> Optional[list[str]]:
    if not values:
        return None
    if len(values) == 1 and "," in values[0]:
        values = values[0].split(",")
    cleaned = [value.strip() for value in values if value and value.strip()]
    return list(dict.fromkeys(cleaned)) or None


def get_tag_stats(conn) -> list[dict[str, Any]]:
    try:
        rows = conn.execute(
            "SELECT tag_label, COUNT(*) as count FROM market_tags GROUP BY tag_label ORDER BY count DESC"
        ).fetchall()
    except Exception:
        return []

    result: list[dict[str, Any]] = []
    for row in rows:
        if hasattr(row, "keys"):
            result.append({"tag_label": row["tag_label"], "count": row["count"]})
        else:
            result.append({"tag_label": row[0], "count": row[1]})
    return result


def get_status_timestamps(conn) -> dict[str, Optional[str]]:
    try:
        last_updated_row = conn.execute(
            "SELECT MAX(snapshot_at) as last_updated FROM active_market_outcomes"
        ).fetchone()
        smart_row = conn.execute(
            "SELECT MAX(last_updated_at) as smart_money_last_updated FROM market_smart_money_stats"
        ).fetchone()
    except Exception:
        return {"last_updated": None, "smart_money_last_updated": None}

    return {
        "last_updated": last_updated_row["last_updated"] if last_updated_row else None,
        "smart_money_last_updated": smart_row["smart_money_last_updated"] if smart_row else None,
    }


def _build_apr_sql(conn) -> str:
    amo_cols = {
        column_name
        for column_name in (
            _pragma_column_name(row)
            for row in conn.execute("PRAGMA table_info(active_market_outcomes)").fetchall()
        )
        if column_name
    }
    if "apr" in amo_cols:
        return "amo.apr"
    return (
        "CASE "
        "WHEN amo.price IS NOT NULL "
        " AND amo.price > 0.0 "
        " AND amo.price < 1.0 "
        " AND amo.end_date IS NOT NULL "
        " AND amo.snapshot_at IS NOT NULL "
        " AND julianday(datetime(amo.end_date)) > julianday(datetime(amo.snapshot_at)) "
        "THEN ((1.0 / amo.price) - 1.0) * "
        "(365.0 / (julianday(datetime(amo.end_date)) - julianday(datetime(amo.snapshot_at)))) "
        "ELSE NULL "
        "END"
    )


def build_markets_sql(
    conn,
    *,
    included_tags: Optional[list[str]] = None,
    excluded_tags: Optional[list[str]] = None,
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
    min_losing_opposite: int = 0,
) -> tuple[str, list[Any]]:
    del profit_threshold

    apr_sql = _build_apr_sql(conn)
    where_clauses = ["1=1"]
    params: list[Any] = []

    if min_volume:
        where_clauses.append("amo.volume_usd >= ?")
        params.append(min_volume)

    if min_liquidity:
        where_clauses.append("amo.liquidity_usd >= ?")
        params.append(min_liquidity)

    if min_price is not None:
        where_clauses.append("amo.price >= ?")
        params.append(min_price)

    if max_price is not None:
        where_clauses.append("amo.price <= ?")
        params.append(max_price)

    if max_spread is not None:
        where_clauses.append("amo.spread <= ?")
        params.append(max_spread)

    if min_apr is not None and float(min_apr) > 0:
        where_clauses.append(f"(({apr_sql}) IS NOT NULL AND ({apr_sql}) >= ?)")
        params.append(float(min_apr))

    if min_profitable > 0:
        where_clauses.append(
            """
            (CASE
                WHEN amo.outcome_index = 0 THEN COALESCE(msm.yes_profitable_count, 0)
                ELSE COALESCE(msm.no_profitable_count, 0)
             END) >= ?
            """
        )
        params.append(int(min_profitable))

    if min_losing_opposite > 0:
        where_clauses.append(
            """
            (CASE
                WHEN amo.outcome_index = 0 THEN COALESCE(msm.no_losing_count, 0)
                ELSE COALESCE(msm.yes_losing_count, 0)
             END) >= ?
            """
        )
        params.append(int(min_losing_opposite))

    if search:
        where_clauses.append("(amo.question LIKE ? OR amo.outcome_name LIKE ?)")
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    if min_hours_to_expire is not None and int(min_hours_to_expire) <= 0:
        min_hours_to_expire = None
    if max_hours_to_expire is not None and int(max_hours_to_expire) <= 0:
        max_hours_to_expire = None
    if min_hours_to_expire is not None and max_hours_to_expire is not None and int(min_hours_to_expire) > int(max_hours_to_expire):
        min_hours_to_expire, max_hours_to_expire = max_hours_to_expire, min_hours_to_expire

    if min_hours_to_expire is not None:
        min_dt = datetime.now(timezone.utc) + timedelta(hours=int(min_hours_to_expire))
        where_clauses.append("amo.end_date >= ?")
        params.append(min_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))

    if max_hours_to_expire is not None:
        cutoff_dt = datetime.now(timezone.utc) + timedelta(hours=int(max_hours_to_expire))
        where_clauses.append("amo.end_date <= ?")
        params.append(cutoff_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))

    if (min_hours_to_expire is not None or max_hours_to_expire is not None) and not include_expired:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        where_clauses.append("amo.end_date >= ?")
        params.append(now_str)

    included_tags = normalize_tag_filters(included_tags)
    excluded_tags = normalize_tag_filters(excluded_tags)

    if included_tags:
        placeholders = ",".join("?" * len(included_tags))
        where_clauses.append(
            f"amo.market_id IN (SELECT market_id FROM market_tags WHERE tag_label IN ({placeholders}))"
        )
        params.extend(included_tags)

    if excluded_tags:
        placeholders = ",".join("?" * len(excluded_tags))
        where_clauses.append(
            f"amo.market_id NOT IN (SELECT market_id FROM market_tags WHERE tag_label IN ({placeholders}))"
        )
        params.extend(excluded_tags)

    sort_sql = VALID_SORTS.get(sort_by, VALID_SORTS["volume_usd"])
    where_sql = " AND ".join(where_clauses)

    sql = f"""
        SELECT
            amo.*,
            ({apr_sql}) AS apr,
            COALESCE(msm.yes_profitable_count, 0) AS yes_profitable_count,
            COALESCE(msm.yes_losing_count, 0) AS yes_losing_count,
            COALESCE(msm.yes_total, 0) AS yes_total,
            COALESCE(msm.no_profitable_count, 0) AS no_profitable_count,
            COALESCE(msm.no_losing_count, 0) AS no_losing_count,
            COALESCE(msm.no_total, 0) AS no_total
        FROM active_market_outcomes amo
        LEFT JOIN market_smart_money_stats msm
          ON msm.condition_id = amo.condition_id
        WHERE {where_sql}
        ORDER BY {sort_sql} {'ASC' if sort_dir == 'asc' else 'DESC'}
        LIMIT ? OFFSET ?
    """
    params.extend([int(limit), int(offset)])
    return sql, params


def query_markets(conn, **kwargs) -> list[dict[str, Any]]:
    sql, params = build_markets_sql(conn, **kwargs)
    cursor = conn.cursor()

    started_at = time.time()
    try:
        rows = cursor.execute(sql, params).fetchall()
    except Exception as exc:
        logger.exception("Error executing markets SQL: %s", exc)
        return []

    duration = time.time() - started_at
    if duration > 0.5:
        logger.warning("Slow SQL query (%.4fs): %s params=%s", duration, sql, params)
        try:
            plan_rows = cursor.execute(f"EXPLAIN QUERY PLAN {sql}", params).fetchall()
            for row in plan_rows:
                logger.debug("Query plan row: %s", dict(row))
        except Exception:
            pass
    return [dict(row) for row in rows]

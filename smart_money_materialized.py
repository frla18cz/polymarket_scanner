from __future__ import annotations

from datetime import datetime, timezone


SMART_MONEY_SCHEMA_COLUMNS: tuple[tuple[str, str], ...] = (
    ("condition_id", "TEXT PRIMARY KEY"),
    ("yes_profitable_count", "INTEGER DEFAULT 0"),
    ("yes_losing_count", "INTEGER DEFAULT 0"),
    ("yes_total", "INTEGER DEFAULT 0"),
    ("no_profitable_count", "INTEGER DEFAULT 0"),
    ("no_losing_count", "INTEGER DEFAULT 0"),
    ("no_total", "INTEGER DEFAULT 0"),
    ("smart_money_win_rate", "REAL"),
    ("last_updated_at", "TEXT"),
)


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


def ensure_market_smart_money_stats_schema(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS market_smart_money_stats (
            condition_id TEXT PRIMARY KEY,
            yes_profitable_count INTEGER DEFAULT 0,
            yes_losing_count INTEGER DEFAULT 0,
            yes_total INTEGER DEFAULT 0,
            no_profitable_count INTEGER DEFAULT 0,
            no_losing_count INTEGER DEFAULT 0,
            no_total INTEGER DEFAULT 0,
            smart_money_win_rate REAL,
            last_updated_at TEXT
        )
        """
    )

    columns = {
        column_name
        for column_name in (
            _pragma_column_name(row)
            for row in conn.execute("PRAGMA table_info(market_smart_money_stats)").fetchall()
        )
        if column_name
    }
    for column_name, column_def in SMART_MONEY_SCHEMA_COLUMNS:
        if column_name not in columns:
            conn.execute(f"ALTER TABLE market_smart_money_stats ADD COLUMN {column_name} {column_def}")

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_market_smart_money_last_updated ON market_smart_money_stats(last_updated_at)"
    )


def rebuild_market_smart_money_stats(conn, generated_at: str | None = None) -> str:
    ensure_market_smart_money_stats_schema(conn)
    now_iso = generated_at or datetime.now(timezone.utc).isoformat()

    conn.execute(
        """
        DELETE FROM market_smart_money_stats
        WHERE condition_id NOT IN (
            SELECT DISTINCT market_id
            FROM holders
            WHERE market_id IS NOT NULL
        )
        """
    )

    conn.execute(
        """
        INSERT INTO market_smart_money_stats (
            condition_id,
            yes_profitable_count,
            yes_losing_count,
            yes_total,
            no_profitable_count,
            no_losing_count,
            no_total,
            smart_money_win_rate,
            last_updated_at
        )
        SELECT
            h.market_id AS condition_id,
            SUM(CASE WHEN h.outcome_index = 0 AND ws.total_pnl > 0 THEN 1 ELSE 0 END) AS yes_profitable_count,
            SUM(CASE WHEN h.outcome_index = 0 AND ws.total_pnl < 0 THEN 1 ELSE 0 END) AS yes_losing_count,
            SUM(CASE WHEN h.outcome_index = 0 THEN 1 ELSE 0 END) AS yes_total,
            SUM(CASE WHEN h.outcome_index = 1 AND ws.total_pnl > 0 THEN 1 ELSE 0 END) AS no_profitable_count,
            SUM(CASE WHEN h.outcome_index = 1 AND ws.total_pnl < 0 THEN 1 ELSE 0 END) AS no_losing_count,
            SUM(CASE WHEN h.outcome_index = 1 THEN 1 ELSE 0 END) AS no_total,
            CASE
                WHEN COUNT(*) > 0
                THEN CAST(SUM(CASE WHEN ws.total_pnl > 0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*)
                ELSE NULL
            END AS smart_money_win_rate,
            ? AS last_updated_at
        FROM holders h
        LEFT JOIN wallets_stats ws
          ON h.wallet_address = ws.wallet_address
        WHERE h.market_id IS NOT NULL
        GROUP BY h.market_id
        ON CONFLICT(condition_id) DO UPDATE SET
            yes_profitable_count = excluded.yes_profitable_count,
            yes_losing_count = excluded.yes_losing_count,
            yes_total = excluded.yes_total,
            no_profitable_count = excluded.no_profitable_count,
            no_losing_count = excluded.no_losing_count,
            no_total = excluded.no_total,
            smart_money_win_rate = excluded.smart_money_win_rate,
            last_updated_at = excluded.last_updated_at
        """,
        (now_iso,),
    )
    return now_iso

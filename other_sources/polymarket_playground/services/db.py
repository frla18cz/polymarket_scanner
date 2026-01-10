import duckdb
import os

DB_PATH = "data/polymarket.db"


def get_connection(read_only=False):
    """
    Returns a connection to the DuckDB database.
    If read_only is True, opens in read-only mode (useful for UI/concurrent reads).
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return duckdb.connect(DB_PATH, read_only=read_only)


def init_db():
    """
    Initializes the database schema if it doesn't exist.
    """
    conn = get_connection()

    # Table: user_positions
    # Stores raw position data from the Subgraph.
    # We store realizedPnl as DOUBLE for easier aggregation,
    # assuming precision loss at >1e15 is acceptable for analysis (or use DECIMAL(38,0) if strict).
    # For now, DOUBLE is fastest for analytics.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_positions (
            id VARCHAR PRIMARY KEY,
            user_addr VARCHAR,
            realizedPnl DOUBLE,
            avgPrice DOUBLE,
            totalBought DOUBLE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Index for fast lookups by user
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_user_positions_user ON user_positions(user_addr)
    """
    )

    # Table: wallet_labels
    # Stores annotations, tags, and suspicion flags for specific wallets.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS wallet_labels (
            user_addr VARCHAR PRIMARY KEY,
            label VARCHAR,
            notes TEXT,
            is_suspicious BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Table: active_market_holders
    # Stores snapshot of current holders for active markets.
    # Used for "Smart Money" analysis (who holds what NOW).
    conn.execute("""
        CREATE TABLE IF NOT EXISTS active_market_holders (
            market_id VARCHAR,
            user_addr VARCHAR,
            outcome_index INTEGER,
            position_size DOUBLE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (market_id, user_addr, outcome_index)
        )
    """)

    # Index for fast joins
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_holders_user ON active_market_holders(user_addr)
    """)

    # Table: market_analytics
    # Stores per-market snapshot metrics (Smart Money, liquidity, etc.).
    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_analytics (
            market_id VARCHAR,
            question VARCHAR,
            slug VARCHAR,
            outcome_index INTEGER,
            smart_vol DOUBLE,
            ghost_vol DOUBLE,
            total_vol_snapshot DOUBLE,
            smart_holders_count BIGINT,
            total_holders_count BIGINT,
            smart_ratio DOUBLE,
            liquidity_usd DOUBLE,
            volume_usd DOUBLE,
            market_snapshot_at TIMESTAMP,
            snapshot_ts TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_analytics_market ON market_analytics(market_id)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_analytics_snapshot ON market_analytics(snapshot_ts)
    """)
    
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()

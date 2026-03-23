from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from typing import Any, Optional

from market_queries import get_status_timestamps, get_tag_stats, query_markets, table_exists


BOOTSTRAP_CACHE_CONTROL = "public, s-maxage=300, stale-while-revalidate=3600"
HOMEPAGE_LOCAL_CACHE_MAX_AGE_MS = 24 * 60 * 60 * 1000
APP_BOOTSTRAP_LIMIT = 100
HOMEPAGE_SPOTLIGHT_LIMIT = 100
HOMEPAGE_SPOTLIGHT_PAGE_SIZE = 18
PLAYBOOK_PREVIEW_LIMIT = 3

DEFAULT_APP_FILTERS: dict[str, Any] = {
    "includedTags": [],
    "excludedTags": [],
    "min_volume": 5000,
    "min_liquidity": 1000,
    "min_price": 0.00,
    "max_price": 1.00,
    "max_spread": 0.05,
    "min_apr_percent": 0,
    "min_hours_to_expire": 0,
    "max_hours_to_expire": 0,
    "expiry_index": 0,
    "include_expired": True,
    "min_profitable": 0,
    "min_losing_opposite": 0,
    "search": "",
    "sort_by": "volume_usd",
    "sort_dir": "desc",
}

PRESET_BOOTSTRAP_SPECS: list[dict[str, Any]] = [
    {
        "id": "smart_money_edge",
        "view": "smart",
        "locked": False,
        "homepage_target_view": "smart",
        "apply": {
            "min_profitable": 15,
            "min_losing_opposite": 15,
            "max_spread": 0.05,
            "min_liquidity": 1000,
            "sort_by": "volume_usd",
            "sort_dir": "desc",
        },
    },
    {
        "id": "safe_haven",
        "view": "scanner",
        "locked": False,
        "apply": {
            "min_price": 0.90,
            "max_price": 1.00,
            "max_spread": 0.02,
            "min_liquidity": 500,
        },
    },
    {
        "id": "buffett",
        "view": "scanner",
        "locked": True,
        "apply": {
            "min_price": 0.90,
            "min_liquidity": 50000,
            "max_spread": 0.02,
            "excludedTags": [
                "Crypto",
                "Crypto Prices",
                "Crypto Policy",
                "Crypto Summit",
                "CryptoPunks",
                "Bitcoin",
                "Ethereum",
                "Solana",
            ],
        },
    },
    {
        "id": "sniper",
        "view": "scanner",
        "locked": True,
        "apply": {
            "max_hours_to_expire": 24,
            "include_expired": False,
            "sort_by": "end_date",
            "sort_dir": "asc",
        },
    },
    {
        "id": "coinflip",
        "view": "scanner",
        "locked": False,
        "apply": {
            "min_price": 0.45,
            "max_price": 0.55,
        },
    },
    {
        "id": "yolo",
        "view": "scanner",
        "locked": False,
        "apply": {
            "max_price": 0.05,
            "min_volume": 1000,
            "sort_by": "price",
            "sort_dir": "asc",
        },
    },
    {
        "id": "longshot",
        "view": "scanner",
        "locked": False,
        "apply": {
            "max_price": 0.15,
            "min_liquidity": 500,
        },
    },
    {
        "id": "newsmaker",
        "view": "scanner",
        "locked": False,
        "apply": {
            "min_volume": 100000,
            "sort_by": "volume_usd",
            "sort_dir": "desc",
        },
    },
]


def ensure_precomputed_snapshots_schema(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS precomputed_snapshots (
            snapshot_key TEXT PRIMARY KEY,
            payload_json TEXT NOT NULL,
            generated_at TEXT NOT NULL,
            market_last_updated TEXT,
            smart_money_last_updated TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_precomputed_snapshots_generated_at ON precomputed_snapshots(generated_at)"
    )


def resolve_preset_spec(preset_id: Optional[str]) -> Optional[dict[str, Any]]:
    if not preset_id:
        return None
    for spec in PRESET_BOOTSTRAP_SPECS:
        if spec["id"] == preset_id:
            return spec
    return None


def build_snapshot_cache_key(view: str = "scanner", preset_id: Optional[str] = None) -> str:
    normalized_view = "smart" if view == "smart" else "scanner"
    suffix = preset_id or "default"
    return f"polylab:app-bootstrap:{normalized_view}:{suffix}"


def _copy_default_filters() -> dict[str, Any]:
    return copy.deepcopy(DEFAULT_APP_FILTERS)


def build_filters_for_preset(preset_id: Optional[str], view: str = "scanner") -> tuple[str, Optional[str], dict[str, Any]]:
    filters = _copy_default_filters()
    resolved_view = "smart" if view == "smart" else "scanner"
    active_preset_id = None

    spec = resolve_preset_spec(preset_id)
    if spec:
        active_preset_id = spec["id"]
        resolved_view = spec.get("view", resolved_view)
        for key, value in spec.get("apply", {}).items():
            filters[key] = copy.deepcopy(value)
    return resolved_view, active_preset_id, filters


def _conviction_score(market: dict[str, Any]) -> int | None:
    yes_total = int(market.get("yes_total") or 0)
    no_total = int(market.get("no_total") or 0)
    if yes_total <= 0 or no_total <= 0:
        return None
    yes_pct = round(((market.get("yes_profitable_count") or 0) / yes_total) * 100)
    no_pct = round(((market.get("no_profitable_count") or 0) / no_total) * 100)
    score = abs(yes_pct - no_pct)
    return score if score >= 25 else None


def _select_homepage_spotlights(markets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for market in markets:
        condition_id = market.get("condition_id")
        if not condition_id or condition_id in seen:
            continue
        if int(market.get("yes_total") or 0) < 20 or int(market.get("no_total") or 0) < 20:
            continue
        seen.add(condition_id)
        deduped.append(market)

    strict: list[dict[str, Any]] = []
    relaxed: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    for market in deduped:
        yes_profitable = int(market.get("yes_profitable_count") or 0)
        no_profitable = int(market.get("no_profitable_count") or 0)
        yes_losing = int(market.get("yes_losing_count") or 0)
        no_losing = int(market.get("no_losing_count") or 0)
        strict_hit = (
            yes_profitable >= 15 and no_losing >= 15
        ) or (
            no_profitable >= 15 and yes_losing >= 15
        )
        relaxed_hit = yes_profitable >= 15 or no_profitable >= 15
        if strict_hit:
            strict.append(market)
        elif relaxed_hit:
            relaxed.append(market)
        elif _conviction_score(market) is not None:
            fallback.append(market)
    return (strict + relaxed + fallback)[:HOMEPAGE_SPOTLIGHT_PAGE_SIZE]


def _filters_to_market_query(filters: dict[str, Any], view: str) -> dict[str, Any]:
    params: dict[str, Any] = {
        "included_tags": filters.get("includedTags") or None,
        "excluded_tags": filters.get("excludedTags") or None,
        "sort_by": filters.get("sort_by", "volume_usd"),
        "sort_dir": filters.get("sort_dir", "desc"),
        "limit": APP_BOOTSTRAP_LIMIT,
        "offset": 0,
        "min_volume": filters.get("min_volume", 0),
        "min_liquidity": filters.get("min_liquidity", 0),
        "min_price": filters.get("min_price", 0.0),
        "max_price": filters.get("max_price", 1.0),
        "max_spread": filters.get("max_spread"),
        "min_apr": (float(filters.get("min_apr_percent", 0)) / 100.0) if float(filters.get("min_apr_percent", 0) or 0) > 0 else None,
        "min_hours_to_expire": filters.get("min_hours_to_expire") or None,
        "max_hours_to_expire": filters.get("max_hours_to_expire") or None,
        "include_expired": bool(filters.get("include_expired", True)),
        "search": filters.get("search") or None,
        "min_profitable": int(filters.get("min_profitable", 0) or 0) if view == "smart" else 0,
        "min_losing_opposite": int(filters.get("min_losing_opposite", 0) or 0) if view == "smart" else 0,
    }
    return params


def build_homepage_bootstrap_payload(conn) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    timestamps = get_status_timestamps(conn)
    has_markets_table = table_exists(conn, "active_market_outcomes")

    spotlight_universe = []
    if has_markets_table:
        spotlight_universe = query_markets(
            conn,
            sort_by="volume_usd",
            sort_dir="desc",
            limit=HOMEPAGE_SPOTLIGHT_LIMIT,
            min_liquidity=1000,
            max_spread=0.05,
        )
    playbook_previews: dict[str, list[dict[str, Any]]] = {}
    for spec in PRESET_BOOTSTRAP_SPECS:
        preview_rows: list[dict[str, Any]] = []
        if has_markets_table:
            view, _, filters = build_filters_for_preset(spec["id"], spec.get("view", "scanner"))
            preview_rows = query_markets(
                conn,
                **{
                    **_filters_to_market_query(filters, view),
                    "limit": PLAYBOOK_PREVIEW_LIMIT,
                },
            )
        playbook_previews[spec["id"]] = preview_rows[:PLAYBOOK_PREVIEW_LIMIT]

    return {
        "generated_at": generated_at,
        "market_last_updated": timestamps["last_updated"],
        "smart_money_last_updated": timestamps["smart_money_last_updated"],
        "cache_max_age_ms": HOMEPAGE_LOCAL_CACHE_MAX_AGE_MS,
        "spotlight_markets": _select_homepage_spotlights(spotlight_universe),
        "playbook_previews": playbook_previews,
    }


def build_app_bootstrap_payload(conn, *, view: str = "scanner", preset_id: Optional[str] = None) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    timestamps = get_status_timestamps(conn)
    resolved_view, active_preset_id, filters = build_filters_for_preset(preset_id, view=view)
    markets = []
    if table_exists(conn, "active_market_outcomes"):
        markets = query_markets(conn, **_filters_to_market_query(filters, resolved_view))
    tags = get_tag_stats(conn)

    return {
        "generated_at": generated_at,
        "market_last_updated": timestamps["last_updated"],
        "smart_money_last_updated": timestamps["smart_money_last_updated"],
        "view": resolved_view,
        "active_preset_id": active_preset_id,
        "filters": filters,
        "markets": markets,
        "tags": tags,
        "cache_key": build_snapshot_cache_key(resolved_view, active_preset_id),
    }


def _upsert_snapshot(conn, snapshot_key: str, payload: dict[str, Any], timestamps: dict[str, Optional[str]]) -> None:
    ensure_precomputed_snapshots_schema(conn)
    conn.execute(
        """
        INSERT INTO precomputed_snapshots (
            snapshot_key,
            payload_json,
            generated_at,
            market_last_updated,
            smart_money_last_updated
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(snapshot_key) DO UPDATE SET
            payload_json = excluded.payload_json,
            generated_at = excluded.generated_at,
            market_last_updated = excluded.market_last_updated,
            smart_money_last_updated = excluded.smart_money_last_updated
        """,
        (
            snapshot_key,
            json.dumps(payload),
            payload["generated_at"],
            timestamps["last_updated"],
            timestamps["smart_money_last_updated"],
        ),
    )


def refresh_precomputed_snapshots(conn) -> None:
    ensure_precomputed_snapshots_schema(conn)
    homepage_payload = build_homepage_bootstrap_payload(conn)
    homepage_timestamps = {
        "last_updated": homepage_payload["market_last_updated"],
        "smart_money_last_updated": homepage_payload["smart_money_last_updated"],
    }
    _upsert_snapshot(conn, "homepage", homepage_payload, homepage_timestamps)

    for view, preset_id, snapshot_key in [
        ("scanner", None, "app_default_scanner"),
        ("smart", None, "app_default_smart"),
    ]:
        payload = build_app_bootstrap_payload(conn, view=view, preset_id=preset_id)
        timestamps = {
            "last_updated": payload["market_last_updated"],
            "smart_money_last_updated": payload["smart_money_last_updated"],
        }
        _upsert_snapshot(conn, snapshot_key, payload, timestamps)

    for spec in PRESET_BOOTSTRAP_SPECS:
        payload = build_app_bootstrap_payload(conn, view=spec.get("view", "scanner"), preset_id=spec["id"])
        timestamps = {
            "last_updated": payload["market_last_updated"],
            "smart_money_last_updated": payload["smart_money_last_updated"],
        }
        _upsert_snapshot(conn, f"app_preset_{spec['id']}", payload, timestamps)


def load_precomputed_snapshot(conn, snapshot_key: str) -> Optional[dict[str, Any]]:
    ensure_precomputed_snapshots_schema(conn)
    row = conn.execute(
        "SELECT payload_json FROM precomputed_snapshots WHERE snapshot_key = ?",
        (snapshot_key,),
    ).fetchone()
    if not row or not row["payload_json"]:
        return None
    return json.loads(row["payload_json"])

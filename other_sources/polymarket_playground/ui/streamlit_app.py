import os
import io
import contextlib
import time
import json
import importlib
from typing import Optional
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Ensure repository root is importable when running from ui/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Internal modules
import events
import analyze_market_players as amp
import final_analysis as fa
import analyze_subgraph as asg  # analyze_subgraph
import get_relevant_wallets as grw
import aggregate_pnl as ap
import fetch_active_holders
import run_market_analysis
from services.db import get_connection

# Ensure we have the latest functions even if Streamlit cached an older module instance
if not hasattr(events, "refresh_active_markets_snapshot") or not hasattr(
    events, "get_market_snapshot_metadata"
):
    events = importlib.reload(events)

st.set_page_config(page_title="Polymarket Playground", layout="wide")

# --- File Paths ---
DATA_DIR = ROOT / "data"
TEST_OUTPUT_DIR = ROOT / "tests" / "output"
ACTIVE_MARKETS_FILE = DATA_DIR / "markets_current.csv"
RELEVANT_WALLETS_FILE = DATA_DIR / "relevant_wallets.json"
PNL_ANALYSIS_FILE = DATA_DIR / "subgraph_pnl_analysis.csv"
PNL_BY_USER_FILE = DATA_DIR / "pnl_by_user.csv"
MARKET_ANALYTICS_FILE = DATA_DIR / "markets_analytics.csv"
DB_FILE = DATA_DIR / "polymarket.db"

# -------- Helpers --------
# -------- Helpers --------
@st.cache_data(ttl=300)
def load_csv(path: Path | str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        return None


@st.cache_data(ttl=300)
def load_json(path: Path | str) -> Optional[list]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def format_snapshot_timestamp(value: Optional[str]) -> str:
    """Format ISO timestamps for UI display."""
    if not value:
        return "neznámé"
    try:
        dt = pd.to_datetime(value, utc=True)
    except Exception:
        return str(value)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def format_for_display(path) -> str:
    """Return repository-relative path string for UI messages."""
    path_obj = Path(path)
    try:
        return str(path_obj.relative_to(ROOT))
    except ValueError:
        return str(path_obj)


def run_with_logs(fn, *args, **kwargs) -> str:
    buf = io.StringIO()
    original_cwd = os.getcwd()
    try:
        os.chdir(ROOT)  # Change to project root
        with contextlib.redirect_stdout(buf):
            fn(*args, **kwargs)
    finally:
        os.chdir(original_cwd)  # Change back
    return buf.getvalue()


def get_output_paths(test_mode: bool) -> tuple[Path, Path]:
    if test_mode:
        return (
            TEST_OUTPUT_DIR / "final_market_analysis_test.csv",
            TEST_OUTPUT_DIR / "detailed_market_analysis_test.csv",
        )
    return (
        DATA_DIR / "final_market_analysis.csv",
        DATA_DIR / "detailed_market_analysis.csv",
    )


# -------- Sidebar --------
st.sidebar.title("Polymarket Playground")
st.sidebar.markdown("Verze s cíleným stahováním dat.")

# Global settings
st.sidebar.markdown("---")
st.sidebar.header("Globální nastavení")
test_mode = st.sidebar.checkbox(
    "Test mód (rychlý běh)",
    value=False,
    help="Použije menší počet trhů pro rychlé otestování funkčnosti. Výsledky se ukládají do složky `tests/output/`.",
)
max_markets = st.sidebar.number_input(
    "Max trhů (pouze v test módu)",
    min_value=1,
    value=3,
    step=1,
    disabled=not test_mode,
    help="Omezí počet trhů zpracovaných v testovacím módu.",
)
market_offset = st.sidebar.number_input(
    "Přeskočit prvních N trhů (Offset)",
    min_value=0,
    value=0,
    step=100,
    help="Počet trhů, které se mají přeskočit na začátku seznamu. Užitečné pro analýzu starších trhů.",
)

# Main navigation
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigace",
    ["Krok 1: Sběr dat", "Krok 2: Analýza", "Krok 3: Prohlížení výsledků", "SQL & Smart Money"],
    index=3,
    help="Vyberte fázi procesu. Postupujte od Kroku 1 k Kroku 3.",
)
st.sidebar.markdown("---")


# -------- Main Content --------
st.title("Ovládací panel")

if page == "Krok 1: Sběr dat":
    st.header("Krok 1: Cílený sběr dat")
    st.markdown(
        "Tento proces je nyní rozdělen do tří kroků, které na sebe navazují. Tlačítka se aktivují postupně."
    )

    # Check existence of files to manage button states
    markets_exist = os.path.exists(ACTIVE_MARKETS_FILE)
    wallets_exist = os.path.exists(RELEVANT_WALLETS_FILE)
    market_snapshot_meta = events.get_market_snapshot_metadata()

    # --- Step 1A: Market Snapshot ---
    st.subheader("1A: Stáhnout aktivní trhy")
    st.caption(
        "Rychlý refresh trhů – stáhne pouze aktivní kontrakty a neřeší P/L peněženek."
    )
    if st.button(
        "Spustit 1A: Stáhnout aktivní trhy",
        help="Stáhne seznam všech aktivních trhů z Polymarket API a uloží snapshot do data/.",
    ):
        with st.spinner("Stahuji všechny aktivní trhy..."):
            logs = run_with_logs(events.refresh_active_markets_snapshot)
        st.cache_data.clear()
        st.session_state.step1a_logs = logs
        st.session_state.step1a_snapshot_meta = events.get_market_snapshot_metadata()
        st.rerun()

    if "step1a_logs" in st.session_state:
        st.text_area("Log (1A)", st.session_state.step1a_logs, height=150)
        del st.session_state.step1a_logs

    if "step1a_snapshot_meta" in st.session_state:
        meta = st.session_state.step1a_snapshot_meta
        if meta:
            fetched_at = format_snapshot_timestamp(meta.get("fetched_at"))
            st.success(
                f"Snapshot dokončen: {fetched_at} · {meta.get('markets_count', 0)} trhů."
            )
        else:
            st.warning("Snapshot metadata nejsou k dispozici.")
        del st.session_state.step1a_snapshot_meta

    df_markets = load_csv(ACTIVE_MARKETS_FILE)
    if df_markets is not None:
        fetched_at = format_snapshot_timestamp(
            (market_snapshot_meta or {}).get("fetched_at")
        )
        st.success(
            f"Nalezeno `{format_for_display(ACTIVE_MARKETS_FILE)}`. "
            f"Obsahuje {len(df_markets)} trhů · snapshot: {fetched_at}."
        )
    else:
        st.info(f"Soubor `{format_for_display(ACTIVE_MARKETS_FILE)}` zatím neexistuje.")

    st.markdown("---    ")

    # --- Step 1B: Find Relevant Wallets ---
    st.subheader("1B: Najít relevantní peněženky")
    col1, col2 = st.columns(2)
    with col1:
        ui_per_market_limit = st.number_input(
            "Limit peněženek na trh (volit.)",
            min_value=0,
            value=0,
            step=10,
            help="Max. počet unikátních peněženek, které se mají sebrat na každý trh. 0 = bez limitu.",
        )
    with col2:
        ui_sleep_1b = st.number_input(
            "Sleep mezi trhy (s)",
            min_value=0.0,
            max_value=5.0,
            value=0.3,
            step=0.1,
            help="Pauza mezi požadavky v Kroku 1B pro šetrnost k API.",
        )
    if st.button(
        "Spustit 1B: Najít peněženky",
        disabled=not markets_exist,
        help="Projít stažené trhy a najít všechny unikátní účastníky.",
    ):
        with st.spinner(
            "Hledám unikátní peněženky ve všech aktivních trzích... Může to trvat několik minut."
        ):
            logs = run_with_logs(
                grw.fetch_wallets_for_active_markets,
                max_markets=(max_markets if test_mode else None),
                offset=market_offset,
                per_market_limit=(
                    int(ui_per_market_limit) if ui_per_market_limit > 0 else None
                ),
                sleep_seconds=float(ui_sleep_1b),
            )
        st.cache_data.clear()
        st.session_state.step1b_logs = logs
        st.rerun()

    if "step1b_logs" in st.session_state:
        st.text_area("Log (1B)", st.session_state.step1b_logs, height=200)
        del st.session_state.step1b_logs

    wallets = load_json(RELEVANT_WALLETS_FILE)
    if wallets is not None:
        st.success(
            f"Nalezeno `{format_for_display(RELEVANT_WALLETS_FILE)}`. Obsahuje {len(wallets)} unikátních peněženek."
        )
    else:
        st.info(
            f"Soubor `{format_for_display(RELEVANT_WALLETS_FILE)}` zatím neexistuje. Spusťte krok 1B."
        )

    st.markdown("---    ")

    # --- Step 1C: Fetch PNL for Wallets ---
    st.subheader("1C: Stáhnout P/L pro relevantní peněženky")

    with st.expander("Pokročilé nastavení 1C"):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            ui_wallet_batch_size = st.number_input(
                "Wallet batch size",
                min_value=50,
                max_value=1000,
                value=300,
                step=50,
                help="Počet peněženek v jednom `user_in` dotazu na Subgraph.",
            )
        with c2:
            ui_positions_page_size = st.number_input(
                "Positions page size",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Počet záznamů načtených v jednom stránkovaném dotazu.",
            )
        with c3:
            ui_sleep_page = st.number_input(
                "Sleep mezi stránkami (s)",
                min_value=0.0,
                max_value=5.0,
                value=0.5,
                step=0.1,
                help="Pauza mezi stránkovanými dotazy. Zvyšte při throttlingu.",
            )
        with c4:
            ui_sleep_batch = st.number_input(
                "Sleep mezi batchi (s)",
                min_value=0.0,
                max_value=10.0,
                value=0.0,
                step=0.1,
                help="Pauza mezi dávkami peněženek.",
            )
        with c5:
            ui_wallet_limit = st.number_input(
                "Wallet limit (0=all)",
                min_value=0,
                max_value=100000,
                value=0,
                step=100,
                help="Volitelný limit počtu peněženek pro rychlé testy.",
            )

    if st.button(
        "Spustit 1C: Stáhnout P/L",
        disabled=not wallets_exist,
        help="Stáhne P/L historii pouze pro nalezené relevantní peněženky.",
    ):
        with st.spinner("Stahuji P/L historii pro relevantní peněženky..."):
            logs = run_with_logs(
                asg.fetch_pnl_for_wallets,
                wallet_batch_size=int(ui_wallet_batch_size),
                positions_page_size=int(ui_positions_page_size),
                sleep_seconds_page=float(ui_sleep_page),
                sleep_seconds_batch=float(ui_sleep_batch),
                wallet_limit=(int(ui_wallet_limit) if ui_wallet_limit > 0 else None),
            )
        st.cache_data.clear()
        st.session_state.step1c_logs = logs
        st.rerun()

    if "step1c_logs" in st.session_state:
        st.text_area("Log (1C)", st.session_state.step1c_logs, height=200)
        del st.session_state.step1c_logs

    df_pnl = load_csv(PNL_ANALYSIS_FILE)
    if df_pnl is not None:
        st.success(
            f"Nalezeno `{format_for_display(PNL_ANALYSIS_FILE)}`. Obsahuje {len(df_pnl)} záznamů."
        )
    else:
        st.info(
            f"Soubor `{format_for_display(PNL_ANALYSIS_FILE)}` zatím neexistuje. Spusťte krok 1C."
        )

elif page == "Krok 2: Analýza":
    # This page remains largely the same
    st.header("Krok 2: Zpracování a analýza dat")
    st.markdown("V tomto kroku pracujete s již staženými, lokálními daty.")
    # ... (rest of the page is the same as before)
    st.subheader("Nastavení analýzy")
    top_k = st.number_input(
        "TOP_K",
        min_value=1,
        value=10,
        step=1,
        help="Počet největších hráčů (podle velikosti pozice), které chcete analyzovat na každé straně trhu (Yes/No).",
    )
    min_position = st.number_input(
        "Min. velikost pozice",
        min_value=0.0,
        value=0.0,
        step=10.0,
        format="%.2f",
        help="Zahrne do analýzy pouze pozice větší než tato hodnota.",
    )

    st.markdown("---")

    st.subheader("1. Agregace P/L dle uživatele")
    if st.button(
        "Spustit agregaci P/L (aggregate_pnl.py)",
        help="Vezme surová P/L data a sečte je pro každou unikátní peněženku.",
    ):
        with st.spinner("Agreguji P/L podle peněženky…"):
            logs = run_with_logs(ap.aggregate_pnl_by_user)
        st.cache_data.clear()
        st.session_state.agg_logs = logs
        st.rerun()

    if "agg_logs" in st.session_state:
        st.success("Hotovo – `pnl_by_user.csv` uloženo do `data/`.")
        st.text_area("Logy (aggregate_pnl.py)", st.session_state.agg_logs, height=150)
        del st.session_state.agg_logs

    df_pnl_user = load_csv(PNL_BY_USER_FILE)
    if df_pnl_user is not None:
        st.dataframe(df_pnl_user.head(), use_container_width=True)

    st.markdown("---")

    st.subheader("2. Finální analýza a reporty")
    if st.button("Spustit Analyze Market Players (Top‑K)"):
        with st.spinner("Analyzuji držitele na vybraných trzích..."):
            logs = run_with_logs(
                amp.analyze_market_players,
                top_k=top_k,
                min_position=min_position,
                test_mode=test_mode,
                max_markets=(max_markets if test_mode else None),
            )
        st.cache_data.clear()
        st.session_state.amp_logs = logs
        st.rerun()

    if "amp_logs" in st.session_state:
        st.text_area(
            "Logy (analyze_market_players.py)", st.session_state.amp_logs, height=200
        )
        del st.session_state.amp_logs

    if st.button("Spustit Final Analysis (agregace)"):
        with st.spinner("Počítám agregované metriky a detaily..."):
            logs = run_with_logs(
                fa.generate_final_analysis,
                top_k=top_k,
                min_position=min_position,
                test_mode=test_mode,
                max_markets=(max_markets if test_mode else None),
            )
        st.cache_data.clear()
        st.session_state.fa_logs = logs
        st.rerun()

    if "fa_logs" in st.session_state:
        st.text_area("Logy (final_analysis.py)", st.session_state.fa_logs, height=200)
        del st.session_state.fa_logs

elif page == "SQL & Smart Money":
    st.header("⚡️ Smart Money & SQL Lab")
    st.markdown("Analýza založená na DuckDB a živých držitelích (Active Holders).")
    
    tab_sm1, tab_sm2, tab_sm3 = st.tabs(["Smart Money Analysis", "Wallet Inspector", "SQL Lab"])
    
    with tab_sm1:
        st.subheader("1. Stáhnout aktuální pozice (Active Holders)")
        col1, col2 = st.columns(2)
        with col1:
            limit_mkts = st.number_input("Limit trhů (0=vše)", min_value=0, value=50, step=10)
        with col2:
            if st.button("Spustit Fetch Active Holders"):
                with st.spinner("Stahuji držitele a ukládám do DB..."):
                    # Convert 0 to None for the function
                    limit_val = int(limit_mkts) if limit_mkts > 0 else None
                    logs = run_with_logs(fetch_active_holders.fetch_active_holders, limit_markets=limit_val)
                    st.success("Hotovo! Data uložena do DuckDB.")
                    st.text_area("Logy", logs, height=100)
        
        st.markdown("---")
        st.subheader("2. Spustit Smart Money Analýzu")
        st.caption("Spojí aktivní držitele s historickým P/L z databáze.")
        if st.button("Spustit SQL Analýzu"):
            with st.spinner("Počítám metriky v DuckDB..."):
                logs = run_with_logs(run_market_analysis.run_market_analysis)
                st.success(
                    f"Analýza dokončena. Výstup: `{format_for_display(MARKET_ANALYTICS_FILE)}` "
                    "a tabulka `market_analytics` v DuckDB."
                )
                st.text_area("Logy", logs, height=100)
                st.cache_data.clear() # Clear CSV cache to reload new file
                st.rerun()
        
        st.markdown("---")
        st.subheader("Výsledky: Smart Markets")
        df_sm = load_csv(MARKET_ANALYTICS_FILE)
        if df_sm is not None:
            meta_cols = [
                "market_id",
                "question",
                "slug",
                "market_snapshot_at",
                "liquidity_usd",
                "volume_usd",
                "event_link",
                "snapshot_ts",
            ]
            meta_present = [c for c in meta_cols if c in df_sm.columns]
            value_cols = [c for c in df_sm.columns if c not in meta_cols]
            value_cols_sorted = sorted(value_cols)
            df_display = df_sm[meta_present + value_cols_sorted].copy()

            ratio_cols = [c for c in df_display.columns if c.startswith("smart_ratio_")]
            price_cols = [c for c in df_display.columns if c.startswith("outcome_price_")]
            num_cols = [
                c
                for c in df_display.columns
                if c not in ratio_cols + price_cols and c not in meta_cols
            ]
            df_display[num_cols + price_cols + ratio_cols] = df_display[
                num_cols + price_cols + ratio_cols
            ].apply(pd.to_numeric, errors="coerce")

            format_dict = {col: "{:.2%}" for col in ratio_cols}
            format_dict.update({col: "{:.4f}" for col in price_cols})

            st.dataframe(
                df_display.style.format(format_dict),
                use_container_width=True,
            )
        else:
            st.info(
                f"Zatím žádné výsledky. Spusťte analýzu výše pro vytvoření "
                f"`{format_for_display(MARKET_ANALYTICS_FILE)}`."
            )

    with tab_sm2:
        st.subheader("🔎 Wallet Inspector")
        wallet_addr = st.text_input("Zadejte adresu peněženky:", placeholder="0x...")
        
        if wallet_addr:
            addr_clean = wallet_addr.strip().lower()
            conn = get_connection(read_only=True)
            try:
                # 1. Get Total P/L
                res_pl = conn.execute(f"SELECT SUM(realizedPnl)/1e6 FROM user_positions WHERE user_addr = '{addr_clean}'").fetchone()
                total_pl = res_pl[0] if res_pl and res_pl[0] is not None else 0.0
                
                # 2. Get Labels
                res_lbl = conn.execute(f"SELECT label, notes, is_suspicious FROM wallet_labels WHERE user_addr = '{addr_clean}'").fetchone()
                label_str = "N/A"
                if res_lbl:
                    label_str = f"{res_lbl[0]} ({res_lbl[1]})"
                    if res_lbl[2]:
                        st.error(f"⚠️ Suspicious Wallet: {label_str}")
                    else:
                        st.info(f"Label: {label_str}")
                
                st.metric("Celkový historický P/L (Realized)", f"${total_pl:,.2f}")
                
                # 3. Top 10 Positions
                st.markdown("#### Top 10 Historických zisků")
                df_pos = conn.execute(f"""
                    SELECT id, realizedPnl/1e6 as pnl_usd, totalBought 
                    FROM user_positions 
                    WHERE user_addr = '{addr_clean}' 
                    ORDER BY realizedPnl DESC 
                    LIMIT 10
                """).df()
                st.dataframe(df_pos, use_container_width=True)
                
            except Exception as e:
                st.error(f"Chyba DB: {e}")
            finally:
                conn.close()

    with tab_sm3:
        st.subheader("🛠️ SQL Lab")
        query = st.text_area("Zadejte SQL dotaz (DuckDB):", value="SELECT * FROM wallet_labels", height=150)
        if st.button("Spustit dotaz"):
            conn = get_connection(read_only=True)
            try:
                df_res = conn.execute(query).df()
                st.dataframe(df_res, use_container_width=True)
                st.caption(f"Vráceno {len(df_res)} řádků.")
            except Exception as e:
                st.error(f"Chyba: {e}")
            finally:
                conn.close()

elif page == "Krok 3: Prohlížení výsledků":
    st.header("Krok 3: Prohlížení výsledků analýzy")
    # This page remains the same
    # ... (rest of the page is the same as before)
    agg_path, detail_path = get_output_paths(test_mode)
    agg_display = format_for_display(agg_path)
    detail_display = format_for_display(detail_path)
    st.info(
        f"Zobrazuji data pro **{'Test mód' if test_mode else 'Plný mód'}**. Výstupní soubory: `{agg_display}` a `{detail_display}`"
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Final Analysis",
            "Wallets Detail",
            "P/L by User",
            "Raw Subgraph P/L",
            "Markets Snapshot",
        ]
    )

    with tab1:
        st.subheader("Agregované metriky (Top‑K)")
        df_agg = load_csv(agg_path)
        if df_agg is None:
            st.warning(
                f"Soubor `{agg_display}` nenalezen. Spusťte 'Final Analysis' v Kroku 2."
            )
        else:
            df_markets_snapshot = load_csv(ACTIVE_MARKETS_FILE)
            df_display = df_agg.copy()
            if df_markets_snapshot is not None:
                renamed_snapshot = df_markets_snapshot.rename(
                    columns={
                        "id": "market_id",
                        "slug": "market_slug",
                        "liquidityNum": "liquidity_usd",
                        "volumeNum": "volume_usd",
                        "snapshot_fetched_at": "market_snapshot_at",
                    }
                )
                snapshot_columns = [
                    col
                    for col in [
                        "market_id",
                        "market_slug",
                        "liquidity_usd",
                        "volume_usd",
                        "market_snapshot_at",
                    ]
                    if col in renamed_snapshot.columns
                ]
                df_display = df_display.merge(
                    renamed_snapshot[snapshot_columns], on="market_id", how="left"
                )
                if "market_slug" in df_display.columns:
                    df_display["event_link"] = df_display["market_slug"].apply(
                        lambda slug: (
                            f"https://polymarket.com/event/{slug}"
                            if isinstance(slug, str) and slug
                            else None
                        )
                    )
                    df_display.drop(columns=["market_slug"], inplace=True)
                if "liquidity_usd" in df_display.columns:
                    df_display["liquidity_usd"] = pd.to_numeric(
                        df_display["liquidity_usd"], errors="coerce"
                    ).round(2)
                if "volume_usd" in df_display.columns:
                    df_display["volume_usd"] = pd.to_numeric(
                        df_display["volume_usd"], errors="coerce"
                    ).round(2)
                if "market_snapshot_at" in df_display.columns:
                    df_display["market_snapshot_at"] = df_display[
                        "market_snapshot_at"
                    ].apply(
                        lambda val: (
                            format_snapshot_timestamp(val)
                            if pd.notna(val)
                            else "neznámé"
                        )
                    )
                insert_after = "market_question"
                for col_name in [
                    "event_link",
                    "market_snapshot_at",
                    "liquidity_usd",
                    "volume_usd",
                ]:
                    if (
                        col_name in df_display.columns
                        and insert_after in df_display.columns
                    ):
                        value_series = df_display.pop(col_name)
                        insert_pos = df_display.columns.get_loc(insert_after) + 1
                        df_display.insert(insert_pos, col_name, value_series)
                        insert_after = col_name
            st.dataframe(df_display, use_container_width=True)

    with tab2:
        st.subheader("Detail peněženek (Top‑K)")
        df_detail = load_csv(detail_path)
        if df_detail is None:
            st.warning(
                f"Soubor `{detail_display}` nenalezen. Spusťte 'Final Analysis' v Kroku 2."
            )
        else:
            st.dataframe(df_detail, use_container_width=True)

    with tab3:
        st.subheader("Agregované P/L dle peněženky")
        df_user = load_csv(PNL_BY_USER_FILE)
        if df_user is None:
            st.warning(
                f"Soubor `{format_for_display(PNL_BY_USER_FILE)}` nenalezen. Spusťte agregaci v Kroku 2."
            )
        else:
            sort_col = None
            if "total_pl_usd" in df_user.columns:
                sort_col = "total_pl_usd"
            elif "total_pnl" in df_user.columns:
                sort_col = "total_pnl"
            st.dataframe(
                (
                    df_user.sort_values(by=sort_col, ascending=False)
                    if sort_col
                    else df_user
                ),
                use_container_width=True,
            )

    with tab4:
        st.subheader("Subgraph – surové pozice s nenulovým P/L")
        # IMPORTANT: Do not load full CSV to avoid OOM (3GB+)
        if not os.path.exists(PNL_ANALYSIS_FILE):
            st.warning(
                f"Soubor `{format_for_display(PNL_ANALYSIS_FILE)}` nenalezen. Spusťte krok 1C."
            )
        else:
            file_size_mb = os.path.getsize(PNL_ANALYSIS_FILE) / (1024 * 1024)
            st.warning(
                f"⚠️ Soubor je příliš velký ({file_size_mb:.1f} MB) pro plné zobrazení. Zobrazuji náhled prvních 100 řádků."
            )

            try:
                df_preview = pd.read_csv(PNL_ANALYSIS_FILE, nrows=100)
                st.dataframe(df_preview, use_container_width=True)
            except Exception as e:
                st.error(f"Chyba při načítání náhledu: {e}")

    with tab5:
        st.subheader("Snapshot trhů")
        df_markets = load_csv(ACTIVE_MARKETS_FILE)
        if df_markets is None:
            st.warning(
                f"Soubor `{format_for_display(ACTIVE_MARKETS_FILE)}` nenalezen. Spusťte krok 1A."
            )
        else:
            meta = events.get_market_snapshot_metadata()
            if meta:
                st.caption(
                    f"Snapshot: {format_snapshot_timestamp(meta.get('fetched_at'))} · "
                    f"{meta.get('markets_count', len(df_markets))} trhů."
                )
            st.dataframe(df_markets, use_container_width=True)

# Goldsky holders fetch (positions subgraph)

This script pulls **full** holders for Polymarket outcomes from the Goldsky
positions subgraph. It is not capped at top-20 the way the data-api `/holders`
endpoint is.

Endpoint used:
- `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/positions-subgraph/0.0.7/gn`

## Install

```bash
pip install requests
```

## Usage

Fetch full holders for a Yes/No market (outcomes 0 and 1):

```bash
python goldsky_holders_fetch.py \
  --condition 0xd595eb9b81885ff018738300c79047e3ec89e87294424f57a29a7fa9162bf116 \
  --outcomes 0 1 \
  --page-size 1000 \
  --max-workers 4 \
  --output data/goldsky_holders.csv
```

Counts-only (no CSV, just holder counts):

```bash
python goldsky_holders_fetch.py \
  --condition 0xd595eb9b81885ff018738300c79047e3ec89e87294424f57a29a7fa9162bf116 \
  --outcomes 0 1 \
  --counts-only
```

Multiple markets (repeat `--condition`):

```bash
python goldsky_holders_fetch.py \
  --condition 0xabc... \
  --condition 0xdef... \
  --outcomes 0 1 \
  --max-workers 8
```

## Notes

- `balance_raw` is the on-chain token balance (raw units, not USD).
- `outcome_index` is usually 0/1 for Yes/No markets.
- If you hit rate limits, reduce `--max-workers` or add `--sleep 0.2`.

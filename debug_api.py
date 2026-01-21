from main import get_markets
from fastapi import Response

try:
    markets = get_markets(Response(), limit=1)
    if markets:
        m = markets[0]
        print(f"Market ID: {m.get('market_id')} (Type: {type(m.get('market_id'))})")
        print(f"Condition ID: {m.get('condition_id')} (Type: {type(m.get('condition_id'))})")
    else:
        print("No markets found.")
except Exception as e:
    print(f"Error: {e}")

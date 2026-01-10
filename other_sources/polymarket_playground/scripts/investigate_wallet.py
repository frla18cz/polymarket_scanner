import requests

# Asset ID from the first result (last part of the ID string)
# 0xf29bb8e0712075041e87e8605b69833ef738dd4c-143...
# Let's take the first one from the previous output
asset_id_int = 143000000000000000000  # Placeholder, I need to parse the real output
# Wait, I can't copy-paste the truncation. I need to run a script that gets the FULL ID.

from services.db import get_connection

conn = get_connection(read_only=True)
addr = "0xf29bb8e0712075041e87e8605b69833ef738dd4c".lower()

# Get the full ID string
res = conn.execute(
    f"""
    SELECT id 
    FROM user_positions 
    WHERE user_addr = '{addr}' 
    ORDER BY realizedPnl DESC 
    LIMIT 1
"""
).fetchone()

full_id = res[0]
print(f"Full Position ID: {full_id}")

# Parse Asset ID (everything after the dash)
asset_id = full_id.split("-")[1]
print(f"Asset ID (Token): {asset_id}")

# Now fetch market details for this token from Gamma API
# Gamma API lets us filter by token_id
url = f"https://gamma-api.polymarket.com/markets?token_id={asset_id}"
print(f"Fetching market info from: {url}")

try:
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    if data:
        m = data[0]  # Assuming list response
        print("\n--- MARKET FOUND ---")
        print(f"Question: {m.get('question')}")
        print(f"Slug: {m.get('slug')}")
        print(
            f"Outcome: {m.get('outcome')}"
        )  # This might need parsing depending on structure
    else:
        print(
            "No market found for this token ID (might be an old/resolved market not in Gamma active list?)"
        )
except Exception as e:
    print(f"API Error: {e}")

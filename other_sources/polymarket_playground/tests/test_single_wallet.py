import requests
import json

# Address provided by the user for testing
user_address = "0x908355107b56e0a66b4fd0e06b059899aec8d27b"
url = "https://data-api.polymarket.com/closed-positions"
params = {"user": user_address, "limit": 1000}

print(f"--- Focused Test: Checking a single wallet for P/L ---")
print(f"Target Address: {user_address}")
print(f"Endpoint URL: {url}")

try:
    response = requests.get(url, params=params)
    print(f"API Status Code: {response.status_code}")
    response.raise_for_status()

    data = response.json()
    print("\nSUCCESS: API returned a valid response.")

    if data:
        total_pl = sum(item.get("pnl", 0) for item in data)
        print(f"  - Total P/L calculated: ${total_pl:,.2f}")
        print(f"  - Number of closed positions found: {len(data)}")
        print("\n  - Sample of first position:")
        print(json.dumps(data[0], indent=2))
    else:
        print(
            "  - API returned an empty list. No closed positions found for this address."
        )

except requests.exceptions.HTTPError as e:
    print(f"\nERROR: An HTTP error occurred: {e}")
    if e.response.status_code == 404:
        print(
            "  - This 404 error confirms that the API does not have a public 'closed-positions' history for this specific address."
        )
except Exception as e:
    print(f"\nERROR: A general error occurred: {e}")

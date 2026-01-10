import requests
import json

user_address = "0x908355107b56e0a66b4fd0e06b059899aec8d27b"
url = f"https://gamma-api.polymarket.com/users/{user_address}/closed-positions"

print(f"Testing endpoint for your address: {url}")

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    response.raise_for_status()

    data = response.json()
    print("SUCCESS! API returned data.")

    # Calculate P/L from the response
    total_pl = sum(item.get("pnl", 0) for item in data)
    print(f"Calculated P/L for your address: ${total_pl:,.2f}")

    # Print a sample of the data
    if data:
        print("\nSample of the first closed position:")
        print(json.dumps(data[0], indent=2))

except requests.exceptions.HTTPError as e:
    print(f"HTTP ERROR: {e}")
    if e.response.status_code == 404:
        print(
            "API returned 404 Not Found. This means no closed positions were found for this address."
        )
except requests.exceptions.RequestException as e:
    print(f"A network error occurred: {e}")

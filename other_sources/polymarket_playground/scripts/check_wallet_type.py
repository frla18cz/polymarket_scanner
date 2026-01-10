import requests
import json

# Public Polygon RPC
RPC_URL = "https://polygon-rpc.com"
WALLET_ADDR = "0xf29bb8e0712075041e87e8605b69833ef738dd4c"


def is_contract(address):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getCode",
        "params": [address, "latest"],
        "id": 1,
    }
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        result = response.json().get("result")

        # 0x means no code (EOA - User Wallet)
        # Anything else (long hex string) means Contract (Proxy/Bot)
        if result == "0x":
            return False, "EOA (Běžná peněženka)"
        else:
            return True, f"Smart Contract (Code length: {len(result)} chars)"

    except Exception as e:
        return None, f"Error: {e}"


is_c, desc = is_contract(WALLET_ADDR)
print(f"Adresa {WALLET_ADDR}:")
print(f"Typ: {desc}")

if is_c:
    print("\nVYSVĚTLENÍ:")
    print("Tato adresa je Smart Contract (pravděpodobně Proxy).")
    print(
        "Polymarket analytics weby často ukazují 'Majitele' (Owner) této proxy, nikoliv proxy samotnou."
    )

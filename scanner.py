import json
import time
import websocket

WS_URL = "wss://api.derivws.com/trading/v1/options/ws/public"

def main():
    print("DERIV MARKET SCANNER")
    print("Starting connection...")

    ws = websocket.create_connection(WS_URL, timeout=30)

    try:
        ws.send(json.dumps({
            "active_symbols": "brief",
            "req_id": 1
        }))

        while True:
            data = json.loads(ws.recv())

            if data.get("req_id") == 1:
                if "error" in data:
                    print("API ERROR:", data["error"])
                    return

                symbols = data.get("active_symbols", [])

                print("TOTAL AVAILABLE SYMBOLS:", len(symbols))
                print("--------------------------------")

                for item in symbols:
                    name = item.get("display_name", "")
                    code = item.get("symbol", "")

                    text = (name + " " + code).lower()

                    if any(word in text for word in [
                        "gold", "silver", "bitcoin",
                        "eur", "usd", "gbp", "btc"
                    ]):
                        print(name, "|", code)

                print("--------------------------------")
                print("SCAN COMPLETED")
                break

    finally:
        ws.close()


if __name__ == "__main__":
    main()

import json
import os
import sys
import time
import urllib.request

WS_URL = "wss://api.derivws.com/trading/v1/options/ws/public"

# Instruments we want to monitor.
WATCHLIST = [
    "XAUUSD",
    "XAGUSD",
    "XAUEUR",
    "XAGEUR",
    "EURUSD",
    "GBPUSD",
    "BTCUSD",
]

TIMEFRAMES = {
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
}


def get_active_symbols(ws):
    ws.send(json.dumps({"active_symbols": "brief", "req_id": 1}))

    while True:
        response = json.loads(ws.recv())

        if response.get("req_id") == 1:
            if "error" in response:
                raise RuntimeError(response["error"]["message"])

            return response.get("active_symbols", [])


def get_candles(ws, symbol, seconds):
    ws.send(json.dumps({
        "ticks_history": symbol,
        "end": "latest",
        "count": 100,
        "style": "candles",
        "granularity": seconds,
        "req_id": 2
    }))

    while True:
        response = json.loads(ws.recv())

        if response.get("req_id") == 2:
            if "error" in response:
                raise RuntimeError(response["error"]["message"])

            return response.get("candles", [])


def main():
    try:
        import websocket
    except ImportError:
        print("Missing websocket-client package.")
        sys.exit(1)

    ws = websocket.create_connection(WS_URL, timeout=20)

    try:
        available = get_active_symbols(ws)

        # Match requested instruments to Deriv's actual symbol codes.
        found = {}

        for item in available:
            name = item.get("display_name", "").upper()
            code = item.get("symbol", "")

            for wanted in WATCHLIST:
                if name == wanted:
                    found[wanted] = code

        print("DERIV MARKET SCAN")
        print("Time:", time.strftime("%Y-%m-%d %H:%M UTC"))
        print("-" * 35)

        for wanted in WATCHLIST:
            code = found.get(wanted)

            if not code:
                print(wanted, "- NOT FOUND on Deriv")
                continue

            print("\n", wanted, "(", code, ")")

            for timeframe, seconds in TIMEFRAMES.items():
                candles = get_candles(ws, code, seconds)

                if candles:
                    last = candles[-1]
                    print(
                        timeframe,
                        "Close:", last.get("close"),
                        "Candles:", len(candles)
                    )
                else:
                    print(timeframe, "- No candle data")

        print("\nScan completed.")
        print("This version checks market data only.")
        print("It does NOT generate trading signals or place trades.")

    finally:
        ws.close()


if __name__ == "__main__":
    main()

# reveal_client.py
# Reveal IN CLASS, allowed once the commit deadline has passed

import requests
from datetime import datetime, timezone

API_DEFAULT = "https://script.google.com/macros/s/REPLACE_WITH_YOUR_/exec"

# Opens right after the commit deadline (15 Nov 2026 23:59:59 Paris, UTC+1).
# Local reveal open: 2026-11-16 00:00:00 Europe/Paris  ==  2026-11-15 23:00:00 UTC
REVEAL_OPEN_UTC = datetime(2026, 11, 15, 23, 0, 0, tzinfo=timezone.utc)

def now_utc():
    return datetime.now(timezone.utc)

def main():
    print("Default API URL:\n ", API_DEFAULT)
    api = input("Paste API URL (or press Enter to use default): ").strip() or API_DEFAULT

    # Enforce reveal not before opening time
    current = now_utc()
    if current < REVEAL_OPEN_UTC:
        print("\n⛔ Reveal window is NOT open yet.")
        print("Reveal opens after the commit deadline (15 Nov 2026 23:59:59 Paris).")
        print("The reveal is done together in class.\n")
        return

    print("\n--- REVEAL PHASE (run in class) ---")
    print("Re-enter EXACTLY what you committed at home.")
    uni_id = input("Your University ID: ").strip()
    try:
        number = int(input("Your number (0..100): ").strip())
    except ValueError:
        print("Number must be an integer."); return
    if not (0 <= number <= 100):
        print("Number must be between 0 and 100."); return
    nonce = input("Your secret nonce: ").strip()
    if not nonce:
        print("Nonce cannot be empty."); return

    payload = {"kind": "reveal", "uni_id": uni_id, "number": number, "nonce": nonce}
    try:
        r = requests.post(api, json=payload, timeout=15)
        print("Server:", r.status_code, r.text)
    except Exception as e:
        print("Network error:", e)

if __name__ == "__main__":
    main()

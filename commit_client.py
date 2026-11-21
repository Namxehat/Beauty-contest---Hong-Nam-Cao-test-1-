# commit_client.py
# Commit AT HOME, allowed until 15 Nov 2026 23:59:59 Europe/Paris

import hashlib, requests
from datetime import datetime, timezone

API_DEFAULT = "https://script.google.com/macros/s/REPLACE_WITH_YOUR_/exec"

# Paris is UTC+1 (CET) on 15 Nov 2026 (DST ended 25 Oct 2026). We enforce using UTC to avoid tz issues.
# Local deadline: 2026-11-15 23:59:59 Europe/Paris  ==  2026-11-15 22:59:59 UTC
COMMIT_DEADLINE_UTC = datetime(2026, 11, 21, 22, 59, 59, tzinfo=timezone.utc)

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def now_utc():
    return datetime.now(timezone.utc)

def main():
    print("Default API URL:\n ", API_DEFAULT)
    api = input("Paste API URL (or press Enter to use default): ").strip() or API_DEFAULT

    # Enforce deadline in UTC
    current = now_utc()
    if current > COMMIT_DEADLINE_UTC:
        print("\n⛔ Commit window is CLOSED.")
        print("Commit deadline (local Paris): 15 Nov 2026 23:59:59")
        print("Commit deadline (UTC):         15 Nov 2026 22:59:59\n")
        return

    print("\n--- COMMIT PHASE (run at home before 15 Nov 2026, 23:59:59 Paris) ---")
    uni_id = input("Your University ID: ").strip()
    try:
        number = int(input("Choose your number (0..100): ").strip())
    except ValueError:
        print("Number must be an integer."); return
    if not (0 <= number <= 100):
        print("Number must be between 0 and 100."); return
    nonce = input("Choose a secret nonce (keep it safe): ").strip()
    if not nonce:
        print("Nonce cannot be empty."); return

    preimage = f"{uni_id}|{number}|{nonce}"
    commit_hash = sha256(preimage)

    print("\nYour commit hash:", commit_hash)
    print("Write this down (you must re-enter it in class):")
    print("PREIMAGE:", preimage)

    payload = {"kind": "commit", "uni_id": uni_id, "commit": commit_hash}
    try:
        r = requests.post(api, json=payload, timeout=15)
        print("Server:", r.status_code, r.text)
    except Exception as e:
        print("Network error:", e)

if __name__ == "__main__":
    main()

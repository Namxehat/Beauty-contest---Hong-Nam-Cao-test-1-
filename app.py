# -*- coding: utf-8 -*-
"""
Streamlit frontend for the Decentralized Beauty Contest Game.
Integrates commit_client.py, reveal_client.py, and merge_consensus_from_api.py.
"""

from statistics import mean
import pandas as pd
import requests
import streamlit as st

import commit_client as cc
import merge_consensus_from_api as mc
import reveal_client as rc

st.set_page_config(page_title="Decentralized Beauty Contest Game", layout="wide")
st.title("Decentralized Beauty Contest Game")

# Sidebar configuration & navigation
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input(
    "Google Apps Script API URL (/exec)",
    value=cc.API_DEFAULT,
).strip()

page = st.sidebar.selectbox("Phase", ["Commit", "Reveal", "Results"])


def compute_consensus(base_url: str):
    """Fetch commits & reveals from the API and compute verified scores/winners."""
    commits_url = f"{base_url}?table=commits"
    reveals_url = f"{base_url}?table=reveals"

    commits_raw = mc.get_csv(commits_url)
    reveals_raw = mc.get_csv(reveals_url)

    commits = {}
    for r in commits_raw:
        uid = (r.get("uni_id") or "").strip()
        ch = (r.get("commit") or "").strip()
        ts = (r.get("timestamp_utc") or "").strip()
        if not uid or not ch:
            continue
        commits.setdefault(uid, []).append({
            "timestamp_utc": ts,
            "ts_parsed": mc.parse_ts(ts),
            "uni_id": uid,
            "commit": ch,
        })

    reveals = {}
    for r in reveals_raw:
        uid = (r.get("uni_id") or "").strip()
        num = (r.get("number") or "").strip()
        nonce = (r.get("nonce") or "").strip()
        ts = (r.get("timestamp_utc") or "").strip()
        if not uid or not num or not nonce:
            continue
        reveals.setdefault(uid, []).append({
            "timestamp_utc": ts,
            "ts_parsed": mc.parse_ts(ts),
            "uni_id": uid,
            "number_raw": num,
            "nonce": nonce,
        })

    verified_rows = []
    matched_commits = {}

    for uid, rlist in reveals.items():
        rlist_sorted = sorted(rlist, key=lambda x: (x["ts_parsed"] or mc.datetime.min))
        latest_rev = rlist_sorted[-1]
        ts_rev = latest_rev["ts_parsed"] or mc.datetime.min

        try:
            num = int(latest_rev["number_raw"])
        except Exception:
            num = None

        cands = [
            c for c in commits.get(uid, [])
            if (c["ts_parsed"] or mc.datetime.min) <= ts_rev
        ]
        cands.sort(key=lambda x: (x["ts_parsed"] or mc.datetime.min))
        chosen_commit = cands[-1] if cands else None
        if chosen_commit:
            matched_commits[uid] = chosen_commit

        reason = "ok"
        verified = False
        if chosen_commit is None:
            reason = "no_commit_before_reveal"
        elif num is None:
            reason = "number_not_int"
        elif not (mc.ALLOWED_MIN <= num <= mc.ALLOWED_MAX):
            reason = "out_of_range"
        else:
            pre = f"{uid}|{num}|{latest_rev['nonce']}"
            verified = mc.sha256(pre) == chosen_commit["commit"]
            if not verified:
                reason = "hash_mismatch"

        verified_rows.append({
            "uni_id": uid,
            "timestamp_utc": latest_rev["timestamp_utc"],
            "number": "" if num is None else str(num),
            "nonce": latest_rev["nonce"],
            "commit": chosen_commit["commit"] if chosen_commit else "",
            "preimage_hash": "" if num is None else mc.sha256(f"{uid}|{num}|{latest_rev['nonce']}"),
            "verified": "True" if verified else "False",
            "reason": reason,
        })

    valid = [
        (r["uni_id"], int(r["number"]))
        for r in verified_rows
        if r["verified"] == "True" and r["number"] != ""
    ]

    if valid:
        avg_val = mean(n for _, n in valid)
        target = mc.K_FACTOR * avg_val
        distances = [(uid, n, abs(n - target)) for uid, n in valid]
        min_dist = min(d for _, _, d in distances)
        winners = [(uid, n, d) for uid, n, d in distances if abs(d - min_dist) < 1e-12]
    else:
        avg_val = target = min_dist = None
        winners = []

    for r in verified_rows:
        if r["verified"] == "True" and target is not None:
            r["distance"] = f"{abs(int(r['number']) - target):.6f}"
        else:
            r["distance"] = ""

    leaderboard = sorted(
        verified_rows,
        key=lambda r: (r["verified"] != "True", r.get("distance", "ZZZ"), r["uni_id"]),
    )

    return {
        "matched_commits": sorted(
            matched_commits.values(), key=lambda r: (r["uni_id"], r["timestamp_utc"])
        ),
        "verified_reveals": sorted(
            [r for r in verified_rows if r["verified"] == "True"],
            key=lambda r: (r["uni_id"], r["timestamp_utc"]),
        ),
        "leaderboard": leaderboard,
        "valid_count": len(valid),
        "avg_val": avg_val,
        "target": target,
        "min_dist": min_dist,
        "winners": winners,
    }


def save_output_files(data):
    """Write the same CSV and TXT files generated by merge_consensus_from_api.py."""
    mc.write_csv(
        mc.OUT_COMMITS,
        ["timestamp_utc", "uni_id", "commit"],
        data["matched_commits"],
    )
    mc.write_csv(
        mc.OUT_REVEALS,
        ["timestamp_utc", "uni_id", "number", "nonce", "preimage_hash", "verified"],
        data["verified_reveals"],
    )
    mc.write_csv(
        mc.OUT_LEADER,
        ["uni_id", "number", "verified", "reason", "distance", "commit", "nonce", "timestamp_utc"],
        data["leaderboard"],
    )
    with open(mc.OUT_RESULTS, "w", encoding="utf-8") as f:
        f.write("=== CLASS RESULTS (Latest-Attempt Consensus) ===\n")
        f.write(f"k_factor = {mc.K_FACTOR}\n")
        if data["valid_count"] > 0:
            f.write(f"participants_counted = {data['valid_count']}\n")
            f.write(f"average = {data['avg_val']:.6f}\n")
            f.write(f"target = {data['target']:.6f}\n")
            f.write(f"min_distance = {data['min_dist']:.6f}\n")
            f.write("winners:\n")
            for uid, n, d in data["winners"]:
                f.write(f"  - {uid} with {n} (distance {d:.6f})\n")
        else:
            f.write("No valid verified reveals. Cannot compute winners.\n")


# --- PAGES ---
if page == "Commit":
    st.header("Commit Phase")
    st.write("Submit your hashed commitment before the deadline.")

    current = cc.now_utc()
    st.caption(f"Commit deadline (UTC): `{cc.COMMIT_DEADLINE_UTC.isoformat()}` | Current UTC: `{current.isoformat()}`")

    if current > cc.COMMIT_DEADLINE_UTC:
        st.error("Commit window is CLOSED.")
    else:
        with st.form("commit_form"):
            uni_id = st.text_input("Your University ID").strip()
            number = st.number_input(
                "Choose your number (0..100)",
                min_value=mc.ALLOWED_MIN,
                max_value=mc.ALLOWED_MAX,
                step=1,
                value=50,
            )
            nonce = st.text_input("Choose a secret nonce (keep it safe)", type="password").strip()
            submitted = st.form_submit_button("Generate & Submit Commit")

        if submitted:
            if not api_url or "REPLACE_WITH_YOUR_" in api_url:
                st.warning("Please set a valid API URL in the sidebar before submitting.")
            elif not uni_id:
                st.error("University ID cannot be empty.")
            elif not nonce:
                st.error("Nonce cannot be empty.")
            else:
                preimage = f"{uni_id}|{int(number)}|{nonce}"
                commit_hash = cc.sha256(preimage)

                st.info("Save your preimage and commit hash—you will need them for the Reveal phase:")
                st.code(f"Commit Hash: {commit_hash}\nPreimage:    {preimage}", language="text")

                payload = {"kind": "commit", "uni_id": uni_id, "commit": commit_hash}
                try:
                    resp = requests.post(api_url, json=payload, timeout=15)
                    st.success(f"Server response ({resp.status_code}): {resp.text}")
                except Exception as exc:
                    st.error(f"Network error: {exc}")

elif page == "Reveal":
    st.header("Reveal Phase")
    st.write("Reveal your previous choice using the exact University ID, number, and nonce.")

    current = rc.now_utc()
    st.caption(f"Reveal opens (UTC): `{rc.REVEAL_OPEN_UTC.isoformat()}` | Current UTC: `{current.isoformat()}`")

    if current < rc.REVEAL_OPEN_UTC:
        st.warning("Reveal window is NOT open yet.")
    else:
        with st.form("reveal_form"):
            uni_id = st.text_input("Your University ID").strip()
            number = st.number_input(
                "Your number (0..100)",
                min_value=mc.ALLOWED_MIN,
                max_value=mc.ALLOWED_MAX,
                step=1,
                value=50,
            )
            nonce = st.text_input("Your secret nonce", type="password").strip()
            submitted = st.form_submit_button("Submit Reveal")

        if submitted:
            if not api_url or "REPLACE_WITH_YOUR_" in api_url:
                st.warning("Please set a valid API URL in the sidebar before submitting.")
            elif not uni_id:
                st.error("University ID cannot be empty.")
            elif not nonce:
                st.error("Nonce cannot be empty.")
            else:
                payload = {
                    "kind": "reveal",
                    "uni_id": uni_id,
                    "number": int(number),
                    "nonce": nonce,
                }
                try:
                    resp = requests.post(api_url, json=payload, timeout=15)
                    st.success(f"Server response ({resp.status_code}): {resp.text}")
                except Exception as exc:
                    st.error(f"Network error: {exc}")

elif page == "Results":
    st.header("Consensus Results")
    st.write(f"Target factor (`k`): **{mc.K_FACTOR:.4f}** | Allowed range: **[{mc.ALLOWED_MIN}, {mc.ALLOWED_MAX}]**")

    save_files = st.checkbox("Also save CSV/TXT output files locally (`merged_*.csv`, `class_leaderboard.csv`, `class_results.txt`)", value=False)

    if st.button("Fetch & Compute Consensus"):
        if not api_url or "REPLACE_WITH_YOUR_" in api_url:
            st.warning("Please set a valid API URL in the sidebar first.")
        else:
            try:
                with st.spinner("Fetching commits & reveals and verifying hashes..."):
                    data = compute_consensus(api_url)
                    if save_files:
                        save_output_files(data)

                if data["valid_count"] > 0:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Verified Participants", data["valid_count"])
                    c2.metric("Class Average", f"{data['avg_val']:.4f}")
                    c3.metric("Target (2/3 Avg)", f"{data['target']:.4f}")
                    c4.metric("Min Distance", f"{data['min_dist']:.4f}")

                    winner_str = ", ".join(
                        f"**{uid}** (number: `{n}`, distance: `{d:.4f}`)"
                        for uid, n, d in data["winners"]
                    )
                    st.success(f"Winner(s): {winner_str}")
                else:
                    st.info("No valid verified reveals found yet.")

                st.subheader("Leaderboard")
                if data["leaderboard"]:
                    st.dataframe(pd.DataFrame(data["leaderboard"]), use_container_width=True)
                else:
                    st.write("No reveal entries to display.")

                if save_files:
                    st.caption(
                        f"Saved `{mc.OUT_COMMITS}`, `{mc.OUT_REVEALS}`, `{mc.OUT_LEADER}`, and `{mc.OUT_RESULTS}`."
                    )
            except Exception as exc:
                st.error(f"Failed to fetch or compute results: {exc}")

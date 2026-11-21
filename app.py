# -*- coding: utf-8 -*-
"""
Streamlit frontend for the Decentralized Beauty Contest Game (French Tricolor Theme).
Integrates commit_client.py, reveal_client.py, and merge_consensus_from_api.py.
"""

from html import escape
from statistics import mean
import pandas as pd
import requests
import streamlit as st

import commit_client as cc
import merge_consensus_from_api as mc
import reveal_client as rc

st.set_page_config(
    page_title="Decentralized Beauty Contest Game 🇫🇷",
    page_icon="🇫🇷",
    layout="wide",
)

# French Tricolor Theme Styling
st.markdown(
    """
    <style>
        :root {
            --fr-blue: #002654;
            --fr-white: #FFFFFF;
            --fr-red: #ED2939;
            --fr-bg: #F4F7FB;
            --fr-border: #D6E0EE;
        }

        .stApp {
            background: linear-gradient(180deg, #F7F9FC 0%, #EEF2F8 100%);
        }

        /* Tricolor header banner */
        .tricolor-banner {
            display: flex;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 6px 18px rgba(0, 38, 84, 0.14);
            margin-bottom: 1.25rem;
            border: 1px solid var(--fr-border);
        }
        .tricolor-stripe-blue {
            width: 14px;
            background-color: var(--fr-blue);
        }
        .tricolor-stripe-white {
            width: 10px;
            background-color: var(--fr-white);
        }
        .tricolor-stripe-red {
            width: 14px;
            background-color: var(--fr-red);
        }
        .tricolor-content {
            flex: 1;
            background: linear-gradient(90deg, #002654 0%, #0B3B75 55%, #8F1D2C 100%);
            color: #FFFFFF;
            padding: 1.15rem 1.5rem;
        }
        .tricolor-content h1 {
            color: #FFFFFF !important;
            margin: 0 !important;
            font-size: 1.85rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.2px;
        }
        .tricolor-content p {
            color: #E8EEF7 !important;
            margin: 0.35rem 0 0 0 !important;
            font-size: 0.98rem;
        }

        /* Section headers */
        .phase-header {
            border-left: 6px solid var(--fr-blue);
            border-right: 6px solid var(--fr-red);
            background-color: #FFFFFF;
            padding: 0.65rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0, 38, 84, 0.06);
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid var(--fr-border);
            border-top: 4px solid var(--fr-blue);
            border-radius: 10px;
            padding: 0.85rem 1rem;
            box-shadow: 0 2px 8px rgba(0, 38, 84, 0.05);
        }
        div[data-testid="stMetric"]:nth-child(even) {
            border-top-color: var(--fr-red);
        }

        /* Top 5 Winner Box */
        .winners-box {
            background: #FFFFFF;
            border: 1px solid var(--fr-border);
            border-left: 6px solid var(--fr-blue);
            border-right: 6px solid var(--fr-red);
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            margin: 1rem 0 1.4rem 0;
            box-shadow: 0 4px 14px rgba(0, 38, 84, 0.08);
        }
        .winners-box-title {
            color: var(--fr-blue);
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            padding-bottom: 0.45rem;
            border-bottom: 2px solid #EEF2F8;
        }
        .winner-item {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 0.6rem;
            padding: 0.65rem 0.9rem;
            margin-bottom: 0.55rem;
            border-radius: 8px;
            background: #F8FAFD;
            border: 1px solid #E1E8F2;
        }
        .winner-item:last-child {
            margin-bottom: 0;
        }
        .winner-rank-1 {
            background: linear-gradient(90deg, rgba(0, 38, 84, 0.08) 0%, rgba(237, 41, 57, 0.08) 100%);
            border: 1px solid #B8C9E2;
        }
        .winner-left {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            color: #002654;
            font-weight: 700;
            font-size: 1rem;
        }
        .winner-details {
            color: #334155;
            font-size: 0.92rem;
        }
        .winner-badge {
            display: inline-block;
            padding: 0.15rem 0.55rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            background-color: #002654;
            color: #FFFFFF;
            margin-left: 0.35rem;
        }
        .winner-badge-red {
            background-color: #ED2939;
        }

        /* Primary buttons */
        .stButton > button,
        .stFormSubmitButton > button {
            background-color: var(--fr-blue) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--fr-blue) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 0.45rem 1.1rem !important;
            transition: all 0.2s ease;
        }
        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            background-color: var(--fr-red) !important;
            border-color: var(--fr-red) !important;
            color: #FFFFFF !important;
        }

        /* Sidebar accent */
        section[data-testid="stSidebar"] {
            border-right: 4px solid var(--fr-blue);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="tricolor-banner">
        <div class="tricolor-stripe-blue"></div>
        <div class="tricolor-stripe-white"></div>
        <div class="tricolor-stripe-red"></div>
        <div class="tricolor-content">
            <h1>🇫🇷 Decentralized Beauty Contest Game</h1>
            <p>Cryptographic Commit–Reveal Consensus • Target = (2/3) × Class Average</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar configuration & navigation
st.sidebar.markdown("### 🇫🇷 Configuration")
api_url = st.sidebar.text_input(
    "Google Apps Script API URL (/exec)",
    value=cc.API_DEFAULT,
).strip()

page = st.sidebar.selectbox("Phase", ["Commit", "Reveal", "Results"])
st.sidebar.markdown("---")
st.sidebar.caption("🔵 Bleu • ⚪ Blanc • 🔴 Rouge")


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
        key=lambda r: (
            r["verified"] != "True",
            float(r["distance"]) if r["distance"] != "" else float("inf"),
            r["uni_id"],
        ),
    )

    top_5 = [
        {
            "rank": idx,
            "uni_id": r["uni_id"],
            "number": int(r["number"]),
            "distance": float(r["distance"]),
            "timestamp_utc": r["timestamp_utc"],
            "commit": r["commit"],
        }
        for idx, r in enumerate(
            [row for row in leaderboard if row["verified"] == "True"][:5],
            start=1,
        )
    ]

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
        "top_5": top_5,
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


def render_top_5_box(top_5: list):
    """Render a styled text box highlighting the Top 5 winners."""
    medals = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🏅", 5: "🏅"}
    items_html = []
    for entry in top_5:
        rank = entry["rank"]
        medal = medals.get(rank, "🏅")
        uid_safe = escape(str(entry["uni_id"]))
        ts_safe = escape(str(entry["timestamp_utc"])) or "N/A"
        commit_short = escape(str(entry["commit"])[:12]) + "..." if entry["commit"] else "N/A"
        highlight_cls = "winner-item winner-rank-1" if rank == 1 else "winner-item"

        items_html.append(
            f"""
            <div class="{highlight_cls}">
                <div class="winner-left">
                    <span>{medal} #{rank} — {uid_safe}</span>
                    <span class="winner-badge">Choice: {entry['number']}</span>
                    <span class="winner-badge winner-badge-red">Distance: {entry['distance']:.4f}</span>
                </div>
                <div class="winner-details">
                    Commit: <code>{commit_short}</code> &nbsp;|&nbsp; Revealed (UTC): <code>{ts_safe}</code>
                </div>
            </div>
            """
        )

    st.markdown(
        f"""
        <div class="winners-box">
            <div class="winners-box-title">🏆 Top 5 Winners (Closest to Target)</div>
            {''.join(items_html)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- PAGES ---
if page == "Commit":
    st.markdown(
        '<div class="phase-header"><h2 style="margin:0;color:#002654;">🔒 Commit Phase</h2>'
        '<span style="color:#4A5568;">Submit your hashed commitment before the deadline</span></div>',
        unsafe_allow_html=True,
    )

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
    st.markdown(
        '<div class="phase-header"><h2 style="margin:0;color:#002654;">🔓 Reveal Phase</h2>'
        '<span style="color:#4A5568;">Reveal your previous choice using the exact University ID, number, and nonce</span></div>',
        unsafe_allow_html=True,
    )

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
    st.markdown(
        '<div class="phase-header"><h2 style="margin:0;color:#002654;">🏆 Consensus Results</h2>'
        f'<span style="color:#4A5568;">Target factor (k): <b>{mc.K_FACTOR:.4f}</b> | Allowed range: <b>[{mc.ALLOWED_MIN}, {mc.ALLOWED_MAX}]</b></span></div>',
        unsafe_allow_html=True,
    )

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

                    render_top_5_box(data["top_5"])
                else:
                    st.info("No valid verified reveals found yet.")

                st.subheader("Full Leaderboard")
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

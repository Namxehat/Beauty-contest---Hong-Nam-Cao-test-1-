# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 23:10:04 2026

@author: admins
"""

import streamlit as st

st.title("Decentralized Beauty Contest Game")

page = st.sidebar.selectbox("Phase",["Commit","Reveal","Results"])

if page == "Commit":
    st.header("Commit Phase")
    st.write("Submit your hashed commitment")

elif page == "Reveal":
    st.header("Reveal Phase")
    st.write("Reveal your previous choice")

elif page == "Results":
    st.header("Consensus Results")
    st.write("Leaderboard will appear here")
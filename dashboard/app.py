"""
dashboard/app.py — the human-facing view of the same knowledge base the
ticket_kb_server.py MCP tool reads. Same data, two front doors: one for a
person browsing in a tab, one for an agent calling a tool.

Run with:  streamlit run dashboard/app.py
"""

import json
from pathlib import Path

import streamlit as st

KB_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.json"

st.set_page_config(page_title="Internal Issue Knowledge Base", layout="wide")

st.title("Internal Issue Knowledge Base")
st.caption("Past resolved tickets — what a support engineer already opens before filing a new one.")

kb = json.loads(KB_PATH.read_text())

all_tags = sorted({tag for entry in kb for tag in entry["tags"]})
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Filter")
    selected_tags = st.multiselect("Tags", all_tags)
    search = st.text_input("Search title or symptom")

with col2:
    st.subheader(f"{len(kb)} known issues")

    filtered = kb
    if selected_tags:
        filtered = [e for e in filtered if any(t in e["tags"] for t in selected_tags)]
    if search:
        needle = search.lower()
        filtered = [
            e for e in filtered
            if needle in e["title"].lower() or needle in e["symptom"].lower()
        ]

    for entry in filtered:
        with st.expander(f"{entry['id']} — {entry['title']}"):
            st.markdown(f"**Tags:** {', '.join(entry['tags'])}")
            st.markdown(f"**Symptom:** {entry['symptom']}")
            st.markdown(f"**Resolution:** {entry['resolution']}")
            st.caption(f"Resolved by {entry['resolved_by']} on {entry['date']}")

    if not filtered:
        st.info("No matching issues.")

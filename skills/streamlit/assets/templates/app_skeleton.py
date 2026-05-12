from __future__ import annotations

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Data App", layout="wide")


@st.cache_data(ttl="10m", show_spinner="Loading data...")
def load_data(source: str) -> pd.DataFrame:
    return pd.read_csv(source)


def init_state() -> None:
    st.session_state.setdefault("filters", {})


init_state()
st.title("Data App")

with st.sidebar.form("filters"):
    source = st.text_input("CSV path", value="data.csv")
    submitted = st.form_submit_button("Load")

if submitted:
    st.session_state["filters"] = {"source": source}

active_source = st.session_state["filters"].get("source", "data.csv")
data = load_data(active_source)
st.dataframe(data, use_container_width=True)

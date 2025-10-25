import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import subprocess
import time

st.set_page_config(page_title="AI-Powered Lead Dashboard", layout="wide")

st.title("AI-Powered Lead Intelligence Dashboard")
st.markdown("A quick view of enriched and routed marketing leads processed by the AI pipeline.")

# --- Load data ---
OUTPUT_PATH = Path("../outputs/enriched_leads.json").resolve()

if not OUTPUT_PATH.exists():
    info_box = st.info("Generating enriched leads... please wait.")
    status_box = st.empty()
    status_box.write("Running lead enrichment pipeline...")
    try:
        subprocess.run(
            ["python", str(Path(__file__).resolve().parent / "processdata.py")],
            check=True,
            cwd=Path(__file__).resolve().parent,
        )
    except subprocess.CalledProcessError as exc:
        status_box.error(f"Failed to generate leads: {exc}")
        time.sleep(0.6)
        st.stop()
    else:
        status_box.success("Enriched leads generated successfully.")
        time.sleep(0.8)
    finally:
        info_box.empty()
        status_box.empty()

try:
    data = pd.read_json(OUTPUT_PATH)
except Exception as exc:
    st.error(f"Unable to load enriched_leads.json: {exc}")
    st.stop()

# --- Metrics Summary ---
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Total Leads", len(data))
col2.metric("High Urgency Leads", int((data["urgency"] == "High").sum()))
col3.metric("Decision Makers", int((data["persona_type"] == "Decision Maker").sum()))

# --- Distribution Charts ---
st.subheader("Distribution Insights")
tab1, tab2, tab3 = st.tabs([ "By Assigned Team","By Persona Type", "By Urgency" ])

with tab1:
    fig = px.histogram(data, x="assigned_team", color="urgency", title="Lead Routing by Team")
    st.plotly_chart(fig, config={"responsive": True}, use_container_width=True)

with tab2:
    fig = px.histogram(
        data,
        x="persona_type",
        color="persona_type",
        title="Lead Distribution by Persona Type",
        color_discrete_sequence=["#EF553B","#636EFA", "#00CC96"],  # custom colors
    )
    st.plotly_chart(fig, config={"responsive": True}, use_container_width=True)

with tab3:
    fig = px.histogram(data, x="urgency", color="urgency", title="Lead Distribution by Urgency")
    st.plotly_chart(fig, config={"responsive": True}, use_container_width=True)

# --- Data Table ---
st.subheader("Enriched Lead Data")
st.dataframe(data, use_container_width=True, hide_index=True)

# --- Download Button ---
st.download_button(
    label="Download Enriched Leads JSON",
    data=data.to_json(orient="records", indent=2),
    file_name="enriched_leads.json",
    mime="application/json",
)

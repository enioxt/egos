#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""incident_pattern_dashboard.py

Display functions for the Incident Pattern Analysis page within the EGOS Streamlit
Dashboard.  Uses existing Parquet & JSON outputs from the ROI pipeline.

If data is missing, falls back to synthetic placeholders so the page still renders.

This module is imported by `core/streamlit_app.py`.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st

logger = logging.getLogger("EGOS.IncidentPatternDashboard")

# --- File locations (adjust if pipeline paths change) ---
DATA_DIR = Path("C:/EGOS/data/roi")
INCIDENTS_PATH = DATA_DIR / "master_incidents.parquet"
ROI_JSON_PATH = DATA_DIR / "latest_roi.json"

# --- Synthetic fallback helpers ------------------------------------------------

def _synthetic_incidents(n: int = 500) -> pd.DataFrame:
    import numpy as np
    import random, string
    sectors = [
        "mobility",
        "manufacturing",
        "media",
        "public_safety",
        "healthcare",
        "education",
        "financial",
    ]
    rng = pd.Timestamp.now().floor("D") - pd.to_timedelta(np.random.randint(0, 90, n), unit="D")
    data = {
        "estimated_cost_usd": np.random.lognormal(mean=13, sigma=1, size=n),
        "severity_score": np.random.choice([1, 2, 3], size=n, p=[0.6, 0.3, 0.1]),
        "sector": np.random.choice(sectors, size=n),
        "incident_id": ["synth_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8)) for _ in range(n)],
        "incident_date": rng,
    }
    return pd.DataFrame(data)


def _synthetic_roi() -> Dict:
    return {
        "average_avoided_cost": 1_000_000,
        "total_costs": 100_000,
        "roi_pct": 900,
        "sectors": {
            "mobility": {"average_avoided_cost": 2_400_000, "roi_pct": 15000},
            "media": {"average_avoided_cost": 140_000, "roi_pct": 800},
        },
    }

# --- Main display --------------------------------------------------------------

def display_incident_pattern_dashboard(live_data: bool = False):  # signature mirrors others
    """Render the Incident Pattern Analysis page inside the Streamlit app."""

    st.title("📊 Incident Pattern Analysis")
    
    # Load data with graceful fallback
    try:
        incidents_df = pd.read_parquet(INCIDENTS_PATH)
        logger.info("Loaded incidents parquet for dashboard.")
    except Exception as exc:
        logger.warning(f"Could not load incidents parquet ({INCIDENTS_PATH}): {exc}. Using synthetic data.")
        incidents_df = _synthetic_incidents()

    try:
        roi_data = json.loads(Path(ROI_JSON_PATH).read_text())
        logger.info("Loaded ROI JSON for dashboard.")
    except Exception as exc:
        logger.warning(f"Could not load ROI JSON ({ROI_JSON_PATH}): {exc}. Using synthetic data.")
        roi_data = _synthetic_roi()

    # --- KPI cards -------------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Avoided Cost", f"${roi_data.get('average_avoided_cost', 0):,.0f}")
    with col2:
        st.metric("Total Implementation Cost", f"${roi_data.get('total_costs', 0):,.0f}")
    with col3:
        st.metric("Overall ROI %", f"{roi_data.get('roi_pct', 0):.1f}%")

    st.markdown("---")

    # --- Sector ROI Bar Chart --------------------------------------------------
    sectors = roi_data.get("sectors", {})
    if sectors:
        sector_df = pd.DataFrame([
            {"sector": k, "roi_pct": v.get("roi_pct", 0)} for k, v in sectors.items()
        ])
        fig_bar = px.bar(sector_df, x="sector", y="roi_pct", title="ROI % by Sector", color="sector")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sector-level ROI data not available.")

    # --- Incident Heatmap ------------------------------------------------------
    if not incidents_df.empty:
        # Bucket dates to week for readability
        incidents_df["week"] = incidents_df["incident_date"].dt.to_period("W").dt.start_time
        
        # Check if source column exists for data source visualization
        if 'source' in incidents_df.columns:
            # Group by source, sector, and week
            heat_df = (
                incidents_df.groupby(["source", "sector", "week"]).size().reset_index(name="count")
            )
            if not heat_df.empty:
                fig_heat = px.density_heatmap(
                    heat_df,
                    x="week",
                    y="sector",
                    z="count",
                    facet_col="source",  # Separate by data source
                    color_continuous_scale="Viridis",
                    title="Incident Volume by Source, Sector & Week",
                )
                fig_heat.update_xaxes(dtick="M1", tickformat="%b %d")
                st.plotly_chart(fig_heat, use_container_width=True)
                
                # Also show source distribution
                source_counts = incidents_df['source'].value_counts().reset_index()
                source_counts.columns = ['source', 'count']
                fig_source = px.pie(
                    source_counts, 
                    values='count', 
                    names='source',
                    title="Incident Distribution by Source",
                    hole=0.4,  # Donut chart
                )
                st.plotly_chart(fig_source, use_container_width=True)
        else:
            # Original heatmap without source differentiation
            heat_df = (
                incidents_df.groupby(["sector", "week"]).size().reset_index(name="count")
            )
            if not heat_df.empty:
                fig_heat = px.density_heatmap(
                    heat_df,
                    x="week",
                    y="sector",
                    z="count",
                    color_continuous_scale="Viridis",
                    title="Incident Volume by Sector & Week",
                )
                fig_heat.update_xaxes(dtick="M1", tickformat="%b %d")
                st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Incident data not available.")

    # --- Relation Graph (beta) -----------------------------------------------
    with st.expander("Relation Graph (beta)"):
        if incidents_df.empty:
            st.info("No incident text available for relation extraction.")
        else:
            sample_texts = incidents_df["description"].dropna().head(50).tolist()
            try:
                import requests

                resp = requests.post(
                    "http://localhost:8000/extract",
                    json={"texts": sample_texts},
                    timeout=3,
                )
                if resp.status_code == 200:
                    relations = resp.json().get("relations", [])
                    rel_count = sum(len(r) for r in relations)
                    st.success(f"Relation service responded with {rel_count} triples (dummy model). Visualization TBD.")
                else:
                    st.warning("Relation service error: " + resp.text[:200])
            except requests.exceptions.ConnectionError:
                st.info("Relation extraction service not running. Start it with:\n  uvicorn services.relation_extraction.service:app --reload")
            except Exception as exc:
                st.warning(f"Unexpected error contacting relation service: {exc}")


# When executed directly (development), render standalone
if __name__ == "__main__":
    import streamlit as st
    display_incident_pattern_dashboard()

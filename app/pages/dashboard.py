"""Dashboard page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

from state import get_state
from components.metrics import render_summary_metrics
from components.charts import render_trend_chart, render_comparison_bar


def render_dashboard():
    """Render the main dashboard."""
    st.subheader("Dashboard")
    
    firm_id = get_state("firm_id", 1)
    period = get_state("period", 0)
    
    # Summary metrics section
    st.write("### Key Metrics")
    
    # Get data from state or use defaults
    results = get_state("results")
    
    if results:
        render_summary_metrics(
            sales=results.get("sales", 0),
            result=results.get("result", 0),
            smpi=results.get("smpi", 0),
            financial_score=results.get("financial_score", 0),
            rse_score=results.get("rse_score", 0),
        )
    else:
        # Show placeholder metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Sales", "-- KEUR")
        with col2:
            st.metric("Result", "-- KEUR")
        with col3:
            st.metric("SMPI", "--")
        with col4:
            st.metric("Financial Score", "--")
        with col5:
            st.metric("RSE Score", "--")
    
    st.divider()
    
    # Quick actions
    st.write("### Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        uploaded_decisions = st.file_uploader(
            "Upload Decisions File",
            type=["xlsx", "xls", "csv"],
            key="decisions_upload",
        )
        if uploaded_decisions:
            st.success("Decisions file uploaded")
    
    with col2:
        uploaded_results = st.file_uploader(
            "Upload Results File",
            type=["xlsx", "xls", "csv"],
            key="results_upload",
        )
        if uploaded_results:
            st.success("Results file uploaded")
    
    with col3:
        uploaded_studies = st.file_uploader(
            "Upload Studies File",
            type=["xlsx", "xls", "csv"],
            key="studies_upload",
        )
        if uploaded_studies:
            st.success("Studies file uploaded")
    
    st.divider()
    
    # Period overview
    st.write("### Period Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Current Decisions Summary**")
        st.info("Load decision file to see summary")
    
    with col2:
        st.write("**Previous Results Summary**")
        st.info("Load results file to see summary")

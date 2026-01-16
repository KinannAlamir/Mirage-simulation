"""Decisions page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import streamlit as st

from state import get_state, set_state
from components.forms import render_product_form, render_marketing_form, render_production_form
from mirage.models.decisions import Decisions, ProductDecisions


def render_decisions():
    """Render the decisions page."""
    st.subheader("Decisions")
    
    firm_id = get_state("firm_id", 1)
    period = get_state("period", 0)
    
    # Tabs for different decision categories
    tab_products, tab_marketing, tab_supply, tab_production, tab_csr, tab_finance, tab_forecasts = st.tabs([
        "Products", "Marketing", "Supply", "Production", "CSR", "Finance", "Forecasts"
    ])
    
    with tab_products:
        render_products_tab()
    
    with tab_marketing:
        render_marketing_tab()
    
    with tab_supply:
        render_supply_tab()
    
    with tab_production:
        render_production_tab()
    
    with tab_csr:
        render_csr_tab()
    
    with tab_finance:
        render_finance_tab()
    
    with tab_forecasts:
        render_forecasts_tab()


def render_products_tab():
    """Render products decisions."""
    st.write("### Product Decisions")
    
    # Market selection
    market = st.radio(
        "Market",
        options=["TO (Traditional)", "MR (Modern Retail)"],
        horizontal=True,
    )
    
    market_code = "TO" if "TO" in market else "MR"
    
    st.divider()
    
    # Product forms
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Product A**")
        product_a = render_product_form("A", market_code)
    
    with col2:
        st.write("**Product B**")
        product_b = render_product_form("B", market_code)
    
    with col3:
        st.write("**Product C**")
        product_c = render_product_form("C", market_code)
    
    # Summary
    st.divider()
    total_production = product_a.production + product_b.production + product_c.production
    st.metric("Total Production", f"{total_production} KU")


def render_marketing_tab():
    """Render marketing decisions."""
    st.write("### Marketing Decisions")
    
    marketing = render_marketing_form()
    
    # Summary
    st.divider()
    st.write("**Summary**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Salesforce", marketing.nb_salesmen_to + marketing.nb_salesmen_mr)
    with col2:
        st.metric("Total Advertising", f"{marketing.advertising_to + marketing.advertising_mr} KEUR")
    with col3:
        studies = marketing.coded_studies_abcd + marketing.coded_studies_efgh
        st.metric("Studies Ordered", studies.replace("N", ""))


def render_supply_tab():
    """Render supply decisions."""
    st.write("### Supply & Maintenance Decisions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Raw Materials - Normal Quality (N)**")
        raw_n_order = st.number_input("Order (KU/period)", min_value=0, value=0, key="raw_n")
        raw_n_duration = st.selectbox("Contract Duration", options=[0, 1, 2, 3, 4], key="raw_n_dur")
    
    with col2:
        st.write("**Raw Materials - Superior Quality (S)**")
        raw_s_order = st.number_input("Order (KU/period)", min_value=0, value=0, key="raw_s")
        raw_s_duration = st.selectbox("Contract Duration", options=[0, 1, 2, 3, 4], key="raw_s_dur")
    
    st.divider()
    
    maintenance = st.checkbox("Maintenance", value=True)
    
    if not maintenance:
        st.warning("Skipping maintenance may cause production issues")


def render_production_tab():
    """Render production decisions."""
    st.write("### Production Decisions")
    
    production = render_production_form()
    
    # Capacity calculation
    st.divider()
    st.write("**Capacity Estimation**")
    
    capacity_m1 = production.nb_active_machines_m1 * 30  # Approximate
    capacity_m2 = production.nb_active_machines_m2 * 50  # Approximate
    total_capacity = capacity_m1 + capacity_m2
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("M1 Capacity", f"{capacity_m1} KU")
    with col2:
        st.metric("M2 Capacity", f"{capacity_m2} KU")
    with col3:
        st.metric("Total Capacity", f"{total_capacity} KU")


def render_csr_tab():
    """Render CSR decisions."""
    st.write("### CSR Decisions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        recycling = st.number_input("Recycling Budget (KEUR)", min_value=0.0, value=0.0)
    
    with col2:
        adapted = st.number_input("Adapted Facilities (KEUR)", min_value=0.0, value=0.0)
    
    with col3:
        rd = st.number_input("Research & Development (KEUR)", min_value=0.0, value=0.0)
    
    st.divider()
    total_csr = recycling + adapted + rd
    st.metric("Total CSR Investment", f"{total_csr} KEUR")


def render_finance_tab():
    """Render finance decisions."""
    st.write("### Finance Decisions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Financing**")
        lt_loan = st.number_input("Long Term Loan (KEUR)", min_value=0.0, value=0.0)
        lt_quarters = st.selectbox("LT Loan Quarters", options=list(range(0, 9)))
        st_loan = st.number_input("Short Term Loan (KEUR)", min_value=0.0, value=0.0)
        factoring = st.number_input("Invoice Factoring (KEUR)", min_value=0.0, value=0.0)
    
    with col2:
        st.write("**Payments & Stock**")
        dividends = st.number_input("Dividends (KEUR)", min_value=0.0, value=0.0)
        discount = st.number_input("Commercial Discount (%)", min_value=0.0, max_value=100.0, value=0.0)
        social = st.number_input("Social Effort (%)", min_value=0.0, value=0.0)
        early_repay = st.checkbox("Early Repay LT Loan")
    
    st.divider()
    st.write("**New Shares**")
    col1, col2 = st.columns(2)
    with col1:
        new_shares = st.number_input("New Shares Issued (KU)", min_value=0, value=0)
    with col2:
        share_price = st.number_input("Offered Price (EUR)", min_value=0.0, value=0.0)


def render_forecasts_tab():
    """Render forecasts."""
    st.write("### Forecasts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sales_forecast = st.number_input("Sales Forecast WT (KEUR)", min_value=0.0, value=0.0)
        result_forecast = st.number_input("Result Forecast (KEUR)", value=0.0)
    
    with col2:
        cash_in = st.number_input("Cash In Forecast (KEUR)", min_value=0.0, value=0.0)
        cash_out = st.number_input("Cash Out Forecast (KEUR)", min_value=0.0, value=0.0)
    
    st.divider()
    st.write("**Stock Trading**")
    
    cols = st.columns(6)
    for i, col in enumerate(cols, 1):
        with col:
            st.number_input(f"F{i} Shares", value=0, key=f"shares_f{i}")

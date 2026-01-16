"""Results page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

from state import get_state
from components.tables import render_dataframe, render_income_statement_table


def render_results():
    """Render the results page."""
    st.subheader("Results")
    
    firm_id = get_state("firm_id", 1)
    period = get_state("period", 0)
    
    # Tabs for different result views
    tabs = st.tabs([
        "Income Statement", "Expenses", "Incomes", "Balance Sheet", 
        "Cash Situation", "Operating/Product", "Profit/Product", "Stocks"
    ])
    
    with tabs[0]:
        render_income_statement()
    
    with tabs[1]:
        render_expenses()
    
    with tabs[2]:
        render_incomes()
    
    with tabs[3]:
        render_balance_sheet()
    
    with tabs[4]:
        render_cash_situation()
    
    with tabs[5]:
        render_operating_product()
    
    with tabs[6]:
        render_profit_product()
    
    with tabs[7]:
        render_stocks()


def render_income_statement():
    """Render income statement."""
    st.write("### Income Statement")
    
    results = get_state("results")
    
    if results and "income_statement" in results:
        render_income_statement_table(results["income_statement"])
    else:
        st.info("Load results file to view income statement")
        
        # Show empty template
        data = {
            "Item": [
                "Sales TO", "Sales MR", "Total Revenue", "",
                "Raw Materials", "Direct Labor", "Production Overhead",
                "Marketing Costs", "Administrative Costs", "Depreciation", "",
                "Operating Result", "Financial Result", "Exceptional Result",
                "Taxes", "", "Net Result"
            ],
            "Amount (KEUR)": ["--"] * 17
        }
        st.dataframe(pd.DataFrame(data), hide_index=True)


def render_expenses():
    """Render expenses breakdown."""
    st.write("### Expenses")
    st.info("Load results file to view expenses breakdown")


def render_incomes():
    """Render incomes breakdown."""
    st.write("### Incomes")
    st.info("Load results file to view incomes breakdown")


def render_balance_sheet():
    """Render balance sheet."""
    st.write("### Balance Sheet")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Assets**")
        assets_data = {
            "Item": [
                "Fixed Assets (Gross)", "Accumulated Depreciation", "Net Fixed Assets", "",
                "Raw Materials Stock", "Finished Goods Stock", "Accounts Receivable", "Cash", "",
                "Total Assets"
            ],
            "Amount (KEUR)": ["--"] * 10
        }
        st.dataframe(pd.DataFrame(assets_data), hide_index=True)
    
    with col2:
        st.write("**Liabilities**")
        liabilities_data = {
            "Item": [
                "Share Capital", "Reserves", "Retained Earnings", "Net Result", "Total Equity", "",
                "Long Term Debt", "Short Term Debt", "Accounts Payable", "",
                "Total Liabilities"
            ],
            "Amount (KEUR)": ["--"] * 11
        }
        st.dataframe(pd.DataFrame(liabilities_data), hide_index=True)


def render_cash_situation():
    """Render cash situation."""
    st.write("### Cash Situation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cash Inflows**")
        inflows = {
            "Source": ["Sales", "Financing", "Other", "Total In"],
            "Amount (KEUR)": ["--"] * 4
        }
        st.dataframe(pd.DataFrame(inflows), hide_index=True)
    
    with col2:
        st.write("**Cash Outflows**")
        outflows = {
            "Use": ["Purchases", "Salaries", "Investments", "Debt Service", "Dividends", "Taxes", "Other", "Total Out"],
            "Amount (KEUR)": ["--"] * 8
        }
        st.dataframe(pd.DataFrame(outflows), hide_index=True)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Opening Cash", "-- KEUR")
    with col2:
        st.metric("Net Cash Flow", "-- KEUR")
    with col3:
        st.metric("Closing Cash", "-- KEUR")


def render_operating_product():
    """Render operating data by product."""
    st.write("### Operating by Product")
    
    market = st.radio("Market", ["TO", "MR"], horizontal=True, key="op_market")
    
    data = {
        "Product": ["A", "B", "C", "Total"],
        "Production (KU)": ["--"] * 4,
        "Sales (KU)": ["--"] * 4,
        "Unit Cost (EUR)": ["--"] * 4,
        "Unit Price (EUR)": ["--"] * 4,
        "Revenue (KEUR)": ["--"] * 4,
        "COGS (KEUR)": ["--"] * 4,
    }
    st.dataframe(pd.DataFrame(data), hide_index=True)


def render_profit_product():
    """Render profit analysis by product."""
    st.write("### Profit by Product")
    
    market = st.radio("Market", ["TO", "MR"], horizontal=True, key="profit_market")
    
    data = {
        "Product": ["A", "B", "C", "Total"],
        "Revenue (KEUR)": ["--"] * 4,
        "Variable Costs (KEUR)": ["--"] * 4,
        "Contribution Margin (KEUR)": ["--"] * 4,
        "Fixed Costs (KEUR)": ["--"] * 4,
        "Operating Profit (KEUR)": ["--"] * 4,
        "Margin (%)": ["--"] * 4,
    }
    st.dataframe(pd.DataFrame(data), hide_index=True)


def render_stocks():
    """Render stock levels."""
    st.write("### Stock Levels")
    
    st.write("**Raw Materials**")
    raw_data = {
        "Material": ["Normal (N)", "Superior (S)"],
        "Quantity (KU)": ["--", "--"],
        "Value (KEUR)": ["--", "--"],
    }
    st.dataframe(pd.DataFrame(raw_data), hide_index=True)
    
    st.write("**Finished Products - TO**")
    to_data = {
        "Product": ["A", "B", "C"],
        "Quantity (KU)": ["--"] * 3,
        "Value (KEUR)": ["--"] * 3,
    }
    st.dataframe(pd.DataFrame(to_data), hide_index=True)
    
    st.write("**Finished Products - MR**")
    mr_data = {
        "Product": ["A", "B", "C"],
        "Quantity (KU)": ["--"] * 3,
        "Value (KEUR)": ["--"] * 3,
    }
    st.dataframe(pd.DataFrame(mr_data), hide_index=True)

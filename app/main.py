"""Main Streamlit application for Mirage Simulation."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Mirage Simulation",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
)

from state import init_session_state, get_state

# Initialize session state
init_session_state()


def main():
    """Main application entry point."""
    st.title("Mirage Simulation - Decision Tool")
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # Firm selector
        firm_id = st.selectbox(
            "Select Firm",
            options=[1, 2, 3, 4, 5, 6],
            index=get_state("firm_id", 1) - 1,
            format_func=lambda x: f"Firm {x}",
        )
        
        if firm_id != get_state("firm_id"):
            st.session_state.firm_id = firm_id
        
        # Period selector
        period = st.number_input(
            "Current Period",
            min_value=-10,
            max_value=20,
            value=get_state("period", 0),
        )
        
        if period != get_state("period"):
            st.session_state.period = period
        
        st.divider()
        
        # Navigation
        st.header("Navigation")
        
        pages = {
            "Dashboard": "dashboard",
            "Decisions": "decisions",
            "Results": "results",
            "Analysis": "analysis",
            "Competition": "competition",
            "Studies": "studies",
        }
        
        selected_page = st.radio(
            "Go to",
            options=list(pages.keys()),
            index=list(pages.keys()).index(get_state("current_page", "Dashboard")),
            label_visibility="collapsed",
        )
        
        if selected_page != get_state("current_page"):
            st.session_state.current_page = selected_page
    
    # Main content area
    st.header(f"Firm {get_state('firm_id')} - Period {get_state('period')}")
    
    # Display selected page content
    current_page = get_state("current_page", "Dashboard")
    
    if current_page == "Dashboard":
        show_dashboard()
    elif current_page == "Decisions":
        show_decisions()
    elif current_page == "Results":
        show_results()
    elif current_page == "Analysis":
        show_analysis()
    elif current_page == "Competition":
        show_competition()
    elif current_page == "Studies":
        show_studies()


def show_dashboard():
    """Display the dashboard page."""
    st.subheader("Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sales", "11 576 KEUR", delta=None)
    
    with col2:
        st.metric("Result", "254 KEUR", delta=None)
    
    with col3:
        st.metric("SMPI", "0.00", delta=None)
    
    with col4:
        st.metric("RSE Score", "50", delta=None)
    
    st.info("Load data files to see your actual results.")


def show_decisions():
    """Display the decisions page."""
    st.subheader("Decisions")
    
    tabs = st.tabs([
        "Products", "Marketing", "Supply", "Production", "CSR", "Finance", "Forecasts"
    ])
    
    with tabs[0]:
        st.write("Product decisions will be displayed here")
    
    with tabs[1]:
        st.write("Marketing decisions will be displayed here")
    
    with tabs[2]:
        st.write("Supply decisions will be displayed here")
    
    with tabs[3]:
        st.write("Production decisions will be displayed here")
    
    with tabs[4]:
        st.write("CSR decisions will be displayed here")
    
    with tabs[5]:
        st.write("Finance decisions will be displayed here")
    
    with tabs[6]:
        st.write("Forecasts will be displayed here")


def show_results():
    """Display the results page."""
    st.subheader("Results")
    
    tabs = st.tabs([
        "Income Statement", "Balance Sheet", "Cash Situation", 
        "Operating/Product", "Profit/Product", "Stocks"
    ])
    
    with tabs[0]:
        st.write("Income statement will be displayed here")
    
    with tabs[1]:
        st.write("Balance sheet will be displayed here")
    
    with tabs[2]:
        st.write("Cash situation will be displayed here")
    
    with tabs[3]:
        st.write("Operating by product will be displayed here")
    
    with tabs[4]:
        st.write("Profit by product will be displayed here")
    
    with tabs[5]:
        st.write("Stock levels will be displayed here")


def show_analysis():
    """Display the analysis page."""
    st.subheader("Analysis")
    
    tabs = st.tabs([
        "Trends", "Ratios", "Comparisons", "Forecasting"
    ])
    
    with tabs[0]:
        st.write("Trend analysis will be displayed here")
    
    with tabs[1]:
        st.write("Financial ratios will be displayed here")
    
    with tabs[2]:
        st.write("Period comparisons will be displayed here")
    
    with tabs[3]:
        st.write("Forecasting tools will be displayed here")


def show_competition():
    """Display the competition page."""
    st.subheader("Competition")
    
    tabs = st.tabs([
        "Overview", "Market Shares", "Pricing", "Benchmarking"
    ])
    
    with tabs[0]:
        st.write("Competition overview will be displayed here")
    
    with tabs[1]:
        st.write("Market share analysis will be displayed here")
    
    with tabs[2]:
        st.write("Pricing comparison will be displayed here")
    
    with tabs[3]:
        st.write("Benchmarking will be displayed here")


def show_studies():
    """Display the studies page."""
    st.subheader("Studies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Free Studies (A-D)**")
        st.write("- A: Market Evolution")
        st.write("- B: Consumer Behavior")
        st.write("- C: Competition Analysis")
        st.write("- D: Distribution Channels")
    
    with col2:
        st.write("**Fee-Paying Studies (E-H)**")
        st.write("- E: Economic Outlook")
        st.write("- F: Financial Analysis")
        st.write("- G: Geographic Analysis")
        st.write("- H: Human Resources")


if __name__ == "__main__":
    main()

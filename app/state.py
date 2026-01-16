"""Session state management for Streamlit app."""

import streamlit as st
from typing import Any


def init_session_state() -> None:
    """Initialize session state with default values."""
    defaults = {
        "firm_id": 1,
        "period": 0,
        "current_page": "Dashboard",
        "data_loaded": False,
        "decisions": None,
        "results": None,
        "competitors": None,
        "studies": None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_state(key: str, default: Any = None) -> Any:
    """Get a value from session state."""
    return st.session_state.get(key, default)


def set_state(key: str, value: Any) -> None:
    """Set a value in session state."""
    st.session_state[key] = value


def clear_state() -> None:
    """Clear all session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()

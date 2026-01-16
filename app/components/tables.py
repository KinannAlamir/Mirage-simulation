"""Table display components."""

from typing import Optional, Any
import streamlit as st
import pandas as pd


def render_dataframe(
    data: pd.DataFrame,
    title: Optional[str] = None,
    hide_index: bool = True,
    use_container_width: bool = True,
    column_config: Optional[dict] = None,
) -> None:
    """Render a styled dataframe.
    
    Args:
        data: DataFrame to display
        title: Optional title above the table
        hide_index: Whether to hide the index column
        use_container_width: Whether to use full container width
        column_config: Column configuration for st.dataframe
    """
    if title:
        st.subheader(title)
    
    st.dataframe(
        data,
        hide_index=hide_index,
        use_container_width=use_container_width,
        column_config=column_config,
    )


def render_comparison_table(
    current: dict,
    previous: dict,
    labels: dict[str, str],
    title: Optional[str] = None,
) -> None:
    """Render a comparison table between two periods.
    
    Args:
        current: Current period values
        previous: Previous period values
        labels: Mapping of keys to display labels
        title: Optional title
    """
    if title:
        st.subheader(title)
    
    rows = []
    for key, label in labels.items():
        curr_val = current.get(key, 0)
        prev_val = previous.get(key, 0)
        
        if prev_val != 0:
            change = ((curr_val - prev_val) / abs(prev_val)) * 100
            change_str = f"{change:+.1f}%"
        else:
            change_str = "N/A"
        
        rows.append({
            "Metric": label,
            "Previous": prev_val,
            "Current": curr_val,
            "Change": change_str,
        })
    
    df = pd.DataFrame(rows)
    render_dataframe(df)


def render_firms_comparison(
    firms_data: list[dict],
    metrics: list[str],
    metric_labels: dict[str, str],
) -> None:
    """Render a comparison table across all firms.
    
    Args:
        firms_data: List of firm data dicts with firm_id and metrics
        metrics: List of metric keys to compare
        metric_labels: Mapping of metric keys to display labels
    """
    # Build comparison table
    rows = []
    for metric in metrics:
        row = {"Metric": metric_labels.get(metric, metric)}
        for firm in firms_data:
            firm_id = firm.get("firm_id", 0)
            value = firm.get(metric, 0)
            row[f"Firm {firm_id}"] = value
        rows.append(row)
    
    df = pd.DataFrame(rows)
    render_dataframe(df)


def render_income_statement_table(data: dict) -> None:
    """Render an income statement in table format."""
    rows = [
        ("Revenue", ""),
        ("  Sales TO", data.get("sales_to", 0)),
        ("  Sales MR", data.get("sales_mr", 0)),
        ("  Total Revenue", data.get("total_revenue", 0)),
        ("", ""),
        ("Costs", ""),
        ("  Raw Materials", data.get("raw_materials", 0)),
        ("  Direct Labor", data.get("direct_labor", 0)),
        ("  Production Overhead", data.get("production_overhead", 0)),
        ("  Marketing Costs", data.get("marketing_costs", 0)),
        ("  Administrative Costs", data.get("admin_costs", 0)),
        ("  Depreciation", data.get("depreciation", 0)),
        ("", ""),
        ("Operating Result", data.get("operating_result", 0)),
        ("Financial Result", data.get("financial_result", 0)),
        ("Exceptional Result", data.get("exceptional_result", 0)),
        ("Taxes", data.get("taxes", 0)),
        ("", ""),
        ("Net Result", data.get("net_result", 0)),
    ]
    
    df = pd.DataFrame(rows, columns=["Item", "Amount (KEUR)"])
    render_dataframe(df)

"""Metric display components."""

from typing import Optional
import streamlit as st


def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal",
) -> None:
    """Render a single metric card."""
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color,
    )


def render_metrics_row(
    metrics: list[dict],
    columns: int = 4,
) -> None:
    """Render a row of metrics.
    
    Args:
        metrics: List of dicts with keys: label, value, delta (optional)
        columns: Number of columns to display
    """
    cols = st.columns(columns)
    
    for i, metric in enumerate(metrics):
        col_idx = i % columns
        with cols[col_idx]:
            render_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta"),
                delta_color=metric.get("delta_color", "normal"),
            )


def render_summary_metrics(
    sales: float,
    result: float,
    smpi: float,
    financial_score: float,
    rse_score: float,
    previous_values: Optional[dict] = None,
) -> None:
    """Render the main summary metrics."""
    metrics = [
        {
            "label": "Sales",
            "value": f"{sales:,.0f} KEUR".replace(",", " "),
            "delta": _calc_delta(sales, previous_values.get("sales")) if previous_values else None,
        },
        {
            "label": "Result",
            "value": f"{result:,.0f} KEUR".replace(",", " "),
            "delta": _calc_delta(result, previous_values.get("result")) if previous_values else None,
        },
        {
            "label": "SMPI",
            "value": f"{smpi:.2f}",
            "delta": _calc_delta(smpi, previous_values.get("smpi")) if previous_values else None,
        },
        {
            "label": "Financial Score",
            "value": f"{financial_score:.0f}",
            "delta": _calc_delta(financial_score, previous_values.get("financial_score")) if previous_values else None,
        },
        {
            "label": "RSE Score",
            "value": f"{rse_score:.0f}",
            "delta": _calc_delta(rse_score, previous_values.get("rse_score")) if previous_values else None,
        },
    ]
    
    render_metrics_row(metrics, columns=5)


def _calc_delta(current: float, previous: Optional[float]) -> Optional[str]:
    """Calculate delta string between two values."""
    if previous is None or previous == 0:
        return None
    
    change = current - previous
    pct = (change / abs(previous)) * 100
    
    if change > 0:
        return f"+{pct:.1f}%"
    elif change < 0:
        return f"{pct:.1f}%"
    else:
        return "0%"

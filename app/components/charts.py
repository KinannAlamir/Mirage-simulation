"""Chart components using Plotly."""

from typing import Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_line_chart(
    data: pd.DataFrame,
    x: str,
    y: str | list[str],
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: Optional[str] = None,
) -> None:
    """Render a line chart.
    
    Args:
        data: DataFrame with chart data
        x: Column name for x-axis
        y: Column name(s) for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Column name for color grouping
    """
    fig = px.line(
        data,
        x=x,
        y=y,
        title=title,
        labels={x: x_label or x, y: y_label or y} if isinstance(y, str) else None,
        color=color,
    )
    
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        legend_title=color if color else None,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    color: Optional[str] = None,
    orientation: str = "v",
) -> None:
    """Render a bar chart.
    
    Args:
        data: DataFrame with chart data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        color: Column name for color grouping
        orientation: 'v' for vertical, 'h' for horizontal
    """
    fig = px.bar(
        data,
        x=x,
        y=y,
        title=title,
        color=color,
        orientation=orientation,
    )
    
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_pie_chart(
    data: pd.DataFrame,
    values: str,
    names: str,
    title: Optional[str] = None,
    hole: float = 0.0,
) -> None:
    """Render a pie chart.
    
    Args:
        data: DataFrame with chart data
        values: Column name for values
        names: Column name for segment names
        title: Chart title
        hole: Size of hole for donut chart (0.0-1.0)
    """
    fig = px.pie(
        data,
        values=values,
        names=names,
        title=title,
        hole=hole,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_trend_chart(
    periods: list[int],
    values: list[float],
    title: str,
    y_label: str,
    show_trend_line: bool = True,
) -> None:
    """Render a trend chart with optional trend line.
    
    Args:
        periods: List of period numbers
        values: List of values
        title: Chart title
        y_label: Y-axis label
        show_trend_line: Whether to show trend line
    """
    fig = go.Figure()
    
    # Main line
    fig.add_trace(go.Scatter(
        x=periods,
        y=values,
        mode='lines+markers',
        name='Actual',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8),
    ))
    
    # Trend line
    if show_trend_line and len(periods) >= 2:
        import numpy as np
        z = np.polyfit(periods, values, 1)
        p = np.poly1d(z)
        trend_values = [p(x) for x in periods]
        
        fig.add_trace(go.Scatter(
            x=periods,
            y=trend_values,
            mode='lines',
            name='Trend',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Period',
        yaxis_title=y_label,
        showlegend=True,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_comparison_bar(
    firms: list[str],
    values: list[float],
    title: str,
    highlight_firm: Optional[int] = None,
) -> None:
    """Render a bar chart comparing firms.
    
    Args:
        firms: List of firm names/labels
        values: List of values
        title: Chart title
        highlight_firm: Index of firm to highlight
    """
    colors = ['#1f77b4'] * len(firms)
    if highlight_firm is not None and 0 <= highlight_firm < len(firms):
        colors[highlight_firm] = '#ff7f0e'
    
    fig = go.Figure(data=[
        go.Bar(
            x=firms,
            y=values,
            marker_color=colors,
        )
    ])
    
    fig.update_layout(
        title=title,
        xaxis_title='Firm',
        yaxis_title='Value',
    )
    
    st.plotly_chart(fig, use_container_width=True)

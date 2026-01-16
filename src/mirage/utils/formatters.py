"""Formatting utilities."""

from typing import Optional


def format_currency(
    value: float,
    currency: str = "EUR",
    decimals: int = 2,
    thousands_sep: str = " ",
) -> str:
    """Format a value as currency."""
    formatted = f"{value:,.{decimals}f}".replace(",", thousands_sep)
    
    if currency == "EUR":
        return f"{formatted} EUR"
    elif currency == "KEUR":
        return f"{formatted} KEUR"
    else:
        return f"{formatted} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a value as percentage."""
    return f"{value:.{decimals}f}%"


def format_number(
    value: float,
    decimals: int = 0,
    thousands_sep: str = " ",
    suffix: str = "",
) -> str:
    """Format a number with thousands separator."""
    formatted = f"{value:,.{decimals}f}".replace(",", thousands_sep)
    return f"{formatted}{suffix}" if suffix else formatted


def format_change(value: float, decimals: int = 2) -> str:
    """Format a change value with sign."""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}"


def format_trend(current: float, previous: float) -> tuple[str, str]:
    """Format trend between two values. Returns (arrow, percentage)."""
    if previous == 0:
        return ("", "N/A")
    
    change = ((current - previous) / previous) * 100
    
    if change > 0:
        return ("^", f"+{change:.1f}%")
    elif change < 0:
        return ("v", f"{change:.1f}%")
    else:
        return ("-", "0%")

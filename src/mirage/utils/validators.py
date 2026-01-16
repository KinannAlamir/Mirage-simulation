"""Validation utilities."""

from typing import Optional


def validate_firm_id(firm_id: int) -> tuple[bool, Optional[str]]:
    """Validate a firm ID. Returns (is_valid, error_message)."""
    if not isinstance(firm_id, int):
        return False, "Firm ID must be an integer"
    if firm_id < 1 or firm_id > 6:
        return False, "Firm ID must be between 1 and 6"
    return True, None


def validate_period(period: int, min_period: int = -10, max_period: int = 20) -> tuple[bool, Optional[str]]:
    """Validate a period number. Returns (is_valid, error_message)."""
    if not isinstance(period, int):
        return False, "Period must be an integer"
    if period < min_period or period > max_period:
        return False, f"Period must be between {min_period} and {max_period}"
    return True, None


def validate_positive(value: float, field_name: str) -> tuple[bool, Optional[str]]:
    """Validate that a value is positive. Returns (is_valid, error_message)."""
    if value < 0:
        return False, f"{field_name} cannot be negative"
    return True, None


def validate_percentage(value: float, field_name: str) -> tuple[bool, Optional[str]]:
    """Validate that a value is a valid percentage (0-100). Returns (is_valid, error_message)."""
    if value < 0 or value > 100:
        return False, f"{field_name} must be between 0 and 100"
    return True, None


def validate_production_capacity(
    total_production: int,
    machines_m1: int,
    machines_m2: int,
    capacity_m1: int = 30,
    capacity_m2: int = 50,
) -> tuple[bool, Optional[str]]:
    """Validate production against capacity. Returns (is_valid, error_message)."""
    max_capacity = (machines_m1 * capacity_m1) + (machines_m2 * capacity_m2)
    
    if total_production > max_capacity:
        return False, f"Production ({total_production} KU) exceeds capacity ({max_capacity} KU)"
    
    return True, None

"""Decision management service."""

from typing import Optional
from mirage.models.decisions import Decisions


class DecisionService:
    """Service for managing decisions."""

    def __init__(self):
        self._decisions: dict[tuple[int, int], Decisions] = {}  # (firm_id, period) -> Decisions

    def get_decisions(self, firm_id: int, period: int) -> Optional[Decisions]:
        """Get decisions for a firm and period."""
        return self._decisions.get((firm_id, period))

    def set_decisions(self, decisions: Decisions) -> None:
        """Set decisions for a firm and period."""
        self._decisions[(decisions.firm_id, decisions.period)] = decisions

    def get_historical_decisions(self, firm_id: int, up_to_period: int) -> list[Decisions]:
        """Get all decisions for a firm up to a given period."""
        return [
            d for (fid, p), d in self._decisions.items()
            if fid == firm_id and p <= up_to_period
        ]

    def validate_decisions(self, decisions: Decisions) -> list[str]:
        """Validate decisions and return list of warnings/errors."""
        warnings = []
        
        # Example validations
        prod = decisions.production
        if prod.nb_active_machines_m1 < 0 or prod.nb_active_machines_m2 < 0:
            warnings.append("Number of active machines cannot be negative")
        
        # Check production capacity
        total_production = (
            decisions.product_a_to.production +
            decisions.product_b_to.production +
            decisions.product_c_to.production +
            decisions.product_a_mr.production +
            decisions.product_b_mr.production +
            decisions.product_c_mr.production
        )
        
        # Rough capacity check (can be refined)
        estimated_capacity = (
            prod.nb_active_machines_m1 * 30 + 
            prod.nb_active_machines_m2 * 50
        )
        if total_production > estimated_capacity:
            warnings.append(
                f"Total production ({total_production} KU) may exceed capacity ({estimated_capacity} KU)"
            )
        
        return warnings

    def compare_periods(self, firm_id: int, period1: int, period2: int) -> dict:
        """Compare decisions between two periods."""
        d1 = self.get_decisions(firm_id, period1)
        d2 = self.get_decisions(firm_id, period2)
        
        if not d1 or not d2:
            return {}
        
        # Return differences (simplified)
        return {
            "period1": period1,
            "period2": period2,
            "d1": d1.model_dump(),
            "d2": d2.model_dump(),
        }

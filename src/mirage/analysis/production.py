"""Production analysis module."""

from typing import Optional
from mirage.models.decisions import ProductDecisions, ProductionDecisions


class ProductionAnalyzer:
    """Analyzer for production data."""

    # Default capacity per machine type (KU per period)
    DEFAULT_CAPACITY_M1 = 30
    DEFAULT_CAPACITY_M2 = 50

    def calculate_capacity(
        self,
        machines_m1: int,
        machines_m2: int,
        capacity_m1: int = DEFAULT_CAPACITY_M1,
        capacity_m2: int = DEFAULT_CAPACITY_M2,
    ) -> int:
        """Calculate total production capacity."""
        return (machines_m1 * capacity_m1) + (machines_m2 * capacity_m2)

    def calculate_utilization(
        self,
        total_production: int,
        capacity: int,
    ) -> float:
        """Calculate capacity utilization percentage."""
        if capacity == 0:
            return 0.0
        return (total_production / capacity) * 100

    def analyze_production_mix(
        self,
        products: list[tuple[str, int]],  # (product_name, production_volume)
    ) -> dict:
        """Analyze production mix."""
        total = sum(vol for _, vol in products)
        
        if total == 0:
            return {"total": 0, "mix": {}}
        
        mix = {
            name: {
                "volume": vol,
                "share": (vol / total) * 100
            }
            for name, vol in products
        }
        
        return {
            "total": total,
            "mix": mix,
        }

    def check_capacity_constraints(
        self,
        production_decisions: ProductionDecisions,
        total_planned_production: int,
    ) -> dict:
        """Check if production plans are within capacity."""
        capacity = self.calculate_capacity(
            production_decisions.nb_active_machines_m1,
            production_decisions.nb_active_machines_m2,
        )
        
        utilization = self.calculate_utilization(
            total_planned_production,
            capacity,
        )
        
        is_feasible = total_planned_production <= capacity
        slack = capacity - total_planned_production
        
        return {
            "capacity": capacity,
            "planned_production": total_planned_production,
            "utilization": utilization,
            "is_feasible": is_feasible,
            "slack": slack,
            "warning": None if is_feasible else f"Production exceeds capacity by {-slack} KU",
        }

    def calculate_quality_cost_impact(
        self,
        base_cost: float,
        quality_level: int,
        quality_cost_factor: float = 0.005,
    ) -> float:
        """Calculate additional cost for quality level."""
        # Higher quality = higher cost
        quality_premium = base_cost * quality_level * quality_cost_factor
        return base_cost + quality_premium

    def analyze_machine_efficiency(
        self,
        machines_m1: int,
        machines_m2: int,
        maintenance: bool,
    ) -> dict:
        """Analyze machine efficiency and recommendations."""
        efficiency_m1 = 1.0 if maintenance else 0.85  # 15% efficiency loss without maintenance
        efficiency_m2 = 1.0 if maintenance else 0.90  # 10% efficiency loss without maintenance
        
        effective_capacity_m1 = int(machines_m1 * self.DEFAULT_CAPACITY_M1 * efficiency_m1)
        effective_capacity_m2 = int(machines_m2 * self.DEFAULT_CAPACITY_M2 * efficiency_m2)
        
        return {
            "machines_m1": machines_m1,
            "machines_m2": machines_m2,
            "maintenance": maintenance,
            "efficiency_m1": efficiency_m1,
            "efficiency_m2": efficiency_m2,
            "theoretical_capacity": self.calculate_capacity(machines_m1, machines_m2),
            "effective_capacity": effective_capacity_m1 + effective_capacity_m2,
            "capacity_loss": (
                self.calculate_capacity(machines_m1, machines_m2) - 
                (effective_capacity_m1 + effective_capacity_m2)
            ) if not maintenance else 0,
        }

    def recommend_production_level(
        self,
        demand_forecast: int,
        current_stock: int,
        capacity: int,
        target_stock_days: int = 30,
        days_per_period: int = 90,
    ) -> dict:
        """Recommend production level based on demand and stock."""
        # Calculate target ending stock (safety stock)
        daily_demand = demand_forecast / days_per_period
        target_stock = int(daily_demand * target_stock_days)
        
        # Calculate needed production
        needed_production = demand_forecast + target_stock - current_stock
        needed_production = max(0, needed_production)
        
        # Cap at capacity
        recommended_production = min(needed_production, capacity)
        
        return {
            "demand_forecast": demand_forecast,
            "current_stock": current_stock,
            "target_stock": target_stock,
            "needed_production": needed_production,
            "capacity": capacity,
            "recommended_production": recommended_production,
            "will_meet_demand": recommended_production >= needed_production,
            "expected_ending_stock": current_stock + recommended_production - demand_forecast,
        }

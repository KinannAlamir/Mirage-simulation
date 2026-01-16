"""Analysis service for Mirage simulation."""

from typing import Optional
import numpy as np

from mirage.models.results import FirmSummary, IncomeStatement, BalanceSheet
from mirage.models.market import CompetitorData


class AnalysisService:
    """Service for analyzing simulation data."""

    def calculate_market_share(
        self, firm_sales: float, all_firms_sales: list[float]
    ) -> float:
        """Calculate market share percentage."""
        total = sum(all_firms_sales)
        if total == 0:
            return 0.0
        return (firm_sales / total) * 100

    def calculate_growth_rate(
        self, current_value: float, previous_value: float
    ) -> float:
        """Calculate growth rate percentage."""
        if previous_value == 0:
            return 0.0 if current_value == 0 else 100.0
        return ((current_value - previous_value) / previous_value) * 100

    def calculate_profitability_ratios(self, income: IncomeStatement) -> dict:
        """Calculate profitability ratios."""
        revenue = income.total_revenue if income.total_revenue > 0 else 1
        
        return {
            "gross_margin": (
                (revenue - income.raw_materials - income.direct_labor) / revenue * 100
            ),
            "operating_margin": income.operating_result / revenue * 100,
            "net_margin": income.net_result / revenue * 100,
        }

    def calculate_liquidity_ratios(self, balance: BalanceSheet) -> dict:
        """Calculate liquidity ratios."""
        current_assets = (
            balance.assets.raw_materials_stock +
            balance.assets.finished_goods_stock +
            balance.assets.accounts_receivable +
            balance.assets.cash
        )
        current_liabilities = (
            balance.liabilities.short_term_debt +
            balance.liabilities.accounts_payable
        )
        
        if current_liabilities == 0:
            current_liabilities = 1
        
        return {
            "current_ratio": current_assets / current_liabilities,
            "quick_ratio": (
                (balance.assets.accounts_receivable + balance.assets.cash) /
                current_liabilities
            ),
            "cash_ratio": balance.assets.cash / current_liabilities,
        }

    def calculate_solvency_ratios(self, balance: BalanceSheet) -> dict:
        """Calculate solvency ratios."""
        total_assets = balance.assets.total_assets if balance.assets.total_assets > 0 else 1
        total_equity = balance.liabilities.total_equity if balance.liabilities.total_equity > 0 else 1
        
        total_debt = (
            balance.liabilities.long_term_debt +
            balance.liabilities.short_term_debt
        )
        
        return {
            "debt_ratio": total_debt / total_assets * 100,
            "equity_ratio": balance.liabilities.total_equity / total_assets * 100,
            "debt_to_equity": total_debt / total_equity,
        }

    def rank_firms(
        self, summaries: list[FirmSummary], metric: str = "sales"
    ) -> list[tuple[int, float, int]]:
        """Rank firms by a metric. Returns list of (firm_id, value, rank)."""
        if not summaries:
            return []
        
        values = [(s.firm_id, getattr(s, metric, 0)) for s in summaries]
        sorted_values = sorted(values, key=lambda x: x[1], reverse=True)
        
        return [
            (firm_id, value, rank + 1)
            for rank, (firm_id, value) in enumerate(sorted_values)
        ]

    def compare_to_competitors(
        self, firm_summary: FirmSummary, competitors: list[CompetitorData]
    ) -> dict:
        """Compare firm performance to competitors."""
        if not competitors:
            return {}
        
        all_sales = [firm_summary.sales] + [c.sales for c in competitors]
        all_results = [firm_summary.result] + [c.result for c in competitors]
        
        return {
            "sales_rank": sorted(all_sales, reverse=True).index(firm_summary.sales) + 1,
            "result_rank": sorted(all_results, reverse=True).index(firm_summary.result) + 1,
            "avg_sales": np.mean(all_sales),
            "avg_result": np.mean(all_results),
            "sales_vs_avg": firm_summary.sales - np.mean(all_sales),
            "result_vs_avg": firm_summary.result - np.mean(all_results),
        }

    def calculate_trend(self, values: list[float]) -> dict:
        """Calculate trend statistics for a series of values."""
        if len(values) < 2:
            return {"trend": "insufficient_data"}
        
        x = np.arange(len(values))
        y = np.array(values)
        
        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate average growth
        growth_rates = [
            (values[i] - values[i-1]) / values[i-1] * 100 if values[i-1] != 0 else 0
            for i in range(1, len(values))
        ]
        
        return {
            "trend": "up" if slope > 0 else "down" if slope < 0 else "flat",
            "slope": slope,
            "avg_growth_rate": np.mean(growth_rates),
            "volatility": np.std(values),
            "min": min(values),
            "max": max(values),
        }

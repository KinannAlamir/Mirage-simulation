"""Financial analysis module."""

from typing import Optional
from mirage.models.results import IncomeStatement, BalanceSheet


class FinancialAnalyzer:
    """Analyzer for financial data."""

    def calculate_roe(self, net_result: float, equity: float) -> float:
        """Calculate Return on Equity."""
        if equity == 0:
            return 0.0
        return (net_result / equity) * 100

    def calculate_roa(self, net_result: float, total_assets: float) -> float:
        """Calculate Return on Assets."""
        if total_assets == 0:
            return 0.0
        return (net_result / total_assets) * 100

    def calculate_debt_ratio(self, total_debt: float, total_assets: float) -> float:
        """Calculate Debt Ratio."""
        if total_assets == 0:
            return 0.0
        return (total_debt / total_assets) * 100

    def calculate_current_ratio(
        self, current_assets: float, current_liabilities: float
    ) -> float:
        """Calculate Current Ratio."""
        if current_liabilities == 0:
            return float('inf') if current_assets > 0 else 0.0
        return current_assets / current_liabilities

    def calculate_gross_margin(self, revenue: float, cogs: float) -> float:
        """Calculate Gross Margin percentage."""
        if revenue == 0:
            return 0.0
        return ((revenue - cogs) / revenue) * 100

    def calculate_operating_margin(
        self, operating_result: float, revenue: float
    ) -> float:
        """Calculate Operating Margin percentage."""
        if revenue == 0:
            return 0.0
        return (operating_result / revenue) * 100

    def calculate_net_margin(self, net_result: float, revenue: float) -> float:
        """Calculate Net Margin percentage."""
        if revenue == 0:
            return 0.0
        return (net_result / revenue) * 100

    def analyze_income_statement(
        self, statement: IncomeStatement
    ) -> dict:
        """Perform full analysis of income statement."""
        return {
            "gross_margin": self.calculate_gross_margin(
                statement.total_revenue,
                statement.raw_materials + statement.direct_labor
            ),
            "operating_margin": self.calculate_operating_margin(
                statement.operating_result,
                statement.total_revenue
            ),
            "net_margin": self.calculate_net_margin(
                statement.net_result,
                statement.total_revenue
            ),
        }

    def analyze_balance_sheet(self, sheet: BalanceSheet) -> dict:
        """Perform full analysis of balance sheet."""
        total_debt = (
            sheet.liabilities.long_term_debt + 
            sheet.liabilities.short_term_debt
        )
        
        current_assets = (
            sheet.assets.raw_materials_stock +
            sheet.assets.finished_goods_stock +
            sheet.assets.accounts_receivable +
            sheet.assets.cash
        )
        
        current_liabilities = (
            sheet.liabilities.short_term_debt +
            sheet.liabilities.accounts_payable
        )
        
        return {
            "roe": self.calculate_roe(
                sheet.liabilities.net_result,
                sheet.liabilities.total_equity
            ),
            "roa": self.calculate_roa(
                sheet.liabilities.net_result,
                sheet.assets.total_assets
            ),
            "debt_ratio": self.calculate_debt_ratio(
                total_debt,
                sheet.assets.total_assets
            ),
            "current_ratio": self.calculate_current_ratio(
                current_assets,
                current_liabilities
            ),
        }

"""Results management service."""

from typing import Optional
from mirage.models.results import (
    FirmSummary,
    IncomeStatement,
    BalanceSheet,
    CashSituation,
    Stocks,
)


class ResultsService:
    """Service for managing and analyzing results."""

    def __init__(self):
        self._summaries: dict[tuple[int, int], FirmSummary] = {}
        self._income_statements: dict[tuple[int, int], IncomeStatement] = {}
        self._balance_sheets: dict[tuple[int, int], BalanceSheet] = {}
        self._cash_situations: dict[tuple[int, int], CashSituation] = {}
        self._stocks: dict[tuple[int, int], Stocks] = {}

    def add_summary(self, summary: FirmSummary) -> None:
        """Add a firm summary."""
        self._summaries[(summary.firm_id, summary.period)] = summary

    def get_summary(self, firm_id: int, period: int) -> Optional[FirmSummary]:
        """Get firm summary for a period."""
        return self._summaries.get((firm_id, period))

    def get_all_summaries_for_period(self, period: int) -> list[FirmSummary]:
        """Get all firm summaries for a period (for comparison)."""
        return [s for (fid, p), s in self._summaries.items() if p == period]

    def add_income_statement(self, statement: IncomeStatement) -> None:
        """Add an income statement."""
        self._income_statements[(statement.firm_id, statement.period)] = statement

    def get_income_statement(self, firm_id: int, period: int) -> Optional[IncomeStatement]:
        """Get income statement for a firm and period."""
        return self._income_statements.get((firm_id, period))

    def add_balance_sheet(self, sheet: BalanceSheet) -> None:
        """Add a balance sheet."""
        self._balance_sheets[(sheet.firm_id, sheet.period)] = sheet

    def get_balance_sheet(self, firm_id: int, period: int) -> Optional[BalanceSheet]:
        """Get balance sheet for a firm and period."""
        return self._balance_sheets.get((firm_id, period))

    def add_cash_situation(self, cash: CashSituation) -> None:
        """Add cash situation."""
        self._cash_situations[(cash.firm_id, cash.period)] = cash

    def get_cash_situation(self, firm_id: int, period: int) -> Optional[CashSituation]:
        """Get cash situation for a firm and period."""
        return self._cash_situations.get((firm_id, period))

    def add_stocks(self, stocks: Stocks) -> None:
        """Add stocks data."""
        self._stocks[(stocks.firm_id, stocks.period)] = stocks

    def get_stocks(self, firm_id: int, period: int) -> Optional[Stocks]:
        """Get stocks for a firm and period."""
        return self._stocks.get((firm_id, period))

    def get_historical_results(self, firm_id: int, up_to_period: int) -> dict:
        """Get all historical results for a firm."""
        return {
            "summaries": [
                s for (fid, p), s in self._summaries.items()
                if fid == firm_id and p <= up_to_period
            ],
            "income_statements": [
                s for (fid, p), s in self._income_statements.items()
                if fid == firm_id and p <= up_to_period
            ],
            "balance_sheets": [
                s for (fid, p), s in self._balance_sheets.items()
                if fid == firm_id and p <= up_to_period
            ],
        }

"""Results data loader."""

from pathlib import Path
from typing import Optional, Any

import pandas as pd

from mirage.loaders.base_loader import BaseLoader
from mirage.models.results import (
    FirmSummary,
    IncomeStatement,
    BalanceSheet,
    BalanceSheetAssets,
    BalanceSheetLiabilities,
    CashSituation,
    Stocks,
)


class ResultsLoader(BaseLoader):
    """Loader for results spreadsheets."""

    def __init__(self, file_path: Optional[Path] = None):
        super().__init__(file_path)
        self.firm_id: int = 1
        self.period: int = 0

    def set_context(self, firm_id: int, period: int) -> None:
        """Set firm and period context for parsing."""
        self.firm_id = firm_id
        self.period = period

    def parse(self) -> dict[str, Any]:
        """Parse all result types from loaded data."""
        return {
            "summary": self.parse_summary(),
            "income_statement": self.parse_income_statement(),
            "balance_sheet": self.parse_balance_sheet(),
            "cash_situation": self.parse_cash_situation(),
            "stocks": self.parse_stocks(),
        }

    def parse_summary(self) -> Optional[FirmSummary]:
        """Parse firm summary data."""
        if self._data is None:
            return None
        
        # Implementation depends on exact spreadsheet structure
        return FirmSummary(
            firm_id=self.firm_id,
            period=self.period,
            sales=0.0,
            result=0.0,
            smpi=0.0,
            financial_score=0.0,
            rse_score=0.0,
        )

    def parse_income_statement(self) -> Optional[IncomeStatement]:
        """Parse income statement data."""
        if self._data is None:
            return None
        
        return IncomeStatement(
            firm_id=self.firm_id,
            period=self.period,
        )

    def parse_balance_sheet(self) -> Optional[BalanceSheet]:
        """Parse balance sheet data."""
        if self._data is None:
            return None
        
        return BalanceSheet(
            firm_id=self.firm_id,
            period=self.period,
            assets=BalanceSheetAssets(),
            liabilities=BalanceSheetLiabilities(),
        )

    def parse_cash_situation(self) -> Optional[CashSituation]:
        """Parse cash situation data."""
        if self._data is None:
            return None
        
        return CashSituation(
            firm_id=self.firm_id,
            period=self.period,
        )

    def parse_stocks(self) -> Optional[Stocks]:
        """Parse stocks data."""
        if self._data is None:
            return None
        
        return Stocks(
            firm_id=self.firm_id,
            period=self.period,
        )

    def load_summary_from_dataframe(self, df: pd.DataFrame) -> list[FirmSummary]:
        """Load firm summaries from a pre-formatted DataFrame."""
        summaries = []
        
        for _, row in df.iterrows():
            try:
                summary = FirmSummary(
                    firm_id=int(row.get("firm_id", row.get("Firms", "").split()[-1])),
                    period=self.period,
                    sales=float(row.get("Sales", 0)),
                    result=float(row.get("Result", 0)),
                    smpi=float(row.get("SMPI", 0)),
                    financial_score=float(row.get("Financial Score", 0)),
                    rse_score=float(row.get("RSE Score", 0)),
                )
                summaries.append(summary)
            except (ValueError, KeyError):
                continue
        
        return summaries

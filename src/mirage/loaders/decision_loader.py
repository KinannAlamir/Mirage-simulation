"""Decision data loader."""

from pathlib import Path
from typing import Optional, Any

import pandas as pd

from mirage.loaders.base_loader import BaseLoader
from mirage.models.decisions import (
    Decisions,
    ProductDecisions,
    MarketingDecisions,
    SupplyDecisions,
    ProductionDecisions,
    CSRDecisions,
    FinanceDecisions,
    ForecastDecisions,
    StockDecisions,
)


class DecisionLoader(BaseLoader):
    """Loader for decision spreadsheets."""

    # Row mappings based on the Mirage decision sheet structure
    ROW_MAPPINGS = {
        # Product A - TO
        "011": ("product_a_to", "catalog_price"),
        "012": ("product_a_to", "promotion"),
        "013": ("product_a_to", "production"),
        "014": ("product_a_to", "produced_quality"),
        "015": ("product_a_to", "recycled_packaging"),
        # Product A - MR
        "021": ("product_a_mr", "catalog_price"),
        "022": ("product_a_mr", "rebate_mr"),
        "023": ("product_a_mr", "promotion"),
        "024": ("product_a_mr", "production"),
        "025": ("product_a_mr", "produced_quality"),
        "026": ("product_a_mr", "recycled_packaging"),
        # Product B - TO
        "031": ("product_b_to", "catalog_price"),
        "032": ("product_b_to", "promotion"),
        "033": ("product_b_to", "production"),
        "034": ("product_b_to", "produced_quality"),
        "035": ("product_b_to", "recycled_packaging"),
        # Product B - MR
        "041": ("product_b_mr", "catalog_price"),
        "042": ("product_b_mr", "rebate_mr"),
        "043": ("product_b_mr", "promotion"),
        "044": ("product_b_mr", "production"),
        "045": ("product_b_mr", "produced_quality"),
        "046": ("product_b_mr", "recycled_packaging"),
        # Product C - TO
        "051": ("product_c_to", "catalog_price"),
        "052": ("product_c_to", "promotion"),
        "053": ("product_c_to", "production"),
        "054": ("product_c_to", "produced_quality"),
        "055": ("product_c_to", "recycled_packaging"),
        # Product C - MR
        "061": ("product_c_mr", "catalog_price"),
        "062": ("product_c_mr", "rebate_mr"),
        "063": ("product_c_mr", "promotion"),
        "064": ("product_c_mr", "production"),
        "065": ("product_c_mr", "produced_quality"),
        "066": ("product_c_mr", "recycled_packaging"),
        # Marketing
        "071": ("marketing", "nb_salesmen_to"),
        "072": ("marketing", "commission"),
        "073": ("marketing", "coded_studies_abcd"),
        "074": ("marketing", "coded_studies_efgh"),
        "075": ("marketing", "nb_salesmen_mr"),
        "076": ("marketing", "quarterly_bonus"),
        "078": ("marketing", "advertising_to"),
        "079": ("marketing", "advertising_mr"),
        # Supply
        "080": ("supply", "raw_mat_n_order"),
        "081": ("supply", "raw_mat_n_contract_duration"),
        "082": ("supply", "raw_mat_s_order"),
        "083": ("supply", "raw_mat_s_contract_duration"),
        "086": ("supply", "maintenance"),
        # Production
        "089": ("production", "nb_active_machines_m1"),
        "090": ("production", "nb_active_machines_m2"),
        "091": ("production", "old_machines_m1_sold"),
        "092": ("production", "machines_m1_to_buy"),
        "093": ("production", "machines_m2_to_buy"),
        "094": ("production", "hiring_dismissal_workers"),
        "095": ("production", "variation_purchasing_power"),
        # CSR
        "087": ("csr", "recycling_budget"),
        "088": ("csr", "adapted_facilities"),
        "096": ("csr", "research_development"),
        # Finance
        "097": ("finance", "long_term_loan"),
        "098": ("finance", "long_term_loan_quarters"),
        "101": ("finance", "social_effort"),
        "102": ("finance", "short_term_loan"),
        "103": ("finance", "invoice_factoring"),
        "104": ("finance", "commercial_discount"),
        "105": ("finance", "dividends"),
        "106": ("finance", "early_repay_lt_loan"),
        "107": ("finance", "nb_new_shares_issued"),
        "108": ("finance", "offered_price_new_shares"),
        # Forecasts
        "121": ("forecasts", "sales_forecast_wt"),
        "122": ("forecasts", "result_forecast"),
        "123": ("forecasts", "cash_in_forecast"),
        "124": ("forecasts", "cash_out_forecast"),
        # Stocks
        "131": ("stocks", "purch_sale_shares_f1"),
        "132": ("stocks", "purch_sale_shares_f2"),
        "133": ("stocks", "purch_sale_shares_f3"),
        "134": ("stocks", "purch_sale_shares_f4"),
        "135": ("stocks", "purch_sale_shares_f5"),
        "136": ("stocks", "purch_sale_shares_f6"),
    }

    def __init__(self, file_path: Optional[Path] = None):
        super().__init__(file_path)
        self.firm_id: int = 1

    def set_firm_id(self, firm_id: int) -> None:
        """Set the firm ID for parsing."""
        self.firm_id = firm_id

    def parse(self) -> list[Decisions]:
        """Parse loaded decision data into Decisions models."""
        if self._data is None:
            raise ValueError("No data loaded. Call load_excel or load_csv first.")
        
        # This is a simplified parser - actual implementation depends on exact format
        decisions_list = []
        
        # Assuming columns represent periods (P.-3, P.-2, P.-1, P.0, P.1, etc.)
        # and rows are identified by codes (011, 012, etc.)
        
        # Get period columns (skip the first column which is the row identifier)
        period_columns = [col for col in self._data.columns if col != self._data.columns[0]]
        
        for period_idx, period_col in enumerate(period_columns):
            period_num = period_idx - 3  # Adjust based on actual data structure
            
            decisions = self._parse_period_column(period_col, period_num)
            if decisions:
                decisions_list.append(decisions)
        
        return decisions_list

    def _parse_period_column(self, column: str, period: int) -> Optional[Decisions]:
        """Parse a single period column into a Decisions object."""
        if self._data is None:
            return None
        
        # Initialize decision components
        product_a_to = ProductDecisions()
        product_a_mr = ProductDecisions()
        product_b_to = ProductDecisions()
        product_b_mr = ProductDecisions()
        product_c_to = ProductDecisions()
        product_c_mr = ProductDecisions()
        marketing = MarketingDecisions()
        supply = SupplyDecisions()
        production = ProductionDecisions()
        csr = CSRDecisions()
        finance = FinanceDecisions()
        forecasts = ForecastDecisions()
        stocks = StockDecisions()
        
        components = {
            "product_a_to": product_a_to,
            "product_a_mr": product_a_mr,
            "product_b_to": product_b_to,
            "product_b_mr": product_b_mr,
            "product_c_to": product_c_to,
            "product_c_mr": product_c_mr,
            "marketing": marketing,
            "supply": supply,
            "production": production,
            "csr": csr,
            "finance": finance,
            "forecasts": forecasts,
            "stocks": stocks,
        }
        
        # Parse each row
        for _, row in self._data.iterrows():
            row_code = str(row.iloc[0]).split("-")[0].strip()
            
            if row_code in self.ROW_MAPPINGS:
                component_name, field_name = self.ROW_MAPPINGS[row_code]
                value = row[column]
                
                component = components[component_name]
                self._set_field_value(component, field_name, value)
        
        return Decisions(
            firm_id=self.firm_id,
            period=period,
            product_a_to=product_a_to,
            product_a_mr=product_a_mr,
            product_b_to=product_b_to,
            product_b_mr=product_b_mr,
            product_c_to=product_c_to,
            product_c_mr=product_c_mr,
            marketing=marketing,
            supply=supply,
            production=production,
            csr=csr,
            finance=finance,
            forecasts=forecasts,
            stocks=stocks,
        )

    def _set_field_value(self, component: Any, field_name: str, value: Any) -> None:
        """Set a field value on a component, handling type conversion."""
        if pd.isna(value):
            return
        
        # Handle Y/N -> bool conversion
        if isinstance(value, str):
            if value.upper() in ("Y", "YES", "O", "OUI"):
                value = True
            elif value.upper() in ("N", "NO", "NON", "-N-"):
                value = False
        
        # Handle numeric conversion
        if hasattr(component, field_name):
            field_type = type(getattr(component, field_name))
            try:
                if field_type == int:
                    value = int(float(value))
                elif field_type == float:
                    value = float(value)
                elif field_type == bool and isinstance(value, (int, float)):
                    value = bool(value)
                
                setattr(component, field_name, value)
            except (ValueError, TypeError):
                pass  # Keep default value if conversion fails

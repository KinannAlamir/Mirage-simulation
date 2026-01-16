"""Decision models for Mirage simulation."""

from typing import Literal
from pydantic import BaseModel, Field


class ProductDecisions(BaseModel):
    """Decisions for a single product (A, B, or C) in a market (TO or MR)."""

    catalog_price: float = Field(default=0.0, ge=0, description="Catalog price (EUR/Unity)")
    promotion: float = Field(default=0.0, ge=0, description="Promotion (EUR/Unity)")
    production: int = Field(default=0, ge=0, description="Production (KU)")
    produced_quality: int = Field(default=0, ge=0, le=100, description="Produced quality (%)")
    recycled_packaging: bool = Field(default=False, description="Use recycled packaging (Y/N)")
    rebate_mr: float = Field(default=0.0, ge=0, le=100, description="Rebate MR (%) - MR only")


class MarketingDecisions(BaseModel):
    """Marketing decisions."""

    nb_salesmen_to: int = Field(default=0, ge=0, description="Number of salesmen TO")
    nb_salesmen_mr: int = Field(default=0, ge=0, description="Number of salesmen MR")
    commission: float = Field(default=0.0, ge=0, description="Commission (% Sales)")
    coded_studies_abcd: Literal["A", "B", "C", "D", "AB", "AC", "AD", "BC", "BD", "CD", 
                                 "ABC", "ABD", "ACD", "BCD", "ABCD", "N"] = Field(
        default="N", description="Coded studies A-D or N"
    )
    coded_studies_efgh: Literal["E", "F", "G", "H", "EF", "EG", "EH", "FG", "FH", "GH",
                                 "EFG", "EFH", "EGH", "FGH", "EFGH", "N"] = Field(
        default="N", description="Coded studies E-H or N"
    )
    quarterly_bonus: float = Field(default=0.0, ge=0, description="Quarterly bonus (EUR/Salesman)")
    advertising_to: float = Field(default=0.0, ge=0, description="Advertising TO (KEUR)")
    advertising_mr: float = Field(default=0.0, ge=0, description="Advertising MR (KEUR)")


class SupplyDecisions(BaseModel):
    """Supply and maintenance decisions."""

    raw_mat_n_order: int = Field(default=0, ge=0, description="Raw Mat. N order (KU/period)")
    raw_mat_n_contract_duration: int = Field(
        default=0, ge=0, le=4, description="Contract duration 1-4 periods"
    )
    raw_mat_s_order: int = Field(default=0, ge=0, description="Raw Mat. S order (KU/period)")
    raw_mat_s_contract_duration: int = Field(
        default=0, ge=0, le=4, description="Contract duration 1-4 periods"
    )
    maintenance: bool = Field(default=True, description="Maintenance (Y/N)")


class ProductionDecisions(BaseModel):
    """Production decisions."""

    nb_active_machines_m1: int = Field(default=0, ge=0, description="Nb of active Mach. M1 (U)")
    nb_active_machines_m2: int = Field(default=0, ge=0, description="Nb of active Mach. M2 (U)")
    old_machines_m1_sold: int = Field(default=0, ge=0, description="Old machines M1 sold (U)")
    machines_m1_to_buy: int = Field(default=0, ge=0, description="Machines M1 to buy (U)")
    machines_m2_to_buy: int = Field(default=0, ge=0, description="Machines M2 to buy (U)")
    hiring_dismissal_workers: int = Field(
        default=0, description="Hiring (+) / Dismissal (-) workers (U)"
    )
    variation_purchasing_power: float = Field(
        default=0.0, description="Variation purchasing power (%)"
    )


class CSRDecisions(BaseModel):
    """CSR (Corporate Social Responsibility) decisions."""

    recycling_budget: float = Field(default=0.0, ge=0, description="Recycling budget (KEUR)")
    adapted_facilities: float = Field(default=0.0, ge=0, description="Adapted facilities (KEUR)")
    research_development: float = Field(default=0.0, ge=0, description="Research & Development (KEUR)")


class FinanceDecisions(BaseModel):
    """Finance and stock market decisions."""

    long_term_loan: float = Field(default=0.0, ge=0, description="Long term loan (KEUR)")
    long_term_loan_quarters: int = Field(
        default=0, ge=0, le=8, description="Nb of quarters 2 to 8"
    )
    social_effort: float = Field(default=0.0, ge=0, description="Social effort (%)")
    short_term_loan: float = Field(default=0.0, ge=0, description="Short term loan (KEUR)")
    invoice_factoring: float = Field(
        default=0.0, ge=0, description="Invoice factoring to bank (KEUR)"
    )
    commercial_discount: float = Field(default=0.0, ge=0, description="Commercial discount (%)")
    dividends: float = Field(default=0.0, ge=0, description="Dividends (KEUR)")
    early_repay_lt_loan: bool = Field(default=False, description="Early repay LT loan (Y/N)")
    nb_new_shares_issued: int = Field(default=0, ge=0, description="Nb new shares issued (KU)")
    offered_price_new_shares: float = Field(
        default=0.0, ge=0, description="Offered price new shares (EUR)"
    )


class ForecastDecisions(BaseModel):
    """Forecast decisions."""

    sales_forecast_wt: float = Field(default=0.0, ge=0, description="Sales forecast WT (KEUR)")
    result_forecast: float = Field(default=0.0, description="Result forecast (KEUR)")
    cash_in_forecast: float = Field(default=0.0, ge=0, description="Cash in forecast (KEUR)")
    cash_out_forecast: float = Field(default=0.0, ge=0, description="Cash out forecast (KEUR)")


class StockDecisions(BaseModel):
    """Stock purchase/sale decisions."""

    purch_sale_shares_f1: int = Field(default=0, description="Purchase (+) / Sale (-) shares F1")
    purch_sale_shares_f2: int = Field(default=0, description="Purchase (+) / Sale (-) shares F2")
    purch_sale_shares_f3: int = Field(default=0, description="Purchase (+) / Sale (-) shares F3")
    purch_sale_shares_f4: int = Field(default=0, description="Purchase (+) / Sale (-) shares F4")
    purch_sale_shares_f5: int = Field(default=0, description="Purchase (+) / Sale (-) shares F5")
    purch_sale_shares_f6: int = Field(default=0, description="Purchase (+) / Sale (-) shares F6")


class Decisions(BaseModel):
    """All decisions for a firm in a period."""

    firm_id: int = Field(..., ge=1, le=6, description="Firm ID")
    period: int = Field(..., description="Period number")
    
    # Products - TO Market
    product_a_to: ProductDecisions = Field(default_factory=ProductDecisions)
    product_b_to: ProductDecisions = Field(default_factory=ProductDecisions)
    product_c_to: ProductDecisions = Field(default_factory=ProductDecisions)
    
    # Products - MR Market
    product_a_mr: ProductDecisions = Field(default_factory=ProductDecisions)
    product_b_mr: ProductDecisions = Field(default_factory=ProductDecisions)
    product_c_mr: ProductDecisions = Field(default_factory=ProductDecisions)
    
    # Other decisions
    marketing: MarketingDecisions = Field(default_factory=MarketingDecisions)
    supply: SupplyDecisions = Field(default_factory=SupplyDecisions)
    production: ProductionDecisions = Field(default_factory=ProductionDecisions)
    csr: CSRDecisions = Field(default_factory=CSRDecisions)
    finance: FinanceDecisions = Field(default_factory=FinanceDecisions)
    forecasts: ForecastDecisions = Field(default_factory=ForecastDecisions)
    stocks: StockDecisions = Field(default_factory=StockDecisions)

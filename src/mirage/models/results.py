"""Results models for Mirage simulation."""

from pydantic import BaseModel, Field


class FirmSummary(BaseModel):
    """Summary results for a firm."""

    firm_id: int = Field(..., ge=1, le=6)
    period: int
    sales: float = Field(default=0.0, description="Sales (KEUR)")
    result: float = Field(default=0.0, description="Result (KEUR)")
    smpi: float = Field(default=0.0, description="SMPI index")
    financial_score: float = Field(default=0.0, description="Financial score")
    rse_score: float = Field(default=0.0, description="RSE score")


class IncomeStatementLine(BaseModel):
    """A line item in the income statement."""

    label: str
    amount: float = 0.0


class IncomeStatement(BaseModel):
    """Income statement for a firm."""

    firm_id: int = Field(..., ge=1, le=6)
    period: int
    
    # Revenue
    sales_to: float = Field(default=0.0, description="Sales TO")
    sales_mr: float = Field(default=0.0, description="Sales MR")
    total_revenue: float = Field(default=0.0, description="Total revenue")
    
    # Costs
    raw_materials: float = Field(default=0.0, description="Raw materials cost")
    direct_labor: float = Field(default=0.0, description="Direct labor cost")
    production_overhead: float = Field(default=0.0, description="Production overhead")
    marketing_costs: float = Field(default=0.0, description="Marketing costs")
    admin_costs: float = Field(default=0.0, description="Administrative costs")
    depreciation: float = Field(default=0.0, description="Depreciation")
    
    # Results
    operating_result: float = Field(default=0.0, description="Operating result")
    financial_result: float = Field(default=0.0, description="Financial result")
    exceptional_result: float = Field(default=0.0, description="Exceptional result")
    taxes: float = Field(default=0.0, description="Taxes")
    net_result: float = Field(default=0.0, description="Net result")


class BalanceSheetAssets(BaseModel):
    """Assets side of balance sheet."""

    fixed_assets: float = Field(default=0.0, description="Fixed assets (gross)")
    accumulated_depreciation: float = Field(default=0.0, description="Accumulated depreciation")
    net_fixed_assets: float = Field(default=0.0, description="Net fixed assets")
    
    raw_materials_stock: float = Field(default=0.0, description="Raw materials stock")
    finished_goods_stock: float = Field(default=0.0, description="Finished goods stock")
    accounts_receivable: float = Field(default=0.0, description="Accounts receivable")
    cash: float = Field(default=0.0, description="Cash")
    
    total_assets: float = Field(default=0.0, description="Total assets")


class BalanceSheetLiabilities(BaseModel):
    """Liabilities side of balance sheet."""

    share_capital: float = Field(default=0.0, description="Share capital")
    reserves: float = Field(default=0.0, description="Reserves")
    retained_earnings: float = Field(default=0.0, description="Retained earnings")
    net_result: float = Field(default=0.0, description="Net result")
    total_equity: float = Field(default=0.0, description="Total equity")
    
    long_term_debt: float = Field(default=0.0, description="Long term debt")
    short_term_debt: float = Field(default=0.0, description="Short term debt")
    accounts_payable: float = Field(default=0.0, description="Accounts payable")
    
    total_liabilities: float = Field(default=0.0, description="Total liabilities")


class BalanceSheet(BaseModel):
    """Balance sheet for a firm."""

    firm_id: int = Field(..., ge=1, le=6)
    period: int
    assets: BalanceSheetAssets = Field(default_factory=BalanceSheetAssets)
    liabilities: BalanceSheetLiabilities = Field(default_factory=BalanceSheetLiabilities)


class CashSituation(BaseModel):
    """Cash flow situation for a firm."""

    firm_id: int = Field(..., ge=1, le=6)
    period: int
    
    # Cash inflows
    cash_from_sales: float = Field(default=0.0)
    cash_from_financing: float = Field(default=0.0)
    other_cash_in: float = Field(default=0.0)
    total_cash_in: float = Field(default=0.0)
    
    # Cash outflows
    cash_for_purchases: float = Field(default=0.0)
    cash_for_salaries: float = Field(default=0.0)
    cash_for_investments: float = Field(default=0.0)
    cash_for_debt_service: float = Field(default=0.0)
    cash_for_dividends: float = Field(default=0.0)
    cash_for_taxes: float = Field(default=0.0)
    other_cash_out: float = Field(default=0.0)
    total_cash_out: float = Field(default=0.0)
    
    # Net position
    net_cash_flow: float = Field(default=0.0)
    opening_cash: float = Field(default=0.0)
    closing_cash: float = Field(default=0.0)


class OperatingProduct(BaseModel):
    """Operating data for a product."""

    product: str = Field(..., description="Product code (A, B, C)")
    market: str = Field(..., description="Market (TO, MR)")
    
    production_volume: int = Field(default=0)
    sales_volume: int = Field(default=0)
    unit_cost: float = Field(default=0.0)
    unit_price: float = Field(default=0.0)
    revenue: float = Field(default=0.0)
    cost_of_goods_sold: float = Field(default=0.0)


class ProfitProduct(BaseModel):
    """Profit analysis for a product."""

    product: str = Field(..., description="Product code (A, B, C)")
    market: str = Field(..., description="Market (TO, MR)")
    
    revenue: float = Field(default=0.0)
    variable_costs: float = Field(default=0.0)
    contribution_margin: float = Field(default=0.0)
    fixed_costs_allocated: float = Field(default=0.0)
    operating_profit: float = Field(default=0.0)
    margin_percentage: float = Field(default=0.0)


class Stocks(BaseModel):
    """Stock levels for a firm."""

    firm_id: int = Field(..., ge=1, le=6)
    period: int
    
    # Raw materials
    raw_mat_n_quantity: int = Field(default=0, description="Raw Mat N quantity (KU)")
    raw_mat_n_value: float = Field(default=0.0, description="Raw Mat N value (KEUR)")
    raw_mat_s_quantity: int = Field(default=0, description="Raw Mat S quantity (KU)")
    raw_mat_s_value: float = Field(default=0.0, description="Raw Mat S value (KEUR)")
    
    # Finished products - TO
    product_a_to_quantity: int = Field(default=0)
    product_a_to_value: float = Field(default=0.0)
    product_b_to_quantity: int = Field(default=0)
    product_b_to_value: float = Field(default=0.0)
    product_c_to_quantity: int = Field(default=0)
    product_c_to_value: float = Field(default=0.0)
    
    # Finished products - MR
    product_a_mr_quantity: int = Field(default=0)
    product_a_mr_value: float = Field(default=0.0)
    product_b_mr_quantity: int = Field(default=0)
    product_b_mr_value: float = Field(default=0.0)
    product_c_mr_quantity: int = Field(default=0)
    product_c_mr_value: float = Field(default=0.0)

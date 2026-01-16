"""Market and competition models for Mirage simulation."""

from typing import Optional
from pydantic import BaseModel, Field


class MarketSegment(BaseModel):
    """Market segment data."""

    name: str
    size: int = Field(default=0, description="Market size (KU)")
    growth_rate: float = Field(default=0.0, description="Growth rate (%)")
    price_sensitivity: float = Field(default=0.0, description="Price sensitivity")
    quality_sensitivity: float = Field(default=0.0, description="Quality sensitivity")


class MarketData(BaseModel):
    """Overall market data."""

    period: int
    
    # TO Market
    to_market_size: int = Field(default=0, description="TO market size (KU)")
    to_market_growth: float = Field(default=0.0, description="TO market growth (%)")
    
    # MR Market
    mr_market_size: int = Field(default=0, description="MR market size (KU)")
    mr_market_growth: float = Field(default=0.0, description="MR market growth (%)")
    
    # Economic indicators
    inflation_rate: float = Field(default=0.0, description="Inflation rate (%)")
    interest_rate: float = Field(default=0.0, description="Interest rate (%)")
    exchange_rate: float = Field(default=1.0, description="Exchange rate")


class CompetitorProduct(BaseModel):
    """Competitor's product information."""

    product: str = Field(..., description="Product code (A, B, C)")
    market: str = Field(..., description="Market (TO, MR)")
    price: float = Field(default=0.0)
    quality: int = Field(default=0)
    recycled_packaging: bool = Field(default=False)
    market_share: float = Field(default=0.0)


class CompetitorData(BaseModel):
    """Competitor information."""

    firm_id: int = Field(..., ge=1, le=6)
    period: int
    
    # General info
    sales: float = Field(default=0.0, description="Sales (KEUR)")
    result: float = Field(default=0.0, description="Result (KEUR)")
    smpi: float = Field(default=0.0, description="SMPI index")
    financial_score: float = Field(default=0.0)
    rse_score: float = Field(default=0.0)
    
    # Workforce
    nb_workers: int = Field(default=0, description="Number of workers")
    avg_wage: float = Field(default=0.0, description="Average wage")
    
    # Salesforce
    to_salesforce_nb: int = Field(default=0)
    mr_salesforce_nb: int = Field(default=0)
    to_salesforce_wage: float = Field(default=0.0)
    mr_salesforce_wage: float = Field(default=0.0)
    
    # Products
    products: list[CompetitorProduct] = Field(default_factory=list)
    
    # Advertising
    advertising_to: float = Field(default=0.0)
    advertising_mr: float = Field(default=0.0)


class StudyData(BaseModel):
    """Market study data."""

    study_code: str = Field(..., description="Study code (A-H)")
    period: int
    firm_id: int = Field(..., ge=1, le=6)
    
    # Study content depends on type
    content: dict = Field(default_factory=dict, description="Study-specific content")
    
    @property
    def study_name(self) -> str:
        study_names = {
            "A": "Market Evolution",
            "B": "Consumer Behavior",
            "C": "Competition Analysis",
            "D": "Distribution Channels",
            "E": "Economic Outlook",
            "F": "Financial Analysis",
            "G": "Geographic Analysis",
            "H": "Human Resources",
        }
        return study_names.get(self.study_code, "Unknown Study")


class RawMaterialsData(BaseModel):
    """Raw materials market data."""

    period: int
    
    # Normal quality (N)
    mat_n_spot_price: float = Field(default=0.0, description="Mat N spot price (EUR/KU)")
    mat_n_contract_prices: list[float] = Field(
        default_factory=list, description="Mat N contract prices by duration"
    )
    
    # Superior quality (S)
    mat_s_spot_price: float = Field(default=0.0, description="Mat S spot price (EUR/KU)")
    mat_s_contract_prices: list[float] = Field(
        default_factory=list, description="Mat S contract prices by duration"
    )


class StockMarketData(BaseModel):
    """Stock market data."""

    period: int
    
    firm_prices: dict[int, float] = Field(
        default_factory=dict, description="Share prices by firm ID"
    )
    firm_volumes: dict[int, int] = Field(
        default_factory=dict, description="Trading volumes by firm ID"
    )
    market_index: float = Field(default=0.0, description="Market index value")

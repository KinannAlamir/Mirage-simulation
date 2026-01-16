"""Market data loader."""

from pathlib import Path
from typing import Optional, Any

import pandas as pd

from mirage.loaders.base_loader import BaseLoader
from mirage.models.market import (
    MarketData,
    CompetitorData,
    CompetitorProduct,
    StudyData,
    RawMaterialsData,
)


class MarketLoader(BaseLoader):
    """Loader for market and study data."""

    def __init__(self, file_path: Optional[Path] = None):
        super().__init__(file_path)
        self.period: int = 0

    def set_period(self, period: int) -> None:
        """Set period context for parsing."""
        self.period = period

    def parse(self) -> dict[str, Any]:
        """Parse all market data types."""
        return {
            "market_data": self.parse_market_data(),
            "competitors": self.parse_competitors(),
            "studies": self.parse_studies(),
        }

    def parse_market_data(self) -> Optional[MarketData]:
        """Parse general market data."""
        if self._data is None:
            return None
        
        return MarketData(period=self.period)

    def parse_competitors(self) -> list[CompetitorData]:
        """Parse competitor data (Studies + ABC format)."""
        if self._data is None:
            return []
        
        competitors = []
        
        # This needs to be adapted to the actual spreadsheet format
        # Based on the image, the Studies+ABC sheet has this format
        
        return competitors

    def parse_studies(self) -> list[StudyData]:
        """Parse study data (A-H)."""
        if self._data is None:
            return []
        
        return []

    def parse_abc_study(self, df: pd.DataFrame, firm_id: int) -> Optional[CompetitorData]:
        """Parse ABC study data for a specific firm."""
        # Based on the Studies + ABC format shown in the image
        try:
            # Find the column for this firm (columns are 1-6)
            firm_col = str(firm_id)
            
            if firm_col not in df.columns:
                return None
            
            # Parse the relevant rows
            competitor = CompetitorData(
                firm_id=firm_id,
                period=self.period,
            )
            
            # Extract data based on row labels
            for _, row in df.iterrows():
                label = str(row.iloc[0]).strip().lower() if pd.notna(row.iloc[0]) else ""
                value = row.get(firm_col, 0)
                
                if "number of workers" in label:
                    competitor.nb_workers = int(value) if pd.notna(value) else 0
                elif "av. wage" in label or "average wage" in label:
                    competitor.avg_wage = float(value) if pd.notna(value) else 0.0
                elif "to salesforce nb" in label:
                    competitor.to_salesforce_nb = int(value) if pd.notna(value) else 0
                elif "mr salesforce nb" in label:
                    competitor.mr_salesforce_nb = int(value) if pd.notna(value) else 0
                elif "to salesforce wage" in label:
                    competitor.to_salesforce_wage = float(value) if pd.notna(value) else 0.0
                elif "mr salesforce wage" in label:
                    competitor.mr_salesforce_wage = float(value) if pd.notna(value) else 0.0
                elif "advertising to" in label:
                    competitor.advertising_to = float(value) if pd.notna(value) else 0.0
                elif "advertising mr" in label:
                    competitor.advertising_mr = float(value) if pd.notna(value) else 0.0
            
            # Parse quality/recycl.pack rows for products
            competitor.products = self._parse_product_rows(df, firm_col)
            
            return competitor
            
        except Exception:
            return None

    def _parse_product_rows(self, df: pd.DataFrame, firm_col: str) -> list[CompetitorProduct]:
        """Parse product quality and packaging rows."""
        products = []
        
        product_configs = [
            ("A", "TO"), ("A", "MR"),
            ("B", "TO"), ("B", "MR"),
            ("C", "TO"), ("C", "MR"),
        ]
        
        for product, market in product_configs:
            search_label = f"quality/recycl.pack. {product.lower()}-{market.lower()}"
            
            for _, row in df.iterrows():
                label = str(row.iloc[0]).strip().lower() if pd.notna(row.iloc[0]) else ""
                
                if search_label in label:
                    value = str(row.get(firm_col, "0-N"))
                    parts = value.split("-")
                    
                    quality = int(parts[0]) if parts[0].isdigit() else 0
                    recycled = parts[1].upper() == "Y" if len(parts) > 1 else False
                    
                    products.append(CompetitorProduct(
                        product=product,
                        market=market,
                        quality=quality,
                        recycled_packaging=recycled,
                    ))
                    break
        
        return products

    def parse_raw_materials(self, df: pd.DataFrame) -> Optional[RawMaterialsData]:
        """Parse raw materials market data."""
        return RawMaterialsData(period=self.period)

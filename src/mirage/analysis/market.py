"""Market analysis module."""

from typing import Optional
from mirage.models.market import CompetitorData, MarketData


class MarketAnalyzer:
    """Analyzer for market data."""

    def calculate_market_share(
        self, firm_sales: float, total_market_sales: float
    ) -> float:
        """Calculate market share percentage."""
        if total_market_sales == 0:
            return 0.0
        return (firm_sales / total_market_sales) * 100

    def calculate_relative_market_share(
        self, firm_share: float, leader_share: float
    ) -> float:
        """Calculate relative market share vs leader."""
        if leader_share == 0:
            return 0.0
        return firm_share / leader_share

    def rank_competitors(
        self, competitors: list[CompetitorData], metric: str = "sales"
    ) -> list[tuple[int, float, int]]:
        """Rank competitors by a metric. Returns (firm_id, value, rank)."""
        values = [(c.firm_id, getattr(c, metric, 0)) for c in competitors]
        sorted_values = sorted(values, key=lambda x: x[1], reverse=True)
        
        return [
            (firm_id, value, rank + 1)
            for rank, (firm_id, value) in enumerate(sorted_values)
        ]

    def analyze_pricing_position(
        self, 
        firm_price: float, 
        competitor_prices: list[float]
    ) -> dict:
        """Analyze firm's pricing position vs competitors."""
        if not competitor_prices:
            return {"position": "unknown"}
        
        avg_price = sum(competitor_prices) / len(competitor_prices)
        min_price = min(competitor_prices)
        max_price = max(competitor_prices)
        
        if firm_price < min_price:
            position = "lowest"
        elif firm_price > max_price:
            position = "highest"
        elif firm_price < avg_price:
            position = "below_average"
        elif firm_price > avg_price:
            position = "above_average"
        else:
            position = "average"
        
        return {
            "position": position,
            "firm_price": firm_price,
            "avg_competitor_price": avg_price,
            "min_competitor_price": min_price,
            "max_competitor_price": max_price,
            "price_vs_avg": firm_price - avg_price,
            "price_vs_avg_pct": ((firm_price - avg_price) / avg_price * 100) if avg_price else 0,
        }

    def analyze_quality_position(
        self,
        firm_quality: int,
        competitor_qualities: list[int]
    ) -> dict:
        """Analyze firm's quality position vs competitors."""
        if not competitor_qualities:
            return {"position": "unknown"}
        
        avg_quality = sum(competitor_qualities) / len(competitor_qualities)
        
        if firm_quality > avg_quality:
            position = "above_average"
        elif firm_quality < avg_quality:
            position = "below_average"
        else:
            position = "average"
        
        return {
            "position": position,
            "firm_quality": firm_quality,
            "avg_competitor_quality": avg_quality,
            "quality_vs_avg": firm_quality - avg_quality,
        }

    def identify_market_leader(
        self, competitors: list[CompetitorData]
    ) -> Optional[CompetitorData]:
        """Identify the market leader by sales."""
        if not competitors:
            return None
        
        return max(competitors, key=lambda c: c.sales)

    def calculate_concentration_ratio(
        self, market_shares: list[float], top_n: int = 4
    ) -> float:
        """Calculate CR-n (concentration ratio for top n firms)."""
        sorted_shares = sorted(market_shares, reverse=True)
        return sum(sorted_shares[:top_n])

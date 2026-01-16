"""Tests for analysis service."""

import pytest
from mirage.services.analysis_service import AnalysisService


class TestAnalysisService:
    """Tests for AnalysisService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AnalysisService()

    def test_calculate_market_share(self):
        """Test market share calculation."""
        firm_sales = 1000.0
        all_sales = [1000.0, 2000.0, 1500.0, 500.0]
        
        share = self.service.calculate_market_share(firm_sales, all_sales)
        
        assert share == 20.0  # 1000 / 5000 * 100

    def test_calculate_market_share_zero_total(self):
        """Test market share with zero total."""
        share = self.service.calculate_market_share(0, [0, 0, 0])
        assert share == 0.0

    def test_calculate_growth_rate(self):
        """Test growth rate calculation."""
        growth = self.service.calculate_growth_rate(1100.0, 1000.0)
        assert growth == 10.0

    def test_calculate_growth_rate_negative(self):
        """Test negative growth rate."""
        growth = self.service.calculate_growth_rate(900.0, 1000.0)
        assert growth == -10.0

    def test_calculate_growth_rate_zero_previous(self):
        """Test growth rate with zero previous."""
        growth = self.service.calculate_growth_rate(100.0, 0.0)
        assert growth == 100.0

    def test_calculate_trend(self):
        """Test trend calculation."""
        values = [100.0, 110.0, 120.0, 130.0]
        
        trend = self.service.calculate_trend(values)
        
        assert trend["trend"] == "up"
        assert trend["slope"] > 0
        assert trend["min"] == 100.0
        assert trend["max"] == 130.0

    def test_calculate_trend_insufficient_data(self):
        """Test trend with insufficient data."""
        trend = self.service.calculate_trend([100.0])
        assert trend["trend"] == "insufficient_data"

"""Tests for decision models."""

import pytest
from mirage.models.decisions import (
    ProductDecisions,
    MarketingDecisions,
    ProductionDecisions,
    Decisions,
)


class TestProductDecisions:
    """Tests for ProductDecisions model."""

    def test_default_values(self):
        """Test default values are set correctly."""
        product = ProductDecisions()
        
        assert product.catalog_price == 0.0
        assert product.promotion == 0.0
        assert product.production == 0
        assert product.produced_quality == 0
        assert product.recycled_packaging is False
        assert product.rebate_mr == 0.0

    def test_custom_values(self):
        """Test custom values are set correctly."""
        product = ProductDecisions(
            catalog_price=20.60,
            promotion=0.30,
            production=420,
            produced_quality=100,
            recycled_packaging=False,
        )
        
        assert product.catalog_price == 20.60
        assert product.promotion == 0.30
        assert product.production == 420
        assert product.produced_quality == 100


class TestMarketingDecisions:
    """Tests for MarketingDecisions model."""

    def test_default_values(self):
        """Test default values."""
        marketing = MarketingDecisions()
        
        assert marketing.nb_salesmen_to == 0
        assert marketing.nb_salesmen_mr == 0
        assert marketing.commission == 0.0
        assert marketing.coded_studies_abcd == "N"

    def test_studies_codes(self):
        """Test study code validation."""
        marketing = MarketingDecisions(
            coded_studies_abcd="ABC",
            coded_studies_efgh="N",
        )
        
        assert marketing.coded_studies_abcd == "ABC"
        assert marketing.coded_studies_efgh == "N"


class TestDecisions:
    """Tests for complete Decisions model."""

    def test_create_decisions(self):
        """Test creating a complete decisions object."""
        decisions = Decisions(
            firm_id=1,
            period=0,
        )
        
        assert decisions.firm_id == 1
        assert decisions.period == 0
        assert decisions.product_a_to.catalog_price == 0.0

    def test_decisions_with_products(self):
        """Test decisions with product data."""
        decisions = Decisions(
            firm_id=1,
            period=1,
            product_a_to=ProductDecisions(
                catalog_price=20.60,
                production=420,
                produced_quality=100,
            ),
        )
        
        assert decisions.product_a_to.catalog_price == 20.60
        assert decisions.product_a_to.production == 420

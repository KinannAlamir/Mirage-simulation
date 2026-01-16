"""Form components for decision input."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from typing import Optional, Callable
import streamlit as st

from mirage.models.decisions import (
    ProductDecisions,
    MarketingDecisions,
    ProductionDecisions,
    SupplyDecisions,
    FinanceDecisions,
    CSRDecisions,
)


def render_product_form(
    product_code: str,
    market: str,
    current_values: Optional[ProductDecisions] = None,
    on_change: Optional[Callable] = None,
) -> ProductDecisions:
    """Render a product decision form.
    
    Args:
        product_code: Product code (A, B, C)
        market: Market (TO, MR)
        current_values: Current decision values
        on_change: Callback when values change
        
    Returns:
        Updated ProductDecisions
    """
    current = current_values or ProductDecisions()
    
    st.write(f"**Product {product_code} - {market}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        catalog_price = st.number_input(
            "Catalog Price (EUR/Unity)",
            min_value=0.0,
            value=float(current.catalog_price),
            step=0.10,
            key=f"price_{product_code}_{market}",
        )
        
        production = st.number_input(
            "Production (KU)",
            min_value=0,
            value=int(current.production),
            step=10,
            key=f"prod_{product_code}_{market}",
        )
        
        quality = st.slider(
            "Quality (%)",
            min_value=0,
            max_value=100,
            value=int(current.produced_quality),
            key=f"qual_{product_code}_{market}",
        )
    
    with col2:
        promotion = st.number_input(
            "Promotion (EUR/Unity)",
            min_value=0.0,
            value=float(current.promotion),
            step=0.10,
            key=f"promo_{product_code}_{market}",
        )
        
        recycled = st.checkbox(
            "Recycled Packaging",
            value=current.recycled_packaging,
            key=f"recyc_{product_code}_{market}",
        )
        
        rebate = 0.0
        if market == "MR":
            rebate = st.number_input(
                "Rebate MR (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(current.rebate_mr),
                step=0.5,
                key=f"rebate_{product_code}_{market}",
            )
    
    return ProductDecisions(
        catalog_price=catalog_price,
        promotion=promotion,
        production=production,
        produced_quality=quality,
        recycled_packaging=recycled,
        rebate_mr=rebate,
    )


def render_marketing_form(
    current_values: Optional[MarketingDecisions] = None,
) -> MarketingDecisions:
    """Render marketing decisions form."""
    current = current_values or MarketingDecisions()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Salesforce**")
        nb_salesmen_to = st.number_input(
            "Salesmen TO",
            min_value=0,
            value=current.nb_salesmen_to,
            key="salesmen_to",
        )
        
        nb_salesmen_mr = st.number_input(
            "Salesmen MR",
            min_value=0,
            value=current.nb_salesmen_mr,
            key="salesmen_mr",
        )
        
        commission = st.number_input(
            "Commission (% Sales)",
            min_value=0.0,
            value=current.commission,
            step=0.1,
            key="commission",
        )
        
        quarterly_bonus = st.number_input(
            "Quarterly Bonus (EUR/Salesman)",
            min_value=0.0,
            value=current.quarterly_bonus,
            step=100.0,
            key="bonus",
        )
    
    with col2:
        st.write("**Advertising**")
        advertising_to = st.number_input(
            "Advertising TO (KEUR)",
            min_value=0.0,
            value=current.advertising_to,
            step=50.0,
            key="adv_to",
        )
        
        advertising_mr = st.number_input(
            "Advertising MR (KEUR)",
            min_value=0.0,
            value=current.advertising_mr,
            step=50.0,
            key="adv_mr",
        )
        
        st.write("**Studies**")
        coded_studies_abcd = st.text_input(
            "Studies A-D (or N)",
            value=current.coded_studies_abcd,
            max_chars=4,
            key="studies_abcd",
        ).upper() or "N"
        
        coded_studies_efgh = st.text_input(
            "Studies E-H (or N)",
            value=current.coded_studies_efgh,
            max_chars=4,
            key="studies_efgh",
        ).upper() or "N"
    
    return MarketingDecisions(
        nb_salesmen_to=nb_salesmen_to,
        nb_salesmen_mr=nb_salesmen_mr,
        commission=commission,
        quarterly_bonus=quarterly_bonus,
        advertising_to=advertising_to,
        advertising_mr=advertising_mr,
        coded_studies_abcd=coded_studies_abcd,
        coded_studies_efgh=coded_studies_efgh,
    )


def render_production_form(
    current_values: Optional[ProductionDecisions] = None,
) -> ProductionDecisions:
    """Render production decisions form."""
    current = current_values or ProductionDecisions()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Machines**")
        nb_m1 = st.number_input(
            "Active Machines M1",
            min_value=0,
            value=current.nb_active_machines_m1,
            key="machines_m1",
        )
        
        nb_m2 = st.number_input(
            "Active Machines M2",
            min_value=0,
            value=current.nb_active_machines_m2,
            key="machines_m2",
        )
        
        m1_sold = st.number_input(
            "Old M1 to Sell",
            min_value=0,
            value=current.old_machines_m1_sold,
            key="m1_sell",
        )
        
        m1_buy = st.number_input(
            "M1 to Buy",
            min_value=0,
            value=current.machines_m1_to_buy,
            key="m1_buy",
        )
        
        m2_buy = st.number_input(
            "M2 to Buy",
            min_value=0,
            value=current.machines_m2_to_buy,
            key="m2_buy",
        )
    
    with col2:
        st.write("**Workers**")
        hiring = st.number_input(
            "Hiring (+) / Dismissal (-)",
            value=current.hiring_dismissal_workers,
            key="hiring",
        )
        
        purch_power = st.number_input(
            "Variation Purchasing Power (%)",
            value=current.variation_purchasing_power,
            step=0.5,
            key="purch_power",
        )
    
    return ProductionDecisions(
        nb_active_machines_m1=nb_m1,
        nb_active_machines_m2=nb_m2,
        old_machines_m1_sold=m1_sold,
        machines_m1_to_buy=m1_buy,
        machines_m2_to_buy=m2_buy,
        hiring_dismissal_workers=hiring,
        variation_purchasing_power=purch_power,
    )


def render_decision_form(form_type: str, current_values: Optional[dict] = None) -> dict:
    """Render a generic decision form based on type.
    
    Args:
        form_type: Type of form (product, marketing, production, supply, finance, csr)
        current_values: Current values as dict
        
    Returns:
        Updated values as dict
    """
    # Dispatch to appropriate form renderer
    if form_type == "marketing":
        result = render_marketing_form(
            MarketingDecisions(**current_values) if current_values else None
        )
        return result.model_dump()
    elif form_type == "production":
        result = render_production_form(
            ProductionDecisions(**current_values) if current_values else None
        )
        return result.model_dump()
    else:
        st.warning(f"Form type '{form_type}' not implemented yet")
        return current_values or {}

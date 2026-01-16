"""Streamlit application for Mirage simulation decision support."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd

from src.mirage.models import (
    AllDecisions,
    ProductDecision,
    MarketingDecision,
    ApprovisionnementDecision,
    ProductionDecision,
    RSEDecision,
    FinanceDecision,
    TitresDecision,
    PeriodState,
)
from src.mirage.calculator import calculate_all, calculate_study_costs
from src.mirage import constants as C
from src.mirage.parser import parse_mirage_markdown, extract_period_state, get_empty_state
from src.mirage.utils import serialize_simulation_state, deserialize_simulation_state

def sync_widgets_with_state(state: PeriodState):
    """Met à jour les widgets de la sidebar avec les valeurs de l'état."""
    st.session_state.s_a_ct = float(state.stock_a_ct) if state.stock_a_ct is not None else 0.0
    st.session_state.s_a_gs = float(state.stock_a_gs) if state.stock_a_gs is not None else 0.0
    st.session_state.s_b_ct = float(state.stock_b_ct) if state.stock_b_ct is not None else 0.0
    st.session_state.s_b_gs = float(state.stock_b_gs) if state.stock_b_gs is not None else 0.0
    st.session_state.s_c_ct = float(state.stock_c_ct) if state.stock_c_ct is not None else 0.0
    st.session_state.s_c_gs = float(state.stock_c_gs) if state.stock_c_gs is not None else 0.0
    st.session_state.s_mp_n = int(state.stock_mp_n) if state.stock_mp_n is not None else 0
    st.session_state.s_mp_s = int(state.stock_mp_s) if state.stock_mp_s is not None else 0
    st.session_state.s_ouvriers = int(state.nb_ouvriers) if state.nb_ouvriers is not None else 0
    st.session_state.s_m1 = int(state.nb_machines_m1) if state.nb_machines_m1 is not None else 0
    st.session_state.s_m2 = int(state.nb_machines_m2) if state.nb_machines_m2 is not None else 0
    st.session_state.s_cash = float(state.cash) if state.cash is not None else 0.0
    st.session_state.s_dlt = float(state.dette_lt) if state.dette_lt is not None else 0.0
    st.session_state.s_dct = float(state.dette_ct) if state.dette_ct is not None else 0.0
    st.session_state.s_ip = float(state.indice_prix) if state.indice_prix is not None else 0.0
    st.session_state.s_is = float(state.indice_salaire) if state.indice_salaire is not None else 0.0

# Page config
st.set_page_config(
    page_title="Mirage - Aide à la Décision",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏭 Mirage - Simulateur de Décisions")
st.markdown("---")

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = PeriodState(
        stock_a_ct=609_212,
        stock_a_gs=0,
        stock_b_ct=0,
        stock_b_gs=355_257,
        stock_c_ct=0,
        stock_c_gs=0,
        stock_mp_n=2_889_090,
        stock_mp_s=687_500,
        nb_ouvriers=580,
        nb_machines_m1=18,
        nb_machines_m2=0,
        cash=414.0,
        dette_lt=5_600.0,
        dette_ct=0.0,
        indice_prix=107.12,
        indice_salaire=103.0,
    )
    sync_widgets_with_state(st.session_state.state)
elif "s_a_ct" not in st.session_state:
    sync_widgets_with_state(st.session_state.state)


# =====================================================
# SIDEBAR - État initial de la période
# =====================================================
with st.sidebar:
    st.header("� Sauvegarde / Chargement")
    
    # Save/Load logic
    col_save, col_load = st.columns(2)
    
    with col_save:
        # Pousser le dictionnaire de session_state actuel vers JSON
        # On convertit en dict d'abord pour passer à la fonction
        json_state = serialize_simulation_state(dict(st.session_state))
        st.download_button(
            label="💾 Sauvegarder",
            data=json_state,
            file_name="mirage_session.json",
            mime="application/json",
            help="Télécharger le fichier de sauvegarde de votre session actuelle"
        )
        
    # Charger
    uploaded_session = st.file_uploader("Charger une session (.json)", type=["json"], label_visibility="collapsed")
    
    if uploaded_session is not None:
        try:
            content = uploaded_session.read().decode("utf-8")
            loaded_state = deserialize_simulation_state(content)
            
            if loaded_state:
                # Update session state with loaded values
                for k, v in loaded_state.items():
                    st.session_state[k] = v
                
                st.success("✅ Session chargée avec succès!")
                # On rerun pour rafraîchir les widgets avec les nouvelles valeurs
                if st.button("🔄 Appliquer le chargement", type="primary"):
                    st.rerun()
            else:
                st.warning("Le fichier semble vide ou invalide.")
        except Exception as e:
            st.error(f"Erreur lors du chargement: {e}")

    st.markdown("---")
    st.header("�📊 État Initial")

    # Import options
    st.subheader("📁 Importer des données")

    # File uploader for markdown
    uploaded_file = st.file_uploader(
        "Charger un fichier Markdown",
        type=["md"],
        help="Fichier au format 'Simulation Md des données year -X.md'"
    )

    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode("utf-8")
            parsed = parse_mirage_markdown(content)
            new_state = extract_period_state(parsed)
            st.session_state.state = new_state
            sync_widgets_with_state(new_state)
            st.success(f"✅ Fichier '{uploaded_file.name}' importé!")
        except Exception as e:
            st.error(f"Erreur lors de l'import: {e}")

    # Load from existing files in workspace
    workspace_path = Path(__file__).parent.parent
    md_files = list(workspace_path.glob("Simulation*.md"))

    if md_files:
        st.markdown("**Ou charger depuis le workspace:**")
        file_options = ["-- Sélectionner --"] + [f.name for f in md_files]
        selected_file = st.selectbox("Fichier existant", file_options)

        if selected_file != "-- Sélectionner --":
            if st.button("📥 Charger ce fichier"):
                file_path = workspace_path / selected_file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    parsed = parse_mirage_markdown(content)
                    new_state = extract_period_state(parsed)
                    st.session_state.state = new_state
                    sync_widgets_with_state(new_state)
                    st.success(f"✅ Données de '{selected_file}' chargées!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")

    st.markdown("---")

    # Reset button
    col_reset1, col_reset2 = st.columns(2)
    with col_reset1:
        if st.button("🔄 Tout à zéro", use_container_width=True):
            empty_state = get_empty_state()
            st.session_state.state = empty_state
            sync_widgets_with_state(empty_state)
            st.success("Valeurs remises à zéro!")
            st.rerun()
    with col_reset2:
        if st.button("📊 Valeurs P.-2", use_container_width=True):
            # Reload year -2 defaults
            p2_state = PeriodState(
                stock_a_ct=609_212,
                stock_a_gs=0,
                stock_b_ct=0,
                stock_b_gs=355_257,
                stock_c_ct=0,
                stock_c_gs=0,
                stock_mp_n=2_889_090,
                stock_mp_s=687_500,
                nb_ouvriers=580,
                nb_machines_m1=18,
                nb_machines_m2=0,
                cash=414.0,
                dette_lt=5_600.0,
                dette_ct=0.0,
                indice_prix=107.12,
                indice_salaire=103.0,
            )
            st.session_state.state = p2_state
            sync_widgets_with_state(p2_state)
            st.success("Valeurs P.-2 chargées!")
            st.rerun()

    st.markdown("---")

    st.subheader("✏️ Stocks Produits Finis (U)")
    col1, col2 = st.columns(2)
    with col1:
        stock_a_ct = st.number_input("Stock A-CT", min_value=0, step=1000, key="s_a_ct")
        stock_b_ct = st.number_input("Stock B-CT", min_value=0, step=1000, key="s_b_ct")
        stock_c_ct = st.number_input("Stock C-CT", min_value=0, step=1000, key="s_c_ct")
    with col2:
        stock_a_gs = st.number_input("Stock A-GS", min_value=0, step=1000, key="s_a_gs")
        stock_b_gs = st.number_input("Stock B-GS", min_value=0, step=1000, key="s_b_gs")
        stock_c_gs = st.number_input("Stock C-GS", min_value=0, step=1000, key="s_c_gs")

    st.subheader("📦 Stocks MP (unités)")
    stock_mp_n = st.number_input("Stock MP N", min_value=0, step=10000, key="s_mp_n")
    stock_mp_s = st.number_input("Stock MP S", min_value=0, step=10000, key="s_mp_s")

    st.subheader("👷 Effectifs & Équipements")
    nb_ouvriers = st.number_input("Nb Ouvriers", min_value=0, step=10, key="s_ouvriers")
    nb_machines_m1 = st.number_input("Nb Machines M1", min_value=0, step=1, key="s_m1")
    nb_machines_m2 = st.number_input("Nb Machines M2", min_value=0, step=1, key="s_m2")

    st.subheader("💰 Trésorerie & Dettes (K€)")
    cash = st.number_input("Trésorerie", step=100.0, key="s_cash")
    dette_lt = st.number_input("Dette LT", min_value=0.0, step=100.0, key="s_dlt")
    dette_ct = st.number_input("Dette CT", min_value=0.0, step=100.0, key="s_dct")

    st.subheader("📈 Indices")
    indice_prix = st.number_input("Indice Prix", step=0.1, key="s_ip")
    indice_salaire = st.number_input("Indice Salaire", step=0.1, key="s_is")

    st.markdown("---")
    
    with st.expander("📝 Notes Personnelles"):
        st.text_area(
            "Vos notes (sauvegardées avec la session)",
            value=st.session_state.get("user_notes", ""),
            height=200,
            key="user_notes",
            placeholder="Écrivez vos remarques, stratégies ou calculs ici..."
        )

# Create current state from sidebar inputs
state = PeriodState(
    stock_a_ct=stock_a_ct,
    stock_a_gs=stock_a_gs,
    stock_b_ct=stock_b_ct,
    stock_b_gs=stock_b_gs,
    stock_c_ct=stock_c_ct,
    stock_c_gs=stock_c_gs,
    stock_mp_n=stock_mp_n,
    stock_mp_s=stock_mp_s,
    nb_ouvriers=nb_ouvriers,
    nb_machines_m1=nb_machines_m1,
    nb_machines_m2=nb_machines_m2,
    cash=cash,
    dette_lt=dette_lt,
    dette_ct=dette_ct,
    indice_prix=indice_prix,
    indice_salaire=indice_salaire,
)


# =====================================================
# MAIN AREA - Décisions
# =====================================================

# Tabs pour organiser les décisions
tabs = st.tabs([
    "🏷️ Produits",
    "📢 Marketing",
    "📦 Approvisionnements",
    "🔧 Production",
    "🌱 RSE",
    "💰 Finances",
    "📈 Résultats"
])

# =====================================================
# TAB 1: PRODUITS
# =====================================================
with tabs[0]:
    st.header("Décisions Produits")

    # Button to reset all products to zero
    if st.button("🔄 Remettre tous les produits à zéro"):
        st.session_state.reset_products = True
        st.rerun()

    reset_products = st.session_state.get("reset_products", False)
    if reset_products:
        st.session_state.reset_products = False

    # Produit A
    st.subheader("Produit A")
    col_a1, col_a2 = st.columns(2)

    with col_a1:
        st.markdown("**Canal CT (Commerce Traditionnel)**")
        a_ct_prix = st.number_input("011-A CT Prix Tarif (€/U)", min_value=0.0, value=0.0 if reset_products else 20.60, step=0.10, key="a_ct_prix")
        a_ct_promo = st.number_input("012- Promotion (€/U)", min_value=0.0, value=0.0 if reset_products else 0.30, step=0.05, key="a_ct_promo")
        a_ct_prod = st.number_input("013- Production (KU)", min_value=0, value=0 if reset_products else 420, step=10, key="a_ct_prod")
        a_ct_qual = st.selectbox("014- Qualité Produite (%)", [100, 50], index=0, key="a_ct_qual")
        a_ct_emb = st.checkbox("015- Emballages Recyclés", value=False, key="a_ct_emb")

    with col_a2:
        st.markdown("**Canal GS (Grandes Surfaces)**")
        a_gs_prix = st.number_input("021-A GS Prix Tarif (€/U)", min_value=0.0, value=0.0, step=0.10, key="a_gs_prix")
        a_gs_rist = st.number_input("022- Ristourne (%)", min_value=0.0, max_value=20.0, value=0.0, step=0.5, key="a_gs_rist")
        a_gs_promo = st.number_input("023- Promotion (€/U)", min_value=0.0, value=0.0, step=0.05, key="a_gs_promo")
        a_gs_prod = st.number_input("024- Production (KU)", min_value=0, value=0, step=10, key="a_gs_prod")
        a_gs_qual = st.selectbox("025- Qualité Produite (%)", [100, 50, 0], index=2, key="a_gs_qual")
        a_gs_emb = st.checkbox("026- Emballages Recyclés", value=False, key="a_gs_emb")

    st.markdown("---")

    # Produit B
    st.subheader("Produit B")
    col_b1, col_b2 = st.columns(2)

    with col_b1:
        st.markdown("**Canal CT (Commerce Traditionnel)**")
        b_ct_prix = st.number_input("031-B CT Prix Tarif (€/U)", min_value=0.0, value=0.0, step=0.10, key="b_ct_prix")
        b_ct_promo = st.number_input("032- Promotion (€/U)", min_value=0.0, value=0.0, step=0.05, key="b_ct_promo")
        b_ct_prod = st.number_input("033- Production (KU)", min_value=0, value=0, step=10, key="b_ct_prod")
        b_ct_qual = st.selectbox("034- Qualité Produite (%)", [100, 50, 0], index=2, key="b_ct_qual")
        b_ct_emb = st.checkbox("035- Emballages Recyclés", value=False, key="b_ct_emb")

    with col_b2:
        st.markdown("**Canal GS (Grandes Surfaces)**")
        b_gs_prix = st.number_input("041-B GS Prix Tarif (€/U)", min_value=0.0, value=0.0 if reset_products else 22.40, step=0.10, key="b_gs_prix")
        b_gs_rist = st.number_input("042- Ristourne (%)", min_value=0.0, max_value=20.0, value=0.0 if reset_products else 7.0, step=0.5, key="b_gs_rist")
        b_gs_promo = st.number_input("043- Promotion (€/U)", min_value=0.0, value=0.0 if reset_products else 0.80, step=0.05, key="b_gs_promo")
        b_gs_prod = st.number_input("044- Production (KU)", min_value=0, value=0 if reset_products else 120, step=10, key="b_gs_prod")
        b_gs_qual = st.selectbox("045- Qualité Produite (%)", [100, 50], index=1, key="b_gs_qual")
        b_gs_emb = st.checkbox("046- Emballages Recyclés", value=False, key="b_gs_emb")

    st.markdown("---")

    # Produit C
    st.subheader("Produit C")
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("**Canal CT (Commerce Traditionnel)**")
        c_ct_prix = st.number_input("051-C CT Prix Tarif (€/U)", min_value=0.0, value=0.0, step=0.10, key="c_ct_prix")
        c_ct_promo = st.number_input("052- Promotion (€/U)", min_value=0.0, value=0.0, step=0.05, key="c_ct_promo")
        c_ct_prod = st.number_input("053- Production (KU)", min_value=0, value=0, step=10, key="c_ct_prod")
        c_ct_qual = st.selectbox("054- Qualité Produite (%)", [100, 50, 0], index=2, key="c_ct_qual")
        c_ct_emb = st.checkbox("055- Emballages Recyclés", value=False, key="c_ct_emb")

    with col_c2:
        st.markdown("**Canal GS (Grandes Surfaces)**")
        c_gs_prix = st.number_input("061-C GS Prix Tarif (€/U)", min_value=0.0, value=0.0, step=0.10, key="c_gs_prix")
        c_gs_rist = st.number_input("062- Ristourne (%)", min_value=0.0, max_value=20.0, value=0.0, step=0.5, key="c_gs_rist")
        c_gs_promo = st.number_input("063- Promotion (€/U)", min_value=0.0, value=0.0, step=0.05, key="c_gs_promo")
        c_gs_prod = st.number_input("064- Production (KU)", min_value=0, value=0, step=10, key="c_gs_prod")
        c_gs_qual = st.selectbox("065- Qualité Produite (%)", [100, 50, 0], index=2, key="c_gs_qual")
        c_gs_emb = st.checkbox("066- Emballages Recyclés", value=False, key="c_gs_emb")


# =====================================================
# TAB 2: MARKETING
# =====================================================
with tabs[1]:
    st.header("Décisions Marketing")

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.subheader("Commerce Traditionnel (CT)")
        mkt_vendeurs_ct = st.number_input("071- Nombre Vendeurs CT", min_value=0, value=35, step=1)
        mkt_commission = st.number_input("072- Commission (% du CA)", min_value=0.0, max_value=5.0, value=0.5, step=0.1)
        mkt_pub_ct = st.number_input("078- Publicité CT (K€)", min_value=0.0, value=400.0, step=50.0)

    with col_m2:
        st.subheader("Grandes Surfaces (GS)")
        mkt_vendeurs_gs = st.number_input("075- Nombre Vendeurs GS", min_value=0, value=12, step=1)
        mkt_prime_gs = st.number_input("076- Prime Trimest. (€/Vendeur)", min_value=0.0, value=600.0, step=50.0)
        mkt_pub_gs = st.number_input("079- Publicité GS (K€)", min_value=0.0, value=0.0, step=50.0)

    st.subheader("Études de Marché")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        mkt_etudes_abcd = st.text_input("073- Études (A..D) ou N", value="ABC").upper()
    with col_e2:
        mkt_etudes_efgh = st.text_input("074- Études (E..H) ou N", value="N").upper()

    # Afficher coût des études
    cout_etudes = calculate_study_costs(mkt_etudes_abcd, mkt_etudes_efgh)
    st.info(f"💡 Coût des études: **{cout_etudes:.0f} K€**")


# =====================================================
# TAB 3: APPROVISIONNEMENTS
# =====================================================
with tabs[2]:
    st.header("Décisions Approvisionnements")

    col_ap1, col_ap2 = st.columns(2)

    with col_ap1:
        st.subheader("Matières Premières N (Qualité 100%)")
        app_mp_n = st.number_input("080- Commandes MP N (KU/per)", min_value=0, value=0, step=500)
        app_duree_n = st.number_input("081- Durée contrat N (1-4)", min_value=0, max_value=4, value=0, step=1)

    with col_ap2:
        st.subheader("Matières Premières S (Qualité 50%)")
        app_mp_s = st.number_input("082- Commandes MP S (KU/per)", min_value=0, value=0, step=500)
        app_duree_s = st.number_input("083- Durée contrat S (1-4)", min_value=0, max_value=4, value=0, step=1)

    st.markdown("---")
    app_maintenance = st.checkbox("086- Maintenance (O/N)", value=True)

    # Afficher prix MP
    st.subheader("📋 Grille de Prix MP (référence)")
    st.markdown("*Prix HT applicables selon quantité et durée de contrat*")

    col_prix1, col_prix2 = st.columns(2)
    with col_prix1:
        st.markdown("**MP N**")
        prix_n_df = pd.DataFrame({
            "Durée": ["1 per", "2 per", "3 per", "4 per"],
            "<1000": [1.235, 1.204, 1.173, 1.143],
            "1000-1500": [1.204, 1.173, 1.143, 1.112],
            "1500-2000": [1.173, 1.143, 1.112, 1.081],
            "2000-2500": [1.143, 1.112, 1.081, 1.050],
            "2500-3000": [1.112, 1.081, 1.050, 1.019],
            ">3000": [1.081, 1.050, 1.019, 0.988],
        })
        st.dataframe(prix_n_df, hide_index=True)

    with col_prix2:
        st.markdown("**MP S**")
        prix_s_df = pd.DataFrame({
            "Durée": ["1 per", "2 per", "3 per", "4 per"],
            "<1000": [0.874, 0.852, 0.830, 0.808],
            "1000-1500": [0.852, 0.830, 0.808, 0.786],
            "1500-2000": [0.830, 0.808, 0.786, 0.764],
            "2000-2500": [0.808, 0.786, 0.764, 0.743],
            "2500-3000": [0.786, 0.764, 0.743, 0.721],
            ">3000": [0.764, 0.743, 0.721, 0.699],
        })
        st.dataframe(prix_s_df, hide_index=True)


# =====================================================
# TAB 4: PRODUCTION
# =====================================================
with tabs[3]:
    st.header("Décisions Production")

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.subheader("Machines")
        prod_m1_actives = st.number_input(
            "089- Machines M1 Actives",
            min_value=0,
            max_value=nb_machines_m1 + 10,  # Allow buying new ones
            value=min(17, nb_machines_m1),
            step=1
        )
        prod_m2_actives = st.number_input(
            "090- Machines M2 Actives",
            min_value=0,
            max_value=nb_machines_m2 + 10,
            value=0,
            step=1
        )

        st.markdown("---")
        st.subheader("Achats/Ventes Machines")
        prod_ventes_m1 = st.number_input("091- Ventes Machines M1", min_value=0, value=0, step=1)
        prod_achats_m1 = st.number_input("092- Achats Machines M1", min_value=0, value=0, step=1)
        prod_achats_m2 = st.number_input("093- Achats Machines M2", min_value=0, value=0, step=1)

    with col_p2:
        st.subheader("Personnel")
        prod_emb_deb = st.number_input("094- Emb/Deb. Ouvriers", value=0, step=10)
        prod_var_pa = st.number_input("095- Variat. Pouvoir Achat (%)", value=2.0, step=0.5)

        st.markdown("---")
        # Calculs capacité
        capacite_m1 = prod_m1_actives * C.M1_CAPACITY_A
        capacite_m2 = prod_m2_actives * C.M2_CAPACITY_A
        capacite_totale = capacite_m1 + capacite_m2

        ouvriers_apres = nb_ouvriers + prod_emb_deb
        ouvriers_necessaires = prod_m1_actives * C.WORKERS_PER_M1 + prod_m2_actives * C.WORKERS_PER_M2

        st.subheader("📊 Capacités Calculées")
        st.metric("Capacité M1 (unités A)", f"{capacite_m1:,.0f}")
        st.metric("Capacité M2 (unités A)", f"{capacite_m2:,.0f}")
        st.metric("Capacité Totale", f"{capacite_totale:,.0f}")

        st.markdown("---")
        st.subheader("👷 Ouvriers")
        st.metric("Ouvriers après décision", ouvriers_apres)
        st.metric("Ouvriers nécessaires", ouvriers_necessaires)
        if ouvriers_apres < ouvriers_necessaires:
            st.error(f"⚠️ Manque {ouvriers_necessaires - ouvriers_apres} ouvriers!")


# =====================================================
# TAB 5: RSE
# =====================================================
with tabs[4]:
    st.header("Décisions RSE")

    col_r1, col_r2, col_r3 = st.columns(3)

    with col_r1:
        rse_recyclage = st.number_input("087- Budget Recyclage (K€)", min_value=0.0, value=0.0, step=50.0)
    with col_r2:
        rse_amenagements = st.number_input("088- Aménagements adaptés (K€)", min_value=0.0, value=0.0, step=50.0)
    with col_r3:
        rse_rd = st.number_input("096- Recherche et Dévelop. (K€)", min_value=0.0, value=0.0, step=50.0)

    st.info("💡 Ces investissements améliorent votre indicateur RSE et peuvent débloquer le label Mir'EcoCert.")


# =====================================================
# TAB 6: FINANCES
# =====================================================
with tabs[5]:
    st.header("Décisions Financières")

    col_f1, col_f2 = st.columns(2)

    with col_f1:
        st.subheader("Emprunts")
        fin_emprunt_lt = st.number_input("097- Emprunt Long Terme (K€)", min_value=0.0, value=0.0, step=100.0)
        fin_duree_lt = st.number_input("098- Nb de Trimestres (2-8)", min_value=0, max_value=8, value=0, step=1)
        fin_emprunt_ct = st.number_input("102- Emprunt Court Terme (K€)", min_value=0.0, value=0.0, step=100.0)
        fin_effets = st.number_input("103- Effets escomptés (K€)", min_value=0.0, value=0.0, step=100.0)
        fin_rembt = st.checkbox("106- Rembt. dernier emprunt", value=False)

    with col_f2:
        st.subheader("Autres")
        fin_effort_social = st.number_input("101- Effort Social (%)", min_value=0.0, max_value=10.0, value=0.0, step=0.5)
        fin_escompte = st.number_input("104- Escompte Paiement Cpt (%)", min_value=0.0, max_value=10.0, value=7.5, step=0.5)
        fin_dividendes = st.number_input("105- Dividendes (K€)", min_value=0.0, value=200.0, step=50.0)

        st.markdown("---")
        st.subheader("Augmentation de Capital")
        fin_actions_new = st.number_input("107- Nb actions nouvelles (KU)", min_value=0, value=0, step=10)
        fin_prix_emission = st.number_input("108- Prix d'emission (€)", min_value=0.0, value=0.0, step=1.0)

    st.markdown("---")
    st.subheader("Achats/Ventes de Titres")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        titres_f1 = st.number_input("131- Actions F1", value=0, step=100)
        titres_f2 = st.number_input("132- Actions F2", value=0, step=100)
    with col_t2:
        titres_f3 = st.number_input("133- Actions F3", value=0, step=100)
        titres_f4 = st.number_input("134- Actions F4", value=0, step=100)
    with col_t3:
        titres_f5 = st.number_input("135- Actions F5", value=0, step=100)
        titres_f6 = st.number_input("136- Actions F6", value=0, step=100)


# =====================================================
# TAB 7: RÉSULTATS CALCULÉS
# =====================================================
with tabs[6]:
    st.header("📊 Résultats Calculés")

    # Construire les décisions
    decisions = AllDecisions(
        produit_a_ct=ProductDecision(
            prix_tarif=a_ct_prix, promotion=a_ct_promo, production=a_ct_prod,
            qualite=a_ct_qual, emballage_recycle=a_ct_emb
        ),
        produit_a_gs=ProductDecision(
            prix_tarif=a_gs_prix, ristourne=a_gs_rist, promotion=a_gs_promo,
            production=a_gs_prod, qualite=a_gs_qual if a_gs_qual > 0 else 100, emballage_recycle=a_gs_emb
        ),
        produit_b_ct=ProductDecision(
            prix_tarif=b_ct_prix, promotion=b_ct_promo, production=b_ct_prod,
            qualite=b_ct_qual if b_ct_qual > 0 else 100, emballage_recycle=b_ct_emb
        ),
        produit_b_gs=ProductDecision(
            prix_tarif=b_gs_prix, ristourne=b_gs_rist, promotion=b_gs_promo,
            production=b_gs_prod, qualite=b_gs_qual, emballage_recycle=b_gs_emb
        ),
        produit_c_ct=ProductDecision(
            prix_tarif=c_ct_prix, promotion=c_ct_promo, production=c_ct_prod,
            qualite=c_ct_qual if c_ct_qual > 0 else 100, emballage_recycle=c_ct_emb
        ),
        produit_c_gs=ProductDecision(
            prix_tarif=c_gs_prix, ristourne=c_gs_rist, promotion=c_gs_promo,
            production=c_gs_prod, qualite=c_gs_qual if c_gs_qual > 0 else 100, emballage_recycle=c_gs_emb
        ),
        marketing=MarketingDecision(
            vendeurs_ct=mkt_vendeurs_ct, commission_ct=mkt_commission,
            vendeurs_gs=mkt_vendeurs_gs, prime_trimestre_gs=mkt_prime_gs,
            publicite_ct=mkt_pub_ct, publicite_gs=mkt_pub_gs,
            etudes_abcd=mkt_etudes_abcd, etudes_efgh=mkt_etudes_efgh
        ),
        approvisionnement=ApprovisionnementDecision(
            commandes_mp_n=app_mp_n, duree_contrat_n=app_duree_n,
            commandes_mp_s=app_mp_s, duree_contrat_s=app_duree_s,
            maintenance=app_maintenance
        ),
        production=ProductionDecision(
            machines_m1_actives=prod_m1_actives, machines_m2_actives=prod_m2_actives,
            ventes_m1=prod_ventes_m1, achats_m1=prod_achats_m1, achats_m2=prod_achats_m2,
            emb_deb_ouvriers=prod_emb_deb, variation_pouvoir_achat=prod_var_pa
        ),
        rse=RSEDecision(
            budget_recyclage=rse_recyclage, amenagements_adaptes=rse_amenagements,
            recherche_dev=rse_rd
        ),
        finance=FinanceDecision(
            emprunt_lt=fin_emprunt_lt, duree_emprunt_lt=fin_duree_lt,
            effort_social=fin_effort_social, emprunt_ct=fin_emprunt_ct,
            effets_escomptes=fin_effets, escompte_paiement_cpt=fin_escompte,
            dividendes=fin_dividendes, rembt_dernier_emprunt=fin_rembt,
            nb_actions_nouvelles=fin_actions_new, prix_emission=fin_prix_emission
        ),
        titres=TitresDecision(
            actions_f1=titres_f1, actions_f2=titres_f2, actions_f3=titres_f3,
            actions_f4=titres_f4, actions_f5=titres_f5, actions_f6=titres_f6
        )
    )

    # Calculer les résultats
    results = calculate_all(decisions, state)

    # Afficher les warnings en premier
    if results.warnings:
        st.error("### ⚠️ Alertes")
        for warning in results.warnings:
            st.warning(warning)

    # Résultats en colonnes
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🏭 Production")
        st.metric("Capacité Totale (unités A)", f"{results.capacite_totale_a:,.0f}")

        production_totale = (
            (a_ct_prod + a_gs_prod + b_ct_prod + b_gs_prod + c_ct_prod + c_gs_prod) * 1000
        )
        st.metric("Production Demandée", f"{production_totale:,.0f}")

        st.markdown("---")
        st.markdown("**Matières Premières**")
        st.metric("MP N nécessaire", f"{results.mp_n_necessaire:,.0f}")
        st.metric("MP S nécessaire", f"{results.mp_s_necessaire:,.0f}")
        st.metric("MP N après production", f"{results.mp_n_apres_prod:,.0f}",
                  delta=f"{results.mp_n_apres_prod - state.stock_mp_n:,.0f}")
        st.metric("MP S après production", f"{results.mp_s_apres_prod:,.0f}",
                  delta=f"{results.mp_s_apres_prod - state.stock_mp_s:,.0f}")

    with col2:
        st.subheader("💶 Coûts Estimés (K€)")
        st.metric("Coût MP", f"{results.cout_mp:,.0f}")
        st.metric("Coût Main d'œuvre", f"{results.cout_main_oeuvre:,.0f}")
        st.metric("Amortissement", f"{results.cout_amortissement:,.0f}")
        st.metric("Maintenance", f"{results.cout_maintenance:,.0f}")
        st.metric("**Coût Production Total**", f"{results.cout_production_total:,.0f}")

        st.markdown("---")
        st.metric("Coût Promotion", f"{results.cout_promotion:,.0f}")
        st.metric("Coût Vendeurs", f"{results.cout_vendeurs:,.0f}")
        st.metric("Coût Publicité", f"{results.cout_publicite:,.0f}")
        st.metric("Coût Études", f"{results.cout_etudes:,.0f}")
        st.metric("**Coût Commercial Total**", f"{results.cout_commercial_total:,.0f}")

    with col3:
        st.subheader("💰 Revenus & Trésorerie (K€)")

        st.markdown("**Prix Nets**")
        if a_ct_prix > 0:
            st.write(f"A-CT: {results.prix_net_a_ct:.2f} €")
        if a_gs_prix > 0:
            st.write(f"A-GS: {results.prix_net_a_gs:.2f} €")
        if b_ct_prix > 0:
            st.write(f"B-CT: {results.prix_net_b_ct:.2f} €")
        if b_gs_prix > 0:
            st.write(f"B-GS: {results.prix_net_b_gs:.2f} €")
        if c_ct_prix > 0:
            st.write(f"C-CT: {results.prix_net_c_ct:.2f} €")
        if c_gs_prix > 0:
            st.write(f"C-GS: {results.prix_net_c_gs:.2f} €")

        st.markdown("---")
        st.metric("CA Potentiel Total", f"{results.ca_potentiel_total:,.0f}")

        st.markdown("---")
        st.subheader("📊 Cash Flow Estimé")
        st.metric("Décaissements estimés", f"{results.decaissements_total:,.0f}")
        st.metric("Encaissements estimés", f"{results.encaissements_total:,.0f}")
        st.metric(
            "Trésorerie estimée fin période",
            f"{results.tresorerie_estimee:,.0f}",
            delta=f"{results.tresorerie_estimee - state.cash:,.0f}"
        )

    # Tableau récapitulatif des stocks
    st.markdown("---")
    st.subheader("📦 Stocks Disponibles à la Vente")

    stocks_df = pd.DataFrame({
        "Produit": ["A-CT", "A-GS", "B-CT", "B-GS", "C-CT", "C-GS"],
        "Stock Initial": [state.stock_a_ct, state.stock_a_gs, state.stock_b_ct,
                          state.stock_b_gs, state.stock_c_ct, state.stock_c_gs],
        "Production": [a_ct_prod * 1000, a_gs_prod * 1000, b_ct_prod * 1000,
                       b_gs_prod * 1000, c_ct_prod * 1000, c_gs_prod * 1000],
        "Stock Dispo": [results.stock_dispo_a_ct, results.stock_dispo_a_gs,
                        results.stock_dispo_b_ct, results.stock_dispo_b_gs,
                        results.stock_dispo_c_ct, results.stock_dispo_c_gs],
        "Prix Net (€)": [results.prix_net_a_ct, results.prix_net_a_gs,
                         results.prix_net_b_ct, results.prix_net_b_gs,
                         results.prix_net_c_ct, results.prix_net_c_gs],
        "CA Potentiel (K€)": [results.ca_potentiel_a_ct, results.ca_potentiel_a_gs,
                              results.ca_potentiel_b_ct, results.ca_potentiel_b_gs,
                              results.ca_potentiel_c_ct, results.ca_potentiel_c_gs],
    })

    # Filtrer les lignes avec production ou stock
    stocks_df_filtered = stocks_df[
        (stocks_df["Stock Initial"] > 0) |
        (stocks_df["Production"] > 0)
    ]

    if not stocks_df_filtered.empty:
        st.dataframe(
            stocks_df_filtered.style.format({
                "Stock Initial": "{:,.0f}",
                "Production": "{:,.0f}",
                "Stock Dispo": "{:,.0f}",
                "Prix Net (€)": "{:.2f}",
                "CA Potentiel (K€)": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Aucune production ni stock disponible.")

    # Prévisions à remplir
    st.markdown("---")
    st.subheader("📝 Prévisions (à renseigner)")

    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        prev_ca = st.number_input("121- Prévision CA HT (K€)", min_value=0.0, value=0.0, step=100.0)
        prev_resultat = st.number_input("122- Prévision Résultat (K€)", value=0.0, step=50.0)
    with col_prev2:
        prev_encaiss = st.number_input("123- Prévision Encaissem. (K€)", min_value=0.0, value=0.0, step=100.0)
        prev_decaiss = st.number_input("124- Prévision Décaissem. (K€)", min_value=0.0, value=0.0, step=100.0)

    st.info(f"""
    💡 **Suggestions basées sur les calculs:**
    - CA estimé: ~{results.ca_potentiel_total * 0.7:,.0f} K€ (si 70% vendu)
    - Encaissements estimés: ~{results.encaissements_total:,.0f} K€
    - Décaissements estimés: ~{results.decaissements_total:,.0f} K€
    """)


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    🏭 Mirage Simulation - Aide à la Décision | v0.1.0
    </div>
    """,
    unsafe_allow_html=True
)

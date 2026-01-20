"""Streamlit application for Mirage simulation decision support."""

import sys
from pathlib import Path
import importlib

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Force reload of backend modules to pick up changes
if "src.mirage.constants" in sys.modules:
    import src.mirage.constants
    importlib.reload(src.mirage.constants)
if "src.mirage.models" in sys.modules:
    import src.mirage.models
    importlib.reload(src.mirage.models)
if "src.mirage.calculator" in sys.modules:
    import src.mirage.calculator
    importlib.reload(src.mirage.calculator)

import streamlit as st
import pandas as pd
import json # Added for save/load features

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

# --- SAVE / LOAD HELPERS ---
SAVE_FILE = "data/saved_defaults.json"

def save_state_to_file():
    """Sauvegarde l'état actuel (session_state) dans un fichier JSON."""
    serializable_state = {}
    # Keys to exclude from saving (especially buttons which cause errors if reloaded)
    EXCLUDED_KEYS = ["state", "reset_btn", "auto_app_n", "auto_app_s"]

    # On sauvegarde toutes les clés simples (int, float, str, bool, list)
    # On exclut les objets complexes comme PeriodState qui sera reconstruit via les widgets
    for k, v in st.session_state.items():
        if k in EXCLUDED_KEYS: continue 
        if isinstance(v, (int, float, str, bool, list, dict, type(None))):
            serializable_state[k] = v
            
    try:
        Path("data").mkdir(exist_ok=True)
        with open(SAVE_FILE, "w") as f:
            json.dump(serializable_state, f, indent=2)
        st.toast("✅ Valeurs sauvegardées comme défaut !", icon="💾")
    except Exception as e:
        st.error(f"Erreur sauvegarde: {e}")

def load_state_from_file():
    """Charge l'état depuis le fichier JSON."""
    if not Path(SAVE_FILE).exists():
        st.toast("⚠️ Aucune sauvegarde trouvée.", icon="📂")
        return
    
    try:
        with open(SAVE_FILE, "r") as f:
            loaded_state = json.load(f)
        
        # Mise à jour du session_state
        for k, v in loaded_state.items():
            if k == "reset_btn": continue # Safety check
            st.session_state[k] = v
            
        # On force le rechargement pour que les widgets prennent les nouvelles valeurs
        st.toast("✅ Valeurs chargées !", icon="📂")
        st.rerun()
    except Exception as e:
        st.error(f"Erreur chargement: {e}")

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

# Sidebar: Documentation des règles
with st.sidebar:
    with st.expander("ℹ️ Règles de Gestion Actives"):
        st.markdown("""
        **1. Contrats & Stock**
        - Priorité absolue aux contrats sur le stock disponible.
        - **Pénalité de Rupture :** Si `(Stock + Prod) < Demande Contrat`, pénalité de 50% du prix le plus élevé.
        
        **2. RH & Production**
        - **Saisonniers :** Embauche auto si `Besoin > Dispo`. Coût : **150%** du salaire.
        - **Chômage Technique :** Mise au chômage auto si `Besoin < Dispo`. Coût : **50%** du salaire.
        
        **3. Maintenance Machines**
        - Si case *Maintenance* décochée :
            - Économie du coût de maintenance.
            - **MALUS : -5%** de capacité de production sur toutes les machines.
        
        **4. Finance**
        - **Dividendes :** Plafonnés à `10% * (Réserves + Résultat N-1)`. Le surplus est ignoré.
        """)

st.title("🏭 Mirage - Simulateur de Décisions")
st.markdown("---")

# Initialize session state
if "state" not in st.session_state:
    # First check if we have custom defaults saved
    if Path(SAVE_FILE).exists() and st.query_params.get("reset") != "true":
         try:
            with open(SAVE_FILE, "r") as f:
                loaded_state = json.load(f)
            for k, v in loaded_state.items():
                if k == "reset_btn": continue
                st.session_state[k] = v
         except:
             pass

    if "state" not in st.session_state: # If still not present (or we just loaded params but not the complex object)
        st.session_state.state = PeriodState(
            stock_a_ct=609_212,
            stock_a_gs=0,
            stock_b_ct=0,
            stock_b_gs=355_257,
            stock_c_ct=0,
            stock_c_gs=0,
            stock_mp_n=2_889_090,
            stock_mp_s=687_500,
            nb_ouvriers=560,
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
                EXCLUDED_LOAD_KEYS = {"reset_btn", "auto_app_n", "auto_app_s"}
                for k, v in loaded_state.items():
                    if k in EXCLUDED_LOAD_KEYS: continue
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

    # Save / Load Defaults
    col_save1, col_save2 = st.columns(2)
    with col_save1:
        if st.button("💾 Sauver Défaut", use_container_width=True, help="Sauvegarder les valeurs actuelles comme personnalisées"):
            save_state_to_file()
    with col_save2:
        if st.button("📂 Charger Défaut", use_container_width=True, help="Charger les valeurs personnalisées sauvegardées"):
            load_state_from_file()

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
# Note: period_selector needs to be retrieved from session state or default if not yet rendered
# But since we defined it above inside tab block (bad practice), it might be out of scope.
# ACTUALLY, to fix the scope issue properly, we should move the period selector BEFORE state creation.
# Or use session_state access.
current_period = st.session_state.get("period_selector_val", 1)

state = PeriodState(
    period_num=current_period,
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

# Helper for table layout
def decision_row(label, widget_type="number", **kwargs):
    """Renders a decision row with label and input."""
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"**{label}**")
    with col2:
        # Use label_visibility="collapsed" to hide the widget's internal label
        if widget_type == "number":
            return st.number_input(label, label_visibility="collapsed", **kwargs)
        elif widget_type == "select":
            return st.selectbox(label, label_visibility="collapsed", **kwargs)
        elif widget_type == "checkbox":
            return st.checkbox("", **kwargs) # Checkbox label is weird when collapsed, using empty string
        elif widget_type == "text":
            return st.text_input(label, label_visibility="collapsed", **kwargs)

# Tabs: Inputs vs Results
tabs = st.tabs(["📝 Saisie des Décisions", "📊 Résultats & Analyse"])

# =====================================================
# TAB 1: SAISIE DES DÉCISIONS (Table Unique)
# =====================================================
with tabs[0]:
    # Create info expander in sidebar
    # We use a unique key to store it in session state
    with st.sidebar:
        st.header("⚙️ Paramètres Période")
        st.selectbox("Période Simulée", options=[1, 2, 3, 4], index=0, help="Détermine le taux de congés payés (3.5%, 4%, 21%...)", key="period_selector_val")
        
    st.header("Tableau de Bord des Décisions")
    
    # Button to reset all products to zero
    if st.button("🔄 Remettre tous les produits à zéro", key="reset_btn"):
        st.session_state.reset_products = True
        st.rerun()

    reset_products = st.session_state.get("reset_products", False)
    if reset_products:
        st.session_state.reset_products = False

    # Header de la "Table"
    st.markdown("---")
    h1, h2 = st.columns([3, 2])
    h1.markdown("#### Libellé des Décisions")
    h2.markdown("#### Décision P. 1")
    st.markdown("---")

    # --- PRODUIT A ---
    st.subheader("PRODUIT A")
    # A-CT
    a_ct_prix = decision_row("011-A CT Prix Tarif (€/U)", "number", min_value=0.0, value=0.0 if reset_products else 20.60, step=0.10, key="a_ct_prix")
    a_ct_promo = decision_row("012- Promotion (€/U)", "number", min_value=0.0, value=0.0 if reset_products else 0.30, step=0.05, key="a_ct_promo")
    a_ct_prod = decision_row("013- Production (KU)", "number", min_value=0, value=0 if reset_products else 420, step=10, key="a_ct_prod")
    a_ct_qual = decision_row("014- Qualité Produite (%)", "number", min_value=0, max_value=100, value=100, step=5, key="a_ct_qual")
    a_ct_emb = decision_row("015- Emballages Recyclés (O/N)", "checkbox", value=False, key="a_ct_emb")
    with st.expander("Contrats A-CT"):
        a_ct_v_contrat = decision_row("Ventes Contrat (U)", "number", min_value=0, value=0, step=100, key="a_ct_vc")
        a_ct_a_contrat = decision_row("Achats Contrat (U)", "number", min_value=0, value=0, step=100, key="a_ct_ac")
    
    # A-GS
    st.markdown("**Produit A - Grande Surface**")
    a_gs_prix = decision_row("021-A GS Prix Tarif (€/U)", "number", min_value=0.0, value=0.0, step=0.10, key="a_gs_prix")
    a_gs_rist = decision_row("022- Ristourne (%)", "number", min_value=0.0, max_value=20.0, value=0.0, step=0.5, key="a_gs_rist")
    a_gs_promo = decision_row("023- Promotion (€/U)", "number", min_value=0.0, value=0.0, step=0.05, key="a_gs_promo")
    a_gs_prod = decision_row("024- Production (KU)", "number", min_value=0, value=0, step=10, key="a_gs_prod")
    a_gs_qual = decision_row("025- Qualité Produite (%)", "number", min_value=0, max_value=100, value=0, step=5, key="a_gs_qual")
    a_gs_emb = decision_row("026- Emballages Recyclés (O/N)", "checkbox", value=False, key="a_gs_emb")
    with st.expander("Contrats A-GS"):
        a_gs_v_contrat = decision_row("Ventes Contrat (U)", "number", min_value=0, value=0, step=100, key="a_gs_vc")
        a_gs_a_contrat = decision_row("Achats Contrat (U)", "number", min_value=0, value=0, step=100, key="a_gs_ac")
    
    net_a_container = st.empty()
    
    st.markdown("---")

    # --- PRODUIT B ---
    st.subheader("PRODUIT B")
    # B-CT
    b_ct_prix = decision_row("031-B CT Prix Tarif (€/U)", "number", min_value=0.0, value=0.0, step=0.10, key="b_ct_prix")
    b_ct_promo = decision_row("032- Promotion (€/U)", "number", min_value=0.0, value=0.0, step=0.05, key="b_ct_promo")
    b_ct_prod = decision_row("033- Production (KU)", "number", min_value=0, value=0, step=10, key="b_ct_prod")
    b_ct_qual = decision_row("034- Qualité Produite (%)", "number", min_value=0, max_value=100, value=0, step=5, key="b_ct_qual")
    b_ct_emb = decision_row("035- Emballages Recyclés (O/N)", "checkbox", value=False, key="b_ct_emb")
    with st.expander("Contrats B-CT"):
        b_ct_v_contrat = decision_row("Ventes Contrat (U)", "number", min_value=0, value=0, step=100, key="b_ct_vc")
        b_ct_a_contrat = decision_row("Achats Contrat (U)", "number", min_value=0, value=0, step=100, key="b_ct_ac")

    # B-GS
    st.markdown("**Produit B - Grande Surface**")
    b_gs_prix = decision_row("041-B GS Prix Tarif (€/U)", "number", min_value=0.0, value=0.0 if reset_products else 22.40, step=0.10, key="b_gs_prix")
    b_gs_rist = decision_row("042- Ristourne (%)", "number", min_value=0.0, max_value=20.0, value=0.0 if reset_products else 7.0, step=0.5, key="b_gs_rist")
    b_gs_promo = decision_row("043- Promotion (€/U)", "number", min_value=0.0, value=0.0 if reset_products else 0.80, step=0.05, key="b_gs_promo")
    b_gs_prod = decision_row("044- Production (KU)", "number", min_value=0, value=0 if reset_products else 120, step=10, key="b_gs_prod")
    b_gs_qual = decision_row("045- Qualité Produite (%)", "number", min_value=0, max_value=100, value=50, step=5, key="b_gs_qual")
    b_gs_emb = decision_row("046- Emballages Recyclés (O/N)", "checkbox", value=False, key="b_gs_emb")
    with st.expander("Contrats B-GS"):
        b_gs_v_contrat = decision_row("Ventes Contrat (U)", "number", min_value=0, value=0, step=100, key="b_gs_vc")
        b_gs_a_contrat = decision_row("Achats Contrat (U)", "number", min_value=0, value=0, step=100, key="b_gs_ac")
    
    net_b_container = st.empty()

    st.markdown("---")

    # --- PRODUIT C ---
    st.subheader("PRODUIT C")
    # C-CT
    c_ct_prix = decision_row("051-C CT Prix Tarif (€/U)", "number", min_value=0.0, value=0.0, step=0.10, key="c_ct_prix")
    c_ct_promo = decision_row("052- Promotion (€/U)", "number", min_value=0.0, value=0.0, step=0.05, key="c_ct_promo")
    c_ct_prod = decision_row("053- Production (KU)", "number", min_value=0, value=0, step=10, key="c_ct_prod")
    c_ct_qual = decision_row("054- Qualité Produite (%)", "number", min_value=0, max_value=100, value=0, step=5, key="c_ct_qual")
    c_ct_emb = decision_row("055- Emballages Recyclés (O/N)", "checkbox", value=False, key="c_ct_emb")
    with st.expander("Contrats C-CT"):
        c_ct_v_contrat = decision_row("Ventes Contrat (U)", "number", min_value=0, value=0, step=100, key="c_ct_vc")
        c_ct_a_contrat = decision_row("Achats Contrat (U)", "number", min_value=0, value=0, step=100, key="c_ct_ac")

    # C-GS
    st.markdown("**Produit C - Grande Surface**")
    c_gs_prix = decision_row("061-C GS Prix Tarif (€/U)", "number", min_value=0.0, value=0.0, step=0.10, key="c_gs_prix")
    c_gs_rist = decision_row("062- Ristourne (%)", "number", min_value=0.0, max_value=20.0, value=0.0, step=0.5, key="c_gs_rist")
    c_gs_promo = decision_row("063- Promotion (€/U)", "number", min_value=0.0, value=0.0, step=0.05, key="c_gs_promo")
    c_gs_prod = decision_row("064- Production (KU)", "number", min_value=0, value=0, step=10, key="c_gs_prod")
    c_gs_qual = decision_row("065- Qualité Produite (%)", "number", min_value=0, max_value=100, value=0, step=5, key="c_gs_qual")
    c_gs_emb = decision_row("066- Emballages Recyclés (O/N)", "checkbox", value=False, key="c_gs_emb")
    with st.expander("Contrats C-GS"):
        c_gs_v_contrat = decision_row("Ventes Contrat (U)", "number", min_value=0, value=0, step=100, key="c_gs_vc")
        c_gs_a_contrat = decision_row("Achats Contrat (U)", "number", min_value=0, value=0, step=100, key="c_gs_ac")
    
    net_c_container = st.empty()

    st.markdown("---")

    # --- MARKETING ---
    st.subheader("MARKETING")
    mkt_vendeurs_ct = decision_row("071- Nombre Vendeurs C.T.", "number", min_value=0, value=35, step=1, key="mkt_ven_ct")
    mkt_commission = decision_row("072- Commission (% du C.A.)", "number", min_value=0.0, max_value=5.0, value=0.5, step=0.1, key="mkt_comm")
    
    # Callback pour forcer majuscules sur les études
    def force_upper(key):
        if key in st.session_state and st.session_state[key]:
            st.session_state[key] = st.session_state[key].upper()

    mkt_etudes_abcd = decision_row("073- Etudes Codées (A..D) ou N", "text", value="ABC", key="mkt_etu_ad", on_change=force_upper, args=("mkt_etu_ad",))
    # Pas besoin de post-process manuel car le callback modifie le state, mais decision_row retourne la valeur courante.
    # Au prochain rerun ce sera à jour. Pour l'affichage instantané, on fait confiance au retour.
    
    mkt_etudes_efgh = decision_row("074- Etudes Codées (E..H) ou N", "text", value="N", key="mkt_etu_eh", on_change=force_upper, args=("mkt_etu_eh",))

    mkt_vendeurs_gs = decision_row("075- Nombre Vendeurs G.S.", "number", min_value=0, value=12, step=1, key="mkt_ven_gs")
    mkt_prime_gs = decision_row("076- Prime Trimest. (€/Vendeur)", "number", min_value=0.0, value=600.0, step=50.0, key="mkt_prime_gs")
    
    # Note: 077 seems missing in original code's sequence or was skipped
    
    mkt_pub_ct = decision_row("078- Publicité C.T. (K€)", "number", min_value=0.0, value=400.0, step=50.0, key="mkt_pub_ct")
    mkt_pub_gs = decision_row("079- Publicité G.S. (K€)", "number", min_value=0.0, value=0.0, step=50.0, key="mkt_pub_gs")

    net_mkt_container = st.empty()

    st.markdown("---")

    # --- APPROVISIONNEMENTS ---
    st.subheader("APPROVISIONNEMENTS")
    app_mp_n = decision_row("080- Commandes MP N (KU/per)", "number", min_value=0, value=0, step=500, key="app_mp_n_val")
    app_duree_n = decision_row("081- Durée contrat N (1-4)", "number", min_value=0, max_value=4, value=0, step=1, key="app_duree_n")

    app_mp_s = decision_row("082- Commandes MP S (KU/per)", "number", min_value=0, value=0, step=500, key="app_mp_s_val")
    app_duree_s = decision_row("083- Durée contrat S (1-4)", "number", min_value=0, max_value=4, value=0, step=1, key="app_duree_s")
    
    app_maintenance = decision_row("086- Maintenance (O/N)", "checkbox", value=True, key="app_maint")

    # Info Prix MP expander
    with st.expander("📋 Voir Grille de Prix MP"):
        col_prix1, col_prix2 = st.columns(2)
        with col_prix1:
            st.markdown("**MP N**")
            prix_n_df = pd.DataFrame({
                "Durée": ["1 per", "2 per", "3 per", "4 per"],
                "<1000": [1.235, 1.204, 1.173, 1.143],
                "1000-1500": [1.204, 1.173, 1.143, 1.112],
                ">3000": [1.081, 1.050, 1.019, 0.988], # Simplified for space
            })
            st.dataframe(prix_n_df, hide_index=True)
        with col_prix2:
            st.markdown("**MP S**")
            st.caption("Voir onglet Résultats pour détails si besoin")

    net_appro_container = st.empty()

    st.markdown("---")



    # --- PRODUCTION ---
    st.subheader("PRODUCTION")

    prod_m1_actives = decision_row("089- Machines M1 Actives", "number", min_value=0, value=min(17, nb_machines_m1) if nb_machines_m1 > 0 else 0, step=1, key="prod_m1")
    prod_m2_actives = decision_row("090- Machines M2 Actives", "number", min_value=0, value=0, step=1, key="prod_m2")

    prod_ventes_m1 = decision_row("091- Ventes Machines M1", "number", min_value=0, value=0, step=1, key="prod_v_m1")
    prod_achats_m1 = decision_row("092- Achats Machines M1", "number", min_value=0, value=0, step=1, key="prod_a_m1")
    prod_achats_m2 = decision_row("093- Achats Machines M2", "number", min_value=0, value=0, step=1, key="prod_a_m2")

    prod_emb_deb = decision_row("094- Emb/Deb. Ouvriers", "number", value=0, step=10, key="prod_emb")
    prod_var_pa = decision_row("095- Variat. Pouvoir Achat (%)", "number", value=2.0, step=0.5, key="prod_vpa")
    
    # Info Capacité
    capacite_m1 = prod_m1_actives * C.M1_CAPACITY_A
    capacite_m2 = prod_m2_actives * C.M2_CAPACITY_A
    capacite_totale = capacite_m1 + capacite_m2
    ouvriers_apres = nb_ouvriers + prod_emb_deb
    ouvriers_necessaires = prod_m1_actives * C.WORKERS_PER_M1 + prod_m2_actives * C.WORKERS_PER_M2
    
    if ouvriers_apres < ouvriers_necessaires:
        st.error(f"⚠️ **Attention**: Manque {ouvriers_necessaires - ouvriers_apres} ouvriers pour faire tourner les machines!")
    else:
        st.caption(f"ℹ️ Capacité Totale: {capacite_totale:,.0f} U | Ouvriers dispo: {ouvriers_apres}")

    # --- NOUVEAU: Pré-calcul des besoins en MP pour aider à la saisie ---
    st.markdown("**Besoins en Matières Premières (Estimés)**")
    # On utilise les résultats du calcul anticipé qui sont disponibles via sim_results
    # MAIS attention sim_results n'est calculé que tout en bas du script, donc pas encore dispo ici dans le flux d'affichage standard...
    # SAUF si on fait un pre-calcul léger ici ou si on utilise les placeholders.
    # Pour faire simple et robuste : on calcule les besoins théoriques MP ici basés sur les inputs actuels
    
    # Recalcul rapide des besoins (logique dupliquée de calculator malheureusement, ou on attend le recalcul complet)
    # Pour être "automatique", on peut proposer un bouton ou juste afficher l'info calculation
    
    # Récupération des décisions de prod saisies plus haut
    prod_a_tot = (a_ct_prod + a_gs_prod) * 1000
    prod_b_tot = (b_ct_prod + b_gs_prod) * 1000
    prod_c_tot = (c_ct_prod + c_gs_prod) * 1000

    def get_mp_needs_local(prod_u, units_per_prod, qual):
        n_needed = prod_u * units_per_prod * (qual / 100.0)
        s_needed = prod_u * units_per_prod * ((100.0 - qual) / 100.0)
        return n_needed, s_needed

    need_n_a, need_s_a = get_mp_needs_local(a_ct_prod*1000, C.UNITS_MP_PER_UNIT_A, a_ct_qual)
    need_n_a_gs, need_s_a_gs = get_mp_needs_local(a_gs_prod*1000, C.UNITS_MP_PER_UNIT_A, a_gs_qual)
    need_n_b, need_s_b = get_mp_needs_local(b_ct_prod*1000, C.UNITS_MP_PER_UNIT_B, b_ct_qual)
    need_n_b_gs, need_s_b_gs = get_mp_needs_local(b_gs_prod*1000, C.UNITS_MP_PER_UNIT_B, b_gs_qual)
    need_n_c, need_s_c = get_mp_needs_local(c_ct_prod*1000, C.UNITS_MP_PER_UNIT_C, c_ct_qual)
    need_n_c_gs, need_s_c_gs = get_mp_needs_local(c_gs_prod*1000, C.UNITS_MP_PER_UNIT_C, c_gs_qual)

    total_need_n = need_n_a + need_n_a_gs + need_n_b + need_n_b_gs + need_n_c + need_n_c_gs
    total_need_s = need_s_a + need_s_a_gs + need_s_b + need_s_b_gs + need_s_c + need_s_c_gs

    col_mp_info1, col_mp_info2 = st.columns(2)
    with col_mp_info1:
        st.info(f"Besoin TOTAL MP N : **{total_need_n:,.0f}** U")
        st.caption(f"Stock N dispo : {stock_mp_n:,.0f} U")
        manque_n = max(0, total_need_n - stock_mp_n)
        if manque_n > 0:
            st.warning(f"⚠️ Il manque **{manque_n:,.0f}** MP N")

    with col_mp_info2:
        st.info(f"Besoin TOTAL MP S : **{total_need_s:,.0f}** U")
        st.caption(f"Stock S dispo : {stock_mp_s:,.0f} U")
        manque_s = max(0, total_need_s - stock_mp_s)
        if manque_s > 0:
            st.warning(f"⚠️ Il manque **{manque_s:,.0f}** MP S")
            if st.button("🛒 Ajuster Commande S", key="auto_app_s"):
                missing_ku = manque_s / 1000.0
                st.session_state["app_mp_s_val"] = float(int(missing_ku) + 1)
                st.rerun()

    net_prod_container = st.empty()
    net_rse_container = st.empty()

    st.markdown("---")

    # --- RSE ---
    st.subheader("RSE (RESPONSABILITÉ SOCIÉTALE)")
    rse_recyclage = decision_row("087- Budget Recyclage (K€)", "number", min_value=0.0, value=0.0, step=50.0, key="rse_cyc")
    rse_amenagements = decision_row("088- Aménagements adaptés (K€)", "number", min_value=0.0, value=0.0, step=50.0, key="rse_amen")
    rse_rd = decision_row("096- Recherche et Dévelop. (K€)", "number", min_value=0.0, value=0.0, step=50.0, key="rse_rd")

    net_rse_container = st.empty()

    st.markdown("---")

    # --- FINANCES ---
    st.subheader("FINANCES")
    
    fin_emprunt_lt = decision_row("097- Emprunt Long Terme (K€)", "number", min_value=0.0, value=0.0, step=100.0, key="fin_elt")
    fin_duree_lt = decision_row("098- Nb de Trimestres (2-8)", "number", min_value=0, max_value=8, value=0, step=1, key="fin_dlt")
    
    fin_effort_social = decision_row("101- Effort Social (%)", "number", min_value=0.0, max_value=10.0, value=0.0, step=0.5, key="fin_soc")
    fin_emprunt_ct = decision_row("102- Emprunt Court Terme (K€)", "number", min_value=0.0, value=0.0, step=100.0, key="fin_ect")
    fin_effets = decision_row("103- Effets escomptés (K€)", "number", min_value=0.0, value=0.0, step=100.0, key="fin_eff")
    fin_escompte = decision_row("104- Escompte Paiement Cpt (%)", "number", min_value=0.0, max_value=10.0, value=7.5, step=0.5, key="fin_esc")
    fin_dividendes = decision_row("105- Dividendes (K€)", "number", min_value=0.0, value=200.0, step=50.0, key="fin_div")
    fin_rembt = decision_row("106- Rembt. dernier emprunt", "checkbox", value=False, key="fin_rem")
    
    fin_actions_new = decision_row("107- Nb actions nouvelles (KU)", "number", min_value=0, value=0, step=10, key="fin_act")
    fin_prix_emission = decision_row("108- Prix d'emission (€)", "number", min_value=0.0, value=0.0, step=1.0, key="fin_pax")

    net_finance_container = st.empty()

    st.markdown("---")
    st.subheader("FRAIS DE STRUCTURE & DIVERS")
    st.info("ℹ️ Cette section regroupe les frais administratifs, de direction et de déplacements.")
    net_structure_container = st.empty()

    st.markdown("---")
    st.subheader("ACHATS / VENTES DE TITRES")
    titres_f1 = decision_row("131- Actions F1", "number", value=0, step=100, key="tit_f1")
    titres_f2 = decision_row("132- Actions F2", "number", value=0, step=100, key="tit_f2")
    titres_f3 = decision_row("133- Actions F3", "number", value=0, step=100, key="tit_f3")
    titres_f4 = decision_row("134- Actions F4", "number", value=0, step=100, key="tit_f4")
    titres_f5 = decision_row("135- Actions F5", "number", value=0, step=100, key="tit_f5")
    titres_f6 = decision_row("136- Actions F6", "number", value=0, step=100, key="tit_f6")

    st.markdown("---")
    
    # --- PRÉVISIONS ---
    st.subheader("PRÉVISIONS (Pour information)")

    # Calcul des disponibilités maximales pour définir les bornes des sliders
    # Dispo = Stock Init + Prod(U) + Achat Contract(U) - Vente Contract(U)
    # Les inputs Production sont en KU (*1000)
    def get_max_sales_vol(stock, prod_ku, achat_c, vente_c):
        total_phys = stock + (prod_ku * 1000) + achat_c
        return max(0, total_phys - vente_c)

    # Récupération sécurisée des valeurs
    max_a_ct = get_max_sales_vol(state.stock_a_ct, a_ct_prod, a_ct_a_contrat, a_ct_v_contrat)
    max_a_gs = get_max_sales_vol(state.stock_a_gs, a_gs_prod, a_gs_a_contrat, a_gs_v_contrat)
    max_b_ct = get_max_sales_vol(state.stock_b_ct, b_ct_prod, b_ct_a_contrat, b_ct_v_contrat)
    max_b_gs = get_max_sales_vol(state.stock_b_gs, b_gs_prod, b_gs_a_contrat, b_gs_v_contrat)
    max_c_ct = get_max_sales_vol(state.stock_c_ct, c_ct_prod, c_ct_a_contrat, c_ct_v_contrat)
    max_c_gs = get_max_sales_vol(state.stock_c_gs, c_gs_prod, c_gs_a_contrat, c_gs_v_contrat)

    st.markdown("##### 🔮 Hypothèses de Ventes (Volumes)")
    st.caption("Ajustez le volume de vente prévisionnel pour estimer la trésorerie et la rentabilité. (Max = Stock dispo + Production net de contrats)")

    col_prev1, col_prev2, col_prev3 = st.columns(3)
    
    # Helper pour initialiser le number_input sans erreur si value > max
    def numeric_input_safe(label, max_val, step=100):
        # Si le max est 0, on garde 0.
        # Sinon on essaye d'initialiser à max par défaut pour faciliter la vie.
        return st.number_input(label, min_value=0, max_value=int(max_val), value=int(max_val), step=step)
    
    with col_prev1:
        st.markdown("**Produit A**")
        fc_a_ct = numeric_input_safe("Prev. Vente A-CT", max_a_ct)
        fc_a_gs = numeric_input_safe("Prev. Vente A-GS", max_a_gs)
    
    with col_prev2:
        st.markdown("**Produit B**")
        fc_b_ct = numeric_input_safe("Prev. Vente B-CT", max_b_ct)
        fc_b_gs = numeric_input_safe("Prev. Vente B-GS", max_b_gs)
        
    with col_prev3:
        st.markdown("**Produit C**")
        fc_c_ct = numeric_input_safe("Prev. Vente C-CT", max_c_ct)
        fc_c_gs = numeric_input_safe("Prev. Vente C-GS", max_c_gs)

    forecast_dict = {
        "A-CT": fc_a_ct, "A-GS": fc_a_gs,
        "B-CT": fc_b_ct, "B-GS": fc_b_gs,
        "C-CT": fc_c_ct, "C-GS": fc_c_gs
    }

    # Calcul intermédiaire pour aider à la saisie
    # On reconstitue l'objet décisions avec les variables locales définies ci-dessus
    current_decisions = AllDecisions(
        produit_a_ct=ProductDecision(
            prix_tarif=a_ct_prix, promotion=a_ct_promo, production=a_ct_prod,
            qualite=a_ct_qual, emballage_recycle=a_ct_emb,
            ventes_contrat=a_ct_v_contrat, achats_contrat=a_ct_a_contrat
        ),
        produit_a_gs=ProductDecision(
            prix_tarif=a_gs_prix, ristourne=a_gs_rist, promotion=a_gs_promo,
            production=a_gs_prod, qualite=a_gs_qual, emballage_recycle=a_gs_emb,
            ventes_contrat=a_gs_v_contrat, achats_contrat=a_gs_a_contrat
        ),
        produit_b_ct=ProductDecision(
            prix_tarif=b_ct_prix, promotion=b_ct_promo, production=b_ct_prod,
            qualite=b_ct_qual, emballage_recycle=b_ct_emb,
            ventes_contrat=b_ct_v_contrat, achats_contrat=b_ct_a_contrat
        ),
        produit_b_gs=ProductDecision(
            prix_tarif=b_gs_prix, ristourne=b_gs_rist, promotion=b_gs_promo,
            production=b_gs_prod, qualite=b_gs_qual, emballage_recycle=b_gs_emb,
            ventes_contrat=b_gs_v_contrat, achats_contrat=b_gs_a_contrat
        ),
        produit_c_ct=ProductDecision(
            prix_tarif=c_ct_prix, promotion=c_ct_promo, production=c_ct_prod,
            qualite=c_ct_qual, emballage_recycle=c_ct_emb,
            ventes_contrat=c_ct_v_contrat, achats_contrat=c_ct_a_contrat
        ),
        produit_c_gs=ProductDecision(
            prix_tarif=c_gs_prix, ristourne=c_gs_rist, promotion=c_gs_promo,
            production=c_gs_prod, qualite=c_gs_qual, emballage_recycle=c_gs_emb,
            ventes_contrat=c_gs_v_contrat, achats_contrat=c_gs_a_contrat
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
            maintenance=app_maintenance,
            achat_spot_n=0, achat_spot_s=0
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
    
    # Calcul anticipé
    sim_results = calculate_all(current_decisions, state, forecast_sales=forecast_dict)

    # --- POPULATE NET CATEGORY PLACEHOLDERS ---
    
    # NET A
    if 'net_a_container' in locals():
        res_a = sim_results.marge_sur_cout_variable_a
        c_a = "green" if res_a > 0 else "red"
        net_a_container.markdown(f"👉 **NET CATEGORIE A** (Gain - Coûts Spécifiques) : <span style='color:{c_a}; font-weight:bold'>{res_a:,.0f} K€</span>", unsafe_allow_html=True)

    # NET B
    if 'net_b_container' in locals():
        res_b = sim_results.marge_sur_cout_variable_b
        c_b = "green" if res_b > 0 else "red"
        net_b_container.markdown(f"👉 **NET CATEGORIE B** (Gain - Coûts Spécifiques) : <span style='color:{c_b}; font-weight:bold'>{res_b:,.0f} K€</span>", unsafe_allow_html=True)
    
    # NET C
    if 'net_c_container' in locals():
        res_c = sim_results.marge_sur_cout_variable_c
        c_c = "green" if res_c > 0 else "red"
        net_c_container.markdown(f"👉 **NET CATEGORIE C** (Gain - Coûts Spécifiques) : <span style='color:{c_c}; font-weight:bold'>{res_c:,.0f} K€</span>", unsafe_allow_html=True)

    # NET MARKETING
    if 'net_mkt_container' in locals():
        cost_mkt = sim_results.cout_marketing_total_section
        # Marketing est toujours un coût, donc rouge
        net_mkt_container.markdown(f"👉 **TOTAL SECTION MARKETING** : <span style='color:red; font-weight:bold'>-{cost_mkt:,.0f} K€</span>", unsafe_allow_html=True)

    # NET APPROVISIONNEMENT
    if 'net_appro_container' in locals():
        cost_appro = sim_results.cout_appro_total_section
        net_appro_container.markdown(f"👉 **TOTAL SECTION APPROVISIONNEMENT** (MP Consommée + Maint.) : <span style='color:red; font-weight:bold'>-{cost_appro:,.0f} K€</span>", unsafe_allow_html=True)

    # NET PRODUCTION
    if 'net_prod_container' in locals():
        # Prod UI = MO + Amort (MP et Maint sont en Appro) + Embauche
        # Note: sim_results.cout_production_total contient tout sauf embauche (ajoutée après dans calculator, champ séparé)
        cost_prod_ui = sim_results.cout_main_oeuvre + sim_results.cout_amortissement + sim_results.cout_embauche
        net_prod_container.markdown(f"👉 **TOTAL SECTION PRODUCTION** (Main d'Oeuvre + Amort + Embauche) : <span style='color:red; font-weight:bold'>-{cost_prod_ui:,.0f} K€</span>", unsafe_allow_html=True)

    # NET RSE
    if 'net_rse_container' in locals():
        cost_rse = sim_results.cout_rse_total_section
        net_rse_container.markdown(f"👉 **TOTAL SECTION RSE** : <span style='color:red; font-weight:bold'>-{cost_rse:,.0f} K€</span>", unsafe_allow_html=True)

    # NET FINANCE
    if 'net_finance_container' in locals():
        cost_fin = sim_results.cout_finance_total_section
        net_finance_container.markdown(f"👉 **TOTAL SECTION FINANCE** (Impayés + Escompte + Intérêts) : <span style='color:red; font-weight:bold'>-{cost_fin:,.0f} K€</span>", unsafe_allow_html=True)

    # NET STRUCTURE
    if 'net_structure_container' in locals():
        cost_struct = sim_results.cout_structure_admin + sim_results.cout_frais_deplacement
        net_structure_container.markdown(f"👉 **TOTAL CHARGES STRUCTURE/ADMIN** : <span style='color:red; font-weight:bold'>-{cost_struct:,.0f} K€</span>", unsafe_allow_html=True)

    # --- AFFICHAGE DES CALCULS DE PRÉVISION ---
    col_prev1, col_prev2, col_prev3 = st.columns(3)
    with col_prev1:
        st.metric("CA Potentiel Total", f"{sim_results.ca_potentiel_total:,.0f} K€", help="Chiffre d'Affaires si tout le stock disponible est vendu")
    with col_prev2:
        # Estimation Résultat simple
        # Marge = CA - Coûts Prod - Coûts Commerciaux - Etudes - Finances - Embauche + Variation Stock
        marge_estimee = (sim_results.ca_potentiel_total 
                         - sim_results.cout_production_total 
                         - sim_results.cout_commercial_total 
                         - sim_results.cout_etudes 
                         - sim_results.cout_finance_total_section 
                         - sim_results.cout_embauche
                         - sim_results.cout_structure_admin
                         - sim_results.cout_frais_deplacement
                         + sim_results.valeur_variation_stocks)
                         
        st.metric("Résultat Opérationnel Est.", f"{marge_estimee:,.0f} K€", help="Inclus Variation de Stocks (Production stockée ou déstockage valorisé au coût de production)")
    with col_prev3:
        delta_color = "normal" if sim_results.tresorerie_estimee >= 0 else "inverse"
        st.metric("Trésorerie Fin Période", f"{sim_results.tresorerie_estimee:,.0f} K€", delta_color=delta_color)

    # Flux de trésorerie détaillés
    st.caption("Détail flux :")
    col_flow1, col_flow2 = st.columns(2)
    with col_flow1:
        st.metric("Encaissements Totaux", f"+{sim_results.encaissements_total:,.0f} K€", help="Ventes encaissées + Emprunts + Cessions")
    with col_flow2:
        # Update Decaissements calculation logic in calculator? 
        # Actually calculator computes decaissements_total separately.
        # But we need to make sure calculator includes structure cost in decaissements.
        # Checking calculator.py... yes, previously I added it to decaissements_autres via 'cout_production_total' hack which I removed.
        # WAIT! I removed the hack in calculator.py but did I add it to decaissements_autres?
        # I need to CHECK calculator.py again for decaissements logic.
        curr_flow = sim_results.decaissements_total + sim_results.cout_structure_admin + sim_results.cout_frais_deplacement # Patching it here visually if missing in calculator? No, better fix calculator.
        st.metric("Décaissements Totaux", f"-{sim_results.decaissements_total:,.0f} K€", help="Achats MP + Personnel + Charges + Investissements + Dividendes")

    if sim_results.warnings:
        st.error(f"⚠️ {len(sim_results.warnings)} Alertes détectées")
        with st.expander("Voir le détail des alertes", expanded=True):
            for w in sim_results.warnings:
                st.warning(w)

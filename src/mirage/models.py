"""Data models for Mirage simulation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductDecision:
    """Décisions pour un produit sur un marché."""

    prix_tarif: float = 0.0
    promotion: float = 0.0  # €/Unité pour CT, €/Unité pour GS
    ristourne: float = 0.0  # % pour GS uniquement
    production: int = 0  # KU
    qualite: int = 100  # % (100 ou 50)
    emballage_recycle: bool = False
    ventes_contrat: int = 0  # Unités vendues sur contrat
    achats_contrat: int = 0  # Unités achetées sur contrat


@dataclass
class MarketingDecision:
    """Décisions marketing."""

    vendeurs_ct: int = 35
    commission_ct: float = 0.5  # % du CA
    vendeurs_gs: int = 0
    prime_trimestre_gs: float = 0.0  # €/vendeur
    publicite_ct: float = 0.0  # K€
    publicite_gs: float = 0.0  # K€
    etudes_abcd: str = "N"  # Études codées A à D ou N
    etudes_efgh: str = "N"  # Études codées E à H ou N


@dataclass
class ApprovisionnementDecision:
    """Décisions d'approvisionnement."""

    commandes_mp_n: int = 0  # KU/per
    duree_contrat_n: int = 0  # 1 à 4 périodes
    commandes_mp_s: int = 0  # KU/per
    duree_contrat_s: int = 0  # 1 à 4 périodes
    maintenance: bool = True


@dataclass
class ProductionDecision:
    """Décisions de production."""

    machines_m1_actives: int = 15
    machines_m2_actives: int = 0
    ventes_m1: int = 0
    achats_m1: int = 0
    achats_m2: int = 0
    emb_deb_ouvriers: int = 0
    variation_pouvoir_achat: float = 0.0  # %


@dataclass
class RSEDecision:
    """Décisions RSE."""

    budget_recyclage: float = 0.0  # K€
    amenagements_adaptes: float = 0.0  # K€
    recherche_dev: float = 0.0  # K€


@dataclass
class FinanceDecision:
    """Décisions financières."""

    emprunt_lt: float = 0.0  # K€
    duree_emprunt_lt: int = 0  # 2 à 8 trimestres
    effort_social: float = 0.0  # %
    emprunt_ct: float = 0.0  # K€
    effets_escomptes: float = 0.0  # K€
    escompte_paiement_cpt: float = 0.0  # %
    dividendes: float = 0.0  # K€
    rembt_dernier_emprunt: bool = False
    nb_actions_nouvelles: int = 0
    prix_emission: float = 0.0


@dataclass
class TitresDecision:
    """Décisions d'achats/ventes de titres."""

    actions_f1: int = 0
    actions_f2: int = 0
    actions_f3: int = 0
    actions_f4: int = 0
    actions_f5: int = 0
    actions_f6: int = 0


@dataclass
class PeriodState:
    """État de la firme à une période donnée."""

    # Période de l'année (1, 2, 3 ou 4)
    period_num: int = 1

    # Stocks de produits finis
    stock_a_ct: int = 0
    stock_a_gs: int = 0
    stock_b_ct: int = 0
    stock_b_gs: int = 0
    stock_c_ct: int = 0
    stock_c_gs: int = 0

    # Stocks matières premières
    stock_mp_n: int = 0  # unités
    stock_mp_s: int = 0

    # Effectifs
    nb_ouvriers: int = 580
    nb_machines_m1: int = 15
    nb_machines_m2: int = 0

    # Finances
    cash: float = 0.0
    dette_lt: float = 0.0
    dette_ct: float = 0.0
    reserves: float = 0.0  # Réserves accumulées
    resultat_n_1: float = 0.0  # Résultat net de l'année N-1 (ou période précédente)

    # Indices
    indice_prix: float = 100.0
    indice_salaire: float = 100.0


@dataclass
class CalculatedResults:
    """Résultats calculés à partir des décisions."""

    # Capacité de production
    capacite_m1_a: int = 0
    capacite_m1_b: int = 0
    capacite_m1_c: int = 0
    capacite_m2_a: int = 0
    capacite_m2_b: int = 0
    capacite_m2_c: int = 0
    capacite_totale_a: int = 0
    capacite_totale_b: int = 0
    capacite_totale_c: int = 0

    # Besoins en MP
    mp_n_necessaire: int = 0
    mp_s_necessaire: int = 0
    mp_n_disponible: int = 0
    mp_s_disponible: int = 0
    mp_n_apres_prod: int = 0
    mp_s_apres_prod: int = 0

    # Besoins en ouvriers
    ouvriers_necessaires: int = 0
    ouvriers_disponibles: int = 0
    variation_ouvriers: int = 0

    # Coûts de production estimés
    cout_mp: float = 0.0
    cout_main_oeuvre: float = 0.0
    cout_amortissement: float = 0.0
    cout_maintenance: float = 0.0
    cout_production_total: float = 0.0

    # Coûts commerciaux
    cout_promotion: float = 0.0
    cout_vendeurs: float = 0.0
    cout_publicite: float = 0.0
    cout_commercial_total: float = 0.0

    # Coûts études
    cout_etudes: float = 0.0

    # Revenus estimés (si tout vendu)
    ca_contrats: float = 0.0
    ca_potentiel_a_ct: float = 0.0
    ca_potentiel_a_gs: float = 0.0
    ca_potentiel_b_ct: float = 0.0
    ca_potentiel_b_gs: float = 0.0
    ca_potentiel_c_ct: float = 0.0
    ca_potentiel_c_gs: float = 0.0
    ca_potentiel_total: float = 0.0

    # Prix nets
    prix_net_a_ct: float = 0.0
    prix_net_a_gs: float = 0.0
    prix_net_b_ct: float = 0.0
    prix_net_b_gs: float = 0.0
    prix_net_c_ct: float = 0.0
    prix_net_c_gs: float = 0.0

    # Stocks disponibles à la vente
    stock_dispo_a_ct: int = 0
    stock_dispo_a_gs: int = 0
    stock_dispo_b_ct: int = 0
    stock_dispo_b_gs: int = 0
    stock_dispo_c_ct: int = 0
    stock_dispo_c_gs: int = 0

    # Cash flows estimés
    decaissements_mp: float = 0.0
    decaissements_personnel: float = 0.0
    decaissements_investissements: float = 0.0
    decaissements_autres: float = 0.0
    decaissements_total: float = 0.0

    encaissements_ventes_estimees: float = 0.0
    encaissements_emprunts: float = 0.0
    encaissements_total: float = 0.0

    # Prévisions trésorerie
    tresorerie_estimee: float = 0.0

    # Warnings
    warnings: list = field(default_factory=list)

    # Marges analytiques (pour affichage par section)
    cout_prod_a: float = 0.0
    cout_prod_b: float = 0.0
    cout_prod_c: float = 0.0

    marge_sur_cout_variable_a: float = 0.0
    marge_sur_cout_variable_b: float = 0.0
    marge_sur_cout_variable_c: float = 0.0

    cout_marketing_total_section: float = 0.0


@dataclass
class AllDecisions:
    """Toutes les décisions pour une période."""

    produit_a_ct: ProductDecision = field(default_factory=ProductDecision)
    produit_a_gs: ProductDecision = field(default_factory=ProductDecision)
    produit_b_ct: ProductDecision = field(default_factory=ProductDecision)
    produit_b_gs: ProductDecision = field(default_factory=ProductDecision)
    produit_c_ct: ProductDecision = field(default_factory=ProductDecision)
    produit_c_gs: ProductDecision = field(default_factory=ProductDecision)
    marketing: MarketingDecision = field(default_factory=MarketingDecision)
    approvisionnement: ApprovisionnementDecision = field(
        default_factory=ApprovisionnementDecision
    )
    production: ProductionDecision = field(default_factory=ProductionDecision)
    rse: RSEDecision = field(default_factory=RSEDecision)
    finance: FinanceDecision = field(default_factory=FinanceDecision)
    titres: TitresDecision = field(default_factory=TitresDecision)

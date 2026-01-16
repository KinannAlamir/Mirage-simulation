"""Calculator for Mirage simulation decisions."""

from . import constants as C
from .models import AllDecisions, CalculatedResults, PeriodState


def calculate_study_costs(etudes_abcd: str, etudes_efgh: str) -> float:
    """Calcule le coût des études demandées."""
    cost = 0.0
    etudes = (etudes_abcd + etudes_efgh).upper()

    if "A" in etudes:
        cost += C.STUDY_A_COST
    if "B" in etudes:
        cost += C.STUDY_B_COST
    if "C" in etudes:
        cost += C.STUDY_C_COST
    if "D" in etudes:
        cost += C.STUDY_D_COST
    if "E" in etudes:
        cost += C.STUDY_E_COST
    if "F" in etudes:
        cost += C.STUDY_F_COST
    if "G" in etudes:
        cost += C.STUDY_G_COST
    if "H" in etudes:
        cost += C.STUDY_H_COST

    return cost


def calculate_all(decisions: AllDecisions, state: PeriodState) -> CalculatedResults:
    """Calcule tous les résultats à partir des décisions et de l'état actuel."""
    results = CalculatedResults()
    results.warnings = []

    # =========================================================================
    # 1. CAPACITÉ DE PRODUCTION
    # =========================================================================
    m1_active = decisions.production.machines_m1_actives
    m2_active = decisions.production.machines_m2_actives

    results.capacite_m1_a = m1_active * C.M1_CAPACITY_A
    results.capacite_m1_b = m1_active * C.M1_CAPACITY_B
    results.capacite_m1_c = m1_active * C.M1_CAPACITY_C

    results.capacite_m2_a = m2_active * C.M2_CAPACITY_A
    results.capacite_m2_b = m2_active * C.M2_CAPACITY_B
    results.capacite_m2_c = m2_active * C.M2_CAPACITY_C

    results.capacite_totale_a = results.capacite_m1_a + results.capacite_m2_a
    results.capacite_totale_b = results.capacite_m1_b + results.capacite_m2_b
    results.capacite_totale_c = results.capacite_m1_c + results.capacite_m2_c

    # =========================================================================
    # 2. PRODUCTION PLANIFIÉE (en unités)
    # =========================================================================
    prod_a_ct = decisions.produit_a_ct.production * 1000  # KU -> U
    prod_a_gs = decisions.produit_a_gs.production * 1000
    prod_b_ct = decisions.produit_b_ct.production * 1000
    prod_b_gs = decisions.produit_b_gs.production * 1000
    prod_c_ct = decisions.produit_c_ct.production * 1000
    prod_c_gs = decisions.produit_c_gs.production * 1000

    total_prod_a = prod_a_ct + prod_a_gs
    total_prod_b = prod_b_ct + prod_b_gs
    total_prod_c = prod_c_ct + prod_c_gs

    # Vérifier capacité
    # Calcul simplifié: on suppose production équivalente en unités "A"
    # Produit C compte double en termes de capacité
    capacite_equivalent = results.capacite_totale_a
    production_equivalent = total_prod_a + total_prod_b + (total_prod_c * 2)

    if production_equivalent > capacite_equivalent:
        results.warnings.append(
            f"⚠️ Production demandée ({production_equivalent:,.0f} eq.) dépasse la capacité ({capacite_equivalent:,.0f} eq.)"
        )

    # =========================================================================
    # 3. BESOINS EN MATIÈRES PREMIÈRES
    # =========================================================================
    # MP N pour qualité 100%, MP S pour qualité 50%
    mp_a_ct = prod_a_ct * C.UNITS_MP_PER_UNIT_A
    mp_a_gs = prod_a_gs * C.UNITS_MP_PER_UNIT_A
    mp_b_ct = prod_b_ct * C.UNITS_MP_PER_UNIT_B
    mp_b_gs = prod_b_gs * C.UNITS_MP_PER_UNIT_B
    mp_c_ct = prod_c_ct * C.UNITS_MP_PER_UNIT_C
    mp_c_gs = prod_c_gs * C.UNITS_MP_PER_UNIT_C

    # Répartition N/S selon qualité
    mp_n_needed = 0
    mp_s_needed = 0

    if decisions.produit_a_ct.qualite == 100:
        mp_n_needed += mp_a_ct
    else:
        mp_s_needed += mp_a_ct

    if decisions.produit_a_gs.qualite == 100:
        mp_n_needed += mp_a_gs
    else:
        mp_s_needed += mp_a_gs

    if decisions.produit_b_ct.qualite == 100:
        mp_n_needed += mp_b_ct
    else:
        mp_s_needed += mp_b_ct

    if decisions.produit_b_gs.qualite == 100:
        mp_n_needed += mp_b_gs
    else:
        mp_s_needed += mp_b_gs

    if decisions.produit_c_ct.qualite == 100:
        mp_n_needed += mp_c_ct
    else:
        mp_s_needed += mp_c_ct

    if decisions.produit_c_gs.qualite == 100:
        mp_n_needed += mp_c_gs
    else:
        mp_s_needed += mp_c_gs

    results.mp_n_necessaire = int(mp_n_needed)
    results.mp_s_necessaire = int(mp_s_needed)

    # MP disponibles (stock initial + livraisons contrat en cours)
    results.mp_n_disponible = state.stock_mp_n + (
        decisions.approvisionnement.commandes_mp_n * 1000
        if decisions.approvisionnement.duree_contrat_n > 0
        else 0
    )
    results.mp_s_disponible = state.stock_mp_s + (
        decisions.approvisionnement.commandes_mp_s * 1000
        if decisions.approvisionnement.duree_contrat_s > 0
        else 0
    )

    results.mp_n_apres_prod = results.mp_n_disponible - results.mp_n_necessaire
    results.mp_s_apres_prod = results.mp_s_disponible - results.mp_s_necessaire

    if results.mp_n_apres_prod < 0:
        results.warnings.append(
            f"⚠️ Stock MP N insuffisant! Manque {-results.mp_n_apres_prod:,.0f} unités"
        )
    if results.mp_s_apres_prod < 0:
        results.warnings.append(
            f"⚠️ Stock MP S insuffisant! Manque {-results.mp_s_apres_prod:,.0f} unités"
        )

    # =========================================================================
    # 4. BESOINS EN OUVRIERS
    # =========================================================================
    results.ouvriers_necessaires = (
        m1_active * C.WORKERS_PER_M1 + m2_active * C.WORKERS_PER_M2
    )
    results.ouvriers_disponibles = state.nb_ouvriers + decisions.production.emb_deb_ouvriers
    results.variation_ouvriers = decisions.production.emb_deb_ouvriers

    if results.ouvriers_disponibles < results.ouvriers_necessaires:
        results.warnings.append(
            f"⚠️ Ouvriers insuffisants! Besoin: {results.ouvriers_necessaires}, "
            f"Disponible: {results.ouvriers_disponibles}"
        )

    # =========================================================================
    # 5. COÛTS DE PRODUCTION
    # =========================================================================
    # Coût MP (estimation basée sur les prix actuels)
    prix_mp_n = 0.80  # €/unité approximatif
    prix_mp_s = 0.70
    results.cout_mp = (results.mp_n_necessaire * prix_mp_n + results.mp_s_necessaire * prix_mp_s) / 1000  # K€

    # Coût main d'œuvre
    salaire_moyen = C.WORKER_BASE_SALARY * (1 + state.indice_salaire / 100 - 1)
    results.cout_main_oeuvre = (
        results.ouvriers_disponibles * salaire_moyen * (1 + C.SOCIAL_CHARGES_RATE) * 3 / 1000
    )  # K€ pour 3 mois

    # Amortissement machines
    depreciation_m1 = m1_active * C.M1_PURCHASE_PRICE / (C.M1_DEPRECIATION_YEARS * 4)
    depreciation_m2 = m2_active * C.M2_PURCHASE_PRICE / (C.M2_DEPRECIATION_YEARS * 4)
    results.cout_amortissement = depreciation_m1 + depreciation_m2

    # Maintenance
    if decisions.approvisionnement.maintenance:
        results.cout_maintenance = (
            m1_active * C.MAINTENANCE_COST_M1 + m2_active * C.MAINTENANCE_COST_M2
        )
    else:
        results.cout_maintenance = 0

    results.cout_production_total = (
        results.cout_mp
        + results.cout_main_oeuvre
        + results.cout_amortissement
        + results.cout_maintenance
    )

    # =========================================================================
    # 6. COÛTS COMMERCIAUX
    # =========================================================================
    # Promotion
    promo_a_ct = decisions.produit_a_ct.promotion * prod_a_ct / 1000
    promo_a_gs = decisions.produit_a_gs.promotion * prod_a_gs / 1000
    promo_b_ct = decisions.produit_b_ct.promotion * prod_b_ct / 1000
    promo_b_gs = decisions.produit_b_gs.promotion * prod_b_gs / 1000
    promo_c_ct = decisions.produit_c_ct.promotion * prod_c_ct / 1000
    promo_c_gs = decisions.produit_c_gs.promotion * prod_c_gs / 1000
    results.cout_promotion = promo_a_ct + promo_a_gs + promo_b_ct + promo_b_gs + promo_c_ct + promo_c_gs

    # Vendeurs
    cout_vendeurs_ct = (
        decisions.marketing.vendeurs_ct
        * C.TO_SALESPERSON_SALARY
        * 3  # 3 mois
        * (1 + C.SOCIAL_CHARGES_RATE)
        / 1000
    )
    cout_vendeurs_gs = (
        decisions.marketing.vendeurs_gs
        * (C.MR_SALESPERSON_SALARY + decisions.marketing.prime_trimestre_gs)
        * 3
        * (1 + C.SOCIAL_CHARGES_RATE)
        / 1000
    )
    results.cout_vendeurs = cout_vendeurs_ct + cout_vendeurs_gs

    # Publicité
    results.cout_publicite = decisions.marketing.publicite_ct + decisions.marketing.publicite_gs

    results.cout_commercial_total = (
        results.cout_promotion + results.cout_vendeurs + results.cout_publicite
    )

    # =========================================================================
    # 7. COÛT DES ÉTUDES
    # =========================================================================
    results.cout_etudes = calculate_study_costs(
        decisions.marketing.etudes_abcd, decisions.marketing.etudes_efgh
    )

    # =========================================================================
    # 8. PRIX NETS ET CA POTENTIEL
    # =========================================================================
    # Prix nets (après ristourne pour GS)
    results.prix_net_a_ct = decisions.produit_a_ct.prix_tarif
    results.prix_net_a_gs = decisions.produit_a_gs.prix_tarif * (
        1 - decisions.produit_a_gs.ristourne / 100
    )
    results.prix_net_b_ct = decisions.produit_b_ct.prix_tarif
    results.prix_net_b_gs = decisions.produit_b_gs.prix_tarif * (
        1 - decisions.produit_b_gs.ristourne / 100
    )
    results.prix_net_c_ct = decisions.produit_c_ct.prix_tarif
    results.prix_net_c_gs = decisions.produit_c_gs.prix_tarif * (
        1 - decisions.produit_c_gs.ristourne / 100
    )

    # Stocks disponibles à la vente (stock initial + production)
    results.stock_dispo_a_ct = state.stock_a_ct + prod_a_ct
    results.stock_dispo_a_gs = state.stock_a_gs + prod_a_gs
    results.stock_dispo_b_ct = state.stock_b_ct + prod_b_ct
    results.stock_dispo_b_gs = state.stock_b_gs + prod_b_gs
    results.stock_dispo_c_ct = state.stock_c_ct + prod_c_ct
    results.stock_dispo_c_gs = state.stock_c_gs + prod_c_gs

    # CA potentiel (si tout vendu)
    results.ca_potentiel_a_ct = results.stock_dispo_a_ct * results.prix_net_a_ct / 1000
    results.ca_potentiel_a_gs = results.stock_dispo_a_gs * results.prix_net_a_gs / 1000
    results.ca_potentiel_b_ct = results.stock_dispo_b_ct * results.prix_net_b_ct / 1000
    results.ca_potentiel_b_gs = results.stock_dispo_b_gs * results.prix_net_b_gs / 1000
    results.ca_potentiel_c_ct = results.stock_dispo_c_ct * results.prix_net_c_ct / 1000
    results.ca_potentiel_c_gs = results.stock_dispo_c_gs * results.prix_net_c_gs / 1000

    results.ca_potentiel_total = (
        results.ca_potentiel_a_ct
        + results.ca_potentiel_a_gs
        + results.ca_potentiel_b_ct
        + results.ca_potentiel_b_gs
        + results.ca_potentiel_c_ct
        + results.ca_potentiel_c_gs
    )

    # =========================================================================
    # 9. CASH FLOWS ESTIMÉS
    # =========================================================================
    # Décaissements
    results.decaissements_mp = results.cout_mp * 1.2  # Avec TVA
    results.decaissements_personnel = results.cout_main_oeuvre + results.cout_vendeurs
    results.decaissements_investissements = (
        decisions.production.achats_m1 * C.M1_PURCHASE_PRICE
        + decisions.production.achats_m2 * C.M2_PURCHASE_PRICE
    )

    # Autres décaissements
    results.decaissements_autres = (
        results.cout_publicite
        + results.cout_etudes
        + decisions.finance.dividendes
        + decisions.rse.budget_recyclage
        + decisions.rse.amenagements_adaptes
        + decisions.rse.recherche_dev
    )

    results.decaissements_total = (
        results.decaissements_mp
        + results.decaissements_personnel
        + results.decaissements_investissements
        + results.decaissements_autres
    )

    # Encaissements
    # Ventes machines
    ventes_machines = decisions.production.ventes_m1 * C.M1_PURCHASE_PRICE * C.M1_RESALE_PRICE_RATIO

    # Emprunts
    results.encaissements_emprunts = decisions.finance.emprunt_lt + decisions.finance.emprunt_ct

    # Ventes estimées (hypothèse: 70% du CA potentiel encaissé dans la période)
    results.encaissements_ventes_estimees = results.ca_potentiel_total * 0.7

    results.encaissements_total = (
        results.encaissements_ventes_estimees
        + results.encaissements_emprunts
        + ventes_machines
    )

    # Trésorerie estimée
    results.tresorerie_estimee = (
        state.cash + results.encaissements_total - results.decaissements_total
    )

    if results.tresorerie_estimee < 0:
        results.warnings.append(
            f"⚠️ Trésorerie estimée négative: {results.tresorerie_estimee:,.0f} K€"
        )

    return results

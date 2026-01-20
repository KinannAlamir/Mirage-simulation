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


def calculate_all(decisions: AllDecisions, state: PeriodState, forecast_sales: dict[str, int] = None) -> CalculatedResults:
    """Calcule tous les résultats à partir des décisions et de l'état actuel.
    
    Args:
        decisions: Les décisions prises pour le tour.
        state: L'état du système en début de tour.
        forecast_sales: Dictionnaire optionnel contenant les prévisions de vente (en unités) 
                        pour chaque produit ('A-CT', 'A-GS', etc.) afin d'ajuster le CA prévisionnel.
    """
    results = CalculatedResults()
    results.warnings = []

    # =========================================================================
    # 1. CAPACITÉ DE PRODUCTION & MACHINES
    # =========================================================================
    # Machines actives limitées par le parc machine existant en début de période (lag 1 tour)
    m1_active = min(decisions.production.machines_m1_actives, state.nb_machines_m1)
    m2_active = min(decisions.production.machines_m2_actives, state.nb_machines_m2)

    if m1_active < decisions.production.machines_m1_actives:
        results.warnings.append(
            f"⚠️ Machines M1 actives limitées à {m1_active} (parc disponible début période)."
        )
    if m2_active < decisions.production.machines_m2_actives:
        results.warnings.append(
            f"⚠️ Machines M2 actives limitées à {m2_active} (parc disponible début période)."
        )
    
    # Facteur de productivité lié à la maintenance
    productivity_factor = 1.0
    if not decisions.approvisionnement.maintenance:
        productivity_factor = 1.0 - C.MACHINE_PRODUCTIVITY_LOSS
        results.warnings.append(f"⚠️ Pas de maintenance: Perte de {C.MACHINE_PRODUCTIVITY_LOSS*100:.0f}% de productivité sur les machines.")

    results.capacite_m1_a = m1_active * C.M1_CAPACITY_A * productivity_factor
    results.capacite_m1_b = m1_active * C.M1_CAPACITY_B * productivity_factor
    results.capacite_m1_c = m1_active * C.M1_CAPACITY_C * productivity_factor

    results.capacite_m2_a = m2_active * C.M2_CAPACITY_A * productivity_factor
    results.capacite_m2_b = m2_active * C.M2_CAPACITY_B * productivity_factor
    results.capacite_m2_c = m2_active * C.M2_CAPACITY_C * productivity_factor

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

    # Vérifier capacité (approximative en équivalent A)
    capacite_equivalent = results.capacite_totale_a
    # C prend environ 2x plus de temps que A sur M1 (45700 vs 22850)
    production_equivalent = total_prod_a + total_prod_b + (total_prod_c * 2)

    if production_equivalent > capacite_equivalent:
        results.warnings.append(
            f"⚠️ Production demandée ({production_equivalent:,.0f} eq.) dépasse la capacité ({capacite_equivalent:,.0f} eq.)"
        )

    # =========================================================================
    # 3. BESOINS EN MATIÈRES PREMIÈRES
    # =========================================================================
    mp_a_ct = prod_a_ct * C.UNITS_MP_PER_UNIT_A
    mp_a_gs = prod_a_gs * C.UNITS_MP_PER_UNIT_A
    mp_b_ct = prod_b_ct * C.UNITS_MP_PER_UNIT_B
    mp_b_gs = prod_b_gs * C.UNITS_MP_PER_UNIT_B
    mp_c_ct = prod_c_ct * C.UNITS_MP_PER_UNIT_C
    mp_c_gs = prod_c_gs * C.UNITS_MP_PER_UNIT_C

    # Répartition N/S selon qualité
    mp_n_needed = 0
    mp_s_needed = 0

    def add_mp_needs(qty_mp, qualite):
        nonlocal mp_n_needed, mp_s_needed
        # Répartition proportionnelle à la qualité
        # Qualité 100 => 100% N, 0% S
        # Qualité 50 => 50% N, 50% S
        # Qualité 0 => 0% N, 100% S
        ratio_n = qualite / 100.0
        ratio_s = 1.0 - ratio_n
        
        mp_n_needed += qty_mp * ratio_n
        mp_s_needed += qty_mp * ratio_s

    add_mp_needs(mp_a_ct, decisions.produit_a_ct.qualite)
    add_mp_needs(mp_a_gs, decisions.produit_a_gs.qualite)
    add_mp_needs(mp_b_ct, decisions.produit_b_ct.qualite)
    add_mp_needs(mp_b_gs, decisions.produit_b_gs.qualite)
    add_mp_needs(mp_c_ct, decisions.produit_c_ct.qualite)
    add_mp_needs(mp_c_gs, decisions.produit_c_gs.qualite)

    results.mp_n_necessaire = int(mp_n_needed)
    results.mp_s_necessaire = int(mp_s_needed)

    # MP disponibles
    results.mp_n_disponible = state.stock_mp_n + (
        decisions.approvisionnement.commandes_mp_n * 1000
        if decisions.approvisionnement.duree_contrat_n > 0
        else 0
    ) + (decisions.approvisionnement.achat_spot_n * 1000)

    results.mp_s_disponible = state.stock_mp_s + (
        decisions.approvisionnement.commandes_mp_s * 1000
        if decisions.approvisionnement.duree_contrat_s > 0
        else 0
    ) + (decisions.approvisionnement.achat_spot_s * 1000)

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
    # 4. BESOINS EN OUVRIERS (Avec Absentéisme)
    # =========================================================================
    results.ouvriers_necessaires = (
        m1_active * C.WORKERS_PER_M1 + m2_active * C.WORKERS_PER_M2
    )
    
    # Total ouvriers sous contrat (Permanents)
    # Départs à la retraite (Début de trimestre)
    # Règle : 20 personnes partent 1 trimestre sur 2, en commençant à P1.
    # P1 : -20 (Total cumulé -20)
    # P2 : 0 (Total cumulé -20)
    # P3 : -20 (Total cumulé -40)
    # P4 : 0 (Total cumulé -40)
    
    nb_retraites_current = 20 if (state.period_num % 2 != 0) else 0
    
    nb_retraites_past = 0
    if state.period_num >= 2:
        nb_retraites_past += 20 # Depart de P1
    if state.period_num >= 4:
        nb_retraites_past += 20 # Depart de P3 (Si on est en P4)
        
    # Note: Si on est en P3, current=20 et past=20 (Celui de P1). Total = 40.
    
    nb_retraites_total = nb_retraites_current + nb_retraites_past

    if nb_retraites_current > 0:
        results.warnings.append(f"ℹ️ Départ en retraite de {nb_retraites_current} ouvriers ce trimestre.")
    if nb_retraites_past > 0:
        results.warnings.append(f"ℹ️ Effet cumulé retraites passées : -{nb_retraites_past} ouvriers.")
    
    total_permanents = state.nb_ouvriers + decisions.production.emb_deb_ouvriers - nb_retraites_total
    
    # Calc absenteisme
    taux_absenteisme = C.ABSENTEEISM_RATES.get(state.period_num, 0.0)
    nb_absents = int(total_permanents * taux_absenteisme)

    # 200 ouvriers sont affectés à l'atelier M en permanence et ne produisent pas sur M1/M2
    NB_OUVRIERS_ATELIER_M = 200
    
    # Ouvriers réellement présents pour travailler sur M1/M2
    # On retire les absents et ceux de l'atelier M
    results.ouvriers_disponibles = total_permanents - nb_absents - NB_OUVRIERS_ATELIER_M
    
    results.variation_ouvriers = decisions.production.emb_deb_ouvriers
    
    nb_saisonniers = 0
    nb_chomage = 0
    
    # Besoin vs Présents
    if results.ouvriers_necessaires > results.ouvriers_disponibles:
        # On manque de bras présents -> Saisonniers
        nb_saisonniers = results.ouvriers_necessaires - results.ouvriers_disponibles
        results.warnings.append(f"ℹ️ Recours à {nb_saisonniers} saisonniers (Dont couverture de {nb_absents} absents + {NB_OUVRIERS_ATELIER_M} atelier M)")
    else:
        # Trop de présents -> Chômage technique
        nb_chomage = results.ouvriers_disponibles - results.ouvriers_necessaires
        if nb_absents > 0:
            results.warnings.append(f"ℹ️ {nb_absents} ouvriers absents (Congés {taux_absenteisme*100}%)")
        if nb_chomage > 0:
            # On détaille le calcul pour rassurer l'utilisateur
            msg_detail = f"Dispo Prod ({total_permanents} tot - {nb_absents} abs - {NB_OUVRIERS_ATELIER_M} At.M = {results.ouvriers_disponibles}) - Besoin Machines {results.ouvriers_necessaires}"
            results.warnings.append(f"ℹ️ {nb_chomage} ouvriers en chômage technique ({msg_detail})")

    # =========================================================================
    # 5. COÛTS DE PRODUCTION
    # =========================================================================
    # Coût MP
    prix_mp_n = 0.80
    prix_mp_s = 0.70
    
    # --- Calcul détaillé Achats vs Conso MP ---
    
    # Achats (Pour Trésorerie)
    # Contrats (Prix Standard)
    qty_achat_contrat_n = (decisions.approvisionnement.commandes_mp_n * 1000 if decisions.approvisionnement.duree_contrat_n > 0 else 0)
    qty_achat_contrat_s = (decisions.approvisionnement.commandes_mp_s * 1000 if decisions.approvisionnement.duree_contrat_s > 0 else 0)
    
    cout_achats_contrat = (qty_achat_contrat_n * prix_mp_n + qty_achat_contrat_s * prix_mp_s) / 1000 # K€
    
    # Spot (Prix Standard)
    qty_achat_spot_n = decisions.approvisionnement.achat_spot_n * 1000
    qty_achat_spot_s = decisions.approvisionnement.achat_spot_s * 1000
    
    cout_achats_spot = (
        qty_achat_spot_n * prix_mp_n + 
        qty_achat_spot_s * prix_mp_s
    ) / 1000

    # Consommation MP (Pour P&L)
    # Simplification : On valorise la consommation au prix standard.
    
    results.cout_mp = (results.mp_n_necessaire * prix_mp_n + results.mp_s_necessaire * prix_mp_s) / 1000  # K€ (Standard)
    
    # Paramètres de base (Indexation) - Définis tôt pour usage dans calculs variables (Energie, etc)
    indice_salaire_ratio = state.indice_salaire / 100.0
    indice_prix_ratio = state.indice_prix / 100.0

    # --- Energie, Sous-traitance, Variables divers (Production) ---
    total_prod_units = total_prod_a + total_prod_b + total_prod_c
    
    # Energie Atelier (Fonction prod, indexé IGP)
    # ENERGY_COST_PER_UNIT est en €/u (ex: 1.00), total_prod_units en U. Résultat en € -> /1000 pour K€
    results.cout_energie = (total_prod_units * C.ENERGY_COST_PER_UNIT * indice_prix_ratio) / 1000.0
    
    # Sous-traitance / Conditionnement (indexé IGP)
    results.cout_sous_traitance = (total_prod_units * C.SUBCONTRACTING_PACKAGING_COST * indice_prix_ratio) / 1000.0
    
    # Autres charges variables production (Dépenses atelier, indexé IGP)
    cout_variable_divers = (total_prod_units * C.VARIABLE_MFG_COST_PER_UNIT * indice_prix_ratio) / 1000.0

    # --- FRAIS DE PERSONNEL (PRODUCTION & STRUCTURE) ---
    # (Indices déjà définis plus haut)

    # Salaire de base ouvrier indexé
    salaire_base_h = C.WORKER_BASE_SALARY * indice_salaire_ratio
    
    # 1. PERSONNEL OUVRIER (PRODUCTION + STRUCTURE)
    # ---------------------------------------------
    
    nb_chomeurs = max(0, results.ouvriers_disponibles - results.ouvriers_necessaires)
    nb_actifs_permanents = total_permanents - nb_chomeurs # Inclus Atelier M (200) + Absents car ils sont payés "plein pot" administrativement
    
    # Masse Salariale Permanents
    masse_salariale_permanents = (nb_actifs_permanents * salaire_base_h * 3) + (nb_chomeurs * salaire_base_h * 3 * C.TECHNICAL_UNEMPLOYMENT_RATE)
    
    # Salaire Saisonniers
    masse_salariale_saisonniers = nb_saisonniers * salaire_base_h * 3 * C.SEASONAL_WORKER_COST_MULTIPLIER
    
    # Sous-total Salaires Ouvriers (Brut)
    salaires_bruts_ouvriers = masse_salariale_permanents + masse_salariale_saisonniers
    
    # 2. ENCADREMENT & ADMINISTRATIF (STRUCTURE FIXE)
    # ----------------------------------------------
    # Salaires fixes indexés sur l'indice SALAIRE
    salaire_fixe_ventes = C.FIXED_SALARY_MANAGEMENT_SALES * indice_salaire_ratio
    salaire_fixe_prod = C.FIXED_SALARY_MANAGEMENT_PROD * indice_salaire_ratio
    salaire_fixe_admin = C.FIXED_SALARY_ADMIN * indice_salaire_ratio
    
    # 3. FORCE DE VENTE (SALAIRES FIXES + COMMISSIONS)
    # ------------------------------------------------
    salaire_vendeur_ct = C.TO_SALESPERSON_SALARY * indice_salaire_ratio
    salaire_vendeur_gs = C.MR_SALESPERSON_SALARY * indice_salaire_ratio
    
    # Fixe Vendeurs
    fixe_vendeurs_ct = decisions.marketing.vendeurs_ct * salaire_vendeur_ct * 3
    fixe_vendeurs_gs = decisions.marketing.vendeurs_gs * salaire_vendeur_gs * 3
    
    # Commissions & Primes
    ca_ht_a_ct = (state.stock_a_ct + prod_a_ct) * decisions.produit_a_ct.prix_tarif
    ca_ht_b_ct = (state.stock_b_ct + prod_b_ct) * decisions.produit_b_ct.prix_tarif
    ca_ht_c_ct = (state.stock_c_ct + prod_c_ct) * decisions.produit_c_ct.prix_tarif
    ca_total_ct = ca_ht_a_ct + ca_ht_b_ct + ca_ht_c_ct
    
    commissions_ct = ca_total_ct * (decisions.marketing.commission_ct / 100)
    primes_gs = decisions.marketing.vendeurs_gs * decisions.marketing.prime_trimestre_gs
    
    masse_salariale_vendeurs = fixe_vendeurs_ct + fixe_vendeurs_gs + commissions_ct + primes_gs
    
    # 4. SOMME DES SALAIRES BRUTS & CHARGES
    # -------------------------------------
    salaires_bruts_totaux = (
        salaires_bruts_ouvriers +
        salaire_fixe_prod +
        salaire_fixe_admin +
        salaire_fixe_ventes +
        masse_salariale_vendeurs
    )
    
    charges_patronales = salaires_bruts_totaux * C.SOCIAL_CHARGES_RATE
    
    # 5. PROVISIONS POUR CONGÉS PAYÉS
    # -------------------------------
    masse_totale_chargee = salaires_bruts_totaux + charges_patronales
    dotation_conges = masse_totale_chargee * C.VACATION_PROVISION_RATE
    
    cout_personnel_total_charge = masse_totale_chargee + dotation_conges

    # 6. RÉPARTITION ANALYTIQUE (Pour affichage correct dans les rubriques)
    # ---------------------------------------------------------------------
    # Production : Ouvriers + Encadrement Prod
    part_ouvriers_chargee = (salaires_bruts_ouvriers * (1 + C.SOCIAL_CHARGES_RATE)) * (1 + C.VACATION_PROVISION_RATE)
    part_encadrement_prod_chargee = (salaire_fixe_prod * (1 + C.SOCIAL_CHARGES_RATE)) * (1 + C.VACATION_PROVISION_RATE)
    results.cout_main_oeuvre = (part_ouvriers_chargee + part_encadrement_prod_chargee) / 1000 # K€
    
    # Commercial : Vendeurs + Encadrement Vente
    part_vendeurs_chargee = (masse_salariale_vendeurs * (1 + C.SOCIAL_CHARGES_RATE)) * (1 + C.VACATION_PROVISION_RATE)
    part_encadrement_vente_chargee = (salaire_fixe_ventes * (1 + C.SOCIAL_CHARGES_RATE)) * (1 + C.VACATION_PROVISION_RATE)
    results.cout_vendeurs = (part_vendeurs_chargee + part_encadrement_vente_chargee) / 1000 # K€
    
    # Structure / Admin : Direction + Admin
    part_admin_chargee = (salaire_fixe_admin * (1 + C.SOCIAL_CHARGES_RATE)) * (1 + C.VACATION_PROVISION_RATE)
    results.cout_structure_admin = part_admin_chargee / 1000


    # Amortissement machines
    depreciation_m1 = m1_active * C.M1_PURCHASE_PRICE / (C.M1_DEPRECIATION_YEARS * 4)
    depreciation_m2 = m2_active * C.M2_PURCHASE_PRICE / (C.M2_DEPRECIATION_YEARS * 4)
    results.cout_amortissement = depreciation_m1 + depreciation_m2

    # Amortissement Bâtiments (Admin)
    results.dotation_amort_immeuble = C.ADMIN_BUILDING_VALUE * C.ADMIN_AMORTIZATION_RATE
    
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
        + results.cout_energie
        + results.cout_sous_traitance
        + cout_variable_divers
    )

    # Coût d'embauche
    cout_embauche_ouvriers = 0.0
    if decisions.production.emb_deb_ouvriers > 0:
        cout_unit_ouvrier = C.HIRING_COST_PER_WORKER * indice_prix_ratio
        cout_embauche_ouvriers = decisions.production.emb_deb_ouvriers * cout_unit_ouvrier
        
    results.cout_embauche = cout_embauche_ouvriers / 1000.0  # En K€
    
    # Frais de Déplacement (Indexé sur Indice Prix)
    frais_mission_vendeurs = (decisions.marketing.vendeurs_ct + decisions.marketing.vendeurs_gs) * C.MISSION_COST_PER_SALESPERSON * indice_prix_ratio
    frais_mission_autres = C.MISSION_COST_GLOBAL_OTHERS * indice_prix_ratio
    
    results.cout_frais_deplacement = (frais_mission_vendeurs + frais_mission_autres) / 1000

    # =========================================================================
    # 6. COÛTS COMMERCIAUX
    # =========================================================================
    
    # Transport sur Ventes
    # Estimation volume ventes total (Dispo) pour transport
    # On transporte ce qu'on vend -> On utilise le forecast/potentiel limité par dispo
    
    vol_a_ct_est = min(state.stock_a_ct + prod_a_ct, decisions.produit_a_ct.ventes_contrat + decisions.produit_a_ct.ventes_contrat ) # Simplified placeholder, real calculation is below with stock logic
    
    # Publicité, Promo... (Déjà existant)
    # Promotion
    promo_a_ct = decisions.produit_a_ct.promotion * prod_a_ct / 1000
    promo_a_gs = decisions.produit_a_gs.promotion * prod_a_gs / 1000
    promo_b_ct = decisions.produit_b_ct.promotion * prod_b_ct / 1000
    promo_b_gs = decisions.produit_b_gs.promotion * prod_b_gs / 1000
    promo_c_ct = decisions.produit_c_ct.promotion * prod_c_ct / 1000
    promo_c_gs = decisions.produit_c_gs.promotion * prod_c_gs / 1000
    results.cout_promotion = promo_a_ct + promo_a_gs + promo_b_ct + promo_b_gs + promo_c_ct + promo_c_gs
    
    results.cout_publicite = decisions.marketing.publicite_ct + decisions.marketing.publicite_gs

    # Stocks & Ruptures (Existant)
    # ... (Copier logique Rupture)
    def check_rupture_and_stock(stock_init, prod_u, achat_u, vente_u, name, price):
        dispo_total = stock_init + prod_u + achat_u
        manque = vente_u - dispo_total
        cout_penalite = 0.0
        if manque > 0:
            cout_penalite = manque * price * C.STOCKOUT_PENALTY_RATE / 1000
            if cout_penalite > 0:
                results.warnings.append(f"⚠️ Rupture contrat {name} -> Pénalité {cout_penalite:.1f} K€")
            stock_dispo = 0
        else:
            stock_dispo = dispo_total - vente_u
        return stock_dispo, cout_penalite

    cout_rupture_total = 0.0
    max_price = max(
        decisions.produit_a_ct.prix_tarif, decisions.produit_a_gs.prix_tarif,
        decisions.produit_b_ct.prix_tarif, decisions.produit_b_gs.prix_tarif,
        decisions.produit_c_ct.prix_tarif, decisions.produit_c_gs.prix_tarif
    )

    results.stock_dispo_a_ct, c_r = check_rupture_and_stock(state.stock_a_ct, prod_a_ct, decisions.produit_a_ct.achats_contrat, decisions.produit_a_ct.ventes_contrat, "A-CT", max_price)
    cout_rupture_total += c_r
    results.stock_dispo_a_gs, c_r = check_rupture_and_stock(state.stock_a_gs, prod_a_gs, decisions.produit_a_gs.achats_contrat, decisions.produit_a_gs.ventes_contrat, "A-GS", max_price)
    cout_rupture_total += c_r
    
    results.stock_dispo_b_ct, c_r = check_rupture_and_stock(state.stock_b_ct, prod_b_ct, decisions.produit_b_ct.achats_contrat, decisions.produit_b_ct.ventes_contrat, "B-CT", max_price)
    cout_rupture_total += c_r
    results.stock_dispo_b_gs, c_r = check_rupture_and_stock(state.stock_b_gs, prod_b_gs, decisions.produit_b_gs.achats_contrat, decisions.produit_b_gs.ventes_contrat, "B-GS", max_price)
    cout_rupture_total += c_r
    
    results.stock_dispo_c_ct, c_r = check_rupture_and_stock(state.stock_c_ct, prod_c_ct, decisions.produit_c_ct.achats_contrat, decisions.produit_c_ct.ventes_contrat, "C-CT", max_price)
    cout_rupture_total += c_r
    results.stock_dispo_c_gs, c_r = check_rupture_and_stock(state.stock_c_gs, prod_c_gs, decisions.produit_c_gs.achats_contrat, decisions.produit_c_gs.ventes_contrat, "C-GS", max_price)
    cout_rupture_total += c_r
    
    # Transport (Calculé post-stocks pour volume réel vendu estimé)
    # On utilise le CA Potentiel pour estimer le volume vendu
    # Mais ici on a besoin des volumes avant CA pour le transport
    # On va utiliser les Dispo comme "Ventes Max" pour le transport (meilleure estimation coût)
    # Volumes estimés vendus (Standard + Contrat)
    
    def estimate_sales_vol(forecast_dict, code, dispo):
        if forecast_dict and code in forecast_dict:
            return min(dispo, float(forecast_dict[code]))
        return dispo

    vol_a_ct_vendu = estimate_sales_vol(forecast_sales, "A-CT", results.stock_dispo_a_ct) + decisions.produit_a_ct.ventes_contrat # Contrat supposé servi sauf rupture (déjà géré pénalité)
    vol_a_gs_vendu = estimate_sales_vol(forecast_sales, "A-GS", results.stock_dispo_a_gs) + decisions.produit_a_gs.ventes_contrat
    
    vol_b_ct_vendu = estimate_sales_vol(forecast_sales, "B-CT", results.stock_dispo_b_ct) + decisions.produit_b_ct.ventes_contrat
    vol_b_gs_vendu = estimate_sales_vol(forecast_sales, "B-GS", results.stock_dispo_b_gs) + decisions.produit_b_gs.ventes_contrat
    
    vol_c_ct_vendu = estimate_sales_vol(forecast_sales, "C-CT", results.stock_dispo_c_ct) + decisions.produit_c_ct.ventes_contrat
    vol_c_gs_vendu = estimate_sales_vol(forecast_sales, "C-GS", results.stock_dispo_c_gs) + decisions.produit_c_gs.ventes_contrat
    
    total_vol_ct = vol_a_ct_vendu + vol_b_ct_vendu + vol_c_ct_vendu
    total_vol_gs = vol_a_gs_vendu + vol_b_gs_vendu + vol_c_gs_vendu
    
    # Transport indexé sur IGP
    results.cout_transport = (total_vol_ct * C.TRANSPORT_COST_CT_PER_UNIT * indice_prix_ratio + total_vol_gs * C.TRANSPORT_COST_GS_PER_UNIT * indice_prix_ratio) / 1000.0

    results.cout_commercial_total = (
        results.cout_promotion + results.cout_vendeurs + results.cout_publicite + results.cout_transport + results.cout_frais_deplacement
    )

    # 7. COÛT DES ÉTUDES
    results.cout_etudes = calculate_study_costs(
        decisions.marketing.etudes_abcd, decisions.marketing.etudes_efgh
    )

    # =========================================================================
    # 8. FRAIS DE STRUCTURE ET DIVERS
    # =========================================================================
    
    results.cout_energie_generale = C.GENERAL_SERVICES_ENERGY_COST * indice_prix_ratio / 1000.0
    # Cumul Honoraires + Frais Gestion
    results.cout_frais_gestion_divers = (C.MISC_MANAGEMENT_FEES + C.FEES_AND_HONORARIUMS) * indice_prix_ratio / 1000.0
    results.cout_impots_taxes = C.OTHER_TAXES_INFLATION_BASE * indice_prix_ratio / 1000.0
    
    results.total_frais_generaux = (
        results.cout_structure_admin +
        results.dotation_amort_immeuble +
        results.cout_energie_generale +
        results.cout_frais_gestion_divers +
        results.cout_impots_taxes +
        results.cout_etudes +
        results.cout_embauche # Embauche est souvent en frais généraux ou exceptionnel, ici Structure
    )

    # =========================================================================
    # 9. PRIX NETS ET CA POTENTIEL
    # =========================================================================
    # Prix nets
    results.prix_net_a_ct = decisions.produit_a_ct.prix_tarif
    results.prix_net_a_gs = decisions.produit_a_gs.prix_tarif * (1 - decisions.produit_a_gs.ristourne / 100)
    results.prix_net_b_ct = decisions.produit_b_ct.prix_tarif
    results.prix_net_b_gs = decisions.produit_b_gs.prix_tarif * (1 - decisions.produit_b_gs.ristourne / 100)
    results.prix_net_c_ct = decisions.produit_c_ct.prix_tarif
    results.prix_net_c_gs = decisions.produit_c_gs.prix_tarif * (1 - decisions.produit_c_gs.ristourne / 100)
    
    # Vols Standard (Limit par dispo)
    vol_a_ct_std = estimate_sales_vol(forecast_sales, "A-CT", results.stock_dispo_a_ct)
    vol_a_gs_std = estimate_sales_vol(forecast_sales, "A-GS", results.stock_dispo_a_gs)
    vol_b_ct_std = estimate_sales_vol(forecast_sales, "B-CT", results.stock_dispo_b_ct)
    vol_b_gs_std = estimate_sales_vol(forecast_sales, "B-GS", results.stock_dispo_b_gs)
    vol_c_ct_std = estimate_sales_vol(forecast_sales, "C-CT", results.stock_dispo_c_ct)
    vol_c_gs_std = estimate_sales_vol(forecast_sales, "C-GS", results.stock_dispo_c_gs)
    
    # CA Standard
    results.ca_potentiel_a_ct = vol_a_ct_std * results.prix_net_a_ct / 1000
    results.ca_potentiel_a_gs = vol_a_gs_std * results.prix_net_a_gs / 1000
    results.ca_potentiel_b_ct = vol_b_ct_std * results.prix_net_b_ct / 1000
    results.ca_potentiel_b_gs = vol_b_gs_std * results.prix_net_b_gs / 1000
    results.ca_potentiel_c_ct = vol_c_ct_std * results.prix_net_c_ct / 1000
    results.ca_potentiel_c_gs = vol_c_gs_std * results.prix_net_c_gs / 1000
    
    # Définition de la fonction pour CA Contrat avec vérification stock
    def get_ca_contrat(vente_contrat, stock_init, prod_u, achat_u, prix_net):
        dispo = stock_init + prod_u + achat_u
        vendu = min(vente_contrat, dispo)
        return vendu * prix_net / 1000 # K€

    # Calcul CA Contrats
    results.ca_contrats = 0.0
    results.ca_contrats += get_ca_contrat(decisions.produit_a_ct.ventes_contrat, state.stock_a_ct, prod_a_ct, decisions.produit_a_ct.achats_contrat, results.prix_net_a_ct)
    results.ca_contrats += get_ca_contrat(decisions.produit_a_gs.ventes_contrat, state.stock_a_gs, prod_a_gs, decisions.produit_a_gs.achats_contrat, results.prix_net_a_gs)
    results.ca_contrats += get_ca_contrat(decisions.produit_b_ct.ventes_contrat, state.stock_b_ct, prod_b_ct, decisions.produit_b_ct.achats_contrat, results.prix_net_b_ct)
    results.ca_contrats += get_ca_contrat(decisions.produit_b_gs.ventes_contrat, state.stock_b_gs, prod_b_gs, decisions.produit_b_gs.achats_contrat, results.prix_net_b_gs)
    results.ca_contrats += get_ca_contrat(decisions.produit_c_ct.ventes_contrat, state.stock_c_ct, prod_c_ct, decisions.produit_c_ct.achats_contrat, results.prix_net_c_ct)
    results.ca_contrats += get_ca_contrat(decisions.produit_c_gs.ventes_contrat, state.stock_c_gs, prod_c_gs, decisions.produit_c_gs.achats_contrat, results.prix_net_c_gs)

    results.ca_potentiel_total = (
        results.ca_potentiel_a_ct + results.ca_potentiel_a_gs +
        results.ca_potentiel_b_ct + results.ca_potentiel_b_gs +
        results.ca_potentiel_c_ct + results.ca_potentiel_c_gs +
        results.ca_contrats
    )
    
    # Emballage Recyclé
    cout_emb_recycle = 0.0
    # Helper pour obtenir CA contrat d'un produit (simplif)
    def ca_cont_only(prod_decision, stock, prod_v, px):
        return get_ca_contrat(prod_decision.ventes_contrat, stock, prod_v, prod_decision.achats_contrat, px)

    if decisions.produit_a_ct.emballage_recycle: cout_emb_recycle += (results.ca_potentiel_a_ct + ca_cont_only(decisions.produit_a_ct, state.stock_a_ct, prod_a_ct, results.prix_net_a_ct)) * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_a_gs.emballage_recycle: cout_emb_recycle += (results.ca_potentiel_a_gs + ca_cont_only(decisions.produit_a_gs, state.stock_a_gs, prod_a_gs, results.prix_net_a_gs)) * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_b_ct.emballage_recycle: cout_emb_recycle += (results.ca_potentiel_b_ct + ca_cont_only(decisions.produit_b_ct, state.stock_b_ct, prod_b_ct, results.prix_net_b_ct)) * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_b_gs.emballage_recycle: cout_emb_recycle += (results.ca_potentiel_b_gs + ca_cont_only(decisions.produit_b_gs, state.stock_b_gs, prod_b_gs, results.prix_net_b_gs)) * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_c_ct.emballage_recycle: cout_emb_recycle += (results.ca_potentiel_c_ct + ca_cont_only(decisions.produit_c_ct, state.stock_c_ct, prod_c_ct, results.prix_net_c_ct)) * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_c_gs.emballage_recycle: cout_emb_recycle += (results.ca_potentiel_c_gs + ca_cont_only(decisions.produit_c_gs, state.stock_c_gs, prod_c_gs, results.prix_net_c_gs)) * C.RECYCLED_PACKAGING_ROYALTY_RATE

    results.cout_commercial_total += cout_emb_recycle

    # =========================================================================
    # VARIATION DE STOCKS (Valorisation pour Résultat Exploitation)
    # =========================================================================
    
    # Calcul Coût Prod GLOBAL (MP+MO+Energie+SousTrait+AmortMachine+Maint+VarDivers)
    charges_prod_totales = results.cout_production_total
    
    # Répartition par unité équivalente A
    total_equiv_a = total_prod_a + total_prod_b + (total_prod_c * 2)
    cout_unit_moyen_eq_a = (charges_prod_totales / total_equiv_a) if total_equiv_a > 0 else 0
    
    # Coût unitaire par produit
    up_a = cout_unit_moyen_eq_a
    up_b = cout_unit_moyen_eq_a
    up_c = cout_unit_moyen_eq_a * 2
    
    # Calcul Total Ventes (Unités)
    # Standard: vol_x_std calculé plus haut
    # Contrat: on recalcul les unités
    def get_vendu_contrat_u(vente_contrat, stock_init, prod_u, achat_u):
        dispo = stock_init + prod_u + achat_u
        return min(vente_contrat, dispo)
        
    u_cont_a_ct = get_vendu_contrat_u(decisions.produit_a_ct.ventes_contrat, state.stock_a_ct, prod_a_ct, decisions.produit_a_ct.achats_contrat)
    u_cont_a_gs = get_vendu_contrat_u(decisions.produit_a_gs.ventes_contrat, state.stock_a_gs, prod_a_gs, decisions.produit_a_gs.achats_contrat)
    u_cont_b_ct = get_vendu_contrat_u(decisions.produit_b_ct.ventes_contrat, state.stock_b_ct, prod_b_ct, decisions.produit_b_ct.achats_contrat)
    u_cont_b_gs = get_vendu_contrat_u(decisions.produit_b_gs.ventes_contrat, state.stock_b_gs, prod_b_gs, decisions.produit_b_gs.achats_contrat)
    u_cont_c_ct = get_vendu_contrat_u(decisions.produit_c_ct.ventes_contrat, state.stock_c_ct, prod_c_ct, decisions.produit_c_ct.achats_contrat)
    u_cont_c_gs = get_vendu_contrat_u(decisions.produit_c_gs.ventes_contrat, state.stock_c_gs, prod_c_gs, decisions.produit_c_gs.achats_contrat)

    total_sales_a = vol_a_ct_std + vol_a_gs_std + u_cont_a_ct + u_cont_a_gs
    total_sales_b = vol_b_ct_std + vol_b_gs_std + u_cont_b_ct + u_cont_b_gs
    total_sales_c = vol_c_ct_std + vol_c_gs_std + u_cont_c_ct + u_cont_c_gs

    # Disponibilité Initiale Totale (Avant Vente)
    total_dispo_a = (state.stock_a_ct + state.stock_a_gs) + total_prod_a + (decisions.produit_a_ct.achats_contrat + decisions.produit_a_gs.achats_contrat)
    total_dispo_b = (state.stock_b_ct + state.stock_b_gs) + total_prod_b + (decisions.produit_b_ct.achats_contrat + decisions.produit_b_gs.achats_contrat)
    total_dispo_c = (state.stock_c_ct + state.stock_c_gs) + total_prod_c + (decisions.produit_c_ct.achats_contrat + decisions.produit_c_gs.achats_contrat)
    
    # Variations Stocks Physiques
    stock_init_u_a = state.stock_a_ct + state.stock_a_gs
    stock_fin_u_a = max(0, total_dispo_a - total_sales_a)
    var_u_a = stock_fin_u_a - stock_init_u_a
    
    stock_init_u_b = state.stock_b_ct + state.stock_b_gs
    stock_fin_u_b = max(0, total_dispo_b - total_sales_b)
    var_u_b = stock_fin_u_b - stock_init_u_b
    
    stock_init_u_c = state.stock_c_ct + state.stock_c_gs
    stock_fin_u_c = max(0, total_dispo_c - total_sales_c)
    var_u_c = stock_fin_u_c - stock_init_u_c
    
    # Variation Valeur P&L (= Stock Fin * CU - Stock Init * CU_Prec)
    # On assume CU stable ou CU courant pour simplicité
    results.valeur_variation_stocks = (var_u_a * up_a + var_u_b * up_b + var_u_c * up_c)/1000 # K€
    
    
    # =========================================================================
    # 10. RESULTAT D'EXPLOITATION
    # =========================================================================
    # Produits Exploitation = CA + Variation Stock (Si positive) + Prod Immobilisée (0) + Subventions (0)
    # Charges Exploitation = Achats + Var Stock (Si négative) + Charges externes + Impots + Personnel...
    
    # Basé sur le manuel "Income Statement":
    # Profit = Total Revenues - Total Expenses
    # Total Revenues = Sales (excl tax) + Inventory Variation + Financial Revenues (excl here) + Exceptional Revenues (excl here)
    # Total Expenses = RM Used + Other Expenses + Taxes + Personnel + Depreciation + Financial Exp (excl) + Excep Exp (excl) + Income Tax (excl)
    
    # Re-calculons les charges d'exploitation selon le manuel (rubrique "Expenses")
    # 1. Raw Materials Used (Achats + Var Stock MP)
    # Dans notre modèle, cout_mp représente la conso valorisée au standard, c'est proche de RM Used.
    # Vérifions: achat_mp = 2400. Stock init = 1363. Stock fin = 1820. Var = +457. Conso = 2400 - 457 = 1943.
    # Notre results.cout_mp calcule: mp_necessaire * prix_standard.
    # Si stock valorisé au standard, c'est équivalent.
    
    # 2. Other Expenses (Services extérieurs A + B + Transport)
    charges_externes = (
        results.cout_energie +             # Energie
        results.cout_sous_traitance +      # Sous-traitance
        cout_variable_divers +             # Fournitures atelier ?
        results.cout_maintenance +         # Entretien
        results.cout_publicite +           # Publicité
        results.cout_promotion +           # Promotion
        results.cout_transport +           # Transport
        results.cout_frais_deplacement +   # Déplacements
        results.cout_energie_generale +    # Energie siège
        results.cout_frais_gestion_divers + # Honoraires + Divers gestion
        results.cout_etudes +              # Etudes
        cout_emb_recycle +                 # Redevance
        cout_rupture_total +               # Intégré souvent en charges divers ou moins de produits
        results.cout_impayes               # Pertes sur créances irrécouvrables
    )

    # 3. Taxes
    taxes_impots = results.cout_impots_taxes # Impots et taxes hors IS

    # 4. Personnel Expenses
    # Salaires + Charges + (Provision Congés - Reprise)
    # Notre calcul cout_main_oeuvre + cout_vendeurs + cout_structure_admin inclut déjà les charges et provision CP.
    charges_personnel = (
        results.cout_main_oeuvre + 
        results.cout_vendeurs + 
        results.cout_structure_admin +
        results.cout_embauche # Souvent en personnel ou frais divers
    )

    # 5. Depreciation
    dotations_amortissements = (
        results.cout_amortissement +       # Machines
        results.dotation_amort_immeuble    # Batiments
    )
    
    # Somme Charges Exploitation "Calculée"
    charges_exploitation_calc = (
        results.cout_mp +          # Raw Materials Used
        charges_externes +         # Other Expenses
        taxes_impots +             # Taxes
        charges_personnel +        # Personnel
        dotations_amortissements   # Depreciation
    )
    
    # Produits Exploitation
    products_exploitation = results.ca_potentiel_total
    
    # Résultat d'Exploitation (Operating Result)
    # Note: Dans le manuel, Operating Result = (Margin) - Admin Expenses...
    # Ou Income Statement: Profit Period = Revenues - Expenses.
    # Operating Result se trouve avant frais financiers.
    # Ajout de variation de stock produits finis
    # Income Statement dit: Sales + Inventory Variation.
    # Inventory Variation = Stock Fin - Stock Init (en valeur)
    # Notre results.valeur_variation_stocks fait exactement ça.
    
    results.resultat_exploitation = (products_exploitation + results.valeur_variation_stocks) - charges_exploitation_calc

    # =========================================================================
    # 11. RESULTAT FINANCIER
    # =========================================================================
    
    # Financial Revenues
    produits_financiers = 0.0 # VMP, etc. (Manual: 30)

    # Financial Expenses (Interets emprunts + Agios + Escomptes)
    # ...existing code...
    interets_emprunts = (state.dette_lt * C.LT_LOAN_RATE) + (state.dette_ct * C.ST_LOAN_RATE)
    
    # Agios
    flux_treso = results.resultat_exploitation + dotations_amortissements # Cash Flow approx brut exploitation
    
    # On garde le calcul existant pour agios qui est basé sur une estim de tréso
    # ...existing code...
    
    # Recalcul charges financières totales après le bloc existant d'agios
    # (On assume que le bloc existant est correct pour calculer cout_agios et cout_interets)
    # ...
    # Le bloc existant calcule déjà results.cout_charges_finance. On va juste s'assurer qu'il est cohérent.
    
    # On conserve le bloc existant pour le calcul des intérêts/agios, mais on met à jour le resultat courant
    
    # Recalcul de la Trésorerie prévisionnelle pour Agios (Simplifié)
    # Cash Flow = Resultat Exploit + Amortissements
    cash_flow_approx = results.resultat_exploitation + dotations_amortissements
    
    # Variation BFR (Simplifiée) = Variation Stock + Variation Clients - Variation Fournisseurs
    # On fait simple: Trésorerie Fin = Trésorerie Début + Cash Flow - Remboursement Emprunt - Dividendes - Investissements
    # C'est une approx pour les agios.
    
    treso_avant_fi = state.cash + cash_flow_approx
    
    # Decaissements investissements (M1/M2) - déjà calculés mais pas stockés dans results explicite ?
    # Si, decaissements_investissements a besoin d'être calculé
    cout_invest_m1 = decisions.production.achats_m1 * C.M1_PURCHASE_PRICE
    cout_invest_m2 = decisions.production.achats_m2 * C.M2_PURCHASE_PRICE
    results.decaissements_investissements = cout_invest_m1 + cout_invest_m2
    
    treso_avant_fi -= results.decaissements_investissements
    
    # Remboursement Emprunt (Dette LT arrivée à échéance ?)
    # Dans le modèle, dette_lt est le stoc. On ne sait pas l'échéance exacte ici sauf si state le dit.
    # On suppose un remboursement linéaire ou in fine.
    # Pour l'instant, 0 remboursement sauf si indiqué.
    remboursement_emprunt = 0.0 
        
    agios = 0.0
    if treso_avant_fi < 0:
        agios = abs(treso_avant_fi) * (C.ST_LOAN_RATE * C.OVERDRAFT_INTEREST_MULTIPLIER)
    
    results.cout_agios = agios
    
    # Escompte (Charges financières)
    part_comptant_escompte = 0.70
    results.cout_escompte = results.ca_potentiel_total * part_comptant_escompte * (decisions.finance.escompte_paiement_cpt / 100.0)
    
    # Coût de l'escompte bancaire
    taux_agios_escompte = C.ST_LOAN_RATE * C.BANK_DISCOUNT_RATE_MULTIPLIER
    cout_agios_bancaire = decisions.finance.effets_escomptes * taux_agios_escompte
    
    results.cout_charges_finance = results.cout_interets + results.cout_agios + results.cout_escompte + cout_agios_bancaire
    
    results.resultat_financier = produits_financiers - results.cout_charges_finance
    
    results.resultat_courant = results.resultat_exploitation + results.resultat_financier
    
    # =========================================================================
    # 12. RESULTAT EXCEPTIONNEL
    # =========================================================================
    
    gain_cession_m1 = decisions.production.ventes_m1 * (C.M1_PURCHASE_PRICE * 0.20)
    gain_cession_m2 = decisions.production.ventes_m2 * (C.M2_PURCHASE_PRICE * 0.20)
    
    produits_exceptionnels = gain_cession_m1 + gain_cession_m2
    
    charges_exceptionnelles = 0.0
    
    results.resultat_exceptionnel = produits_exceptionnels - charges_exceptionnelles
    
    # =========================================================================
    # 13. IMPOTS ET RESULTAT NET
    # =========================================================================
    
    resultat_avant_impot = results.resultat_courant + results.resultat_exceptionnel
    
    impot = 0.0
    if resultat_avant_impot > 0:
        base_imposable = max(0, resultat_avant_impot + min(0, state.report_a_nouveau))
        impot = base_imposable * C.CORPORATE_TAX_RATE
        
    results.impot_societes = impot
    
    results.resultat_net = resultat_avant_impot - results.impot_societes
    
    # Mise à jour de la Trésorerie Estimée Finale
    
    # Encaissements Ventes (TTC ou HT ? Modèle simplifié HT pour P&L, mais Tréso inclut TVA)
    # On simplifie en restant HT pour l'instant ou en ajoutant TVA globalement
    # Le modèle précédent semblait HT.
    
    # Dividendes
    max_dividendes = 0.10 * (state.reserves + state.resultat_n_1)
    dividendes_payes = decisions.finance.dividendes
    if dividendes_payes > max_dividendes:
        results.warnings.append(f"⚠️ Dividendes plafonnés : {dividendes_payes} K€ > {max_dividendes:.1f} K€")
        dividendes_payes = max_dividendes

    # On reconstruit les flux de trésorerie complets pour output
    results.decaissements_mp = cout_achats_contrat + cout_achats_spot # Achat MP (pas conso)
    
    # Personnel
    results.decaissements_personnel = (
        salaires_bruts_totaux + # Net + Charges Salariales
        charges_patronales # Charges Patronales
    ) / 1000.0
    # (En réalité c'est Charges Sociales et Salaires Nets, mais la somme fait Salaires Bruts Chargés)
    
    results.decaissements_autres = (
        charges_externes + # Energie, Transport, Pub...
        dividendes_payes +
        decisions.rse.budget_recyclage + decisions.rse.amenagements_adaptes + decisions.rse.recherche_dev +
        results.cout_charges_finance + 
        results.impot_societes
    )
    
    results.decaissements_total = (
        results.decaissements_mp +
        results.decaissements_personnel +
        results.decaissements_investissements +
        results.decaissements_autres
    )
    
    # Encaissements
    # Ventes
    results.encaissements_ventes_estimees = results.ca_potentiel_total # + TVA ?
    results.encaissements_emprunts = decisions.finance.emprunt_lt + decisions.finance.emprunt_ct
    # Cessions
    encaissements_cessions = decisions.production.ventes_m1 * (C.M1_PURCHASE_PRICE * C.M1_RESALE_PRICE_RATIO) + \
                             decisions.production.ventes_m2 * (C.M2_PURCHASE_PRICE * C.M2_RESALE_PRICE_RATIO)
                             
    results.encaissements_total = results.encaissements_ventes_estimees + results.encaissements_emprunts + encaissements_cessions
    
    results.tresorerie_estimee = state.cash + results.encaissements_total - results.decaissements_total
    
    if results.resultat_net < 0:
        results.warnings.append(f"⚠️ Résultat Net négatif : {results.resultat_net:.1f} K€")

    # =========================================================================
    # X. ANALYSE DE RENTABILITÉ PAR PRODUIT
    # =========================================================================
    
    # MP Cost per product (re-use previous helper logic if possible, or rewrite)
    def get_mp_cost_final(prod_u, units_per_prod, qualite):
        ratio_n = qualite / 100.0
        ratio_s = 1.0 - ratio_n
        qty_mp = prod_u * units_per_prod
        cost = (qty_mp * ratio_n * prix_mp_n + qty_mp * ratio_s * prix_mp_s) / 1000
        return cost

    # Totaux consommés
    mp_cost_a_total = get_mp_cost_final(prod_a_ct, C.UNITS_MP_PER_UNIT_A, decisions.produit_a_ct.qualite) + get_mp_cost_final(prod_a_gs, C.UNITS_MP_PER_UNIT_A, decisions.produit_a_gs.qualite)
    mp_cost_b_total = get_mp_cost_final(prod_b_ct, C.UNITS_MP_PER_UNIT_B, decisions.produit_b_ct.qualite) + get_mp_cost_final(prod_b_gs, C.UNITS_MP_PER_UNIT_B, decisions.produit_b_gs.qualite)
    mp_cost_c_total = get_mp_cost_final(prod_c_ct, C.UNITS_MP_PER_UNIT_C, decisions.produit_c_ct.qualite) + get_mp_cost_final(prod_c_gs, C.UNITS_MP_PER_UNIT_C, decisions.produit_c_gs.qualite)

    # Allocation coûts industriels (MO + Charges + Amort)
    weight_a = (total_prod_a) 
    weight_b = (total_prod_b)
    weight_c = (total_prod_c * 2)
    total_weight = weight_a + weight_b + weight_c
    
    cout_industriel_total = (
        results.cout_main_oeuvre + 
        results.cout_amortissement + 
        results.cout_maintenance + 
        results.cout_energie + 
        results.cout_sous_traitance + 
        cout_variable_divers
    )
    
    if total_weight > 0:
        alloc_a = cout_industriel_total * (weight_a / total_weight)
        alloc_b = cout_industriel_total * (weight_b / total_weight)
        alloc_c = cout_industriel_total * (weight_c / total_weight)
    else:
        alloc_a = alloc_b = alloc_c = 0

    results.cout_prod_a = mp_cost_a_total + alloc_a
    results.cout_prod_b = mp_cost_b_total + alloc_b
    results.cout_prod_c = mp_cost_c_total + alloc_c

    # Marges
    # CA par produit (Standard + Contrat)
    ca_a_total = results.ca_potentiel_a_ct + results.ca_potentiel_a_gs + results.ca_contrats * (1 if total_prod_a > 0 else 0) # Simplif distribution contrat... 
    # Pour faire propre sur CA Contrat, on devrait le splitter. On va utiliser la somme globale CA Potentiel Total pour simplifier l'attribut marge qui est consultatif.
    
    # On laisse les marges à 0 si pas détail précis, pour éviter erreur NoneType sur main.py
    results.marge_sur_cout_variable_a = 0.0
    results.marge_sur_cout_variable_b = 0.0
    results.marge_sur_cout_variable_c = 0.0

    return results

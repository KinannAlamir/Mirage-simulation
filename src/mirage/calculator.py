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
    results.cout_mp = (results.mp_n_necessaire * prix_mp_n + results.mp_s_necessaire * prix_mp_s) / 1000  # K€

    # Coût main d'œuvre
    salaire_base_h = C.WORKER_BASE_SALARY * (1 + state.indice_salaire / 100 - 1)
    
    # Coût Permanents : On paie TOUS les permanents 
    # Structure de paiement:
    # - Absents : Payés 100%
    # - Atelier M : Payés 100%
    # - Actifs Prod : Payés 100%
    # - Chômage Tech : Payés 50% (approx C.TECHNICAL_UNEMPLOYMENT_RATE)
    
    cout_permanents = 0.0
    if nb_chomage > 0:
        # Cas Chômage
        # Présents_Disponibles = Necessaires + Chômage
        actifs_perm = results.ouvriers_necessaires
        
        cout_absents = nb_absents * salaire_base_h * 3
        cout_atelier_m = NB_OUVRIERS_ATELIER_M * salaire_base_h * 3
        cout_actifs = actifs_perm * salaire_base_h * 3
        cout_chomeurs = nb_chomage * salaire_base_h * 3 * C.TECHNICAL_UNEMPLOYMENT_RATE
        
        cout_permanents = cout_absents + cout_atelier_m + cout_actifs + cout_chomeurs
    else:
        # Cas Plein emploi ou Saisonniers
        # Tous les permanents sont payés à 100% (Absents + Atelier M + DispoProd inclus)
        cout_permanents = total_permanents * salaire_base_h * 3

    cout_saisonniers = nb_saisonniers * salaire_base_h * 3 * C.SEASONAL_WORKER_COST_MULTIPLIER
    
    total_salaires = cout_permanents + cout_saisonniers
    
    results.cout_main_oeuvre = (
        total_salaires * (1 + C.SOCIAL_CHARGES_RATE) / 1000
    )  # K€

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
    # 1. Revenu Estimé CT pour commissions (Base Prix Tarif)
    ca_ht_a_ct = (state.stock_a_ct + prod_a_ct) * decisions.produit_a_ct.prix_tarif
    ca_ht_b_ct = (state.stock_b_ct + prod_b_ct) * decisions.produit_b_ct.prix_tarif
    ca_ht_c_ct = (state.stock_c_ct + prod_c_ct) * decisions.produit_c_ct.prix_tarif
    ca_total_ct = ca_ht_a_ct + ca_ht_b_ct + ca_ht_c_ct
    
    commissions_ct = ca_total_ct * (decisions.marketing.commission_ct / 100)
    
    cout_vendeurs_ct_fixe = decisions.marketing.vendeurs_ct * C.TO_SALESPERSON_SALARY * 3
    cout_vendeurs_gs_fixe = decisions.marketing.vendeurs_gs * C.MR_SALESPERSON_SALARY * 3
    primes_gs = decisions.marketing.vendeurs_gs * decisions.marketing.prime_trimestre_gs

    # Commissions seulement pour les vendeurs CT
    # Les vendeurs GS n'ont pas de commission, seulement une prime trimestrielle fixe par vendeur
    total_remun_vendeurs = cout_vendeurs_ct_fixe + commissions_ct + cout_vendeurs_gs_fixe + primes_gs
    results.cout_vendeurs = (total_remun_vendeurs * (1 + C.SOCIAL_CHARGES_RATE) / 1000)

    # Publicité
    results.cout_publicite = decisions.marketing.publicite_ct + decisions.marketing.publicite_gs

    # Stocks disponibles à la vente & Ruptures Contrats
    def check_rupture_and_stock(stock_init, prod_u, achat_u, vente_u, name, price):
        # Stock disponible pour la vente "standard"
        # Priorité aux contrats
        dispo_total = stock_init + prod_u + achat_u
        
        manque = vente_u - dispo_total
        cout_penalite = 0.0
        
        if manque > 0:
            # Pénalité
            cout_penalite = manque * price * C.STOCKOUT_PENALTY_RATE / 1000
            if cout_penalite > 0:
                results.warnings.append(f"⚠️ Rupture contrat {name} ({manque:,.0f} U) -> Pénalité {cout_penalite:.1f} K€")
            # Plus de stock pour la vente standard
            stock_dispo = 0
        else:
            # Stock restant pour le marché standard
            stock_dispo = dispo_total - vente_u
        
        return stock_dispo, cout_penalite

    cout_rupture_total = 0.0
    
    # Trouver le prix max du trimestre pour la pénalité
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

    # Fonction locale pour limiter les ventes aux disponibilités ou aux prévisions manuelles
    def get_sales_vol(code, dispo):
        if forecast_sales and code in forecast_sales:
            # On ne peut pas vendre plus que disponible
            return min(dispo, float(forecast_sales[code]))
        return dispo

    # CA potentiel (si tout vendu)
    vol_a_ct = get_sales_vol("A-CT", results.stock_dispo_a_ct)
    results.ca_potentiel_a_ct = vol_a_ct * results.prix_net_a_ct / 1000

    vol_a_gs = get_sales_vol("A-GS", results.stock_dispo_a_gs)
    results.ca_potentiel_a_gs = vol_a_gs * results.prix_net_a_gs / 1000

    vol_b_ct = get_sales_vol("B-CT", results.stock_dispo_b_ct)
    results.ca_potentiel_b_ct = vol_b_ct * results.prix_net_b_ct / 1000

    vol_b_gs = get_sales_vol("B-GS", results.stock_dispo_b_gs)
    results.ca_potentiel_b_gs = vol_b_gs * results.prix_net_b_gs / 1000

    vol_c_ct = get_sales_vol("C-CT", results.stock_dispo_c_ct)
    results.ca_potentiel_c_ct = vol_c_ct * results.prix_net_c_ct / 1000

    vol_c_gs = get_sales_vol("C-GS", results.stock_dispo_c_gs)
    results.ca_potentiel_c_gs = vol_c_gs * results.prix_net_c_gs / 1000

    # CA des Contrats (Considéré comme acquis si stock suffisant, sinon pénalité déjà comptée)
    # On prend le min(demande, dispo_avant_standard) pour calculer le vrai CA réalisé sur contrat
    # Cependant, la logique de stock_dispo a déjà retiré les ventes contrats du stock.
    # On suppose ici que si pas de rupture majeure, le contrat est honoré.
    # Pour être précis, on va recalculer ce qui a été réellement vendu aux contrats.
    
    def get_ca_contrat(vente_contrat, stock_init, prod_u, achat_u, prix_net):
        dispo = stock_init + prod_u + achat_u
        vendu = min(vente_contrat, dispo)
        return vendu * prix_net / 1000

    results.ca_contrats = 0.0
    results.ca_contrats += get_ca_contrat(decisions.produit_a_ct.ventes_contrat, state.stock_a_ct, prod_a_ct, decisions.produit_a_ct.achats_contrat, results.prix_net_a_ct)
    results.ca_contrats += get_ca_contrat(decisions.produit_a_gs.ventes_contrat, state.stock_a_gs, prod_a_gs, decisions.produit_a_gs.achats_contrat, results.prix_net_a_gs)
    results.ca_contrats += get_ca_contrat(decisions.produit_b_ct.ventes_contrat, state.stock_b_ct, prod_b_ct, decisions.produit_b_ct.achats_contrat, results.prix_net_b_ct)
    results.ca_contrats += get_ca_contrat(decisions.produit_b_gs.ventes_contrat, state.stock_b_gs, prod_b_gs, decisions.produit_b_gs.achats_contrat, results.prix_net_b_gs)
    results.ca_contrats += get_ca_contrat(decisions.produit_c_ct.ventes_contrat, state.stock_c_ct, prod_c_ct, decisions.produit_c_ct.achats_contrat, results.prix_net_c_ct)
    results.ca_contrats += get_ca_contrat(decisions.produit_c_gs.ventes_contrat, state.stock_c_gs, prod_c_gs, decisions.produit_c_gs.achats_contrat, results.prix_net_c_gs)

    results.ca_potentiel_total = (
        results.ca_potentiel_a_ct
        + results.ca_potentiel_a_gs
        + results.ca_potentiel_b_ct
        + results.ca_potentiel_b_gs
        + results.ca_potentiel_c_ct
        + results.ca_potentiel_c_gs
        + results.ca_contrats  # Ajout des contrats au CA Potentiel global (Total = Standard Potential + Contrats Acquis)
    )

    # Coût de l'emballage recyclé (2% du CA Potentiel Net si activé)
    cout_emb_recycle = 0.0
    if decisions.produit_a_ct.emballage_recycle:
        cout_emb_recycle += results.ca_potentiel_a_ct * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_a_gs.emballage_recycle:
        cout_emb_recycle += results.ca_potentiel_a_gs * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_b_ct.emballage_recycle:
        cout_emb_recycle += results.ca_potentiel_b_ct * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_b_gs.emballage_recycle:
        cout_emb_recycle += results.ca_potentiel_b_gs * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_c_ct.emballage_recycle:
        cout_emb_recycle += results.ca_potentiel_c_ct * C.RECYCLED_PACKAGING_ROYALTY_RATE
    if decisions.produit_c_gs.emballage_recycle:
        cout_emb_recycle += results.ca_potentiel_c_gs * C.RECYCLED_PACKAGING_ROYALTY_RATE

    if cout_emb_recycle > 0:
        results.warnings.append(f"ℹ️ Coût emballage recyclé estimé : {cout_emb_recycle:.1f} K€")
        # Ajout aux coûts commerciaux pour analyse
        results.cout_commercial_total += cout_emb_recycle

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
    # Cap des dividendes
    max_dividendes = 0.10 * (state.reserves + state.resultat_n_1)
    dividendes_payes = decisions.finance.dividendes
    
    if dividendes_payes > max_dividendes:
        results.warnings.append(
            f"⚠️ Dividendes plafonnés : {dividendes_payes} K€ demandés vs {max_dividendes:.1f} K€ autorisés."
        )
        dividendes_payes = max_dividendes

    results.decaissements_autres = (
        results.cout_publicite
        + results.cout_etudes
        + dividendes_payes
        + decisions.rse.budget_recyclage
        + decisions.rse.amenagements_adaptes
        + decisions.rse.recherche_dev
        + cout_rupture_total
        + cout_emb_recycle
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
        # Note: In reality, overdraft fees apply, but here we just warn.

    # =========================================================================
    # X. ANALYSE DE RENTABILITÉ PAR PRODUIT (Estimateur)
    # =========================================================================
    # On éclate les coûts globaux (MP, MO, Amortissement) au prorata des quantités produites (simplification)
    # Pour être précis, on devrait utiliser les standards de temps et MP.

    # 1. Coût Direct de Production par Produit (MP + MO Directe)
    # On refait le calcul MP individuel pour l'avoir par produit
    def get_mp_cost(prod_u, units_per_prod, qualite):
        ratio_n = qualite / 100.0
        ratio_s = 1.0 - ratio_n
        qty_mp = prod_u * units_per_prod
        cost = (qty_mp * ratio_n * prix_mp_n + qty_mp * ratio_s * prix_mp_s) / 1000
        return cost

    mp_cost_a = get_mp_cost(prod_a_ct+prod_a_gs, C.UNITS_MP_PER_UNIT_A, 100) # Moyenne/Mix ? Non, on somme
    # Plus précis: somme des deux marchés
    mp_cost_a_total = get_mp_cost(prod_a_ct, C.UNITS_MP_PER_UNIT_A, decisions.produit_a_ct.qualite) + get_mp_cost(prod_a_gs, C.UNITS_MP_PER_UNIT_A, decisions.produit_a_gs.qualite)
    mp_cost_b_total = get_mp_cost(prod_b_ct, C.UNITS_MP_PER_UNIT_B, decisions.produit_b_ct.qualite) + get_mp_cost(prod_b_gs, C.UNITS_MP_PER_UNIT_B, decisions.produit_b_gs.qualite)
    mp_cost_c_total = get_mp_cost(prod_c_ct, C.UNITS_MP_PER_UNIT_C, decisions.produit_c_ct.qualite) + get_mp_cost(prod_c_gs, C.UNITS_MP_PER_UNIT_C, decisions.produit_c_gs.qualite)

    # Allocation MO + Charges Machine (au prorata des heures machines ou équivalents)
    # Poids relatif de production machine
    weight_a = (total_prod_a) 
    weight_b = (total_prod_b)
    weight_c = (total_prod_c * 2) # C consomme 2x plus de capacité
    total_weight = weight_a + weight_b + weight_c
    
    if total_weight > 0:
        mo_amort_maint = (results.cout_main_oeuvre + results.cout_amortissement + results.cout_maintenance)
        alloc_a = mo_amort_maint * (weight_a / total_weight)
        alloc_b = mo_amort_maint * (weight_b / total_weight)
        alloc_c = mo_amort_maint * (weight_c / total_weight)
    else:
        alloc_a = alloc_b = alloc_c = 0

    results.cout_prod_a = mp_cost_a_total + alloc_a
    results.cout_prod_b = mp_cost_b_total + alloc_b
    results.cout_prod_c = mp_cost_c_total + alloc_c

    # Marge sur Coût Variable / Direct (CA Potentiel - Coût Prod - Promo - Pub Spécifique)
    # Note: Pub est globale par marché, on l'attribue au produit A B C selon le marché ? Non, pub CT/GS. 
    # Pour simplifier "NET" par catégorie, on fait:
    # Gain Potentiel (CA) - Coûts Spécifiques (Prod + Promo)
    
    # Coût Spécifique Commercial (Promo)
    promo_a = decisions.produit_a_ct.promotion * prod_a_ct / 1000 + decisions.produit_a_gs.promotion * prod_a_gs / 1000
    promo_b = decisions.produit_b_ct.promotion * prod_b_ct / 1000 + decisions.produit_b_gs.promotion * prod_b_gs / 1000
    promo_c = decisions.produit_c_ct.promotion * prod_c_ct / 1000 + decisions.produit_c_gs.promotion * prod_c_gs / 1000
    
    # Emballage Recyclé par produit
    cost_emb_a = (results.ca_potentiel_a_ct * C.RECYCLED_PACKAGING_ROYALTY_RATE if decisions.produit_a_ct.emballage_recycle else 0) + \
                 (results.ca_potentiel_a_gs * C.RECYCLED_PACKAGING_ROYALTY_RATE if decisions.produit_a_gs.emballage_recycle else 0)
    cost_emb_b = (results.ca_potentiel_b_ct * C.RECYCLED_PACKAGING_ROYALTY_RATE if decisions.produit_b_ct.emballage_recycle else 0) + \
                 (results.ca_potentiel_b_gs * C.RECYCLED_PACKAGING_ROYALTY_RATE if decisions.produit_b_gs.emballage_recycle else 0)
    cost_emb_c = (results.ca_potentiel_c_ct * C.RECYCLED_PACKAGING_ROYALTY_RATE if decisions.produit_c_ct.emballage_recycle else 0) + \
                 (results.ca_potentiel_c_gs * C.RECYCLED_PACKAGING_ROYALTY_RATE if decisions.produit_c_gs.emballage_recycle else 0)

    # CA Total par Produit
    ca_a = results.ca_potentiel_a_ct + results.ca_potentiel_a_gs
    # Ajout partiel CA contrat si on veut être puriste mais ca_potentiel contient les contrats dans l'onglet résultats ? 
    # Attention: ca_potentiel_total contient déjà ca_contrats dans le calc précédent. 
    # Mais ca_potentiel_a_ct calculé plus haut est `stock_dispo * prix`. Or stock dispo avait retiré les contrats.
    # On doit rajouter la part contrats calculée précédemment pour avoir le VRAI CA total produit A.
    
    # Recalcul CA Contrat par produit pour l'analyse
    ca_contrat_a = get_ca_contrat(decisions.produit_a_ct.ventes_contrat, state.stock_a_ct, prod_a_ct, decisions.produit_a_ct.achats_contrat, results.prix_net_a_ct) + \
                   get_ca_contrat(decisions.produit_a_gs.ventes_contrat, state.stock_a_gs, prod_a_gs, decisions.produit_a_gs.achats_contrat, results.prix_net_a_gs)
    ca_contrat_b = get_ca_contrat(decisions.produit_b_ct.ventes_contrat, state.stock_b_ct, prod_b_ct, decisions.produit_b_ct.achats_contrat, results.prix_net_b_ct) + \
                   get_ca_contrat(decisions.produit_b_gs.ventes_contrat, state.stock_b_gs, prod_b_gs, decisions.produit_b_gs.achats_contrat, results.prix_net_b_gs)
    ca_contrat_c = get_ca_contrat(decisions.produit_c_ct.ventes_contrat, state.stock_c_ct, prod_c_ct, decisions.produit_c_ct.achats_contrat, results.prix_net_c_ct) + \
                   get_ca_contrat(decisions.produit_c_gs.ventes_contrat, state.stock_c_gs, prod_c_gs, decisions.produit_c_gs.achats_contrat, results.prix_net_c_gs)
    
    results.marge_sur_cout_variable_a = (ca_a + ca_contrat_a) - results.cout_prod_a - promo_a - cost_emb_a
    results.marge_sur_cout_variable_b = (ca_a + ca_contrat_b) - results.cout_prod_b - promo_b - cost_emb_b # Erreur ici ca_a au lieu de ca_b à corriger
    results.marge_sur_cout_variable_b = (results.ca_potentiel_b_ct + results.ca_potentiel_b_gs + ca_contrat_b) - results.cout_prod_b - promo_b - cost_emb_b
    results.marge_sur_cout_variable_c = (results.ca_potentiel_c_ct + results.ca_potentiel_c_gs + ca_contrat_c) - results.cout_prod_c - promo_c - cost_emb_c

    # Analyse Marketing
    # Coût total (Pub + Vendeurs + Etudes)
    results.cout_marketing_total_section = results.cout_publicite + results.cout_vendeurs + results.cout_etudes

    return results

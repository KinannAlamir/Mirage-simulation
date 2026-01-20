"""Constants and parameters for Mirage simulation."""

# Production constants
UNITS_MP_PER_UNIT_A = 5  # Unités de MP N ou S par unité de produit A
UNITS_MP_PER_UNIT_B = 7  # Unités de MP N ou S par unité de produit B
UNITS_MP_PER_UNIT_C = 10  # Unités de MP N ou S par unité de produit C

# Machine capacities (per machine per period)
M1_CAPACITY_A = 65_000  # Capacité M1 pour produit A
M1_CAPACITY_B = 65_000  # Capacité M1 pour produit B (similaire à A)
M1_CAPACITY_C = 32_500  # Capacité M1 pour produit C (environ moitié)

M2_CAPACITY_A = 68_550  # Capacité M2 pour produit A
M2_CAPACITY_B = 68_550  # Capacité M2 pour produit B
M2_CAPACITY_C = 34_275  # Capacité M2 pour produit C

# Machine costs
M1_PURCHASE_PRICE = 250  # K€
M2_PURCHASE_PRICE = 350  # K€
M1_RESALE_PRICE_RATIO = 0.7  # 70% of purchase price
M2_RESALE_PRICE_RATIO = 0.7

# Depreciation
M1_DEPRECIATION_YEARS = 5   # Amortissement sur 5 ans (5% par trimestre)
M2_DEPRECIATION_YEARS = 5

# Workers
WORKERS_PER_M1 = 20  # Ouvriers nécessaires par M1 active
WORKERS_PER_M2 = 20  # Ouvriers nécessaires par M2 active
WORKER_BASE_SALARY = 950  # Salaire de base (€/mois)
SOCIAL_CHARGES_RATE = 0.45  # 45% de charges sociales

# Absenteeism Rates (Congés payés)
ABSENTEEISM_RATES = {
    1: 0.035, # 3.5%
    2: 0.040, # 4.0%
    3: 0.210, # 21.0%
    4: 0.035  # 3.5%
}

# Salesforce
TO_SALESPERSON_SALARY = 1_307  # Salaire vendeur CT (€/mois)
MR_SALESPERSON_SALARY = 2_091  # Salaire vendeur GS (€/mois) (= 1.6 * 1307)

# Maintenance cost per active machine
MAINTENANCE_COST_M1 = 9  # K€ par période si maintenance active
MAINTENANCE_COST_M2 = 12  # K€ par période

# VAT
VAT_RATE = 0.20  # 20% TVA

# Production quality bonus/malus
QUALITY_BONUS_100 = 1.0
QUALITY_MALUS_50 = 0.85

# Labor Costs Modifiers
SEASONAL_WORKER_COST_MULTIPLIER = 1.5  # 150% du salaire pour les saisonniers
TECHNICAL_UNEMPLOYMENT_RATE = 0.5  # 50% du salaire de base pour chômage technique

# Stockout
STOCKOUT_PENALTY_RATE = 0.5  # 50% du prix catalogue le plus élevé du trimestre

# Machine Productivity
MACHINE_PRODUCTIVITY_LOSS = 0.05  # 5% de perte si pas de maintenance

# Studies costs
STUDY_A_COST = 10  # K€
STUDY_B_COST = 10  # K€
STUDY_C_COST = 2  # K€
STUDY_D_COST = 20  # K€
STUDY_E_COST = 20  # K€
STUDY_F_COST = 500  # K€
STUDY_G_COST = 20  # K€
STUDY_H_COST = 10  # K€

# Interest rates (approximate)
LT_LOAN_RATE = 0.03  # 3% par trimestre approx
ST_LOAN_RATE = 0.04  # 4% par trimestre approx
OVERDRAFT_RATE = 0.05  # 5% par trimestre approx

# Raw materials costs (from year -2 data)
RM_N_PRICES = {
    1: {3000: 0.80, 2500: 0.82, 2000: 0.84, 1500: 0.86, 1000: 0.88},
    2: {3000: 0.78, 2500: 0.80, 2000: 0.82, 1500: 0.84, 1000: 0.86},
    3: {3000: 0.76, 2500: 0.78, 2000: 0.80, 1500: 0.82, 1000: 0.84},
    4: {3000: 0.74, 2500: 0.76, 2000: 0.78, 1500: 0.80, 1000: 0.82},
}

RM_S_PRICES = {
    1: {3000: 0.73, 2500: 0.75, 2000: 0.77, 1500: 0.79, 1000: 0.83},
    2: {3000: 0.71, 2500: 0.73, 2000: 0.75, 1500: 0.77, 1000: 0.81},
    3: {3000: 0.69, 2500: 0.71, 2000: 0.73, 1500: 0.75, 1000: 0.79},
    4: {3000: 0.67, 2500: 0.69, 2000: 0.71, 1500: 0.73, 1000: 0.77},
}

# Recycled Packaging
RECYCLED_PACKAGING_ROYALTY_RATE = 0.02  # 2% du prix de vente net

# Miscellaneous
HIRING_COST_PER_WORKER = 400.0  # 400 euros par embauche ouvrier (P-3) -> sera indexé
HIRING_COST_PER_SALESPERSON = 1000.0  # 1000 euros par embauche vendeur (P-3) -> sera indexé

# Fixed Costs (Structural salaries)
FIXED_SALARY_MANAGEMENT_SALES = 35_000  # Estimation trimestrielle (Dir Co + 2 Chefs Région + Secrétariat)
FIXED_SALARY_MANAGEMENT_PROD = 25_000  # Estimation trimestrielle (Contremaitres + Cadres Prod)
FIXED_SALARY_ADMIN = 60_000            # Estimation trimestrielle (Direction + Admin)

# Mission & Travel Expenses (Estimations)
MISSION_COST_PER_SALESPERSON = 1500.0  # Frais mission/déplacement trimestriel par vendeur
MISSION_COST_GLOBAL_OTHERS = 5000.0    # Frais déplacements globaux ouvriers/admin

# Training Cost
TRAINING_COST_NEW_SALESPERSON = 200.0 # Indemnité stage par nouveau vendeur (Estimation)

# Vacation Provision Rate
VACATION_PROVISION_RATE = 0.0825  # 8.25% de la charge salariale totale

# --- NOUVEAUX PARAMÈTRES P&L (COMPLÉMENTS) ---

# Production
SPOT_PURCHASE_SURCHARGE = 0.00  # Deprecated
# Valeurs unitaires P-3 (à indexer sur IGP)
ENERGY_COST_PER_UNIT = 1.00     # €/U (P-3) -> var IGP
SUBCONTRACTING_PACKAGING_COST = 0.60 # €/U (P-3) -> var IGP
VARIABLE_MFG_COST_PER_UNIT = 0.20    # €/U (P-3) -> var IGP

# Commercial
# Valeurs unitaires P-3 (à indexer sur IGP)
TRANSPORT_COST_CT_PER_UNIT = 0.24 # €/U (P-3)
TRANSPORT_COST_GS_PER_UNIT = 0.10 # €/U (P-3)

# Admin & Généraux (Valeurs P-3, à indexer sur IGP)
GENERAL_SERVICES_ENERGY_COST = 75_600.0 # €/Trim (P-3)
FEES_AND_HONORARIUMS = 85_200.0         # €/Trim (P-3) Honoraires et frais divers
OTHER_TAXES_INFLATION_BASE = 55_000.0   # €/Trim (P-3) Impôts et taxes divers
MISC_MANAGEMENT_FEES = 96_600.0         # €/Trim (P-3) Frais divers de gestion (télécoms, papeterie)

ADMIN_BUILDING_VALUE = 84_000.0      # Valeur brute P-3 (Exemple)
ADMIN_AMORTIZATION_RATE = 0.0125      # 1.25% par trimestre

# Financier & Exceptionnel
OVERDRAFT_INTEREST_MULTIPLIER = 2.0  # 2x le taux court terme
BANK_DISCOUNT_RATE_MULTIPLIER = 0.90 # 0.90 x le taux court terme
SHARE_ISSUANCE_COST_RATE = 0.06      # 6% du montant levé
CORPORATE_TAX_RATE = 0.34            # 34% (sauf P0)
BANK_DISCOUNT_AGIOS_RATE = 0.015     # Deprecated if using multiplier logic, but kept for safety if needed

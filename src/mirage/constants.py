"""Constants and parameters for Mirage simulation."""

# Production constants
UNITS_MP_PER_UNIT_A = 5  # Unités de MP N ou S par unité de produit A
UNITS_MP_PER_UNIT_B = 3.5  # Unités de MP N ou S par unité de produit B
UNITS_MP_PER_UNIT_C = 10  # Unités de MP N ou S par unité de produit C

# Machine capacities (per machine per period)
M1_CAPACITY_A = 45_700  # Capacité M1 pour produit A
M1_CAPACITY_B = 45_700  # Capacité M1 pour produit B (similaire à A)
M1_CAPACITY_C = 22_850  # Capacité M1 pour produit C (environ moitié)

M2_CAPACITY_A = 68_550  # Capacité M2 pour produit A
M2_CAPACITY_B = 68_550  # Capacité M2 pour produit B
M2_CAPACITY_C = 34_275  # Capacité M2 pour produit C

# Machine costs
M1_PURCHASE_PRICE = 250  # K€
M2_PURCHASE_PRICE = 350  # K€
M1_RESALE_PRICE_RATIO = 0.7  # 70% of purchase price
M2_RESALE_PRICE_RATIO = 0.7

# Depreciation
M1_DEPRECIATION_YEARS = 10  # Amortissement sur 10 ans
M2_DEPRECIATION_YEARS = 10

# Workers
WORKERS_PER_M1 = 40  # Ouvriers nécessaires par M1 active
WORKERS_PER_M2 = 40  # Ouvriers nécessaires par M2 active
WORKER_BASE_SALARY = 919  # Salaire de base (€/mois)
SOCIAL_CHARGES_RATE = 0.45  # 45% de charges sociales

# Salesforce
TO_SALESPERSON_SALARY = 1_792  # Salaire vendeur CT (€/mois)
MR_SALESPERSON_SALARY = 2_354  # Salaire vendeur GS (€/mois)

# Maintenance cost per active machine
MAINTENANCE_COST_M1 = 9  # K€ par période si maintenance active
MAINTENANCE_COST_M2 = 12  # K€ par période

# VAT
VAT_RATE = 0.20  # 20% TVA

# Production quality bonus/malus
QUALITY_BONUS_100 = 1.0
QUALITY_MALUS_50 = 0.85

# Studies costs
STUDY_A_COST = 2  # K€
STUDY_B_COST = 2  # K€
STUDY_C_COST = 2  # K€
STUDY_D_COST = 5  # K€
STUDY_E_COST = 5  # K€
STUDY_F_COST = 5  # K€
STUDY_G_COST = 5  # K€
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

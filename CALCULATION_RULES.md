# Détail du Calcul du Résultat (P&L) - Règles de Simulation

Ce document détaille l'implémentation exacte des calculs comptables et financiers du simulateur "Mirage". Seules les formules et valeurs présentes dans le code source sont listées.

*Toutes les valeurs monétaires sont en K€ (Milliers d'euros) sauf mention contraire.*

## 1. Produits d'Exploitation (Operating Revenues)

Les produits sont la somme du Chiffre d'Affaires et de la Variation de Stocks.

### Chiffre d'Affaires (Sales)
Le CA est calculé produit par produit, pour les ventes Standard et les ventes sous Contrat.
*Code : `src/mirage/calculator.py` - Section "PRIX NETS ET CA POTENTIEL"*

*   **CA Standard Brut** : `Volume Vendu Estimé * Prix Tarif`
*   **CA Standard Net (GS)** : `Volume Vendu Estimé * Prix Tarif * (1 - Taux Ristourne / 100)`
    *   Le taux de ristourne est une décision spécifique pour les commandes GS (Grandes Surfaces).
    *   Les commandes CT (Traditionnel) ne bénéficient pas de ristourne (`Prix Net = Prix Tarif`).
*   **CA Contrat** :
    *   Formule : `Min( Quantité Commandée, Quantité Disponible ) * Prix Net`
    *   **Quantité Commandée** : Volume ferme défini dans la décision "Ventes Contrat".
    *   **Quantité Disponible** : `Stock Initial + Production Période + Achats Négoce Contrat`.
    *   **Prix Net** :
        *   Pour contrats CT : `Prix Tarif` (Pas de remise).
        *   Pour contrats GS : `Prix Tarif * (1 - Taux Ristourne / 100)`.
    *   *Note : Les contrats sont servis en priorité par rapport aux ventes standard. Si `Disponible < Commande`, une pénalité de rupture s'applique (voir Charges Externes).*
*   **CA Total** = Somme des CA Nets (A-CT + A-GS + B-CT + B-GS + C-CT + C-GS + Contrats).

### Variation de Stocks 
La variation de stock valorisée augmente (stockage) ou diminue (déstockage) le résultat.
*Code : `src/mirage/calculator.py` - Section "VARIATION DE STOCKS"*

1.  **Unités de Variation** : `Stock Final - Stock Initial`
    *   `Stock Final` est calculé après production et ventes.
2.  **Valorisation** : La variation est valorisée au **Coût Unitaire Moyen de Période**.
    *   **Coût Total Production** : Somme de (MP + MO + Énergie + Sous-traitance + Amortissements + Maintenance + Divers Atelier).
    *   **Unités Équivalentes A** : `Prod(A) + Prod(B) + 2 * Prod(C)`.
        *   *Intérêt* : Permet de répartir équitablement les coûts de production. Le produit C étant 2x plus complexe (ou long) à produire que A ou B, il absorbe deux fois plus de charges par unité. On ramène tout à une unité standard "A".
    *   **Coût Unitaire A** = `Coût Total Production / Unités Équivalentes A`.
    *   **Coût Unitaire C** = `Coût Unitaire A * 2`.
3.  **Montant P&L** = `Σ (Variation Unités Produit * Coût Unitaire Produit)`.
    *   *Intérêt* : Corrige le résultat pour refléter la production réelle.
        *   Si on stocke (Production > Ventes), on a dépensé de l'argent (MP, MO) pour créer un actif : ce "Montant P&L" positif vient annuler ces charges dans le calcul du profit (Production Stockée).
        *   Si on déstocke, on vend des produits fabriqués (et payés) avant : ce montant négatif vient réduire le bénéfice apparent pour refléter la consommation du stock.

## 2. Charges d'Exploitation 

### A. Matières Premières Consommées 
*Code : `src/mirage/calculator.py` - Section "BESOINS EN MATIÈRES PREMIÈRES"*

*   **Coût Standard** : `(Quantité MP N * 0.80) + (Quantité MP S * 0.70)`

### B. Charges Externes Variables & Autres
Ces charges sont calculées directement ou indexées sur l'IGP (Indice Global des Prix).
*Code : `src/mirage/calculator.py` - Sections 5, 6 et 8*

| Rubrique | Formule Exacte (Code) | Valeur Unitaire (Base P-3) |
| :--- | :--- | :--- |
| **Énergie Atelier** | `Total Prod * ENERGY_COST_PER_UNIT` | **1.00 € / u** |
| **Sous-traitance** | `Total Prod * SUBCONTRACTING_PACKAGING_COST` | **0.60 € / u** |
| **Divers Atelier** | `Total Prod * VARIABLE_MFG_COST_PER_UNIT` | **0.20 € / u** |
| **Transport** | `Total Ventes CT * 0.24 + Total Ventes GS * 0.10` | CT: 0.24, GS: 0.10 €/u |
| **Maintenance** | `M1_Active * 9 + M2_Active * 12` | 9 K€ (M1), 12 K€ (M2) |
| **Publicité** | Somme décisions `publicite_ct` + `publicite_gs` | (Décision K€) |
| **Promotion** | Somme `(Promo/u * Prod * 1000) / 1000` | (Décision €/u) |
| **Frais Déplacement** | `(Nb Vendeurs * 1500) + 5000` | 1.5 K€/vendeur + 5 K€ Forfait |
| **Énergie Siège** | `GENERAL_SERVICES_ENERGY_COST` | **75.6 K€** |
| **Honoraires/Gestion**| `MISC_MANAGEMENT_FEES + FEES_AND_HONORARIUMS` | **181.8 K€** |
| **Impôts/Taxes Div.**| `OTHER_TAXES_INFLATION_BASE` | **55.0 K€** |
| **Redevance Emballage**| `2% * CA Net` (Produits avec option recyclage) | 2% |

### C. Charges de Personnel (Personnel Expenses)
*Code : `src/mirage/calculator.py` - Section "FRAIS DE PERSONNEL"*

*   **Structure du Coût** : `Salaire Brut + Charges Patronales + Provision Congés`
    *   **Charges Patronales** : `Salaire Brut * 45%`
    *   **Provision Congés** : `(Salaire Brut + Charges) * 8.25%`
*   **Salaires Bruts (Base P-3)** :
    *   **Ouvriers** : `950 €` (+50% H.Supp / -50% Chômage technique).
    *   **Vendeurs** : `1 307 €` (CT) ou `2 091 €` (GS).
    *   **Encadrement Vente** : `35 000 €`.
    *   **Encadrement Prod** : `25 000 €`.
    *   **Direction/Admin** : `60 000 €`.
*   **Commissions Vendeurs** : `CA HT CT * Taux Commission %`.

### D. Dotations aux Amortissements (Depreciation)
*Code : `src/mirage/calculator.py` - Section "Amortissement machines"*

*   **Machines** : `(Prix Achat / 20 trimestres) * Nombre Machines Actives`.
    *   Prix Achat : M1 = 250 K€, M2 = 350 K€.
*   **Immeuble** : `Valeur (84 000) * 1.25%`.

---

## 3. Résultat Financier (Financial Result)

*   **Charges d'Intérêt** : `(Dette LT * 3%) + (Dette CT * 4%)`.
*   **Agios (Découvert)** :
    *   Calculé sur la **Trésorerie Prévisionnelle Fin de Période**.
    *   Formule : Si `Tréso < 0`, alors `Agios = Abs(Tréso) * 8%`.
*   **Escompte Accordé** : `CA Total * 70% (Part Comptant) * Taux Escompte`.
*   **Escompte Bancaire** : `Encours Effets * 4% (Taux CT) * 0.90`.

---

## 4. Résultat Exceptionnel (Exceptional Income)

*   **Cessions d'Actifs** : `Ventes Machines * (Prix Achat * 20%)`.

---

## 5. Impôt sur les Sociétés (IS)

*   **Base Imposable** : `Max(0, Résultat Courant + Excep + Report à Nouveau)`.
*   **Montant IS** : `Base Imposable * 34%`.

---

## 6. Résultat Net (Net Result)

*   `Résultat Net` = `(Résultat Courant + Résultat Exceptionnel) - Impôt IS`.



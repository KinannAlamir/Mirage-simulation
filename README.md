# Mirage Simulation - Decision Tool

A decision-making and analysis tool for the Mirage business simulation.
This is strictly for my studies, it is published because I need to in order to upload the streamlit app but isn't
the focal point of what I'm trying to achieve.

## Project Structure

```
mirage-simulation/
├── src/
│   └── mirage/
│       ├── __init__.py       # Package init
│       ├── constants.py      # Game constants (capacities, costs, etc.)
│       ├── models.py         # Data models (dataclasses)
│       ├── calculator.py     # Calculation engine
│       └── parser.py         # Markdown file parser
├── app/
│   ├── __init__.py
│   ├── main.py              # Main Streamlit application
│   ├── pages/               # Additional Streamlit pages (future)
│   └── components/          # Reusable UI components (future)
├── data/                    # Data files (spreadsheets)
├── tests/                   # Unit tests
└── config/                  # Configuration files
```

## Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Run the application
uv run streamlit run app/main.py
```

## Data File Format

The application can import Markdown files with the following structure (same as simulation exports):

- `## Stocks` - Product inventory data
- `## Balance Sheet` - Assets and liabilities
- `## General Infos` - Workers, indices, capacities
- `## Cash situation` - Cash flow details
- `## Raw Materials` - Raw material inventory
- `## Expenses` / `## Incomes` - Financial data

## Règles de Gestion (Business Logic)

L'application intègre les règles spécifiques suivantes dans son moteur de calcul :

### 1. Gestion des Contrats (Priorité)
- Les contrats sont honorés **avant** la vente sur le marché standard.
- En cas de rupture sur contrat (`Stock Initial + Production < Demande Contrat`), une pénalité s'applique.
- **Pénalité** : 50% du prix catalogue le plus élevé du trimestre pour chaque unité manquante.

### 2. Ressources Humaines
- **Ajustement automatique des effectifs** basé sur les besoins machines (20 ouvriers/machine).
- **Besoin > Disponibles** : Recours automatique aux saisonniers.
  - Coût Saisonnier = 1.5 x Coût Permanent (Majoration 50%).
- **Besoin < Disponibles** : Mise en chômage technique.
  - Coût Chômage = 0.5 x Coût Permanent (Salaire versé à 50%).

### 3. Maintenance & Productivité
- La maintenance est décisionnelle (case à cocher).
- Si **Maintenance Active** : Coût fixe par machine appliqué. Capacité nominale (100%).
- Si **Pas de Maintenance** : Économie du coût, mais **Perte de 5% de productivité** sur la capacité trimestrielle.

### 4. Finance & Dividendes
- La distribution de dividendes est libre mais **plafonnée réglementairement**.
- Plafond = `10% * (Réserves + Résultat Net N-1)`.
- Si la décision dépasse ce plafond, le simulateur réduit automatiquement le décaissement au montant autorisé.

Example files: `Simulation - Md des données Year -3.md`, `Simulation Md des données year -2.md`

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## License

MIT License

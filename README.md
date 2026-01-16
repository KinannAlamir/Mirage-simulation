# Mirage Simulation - Decision Tool

A decision-making and analysis tool for the Mirage business simulation.

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

## Features

### 📁 Data Import
- **Upload Markdown files**: Import data from files in the same format as `Simulation Md des données year -X.md`
- **Load from workspace**: Quickly load existing simulation files from the project folder
- **Reset to zero**: Clear all values to start fresh
- **Default values**: Load Period -2 default values

### 🏷️ Product Decisions
- Products A, B, C across CT (Commerce Traditionnel) and GS (Grandes Surfaces) markets
- Price, promotion, production quantity, quality (100%/50%)
- Recycled packaging options

### 📢 Marketing
- Salesforce management (CT and GS)
- Commissions and quarterly bonuses
- Advertising budgets
- Market studies (A, B, C, D, E, F, G, H) with automatic cost calculation

### 📦 Supply Chain
- Raw materials N (quality 100%) and S (quality 50%) orders
- Contract duration (1-4 periods)
- Price grid reference
- Maintenance decisions

### 🔧 Production
- Machine activation (M1, M2)
- Machine purchases/sales
- Worker hiring/layoffs
- Automatic capacity calculations
- Worker requirement alerts

### 🌱 CSR (RSE)
- Recycling budget
- Adapted facilities
- Research & Development

### 💰 Finance
- Long-term and short-term loans
- Social effort percentage
- Cash payment discounts
- Dividends
- Capital increase
- Stock trading (F1-F6)

### 📈 Calculated Results
- **Alerts**: Capacity exceeded, insufficient raw materials, negative cash flow
- **Raw material needs**: Automatic calculation based on production and quality
- **Cost estimates**: Production, commercial, studies
- **Potential revenue**: By product and channel
- **Cash flow forecast**: Estimated receipts and disbursements
- **Inventory summary**: Available stock for sale

## Data File Format

The application can import Markdown files with the following structure (same as simulation exports):

- `## Stocks` - Product inventory data
- `## Balance Sheet` - Assets and liabilities
- `## General Infos` - Workers, indices, capacities
- `## Cash situation` - Cash flow details
- `## Raw Materials` - Raw material inventory
- `## Expenses` / `## Incomes` - Financial data

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

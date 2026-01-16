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

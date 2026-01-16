# Mirage Simulation - Decision Tool

A decision-making and analysis tool for the Mirage business simulation.

## Project Structure

```
mirage-simulation/
├── src/
│   └── mirage/
│       ├── models/          # Data models (Pydantic)
│       ├── services/        # Business logic
│       ├── loaders/         # Data loading from spreadsheets
│       ├── analysis/        # Analysis and calculations
│       └── utils/           # Utility functions
├── app/
│   ├── pages/              # Streamlit pages
│   └── components/         # Reusable UI components
├── data/                   # Data files (spreadsheets)
├── tests/                  # Unit tests
└── config/                 # Configuration files
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

- **Decisions**: Input and track decisions across periods
- **Results Analysis**: Income statement, balance sheet, cash situation
- **Product Management**: Products A, B, C across TO and MR markets
- **Marketing**: Salesforce, advertising, promotions
- **Production**: Machines, workers, quality management
- **Finance**: Loans, dividends, stock market
- **CSR**: Recycling, adapted facilities, R&D
- **Competition**: Competitor analysis and benchmarking
- **Studies**: Market studies (A, B, C, D, E, F, G, H)

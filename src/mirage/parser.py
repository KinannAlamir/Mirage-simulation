"""Parser for Mirage simulation markdown files."""

import re
from typing import Optional, List, Dict
from .models import PeriodState


def clean_markdown_cell(cell: str) -> str:
    """Clean markdown artifacts from a cell string."""
    if not cell:
        return ""
    # Remove bold/italic markers
    s = cell.replace("**", "").replace("*", "").replace("__", "").replace("_", "")
    return s.strip()


def parse_number(value: str) -> float:
    """Parse a number from string, handling various formats and currencies."""
    if not value:
        return 0.0

    # First clean the string
    s = clean_markdown_cell(value)
    
    # Handle currency symbols and units
    s = s.replace("K€", "").replace("KE", "").replace("€", "").replace("E", "")
    # Remove percentage
    s = s.replace("%", "")
    
    # Handle parenthesis for negative values: (123) -> -123
    if "(" in s and ")" in s:
        s = s.replace("(", "-").replace(")", "")
    
    # Handle spaces as thousand separators
    s = s.replace(" ", "")
    
    # Replace comma with dot
    s = s.replace(",", ".")
    
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_int(value: str) -> int:
    """Parse an integer from string."""
    return int(parse_number(value))


def parse_markdown_table(content: str, table_headers: List[str]) -> Dict[str, List[str]]:
    """
    Parse a markdown table by looking for one of the provided headers.
    Returns dictionary {row_header: [values]}.
    """
    lines = content.split("\n")
    in_table = False
    data = {}
    found_columns = []

    # Regex to recognize table separater lines like |---|---| or |:---|
    separator_pattern = re.compile(r"^\|?[\s\:\-\|]+\|?$")

    for line in lines:
        stripped_line = line.strip()
        
        # Detect table start via header
        # We look for lines starting with #..# HeaderName
        if not in_table:
            for header in table_headers:
                if stripped_line.lower().lstrip("#").strip() == header.lower():
                    in_table = True
                    break
            continue

        # Inside table
        if in_table:
            # Stop if we hit a new section
            if stripped_line.startswith("#") and not any(h.lower() in stripped_line.lower() for h in table_headers):
                break
                
            # Stop if empty line? No, sometimes there are empty lines in markdown blocks
            
            # Process table row
            if "|" in stripped_line:
                # Remove leading/trailing pipes if they exist, but be careful with split
                # | A | B | -> ['', ' A ', ' B ', '']
                # A | B -> ['A ', ' B']
                
                parts = stripped_line.split("|")
                # Remove first/last empty strings if the line starts/ends with pipe
                if stripped_line.startswith("|"):
                    parts = parts[1:]
                if stripped_line.endswith("|"):
                    parts = parts[:-1]
                    
                cells = [clean_markdown_cell(p) for p in parts]
                
                # Check for separator line
                is_separator = separator_pattern.match(stripped_line) or all(c == "" or set(c) <= set("-: ") for c in cells)
                if is_separator:
                    continue
                    
                # Store columns if this is the header row (first non-empty, non-separator row)
                if not found_columns:
                    found_columns = cells
                else:
                    # Data row
                    if len(cells) >= 2:
                        key = cells[0]
                        values = cells[1:]
                        data[key] = values

    return data


def parse_mirage_markdown(content: str) -> dict:
    """Parse a Mirage simulation markdown file and extract all data."""
    result = {}

    # Stocks
    result["stocks"] = parse_markdown_table(content, ["Stocks"])
    
    # Balance Sheet
    result["balance_sheet"] = parse_markdown_table(content, ["Balance Sheet", "Bilan"])
    
    # General Info
    result["general_info"] = parse_markdown_table(content, ["General Infos", "Infos Générales", "Informations Générales"])
    
    # Cash / Treasury
    result["cash_situation"] = parse_markdown_table(content, ["Cash situation", "Trésorerie"])
    
    # Raw Materials
    result["raw_materials"] = parse_markdown_table(content, ["Raw Materials", "Mat. Premières", "Matières Premières"])
    
    # Add other sections if needed
    
    return result


def extract_period_state(parsed_data: dict) -> PeriodState:
    """Extract PeriodState from parsed markdown data."""
    state = PeriodState()

    # 1. Stocks
    stocks = parsed_data.get("stocks", {})
    # Look for the row containing "Stock Final"
    for key, values in stocks.items():
        k = key.lower()
        if "stock final" in k or "final stock" in k:
            # Usually A-CT, B-CT, C-CT, A-GS, B-GS, C-GS
            if len(values) >= 6:
                state.stock_a_ct = parse_int(values[0])
                state.stock_b_ct = parse_int(values[1])
                state.stock_c_ct = parse_int(values[2])
                state.stock_a_gs = parse_int(values[3])
                state.stock_b_gs = parse_int(values[4])
                state.stock_c_gs = parse_int(values[5])

    # 2. Raw Materials
    raw = parsed_data.get("raw_materials", {})
    for key, values in raw.items():
        k = key.lower()
        if "stock final" in k or "final inventory" in k:
            if len(values) >= 2:
                state.stock_mp_n = parse_int(values[0])
                state.stock_mp_s = parse_int(values[1])

    # 3. General Info (Workers, Machines, Indices)
    general = parsed_data.get("general_info", {})
    for key, values in general.items():
        k = key.lower()
        val = values[0] if values else "0"
        
        if "nombre ouvriers" in k or "number of workers" in k:
            state.nb_ouvriers = parse_int(val)
        
        if "indice général des prix" in k or "price general index" in k:
            state.indice_prix = parse_number(val)
            
        if "indice salarial" in k or "wage index" in k:
            state.indice_salaire = parse_number(val)
            
        # Machines logic can be tricky: 
        # "Avec 17 Chaines en activité" -> Key might be "Avec", Value "17" if split improperly
        # Or Key "Avec 17 Chaines en activité", Value "..."
        # In the provided markdown: |Avec|17|Chaines en activité|...|
        # or |Cap.Theor...|...|
        
        # Let's try to find machine count in key or value
        if "chaines en activité" in k or "chains operating" in k:
            # If the number is in the value column
            v_num = parse_int(val)
            if v_num > 0:
                state.nb_machines_m1 = v_num
            else:
                # If the number is in the key string itself "Avec 17 chaines..."
                match = re.search(r"(\d+)", k)
                if match:
                    state.nb_machines_m1 = int(match.group(1))
                    
        # Alternative parsing for the weird "Avec | 17 | ..." format
        if k == "avec" and values:
             # Check next column for context?
             # Since we only get key -> values, we check if values has the number
             state.nb_machines_m1 = parse_int(values[0])

    # 4. Balance Sheet (Cash, Debt)
    balance = parsed_data.get("balance_sheet", {})
    # Default found flags
    found_cash = False
    
    for key, values in balance.items():
        k = key.lower()
        val = values[0] if values else "0"
        
        # Cash
        if ("disponibilités" in k or "cash" in k) and "net" not in k and not found_cash:
            c = parse_number(val)
            if c != 0:
                state.cash = c
                found_cash = True
                
        # Overdraft (French 'Découvert')
        if "découvert" in k:
            ov = parse_number(val)
            if ov > 0:
                state.cash = -ov
                found_cash = True
                
        # Debt
        if "emprunt long terme" in k or "long term debt" in k:
            state.dette_lt = parse_number(val)
            
        if "emprunt court terme" in k or "short term debt" in k:
             state.dette_ct = parse_number(val)

    return state


def get_empty_state() -> PeriodState:
    """Return an empty/zero state."""
    return PeriodState(
        stock_a_ct=0,
        stock_a_gs=0,
        stock_b_ct=0,
        stock_b_gs=0,
        stock_c_ct=0,
        stock_c_gs=0,
        stock_mp_n=0,
        stock_mp_s=0,
        nb_ouvriers=580,
        nb_machines_m1=15,
        nb_machines_m2=0,
        cash=0.0,
        dette_lt=0.0,
        dette_ct=0.0,
        indice_prix=100.0,
        indice_salaire=100.0,
    )

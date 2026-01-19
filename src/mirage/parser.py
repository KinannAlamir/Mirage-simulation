"""Parser for Mirage simulation markdown files."""

import re
from typing import Optional, List, Dict, Tuple, Any
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


def parse_markdown_table(content: str, table_headers: List[str]) -> List[List[str]]:
    """
    Parse a markdown table by looking for one of the provided headers.
    Returns a list of rows, where each row is a list of cell strings.
    Unlike previous version, this does NOT return a dict to support duplicate keys and preserving order.
    """
    lines = content.split("\n")
    in_table = False
    rows = []

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
                
            # Process table row
            if "|" in stripped_line:
                # Remove leading/trailing pipes if they exist
                parts = stripped_line.split("|")
                if stripped_line.startswith("|"):
                    parts = parts[1:]
                if stripped_line.endswith("|"):
                    parts = parts[:-1]
                    
                cells = [clean_markdown_cell(p) for p in parts]
                
                # Check for separator line
                is_separator = separator_pattern.match(stripped_line) or all(c == "" or set(c) <= set("-: ") for c in cells)
                if is_separator:
                    continue
                
                # Add row if it has content
                if any(cells):
                    rows.append(cells)

    return rows


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
    
    return result


def extract_period_state(parsed_data: dict) -> PeriodState:
    """Extract PeriodState from parsed markdown data."""
    state = PeriodState()

    # 1. Stocks
    stocks_rows = parsed_data.get("stocks", [])
    # Look for the row containing "Stock Final"
    for row in stocks_rows:
        if not row: continue
        k = row[0].lower()
        if "stock final" in k or "final stock" in k:
            # Row structure: [Label, A-CT, B-CT, C-CT, A-GS, B-GS, C-GS, Total]
            # Need to handle potential extra empty column at start if split poorly, but clean_markdown_cell handles it usually.
            # Usually: ['Stock Final (U)', '427 040', '0', '0', '0', '434 681', '0', '861 721']
            values = row[1:]
            if len(values) >= 6:
                state.stock_a_ct = parse_int(values[0])
                state.stock_b_ct = parse_int(values[1])
                state.stock_c_ct = parse_int(values[2])
                state.stock_a_gs = parse_int(values[3])
                state.stock_b_gs = parse_int(values[4])
                state.stock_c_gs = parse_int(values[5])

    # 2. Raw Materials
    raw_rows = parsed_data.get("raw_materials", [])
    # Format: | Stock Final | N (Unit) | S (Unit) | ... |
    # Rows might be: ['Stock Final', '4 559 090', '3 707 500', '3 662', '2 622']
    for row in raw_rows:
        if not row: continue
        k = row[0].lower()
        if "stock final" in k or "final inventory" in k:
            values = row[1:]
            if len(values) >= 2:
                state.stock_mp_n = parse_int(values[0])
                state.stock_mp_s = parse_int(values[1])

    # 3. General Info (Workers, Machines, Indices)
    general_rows = parsed_data.get("general_info", [])
    
    # Handle duplicate "Avec" keys by keeping track of context (M1 vs M2)
    # The file has:
    # | Cap.Theor.Max./M1... | ... |
    # | Avec | 17 | ... |
    # | Cap.Theor.Max./M2... | ... |
    # | Avec | 0 | ... |
    
    last_context = "" # "m1" or "m2"
    
    for row in general_rows:
        if not row: continue
        if len(row) < 2: continue
        
        k = row[0].lower()
        v = row[1]
        
        if "nombre ouvriers" in k or "number of workers" in k:
            state.nb_ouvriers = parse_int(v)
        
        if "indice général des prix" in k or "price general index" in k:
            state.indice_prix = parse_number(v)
            
        if "indice salarial" in k or "wage index" in k:
            state.indice_salaire = parse_number(v)

        # Machine Context detection
        if "m1" in k:
            last_context = "m1"
        elif "m2" in k:
            last_context = "m2"
            
        if "avec" == k.strip() or "chaines en activité" in row[2].lower() if len(row)>2 else False:
            val = parse_int(v)
            if last_context == "m1":
                state.nb_machines_m1 = val
            elif last_context == "m2":
                state.nb_machines_m2 = val
            else:
                # Fallback if context not found (e.g. first "Avec" is usually M1)
                if state.nb_machines_m1 == 15: # Default
                    state.nb_machines_m1 = val
                else:
                    state.nb_machines_m2 = val

    # 4. Balance Sheet (Cash, Debt)
    # The Bilan table is 2 columns!
    # | ACTIF | Val | PASSIF | Val |
    balance_rows = parsed_data.get("balance_sheet", [])
    found_cash = False
    
    for row in balance_rows:
        if not row: continue
        
        # Strategy: Search entire row for keywords
        # Because "Emprunt" is on the right side (indices 2 and 3 usually)
        
        for i, cell in enumerate(row):
            c_lower = cell.lower()
            
            # Check for value at i+1
            if i + 1 >= len(row): break
            
            val_str = row[i+1]
            
            # Cash
            if ("disponibilités" in c_lower or "cash" in c_lower) and "net" not in c_lower and not found_cash:
                c = parse_number(val_str)
                # Ensure we don't pick up something else
                state.cash = c
                found_cash = True
                
            # Overdraft (French 'Découvert')
            if "découvert" in c_lower:
                ov = parse_number(val_str)
                if ov > 0:
                    state.cash = -ov
                    found_cash = True
            
            # Debt
            if "emprunt long terme" in c_lower or "long term debt" in c_lower:
                state.dette_lt = parse_number(val_str)
                
            if "emprunt court terme" in c_lower or "short term debt" in c_lower:
                state.dette_ct = parse_number(val_str)

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

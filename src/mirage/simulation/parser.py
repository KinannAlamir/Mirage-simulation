"""Parser for Mirage markdown data files."""

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


class MarkdownDataParser:
    """Parses Mirage simulation data from markdown files."""
    
    def __init__(self):
        self.raw_content: str = ""
        self.sections: Dict[str, str] = {}
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a markdown file and extract structured data."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.raw_content = path.read_text(encoding='utf-8')
        self._extract_sections()
        
        return self._build_data_dict()
    
    def _extract_sections(self) -> None:
        """Extract sections from markdown content."""
        # Split by ## headers
        sections = re.split(r'\n## ', self.raw_content)
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.strip().split('\n')
            title = lines[0].strip().replace('#', '').strip()
            content = '\n'.join(lines[1:])
            self.sections[title] = content
    
    def _build_data_dict(self) -> Dict[str, Any]:
        """Build structured data dictionary from sections."""
        data = {
            'period': self._extract_period(),
            'stocks': self._parse_stocks(),
            'raw_materials': self._parse_raw_materials(),
            'production': self._parse_production(),
            'balance_sheet': self._parse_balance_sheet(),
            'income': self._parse_income_statement(),
            'market': self._parse_market_data(),
            'expenses': self._parse_expenses(),
        }
        return data
    
    def _extract_period(self) -> int:
        """Extract period number from content."""
        match = re.search(r'Year\s*(-?\d+)', self.raw_content, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return -3  # Default
    
    def _parse_table(self, section_name: str) -> List[Dict[str, str]]:
        """Parse a markdown table from a section."""
        content = self.sections.get(section_name, '')
        if not content:
            return []
        
        lines = [l.strip() for l in content.split('\n') if l.strip() and '|' in l]
        if len(lines) < 2:
            return []
        
        # Extract headers
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        # Skip separator line
        data_lines = [l for l in lines[1:] if not re.match(r'^[\s\-|:]+$', l)]
        
        rows = []
        for line in data_lines:
            values = [v.strip() for v in line.split('|') if v.strip()]
            if len(values) >= len(headers):
                row = dict(zip(headers, values[:len(headers)]))
                rows.append(row)
        
        return rows
    
    def _parse_numeric(self, value: str) -> float:
        """Parse a numeric value from string."""
        if not value:
            return 0.0
        # Remove currency symbols, spaces, and handle European decimal format
        clean = re.sub(r'[^\d,.\-]', '', str(value))
        # Handle European format (1.234,56)
        if ',' in clean and '.' in clean:
            if clean.index(',') > clean.index('.'):
                # European: 1.234,56 -> 1234.56
                clean = clean.replace('.', '').replace(',', '.')
            # else American format
        elif ',' in clean:
            # Could be European decimal or American thousands
            parts = clean.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # European decimal: 1234,56
                clean = clean.replace(',', '.')
            else:
                # American thousands: 1,234
                clean = clean.replace(',', '')
        
        try:
            return float(clean)
        except ValueError:
            return 0.0
    
    def _parse_stocks(self) -> Dict[str, Any]:
        """Parse stocks section."""
        rows = self._parse_table('Stocks')
        stocks = {
            'a_to_units': 0,
            'a_to_value': 0.0,
            'a_to_quality': 100,
            'b_mr_units': 0,
            'b_mr_value': 0.0,
            'b_mr_quality': 50,
        }
        
        for row in rows:
            product = row.get('', '').lower()
            if 'a-to' in product or 'a to' in product:
                stocks['a_to_units'] = int(self._parse_numeric(row.get('Final stock', '0')))
                stocks['a_to_value'] = self._parse_numeric(row.get('Value', '0'))
                quality = row.get('Quality', '100')
                stocks['a_to_quality'] = int(self._parse_numeric(quality)) if quality else 100
            elif 'b-mr' in product or 'b mr' in product:
                stocks['b_mr_units'] = int(self._parse_numeric(row.get('Final stock', '0')))
                stocks['b_mr_value'] = self._parse_numeric(row.get('Value', '0'))
                quality = row.get('Quality', '50')
                stocks['b_mr_quality'] = int(self._parse_numeric(quality)) if quality else 50
        
        return stocks
    
    def _parse_raw_materials(self) -> Dict[str, Any]:
        """Parse raw materials section."""
        rows = self._parse_table('Raw Materials')
        materials = {
            'n_units': 0,
            'n_value': 0.0,
            's_units': 0,
            's_value': 0.0,
        }
        
        for row in rows:
            mat_type = row.get('Raw Material', '').upper()
            if mat_type == 'N':
                materials['n_units'] = int(self._parse_numeric(row.get('Final stock', '0')))
                materials['n_value'] = self._parse_numeric(row.get('Value', '0'))
            elif mat_type == 'S':
                materials['s_units'] = int(self._parse_numeric(row.get('Final stock', '0')))
                materials['s_value'] = self._parse_numeric(row.get('Value', '0'))
        
        return materials
    
    def _parse_production(self) -> Dict[str, Any]:
        """Parse production-related data from General Infos section."""
        content = self.sections.get('General Infos', '')
        production = {
            'workers': 0,
            'machines_m1': 0,
            'machines_m2': 0,
            'capacity_m1': 0,
            'capacity_m2': 0,
        }
        
        # Look for worker count
        match = re.search(r'(\d+)\s*workers?', content, re.IGNORECASE)
        if match:
            production['workers'] = int(match.group(1))
        
        # Look for machines
        match = re.search(r'(\d+)\s*M1\s*machines?\s*active', content, re.IGNORECASE)
        if match:
            production['machines_m1'] = int(match.group(1))
        
        match = re.search(r'(\d+)\s*M2\s*machines?\s*active', content, re.IGNORECASE)
        if match:
            production['machines_m2'] = int(match.group(1))
        
        # Look for capacity
        match = re.search(r'capacity[:\s]*(\d[\d,]*)\s*units?', content, re.IGNORECASE)
        if match:
            production['capacity_m1'] = int(self._parse_numeric(match.group(1)))
        
        return production
    
    def _parse_balance_sheet(self) -> Dict[str, Any]:
        """Parse balance sheet section."""
        rows = self._parse_table('Balance Sheet')
        balance = {
            'cash': 0.0,
            'receivables': 0.0,
            'payables': 0.0,
            'long_term_debt': 0.0,
            'short_term_debt': 0.0,
            'equity': 0.0,
            'total_assets': 0.0,
            'total_liabilities': 0.0,
        }
        
        for row in rows:
            item = row.get('', row.get('Item', '')).lower()
            value = self._parse_numeric(row.get('Value', row.get('Amount', '0')))
            
            if 'cash' in item or 'disponibilit' in item:
                balance['cash'] = value
            elif 'receivable' in item or 'client' in item or 'creances' in item:
                balance['receivables'] = value
            elif 'payable' in item or 'fournisseur' in item or 'dettes ct' in item:
                balance['payables'] = value
            elif 'long term' in item or 'dettes lt' in item or 'emprunt' in item:
                balance['long_term_debt'] = value
            elif 'short term' in item or 'court terme' in item:
                balance['short_term_debt'] = value
            elif 'equity' in item or 'capitaux' in item or 'fonds propres' in item:
                balance['equity'] = value
            elif 'total' in item and 'asset' in item:
                balance['total_assets'] = value
        
        return balance
    
    def _parse_income_statement(self) -> Dict[str, Any]:
        """Parse income statement section."""
        rows = self._parse_table('Income Statement')
        income = {
            'total_sales': 0.0,
            'total_expenses': 0.0,
            'gross_margin': 0.0,
            'operating_result': 0.0,
            'net_result': 0.0,
        }
        
        for row in rows:
            item = row.get('', row.get('Item', '')).lower()
            value = self._parse_numeric(row.get('Value', row.get('Amount', '0')))
            
            if 'sales' in item or 'vente' in item or 'chiffre' in item:
                income['total_sales'] = value
            elif 'net result' in item or 'resultat net' in item or 'profit' in item:
                income['net_result'] = value
            elif 'operating' in item or 'exploitation' in item:
                income['operating_result'] = value
            elif 'gross' in item or 'marge brute' in item:
                income['gross_margin'] = value
        
        return income
    
    def _parse_market_data(self) -> Dict[str, Any]:
        """Parse market-related data."""
        market = {
            'share_price': 0.0,
            'price_index': 100.0,
            'wage_index': 100.0,
        }
        
        # Stock market section
        stock_rows = self._parse_table('Stock Market')
        for row in stock_rows:
            item = row.get('', row.get('Item', '')).lower()
            value = self._parse_numeric(row.get('Value', row.get('Price', '0')))
            
            if 'share' in item or 'action' in item or 'cours' in item:
                market['share_price'] = value
        
        # General infos for indexes
        content = self.sections.get('General Infos', '')
        
        match = re.search(r'price\s*index[:\s]*(\d+[.,]?\d*)', content, re.IGNORECASE)
        if match:
            market['price_index'] = self._parse_numeric(match.group(1))
        
        match = re.search(r'wage\s*index[:\s]*(\d+[.,]?\d*)', content, re.IGNORECASE)
        if match:
            market['wage_index'] = self._parse_numeric(match.group(1))
        
        return market
    
    def _parse_expenses(self) -> Dict[str, Any]:
        """Parse expenses section."""
        rows = self._parse_table('Expenses')
        expenses = {}
        
        for row in rows:
            item = row.get('', row.get('Item', row.get('Category', '')))
            value = self._parse_numeric(row.get('Value', row.get('Amount', '0')))
            
            # Clean up key
            key = re.sub(r'[^\w]', '_', item.lower()).strip('_')
            if key:
                expenses[key] = value
        
        return expenses


class DecisionParser:
    """Parses decisions from markdown format."""
    
    def __init__(self):
        self.raw_content: str = ""
    
    def parse_file(self, file_path: str, period: int = -3) -> Dict[str, Any]:
        """Parse decisions file and extract data for a specific period."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.raw_content = path.read_text(encoding='utf-8')
        return self._extract_period_decisions(period)
    
    def _extract_period_decisions(self, period: int) -> Dict[str, Any]:
        """Extract decisions for a specific period."""
        decisions = {
            'product_a_to': {},
            'product_a_mr': {},
            'product_b_to': {},
            'product_b_mr': {},
            'product_c_to': {},
            'product_c_mr': {},
            'marketing': {},
            'production': {},
            'supply': {},
            'finance': {},
        }
        
        # Period column pattern
        period_str = f"P.{period}"
        
        # Find tables and extract values for the period
        lines = self.raw_content.split('\n')
        current_section = None
        headers = []
        period_col_idx = -1
        
        for line in lines:
            line = line.strip()
            
            # Section headers
            if line.startswith('##'):
                section_name = line.replace('#', '').strip().lower()
                if 'product a' in section_name:
                    if 'to' in section_name:
                        current_section = 'product_a_to'
                    elif 'mr' in section_name:
                        current_section = 'product_a_mr'
                elif 'product b' in section_name:
                    if 'to' in section_name:
                        current_section = 'product_b_to'
                    elif 'mr' in section_name:
                        current_section = 'product_b_mr'
                elif 'product c' in section_name:
                    if 'to' in section_name:
                        current_section = 'product_c_to'
                    elif 'mr' in section_name:
                        current_section = 'product_c_mr'
                elif 'marketing' in section_name:
                    current_section = 'marketing'
                elif 'supply' in section_name:
                    current_section = 'supply'
                elif 'production' in section_name:
                    current_section = 'production'
                elif 'finance' in section_name:
                    current_section = 'finance'
                elif 'csr' in section_name:
                    current_section = 'csr'
                else:
                    current_section = None
                headers = []
                period_col_idx = -1
                continue
            
            # Table header line
            if '|' in line and current_section:
                cells = [c.strip() for c in line.split('|')]
                cells = [c for c in cells if c]  # Remove empty
                
                # Check if this is header line
                if any(period_str in c for c in cells) or any(c.startswith('P.') for c in cells):
                    headers = cells
                    # Find the column index for our period
                    for idx, h in enumerate(headers):
                        if period_str in h:
                            period_col_idx = idx
                            break
                    continue
                
                # Skip separator line
                if all(c.replace('-', '').replace(':', '').strip() == '' for c in cells):
                    continue
                
                # Data line
                if period_col_idx >= 0 and len(cells) > period_col_idx:
                    row_name = cells[0].lower() if cells else ''
                    value = cells[period_col_idx] if period_col_idx < len(cells) else ''
                    
                    self._map_decision_value(decisions, current_section, row_name, value)
        
        return decisions
    
    def _map_decision_value(self, decisions: Dict, section: str, row_name: str, value: str) -> None:
        """Map a decision value to the appropriate field."""
        if section not in decisions:
            return
        
        # Parse numeric value
        numeric = self._parse_numeric(value)
        
        # Product decisions mapping
        if section.startswith('product_'):
            if 'price' in row_name or 'catalog' in row_name:
                decisions[section]['price'] = numeric
            elif 'promotion' in row_name:
                decisions[section]['promotion'] = numeric
            elif 'production' in row_name or 'quantity' in row_name:
                decisions[section]['production'] = int(numeric)
            elif 'quality' in row_name:
                decisions[section]['quality'] = int(numeric)
            elif 'rebate' in row_name or 'discount' in row_name:
                decisions[section]['rebate'] = numeric
            elif 'recycl' in row_name or 'packaging' in row_name:
                decisions[section]['recycled_packaging'] = value.lower() in ('yes', 'true', '1', 'oui')
        
        # Marketing decisions
        elif section == 'marketing':
            if 'salesm' in row_name and 'to' in row_name:
                decisions[section]['salesmen_to'] = int(numeric)
            elif 'salesm' in row_name and 'mr' in row_name:
                decisions[section]['salesmen_mr'] = int(numeric)
            elif 'commission' in row_name:
                decisions[section]['commission'] = numeric
            elif 'bonus' in row_name:
                decisions[section]['bonus'] = numeric
            elif 'advertis' in row_name and 'to' in row_name:
                decisions[section]['advertising_to'] = numeric
            elif 'advertis' in row_name and 'mr' in row_name:
                decisions[section]['advertising_mr'] = numeric
        
        # Production decisions
        elif section == 'production':
            if 'm1' in row_name and 'active' in row_name:
                decisions[section]['m1_active'] = int(numeric)
            elif 'm2' in row_name and 'active' in row_name:
                decisions[section]['m2_active'] = int(numeric)
            elif 'm1' in row_name and ('sold' in row_name or 'sell' in row_name):
                decisions[section]['m1_sold'] = int(numeric)
            elif 'm1' in row_name and ('bought' in row_name or 'buy' in row_name):
                decisions[section]['m1_bought'] = int(numeric)
            elif 'm2' in row_name and ('bought' in row_name or 'buy' in row_name):
                decisions[section]['m2_bought'] = int(numeric)
            elif 'hiring' in row_name or 'worker' in row_name:
                decisions[section]['hiring'] = int(numeric)
            elif 'purchasing' in row_name or 'power' in row_name:
                decisions[section]['purchasing_power'] = numeric
            elif 'maintenance' in row_name:
                decisions[section]['maintenance'] = value.lower() in ('yes', 'true', '1', 'oui')
        
        # Supply decisions
        elif section == 'supply':
            if ('n' in row_name or 'normal' in row_name) and 'order' in row_name:
                decisions[section]['n_order'] = int(numeric)
            elif ('n' in row_name or 'normal' in row_name) and 'duration' in row_name:
                decisions[section]['n_duration'] = int(numeric)
            elif ('s' in row_name or 'superior' in row_name) and 'order' in row_name:
                decisions[section]['s_order'] = int(numeric)
            elif ('s' in row_name or 'superior' in row_name) and 'duration' in row_name:
                decisions[section]['s_duration'] = int(numeric)
        
        # Finance decisions
        elif section == 'finance':
            if 'long' in row_name and 'loan' in row_name:
                decisions[section]['lt_loan'] = numeric
            elif 'long' in row_name and ('quarter' in row_name or 'term' in row_name):
                decisions[section]['lt_quarters'] = int(numeric)
            elif 'short' in row_name and 'loan' in row_name:
                decisions[section]['st_loan'] = numeric
            elif 'commercial' in row_name or 'discount' in row_name:
                decisions[section]['commercial_discount'] = numeric
            elif 'dividend' in row_name:
                decisions[section]['dividends'] = numeric
    
    def _parse_numeric(self, value: str) -> float:
        """Parse numeric value from string."""
        if not value:
            return 0.0
        clean = re.sub(r'[^\d,.\-]', '', str(value))
        if ',' in clean and '.' in clean:
            if clean.index(',') > clean.index('.'):
                clean = clean.replace('.', '').replace(',', '.')
        elif ',' in clean:
            parts = clean.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                clean = clean.replace(',', '.')
            else:
                clean = clean.replace(',', '')
        try:
            return float(clean)
        except ValueError:
            return 0.0

"""
Simple Data Mapper - Parses DML files and generates executable Python code.
"""

import re
from typing import Dict, List


class SimpleMapper:
    """Simple mapper implementation."""
    
    def __init__(self):
        self.source_type = "CSV"
        self.target_type = "CSV"
        self.rules = []
        
    def parse_mapping(self, text: str) -> Dict:
        """Parse a simple mapping definition."""
        # Extract mapping name
        match = re.search(r'MAPPING\s+(\w+)', text, re.IGNORECASE)
        name = match.group(1) if match else "unnamed"
        
        # Extract source type
        match = re.search(r'SOURCE\s+(CSV|XML|DB|EDI)', text, re.IGNORECASE)
        if match:
            self.source_type = match.group(1).upper()
        
        # Extract target type  
        match = re.search(r'TARGET\s+(CSV|XML|DB|EDI)', text, re.IGNORECASE)
        if match:
            self.target_type = match.group(1).upper()
        
        # Extract RULES block content
        rules_match = re.search(r'RULES\s*\{([^}]*)\}', text, re.IGNORECASE | re.DOTALL)
        rules_content = rules_match.group(1) if rules_match else ""
        
        # Extract map statements from RULES block
        self.rules = []
        for line in rules_content.split('\n'):
            # Match map statement: map source -> target
            map_match = re.match(r'\s*map\s+(\w+)\s*->\s*(\w+)', line, re.IGNORECASE)
            if map_match:
                self.rules.append({
                    'source': map_match.group(1),
                    'target': map_match.group(2)
                })
        
        return {
            'name': name,
            'source_type': self.source_type,
            'target_type': self.target_type,
            'rules': self.rules
        }
    
    def generate_code(self, mapping: Dict) -> str:
        """Generate Python code from mapping."""
        lines = []
        
        # Header
        lines.append('#!/usr/bin/env python3')
        lines.append(f'# Data Mapping: {mapping["name"]}')
        lines.append('')
        
        # Imports
        if self.source_type == 'XML' or self.target_type == 'XML':
            lines.append('import xml.etree.ElementTree as ET')
        if self.source_type == 'DB' or self.target_type == 'DB':
            lines.append('import sqlite3')
        lines.append('import csv')
        lines.append('')
        
        # Transform functions
        lines.append('# Transformation Functions')
        lines.append('def transform_value(value, func_name: str):')
        lines.append('    """Apply transformation function to value."""')
        lines.append('    if value is None:')
        lines.append('        return None')
        lines.append('    try:')
        lines.append('        if func_name == "upper":')
        lines.append('            return str(value).upper()')
        lines.append('        elif func_name == "lower":')
        lines.append('            return str(value).lower()')
        lines.append('        elif func_name == "trim":')
        lines.append('            return str(value).strip()')
        lines.append('        elif func_name == "int":')
        lines.append('            return int(value)')
        lines.append('        elif func_name == "float":')
        lines.append('            return float(value)')
        lines.append('    except Exception:')
        lines.append('        pass')
        lines.append('    return value')
        lines.append('')
        
        # Source reader
        if self.source_type == 'CSV':
            lines.append('def read_source(file_path: str) -> List[Dict]:')
            lines.append('    """Read CSV file."""')
            lines.append('    items = []')
            lines.append('    with open(file_path, "r", newline="") as f:')
            lines.append('        reader = csv.DictReader(f)')
            lines.append('        for row in reader:')
            lines.append('            items.append(dict(row))')
            lines.append('    return items')
        elif self.source_type == 'XML':
            lines.append('def read_source(file_path: str) -> List[Dict]:')
            lines.append('    """Read XML file."""')
            lines.append('    tree = ET.parse(file_path)')
            lines.append('    root = tree.getroot()')
            lines.append('    items = []')
            lines.append('    for elem in root.iter("Item"):')
            lines.append('        item = {child.tag: child.text for child in elem}')
            lines.append('        items.append(item)')
            lines.append('    return items')
        else:
            lines.append('def read_source(file_path: str) -> List[Dict]:')
            lines.append('    return []')
        lines.append('')
        
        # Target writer
        if self.target_type == 'CSV':
            lines.append('def write_target(items: List[Dict], output_path: str):')
            lines.append('    """Write CSV file."""')
            lines.append('    if not items:')
            lines.append('        return')
            lines.append('    fieldnames = list(items[0].keys())')
            lines.append('    with open(output_path, "w", newline="") as f:')
            lines.append('        writer = csv.DictWriter(f, fieldnames=fieldnames)')
            lines.append('        writer.writeheader()')
            lines.append('        for item in items:')
            lines.append('            writer.writerow(item)')
        elif self.target_type == 'XML':
            lines.append('def write_target(items: List[Dict], output_path: str):')
            lines.append('    """Write XML file."""')
            lines.append('    root = ET.Element("Root")')
            lines.append('    for item in items:')
            lines.append('        elem = ET.SubElement(root, "Item")')
            lines.append('        for key, value in item.items():')
            lines.append('            child = ET.SubElement(elem, key)')
            lines.append('            child.text = str(value) if value else ""')
            lines.append('    ET.ElementTree(root).write(output_path, encoding="utf-8", xml_declaration=True)')
        else:
            lines.append('def write_target(items: List[Dict], output_path: str):')
            lines.append('    pass')
        lines.append('')
        
        # Main function
        lines.append('def execute_mapping(input_file: str, output_file: str) -> List[Dict]:')
        lines.append('    """Execute the mapping."""')
        lines.append('    source_items = read_source(input_file)')
        lines.append('    output_items = []')
        
        # Generate rules - create single output item with all mapped fields
        lines.append('    for item in source_items:')
        if mapping.get('rules'):
            lines.append('        output_item = {')
            for i, rule in enumerate(mapping.get('rules', [])):
                src = rule['source']
                tgt = rule['target']
                comma = ',' if i < len(mapping.get('rules', [])) - 1 else ''
                lines.append(f'            "{tgt}": item.get("{src}"){comma}')
            lines.append('        }')
            lines.append('        output_items.append(output_item)')
        else:
            lines.append('        pass')  # No rules, just pass
        
        lines.append('    write_target(output_items, output_file)')
        lines.append('    return output_items')
        lines.append('')
        
        # Entry point
        lines.append('if __name__ == "__main__":')
        lines.append('    import sys')
        lines.append('    if len(sys.argv) >= 3:')
        lines.append('        result = execute_mapping(sys.argv[1], sys.argv[2])')
        lines.append('        print(f"Done: {len(result)} items")')
        lines.append('    else:')
        lines.append('        print("Usage: python mapper.py <input> <output>")')
        
        return '\n'.join(lines)


def compile_mapping(input_file: str, output_file: str) -> Dict:
    """Compile a mapping file."""
    with open(input_file, 'r') as f:
        content = f.read()
    
    mapper = SimpleMapper()
    mapping = mapper.parse_mapping(content)
    code = mapper.generate_code(mapping)
    
    with open(output_file, 'w') as f:
        f.write(code)
    
    print(f"Mapping compiled to {output_file}")
    return mapping


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        compile_mapping(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python simple_mapper.py <input.map> <output.py>")
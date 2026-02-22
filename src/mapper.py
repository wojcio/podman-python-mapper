"""
Complete Data Mapper - Parses DML files and generates executable Python code.
Supports mapping between XML, EDI, DB (databases), and CSV formats.

DML Mapping Language Syntax:
    MAPPING name {
        SOURCE TYPE { config... }
        TARGET TYPE { config... }
        RULES {
            map source_field -> target_field [TRANSFORM func] [IF condition]
        }
    }

Supported types: CSV, XML, DB, EDI
"""

import re
from typing import Dict, List, Optional


class Tokenizer:
    """Tokenizes the mapping language input."""

    TOKENS = [
        ('MAPPING', r'[Mm][Aa][Pp][Pp][Ii][Nn][Gg]\b'),
        ('SOURCE', r'[Ss][Oo][Uu][Rr][Cc][Ee]\b'),
        ('TARGET', r'[Tt][Aa][Rr][Gg][Ee][Tt]\b'),
        ('RULES', r'[Rr][Uu][Ll][Ee][Ss]\b'),
        ('XML', r'[Xx][Mm][Ll]\b'),
        ('CSV', r'[Cc][Ss][Vv]\b'),
        ('DB', r'[Dd][Bb]\b'),
        ('EDI', r'[Ee][Dd][Ii]\b'),
        ('JSON', r'[Jj][Ss][Oo][Nn]\b'),
        ('COMPONENT', r'[Cc][Oo][Mm][Pp][Oo][Nn][Ee][Nn][Tt]\b'),
        ('IF', r'[Ii][Ff]'),
        ('ELSE', r'[Ee][Ll][Ss][Ee]'),
        ('TRANSFORM', r'[Tt][Rr][Aa][Nn][Ss][Ff][Oo][Rr][Mm]'),
        ('DEFAULT', r'[Dd][Ee][Ff][Aa][Uu][Ll][Tt]'),
        ('AS', r'[Aa][Ss]\b'),
        ('MAP', r'[Mm][Aa][Pp]\b'),
        ('LOOP', r'[Ll][Oo][Oo][Pp]'),
        ('AGGREGATE', r'[Aa][Gg][Gg][Rr][Ee][Gg][Aa][Tt][Ee]'),
        ('FUNCTION', r'[Ff][Uu][Nn][Cc][Tt][Ii][Oo][Nn]'),
        ('WHEN', r'[Ww][Hh][Ee][Nn]'),
        ('THEN', r'[Tt][Hh][Ee][Nn]'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('ARROW', r'->'),
        ('COMMA', r','),
        ('COLON', r':'),
        ('GT', r'>'),
        ('LT', r'<'),
        ('GE', r'>='),
        ('LE', r'<='),
        ('EQ', r'=='),
        ('ASSIGN', r'='),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('STAR', r'\*'),
        ('SLASH', r'/'),
        ('PERCENT', r'%'),
        ('DOT', r'\.'),
        # IDENT before NUMBER to allow paths like "1000/OrderID" or just digits
        ('IDENT', r'[a-zA-Z_][a-zA-Z0-9_/]*|[0-9]+[a-zA-Z0-9_/]*'),
        ('STRING', r'"[^"]*"|\'[^\']*\''),
        ('NUMBER', r'-?\d+(\.\d+)?'),
        ('SLASHPATH', r'[a-zA-Z0-9_/-]+/[a-zA-Z0-9_/]*'),
        ('WS', r'\s+'),
        ('COMMENT', r'#.*$'),
    ]

    def __init__(self, text: str):
        self.text = text

    def tokenize(self) -> List[tuple]:
        """Convert input text into tokens."""
        pos = 0
        tokens = []
        while pos < len(self.text):
            match = None
            for token_type, pattern in self.TOKENS:
                regex = re.compile(pattern, re.MULTILINE)
                match = regex.match(self.text, pos)
                if match:
                    value = match.group(0)
                    if token_type not in ('WS', 'COMMENT'):
                        tokens.append((token_type, value))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Unexpected character at position {pos}: '{self.text[pos]}'")
        return tokens


class Parser:
    """Parses tokens into a structured mapping definition."""

    def __init__(self, text: str):
        self.tokenizer = Tokenizer(text)
        self.tokens: List[tuple] = []
        self.pos = 0

    def parse(self) -> Dict:
        """Parse the entire mapping definition."""
        self.tokens = self.tokenizer.tokenize()
        self.pos = 0
        return self.parse_mapping()

    def current_token(self) -> Optional[tuple]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self) -> Optional[tuple]:
        token = self.current_token()
        if token:
            self.pos += 1
        return token

    def expect(self, token_type: str) -> tuple:
        token = self.current_token()
        if not token or token[0] != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token()}")
        self.advance()
        return token

    def match(self, token_type: str) -> Optional[tuple]:
        if self.current_token() and self.current_token()[0] == token_type:
            return self.advance()
        return None

    def skip_whitespace(self):
        while self.current_token() and self.current_token()[0] in ('WS', 'COMMENT'):
            self.advance()

    def parse_mapping(self) -> Dict:
        """Parse MAPPING definition."""
        self.expect('MAPPING')
        name = self.expect('IDENT')[1]

        self.skip_whitespace()
        self.expect('LBRACE')

        sources = []
        target = None
        component = None
        rules = []

        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()

            if self.match('SOURCE'):
                sources.append(self.parse_source_target())
            elif self.match('TARGET'):
                target = self.parse_source_target()
            elif self.match('COMPONENT'):
                component = self.parse_source_target()
            elif self.match('RULES'):
                rules = self.parse_rules()
            else:
                raise SyntaxError(f"Unexpected token in mapping: {self.current_token()}")

        self.expect('RBRACE')

        return {
            'name': name,
            'sources': sources if sources else [{'type': 'CSV', 'alias': 'source1', 'config': {}}],
            'target': target or {'type': 'CSV', 'config': {}},
            'component': component,
            'rules': rules
        }

    def parse_source_target(self) -> Dict:
        """Parse SOURCE or TARGET configuration."""
        type_token = self.current_token()
        
        if not type_token:
            raise SyntaxError("Expected type (XML|CSV|DB|EDI|JSON)")
        
        if type_token[0] in ('XML', 'CSV', 'DB', 'EDI', 'JSON', 'IDENT'):
            config_type = type_token[1].upper()
            self.advance()
        else:
            raise SyntaxError(f"Expected source/target type, got {type_token[0]}")

        self.skip_whitespace()
        
        alias = None
        if self.match('AS'):
            self.skip_whitespace()
            alias = self.expect('IDENT')[1]
            self.skip_whitespace()

        self.expect('LBRACE')

        config = {}

        while self.current_token() and self.current_token()[0] != 'RBRACE':
            key = self.expect('IDENT')[1]
            self.skip_whitespace()
            self.expect('COLON')
            self.skip_whitespace()

            if self.match('LBRACE'):
                nested_config = {}
                while self.current_token() and self.current_token()[0] != 'RBRACE':
                    nested_key = self.expect('IDENT')[1]
                    self.skip_whitespace()
                    self.expect('COLON')
                    nested_value = self.parse_value()
                    nested_config[nested_key] = nested_value
                    self.skip_whitespace()
                    if self.current_token() and self.current_token()[0] == 'COMMA':
                        self.advance()
                self.expect('RBRACE')
                config[key] = nested_config
            else:
                value = self.parse_value()
                config[key] = value

            self.skip_whitespace()

            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.advance()

        self.expect('RBRACE')

        result = {'type': config_type, 'config': config}
        if alias:
            result['alias'] = alias
        return result

    def parse_value(self):
        """Parse a value (string, number, or identifier)."""
        token = self.current_token()
        if not token:
            return None

        if token[0] == 'STRING':
            self.advance()
            return token[1][1:-1]
        elif token[0] == 'NUMBER':
            self.advance()
            if '.' in token[1]:
                return float(token[1])
            return int(token[1])
        elif token[0] == 'IDENT':
            self.advance()
            return token[1]

        return None

    def parse_rules(self) -> List[Dict]:
        """Parse mapping rules."""
        self.expect('LBRACE')

        rules = []

        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()

            rule = self.parse_rule()
            if rule:
                rules.append(rule)

        self.expect('RBRACE')
        return rules

    def parse_rule(self) -> Optional[Dict]:
        """Parse a single mapping rule."""
        if self.match('LOOP'):
            return self.parse_loop_rule()

        if not self.match('MAP'):
            return None

        source_fields = []
        while True:
            self.skip_whitespace()
            token = self.current_token()

            if token and token[0] in ('STRING', 'IDENT'):
                source_fields.append(self.parse_value())
            else:
                break

            if not self.match('COMMA'):
                break

        self.skip_whitespace()
        self.expect('ARROW')
        self.skip_whitespace()

        target_field = None
        token = self.current_token()
        if token and token[0] in ('STRING', 'IDENT'):
            target_field = self.parse_value()

        transform = None
        condition = None
        default_value = None
        data_type = None

        while True:
            self.skip_whitespace()
            token = self.current_token()

            if not token:
                break

            if token[0] == 'TRANSFORM':
                self.advance()
                transform = self.parse_function_call()
            elif token[0] == 'IF':
                self.advance()
                condition = self.parse_condition()
            elif token[0] == 'DEFAULT':
                self.advance()
                default_value = self.parse_value()
            elif token[0] == 'AS':
                self.advance()
                data_type = self.expect('IDENT')[1].lower()
            else:
                break

        return {
            'source_field': source_fields[0] if source_fields else '',
            'target_field': target_field or '',
            'transform': transform,
            'condition': condition,
            'default_value': default_value,
            'data_type': data_type
        }

    def parse_function_call(self) -> str:
        """Parse a function call."""
        func_name = self.expect('IDENT')[1]
        self.skip_whitespace()
        self.expect('LPAREN')

        args = []
        while self.current_token() and self.current_token()[0] != 'RPAREN':
            arg = self.parse_value()
            if arg is not None:
                args.append(arg)
            self.skip_whitespace()

            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.advance()

        self.expect('RPAREN')

        return f"{func_name}({', '.join(repr(a) for a in args)})"

    def parse_condition(self) -> str:
        """Parse a condition expression."""
        parts = []
        while self.current_token() and self.current_token()[0] not in ('RBRACE', 'TRANSFORM', 'DEFAULT', 'AS'):
            token = self.current_token()
            if token[0] not in ('WS', 'COMMENT'):
                parts.append(token[1])
            self.advance()
        return ' '.join(parts)

    def parse_loop_rule(self) -> Optional[Dict]:
        """Parse a loop rule."""
        source_collection = self.expect('IDENT')[1]
        self.skip_whitespace()
        self.expect('LBRACE')

        sub_rules = []
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            rule = self.parse_rule()
            if rule:
                sub_rules.append(rule)

        self.expect('RBRACE')

        return {
            'source_field': source_collection,
            'target_field': 'loop',
            'transform': f'loop({repr(source_collection)})'
        }


class CodeGenerator:
    """Generates executable Python code from mapping definition."""

    def __init__(self, mapping: Dict):
        self.mapping = mapping

    def generate(self) -> str:
        """Generate complete Python code."""
        lines = []
        
        # Header
        lines.append('#!/usr/bin/env python3')
        lines.append(f'# Data Mapping: {self.mapping["name"]}')
        lines.append('# Auto-generated by DML Mapper')
        
        # Imports
        imports = ['import csv', 'import json', 'from typing import Dict, List, Optional']
        
        # Need pandas usually for easy df to sql, or we can use native SQLite inserts.
        # Native is lighter. 
        if self.mapping.get('component'):
            imports.append('import sqlite3')

        for src in self.mapping['sources']:
            source_type = src['type'].upper()
            if source_type in ('XML',):
                imports.append('import xml.etree.ElementTree as ET')
            if source_type in ('DB',):
                imports.append('import sqlite3')
            if source_type in ('EDI',):
                imports.append('import re')
            if source_type in ('JSON',):
                imports.append('import json')
                
        target_type = self.mapping['target']['type'].upper()
        if target_type == 'XML':
            imports.append('import xml.etree.ElementTree as ET')
        if target_type == 'DB':
            imports.append('import sqlite3')
        if target_type == 'EDI':
            imports.append('import re')
        if target_type == 'JSON':
            imports.append('import json')
        
        lines.extend(sorted(set(imports)))
        lines.append('')
        
        # Transformation functions
        lines.extend(self._generate_transform_functions())
        
        # Source handlers
        # Add generated readers for ALL types found
        used_src_types = {src['type'].upper() for src in self.mapping['sources']}
        for type_ in used_src_types:
            lines.extend(self._generate_source_handlers(type_))
        
        # Target handlers
        lines.extend(self._generate_target_handlers(target_type))
        
        # Main function
        lines.extend(self._generate_main_function(target_type))
        
        return '\n'.join(lines)

    def _generate_transform_functions(self) -> List[str]:
        """Generate transformation functions."""
        return [
            '',
            '# Transformation Functions',
            'def transform_value(value, func_name: str, *args):',
            '    """Apply transformation function to value."""',
            '    if value is None:',
            '        return None',
            '    try:',
            '        if func_name == "upper":',
            '            return str(value).upper()',
            '        elif func_name == "lower":',
            '            return str(value).lower()',
            '        elif func_name == "trim":',
            '            return str(value).strip()',
            '        elif func_name == "int":',
            '            return int(value)',
            '        elif func_name == "float":',
            '            return float(value)',
            '        elif func_name == "str":',
            '            return str(value)',
            '        elif func_name == "format_date":',
            '            if args:',
            '                return format_date_func(value, args[0])',
            '        elif func_name == "format_number":',
            '            if args:',
            '                return format_number_func(value, args[0])',
            '        elif func_name == "substring":',
            '            if args:',
            '                start = int(args[0]) if len(args) > 0 else 0',
            '                end = int(args[1]) if len(args) > 1 else None',
            '                return str(value)[start:end]',
            '    except Exception:',
            '        pass',
            '    return value',
            '',
            '# Date formatter',
            'def format_date_func(value, fmt):',
            '    """Format date value according to format string."""',
            '    import datetime',
            '    if isinstance(value, str):',
            '        for fmt_str in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:',
            '            try:',
            '                dt = datetime.datetime.strptime(value, fmt_str)',
            '                return dt.strftime(fmt.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d"))',
            '            except ValueError:',
            '                continue',
            '    return value',
            '',
            '# Number formatter',
            'def format_number_func(value, fmt):',
            '    """Format number according to format string."""',
            '    try:',
            '        num = float(value)',
            '        if fmt == "#,##0.00":',
            '            return f"{num:,.2f}"',
            '        elif fmt == "999999.99":',
            '            return f"{num:08.2f}"',
            '    except (ValueError, TypeError):',
            '        pass',
            '    return value',
        ]

    def _generate_source_handlers(self, source_type: str) -> List[str]:
        """Generate source reading functions."""
        if source_type == 'XML':
            return [
                '',
                '# XML Source Handler',
                'def read_source(file_path: str, root_element: Optional[str] = None) -> List[Dict]:',
                '    """Read data from XML file."""',
                '    tree = ET.parse(file_path)',
                '    root = tree.getroot()',
                '    items = []',
                '    for elem in root.iter(root_element) if root_element else [root]:',
                '        item = {child.tag: child.text for child in elem}',
                '        items.append(item)',
                '    return items',
            ]
        elif source_type == 'CSV':
            return [
                '',
                '# CSV Source Handler',
                'def read_source(file_path: str, has_header: bool = True) -> List[Dict]:',
                '    """Read data from CSV file."""',
                '    items = []',
                '    with open(file_path, "r", newline="") as f:',
                '        if has_header:',
                '            reader = csv.DictReader(f)',
                '            for row in reader:',
                '                items.append(dict(row))',
                '        else:',
                '            reader = csv.reader(f)',
                '            headers = [f"col_{i}" for i in range(len(next(reader)))]',
                '            f.seek(0)',
                '            reader = csv.DictReader(f, fieldnames=headers)',
                '            for row in reader:',
                '                items.append(dict(row))',
                '    return items',
            ]
        elif source_type == 'DB':
            return [
                '',
                '# Database Source Handler',
                'def read_db_source(db_type: str, connection_string: str, query: str) -> List[Dict]:',
                '    """Read data from database."""',
                '    if db_type.lower() == "sqlite":',
                '        conn = sqlite3.connect(connection_string)',
                '    else:',
                '        raise NotImplementedError(f"DB type {db_type} not implemented")',
                '    cursor = conn.cursor()',
                '    cursor.execute(query)',
                '    columns = [desc[0] for desc in cursor.description]',
                '    items = [dict(zip(columns, row)) for row in cursor.fetchall()]',
                '    conn.close()',
                '    return items',
            ]
        elif source_type == 'EDI':
            return [
                '',
                '# EDI Source Handler',
                'def read_edi_source(file_path: str, delimiter: str = "~") -> List[Dict]:',
                '    """Read data from EDI file."""',
                '    with open(file_path, "r") as f:',
                '        content = f.read()',
                '    items = []',
                '    segments = content.strip().split(delimiter)',
                '    for segment in segments:',
                '        if segment.strip():',
                '            parts = segment.split("+")',
                '            items.append({"segment": parts[0], "data": parts})',
                '    return items',
            ]
        else:
            return [
                '',
                '# Generic Source Handler',
                'def read_source(file_path: str) -> List[Dict]:',
                '    return []',
            ]

    def _generate_target_handlers(self, target_type: str) -> List[str]:
        """Generate target writing functions."""
        if target_type == 'XML':
            return [
                '',
                '# XML Target Handler',
                'def write_target(items: List[Dict], output_path: str, root_element: str = "Root"):',
                '    """Write data to XML file."""',
                '    root = ET.Element(root_element)',
                '    for item in items:',
                '        elem = ET.SubElement(root, "Item")',
                '        for key, value in item.items():',
                '            child = ET.SubElement(elem, key)',
                '            child.text = str(value) if value else ""',
                '    ET.ElementTree(root).write(output_path, encoding="utf-8", xml_declaration=True)',
            ]
        elif target_type == 'CSV':
            return [
                '',
                '# CSV Target Handler',
                'def write_target(items: List[Dict], output_path: str):',
                '    """Write data to CSV file."""',
                '    if not items:',
                '        return',
                '    fieldnames = list(items[0].keys())',
                '    with open(output_path, "w", newline="") as f:',
                '        writer = csv.DictWriter(f, fieldnames=fieldnames)',
                '        writer.writeheader()',
                '        for item in items:',
                '            writer.writerow(item)',
            ]
        elif target_type == 'DB':
            return [
                '',
                '# Database Target Handler',
                'def write_db_target(items: List[Dict], db_type: str, connection_string: str, table: str):',
                '    """Write data to database."""',
                '    if db_type.lower() == "sqlite":',
                '        conn = sqlite3.connect(connection_string)',
                '    else:',
                '        raise NotImplementedError(f"DB type {db_type} not implemented")',
                '    cursor = conn.cursor()',
                '    if items:',
                '        cols = list(items[0].keys())',
                '        placeholders = ", ".join(["?" for _ in cols])',
                '        for item in items:',
                '            values = [str(item.get(c)) if item.get(c) is not None else None for c in cols]',
                '            cursor.execute(f"INSERT INTO {table} ({", ".join(cols)}) VALUES ({placeholders})", values)',
                '    conn.commit()',
                '    conn.close()',
            ]
        elif target_type == 'EDI':
            return [
                '',
                '# EDI Target Handler',
                'def write_target(items: List[Dict], output_path: str, delimiter: str = "~"):',
                '    """Write data to EDI file."""',
                '    lines = []',
                '    for item in items:',
                '        segment = "+".join(str(v) if v else "" for v in item.values())',
                '        lines.append(segment)',
                '    with open(output_path, "w") as f:',
                '        f.write(delimiter.join(lines))',
            ]
        elif target_type == 'JSON':
            return [
                '',
                '# JSON Target Handler',
                'def write_target(items: List[Dict], output_path: str):',
                '    """Write data to JSON file."""',
                '    with open(output_path, "w") as f:',
                '        json.dump(items, f, indent=2)'
            ]
        else:
            return [
                '',
                '# Generic Target Handler',
                'def write_target(items: List[Dict], output_path: str):',
                '    pass',
            ]

    def _generate_component_db_setup(self) -> List[str]:
        """Generate code to setup In-Memory Component DB."""
        return [
            '',
            '    # --- Component Preparation (In-Memory DB) ---',
            '    import sqlite3',
            '    conn = sqlite3.connect(":memory:")',
            '    cursor = conn.cursor()',
        ]

    def _generate_main_function(self, target_type: str) -> List[str]:
        """Generate main execute_mapping function."""
        lines = []
        
        target_config = self.mapping['target']['config']
        component_config = self.mapping.get('component', {}).get('config', {})
        
        # In the main function we accept **kwargs for the sources instead
        # For a single source, input_data is a string, for multiple it will be a dict
        lines.extend([
            '',
            '# Main Mapping Function',
            'def execute_mapping(inputs: dict, output_path: str) -> List[Dict]:',
            '    """Execute the mapping and return transformed data.',
            '       inputs is a dict of { alias: file_path }',
            '    """',
            '    sources_data = {}'
        ])
        
        # Read all sources
        for src in self.mapping['sources']:
            source_type = src['type'].upper()
            source_config = src['config']
            alias = src.get('alias', 'source1')
            
            lines.append(f'    input_for_{alias} = inputs.get("{alias}")')
            lines.append(f'    if not input_for_{alias}:')
            lines.append(f'        pass # handle missing input gracefully if needed')
            lines.append(f'    else:')
            
            if source_type == 'CSV':
                has_header = str(source_config.get('has_header', 'true')).capitalize()
                lines.append(f'        sources_data["{alias}"] = read_source(input_for_{alias}, has_header={has_header})')
            elif source_type == 'DB':
                db_type = source_config.get('type', 'sqlite')
                conn_str = source_config.get('connection_string', '')
                query = source_config.get('query', 'SELECT * FROM table')
                escaped_query = query.replace('\\', '\\\\').replace('"', '\\"')
                lines.append(f'        sources_data["{alias}"] = read_db_source("{db_type}", "{conn_str}", """{escaped_query}""")')
            elif source_type == 'EDI':
                version = source_config.get('version', 'X12')
                lines.append(f'        sources_data["{alias}"] = read_edi_source(input_for_{alias}, delimiter="{version}")')
            elif source_type == 'JSON':
                # Reusing existing generic reader for JSON (we should implement a real JSON reader, but simple for now)
                lines.append(f'        with open(input_for_{alias}, "r") as f: sources_data["{alias}"] = json.load(f)')
            else:
                root_elem = source_config.get('root_element', 'Item')
                lines.append(f'        sources_data["{alias}"] = read_source(input_for_{alias}, root_element="{root_elem}")')

        # Insert component preparation block
        if self.mapping.get('component'):
            lines.extend(self._generate_component_db_setup())
            # For each source, create a table and insert its items
            for src in self.mapping['sources']:
                alias = src.get('alias', 'source1')
                lines.extend([
                    f'    if "{alias}" in sources_data and sources_data["{alias}"]:',
                    f'        # Dynamically create table and insert data for alias {alias}',
                    f'        first_item = sources_data["{alias}"][0]',
                    f'        columns = list(first_item.keys())',
                    f'        col_defs = ", ".join([f"{{c}} TEXT" for c in columns])',
                    f'        cursor.execute(f"CREATE TABLE {alias} ({{col_defs}})")',
                    f'        ',
                    f'        placeholders = ", ".join(["?" for _ in columns])',
                    f'        insert_sql = f"INSERT INTO {alias} ({{", ".join(columns)}}) VALUES ({{placeholders}})"',
                    f'        for item in sources_data["{alias}"]:',
                    f'            cursor.execute(insert_sql, [str(item.get(c)) if item.get(c) is not None else None for c in columns])',
                    f'        conn.commit()'
                ])
            
            # Execute Component Query
            comp_query = component_config.get('query', 'SELECT * FROM source1')
            escaped_comp_query = comp_query.replace('\\', '\\\\').replace('"', '\\"')
            lines.extend([
                f'    ',
                f'    # Execute Component query to produce final source items',
                f'    cursor.execute("""{escaped_comp_query}""")',
                f'    columns = [desc[0] for desc in cursor.description]',
                f'    source_items = [dict(zip(columns, row)) for row in cursor.fetchall()]',
                f'    conn.close()'
            ])
        else:
            # Backwards compatibility: if no component, just use the first source alias as source_items
            first_alias = self.mapping['sources'][0].get('alias', 'source1')
            lines.append(f'')
            lines.append(f'    source_items = sources_data.get("{first_alias}", [])')
        
        lines.extend([
            '',
            '    # Transform items',
            '    output_items = []',
        ])
        
        lines.append('    for source_item in source_items:')
        lines.append('        output_item = {}')
        
        # Generate rules - all fields go into one output item
        for rule in self.mapping['rules']:
            lines.extend(self._generate_rule_processing(rule, indent=8))
        
        lines.append('        output_items.append(output_item)')
        lines.append('')
        
        # Write target
        if target_type == 'CSV':
            lines.append('    write_target(output_items, output_path)')
        elif target_type == 'DB':
            db_type = target_config.get('type', 'sqlite')
            conn_str = target_config.get('connection_string', '')
            table = target_config.get('table', 'output')
            lines.append(f'    write_db_target(output_items, "{db_type}", "{conn_str}", "{table}")')
        elif target_type == 'EDI':
            version = target_config.get('version', 'X12')
            lines.append(f'    write_target(output_items, output_path, delimiter="{version}")')
        elif target_type == 'JSON':
            lines.append('    write_target(output_items, output_path)')
        else:
            root_elem = target_config.get('root_element', 'Root')
            lines.append(f'    write_target(output_items, output_path, root_element="{root_elem}")')
        
        lines.extend([
            '',
            '    return output_items',
        ])
        
        # Entry point updated for kwargs loading structure
        lines.extend([
            '',
            'if __name__ == "__main__":',
            '    import sys',
            '    # We map all sys.argv pairs (except last as output) intoinputs',
            '    if len(sys.argv) >= 3:',
            '        output_path = sys.argv[-1]',
            '        inputs = {}',
            '        if len(sys.argv) == 3:',
            '            inputs["source1"] = sys.argv[1]',
            '        else:',
            '            # Format: alias1 path1 alias2 path2 output',
            '            for i in range(1, len(sys.argv)-1, 2):',
            '                inputs[sys.argv[i]] = sys.argv[i+1]',
            '        result = execute_mapping(inputs, output_path)',
            '        print(f"Mapping complete: {len(result)} items")',
            '    else:',
            '        print("Usage: python generated.py [alias1 input1 ...] <output>")',
        ])
        
        return lines

    def _generate_rule_processing(self, rule: Dict, indent: int = 4) -> List[str]:
        """Generate code for processing a single mapping rule."""
        lines = []
        
        if not rule.get('target_field'):
            return lines
        
        source_var = f'source_item.get("{rule["source_field"]}")' if rule.get('source_field') else 'None'
        value_expr = source_var
        
        # Apply default value if provided
        if rule.get('default_value') is not None:
            default_val = repr(rule['default_value'])
            value_expr = f'{source_var} if {source_var} is not None else {default_val}'

        # Apply transform
        if rule.get('transform'):
            func_name = rule['transform'].split('(')[0]
            args_str = rule['transform'][len(func_name)+1:-1]  # Extract args
            value_expr = f'transform_value({value_expr}, "{func_name}", {args_str})'
        
        # Apply data type - map to Python built-ins
        if rule.get('data_type'):
            type_map = {
                'integer': 'int',
                'int': 'int',
                'string': 'str',
                'str': 'str',
                'decimal': 'float',  # Python uses float for decimals
                'float': 'float',
                'boolean': 'bool',
                'bool': 'bool',
            }
            python_type = type_map.get(rule['data_type'].lower(), rule['data_type'])
            value_expr = f'{python_type}({value_expr}) if {value_expr} is not None else None'
        
        # Generate assignment with proper indentation
        indent_str = ' ' * indent
        target_field = rule['target_field']
        
        if rule.get('condition'):
            lines.append(f'{indent_str}if {rule["condition"]}:')
            lines.append(f'{indent_str}    output_item["{target_field}"] = {value_expr}')
        else:
            lines.append(f'{indent_str}output_item["{target_field}"] = {value_expr}')
        
        return lines


def parse_dml_file(filepath: str) -> Dict:
    """Parse a DML mapping file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    parser = Parser(content)
    return parser.parse()


def generate_python_code(mapping: Dict) -> str:
    """Generate Python code from mapping definition."""
    generator = CodeGenerator(mapping)
    return generator.generate()


def compile_mapping(input_file: str, output_file: str) -> Dict:
    """Compile a mapping file to Python code."""
    mapping = parse_dml_file(input_file)
    python_code = generate_python_code(mapping)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    print(f"Mapping '{mapping['name']}' compiled to {output_file}")
    return mapping


if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 3:
        compile_mapping(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python mapper.py <input.map> <output.py>")